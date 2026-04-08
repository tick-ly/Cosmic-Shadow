using System;
using System.Collections.Generic;
using UnityEngine;
using ShadowOfTheUniverse.Core;

namespace ShadowOfTheUniverse.Systems
{
    /// <summary>
    /// 移动管理器 - MonoBehaviour
    /// 处理单位移动、地形跨越、探索触发
    /// </summary>
    public class MovementManager : MonoBehaviour
    {
        // ========== 单例模式 ==========

        private static MovementManager instance;
        public static MovementManager Instance
        {
            get
            {
                if (instance == null)
                {
                    GameObject go = new GameObject("MovementManager");
                    instance = go.AddComponent<MovementManager>();
                }
                return instance;
            }
        }

        // ========== 移动记录 ==========

        private List<MovementRecord> movementHistory;

        // ========== 事件 ==========

        public event Action<CombatUnit, MapNode, MapNode> OnUnitMoved;
        public event Action<CombatUnit, MapNode> OnUnitExplored;
        public event Action<CombatUnit, int> OnAbilityUsedForMovement;

        // ========== 初始化 ==========

        private void Awake()
        {
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }

            instance = this;
            movementHistory = new List<MovementRecord>();
        }

        // ========== 移动执行 ==========

        /// <summary>
        /// 尝试移动单位到目标节点
        /// </summary>
        public MovementResult MoveUnit(CombatUnit unit, MapNode targetNode)
        {
            MovementResult result = new MovementResult
            {
                Success = false,
                Unit = unit,
                TargetNode = targetNode
            };

            // 检查地图是否初始化
            if (!MapManager.Instance.IsInitialized)
            {
                result.ErrorMessage = "地图未初始化";
                return result;
            }

            // 获取当前节点
            if (string.IsNullOrEmpty(unit.CurrentNodeId))
            {
                result.ErrorMessage = "单位当前位置无效";
                return result;
            }

            MapNode currentNode = MapManager.Instance.GetNode(unit.CurrentNodeId);
            if (currentNode == null)
            {
                result.ErrorMessage = "无法找到当前节点";
                return result;
            }

            result.SourceNode = currentNode;

            // 检查是否可以移动
            RouteType? routeType = null;
            if (currentNode.HasConnectionTo(targetNode.NodeId, out RouteType foundRoute))
            {
                routeType = foundRoute;
            }

            MovementValidation validation = unit.CanMoveTo(currentNode, targetNode, routeType);

            if (!validation.CanMove)
            {
                result.ErrorMessage = validation.Reason;
                return result;
            }

            // 如果需要使用能力跨越地形
            if (validation.RequiresAbilityUse)
            {
                // 检查现实债务是否允许
                if (unit.RealityDebt >= 800)
                {
                    result.ErrorMessage = "现实债务过高，无法使用超能力跨越地形";
                    return result;
                }

                result.AbilityUsed = true;
                result.AbilityDebtCost = validation.AbilityDebtCost;

                // 触发能力使用事件
                OnAbilityUsedForMovement?.Invoke(unit, validation.AbilityDebtCost);
            }

            // 执行移动
            unit.ExecuteMovement(targetNode, validation.RequiresAbilityUse);

            // 记录移动历史
            movementHistory.Add(new MovementRecord
            {
                Unit = unit,
                SourceNode = currentNode,
                TargetNode = targetNode,
                Timestamp = DateTime.Now,
                AbilityUsed = result.AbilityUsed
            });

            // 触发探索（如果是未探索节点）
            if (targetNode.Visibility == NodeVisibility.Hidden)
            {
                targetNode.Explore();
                result.ExplorationTriggered = true;
                OnUnitExplored?.Invoke(unit, targetNode);

                Debug.Log($"[MovementManager] 单位 {unit.Name} 发现新区域: {targetNode.NodeName}");
            }

            // 更新视野
            UpdateUnitVision(unit);

            // 触发移动事件
            OnUnitMoved?.Invoke(unit, currentNode, targetNode);

            result.Success = true;
            result.Message = $"成功移动到 {targetNode.NodeName}";

            Debug.Log($"[MovementManager] {unit.Name} 从 {currentNode.NodeName} 移动到 {targetNode.NodeName}");

            return result;
        }

        // ========== 批量移动 ==========

        public List<MovementResult> MoveUnits(List<CombatUnit> units, MapNode targetNode)
        {
            List<MovementResult> results = new List<MovementResult>();

            foreach (var unit in units)
            {
                results.Add(MoveUnit(unit, targetNode));
            }

            return results;
        }

        // ========== 视野更新 ==========

        private void UpdateUnitVision(CombatUnit unit)
        {
            List<string> visibleNodes = TerrainCombatResolver.CalculateVisibleNodes(
                unit,
                MapManager.Instance.AllNodes
            );

            foreach (string nodeId in visibleNodes)
            {
                MapNode node = MapManager.Instance.GetNode(nodeId);
                if (node != null)
                {
                    node.SetVisible();
                    node.Explore();
                }
            }
        }

        // ========== 路径移动 ==========

        public List<MovementResult> MoveUnitAlongPath(CombatUnit unit, List<MapNode> path)
        {
            List<MovementResult> results = new List<MovementResult>();

            foreach (MapNode node in path)
            {
                MovementResult result = MoveUnit(unit, node);
                results.Add(result);

                // 如果移动失败，停止路径
                if (!result.Success)
                {
                    break;
                }

                // 如果移动力耗尽，停止路径
                if (unit.RemainingMovement <= 0 && unit.Domain != UnitDomain.Air)
                {
                    break;
                }
            }

            return results;
        }

        // ========== 回合管理 ==========

        public void ResetUnitMovement(List<CombatUnit> units)
        {
            foreach (var unit in units)
            {
                unit.ResetForNewTurn();
            }

            Debug.Log("[MovementManager] 所有单位移动力已重置");
        }

        // ========== 可移动节点查询 ==========

        public List<MapNode> GetMovableNodes(CombatUnit unit)
        {
            List<MapNode> movableNodes = new List<MapNode>();

            if (string.IsNullOrEmpty(unit.CurrentNodeId))
                return movableNodes;

            MapNode currentNode = MapManager.Instance.GetNode(unit.CurrentNodeId);
            if (currentNode == null)
                return movableNodes;

            // 空军：作战半径内的所有节点
            if (unit.Domain == UnitDomain.Air)
            {
                foreach (var node in MapManager.Instance.NodeList)
                {
                    if (node.NodeId == currentNode.NodeId)
                        continue;

                    float distance = currentNode.GetDistanceTo(node);
                    if (distance <= unit.OperationRange)
                    {
                        movableNodes.Add(node);
                    }
                }
            }
            // 陆军和海军：通过路线连接的节点
            else
            {
                foreach (var connection in currentNode.GetConnections())
                {
                    MapNode neighbor = MapManager.Instance.GetNode(connection.TargetNodeId);
                    if (neighbor != null && unit.RemainingMovement > 0)
                    {
                        MovementValidation validation = unit.CanMoveTo(
                            currentNode,
                            neighbor,
                            connection.RouteType
                        );

                        if (validation.CanMove)
                        {
                            movableNodes.Add(neighbor);
                        }
                    }
                }
            }

            return movableNodes;
        }

        // ========== 移动历史查询 ==========

        public List<MovementRecord> GetMovementHistory(CombatUnit unit)
        {
            return movementHistory.FindAll(r => r.Unit == unit);
        }

        public void ClearHistory()
        {
            movementHistory.Clear();
        }
    }

    // ========== 数据结构 ==========

    /// <summary>
    /// 移动结果
    /// </summary>
    [Serializable]
    public class MovementResult
    {
        public bool Success { get; set; }
        public string Message { get; set; }
        public string ErrorMessage { get; set; }

        public CombatUnit Unit { get; set; }
        public MapNode SourceNode { get; set; }
        public MapNode TargetNode { get; set; }

        public bool AbilityUsed { get; set; }
        public int AbilityDebtCost { get; set; }

        public bool ExplorationTriggered { get; set; }
    }

    /// <summary>
    /// 移动记录
    /// </summary>
    [Serializable]
    public class MovementRecord
    {
        public CombatUnit Unit { get; set; }
        public MapNode SourceNode { get; set; }
        public MapNode TargetNode { get; set; }
        public DateTime Timestamp { get; set; }
        public bool AbilityUsed { get; set; }
    }
}
