#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace AGDS.Engineering.FlatMultiLeg.Editor
{
    /// <summary>Creates neutral articulated primitives and runs an author-owned deterministic smoke check.</summary>
    public static class FlatMultiLegNeutralFixture
    {
        [Serializable]
        private sealed class RunResult
        {
            public string rig;
            public int legCount;
            public float deltaTime;
            public bool passed;
            public float maximumStanceError;
            public int minimumSupport;
            public int reachLimitCount;
            public int rootMotionLimitedSliceCount;
            public float requestedForwardDistance;
            public float actualRootDistance;
            public float yawTravelledDegrees;
            public float stoppedRootDrift;
            public bool releaseRestoredPose;
            public bool releaseStoppedWrites;
            public bool teleportReplanted;
            public string error;
        }

        [Serializable]
        private sealed class SmokeReport
        {
            public string unityVersion;
            public string generatedUtc;
            public bool passed;
            public bool invalidBindingRejected;
            public string invalidBindingReason;
            public bool nearStraightEightLegRejectedWithoutMutation;
            public string nearStraightEightLegReason;
            public RunResult[] runs;
        }

        private sealed class Fixture
        {
            public GameObject gameObject;
            public Transform root;
            public FlatMultiLegKinematicController controller;
            public FlatMultiLegKinematicController.LegBinding[] bindings;
            public Quaternion[] initialUpperRotations;
            public Quaternion[] initialLowerRotations;
        }

        [MenuItem("Tools/AGDS/Flat Multi-Leg/Create Neutral Demonstration")]
        public static void CreateNeutralDemonstration()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            CreateGround();
            var six = CreateRig("Neutral Six-Leg Tall", 6, new Vector3(-2.2f, 0f, 0f), 1.05f, 0.48f, 0.62f, 1.08f, 0.2f);
            var eight = CreateRig("Neutral Eight-Leg Wide", 8, new Vector3(2.2f, 0f, 0f), 0.78f, 0.72f, 0.46f, 1.32f, 0.20f);
            six.gameObject.AddComponent<FlatMultiLegNeutralDemoDriver>().Configure(six.controller, 0.30f, 24f);
            eight.gameObject.AddComponent<FlatMultiLegNeutralDemoDriver>().Configure(eight.controller, 0.24f, 20f);
            CreateCameraAndLight();
            Selection.activeGameObject = GameObject.Find("Neutral Six-Leg Tall");
            SceneView.lastActiveSceneView?.FrameSelected();
        }

        /// <summary>
        /// Batch entry point. Optional argument: -flatMultilegReport absolute-or-project-relative-json-path.
        /// </summary>
        public static void RunBatchValidation()
        {
            var runs = new List<RunResult>();
            var deltaTimes = new[] { 1f / 60f, 1f / 30f, 1f / 15f };
            foreach (var deltaTime in deltaTimes)
            {
                runs.Add(RunOne("Neutral Six-Leg Tall", 6, deltaTime, 1.05f, 0.48f, 0.62f, 1.08f, 0.2f));
                runs.Add(RunOne("Neutral Eight-Leg Wide", 8, deltaTime, 0.78f, 0.72f, 0.46f, 1.32f, 0.20f));
            }

            var invalidRejected = CheckInvalidBinding(out var invalidReason);
            var nearStraightRejected = CheckNearStraightEightLeg(out var nearStraightReason);
            var report = new SmokeReport
            {
                unityVersion = Application.unityVersion,
                generatedUtc = DateTime.UtcNow.ToString("O"),
                passed = invalidRejected && nearStraightRejected && runs.TrueForAll(run => run.passed),
                invalidBindingRejected = invalidRejected,
                invalidBindingReason = invalidReason,
                nearStraightEightLegRejectedWithoutMutation = nearStraightRejected,
                nearStraightEightLegReason = nearStraightReason,
                runs = runs.ToArray()
            };

            var reportPath = ResolveReportPath();
            Directory.CreateDirectory(Path.GetDirectoryName(reportPath) ?? Directory.GetCurrentDirectory());
            File.WriteAllText(reportPath, JsonUtility.ToJson(report, true));
            Debug.Log($"Flat multi-leg smoke report: {reportPath}\n{JsonUtility.ToJson(report, true)}");

            if (Application.isBatchMode)
                EditorApplication.Exit(report.passed ? 0 : 1);
        }

        private static RunResult RunOne(
            string rigName,
            int legCount,
            float deltaTime,
            float bodyHeight,
            float bodyRadiusX,
            float bodyRadiusZ,
            float stanceRadius,
            float kneeOffset)
        {
            var fixture = CreateRig(rigName, legCount, Vector3.zero, bodyHeight, bodyRadiusX, bodyRadiusZ, stanceRadius, kneeOffset);
            var result = new RunResult
            {
                rig = rigName,
                legCount = legCount,
                deltaTime = deltaTime,
                minimumSupport = legCount,
                requestedForwardDistance = 0f,
                passed = false
            };

            try
            {
                if (!fixture.controller.TryInitialize(out var reason))
                    throw new InvalidOperationException(reason);

                Sample(fixture, deltaTime, 2f, 0.30f, 0f, result);
                Sample(fixture, deltaTime, 1.5f, 0.22f, 24f, result);
                Sample(fixture, deltaTime, 1.5f, 0.22f, -24f, result);

                var beforeStop = fixture.root.position;
                fixture.controller.Stop();
                Sample(fixture, deltaTime, 0.5f, 0f, 0f, result);
                result.stoppedRootDrift = Vector3.Distance(beforeStop, fixture.root.position);

                Sample(fixture, deltaTime, 1.5f, 0.06f, 0f, result);
                Sample(fixture, deltaTime, 1f, 0f, 30f, result);
                fixture.controller.Stop();
                Sample(fixture, deltaTime, 0.5f, 0f, 0f, result);

                result.actualRootDistance = fixture.controller.RootDistanceTravelled;
                result.yawTravelledDegrees = fixture.controller.RootYawTravelledDegrees;
                result.reachLimitCount = fixture.controller.ReachLimitCount;
                result.rootMotionLimitedSliceCount = fixture.controller.RootMotionLimitedSliceCount;

                fixture.controller.Release(true);
                result.releaseRestoredPose = PoseMatchesCaptured(fixture, 0.001f);
                var upperAfterRelease = fixture.bindings[0].upper.localRotation;
                var lowerAfterRelease = fixture.bindings[0].lower.localRotation;
                result.releaseStoppedWrites = !fixture.controller.Step(deltaTime) &&
                    Quaternion.Angle(upperAfterRelease, fixture.bindings[0].upper.localRotation) <= 0.001f &&
                    Quaternion.Angle(lowerAfterRelease, fixture.bindings[0].lower.localRotation) <= 0.001f;

                if (!fixture.controller.TryInitialize(out reason))
                    throw new InvalidOperationException(reason);
                var teleported = fixture.root.position + new Vector3(0.75f, 0f, -0.4f);
                result.teleportReplanted = fixture.controller.TeleportAndReplant(
                    teleported,
                    Quaternion.Euler(0f, 37f, 0f),
                    out reason) && fixture.controller.SupportCount == legCount;
                if (!result.teleportReplanted && string.IsNullOrEmpty(result.error))
                    result.error = reason;

                result.passed = result.maximumStanceError <= 0.001f &&
                                result.minimumSupport >= legCount / 2 &&
                                result.reachLimitCount == 0 &&
                                result.actualRootDistance >= result.requestedForwardDistance * 0.5f &&
                                result.stoppedRootDrift <= 0.00001f &&
                                result.releaseRestoredPose &&
                                result.releaseStoppedWrites &&
                                result.teleportReplanted;
            }
            catch (Exception exception)
            {
                result.error = exception.ToString();
                result.passed = false;
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(fixture.gameObject);
            }
            return result;
        }

        private static void Sample(
            Fixture fixture,
            float deltaTime,
            float duration,
            float localForwardSpeed,
            float yawDegreesPerSecond,
            RunResult result)
        {
            var frames = Mathf.CeilToInt(duration / deltaTime);
            for (var frame = 0; frame < frames; frame++)
            {
                var velocity = fixture.root.forward * localForwardSpeed;
                fixture.controller.SetMotion(velocity, yawDegreesPerSecond);
                if (!fixture.controller.Step(deltaTime))
                    throw new InvalidOperationException(fixture.controller.LastError);
                if (!TransformsAreFinite(fixture))
                    throw new InvalidOperationException("A root or leg Transform became non-finite.");

                result.maximumStanceError = Mathf.Max(result.maximumStanceError, fixture.controller.MaxStanceErrorThisStep);
                result.minimumSupport = Mathf.Min(result.minimumSupport, fixture.controller.SupportCount);
            }
            result.requestedForwardDistance += localForwardSpeed * frames * deltaTime;
        }

        private static Fixture CreateRig(
            string name,
            int legCount,
            Vector3 groundOrigin,
            float bodyHeight,
            float bodyRadiusX,
            float bodyRadiusZ,
            float stanceRadius,
            float kneeOffset)
        {
            var rootObject = new GameObject(name);
            var root = rootObject.transform;
            root.position = groundOrigin + Vector3.up * bodyHeight;

            var body = GameObject.CreatePrimitive(legCount == 6 ? PrimitiveType.Capsule : PrimitiveType.Cube);
            body.name = "Neutral Body Visual";
            body.transform.SetParent(root, false);
            body.transform.localScale = legCount == 6
                ? new Vector3(bodyRadiusX * 1.25f, bodyRadiusZ * 0.75f, bodyRadiusZ * 1.45f)
                : new Vector3(bodyRadiusX * 1.4f, 0.32f, bodyRadiusZ * 1.7f);
            RemoveCollider(body);

            var bindings = new FlatMultiLegKinematicController.LegBinding[legCount];
            var initialUpper = new Quaternion[legCount];
            var initialLower = new Quaternion[legCount];
            for (var i = 0; i < legCount; i++)
            {
                var angle = i * Mathf.PI * 2f / legCount;
                var radial = new Vector3(Mathf.Sin(angle), 0f, Mathf.Cos(angle));
                var tangent = new Vector3(radial.z, 0f, -radial.x) * ((i & 1) == 0 ? 1f : -1f);
                var hipLocal = new Vector3(radial.x * bodyRadiusX, 0f, radial.z * bodyRadiusZ);
                var toeLocal = radial * stanceRadius + Vector3.down * bodyHeight;
                var kneeLocal = Vector3.Lerp(hipLocal, toeLocal, legCount == 6 ? 0.46f : 0.58f) +
                                tangent * kneeOffset + Vector3.up * (legCount == 6 ? 0.12f : -0.05f);

                var upper = new GameObject($"Leg {i + 1:00} Upper").transform;
                upper.SetParent(root, false);
                upper.localPosition = hipLocal;
                var lower = new GameObject($"Leg {i + 1:00} Lower").transform;
                lower.SetParent(upper, false);
                lower.localPosition = kneeLocal - hipLocal;
                var toe = new GameObject($"Leg {i + 1:00} Toe").transform;
                toe.SetParent(lower, false);
                toe.localPosition = toeLocal - kneeLocal;

                CreateBoneVisual("Upper Segment", upper, lower.localPosition, legCount == 6 ? 0.055f : 0.075f);
                CreateBoneVisual("Lower Segment", lower, toe.localPosition, legCount == 6 ? 0.045f : 0.06f);
                var toeVisual = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                toeVisual.name = "Toe Contact Visual";
                toeVisual.transform.SetParent(toe, false);
                toeVisual.transform.localScale = Vector3.one * (legCount == 6 ? 0.11f : 0.14f);
                RemoveCollider(toeVisual);

                bindings[i] = new FlatMultiLegKinematicController.LegBinding
                {
                    upper = upper,
                    lower = lower,
                    toe = toe,
                    phase01 = (i & 1) == 0 ? 0f : 0.5f
                };
                initialUpper[i] = upper.localRotation;
                initialLower[i] = lower.localRotation;
            }

            var controller = rootObject.AddComponent<FlatMultiLegKinematicController>();
            controller.Configure(new FlatMultiLegKinematicController.Configuration
            {
                locomotionRoot = root,
                legs = bindings,
                groundHeight = groundOrigin.y,
                minimumSupportContacts = legCount / 2,
                strideLength = legCount == 6 ? 0.34f : 0.42f,
                yawDegreesPerCycle = legCount == 6 ? 42f : 50f,
                swingDuration = legCount == 6 ? 0.22f : 0.28f,
                swingHeight = legCount == 6 ? 0.11f : 0.08f,
                landingPredictionSeconds = legCount == 6 ? 0.22f : 0.28f,
                reachMargin = 0.02f,
                minimumNeutralReachReserve = 0.04f,
                maximumAcceptedDeltaTime = 1f / 12f,
                integrationStep = 1f / 120f,
                autoStep = false,
                autoInitialize = false
            });

            return new Fixture
            {
                gameObject = rootObject,
                root = root,
                controller = controller,
                bindings = bindings,
                initialUpperRotations = initialUpper,
                initialLowerRotations = initialLower
            };
        }

        private static bool CheckInvalidBinding(out string reason)
        {
            var fixture = CreateRig("Invalid Duplicate Binding", 6, Vector3.zero, 1f, 0.45f, 0.6f, 1.05f, 0.18f);
            fixture.bindings[1].toe = fixture.bindings[0].toe;
            var rejected = !fixture.controller.TryInitialize(out reason) && !string.IsNullOrWhiteSpace(reason);
            UnityEngine.Object.DestroyImmediate(fixture.gameObject);
            return rejected;
        }

        private static bool CheckNearStraightEightLeg(out string reason)
        {
            var fixture = CreateRig("Unsupported Near-Straight Eight-Leg", 8, Vector3.zero, 0.78f, 0.72f, 0.46f, 1.32f, 0.12f);
            var rejected = !fixture.controller.TryInitialize(out reason) &&
                           reason.IndexOf("neutral reach reserve", StringComparison.OrdinalIgnoreCase) >= 0 &&
                           PoseMatchesCaptured(fixture, 0.001f);
            UnityEngine.Object.DestroyImmediate(fixture.gameObject);
            return rejected;
        }

        private static bool PoseMatchesCaptured(Fixture fixture, float angleTolerance)
        {
            for (var i = 0; i < fixture.bindings.Length; i++)
            {
                if (Quaternion.Angle(fixture.bindings[i].upper.localRotation, fixture.initialUpperRotations[i]) > angleTolerance ||
                    Quaternion.Angle(fixture.bindings[i].lower.localRotation, fixture.initialLowerRotations[i]) > angleTolerance)
                    return false;
            }
            return true;
        }

        private static bool TransformsAreFinite(Fixture fixture)
        {
            if (!Finite(fixture.root.position) || !Finite(fixture.root.rotation))
                return false;
            for (var i = 0; i < fixture.bindings.Length; i++)
                if (!Finite(fixture.bindings[i].upper.rotation) || !Finite(fixture.bindings[i].lower.rotation) ||
                    !Finite(fixture.bindings[i].toe.position))
                    return false;
            return true;
        }

        private static void CreateBoneVisual(string name, Transform parent, Vector3 endpointLocal, float radius)
        {
            var visual = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            visual.name = name;
            visual.transform.SetParent(parent, false);
            visual.transform.localPosition = endpointLocal * 0.5f;
            visual.transform.localRotation = Quaternion.FromToRotation(Vector3.up, endpointLocal.normalized);
            visual.transform.localScale = new Vector3(radius, endpointLocal.magnitude * 0.5f, radius);
            RemoveCollider(visual);
        }

        private static void CreateGround()
        {
            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Flat Ground";
            ground.transform.localScale = new Vector3(2f, 1f, 2f);
            RemoveCollider(ground);
        }

        private static void CreateCameraAndLight()
        {
            var cameraObject = new GameObject("Demonstration Camera");
            var camera = cameraObject.AddComponent<Camera>();
            cameraObject.transform.SetPositionAndRotation(new Vector3(0f, 5.4f, -7.2f), Quaternion.Euler(27f, 0f, 0f));
            camera.clearFlags = CameraClearFlags.Skybox;

            var lightObject = new GameObject("Demonstration Light");
            var light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.1f;
            lightObject.transform.rotation = Quaternion.Euler(45f, -35f, 0f);
        }

        private static void RemoveCollider(GameObject gameObject)
        {
            var collider = gameObject.GetComponent<Collider>();
            if (collider != null)
                UnityEngine.Object.DestroyImmediate(collider);
        }

        private static string ResolveReportPath()
        {
            var args = Environment.GetCommandLineArgs();
            for (var i = 0; i + 1 < args.Length; i++)
                if (string.Equals(args[i], "-flatMultilegReport", StringComparison.Ordinal))
                    return Path.GetFullPath(args[i + 1]);
            return Path.GetFullPath(Path.Combine(Directory.GetCurrentDirectory(), "FlatMultiLegSmokeReport.json"));
        }

        private static bool Finite(Vector3 value)
        {
            return Finite(value.x) && Finite(value.y) && Finite(value.z);
        }

        private static bool Finite(Quaternion value)
        {
            return Finite(value.x) && Finite(value.y) && Finite(value.z) && Finite(value.w);
        }

        private static bool Finite(float value)
        {
            return !float.IsNaN(value) && !float.IsInfinity(value);
        }
    }
}
#endif
