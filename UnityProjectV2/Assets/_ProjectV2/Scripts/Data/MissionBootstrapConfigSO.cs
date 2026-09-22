using UnityEngine;

namespace ShadowOfTheUniverse.V2.Data
{
    [CreateAssetMenu(fileName = "V2MissionBootstrapConfig", menuName = "Shadow of the Universe/V2/Mission Bootstrap Config")]
    public sealed class MissionBootstrapConfigSO : ScriptableObject
    {
        [SerializeField] private TacticalMissionSO defaultMission;
        [SerializeField] private float secondsPerMove = 15f;

        public TacticalMissionSO DefaultMission
        {
            get { return defaultMission; }
        }

        public float SecondsPerMove
        {
            get { return secondsPerMove; }
        }

        private void OnValidate()
        {
            secondsPerMove = Mathf.Max(1f, secondsPerMove);
        }

#if UNITY_EDITOR
        public void ConfigureForEditor(TacticalMissionSO mission, float moveSeconds)
        {
            defaultMission = mission;
            secondsPerMove = moveSeconds;
            OnValidate();
        }
#endif
    }
}
