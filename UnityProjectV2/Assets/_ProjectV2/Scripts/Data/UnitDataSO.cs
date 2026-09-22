using ShadowOfTheUniverse.V2.Core;
using UnityEngine;

namespace ShadowOfTheUniverse.V2.Data
{
    [CreateAssetMenu(fileName = "V2Unit", menuName = "Shadow of the Universe/V2/Unit")]
    public sealed class UnitDataSO : ScriptableObject
    {
        [SerializeField] private string unitId = "unit_id";
        [SerializeField] private string displayName = "Unit";
        [SerializeField] private UnitDomain domain = UnitDomain.Land;
        [SerializeField] private UnitScale scale = UnitScale.Squad;
        [SerializeField] private int movementRange = 1;
        [SerializeField] private int maxHealth = 100;
        [SerializeField] private SkillDataSO[] skills;

        public string UnitId
        {
            get { return unitId; }
        }

        public UnitState ToRuntimeState(string startNodeId, int startingCompromisePoints)
        {
            UnitState state = new UnitState
            {
                Id = unitId,
                DisplayName = displayName,
                Domain = domain,
                Scale = scale,
                CurrentNodeId = startNodeId,
                MovementRange = movementRange,
                MaxHealth = maxHealth,
                CurrentHealth = maxHealth,
                CompromisePoints = startingCompromisePoints
            };

            if (skills != null)
            {
                for (int i = 0; i < skills.Length; i++)
                {
                    if (skills[i] != null)
                    {
                        state.Skills.Add(skills[i].ToRuntimeData());
                    }
                }
            }

            return state;
        }

        private void OnValidate()
        {
            movementRange = Mathf.Max(1, movementRange);
            maxHealth = Mathf.Max(1, maxHealth);
        }

#if UNITY_EDITOR
        public void ConfigureForEditor(
            string id,
            string unitName,
            UnitDomain unitDomain,
            UnitScale unitScale,
            int moveRange,
            int health,
            SkillDataSO[] availableSkills)
        {
            unitId = id;
            displayName = unitName;
            domain = unitDomain;
            scale = unitScale;
            movementRange = moveRange;
            maxHealth = health;
            skills = availableSkills;
            OnValidate();
        }
#endif
    }
}
