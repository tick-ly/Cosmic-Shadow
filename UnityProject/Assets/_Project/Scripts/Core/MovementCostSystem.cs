using System;
using ShadowOfTheUniverse.Core;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// 地形移动成本系统 - 增强移动策略深度
    /// 基于Agent分析建议的改进
    /// </summary>
    public static class MovementCostSystem
    {
        // ========== 地形移动成本枚举 ==========

        public enum TerrainCost
        {
            Plains = 1,        // 平原：1点移动力
            Forest = 2,        // 森林：2点移动力
            Mountain = 3,      // 山地：3点移动力
            ShallowSea = 1,    // 浅海：1点移动力
            DeepSea = 2,       // 深海：2点移动力
            Coastal = 1        // 沿海：1点移动力
        }

        // ========== 地形类型到成本映射 ==========

        /// <summary>
        /// 获取地形基础移动成本
        /// </summary>
        public static int GetTerrainBaseCost(TerrainType terrain)
        {
            return terrain switch
            {
                TerrainType.Land => 1,     // 陆地基础成本
                TerrainType.Sea => 1,      // 海洋基础成本
                TerrainType.Coastal => 1,  // 沿海基础成本
                _ => 1
            };
        }

        /// <summary>
        /// 获取单位对地形的移动成本修正
        /// </summary>
        public static float GetUnitTerrainCostModifier(UnitDomain domain, TerrainType terrain)
        {
            return (domain, terrain) switch
            {
                // 陆军地形成本
                (UnitDomain.Land, TerrainType.Land) => 1.0f,
                (UnitDomain.Land, TerrainType.Coastal) => 1.0f,
                (UnitDomain.Land, TerrainType.Sea) => float.MaxValue, // 无法通过

                // 海军地形成本
                (UnitDomain.Sea, TerrainType.Sea) => 1.0f,
                (UnitDomain.Sea, TerrainType.Coastal) => 1.0f,
                (UnitDomain.Sea, TerrainType.Land) => float.MaxValue, // 无法通过

                // 空军移动成本（所有地形减半）
                (UnitDomain.Air, _) => 0.5f,

                _ => 1.0f
            };
        }

        /// <summary>
        /// 计算实际移动成本
        /// </summary>
        public static int CalculateMovementCost(
            MapNode from,
            MapNode to,
            UnitDomain domain,
            RouteType? routeType)
        {
            // 检查地形兼容性
            float terrainModifier = GetUnitTerrainCostModifier(domain, to.Terrain);
            if (float.IsInfinity(terrainModifier))
            {
                return int.MaxValue; // 无法通过
            }

            // 基础移动成本
            int baseCost = from.GetManhattanDistanceTo(to);

            // 地形修正
            float cost = baseCost * terrainModifier;

            // 路线类型修正
            if (routeType.HasValue)
            {
                float routeModifier = GetRouteCostModifier(routeType.Value, domain);
                cost *= routeModifier;
            }

            return (int)Math.Ceiling(cost);
        }

        /// <summary>
        /// 获取路线移动成本修正
        /// </summary>
        private static float GetRouteCostModifier(RouteType routeType, UnitDomain domain)
        {
            return (domain, routeType) switch
            {
                // 陆军路线成本
                (UnitDomain.Land, RouteType.LandRoute) => 1.0f,
                (UnitDomain.Land, RouteType.SeaRoute) => float.MaxValue,

                // 海军路线成本
                (UnitDomain.Sea, RouteType.SeaRoute) => 1.0f,
                (UnitDomain.Sea, RouteType.LandRoute) => float.MaxValue,

                // 空军不使用路线
                (UnitDomain.Air, _) => 1.0f,

                _ => 1.0f
            };
        }

        // ========== 高级地形效果 ==========

        /// <summary>
        /// 地形特殊效果
        /// </summary>
        [Flags]
        public enum TerrainEffect
        {
            None = 0,
            ForestAmbush = 1 << 0,    // 森林伏击：攻击+20%
            MountainDefense = 1 << 1,  // 山地防御：防御+30%
            RiverCrossing = 1 << 2,   // 河流穿越：移动+1
            UrbanCombat = 1 << 3,     // 城市战斗：双方-10%
            DeepSeaDanger = 1 << 4,   // 深海危险：移动+2
            CoastalAdvantage = 1 << 5 // 沿海优势：视野+2
        }

        /// <summary>
        /// 获取地形特殊效果
        /// </summary>
        public static TerrainEffect GetTerrainEffects(MapNode node)
        {
            TerrainEffect effects = TerrainEffect.None;

            // 根据节点属性添加效果
            if (node.Terrain == TerrainType.Land)
            {
                // 陆地可能包含森林、山地、城市
                if (node.StrategicValue > 7)
                {
                    effects |= TerrainEffect.UrbanCombat; // 高战略价值=城市
                }
                else if (node.StrategicValue < 3)
                {
                    effects |= TerrainEffect.ForestAmbush; // 低战略价值=森林
                }
                else
                {
                    effects |= TerrainEffect.MountainDefense; // 中等=山地
                }
            }
            else if (node.Terrain == TerrainType.Sea)
            {
                if (node.ResourceValue > 3)
                {
                    effects |= TerrainEffect.DeepSeaDanger; // 高资源=深海
                }
            }
            else if (node.Terrain == TerrainType.Coastal)
            {
                effects |= TerrainEffect.CoastalAdvantage;
            }

            return effects;
        }

        /// <summary>
        /// 应用地形效果到战斗
        /// </summary>
        public static float ApplyTerrainEffect(
            TerrainEffect effect,
            CombatUnit unit,
            bool isAttacker)
        {
            return effect switch
            {
                TerrainEffect.ForestAmbush when isAttacker => 1.2f,    // 森林伏击+20%
                TerrainEffect.MountainDefense when !isAttacker => 1.3f, // 山地防守+30%
                TerrainEffect.UrbanCombat => 0.9f,                       // 城市战斗双方-10%
                TerrainEffect.DeepSeaDanger when isAttacker => 0.85f,  // 深海危险攻击-15%
                TerrainEffect.CoastalAdvantage when !isAttacker => 1.1f, // 沿海防守+10%
                _ => 1.0f
            };
        }

        // ========== 天气系统（预留扩展） ==========

        /// <summary>
        /// 天气类型
        /// </summary>
        public enum WeatherType
        {
            Clear,      // 晴朗
            Rain,       // 雨天
            Snow,       // 雪天
            Fog,        // 雾天
            Storm       // 暴风雨
        }

        /// <summary>
        /// 获取天气对移动的影响
        /// </summary>
        public static float GetWeatherMovementModifier(WeatherType weather, UnitDomain domain)
        {
            return (weather, domain) switch
            {
                // 雨天：陆军移动+50%，海军+20%
                (WeatherType.Rain, UnitDomain.Land) => 1.5f,
                (WeatherType.Rain, UnitDomain.Sea) => 1.2f,
                (WeatherType.Rain, UnitDomain.Air) => 1.3f,

                // 雪天：陆军移动+100%
                (WeatherType.Snow, UnitDomain.Land) => 2.0f,
                (WeatherType.Snow, UnitDomain.Sea) => 1.1f,
                (WeatherType.Snow, UnitDomain.Air) => 1.5f,

                // 雾天：视野减半
                (WeatherType.Fog, _) => 1.0f, // 移动不受影响

                // 暴风雨：所有单位移动+100%
                (WeatherType.Storm, _) => 2.0f,

                _ => 1.0f
            };
        }

        /// <summary>
        /// 获取天气对战斗的影响
        /// </summary>
        public static float GetWeatherCombatModifier(WeatherType weather, UnitDomain domain)
        {
            return (weather, domain) switch
            {
                // 雨天：命中率-10%
                (WeatherType.Rain, _) => 0.9f,

                // 雪天：陆军攻击-20%
                (WeatherType.Snow, UnitDomain.Land) => 0.8f,

                // 雾天：命中率-30%
                (WeatherType.Fog, _) => 0.7f,

                // 暴风雨：海军攻击-30%，空军无法起飞
                (WeatherType.Storm, UnitDomain.Sea) => 0.7f,
                (WeatherType.Storm, UnitDomain.Air) => 0.0f,

                _ => 1.0f
            };
        }

        // ========== 移动成本验证 ==========

        /// <summary>
        /// 验证单位是否有足够移动力
        /// </summary>
        public static MovementValidation ValidateMovement(
            CombatUnit unit,
            MapNode current,
            MapNode target,
            RouteType? routeType)
        {
            MovementValidation validation = new MovementValidation();

            // 计算移动成本
            int cost = CalculateMovementCost(current, target, unit.Domain, routeType);

            if (cost == int.MaxValue)
            {
                validation.CanMove = false;
                validation.Reason = $"地形不兼容，{unit.Domain}单位无法移动到{target.Terrain}";
                return validation;
            }

            if (unit.RemainingMovement < cost)
            {
                validation.CanMove = false;
                validation.Reason = $"移动力不足（需要{cost}点，剩余{unit.RemainingMovement}点）";
                validation.RequiredMovement = cost;
                return validation;
            }

            validation.CanMove = true;
            validation.ActualMovementCost = cost;
            validation.Reason = $"可以移动（消耗{cost}点移动力）";

            // 检查是否需要超能力
            if (!CheckTerrainCompatibility(unit.Domain, target.Terrain))
            {
                if (unit.Scale == UnitScale.Individual && unit.CanCrossTerrain)
                {
                    validation.RequiresAbilityUse = true;
                    validation.AbilityDebtCost = (int)(TerrainBalanceConfig.TERRAIN_CROSSING_BASE_DEBT *
                        TerrainBalanceConfig.GetTerrainCrossingMultiplier(current.Terrain, target.Terrain));
                }
                else
                {
                    validation.CanMove = false;
                    validation.Reason = $"地形不兼容，且无法使用超能力跨越";
                }
            }

            return validation;
        }

        /// <summary>
        /// 检查地形兼容性
        /// </summary>
        private static bool CheckTerrainCompatibility(UnitDomain domain, TerrainType terrain)
        {
            return (domain, terrain) switch
            {
                (UnitDomain.Land, TerrainType.Land) => true,
                (UnitDomain.Land, TerrainType.Coastal) => true,
                (UnitDomain.Land, TerrainType.Sea) => false,

                (UnitDomain.Sea, TerrainType.Sea) => true,
                (UnitDomain.Sea, TerrainType.Coastal) => true,
                (UnitDomain.Sea, TerrainType.Land) => false,

                (UnitDomain.Air, _) => true,

                _ => false
            };
        }

        // ========== 调试和报告 ==========

        /// <summary>
        /// 获取移动成本报告（用于调试）
        /// </summary>
        public static string GetMovementCostReport(
            MapNode from,
            MapNode to,
            UnitDomain domain)
        {
            int baseCost = from.GetManhattanDistanceTo(to);
            float terrainMod = GetUnitTerrainCostModifier(domain, to.Terrain);

            return $@"
移动成本分析报告
============
从: {from.NodeName} ({from.Terrain})
到: {to.NodeName} ({to.Terrain})
单位: {domain}

基础成本: {baseCost}
地形修正: {terrainMod:F2}x
最终成本: {(int)Math.Ceiling(baseCost * terrainMod)}

地形效果: {GetTerrainEffects(to)}
";
        }
    }
}
