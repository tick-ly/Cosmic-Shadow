using System;
using System.Collections.Generic;
using ShadowOfTheUniverse.Data;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// 战斗单位数据模型 - 扩展自Character，支持地形移动和海陆空分类
    /// 纯C#类，不继承MonoBehaviour
    /// </summary>
    [Serializable]
    public class CombatUnit : Character
    {
        // ========== 单位分类 ==========

        public UnitDomain Domain { get; private set; }    // 领域（海陆空）
        public UnitScale Scale { get; private set; }      // 编制（队伍/单兵）

        // ========== 移动属性 ==========

        public int BaseMovementRange { get; private set; }  // 基础移动范围
        public int RemainingMovement { get; set; }          // 剩余移动力

        // ========== 作战半径（空军专用） ==========

        public int OperationRange { get; private set; }

        // ========== 视野范围 ==========

        public int VisionRange { get; private set; }

        // ========== 当前位置 ==========

        public string CurrentNodeId { get; set; }

        // ========== 特殊能力 ==========

        public bool CanCrossTerrain { get; private set; }  // 是否能跨越地形（超能力者）
        public int TerrainCrossingDebtCost { get; private set; }  // 跨越地形的债务代价

        // ========== 构造函数 ==========

        public CombatUnit(string name, BloodlineTier tier, CharacterClassSO classData,
                         UnitDomain domain, UnitScale scale, int maxHealth = 100)
            : base(name, tier, classData, maxHealth)
        {
            Domain = domain;
            Scale = scale;

            // 根据单位类型设置移动属性
            InitializeMovementProperties();

            CurrentNodeId = null;
        }

        // ========== 初始化移动属性 ==========

        private void InitializeMovementProperties()
        {
            switch (Domain)
            {
                case UnitDomain.Land:
                    BaseMovementRange = 2;
                    OperationRange = 0;
                    VisionRange = 2;
                    break;

                case UnitDomain.Sea:
                    BaseMovementRange = 3;
                    OperationRange = 0;
                    VisionRange = 3;
                    break;

                case UnitDomain.Air:
                    BaseMovementRange = 0;  // 空军不使用路线移动
                    OperationRange = 4;     // 作战半径
                    VisionRange = 4;
                    break;
            }

            // 单兵单位（超能力者）可以跨越地形
            if (Scale == UnitScale.Individual)
            {
                CanCrossTerrain = true;
                TerrainCrossingDebtCost = 30;  // 跨越地形增加30点现实债务
            }
            else
            {
                CanCrossTerrain = false;
                TerrainCrossingDebtCost = 0;
            }

            RemainingMovement = BaseMovementRange;
        }

        // ========== 地形通行检查 ==========

        /// <summary>
        /// 检查是否能移动到目标节点
        /// </summary>
        public MovementValidation CanMoveTo(MapNode currentNode, MapNode targetNode, RouteType? routeType)
        {
            MovementValidation validation = new MovementValidation();

            // 空军：检查作战半径
            if (Domain == UnitDomain.Air)
            {
                float distance = currentNode.GetDistanceTo(targetNode);
                if (distance <= OperationRange)
                {
                    validation.CanMove = true;
                    validation.Reason = "在作战半径内";
                }
                else
                {
                    validation.CanMove = false;
                    validation.Reason = $"超出作战半径 ({distance:F1} > {OperationRange})";
                }
                return validation;
            }

            // 常规单位：检查地形和路线类型
            bool terrainValid = CheckTerrainCompatibility(targetNode.Terrain);

            if (!terrainValid)
            {
                // 地形不兼容，但如果是单兵单位可以使用超能力跨越
                if (CanCrossTerrain)
                {
                    validation.CanMove = true;
                    validation.RequiresAbilityUse = true;
                    validation.AbilityDebtCost = TerrainCrossingDebtCost;
                    validation.Reason = "地形不兼容，但可以使用超能力跨越（增加现实债务）";
                }
                else
                {
                    validation.CanMove = false;
                    validation.Reason = $"{Domain}单位无法进入{targetNode.Terrain}地形";
                }
                return validation;
            }

            // 检查是否通过正确的路线类型
            if (routeType.HasValue)
            {
                bool routeValid = CheckRouteCompatibility(routeType.Value);
                if (!routeValid)
                {
                    validation.CanMove = false;
                    validation.Reason = $"无法通过{routeType.Value}移动";
                    return validation;
                }
            }

            // 检查移动力
            if (RemainingMovement <= 0)
            {
                validation.CanMove = false;
                validation.Reason = "移动力不足";
                return validation;
            }

            validation.CanMove = true;
            validation.Reason = "可以移动";
            return validation;
        }

        // ========== 地形兼容性检查 ==========

        private bool CheckTerrainCompatibility(TerrainType terrain)
        {
            return (Domain, terrain) switch
            {
                // 陆军：陆地和沿海
                (UnitDomain.Land, TerrainType.Land) => true,
                (UnitDomain.Land, TerrainType.Coastal) => true,
                (UnitDomain.Land, TerrainType.Sea) => false,

                // 海军：水域和沿海
                (UnitDomain.Sea, TerrainType.Sea) => true,
                (UnitDomain.Sea, TerrainType.Coastal) => true,
                (UnitDomain.Sea, TerrainType.Land) => false,

                // 空军：所有地形
                (UnitDomain.Air, _) => true,

                _ => false
            };
        }

        private bool CheckRouteCompatibility(RouteType routeType)
        {
            return (Domain, routeType) switch
            {
                // 陆军：公路/铁路
                (UnitDomain.Land, RouteType.LandRoute) => true,
                (UnitDomain.Land, RouteType.SeaRoute) => false,
                (UnitDomain.Land, RouteType.AirRoute) => false,

                // 海军：航道
                (UnitDomain.Sea, RouteType.SeaRoute) => true,
                (UnitDomain.Sea, RouteType.LandRoute) => false,
                (UnitDomain.Sea, RouteType.AirRoute) => false,

                // 空军：不需要路线
                (UnitDomain.Air, _) => true,

                _ => false
            };
        }

        // ========== 移动执行 ==========

        public void ExecuteMovement(MapNode targetNode, bool usedAbilityToCross = false)
        {
            CurrentNodeId = targetNode.NodeId;

            // 空军不消耗移动力，但有作战半径限制
            if (Domain != UnitDomain.Air)
            {
                RemainingMovement--;
            }

            // 如果使用超能力跨越地形，增加现实债务
            if (usedAbilityToCross)
            {
                AddRealityDebt(TerrainCrossingDebtCost);
            }
        }

        // ========== 回合重置 ==========

        public void ResetForNewTurn()
        {
            RemainingMovement = BaseMovementRange;
        }

        // ========== 获取地形战斗加成 ==========

        public float GetTerrainCombatBonus(TerrainType terrain)
        {
            // 根据单位和地形返回战斗加成
            return (Domain, terrain) switch
            {
                // 海军在海洋战斗有加成
                (UnitDomain.Sea, TerrainType.Sea) => 1.2f,
                (UnitDomain.Sea, TerrainType.Coastal) => 1.1f,

                // 陆军在陆地战斗有加成
                (UnitDomain.Land, TerrainType.Land) => 1.15f,
                (UnitDomain.Land, TerrainType.Coastal) => 1.05f,

                // 空军在任何地形都有轻微加成
                (UnitDomain.Air, _) => 1.1f,

                // 不利地形战斗惩罚
                (UnitDomain.Land, TerrainType.Sea) => 0.5f,
                (UnitDomain.Sea, TerrainType.Land) => 0.5f,

                _ => 1.0f
            };
        }
    }

    /// <summary>
    /// 移动验证结果（扩展版）
    /// </summary>
    [Serializable]
    public class MovementValidation
    {
        public bool CanMove { get; set; }
        public string Reason { get; set; }
        public bool RequiresAbilityUse { get; set; }
        public int AbilityDebtCost { get; set; }

        // ========== 新增：移动成本信息 ==========

        public int ActualMovementCost { get; set; }        // 实际消耗的移动力
        public int RequiredMovement { get; set; }          // 需要的移动力（失败时）
        public float TerrainModifier { get; set; }         // 地形修正系数
        public MovementCostSystem.TerrainEffect TerrainEffects { get; set; } // 地形特殊效果

        public MovementValidation()
        {
            CanMove = false;
            Reason = "";
            RequiresAbilityUse = false;
            AbilityDebtCost = 0;
            ActualMovementCost = 1;
            RequiredMovement = 0;
            TerrainModifier = 1.0f;
            TerrainEffects = MovementCostSystem.TerrainEffect.None;
        }
    }
}
