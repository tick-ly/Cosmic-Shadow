using System;
using System.Collections.Generic;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// 战斗结算器 - 纯C#类，不继承MonoBehaviour
    /// 处理战斗判定、RNG、反噬计算
    /// </summary>
    public class CombatResolver
    {
        // ========== RNG 系统 ==========

        private static Random random = new Random();

        public static void SetSeed(int seed)
        {
            random = new Random(seed);
        }

        // ========== 技能使用判定 ==========

        public static CombatResult ResolveSkillUse(Character user, SkillBase skill, Character target)
        {
            if (user == null || skill == null)
            {
                return new CombatResult
                {
                    Success = false,
                    Error = "Invalid user or skill"
                };
            }

            // 检查是否可以使用技能
            if (!user.CanUseSkill(skill))
            {
                return new CombatResult
                {
                    Success = false,
                    Error = "Cannot use skill (debt too high or fatigue too high)"
                };
            }

            // 检查冷却
            if (skill.IsOnCooldown())
            {
                return new CombatResult
                {
                    Success = false,
                    Error = "Skill is on cooldown"
                };
            }

            // 计算成功率
            int successRate = skill.GetModifiedSuccessRate(user);
            RiskLevel riskLevel = skill.GetRiskLevel(user);

            // RNG判定
            int roll = random.Next(1, 101); // 1-100
            bool success = roll <= successRate;

            // 构建结果
            CombatResult result = new CombatResult
            {
                Success = success,
                User = user,
                Target = target,
                Skill = skill,
                SuccessRate = successRate,
                RiskLevel = riskLevel,
                Roll = roll,
                DamageDealt = 0,
                DebtIncurred = 0,
                FatigueIncurred = 0
            };

            // 应用效果
            if (success)
            {
                ApplySuccessEffect(result);
            }
            else
            {
                ApplyFailureEffect(result);
            }

            // 更新技能状态
            skill.RecordUse();
            skill.SetCooldown();

            // 记录战斗日志
            result.CombatLog = GenerateCombatLog(result);

            return result;
        }

        // ========== 成功效果 ==========

        private static void ApplySuccessEffect(CombatResult result)
        {
            SkillBase skill = result.Skill;
            Character target = result.Target;

            // 造成伤害
            int damage = skill.GetSuccessDamage();
            if (target != null)
            {
                target.TakeDamage(damage);
                result.DamageDealt = damage;
            }

            // 增加现实债务
            int debt = skill.GetRealityDebtCost(true);
            result.User.AddRealityDebt(debt);
            result.DebtIncurred = debt;

            // 增加疲劳
            int fatigue = skill.GetFatigueCost(true);
            result.User.AddFatigue(fatigue);
            result.FatigueIncurred = fatigue;

            result.Description = skill.Effect.SuccessDescription;
        }

        // ========== 失败效果（反噬） ==========

        private static void ApplyFailureEffect(CombatResult result)
        {
            SkillBase skill = result.Skill;
            Character user = result.User;

            // 反噬伤害（自己受伤）
            int backlash = skill.GetFailureDamage();
            user.TakeDamage(backlash);
            result.SelfDamage = backlash;

            // 失败时债务增加更多
            int debt = skill.GetRealityDebtCost(false);
            user.AddRealityDebt(debt);
            result.DebtIncurred = debt;

            // 失败时疲劳增加更多
            int fatigue = skill.GetFatigueCost(false);
            user.AddFatigue(fatigue);
            result.FatigueIncurred = fatigue;

            result.Description = skill.Effect.FailureDescription;
        }

        // ========== 战斗日志生成 ==========

        private static string GenerateCombatLog(CombatResult result)
        {
            string log = $"{result.User.Name} 使用 {result.Skill.Name}\n";
            log += $"成功率: {result.SuccessRate}% | 风险: {result.RiskLevel}\n";
            log += $"投掷: {result.Roll} vs 需求: {result.SuccessRate}\n";

            if (result.Success)
            {
                log += $"✓ 成功！{result.Description}\n";
                if (result.Target != null)
                {
                    log += $"敌人受到 {result.DamageDealt} 点伤害\n";
                }
            }
            else
            {
                log += $"✗ 失败！{result.Description}\n";
                log += $"反噬伤害: {result.SelfDamage}\n";
            }

            log += $"现实债务: +{result.DebtIncurred} | 疲劳: +{result.FatigueIncurred}";

            return log;
        }

        // ========== 战斗结束检查 ==========

        public static BattleResult CheckBattleEnd(Character hero, Character enemy)
        {
            if (!hero.IsAlive)
            {
                return BattleResult.HeroDefeated;
            }

            if (enemy != null && !enemy.IsAlive)
            {
                return BattleResult.HeroVictory;
            }

            if (hero.RealityDebt >= 1000)
            {
                return BattleResult.DebtCrisis;
            }

            return BattleResult.None;
        }

        // ========== 基础攻击（无风险） ==========

        public static CombatResult ResolveBasicAttack(Character attacker, Character target, int baseDamage = 15)
        {
            // 基础攻击有轻微浮动 ±3
            int variance = random.Next(-3, 4);
            int damage = baseDamage + variance;

            target.TakeDamage(damage);

            return new CombatResult
            {
                Success = true,
                User = attacker,
                Target = target,
                DamageDealt = damage,
                Description = $"{attacker.Name} 进行基础攻击",
                CombatLog = $"{attacker.Name} 基础攻击造成 {damage} 点伤害"
            };
        }

        // ========== 敌人AI攻击 ==========

        public static CombatResult ResolveEnemyAttack(Character enemy, Character player, int baseAttackPower)
        {
            // 敌人攻击有轻微浮动 ±2
            int variance = random.Next(-2, 3);
            int damage = baseAttackPower + variance;

            player.TakeDamage(damage);

            return new CombatResult
            {
                Success = true,
                User = enemy,
                Target = player,
                DamageDealt = damage,
                Description = $"{enemy.Name} 攻击",
                CombatLog = $"{enemy.Name} 对 {player.Name} 造成 {damage} 点伤害"
            };
        }
    }

    /// <summary>
    /// 战斗结果数据结构
    /// </summary>
    [Serializable]
    public class CombatResult
    {
        public bool Success { get; set; }
        public string Error { get; set; }
        public string Description { get; set; }
        public string CombatLog { get; set; }

        public Character User { get; set; }
        public Character Target { get; set; }
        public SkillBase Skill { get; set; }

        public int SuccessRate { get; set; }
        public RiskLevel RiskLevel { get; set; }
        public int Roll { get; set; }

        public int DamageDealt { get; set; }
        public int SelfDamage { get; set; }
        public int DebtIncurred { get; set; }
        public int FatigueIncurred { get; set; }

        // ========== 扩展字段：地形与战斗 ==========

        public int TerrainBonus { get; set; }           // 地形成功率修正
        public MapNode BattleNode { get; set; }         // 战斗发生节点
        public MovementCostSystem.TerrainEffect ActiveTerrainEffect { get; set; } // 地形特殊效果
    }
}
