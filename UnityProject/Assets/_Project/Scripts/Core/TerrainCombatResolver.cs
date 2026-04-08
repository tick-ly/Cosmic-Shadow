using System;
using System.Collections.Generic;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// 扩展战斗结算器 - 支持地形加成和节点战斗
    /// </summary>
    public static class TerrainCombatResolver
    {
        private static readonly Random random = new Random();

        // ========== 节点战斗（含地形加成） ==========

        /// <summary>
        /// 在特定节点进行战斗，应用地形加成
        /// </summary>
        public static CombatResult ResolveTerrainCombat(
            CombatUnit attacker,
            CombatUnit defender,
            SkillBase skill,
            MapNode battleNode)
        {
            if (attacker == null || defender == null)
            {
                return new CombatResult
                {
                    Success = false,
                    Error = "Invalid attacker or defender"
                };
            }

            // 计算地形加成
            float attackerTerrainBonus = attacker.GetTerrainCombatBonus(battleNode.Terrain);
            float defenderTerrainBonus = defender.GetTerrainCombatBonus(battleNode.Terrain);
            float nodeDefenseBonus = battleNode.DefenseBonus;

            // 获取地形特殊效果并叠加到加成上
            MovementCostSystem.TerrainEffect terrainEffect = MovementCostSystem.GetTerrainEffects(battleNode);
            attackerTerrainBonus *= MovementCostSystem.ApplyTerrainEffect(terrainEffect, attacker, true);
            defenderTerrainBonus *= MovementCostSystem.ApplyTerrainEffect(terrainEffect, defender, false);

            // 修正成功率
            int baseSuccessRate = skill.GetModifiedSuccessRate(attacker);

            // 地形修正
            int terrainModifier = CalculateTerrainSuccessModifier(
                attackerTerrainBonus,
                defenderTerrainBonus,
                nodeDefenseBonus
            );

            int finalSuccessRate = Math.Clamp(baseSuccessRate + terrainModifier, 10, 95);

            // RNG判定
            int roll = random.Next(1, 101);
            bool success = roll <= finalSuccessRate;

            // 构建结果
            CombatResult result = new CombatResult
            {
                Success = success,
                User = attacker,
                Target = defender,
                Skill = skill,
                SuccessRate = finalSuccessRate,
                RiskLevel = CalculateRiskLevel(finalSuccessRate),
                Roll = roll,
                TerrainBonus = terrainModifier,
                BattleNode = battleNode,
                ActiveTerrainEffect = terrainEffect
            };

            // 应用效果
            if (success)
            {
                ApplySuccessEffectWithTerrain(result, attackerTerrainBonus);
            }
            else
            {
                ApplyFailureEffect(result);
            }

            // 更新技能状态
            skill.RecordUse();
            skill.SetCooldown();

            // 生成战斗日志
            result.CombatLog = GenerateTerrainCombatLog(result, battleNode);

            return result;
        }

        // ========== 地形成功率修正计算 ==========

        private static int CalculateTerrainSuccessModifier(
            float attackerBonus,
            float defenderBonus,
            float nodeDefense)
        {
            // 攻击者地形优势
            int attackerModifier = (int)((attackerBonus - 1.0f) * 20);

            // 防守者地形优势和节点防御
            int defenderModifier = -(int)((defenderBonus - 1.0f) * 15);
            int nodeModifier = -(int)((nodeDefense - 1.0f) * 10);

            return attackerModifier + defenderModifier + nodeModifier;
        }

        // ========== 成功效果（含地形加成） ==========

        private static void ApplySuccessEffectWithTerrain(CombatResult result, float terrainBonus)
        {
            SkillBase skill = result.Skill;
            Character target = result.Target;

            // 计算伤害（应用地形加成）
            int baseDamage = skill.GetSuccessDamage();
            int finalDamage = (int)(baseDamage * terrainBonus);

            target.TakeDamage(finalDamage);
            result.DamageDealt = finalDamage;

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

        // ========== 失败效果（继承原有逻辑） ==========

        private static void ApplyFailureEffect(CombatResult result)
        {
            SkillBase skill = result.Skill;
            Character user = result.User;

            // 反噬伤害
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

        // ========== 风险等级计算 ==========

        private static RiskLevel CalculateRiskLevel(int successRate)
        {
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

        // ========== 战斗日志生成（含地形信息） ==========

        private static string GenerateTerrainCombatLog(CombatResult result, MapNode battleNode)
        {
            string log = $"【节点战斗】{result.User.Name} vs {result.Target.Name}\n";
            log += $"地点: {battleNode.NodeName} ({battleNode.Terrain})\n";
            if (result.ActiveTerrainEffect != MovementCostSystem.TerrainEffect.None)
                log += $"地形效果: {result.ActiveTerrainEffect}\n";
            log += $"地形修正: {(result.TerrainBonus >= 0 ? "+" : "")}{result.TerrainBonus}%\n";
            log += $"成功率: {result.SuccessRate}% | 投掷: {result.Roll}\n";

            if (result.Success)
            {
                log += $"✓ 成功！造成 {result.DamageDealt} 点伤害\n";
            }
            else
            {
                log += $"✗ 失败！反噬 {result.SelfDamage} 点伤害\n";
            }

            log += $"现实债务: +{result.DebtIncurred}";

            return log;
        }

        // ========== 占领节点 ==========

        public static NodeCaptureResult CaptureNode(CombatUnit attacker, MapNode targetNode)
        {
            NodeCaptureResult result = new NodeCaptureResult
            {
                NodeId = targetNode.NodeId,
                PreviousOwner = targetNode.Owner,
                NewOwner = NodeOwner.Player,
                Success = false
            };

            // 检查是否有驻军
            if (targetNode.GarrisonStrength > 0)
            {
                result.Success = false;
                result.Reason = "节点仍有驻军，需要先击败驻军";
                return result;
            }

            // 占领节点
            targetNode.Owner = NodeOwner.Player;
            result.Success = true;
            result.Reason = "成功占领节点";

            // 触发探索
            targetNode.Explore();

            // 更新玩家数据
            GameState.Instance.DiscoverNode(targetNode.NodeId);

            return result;
        }

        // ========== 视野计算 ==========

        public static List<string> CalculateVisibleNodes(CombatUnit unit, IReadOnlyDictionary<string, MapNode> allNodes)
        {
            List<string> visibleNodes = new List<string>();

            if (string.IsNullOrEmpty(unit.CurrentNodeId))
                return visibleNodes;

            if (!allNodes.TryGetValue(unit.CurrentNodeId, out MapNode currentNode) || currentNode == null)
                return visibleNodes;

            // 当前节点总是可见
            visibleNodes.Add(currentNode.NodeId);

            // 根据视野范围计算可见节点
            foreach (var kvp in allNodes)
            {
                MapNode otherNode = kvp.Value;

                if (otherNode.NodeId == currentNode.NodeId)
                    continue;

                int distance = currentNode.GetManhattanDistanceTo(otherNode);

                if (distance <= unit.VisionRange)
                {
                    visibleNodes.Add(otherNode.NodeId);
                }
            }

            return visibleNodes;
        }
    }

    /// <summary>
    /// 节点占领结果
    /// </summary>
    [Serializable]
    public class NodeCaptureResult
    {
        public string NodeId { get; set; }
        public NodeOwner PreviousOwner { get; set; }
        public NodeOwner NewOwner { get; set; }
        public bool Success { get; set; }
        public string Reason { get; set; }
    }
}
