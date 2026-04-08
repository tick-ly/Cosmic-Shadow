using System;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// 技能基类 - 纯C#类，不继承MonoBehaviour
    /// 实现"物理妥协"核心机制：成功率、风险等级、现实债务
    /// </summary>
    [Serializable]
    public class SkillBase
    {
        // ========== 技能数据 ==========

        public string Id { get; private set; }
        public string Name { get; private set; }
        public BloodlineTier Tier { get; private set; }
        public string Description { get; private set; }

        // 基础数值（从ScriptableObject加载）
        private int baseSuccessRate;
        private int baseRealityDebt;
        private int successDamage;
        private int failureDamage;
        private int cooldown;

        // ========== 使用统计 ==========

        public int ConsecutiveUses { get; private set; }
        public int CurrentCooldown { get; private set; }

        // ========== 技能效果 ==========

        public SkillEffect Effect { get; private set; }

        // ========== 构造函数 ==========

        public SkillBase(string id, string name, BloodlineTier tier, string description,
                        int baseSuccessRate, int baseRealityDebt,
                        int successDamage, int failureDamage,
                        int cooldown, SkillEffect effect)
        {
            Id = id;
            Name = name;
            Tier = tier;
            Description = description;

            this.baseSuccessRate = baseSuccessRate;
            this.baseRealityDebt = baseRealityDebt;
            this.successDamage = successDamage;
            this.failureDamage = failureDamage;
            this.cooldown = cooldown;
            this.Effect = effect;

            ConsecutiveUses = 0;
            CurrentCooldown = 0;
        }

        // ========== 成功率计算（核心逻辑） ==========

        /// <summary>
        /// 获取修正后的成功率 - 实现物理妥协的核心机制
        /// </summary>
        public int GetModifiedSuccessRate(Character user)
        {
            int rate = baseSuccessRate;

            // 1. 连续使用惩罚（每次连续使用降低5%）
            rate -= ConsecutiveUses * 5;

            // 2. 债务过高惩罚（债务>500时降低10%）
            if (user.RealityDebt > 500)
            {
                rate -= 10;
            }

            // 3. 疲劳惩罚（疲劳>70时降低15%）
            if (user.Fatigue > 70)
            {
                rate -= 15;
            }

            // 4. 血统等级修正（可选）
            // 高级血统可以略微提升成功率
            switch (user.Tier)
            {
                case BloodlineTier.High:
                    rate += 5;
                    break;
                case BloodlineTier.Medium:
                    rate += 2;
                    break;
            }

            // 限制成功率范围 [10%, 95%]
            return Math.Clamp(rate, 10, 95);
        }

        /// <summary>
        /// 获取风险等级（基于成功率）
        /// </summary>
        public RiskLevel GetRiskLevel(Character user)
        {
            int successRate = GetModifiedSuccessRate(user);

            if (successRate >= 85)
                return RiskLevel.Safe;
            else if (successRate >= 70)
                return RiskLevel.Low;
            else if (successRate >= 50)
                return RiskLevel.Medium;
            else if (successRate >= 30)
                return RiskLevel.High;
            else
                return RiskLevel.Critical;
        }

        // ========== 冷却管理 ==========

        public bool IsOnCooldown()
        {
            return CurrentCooldown > 0;
        }

        public void ReduceCooldown()
        {
            if (CurrentCooldown > 0)
            {
                CurrentCooldown--;
                // 冷却结束后重置连续使用计数
                if (CurrentCooldown == 0)
                {
                    ConsecutiveUses = 0;
                }
            }
        }

        public void SetCooldown()
        {
            CurrentCooldown = cooldown;
        }

        // ========== 使用追踪 ==========

        public void RecordUse()
        {
            ConsecutiveUses++;
        }

        public void ResetConsecutiveUses()
        {
            ConsecutiveUses = 0;
        }

        // ========== 伤害计算 ==========

        public int GetSuccessDamage()
        {
            return successDamage;
        }

        public int GetFailureDamage()
        {
            return failureDamage;
        }

        // ========== 现实债务计算 ==========

        public int GetRealityDebtCost(bool success)
        {
            if (success)
            {
                return baseRealityDebt;
            }
            else
            {
                // 失败时债务增加1.5倍
                return (int)(baseRealityDebt * 1.5f);
            }
        }

        // ========== 疲劳代价 ==========

        public int GetFatigueCost(bool success)
        {
            // 成功：10点疲劳，失败：20点疲劳
            return success ? 10 : 20;
        }

        // ========== 数据访问 ==========

        public int GetBaseSuccessRate()
        {
            return baseSuccessRate;
        }

        public int GetBaseRealityDebt()
        {
            return baseRealityDebt;
        }

        public int GetCooldown()
        {
            return cooldown;
        }
    }

    /// <summary>
    /// 技能效果定义
    /// </summary>
    [Serializable]
    public class SkillEffect
    {
        public string SuccessDescription { get; private set; }
        public string FailureDescription { get; private set; }
        public string EffectType { get; private set; }

        public SkillEffect(string successDesc, string failureDesc, string effectType = "damage")
        {
            SuccessDescription = successDesc;
            FailureDescription = failureDesc;
            EffectType = effectType;
        }
    }
}
