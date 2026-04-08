using UnityEngine;
using ShadowOfTheUniverse.Core;

namespace ShadowOfTheUniverse.Data
{
    /// <summary>
    /// 技能数据模板 - ScriptableObject
    /// 用于在Unity编辑器中配置技能数据，实现数据驱动设计
    /// </summary>
    [CreateAssetMenu(fileName = "NewSkill", menuName = "Shadow of the Universe/Skill Data")]
    public class SkillDataSO : ScriptableObject
    {
        [Header("基础信息")]
        [SerializeField] private string skillId;
        [SerializeField] private string skillName;
        [SerializeField] private BloodlineTier tier;
        [TextArea(3, 6)]
        [SerializeField] private string description;

        [Header("成功率与风险")]
        [SerializeField] [Range(10, 95)] private int baseSuccessRate;
        [SerializeField] private RiskLevel riskLevel;

        [Header("伤害数值")]
        [SerializeField] private int successDamage;
        [SerializeField] private int failureDamage;

        [Header("代价与冷却")]
        [SerializeField] private int baseRealityDebt;
        [SerializeField] private int cooldown;

        [Header("效果描述")]
        [TextArea(2, 4)]
        [SerializeField] private string successDescription;
        [TextArea(2, 4)]
        [SerializeField] private string failureDescription;

        [Header("视觉效果")]
        [SerializeField] private Sprite icon;
        [SerializeField] private GameObject successEffectPrefab;
        [SerializeField] private GameObject failureEffectPrefab;

        // ========== 属性访问 ==========

        public string SkillId => skillId;
        public string SkillName => skillName;
        public BloodlineTier Tier => tier;
        public string Description => description;
        public int BaseSuccessRate => baseSuccessRate;
        public int SuccessDamage => successDamage;
        public int FailureDamage => failureDamage;
        public int BaseRealityDebt => baseRealityDebt;
        public int Cooldown => cooldown;
        public string SuccessDescription => successDescription;
        public string FailureDescription => failureDescription;
        public Sprite Icon => icon;
        public GameObject SuccessEffectPrefab => successEffectPrefab;
        public GameObject FailureEffectPrefab => failureEffectPrefab;

        // ========== 创建技能实例 ==========

        /// <summary>
        /// 将ScriptableObject数据转换为运行时SkillBase对象
        /// </summary>
        public SkillBase CreateSkillInstance()
        {
            SkillEffect effect = new SkillEffect(successDescription, failureDescription);

            return new SkillBase(
                skillId,
                skillName,
                tier,
                description,
                baseSuccessRate,
                baseRealityDebt,
                successDamage,
                failureDamage,
                cooldown,
                effect
            );
        }

        // ========== 编辑器辅助 ==========

#if UNITY_EDITOR
        /// <summary>
        /// 编辑器中验证数据合法性
        /// </summary>
        private void OnValidate()
        {
            // 确保成功率在合理范围内
            baseSuccessRate = Mathf.Clamp(baseSuccessRate, 10, 95);

            // 根据血统等级自动调整基础成功率建议
            if (tier == BloodlineTier.Low && baseSuccessRate < 80)
            {
                Debug.LogWarning($"[{skillName}] 低级血统技能建议成功率 >= 80%");
            }
            else if (tier == BloodlineTier.Medium && (baseSuccessRate < 60 || baseSuccessRate > 80))
            {
                Debug.LogWarning($"[{skillName}] 中级血统技能建议成功率在 60-80% 之间");
            }
            else if (tier == BloodlineTier.High && baseSuccessRate > 60)
            {
                Debug.LogWarning($"[{skillName}] 高级血统技能建议成功率 <= 60%");
            }

            // 确保代价为正数
            if (baseRealityDebt < 0) baseRealityDebt = 0;
            if (successDamage < 0) successDamage = 0;
            if (failureDamage < 0) failureDamage = 0;
            if (cooldown < 0) cooldown = 0;
        }
#endif
    }
}
