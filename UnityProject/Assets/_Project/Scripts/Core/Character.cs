using System;
using System.Collections.Generic;
using UnityEngine;
using ShadowOfTheUniverse.Data;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// 角色数据模型 - 纯C#类，不继承MonoBehaviour
    /// 遵循MVC原则，仅存储数据和基础逻辑
    /// </summary>
    [Serializable]
    public class Character
    {
        // 基础信息
        public string Name { get; private set; }
        public BloodlineTier Tier { get; private set; }

        // 生命值
        public int MaxHealth { get; private set; }
        public int CurrentHealth { get; private set; }

        // 核心资源
        public int RealityDebt { get; set; }           // 现实债务 (0-1000)
        public int Fatigue { get; set; }               // 疲劳度 (0-100)

        // 技能列表
        private List<SkillBase> skills;

        // 血统属性修正
        private CharacterClassSO classData;

        // ========== 构造函数 ==========

        public Character(string name, BloodlineTier tier, CharacterClassSO classData, int maxHealth = 100)
        {
            Name = name;
            Tier = tier;
            this.classData = classData;
            MaxHealth = maxHealth;
            CurrentHealth = maxHealth;

            // 初始化资源
            RealityDebt = 0;
            Fatigue = 0;

            // 初始化技能列表
            skills = new List<SkillBase>();
        }

        // ========== 属性访问 ==========

        public IReadOnlyList<SkillBase> Skills => skills.AsReadOnly();

        public bool IsAlive => CurrentHealth > 0;

        // ========== 技能管理 ==========

        public void AddSkill(SkillBase skill)
        {
            if (skill != null && !skills.Contains(skill))
            {
                skills.Add(skill);
            }
        }

        public bool CanUseSkill(SkillBase skill)
        {
            if (skill == null || !skills.Contains(skill))
                return false;

            // 债务过高时禁止使用高级技能
            if (RealityDebt > 800 && skill.Tier != BloodlineTier.Low)
                return false;

            // 疲劳过高时禁止使用任何技能
            if (Fatigue >= 100)
                return false;

            return true;
        }

        // ========== 伤害与治疗 ==========

        public void TakeDamage(int damage)
        {
            CurrentHealth = Mathf.Max(0, CurrentHealth - damage);
        }

        public void Heal(int amount)
        {
            CurrentHealth = Mathf.Min(MaxHealth, CurrentHealth + amount);
        }

        // ========== 资源管理 ==========

        public void AddRealityDebt(int amount)
        {
            RealityDebt = Mathf.Min(1000, RealityDebt + amount);
        }

        public void ReduceRealityDebt(int amount)
        {
            RealityDebt = Mathf.Max(0, RealityDebt - amount);
        }

        public void AddFatigue(int amount)
        {
            Fatigue = Mathf.Min(100, Fatigue + amount);
        }

        public void ReduceFatigue(int amount)
        {
            Fatigue = Mathf.Max(0, Fatigue - amount);
        }

        // ========== 休息恢复 ==========

        public void Rest(int debtReduction = 20, int fatigueReduction = 30)
        {
            ReduceRealityDebt(debtReduction);
            ReduceFatigue(fatigueReduction);
        }

        // ========== 状态查询 ==========

        public DebtStatus GetDebtStatus()
        {
            if (RealityDebt >= 900)
                return DebtStatus.Critical;
            if (RealityDebt >= 700)
                return DebtStatus.Dangerous;
            if (RealityDebt >= 500)
                return DebtStatus.Warning;
            if (RealityDebt >= 300)
                return DebtStatus.Caution;
            return DebtStatus.Safe;
        }

        public float GetHealthPercentage()
        {
            return (float)CurrentHealth / MaxHealth;
        }

        public float GetDebtPercentage()
        {
            return RealityDebt / 1000f;
        }

        public float GetFatiguePercentage()
        {
            return Fatigue / 100f;
        }
    }

    /// <summary>
    /// 债务状态
    /// </summary>
    public enum DebtStatus
    {
        Safe,       // 0-299
        Caution,    // 300-499
        Warning,    // 500-699
        Dangerous,  // 700-899
        Critical    // 900-1000
    }
}
