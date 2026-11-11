using UnityEngine;

namespace AGDS.Engineering.FlatMultiLeg
{
    /// <summary>Editor-fixture motion loop. It is an example caller, not a game state or input system.</summary>
    [DisallowMultipleComponent]
    public sealed class FlatMultiLegNeutralDemoDriver : MonoBehaviour
    {
        [SerializeField] private FlatMultiLegKinematicController controller;
        [SerializeField] private float forwardSpeed = 0.3f;
        [SerializeField] private float turnSpeed = 24f;
        private float elapsed;

        public void Configure(FlatMultiLegKinematicController value, float sampleForwardSpeed, float sampleTurnSpeed)
        {
            controller = value;
            forwardSpeed = sampleForwardSpeed;
            turnSpeed = sampleTurnSpeed;
        }

        private void Start()
        {
            if (controller == null)
            {
                Debug.LogError("Flat multi-leg demonstration requires a controller.", this);
                enabled = false;
                return;
            }
            if (!controller.TryInitialize(out var reason))
            {
                Debug.LogError($"Flat multi-leg demonstration could not initialize: {reason}", this);
                enabled = false;
            }
        }

        private void Update()
        {
            elapsed = Mathf.Repeat(elapsed + Time.deltaTime, 10f);
            var localSpeed = 0f;
            var yaw = 0f;
            if (elapsed < 2.5f)
                localSpeed = forwardSpeed;
            else if (elapsed < 5f)
            {
                localSpeed = forwardSpeed * 0.72f;
                yaw = turnSpeed;
            }
            else if (elapsed < 6f)
                localSpeed = 0f;
            else if (elapsed < 7.5f)
                localSpeed = forwardSpeed * 0.2f;
            else
                yaw = -turnSpeed;

            controller.SetMotion(transform.forward * localSpeed, yaw);
            if (!controller.Step(Time.deltaTime))
            {
                Debug.LogError($"Flat multi-leg demonstration stopped: {controller.LastError}", this);
                enabled = false;
            }
        }
    }
}
