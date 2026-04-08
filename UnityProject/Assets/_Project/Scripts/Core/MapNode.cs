using System;
using System.Collections.Generic;
using UnityEngine;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// 地图节点数据模型 - 纯C#类
    /// 包含地形、视野、控制权等信息
    /// </summary>
    [Serializable]
    public class MapNode
    {
        // ========== 基础信息 ==========

        public string NodeId { get; private set; }
        public string NodeName { get; private set; }
        public TerrainType Terrain { get; private set; }
        public TerrainType OriginalTerrain { get; private set; }
        public bool IsAnomalyActive { get; private set; }

        // ========== 位置信息 ==========

        public int CoordinateX { get; private set; }
        public int CoordinateY { get; private set; }
        public float WorldX { get; private set; }
        public float WorldY { get; private set; }
        public float SurfaceHeight { get; private set; }
        public Vector3 WorldPosition => new Vector3(WorldX, SurfaceHeight, WorldY);

        // ========== 连接信息 ==========

        private List<RouteConnection> connections;

        // ========== 视野与探索 ==========

        public NodeVisibility Visibility { get; set; }
        public int VisionRange { get; private set; }  // 视野范围

        // ========== 控制权 ==========

        public NodeOwner Owner { get; set; }
        public int GarrisonStrength { get; set; }  // 驻军强度

        // ========== 资源与战略价值 ==========

        public int StrategicValue { get; private set; }
        public int ResourceValue { get; private set; }

        // ========== 防御加成 ==========

        public float DefenseBonus { get; private set; }

        // ========== 空间折叠相关 ==========

        /// <summary>
        /// 是否为空间折叠的入口节点（虫洞起点）
        /// </summary>
        public bool IsPortalEntry { get; set; }

        /// <summary>
        /// 是否为空间折叠的出口节点（虫洞终点）
        /// </summary>
        public bool IsPortalExit { get; set; }

        /// <summary>
        /// 如果是出口节点，记录它链接的入口节点ID
        /// </summary>
        public string LinkedPortalEntryId { get; set; }

        /// <summary>
        /// 如果是入口节点，记录它链接的出口节点ID
        /// </summary>
        public string LinkedPortalExitId { get; set; }

        /// <summary>
        /// 是否只是空间折叠视觉效果（不影响实际地形，仅用于渲染）
        /// </summary>
        public bool IsSpatialFoldingVisual { get; private set; }

        /// <summary>
        /// 标记为空间折叠视觉效果（不影响可通行性和原有地形）
        /// </summary>
        public void MarkAsSpatialFoldingVisual()
        {
            IsSpatialFoldingVisual = true;
        }

        /// <summary>
        /// 清除空间折叠视觉效果
        /// </summary>
        public void ClearSpatialFoldingVisual()
        {
            IsSpatialFoldingVisual = false;
        }

        // ========== 构造函数 ==========

        public MapNode(string nodeId, string nodeName, TerrainType terrain,
                      int x, int y, int strategicValue = 0, int resourceValue = 0,
                      float? worldX = null, float? worldY = null, float worldHeight = 0f)
        {
            NodeId = nodeId;
            NodeName = nodeName;
            Terrain = terrain;
            OriginalTerrain = terrain;
            IsAnomalyActive = false;

            CoordinateX = x;
            CoordinateY = y;
            WorldX = worldX ?? x;
            WorldY = worldY ?? y;
            SurfaceHeight = worldHeight;

            connections = new List<RouteConnection>();

            Visibility = NodeVisibility.Hidden;
            VisionRange = 1; // 默认视野范围

            Owner = NodeOwner.None;
            GarrisonStrength = 0;

            StrategicValue = strategicValue;
            ResourceValue = resourceValue;

            // 根据地形设置防御加成
            DefenseBonus = CalculateDefenseBonus(terrain);
        }

        public void SetWorldPosition(float worldX, float worldY, float worldHeight = 0f)
        {
            WorldX = worldX;
            WorldY = worldY;
            SurfaceHeight = worldHeight;
        }

        // ========== 连接管理 ==========

        public void AddConnection(MapNode targetNode, RouteType routeType)
        {
            if (targetNode == null || targetNode.NodeId == this.NodeId)
                return;

            // 检查是否已存在连接
            if (!connections.Exists(c => c.TargetNodeId == targetNode.NodeId))
            {
                connections.Add(new RouteConnection(targetNode.NodeId, routeType));
            }
        }

        public IReadOnlyList<RouteConnection> GetConnections()
        {
            return connections.AsReadOnly();
        }

        public bool HasConnectionTo(string targetNodeId, out RouteType routeType)
        {
            routeType = RouteType.LandRoute;
            foreach (var conn in connections)
            {
                if (conn.TargetNodeId == targetNodeId)
                {
                    routeType = conn.RouteType;
                    return true;
                }
            }
            return false;
        }

        // ========== 地形相关 ==========

        public bool IsLandNode()
        {
            return Terrain == TerrainType.Land || Terrain == TerrainType.Coastal;
        }

        public bool IsSeaNode()
        {
            return Terrain == TerrainType.Sea || Terrain == TerrainType.Coastal;
        }

        private float CalculateDefenseBonus(TerrainType terrain)
        {
            return terrain switch
            {
                TerrainType.Coastal => 1.15f,  // 沿海防御+15%
                TerrainType.Land => 1.10f,     // 陆地防御+10%
                TerrainType.Sea => 1.0f,       // 海洋无防御加成
                _ => 1.0f
            };
        }

        // ========== 物理异常/超能力相关 ==========

        public void ApplyAnomaly(TerrainType newTerrain)
        {
            Terrain = newTerrain;
            IsAnomalyActive = true;
            // 重新计算防御加成
            DefenseBonus = CalculateDefenseBonus(Terrain);
        }

        public void RevertAnomaly()
        {
            Terrain = OriginalTerrain;
            IsAnomalyActive = false;
            // 恢复防御加成
            DefenseBonus = CalculateDefenseBonus(Terrain);
        }

        // ========== 视野相关 ==========

        public void Explore()
        {
            if (Visibility == NodeVisibility.Hidden)
            {
                Visibility = NodeVisibility.Fogged;
            }
        }

        public void SetVisible()
        {
            Visibility = NodeVisibility.Visible;
        }

        public void SetFogged()
        {
            if (Visibility == NodeVisibility.Visible)
            {
                Visibility = NodeVisibility.Fogged;
            }
        }

        // ========== 距离计算 ==========

        public float GetDistanceTo(MapNode other)
        {
            int dx = CoordinateX - other.CoordinateX;
            int dy = CoordinateY - other.CoordinateY;
            return (float)Math.Sqrt(dx * dx + dy * dy);
        }

        public int GetManhattanDistanceTo(MapNode other)
        {
            return Math.Abs(CoordinateX - other.CoordinateX) +
                   Math.Abs(CoordinateY - other.CoordinateY);
        }
    }

    /// <summary>
    /// 路线连接
    /// </summary>
    [Serializable]
    public class RouteConnection
    {
        public string TargetNodeId { get; private set; }
        public RouteType RouteType { get; private set; }

        public RouteConnection(string targetNodeId, RouteType routeType)
        {
            TargetNodeId = targetNodeId;
            RouteType = routeType;
        }
    }
}
