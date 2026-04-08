using System;
using ShadowOfTheUniverse.Core;

namespace ShadowOfTheUniverse.Strategy
{
    public enum UnitState
    {
        Idle,
        Moving,
        InCombat
    }

    /// <summary>
    /// 纯 C# 数据类，负责作战单位的核心逻辑与状态
    /// </summary>
    [Serializable]
    public class CombatUnitModel
    {
        public string UnitName { get; private set; }
        public UnitDomain Domain { get; private set; }
        public UnitScale Scale { get; private set; }
        
        public StarNode CurrentNode { get; private set; }
        public StarNode TargetNode { get; private set; }
        public UnitState State { get; private set; }
        public float MovementSpeed { get; private set; }

        // 构造函数
        public CombatUnitModel(string name, UnitDomain domain, UnitScale scale, StarNode startNode, float speed = 2f)
        {
            UnitName = name;
            Domain = domain;
            Scale = scale;
            CurrentNode = startNode;
            MovementSpeed = speed;
            State = UnitState.Idle;
            
            // 初始节点解锁视野
            UnlockVision(CurrentNode);
        }

        // 尝试移动到目标节点
        public bool TryMoveTo(StarNode target)
        {
            if (State != UnitState.Idle) return false;
            
            // 1. 检查是否相连 (空军可以无视连线，只要在一定距离内，这里暂且简化为必须相连)
            if (CurrentNode != null && !CurrentNode.IsConnectedTo(target))
            {
                return false;
            }

            // 2. 检查地形限制
            if (!CanTraverseTerrain(target.terrainType))
            {
                if (Scale == UnitScale.Individual)
                {
                    // 单兵可以强行跨越，但会增加现实债务 (这里仅作 Log 演示)
                    UnityEngine.Debug.LogWarning($"{UnitName} 使用了物理妥协强行跨越地形！现实债务增加！");
                }
                else
                {
                    UnityEngine.Debug.LogWarning($"{UnitName} 是常规部队，无法进入该地形！");
                    return false;
                }
            }

            TargetNode = target;
            State = UnitState.Moving;
            return true;
        }

        // 检查地形通行权限
        private bool CanTraverseTerrain(TerrainType targetTerrain)
        {
            if (Domain == UnitDomain.Air) return true; // 空军无视地形
            
            if (Domain == UnitDomain.Land)
            {
                return targetTerrain == TerrainType.Land || targetTerrain == TerrainType.Coastal;
            }
            
            if (Domain == UnitDomain.Sea)
            {
                return targetTerrain == TerrainType.Sea || targetTerrain == TerrainType.Coastal;
            }

            return false;
        }

        // 抵达目标节点
        public void OnArrival()
        {
            CurrentNode = TargetNode;
            TargetNode = null;
            State = UnitState.Idle;

            // 抵达后解锁视野
            UnlockVision(CurrentNode);

            // 通知 UI 系统
            EventManager.Instance.Emit(GameEvents.UNIT_MOVED, new UnitMoveEventData
            {
                UnitName = UnitName,
                TargetNodeName = CurrentNode?.nodeName ?? "未知"
            });
        }

        // 解锁视野逻辑
        private void UnlockVision(StarNode node)
        {
            if (node == null) return;
            
            // 当前节点变为可见
            node.SetVisibility(NodeVisibility.Visible);
            
            // 相邻节点如果未探索，则变为迷雾状态（点亮轮廓）
            foreach (var neighbor in node.connectedNodes)
            {
                if (neighbor.visibility == NodeVisibility.Hidden)
                {
                    neighbor.SetVisibility(NodeVisibility.Fogged);
                }
            }
        }
    }
}
