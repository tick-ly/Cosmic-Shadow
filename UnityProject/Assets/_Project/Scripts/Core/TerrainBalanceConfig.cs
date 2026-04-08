using ShadowOfTheUniverse.Core;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// 地形平衡配置 - 集中管理所有数值平衡参数
    /// 基于Agent分析建议的平衡性改进
    /// </summary>
    public static class TerrainBalanceConfig
    {
        // ========== 地形战斗加成（重新平衡） ==========

        /// <summary>
        /// 陆军地形战斗加成
        /// </summary>
        public const float LAND_ARMY_BONUS = 1.2f;      // 陆军在陆地+20%（原+15%）
        public const float COASTAL_ARMY_BONUS = 1.1f;   // 陆军在沿海+10%

        /// <summary>
        /// 海军地形战斗加成
        /// </summary>
        public const float SEA_NAVY_BONUS = 1.15f;      // 海军在海洋+15%（原+20%）
        public const float COASTAL_NAVY_BONUS = 1.05f;  // 海军在沿海+5%

        /// <summary>
        /// 空军地形战斗加成（特色化）
        /// </summary>
        public const float AIR_LAND_BONUS = 1.2f;       // 空军对陆地+20%
        public const float AIR_SEA_BONUS = 1.15f;       // 空军对海洋+15%
        public const float AIR_COASTAL_BONUS = 1.25f;   // 空军对沿海+25%（港口重要）

        /// <summary>
        /// 节点防御加成
        /// </summary>
        public const float LAND_DEFENSE_BONUS = 1.15f;  // 陆地防守+15%
        public const float COASTAL_DEFENSE_BONUS = 1.2f; // 沿海防守+20%
        public const float SEA_DEFENSE_BONUS = 1.0f;    // 海洋无防守加成

        // ========== 移动配置（重新平衡） ==========

        /// <summary>
        /// 单位移动范围
        /// </summary>
        public const int ARMY_MOVEMENT_RANGE = 3;      // 陆军移动3格（原2格）
        public const int NAVY_MOVEMENT_RANGE = 2;      // 海军移动2格（原3格）
        public const int AIR_OPERATION_RANGE = 5;      // 空军作战半径5格（原4格）

        /// <summary>
        /// 单位视野范围
        /// </summary>
        public const int ARMY_VISION_RANGE = 3;        // 陆军视野3格
        public const int NAVY_VISION_RANGE = 4;        // 海军视野4格
        public const int AIR_VISION_RANGE = 6;         // 空军视野6格

        // ========== 地形移动成本 ==========

        /// <summary>
        /// 获取地形战斗加成
        /// </summary>
        public static float GetTerrainCombatBonus(UnitDomain domain, TerrainType terrain)
        {
            return (domain, terrain) switch
            {
                // 陆军
                (UnitDomain.Land, TerrainType.Land) => LAND_ARMY_BONUS,
                (UnitDomain.Land, TerrainType.Coastal) => COASTAL_ARMY_BONUS,
                (UnitDomain.Land, TerrainType.Sea) => 0.5f, // 陆军在海洋极度劣势

                // 海军
                (UnitDomain.Sea, TerrainType.Sea) => SEA_NAVY_BONUS,
                (UnitDomain.Sea, TerrainType.Coastal) => COASTAL_NAVY_BONUS,
                (UnitDomain.Sea, TerrainType.Land) => 0.5f, // 海军在陆地极度劣势

                // 空军（特色化加成）
                (UnitDomain.Air, TerrainType.Land) => AIR_LAND_BONUS,
                (UnitDomain.Air, TerrainType.Sea) => AIR_SEA_BONUS,
                (UnitDomain.Air, TerrainType.Coastal) => AIR_COASTAL_BONUS,

                _ => 1.0f
            };
        }

        /// <summary>
        /// 获取节点防御加成
        /// </summary>
        public static float GetNodeDefenseBonus(TerrainType terrain)
        {
            return terrain switch
            {
                TerrainType.Land => LAND_DEFENSE_BONUS,
                TerrainType.Coastal => COASTAL_DEFENSE_BONUS,
                TerrainType.Sea => SEA_DEFENSE_BONUS,
                _ => 1.0f
            };
        }

        /// <summary>
        /// 获取单位移动范围
        /// </summary>
        public static int GetMovementRange(UnitDomain domain)
        {
            return domain switch
            {
                UnitDomain.Land => ARMY_MOVEMENT_RANGE,
                UnitDomain.Sea => NAVY_MOVEMENT_RANGE,
                UnitDomain.Air => 0, // 空军使用作战半径
                _ => 1
            };
        }

        /// <summary>
        /// 获取单位作战半径
        /// </summary>
        public static int GetOperationRange(UnitDomain domain)
        {
            return domain switch
            {
                UnitDomain.Air => AIR_OPERATION_RANGE,
                _ => 0
            };
        }

        /// <summary>
        /// 获取单位视野范围
        /// </summary>
        public static int GetVisionRange(UnitDomain domain)
        {
            return domain switch
            {
                UnitDomain.Land => ARMY_VISION_RANGE,
                UnitDomain.Sea => NAVY_VISION_RANGE,
                UnitDomain.Air => AIR_VISION_RANGE,
                _ => 2
            };
        }

        // ========== 超能力跨越地形配置 ==========

        /// <summary>
        /// 超能力跨越地形的基础债务代价
        /// </summary>
        public const int TERRAIN_CROSSING_BASE_DEBT = 30;

        /// <summary>
        /// 跨越地形额外债务倍率
        /// </summary>
        public static float GetTerrainCrossingMultiplier(TerrainType from, TerrainType to)
        {
            // 跨越到海洋的代价更高
            if (to == TerrainType.Sea)
            {
                return 1.5f;
            }
            return 1.0f;
        }

        // ========== 地形成功率修正配置 ==========

        /// <summary>
        /// 地形优势转换为成功率修正的比例
        /// </summary>
        public const float ATTACK_BONUS_TO_SUCCESS_RATE = 20f;    // 攻击加成 × 20
        public const float DEFENSE_BONUS_TO_SUCCESS_RATE = 15f;   // 防御加成 × 15
        public const float NODE_DEFENSE_TO_SUCCESS_RATE = 10f;    // 节点防御 × 10

        /// <summary>
        /// 计算地形成功率修正
        /// </summary>
        public static int CalculateTerrainSuccessModifier(
            float attackerBonus,
            float defenderBonus,
            float nodeDefense)
        {
            int attackerModifier = (int)((attackerBonus - 1.0f) * ATTACK_BONUS_TO_SUCCESS_RATE);
            int defenderModifier = -(int)((defenderBonus - 1.0f) * DEFENSE_BONUS_TO_SUCCESS_RATE);
            int nodeModifier = -(int)((nodeDefense - 1.0f) * NODE_DEFENSE_TO_SUCCESS_RATE);

            return attackerModifier + defenderModifier + nodeModifier;
        }

        // ========== 验证和平衡检查 ==========

        /// <summary>
        /// 获取平衡性报告（用于调试）
        /// </summary>
        public static string GetBalanceReport()
        {
            return $@"
地形平衡配置报告
================
陆军加成: 陆地{((LAND_ARMY_BONUS - 1) * 100):F0}% 沿海{((COASTAL_ARMY_BONUS - 1) * 100):F0}%
海军加成: 海洋{((SEA_NAVY_BONUS - 1) * 100):F0}% 沿海{((COASTAL_NAVY_BONUS - 1) * 100):F0}%
空军加成: 陆地{((AIR_LAND_BONUS - 1) * 100):F0}% 海洋{((AIR_SEA_BONUS - 1) * 100):F0}% 沿海{((AIR_COASTAL_BONUS - 1) * 100):F0}%

移动范围: 陆军{ARMY_MOVEMENT_RANGE}格 海军{NAVY_MOVEMENT_RANGE}格 空军{AIR_OPERATION_RANGE}格(半径)
视野范围: 陆军{ARMY_VISION_RANGE}格 海军{NAVY_VISION_RANGE}格 空军{AIR_VISION_RANGE}格

防御加成: 陆地{((LAND_DEFENSE_BONUS - 1) * 100):F0}% 沿海{((COASTAL_DEFENSE_BONUS - 1) * 100):F0}%
";
        }
    }
}
