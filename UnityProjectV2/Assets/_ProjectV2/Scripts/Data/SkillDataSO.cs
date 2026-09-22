using ShadowOfTheUniverse.V2.Core;
using UnityEngine;

namespace ShadowOfTheUniverse.V2.Data
{
    [CreateAssetMenu(fileName = "V2Skill", menuName = "Shadow of the Universe/V2/Skill")]
    public sealed class SkillDataSO : ScriptableObject
    {
        [SerializeField] private string skillId = "skill_id";
        [SerializeField] private string displayName = "Skill";
        [TextArea(2, 5)]
        [SerializeField] private string description = "Risk action.";
        [SerializeField, Range(10, 95)] private int baseSuccessRate = 85;
        [SerializeField] private int realityDebtCost = 10;
        [SerializeField] private int compromiseCost;
        [SerializeField] private int backlashDamage = 8;
        [SerializeField] private int fatigueCost = 10;
        [SerializeField] private int cooldownTurns = 0;
        [SerializeField] private int alertOnFailure = 1;
        [SerializeField] private int objectiveProgressOnSuccess = 1;
        [TextArea(2, 5)]
        [SerializeField] private string successDescription = "Action succeeded.";
        [TextArea(2, 5)]
        [SerializeField] private string failureDescription = "Action failed and caused backlash.";

        public string SkillId
        {
            get { return skillId; }
        }

        public SkillData ToRuntimeData()
        {
            return new SkillData
            {
                Id = skillId,
                DisplayName = displayName,
                Description = description,
                BaseSuccessRate = baseSuccessRate,
                RealityDebtCost = realityDebtCost,
                CompromiseCost = compromiseCost,
                BacklashDamage = backlashDamage,
                FatigueCost = fatigueCost,
                CooldownTurns = cooldownTurns,
                AlertOnFailure = alertOnFailure,
                ObjectiveProgressOnSuccess = objectiveProgressOnSuccess,
                SuccessDescription = successDescription,
                FailureDescription = failureDescription
            };
        }

        private void OnValidate()
        {
            baseSuccessRate = Mathf.Clamp(baseSuccessRate, 10, 95);
            realityDebtCost = Mathf.Max(0, realityDebtCost);
            compromiseCost = Mathf.Max(0, compromiseCost);
            backlashDamage = Mathf.Max(0, backlashDamage);
            fatigueCost = Mathf.Max(0, fatigueCost);
            cooldownTurns = Mathf.Max(0, cooldownTurns);
            alertOnFailure = Mathf.Max(0, alertOnFailure);
            objectiveProgressOnSuccess = Mathf.Max(0, objectiveProgressOnSuccess);
        }

#if UNITY_EDITOR
        public void ConfigureForEditor(
            string id,
            string skillName,
            string skillDescription,
            int successRate,
            int debtCost,
            int backlash,
            int fatigue,
            int cooldown,
            int alertFailure,
            int objectiveProgress,
            string successText,
            string failureText)
        {
            skillId = id;
            displayName = skillName;
            description = skillDescription;
            baseSuccessRate = successRate;
            realityDebtCost = debtCost;
            backlashDamage = backlash;
            fatigueCost = fatigue;
            cooldownTurns = cooldown;
            alertOnFailure = alertFailure;
            objectiveProgressOnSuccess = objectiveProgress;
            successDescription = successText;
            failureDescription = failureText;
            OnValidate();
        }
#endif
    }
}
