using UnityEngine;
using ShadowOfTheUniverse.Core;

namespace ShadowOfTheUniverse.Data
{
    /// <summary>
    /// 角色血统类别模板 - ScriptableObject
    /// 定义不同血统等级的基础属性加成
    /// </summary>
    [CreateAssetMenu(fileName = "NewCharacterClass", menuName = "Shadow of the Universe/Character Class")]
    public class CharacterClassSO : ScriptableObject
    {
        [Header("类别信息")]
        [SerializeField] private string classId;
        [SerializeField] private string className;
        [SerializeField] private BloodlineTier tier;
        [TextArea(3, 6)]
        [SerializeField] private string classDescription;

        [Header("基础属性")]
        [SerializeField] private int baseMaxHealth;
        [SerializeField] private int baseSpeed;
        [SerializeField] private int baseArmor;

        [Header("血统特性")]
        [SerializeField] private float debtMultiplier;         // 债务倍率
        [SerializeField] private int fatigueResistance;        // 抗疲劳
        [SerializeField] private int successRateBonus;         // 成功率加成

        [Header("技能容量")]
        [SerializeField] private int maxBasicSkills;
        [SerializeField] private int maxAdvancedSkills;
        [SerializeField] private int maxEliteSkills;

        [Header("视觉效果")]
        [SerializeField] private Sprite classIcon;
        [SerializeField] private GameObject characterPrefab;

        // ========== 属性访问 ==========

        public string ClassId => classId;
        public string ClassName => className;
        public BloodlineTier Tier => tier;
        public string ClassDescription => classDescription;

        public int BaseMaxHealth => baseMaxHealth;
        public int BaseSpeed => baseSpeed;
        public int BaseArmor => baseArmor;

        public float DebtMultiplier => debtMultiplier;
        public int FatigueResistance => fatigueResistance;
        public int SuccessRateBonus => successRateBonus;

        public int MaxBasicSkills => maxBasicSkills;
        public int MaxAdvancedSkills => maxAdvancedSkills;
        public int MaxEliteSkills => maxEliteSkills;

        public Sprite ClassIcon => classIcon;
        public GameObject CharacterPrefab => characterPrefab;

        // ========== 预设配置方法 ==========

        /// <summary>
        /// 配置为低级血统（高成功率，低代价）
        /// </summary>
        public void ConfigureAsLowTier()
        {
            tier = BloodlineTier.Low;
            baseMaxHealth = 100;
            baseSpeed = 50;
            baseArmor = 20;
            debtMultiplier = 1.0f;
            fatigueResistance = 30;
            successRateBonus = 5;
            maxBasicSkills = 5;
            maxAdvancedSkills = 1;
            maxEliteSkills = 0;
        }

        /// <summary>
        /// 配置为中级血统（中等成功率和代价）
        /// </summary>
        public void ConfigureAsMediumTier()
        {
            tier = BloodlineTier.Medium;
            baseMaxHealth = 150;
            baseSpeed = 60;
            baseArmor = 30;
            debtMultiplier = 1.3f;
            fatigueResistance = 20;
            successRateBonus = 2;
            maxBasicSkills = 3;
            maxAdvancedSkills = 3;
            maxEliteSkills = 1;
        }

        /// <summary>
        /// 配置为高级血统（低成功率，高代价）
        /// </summary>
        public void ConfigureAsHighTier()
        {
            tier = BloodlineTier.High;
            baseMaxHealth = 200;
            baseSpeed = 70;
            baseArmor = 40;
            debtMultiplier = 1.8f;
            fatigueResistance = 10;
            successRateBonus = 0;
            maxBasicSkills = 2;
            maxAdvancedSkills = 2;
            maxEliteSkills = 2;
        }

        // ========== 编辑器辅助 ==========

#if UNITY_EDITOR
        private void OnValidate()
        {
            // 确保数值在合理范围内
            if (baseMaxHealth < 1) baseMaxHealth = 1;
            if (baseSpeed < 0) baseSpeed = 0;
            if (baseArmor < 0) baseArmor = 0;
            if (debtMultiplier < 0.5f) debtMultiplier = 0.5f;
            if (debtMultiplier > 3.0f) debtMultiplier = 3.0f;
            if (fatigueResistance < 0) fatigueResistance = 0;
            if (fatigueResistance > 100) fatigueResistance = 100;

            // 根据血统等级自动验证数值合理性
            ValidateTierConsistency();
        }

        private void ValidateTierConsistency()
        {
            switch (tier)
            {
                case BloodlineTier.Low:
                    if (debtMultiplier > 1.2f)
                        Debug.LogWarning($"[{className}] 低级血统建议债务倍率 <= 1.2");
                    if (successRateBonus < 3)
                        Debug.LogWarning($"[{className}] 低级血统建议成功率加成 >= 3");
                    break;

                case BloodlineTier.Medium:
                    if (debtMultiplier < 1.2f || debtMultiplier > 1.5f)
                        Debug.LogWarning($"[{className}] 中级血统建议债务倍率在 1.2-1.5 之间");
                    break;

                case BloodlineTier.High:
                    if (debtMultiplier < 1.5f)
                        Debug.LogWarning($"[{className}] 高级血统建议债务倍率 >= 1.5");
                    if (maxEliteSkills < 1)
                        Debug.LogWarning($"[{className}] 高级血统应该至少拥有1个精英技能槽");
                    break;
            }
        }
#endif
    }
}
