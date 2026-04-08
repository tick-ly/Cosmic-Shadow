using UnityEngine;
using System.Collections.Generic;
using ShadowOfTheUniverse.Core;
using ShadowOfTheUniverse.Data;

namespace ShadowOfTheUniverse.Systems
{
    /// <summary>
    /// 地形战斗系统演示 - MonoBehaviour
    /// 展示海陆空三军单位、地形系统、探索机制
    /// </summary>
    public class TerrainCombatDemo : MonoBehaviour
    {
        [Header("地图设置")]
        [SerializeField] private int mapWidth = 8;
        [SerializeField] private int mapHeight = 8;
        [SerializeField] private int seed = 12345;

        [Header("单位设置")]
        [SerializeField] private CombatUnitDataSO landSquadData;
        [SerializeField] private CombatUnitDataSO seaSquadData;
        [SerializeField] private CombatUnitDataSO airSquadData;
        [SerializeField] private CombatUnitDataSO heroUnitData;

        [Header("技能设置")]
        [SerializeField] private SkillDataSO testSkillData;

        private List<CombatUnit> playerUnits;
        private CombatUnit heroUnit;
        private MapNode selectedNode;

        private void Start()
        {
            Debug.Log("=== 地形战斗系统演示 ===");
            InitializeDemo();
        }

        private void InitializeDemo()
        {
            // 1. 生成地图
            GenerateMap();

            // 2. 创建单位
            CreateUnits();

            // 3. 放置单位到地图
            PlaceUnitsOnMap();

            // 4. 演示移动和探索
            DemonstrateMovementAndExploration();

            // 5. 演示地形战斗
            DemonstrateTerrainCombat();
        }

        private void GenerateMap()
        {
            Debug.Log("\n--- 生成地图 ---");

            // 配置地图管理器
            MapManager mapManager = MapManager.Instance;
            mapManager.SetMapSize(mapWidth, mapHeight);
            mapManager.SetSeed(seed);
            mapManager.GenerateMap();

            Debug.Log($"地图已生成: {mapWidth}x{mapHeight}");
            Debug.Log($"陆地节点: {mapManager.GetNodesByTerrain(TerrainType.Land).Count}");
            Debug.Log($"海洋节点: {mapManager.GetNodesByTerrain(TerrainType.Sea).Count}");
            Debug.Log($"沿海节点: {mapManager.GetNodesByTerrain(TerrainType.Coastal).Count}");
        }

        private void CreateUnits()
        {
            Debug.Log("\n--- 创建单位 ---");
            playerUnits = new List<CombatUnit>();

            // 创建陆军队伍
            if (landSquadData != null)
            {
                CombatUnit landSquad = landSquadData.CreateUnitInstance();
                playerUnits.Add(landSquad);
                Debug.Log($"创建陆军队伍: {landSquad.Name}");
            }
            else
            {
                // 使用默认配置
                CombatUnit landSquad = new CombatUnit(
                    "陆军作战队",
                    BloodlineTier.Low,
                    null,
                    UnitDomain.Land,
                    UnitScale.Squad,
                    100
                );
                playerUnits.Add(landSquad);
                Debug.Log($"创建陆军队伍（默认）: {landSquad.Name}");
            }

            // 创建海军队伍
            if (seaSquadData != null)
            {
                CombatUnit seaSquad = seaSquadData.CreateUnitInstance();
                playerUnits.Add(seaSquad);
                Debug.Log($"创建海军队伍: {seaSquad.Name}");
            }
            else
            {
                CombatUnit seaSquad = new CombatUnit(
                    "海军舰队",
                    BloodlineTier.Low,
                    null,
                    UnitDomain.Sea,
                    UnitScale.Squad,
                    120
                );
                playerUnits.Add(seaSquad);
                Debug.Log($"创建海军队伍（默认）: {seaSquad.Name}");
            }

            // 创建空军队伍
            if (airSquadData != null)
            {
                CombatUnit airSquad = airSquadData.CreateUnitInstance();
                playerUnits.Add(airSquad);
                Debug.Log($"创建空军队伍: {airSquad.Name}");
            }
            else
            {
                CombatUnit airSquad = new CombatUnit(
                    "空军飞行队",
                    BloodlineTier.Low,
                    null,
                    UnitDomain.Air,
                    UnitScale.Squad,
                    80
                );
                playerUnits.Add(airSquad);
                Debug.Log($"创建空军队伍（默认）: {airSquad.Name}");
            }

            // 创建英雄单位（单兵超能力者）
            if (heroUnitData != null)
            {
                heroUnit = heroUnitData.CreateUnitInstance();
            }
            else
            {
                heroUnit = new CombatUnit(
                    "零号实验体",
                    BloodlineTier.Low,
                    null,
                    UnitDomain.Land,
                    UnitScale.Individual,
                    100
                );
            }

            // 给英雄添加技能
            if (testSkillData != null)
            {
                SkillBase skill = testSkillData.CreateSkillInstance();
                heroUnit.AddSkill(skill);
            }
            else
            {
                SkillBase skill = new SkillBase(
                    "heat_transfer",
                    "热量转移",
                    BloodlineTier.Low,
                    "轻微违反热力学第二定律",
                    90, 8, 25, 10, 0,
                    new SkillEffect("成功描述", "失败描述")
                );
                heroUnit.AddSkill(skill);
            }

            playerUnits.Add(heroUnit);
            Debug.Log($"创建英雄单位: {heroUnit.Name} (单兵超能力者)");
        }

        private void PlaceUnitsOnMap()
        {
            Debug.Log("\n--- 放置单位 ---");

            // 找到合适的起始节点
            List<MapNode> landNodes = MapManager.Instance.GetNodesByTerrain(TerrainType.Land);
            List<MapNode> seaNodes = MapManager.Instance.GetNodesByTerrain(TerrainType.Sea);

            // 放置陆军和英雄到陆地
            if (landNodes.Count > 0)
            {
                MapNode landStart = landNodes[0];
                playerUnits[0].CurrentNodeId = landStart.NodeId;  // 陆军
                heroUnit.CurrentNodeId = landStart.NodeId;        // 英雄
                Debug.Log($"陆军和英雄放置在: {landStart.NodeName} ({landStart.Terrain})");
            }

            // 放置海军到水域
            if (seaNodes.Count > 0)
            {
                MapNode seaStart = seaNodes[0];
                playerUnits[1].CurrentNodeId = seaStart.NodeId;   // 海军
                Debug.Log($"海军放置在: {seaStart.NodeName} ({seaStart.Terrain})");
            }

            // 空军放置在任意位置（第一个节点）
            MapNode airStart = MapManager.Instance.NodeList[0];
            playerUnits[2].CurrentNodeId = airStart.NodeId;       // 空军
            Debug.Log($"空军放置在: {airStart.NodeName} ({airStart.Terrain})");

            // 更新视野
            MapManager.Instance.UpdateVisibility(playerUnits);
        }

        private void DemonstrateMovementAndExploration()
        {
            Debug.Log("\n=== 演示移动与探索 ===");

            // 演示1：陆军移动
            DemonstrateLandMovement();

            // 演示2：海军移动
            DemonstrateSeaMovement();

            // 演示3：空军移动
            DemonstrateAirMovement();

            // 演示4：英雄跨越地形
            DemonstrateHeroTerrainCrossing();
        }

        private void DemonstrateLandMovement()
        {
            Debug.Log("\n--- 陆军移动演示 ---");
            CombatUnit landSquad = playerUnits[0];

            MapNode currentNode = MapManager.Instance.GetNode(landSquad.CurrentNodeId);
            List<MapNode> movableNodes = MovementManager.Instance.GetMovableNodes(landSquad);

            Debug.Log($"陆军 {landSquad.Name} 在 {currentNode.NodeName} ({currentNode.Terrain})");
            Debug.Log($"可移动节点数: {movableNodes.Count}");

            if (movableNodes.Count > 0)
            {
                MapNode targetNode = movableNodes[0];
                MovementResult result = MovementManager.Instance.MoveUnit(landSquad, targetNode);

                if (result.Success)
                {
                    Debug.Log($"✓ 移动成功: {result.Message}");
                    if (result.ExplorationTriggered)
                    {
                        Debug.Log($"  发现新区域: {targetNode.NodeName}");
                    }
                }
                else
                {
                    Debug.Log($"✗ 移动失败: {result.ErrorMessage}");
                }
            }
        }

        private void DemonstrateSeaMovement()
        {
            Debug.Log("\n--- 海军移动演示 ---");
            CombatUnit seaSquad = playerUnits[1];

            MapNode currentNode = MapManager.Instance.GetNode(seaSquad.CurrentNodeId);
            List<MapNode> movableNodes = MovementManager.Instance.GetMovableNodes(seaSquad);

            Debug.Log($"海军 {seaSquad.Name} 在 {currentNode.NodeName} ({currentNode.Terrain})");
            Debug.Log($"可移动节点数: {movableNodes.Count}");

            // 尝试移动到陆地（应该失败）
            List<MapNode> landNodes = MapManager.Instance.GetNodesByTerrain(TerrainType.Land);
            if (landNodes.Count > 0)
            {
                MapNode landNode = landNodes[0];
                MovementResult result = MovementManager.Instance.MoveUnit(seaSquad, landNode);

                if (!result.Success)
                {
                    Debug.Log($"✓ 预期失败: {result.ErrorMessage}");
                }
            }
        }

        private void DemonstrateAirMovement()
        {
            Debug.Log("\n--- 空军移动演示 ---");
            CombatUnit airSquad = playerUnits[2];

            MapNode currentNode = MapManager.Instance.GetNode(airSquad.CurrentNodeId);
            List<MapNode> movableNodes = MovementManager.Instance.GetMovableNodes(airSquad);

            Debug.Log($"空军 {airSquad.Name} 在 {currentNode.NodeName}");
            Debug.Log($"作战半径: {airSquad.OperationRange}");
            Debug.Log($"可移动节点数: {movableNodes.Count} (可飞往作战半径内任意地形)");

            // 空军可以移动到任何地形
            if (movableNodes.Count > 0)
            {
                MapNode distantNode = movableNodes[movableNodes.Count / 2];
                MovementResult result = MovementManager.Instance.MoveUnit(airSquad, distantNode);

                if (result.Success)
                {
                    Debug.Log($"✓ 空军成功飞往: {distantNode.NodeName} ({distantNode.Terrain})");
                }
            }
        }

        private void DemonstrateHeroTerrainCrossing()
        {
            Debug.Log("\n--- 英雄跨越地形演示 ---");

            MapNode currentNode = MapManager.Instance.GetNode(heroUnit.CurrentNodeId);
            List<MapNode> seaNodes = MapManager.Instance.GetNodesByTerrain(TerrainType.Sea);

            if (seaNodes.Count > 0)
            {
                MapNode seaNode = seaNodes[0];
                Debug.Log($"英雄 {heroUnit.Name} 尝试跨越到海洋节点: {seaNode.NodeName}");

                MovementResult result = MovementManager.Instance.MoveUnit(heroUnit, seaNode);

                if (result.Success)
                {
                    Debug.Log($"✓ 成功跨越地形！");
                    Debug.Log($"  使用超能力: {result.AbilityUsed}");
                    Debug.Log($"  现实债务增加: {result.AbilityDebtCost}");
                    Debug.Log($"  当前债务: {heroUnit.RealityDebt}/1000");
                }
            }
        }

        private void DemonstrateTerrainCombat()
        {
            Debug.Log("\n=== 演示地形战斗 ===");

            // 创建一个敌人
            CombatUnit enemy = new CombatUnit(
                "敌方单位",
                BloodlineTier.Low,
                null,
                UnitDomain.Land,
                UnitScale.Squad,
                80
            );

            // 找一个陆地节点作为战场
            List<MapNode> landNodes = MapManager.Instance.GetNodesByTerrain(TerrainType.Land);
            if (landNodes.Count > 0)
            {
                MapNode battleNode = landNodes[0];
                enemy.CurrentNodeId = battleNode.NodeId;

                Debug.Log($"\n战场: {battleNode.NodeName} ({battleNode.Terrain})");
                Debug.Log($"防御加成: {battleNode.DefenseBonus * 100 - 100:F0}%");

                // 英雄使用技能攻击
                if (heroUnit.Skills.Count > 0)
                {
                    SkillBase skill = heroUnit.Skills[0];
                    CombatResult result = TerrainCombatResolver.ResolveTerrainCombat(
                        heroUnit,
                        enemy,
                        skill,
                        battleNode
                    );

                    Debug.Log($"\n{result.CombatLog}");

                    if (result.Success)
                    {
                        Debug.Log($"地形修正: {(result.TerrainBonus >= 0 ? "+" : "")}{result.TerrainBonus}%");
                    }
                }
            }
        }

        // ========== GUI调试面板 ==========

        private void OnGUI()
        {
            GUILayout.BeginArea(new Rect(Screen.width - 320, 10, 300, 400));
            GUILayout.BeginVertical("box");

            GUILayout.Label("=== 地形战斗系统 ===");
            GUILayout.Label($"地图节点: {MapManager.Instance.NodeList.Count}");
            GUILayout.Label($"已探索: {MapManager.Instance.GetExploredNodes().Count}");
            GUILayout.Label($"可见: {MapManager.Instance.GetVisibleNodes().Count}");

            GUILayout.Space(10);
            GUILayout.Label("=== 单位状态 ===");

            foreach (var unit in playerUnits)
            {
                GUILayout.Label($"{unit.Name} ({unit.Domain}/{unit.Scale})");
                GUILayout.Label($"  生命: {unit.CurrentHealth}/{unit.MaxHealth}");
                GUILayout.Label($"  债务: {unit.RealityDebt}/1000");
                GUILayout.Label($"  移动力: {unit.RemainingMovement}");
            }

            GUILayout.Space(10);

            if (GUILayout.Button("重新生成地图"))
            {
                MapManager.Instance.GenerateMap();
                PlaceUnitsOnMap();
            }

            if (GUILayout.Button("重置单位移动力"))
            {
                MovementManager.Instance.ResetUnitMovement(playerUnits);
            }

            if (GUILayout.Button("显示可移动节点"))
            {
                foreach (var unit in playerUnits)
                {
                    var nodes = MovementManager.Instance.GetMovableNodes(unit);
                    Debug.Log($"{unit.Name} 可移动到 {nodes.Count} 个节点");
                }
            }

            GUILayout.EndVertical();
            GUILayout.EndArea();
        }
    }
}
