using System;
using System.Collections.Generic;
using UnityEngine;

namespace AGDS.Engineering.FlatMultiLeg
{
    /// <summary>
    /// Kinematic flat-plane locomotion and two-bone IK for symmetric six- or eight-leg rigs.
    /// The controller owns locomotionRoot while active. Do not move that transform through another path.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class FlatMultiLegKinematicController : MonoBehaviour
    {
        private const float Epsilon = 0.00001f;
        private const float ScaleTolerance = 0.001f;

        [Serializable]
        public sealed class LegBinding
        {
            public Transform upper;
            public Transform lower;
            public Transform toe;
            [Range(0f, 0.9999f)] public float phase01;
        }

        [Serializable]
        public sealed class Configuration
        {
            public Transform locomotionRoot;
            public LegBinding[] legs;
            public float groundHeight;
            public int minimumSupportContacts;
            public float strideLength = 0.45f;
            public float yawDegreesPerCycle = 55f;
            public float swingDuration = 0.24f;
            public float swingHeight = 0.12f;
            public float landingPredictionSeconds = 0.24f;
            public float reachMargin = 0.025f;
            public float minimumNeutralReachReserve = 0.04f;
            public float maximumAcceptedDeltaTime = 0.1f;
            public float integrationStep = 1f / 120f;
            public bool autoStep = true;
            public bool autoInitialize = true;
        }

        private sealed class LegState
        {
            public LegBinding binding;
            public Vector3 hipLocal;
            public Vector3 neutralLocal;
            public Vector3 bendHintLocal;
            public Quaternion capturedUpperLocalRotation;
            public Quaternion capturedLowerLocalRotation;
            public float upperLength;
            public float lowerLength;
            public Vector3 anchorWorld;
            public Vector3 swingStartWorld;
            public Vector3 landingWorld;
            public float swingElapsed;
            public int lastCycle;
            public bool swinging;
        }

        [SerializeField] private Transform locomotionRoot;
        [SerializeField] private LegBinding[] legs = Array.Empty<LegBinding>();
        [SerializeField] private float groundHeight;
        [SerializeField] private int minimumSupportContacts = 3;
        [SerializeField] private float strideLength = 0.45f;
        [SerializeField] private float yawDegreesPerCycle = 55f;
        [SerializeField] private float swingDuration = 0.24f;
        [SerializeField] private float swingHeight = 0.12f;
        [SerializeField] private float landingPredictionSeconds = 0.24f;
        [SerializeField] private float reachMargin = 0.025f;
        [SerializeField] private float minimumNeutralReachReserve = 0.04f;
        [SerializeField] private float maximumAcceptedDeltaTime = 0.1f;
        [SerializeField] private float integrationStep = 1f / 120f;
        [SerializeField] private bool autoStep = true;
        [SerializeField] private bool autoInitialize = true;

        private LegState[] states = Array.Empty<LegState>();
        private Vector3 requestedPlanarVelocity;
        private float requestedYawDegreesPerSecond;
        private double gaitCycles;
        private bool active;
        private bool hasStarted;

        public bool IsActive => active;
        public string LastError { get; private set; } = string.Empty;
        public int SupportCount { get; private set; }
        public float MaxStanceErrorThisStep { get; private set; }
        public int ReachLimitCount { get; private set; }
        public int RootMotionLimitedSliceCount { get; private set; }
        public float LastMotionFraction { get; private set; } = 1f;
        public float RootDistanceTravelled { get; private set; }
        public float RootYawTravelledDegrees { get; private set; }
        public int InvalidStepCount { get; private set; }

        private void Start()
        {
            hasStarted = true;
            if (autoInitialize && !active)
                TryInitialize(out _);
        }

        private void OnEnable()
        {
            if (hasStarted && autoInitialize && !active)
                TryInitialize(out _);
        }

        private void Update()
        {
            if (autoStep && active)
                Step(Time.deltaTime);
        }

        private void OnDisable()
        {
            Release(true);
        }

        public void Configure(Configuration configuration)
        {
            if (configuration == null)
                throw new ArgumentNullException(nameof(configuration));
            if (active)
                throw new InvalidOperationException("Release the controller before replacing its configuration.");

            locomotionRoot = configuration.locomotionRoot;
            legs = configuration.legs ?? Array.Empty<LegBinding>();
            groundHeight = configuration.groundHeight;
            minimumSupportContacts = configuration.minimumSupportContacts;
            strideLength = configuration.strideLength;
            yawDegreesPerCycle = configuration.yawDegreesPerCycle;
            swingDuration = configuration.swingDuration;
            swingHeight = configuration.swingHeight;
            landingPredictionSeconds = configuration.landingPredictionSeconds;
            reachMargin = configuration.reachMargin;
            minimumNeutralReachReserve = configuration.minimumNeutralReachReserve;
            maximumAcceptedDeltaTime = configuration.maximumAcceptedDeltaTime;
            integrationStep = configuration.integrationStep;
            autoStep = configuration.autoStep;
            autoInitialize = configuration.autoInitialize;
        }

        public bool TryInitialize(out string reason)
        {
            if (active)
            {
                reason = string.Empty;
                return true;
            }

            if (!ValidateConfiguration(out reason))
            {
                LastError = reason;
                states = Array.Empty<LegState>();
                return false;
            }

            var nextStates = new LegState[legs.Length];
            for (var i = 0; i < legs.Length; i++)
            {
                var binding = legs[i];
                var hip = binding.upper.position;
                var knee = binding.lower.position;
                var toe = binding.toe.position;
                var endDirection = toe - hip;
                var bend = knee - hip;
                if (endDirection.sqrMagnitude > Epsilon)
                    bend -= Vector3.Project(bend, endDirection.normalized);
                if (bend.sqrMagnitude <= Epsilon)
                {
                    var radial = hip - locomotionRoot.position;
                    bend = Vector3.Cross(endDirection, Vector3.up);
                    if (Vector3.Dot(bend, radial) < 0f)
                        bend = -bend;
                }

                var state = new LegState
                {
                    binding = binding,
                    hipLocal = locomotionRoot.InverseTransformPoint(hip),
                    neutralLocal = locomotionRoot.InverseTransformPoint(ProjectToGround(toe)),
                    bendHintLocal = locomotionRoot.InverseTransformDirection(bend.normalized),
                    capturedUpperLocalRotation = binding.upper.localRotation,
                    capturedLowerLocalRotation = binding.lower.localRotation,
                    upperLength = Vector3.Distance(hip, knee),
                    lowerLength = Vector3.Distance(knee, toe),
                    anchorWorld = ProjectToGround(toe),
                    swingStartWorld = ProjectToGround(toe),
                    landingWorld = ProjectToGround(toe),
                    lastCycle = Mathf.FloorToInt(binding.phase01),
                    swinging = false
                };
                nextStates[i] = state;
            }

            states = nextStates;
            gaitCycles = 0d;
            requestedPlanarVelocity = Vector3.zero;
            requestedYawDegreesPerSecond = 0f;
            active = true;
            LastError = string.Empty;
            ResetMetrics();
            SolveAllLegs();
            reason = string.Empty;
            return true;
        }

        public void SetMotion(Vector3 planarWorldVelocity, float yawDegreesPerSecond)
        {
            if (!IsFinite(planarWorldVelocity) || !IsFinite(yawDegreesPerSecond))
                throw new ArgumentException("Motion input must contain finite values.");
            planarWorldVelocity.y = 0f;
            requestedPlanarVelocity = planarWorldVelocity;
            requestedYawDegreesPerSecond = yawDegreesPerSecond;
        }

        /// <summary>Stops root travel immediately. Existing swing arcs still finish while Step continues.</summary>
        public void Stop()
        {
            requestedPlanarVelocity = Vector3.zero;
            requestedYawDegreesPerSecond = 0f;
        }

        public bool Step(float deltaTime)
        {
            if (!active)
            {
                LastError = "The controller is not initialized.";
                InvalidStepCount++;
                return false;
            }
            if (!IsFinite(deltaTime) || deltaTime <= 0f || deltaTime > maximumAcceptedDeltaTime + Epsilon)
            {
                LastError = $"deltaTime must be finite and in (0, {maximumAcceptedDeltaTime:F4}] seconds.";
                InvalidStepCount++;
                return false;
            }

            LastError = string.Empty;
            MaxStanceErrorThisStep = 0f;
            var remaining = deltaTime;
            while (remaining > Epsilon)
            {
                var slice = Mathf.Min(remaining, integrationStep);
                StepSlice(slice);
                remaining -= slice;
            }
            return true;
        }

        /// <summary>Returns the rig to the pose captured at initialization and gives up all contact ownership.</summary>
        public void Release(bool restoreCapturedPose = true)
        {
            if (restoreCapturedPose)
            {
                for (var i = 0; i < states.Length; i++)
                {
                    var state = states[i];
                    if (state?.binding?.upper != null)
                        state.binding.upper.localRotation = state.capturedUpperLocalRotation;
                    if (state?.binding?.lower != null)
                        state.binding.lower.localRotation = state.capturedLowerLocalRotation;
                }
            }

            active = false;
            requestedPlanarVelocity = Vector3.zero;
            requestedYawDegreesPerSecond = 0f;
            states = Array.Empty<LegState>();
            SupportCount = 0;
            LastMotionFraction = 1f;
        }

        /// <summary>Discards old contacts and acquires the transforms exactly as they are now.</summary>
        public bool ResetFromCurrentPose(out string reason)
        {
            Release(false);
            return TryInitialize(out reason);
        }

        /// <summary>Moves the owned root, discards old contacts, and plants from the captured neutral pose at the destination.</summary>
        public bool TeleportAndReplant(Vector3 worldPosition, Quaternion worldRotation, out string reason)
        {
            if (!IsFinite(worldPosition) || !IsFinite(worldRotation))
            {
                reason = "Teleport pose must contain finite values.";
                LastError = reason;
                return false;
            }
            if (locomotionRoot == null)
            {
                reason = "locomotionRoot is required before teleporting.";
                LastError = reason;
                return false;
            }

            Release(true);
            locomotionRoot.SetPositionAndRotation(worldPosition, worldRotation.normalized);
            return TryInitialize(out reason);
        }

        public void ResetMetrics()
        {
            ReachLimitCount = 0;
            RootMotionLimitedSliceCount = 0;
            RootDistanceTravelled = 0f;
            RootYawTravelledDegrees = 0f;
            InvalidStepCount = 0;
            MaxStanceErrorThisStep = 0f;
            LastMotionFraction = 1f;
        }

        /// <summary>Returns the largest safe fraction of one proposed root translation and rotation.</summary>
        public float SafeMotionFraction(Vector3 proposedPosition, Quaternion proposedRotation)
        {
            if (!active || !IsFinite(proposedPosition) || !IsFinite(proposedRotation))
                return 0f;
            if (AllSupportAnchorsReachable(proposedPosition, proposedRotation))
                return 1f;

            var startPosition = locomotionRoot.position;
            var startRotation = locomotionRoot.rotation;
            if (!AllSupportAnchorsReachable(startPosition, startRotation))
                return 0f;

            var low = 0f;
            var high = 1f;
            for (var i = 0; i < 14; i++)
            {
                var middle = (low + high) * 0.5f;
                var position = Vector3.LerpUnclamped(startPosition, proposedPosition, middle);
                var rotation = Quaternion.SlerpUnclamped(startRotation, proposedRotation, middle);
                if (AllSupportAnchorsReachable(position, rotation))
                    low = middle;
                else
                    high = middle;
            }
            return low;
        }

        private void StepSlice(float deltaTime)
        {
            var previousPosition = locomotionRoot.position;
            var previousRotation = locomotionRoot.rotation;
            var proposedPosition = previousPosition + requestedPlanarVelocity * deltaTime;
            proposedPosition.y = previousPosition.y;
            var proposedRotation = Quaternion.AngleAxis(requestedYawDegreesPerSecond * deltaTime, Vector3.up) * previousRotation;
            var safeFraction = SafeMotionFraction(proposedPosition, proposedRotation);
            LastMotionFraction = safeFraction;
            if (safeFraction < 0.9999f &&
                (requestedPlanarVelocity.sqrMagnitude > Epsilon || Mathf.Abs(requestedYawDegreesPerSecond) > Epsilon))
                RootMotionLimitedSliceCount++;

            var nextPosition = Vector3.LerpUnclamped(previousPosition, proposedPosition, safeFraction);
            var nextRotation = Quaternion.SlerpUnclamped(previousRotation, proposedRotation, safeFraction);
            locomotionRoot.SetPositionAndRotation(nextPosition, nextRotation);

            var distance = requestedPlanarVelocity.magnitude * deltaTime * safeFraction;
            var yaw = Mathf.Abs(requestedYawDegreesPerSecond) * deltaTime * safeFraction;
            RootDistanceTravelled += distance;
            RootYawTravelledDegrees += yaw;
            // Intent continues to schedule support exchange while the reach guard holds the root.
            // Using actual movement here can deadlock at a fully extended planted contact.
            gaitCycles += requestedPlanarVelocity.magnitude * deltaTime / strideLength +
                          Mathf.Abs(requestedYawDegreesPerSecond) * deltaTime / yawDegreesPerCycle;

            // Once the guard is actively holding the root, waiting for a distant nominal phase
            // creates dead time. Advance only to the next configured boundary; support limits still
            // decide whether that exchange is legal.
            if (safeFraction < 0.9999f)
                AdvanceToNextSupportExchangeBoundary();

            StartEligibleSwings();
            AdvanceSwings(deltaTime);
            SolveAllLegs();
        }

        private void StartEligibleSwings()
        {
            if (requestedPlanarVelocity.sqrMagnitude <= Epsilon && Mathf.Abs(requestedYawDegreesPerSecond) <= Epsilon)
                return;

            var support = CountSupport();
            for (var i = 0; i < states.Length && support > minimumSupportContacts; i++)
            {
                var state = states[i];
                if (state.swinging)
                    continue;
                var cycle = FloorCycle(gaitCycles + state.binding.phase01);
                if (cycle <= state.lastCycle)
                    continue;

                StartSwing(state);
                state.lastCycle = cycle;
                support--;
            }
        }

        private void AdvanceToNextSupportExchangeBoundary()
        {
            if (CountSupport() <= minimumSupportContacts)
                return;

            var nextBoundary = double.PositiveInfinity;
            for (var i = 0; i < states.Length; i++)
            {
                var state = states[i];
                if (state.swinging)
                    continue;
                var boundary = state.lastCycle + 1d - state.binding.phase01;
                if (boundary > gaitCycles + 1e-9d && boundary < nextBoundary)
                    nextBoundary = boundary;
            }
            if (!double.IsInfinity(nextBoundary))
                gaitCycles = nextBoundary;
        }

        private void StartSwing(LegState state)
        {
            state.swinging = true;
            state.swingElapsed = 0f;
            state.swingStartWorld = state.anchorWorld;

            var prediction = Mathf.Max(0f, landingPredictionSeconds);
            var predictedPosition = locomotionRoot.position + requestedPlanarVelocity * prediction;
            var predictedRotation = Quaternion.AngleAxis(requestedYawDegreesPerSecond * prediction, Vector3.up) * locomotionRoot.rotation;
            var desired = ProjectToGround(TransformPointAtPose(state.neutralLocal, predictedPosition, predictedRotation));

            var predictedHip = TransformPointAtPose(state.hipLocal, predictedPosition, predictedRotation);
            var maximumReach = state.upperLength + state.lowerLength - reachMargin;
            state.landingWorld = ClampGroundTarget(predictedHip, desired, maximumReach);
        }

        private void AdvanceSwings(float deltaTime)
        {
            for (var i = 0; i < states.Length; i++)
            {
                var state = states[i];
                if (!state.swinging)
                    continue;
                state.swingElapsed += deltaTime;
                if (state.swingElapsed + Epsilon >= swingDuration)
                {
                    state.swingElapsed = swingDuration;
                    var hip = state.binding.upper.position;
                    var maximumReach = state.upperLength + state.lowerLength - reachMargin;
                    state.landingWorld = ClampGroundTarget(hip, state.landingWorld, maximumReach);
                    state.swinging = false;
                    state.anchorWorld = state.landingWorld;
                }
            }
        }

        private void SolveAllLegs()
        {
            SupportCount = 0;
            for (var i = 0; i < states.Length; i++)
            {
                var state = states[i];
                Vector3 target;
                if (state.swinging)
                {
                    var t = Mathf.Clamp01(state.swingElapsed / swingDuration);
                    var smooth = t * t * (3f - 2f * t);
                    target = Vector3.LerpUnclamped(state.swingStartWorld, state.landingWorld, smooth);
                    target.y += Mathf.Sin(t * Mathf.PI) * swingHeight;
                }
                else
                {
                    SupportCount++;
                    target = state.anchorWorld;
                    if (!TargetWithinReach(state, target))
                        ReachLimitCount++;
                }

                SolveTwoBone(state, target);
                if (!state.swinging)
                    MaxStanceErrorThisStep = Mathf.Max(MaxStanceErrorThisStep, Vector3.Distance(state.binding.toe.position, state.anchorWorld));
            }
        }

        private void SolveTwoBone(LegState state, Vector3 target)
        {
            var hip = state.binding.upper.position;
            var toTarget = target - hip;
            var distance = toTarget.magnitude;
            if (distance <= Epsilon)
                return;

            var direction = toTarget / distance;
            var minimumReach = Mathf.Abs(state.upperLength - state.lowerLength) + Epsilon;
            var maximumReach = state.upperLength + state.lowerLength - Epsilon;
            distance = Mathf.Clamp(distance, minimumReach, maximumReach);

            var bend = locomotionRoot.TransformDirection(state.bendHintLocal);
            bend -= Vector3.Project(bend, direction);
            if (bend.sqrMagnitude <= Epsilon)
                bend = Vector3.Cross(direction, Vector3.up);
            if (bend.sqrMagnitude <= Epsilon)
                bend = Vector3.Cross(direction, Vector3.right);
            bend.Normalize();

            var along = (state.upperLength * state.upperLength - state.lowerLength * state.lowerLength + distance * distance) /
                        (2f * distance);
            var height = Mathf.Sqrt(Mathf.Max(0f, state.upperLength * state.upperLength - along * along));
            var kneeTarget = hip + direction * along + bend * height;

            var currentUpper = state.binding.lower.position - hip;
            var desiredUpper = kneeTarget - hip;
            if (currentUpper.sqrMagnitude > Epsilon && desiredUpper.sqrMagnitude > Epsilon)
                state.binding.upper.rotation = Quaternion.FromToRotation(currentUpper, desiredUpper) * state.binding.upper.rotation;

            var knee = state.binding.lower.position;
            var currentLower = state.binding.toe.position - knee;
            var desiredLower = target - knee;
            if (currentLower.sqrMagnitude > Epsilon && desiredLower.sqrMagnitude > Epsilon)
                state.binding.lower.rotation = Quaternion.FromToRotation(currentLower, desiredLower) * state.binding.lower.rotation;
        }

        private bool AllSupportAnchorsReachable(Vector3 proposedPosition, Quaternion proposedRotation)
        {
            for (var i = 0; i < states.Length; i++)
            {
                var state = states[i];
                if (state.swinging)
                    continue;
                var hip = TransformPointAtPose(state.hipLocal, proposedPosition, proposedRotation);
                var minimumReach = Mathf.Abs(state.upperLength - state.lowerLength) + Epsilon;
                var maximumReach = state.upperLength + state.lowerLength - reachMargin;
                var distance = Vector3.Distance(hip, state.anchorWorld);
                if (distance > maximumReach + Epsilon || distance < minimumReach - Epsilon)
                    return false;
            }
            return true;
        }

        private bool ValidateConfiguration(out string reason)
        {
            if (locomotionRoot == null)
                return Reject("locomotionRoot is required.", out reason);
            if (legs == null || (legs.Length != 6 && legs.Length != 8))
                return Reject("Exactly 6 or 8 leg bindings are supported.", out reason);
            if ((legs.Length & 1) != 0)
                return Reject("The supported rigs require an even leg count.", out reason);
            if (minimumSupportContacts < legs.Length / 2 || minimumSupportContacts >= legs.Length)
                return Reject($"minimumSupportContacts must be from {legs.Length / 2} through {legs.Length - 1}.", out reason);
            if (!PositiveFinite(strideLength) || !PositiveFinite(yawDegreesPerCycle) || !PositiveFinite(swingDuration) ||
                !IsFinite(swingHeight) || swingHeight < 0f || !IsFinite(landingPredictionSeconds) || landingPredictionSeconds < 0f ||
                !IsFinite(reachMargin) || reachMargin <= 0f || !IsFinite(minimumNeutralReachReserve) ||
                minimumNeutralReachReserve < 0f ||
                !PositiveFinite(maximumAcceptedDeltaTime) ||
                !PositiveFinite(integrationStep) || integrationStep > maximumAcceptedDeltaTime)
                return Reject("Timing, stride, swing, prediction, reach, and delta-time settings must be finite and in their supported positive ranges.", out reason);
            if (landingPredictionSeconds + Epsilon < swingDuration)
                return Reject($"landingPredictionSeconds ({landingPredictionSeconds:G9} s) plus tolerance ({Epsilon:G9} s) must be at least swingDuration ({swingDuration:G9} s).", out reason);
            if (!IsUniformPositiveScale(locomotionRoot.lossyScale))
                return Reject("locomotionRoot requires a fixed positive uniform scale.", out reason);

            var unique = new HashSet<Transform>();
            for (var i = 0; i < legs.Length; i++)
            {
                var leg = legs[i];
                if (leg == null || leg.upper == null || leg.lower == null || leg.toe == null)
                    return Reject($"Leg {i} requires explicit upper, lower, and toe transforms.", out reason);
                if (!IsFinite(leg.phase01) || leg.phase01 < 0f || leg.phase01 >= 1f)
                    return Reject($"Leg {i} phase01 must be finite and in [0, 1).", out reason);
                if (!unique.Add(leg.upper) || !unique.Add(leg.lower) || !unique.Add(leg.toe))
                    return Reject($"Leg {i} reuses a transform already owned by another binding.", out reason);
                if (!leg.upper.IsChildOf(locomotionRoot) || leg.lower.parent != leg.upper || leg.toe.parent != leg.lower)
                    return Reject($"Leg {i} must be a direct upper -> lower -> toe chain below locomotionRoot.", out reason);
                if (!IsUniformPositiveScale(leg.upper.lossyScale) || !IsUniformPositiveScale(leg.lower.lossyScale) ||
                    !IsUniformPositiveScale(leg.toe.lossyScale))
                    return Reject($"Leg {i} requires fixed positive uniform transform scales.", out reason);

                var upperLength = Vector3.Distance(leg.upper.position, leg.lower.position);
                var lowerLength = Vector3.Distance(leg.lower.position, leg.toe.position);
                if (upperLength <= Epsilon || lowerLength <= Epsilon)
                    return Reject($"Leg {i} contains a zero-length bone.", out reason);
                if (reachMargin >= upperLength + lowerLength)
                    return Reject($"Leg {i} reachMargin leaves no usable reach.", out reason);
                var groundToe = ProjectToGround(leg.toe.position);
                var initialReach = Vector3.Distance(leg.upper.position, groundToe);
                var availableReachReserve = upperLength + lowerLength - reachMargin - initialReach;
                if (availableReachReserve + Epsilon < minimumNeutralReachReserve)
                    return Reject($"Leg {i} has {availableReachReserve:F4} m neutral reach reserve; at least {minimumNeutralReachReserve:F4} m is configured.", out reason);
            }

            reason = string.Empty;
            return true;
        }

        private int CountSupport()
        {
            var count = 0;
            for (var i = 0; i < states.Length; i++)
                if (!states[i].swinging)
                    count++;
            return count;
        }

        private Vector3 TransformPointAtPose(Vector3 localPoint, Vector3 worldPosition, Quaternion worldRotation)
        {
            var scale = locomotionRoot.lossyScale.x;
            return worldPosition + worldRotation * (localPoint * scale);
        }

        private Vector3 ProjectToGround(Vector3 point)
        {
            point.y = groundHeight;
            return point;
        }

        private Vector3 ClampGroundTarget(Vector3 hip, Vector3 desired, float maximumReach)
        {
            desired.y = groundHeight;
            var vertical = groundHeight - hip.y;
            var horizontalAllowanceSquared = maximumReach * maximumReach - vertical * vertical;
            if (horizontalAllowanceSquared <= Epsilon)
                return new Vector3(hip.x, groundHeight, hip.z);

            var horizontal = new Vector3(desired.x - hip.x, 0f, desired.z - hip.z);
            var maximumHorizontal = Mathf.Sqrt(horizontalAllowanceSquared);
            if (horizontal.magnitude > maximumHorizontal)
                horizontal = horizontal.normalized * maximumHorizontal;
            return new Vector3(hip.x + horizontal.x, groundHeight, hip.z + horizontal.z);
        }

        private bool TargetWithinReach(LegState state, Vector3 target)
        {
            var distance = Vector3.Distance(state.binding.upper.position, target);
            var minimumReach = Mathf.Abs(state.upperLength - state.lowerLength) + Epsilon;
            // ReachLimitCount reports an unsolvable physical target. The configured reachMargin is
            // a proactive root-motion reserve and is diagnosed separately by RootMotionLimitedSliceCount.
            var maximumReach = state.upperLength + state.lowerLength - Epsilon;
            return distance >= minimumReach - Epsilon && distance <= maximumReach + Epsilon;
        }

        private static int FloorCycle(double value)
        {
            return (int)Math.Floor(value + 1e-9d);
        }

        private static bool Reject(string message, out string reason)
        {
            reason = message;
            return false;
        }

        private static bool PositiveFinite(float value)
        {
            return IsFinite(value) && value > 0f;
        }

        private static bool IsUniformPositiveScale(Vector3 scale)
        {
            return IsFinite(scale) && scale.x > Epsilon && scale.y > Epsilon && scale.z > Epsilon &&
                   Mathf.Abs(scale.x - scale.y) <= ScaleTolerance && Mathf.Abs(scale.x - scale.z) <= ScaleTolerance;
        }

        private static bool IsFinite(Vector3 value)
        {
            return IsFinite(value.x) && IsFinite(value.y) && IsFinite(value.z);
        }

        private static bool IsFinite(Quaternion value)
        {
            return IsFinite(value.x) && IsFinite(value.y) && IsFinite(value.z) && IsFinite(value.w) &&
                   value.x * value.x + value.y * value.y + value.z * value.z + value.w * value.w > Epsilon;
        }

        private static bool IsFinite(float value)
        {
            return !float.IsNaN(value) && !float.IsInfinity(value);
        }
    }
}
