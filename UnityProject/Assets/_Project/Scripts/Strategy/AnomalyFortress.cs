using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using ShadowOfTheUniverse.Core;
using ShadowOfTheUniverse.Systems;

namespace ShadowOfTheUniverse.Strategy
{
    public enum AnomalyType
    {
        None,
        DensityAlteration, // 密度修改（固态海洋）
        SpatialFolding     // 空间折叠：创建虫洞，连接远距离节点
    }

    /// <summary>
    /// 超能力异常堡垒组件，挂载在防守方的特殊 Capture Point 上
    /// 会动态修改周围一圈格子的地形属性，形成 Boss 领域。
    /// </summary>
    public class AnomalyFortress : MonoBehaviour
    {
        [Header("异常设定")]
        public AnomalyType anomalyType = AnomalyType.DensityAlteration;
        public int auraRadius = 3;

        [Header("空间折叠专用")]
        [Tooltip("空间折叠时，虫洞出口节点与入口的最小曼哈顿距离")]
        public int minPortalDistance = 8;

        [Header("空间折叠专用")]
        [Tooltip("空间折叠时，虫洞出口节点与入口的最大曼哈顿距离")]
        public int maxPortalDistance = 15;

        [Header("空间折叠专用")]
        [Tooltip("空间折叠时，入口节点的光环视觉半径（格子数）")]
        public int portalEntryAuraRadius = 2;

        private StarNode parentNode;
        private MapNode parentMapNode;
        private List<MapNode> affectedNodes = new List<MapNode>();

        /// <summary>
        /// 空间折叠的出口节点
        /// </summary>
        private MapNode portalExitNode;

        private void Start()
        {
            parentNode = GetComponent<StarNode>();
            // 延迟一小会儿，确保 MapManager 生成完毕
            Invoke(nameof(ActivateAura), 1.0f);
        }

        public void ActivateAura()
        {
            if (MapManager.Instance == null || !MapManager.Instance.IsInitialized) return;

            // 获取中心节点的坐标
            Vector3 worldPos = transform.position;
            int centerX = Mathf.RoundToInt(worldPos.x);
            int centerY = Mathf.RoundToInt(worldPos.z);

            // 找到对应的 MapNode
            parentMapNode = parentNode != null && !string.IsNullOrEmpty(parentNode.mapNodeId)
                ? MapManager.Instance.GetNode(parentNode.mapNodeId)
                : MapManager.Instance.GetNodeAtPosition(centerX, centerY);

            affectedNodes.Clear();

            switch (anomalyType)
            {
                case AnomalyType.DensityAlteration:
                    ActivateDensityAlteration(centerX, centerY);
                    break;
                case AnomalyType.SpatialFolding:
                    ActivateSpatialFolding(centerX, centerY);
                    break;
            }

            // 通知 MapManager 刷新受影响区域的视觉表现
            MapManager.Instance.RefreshTileVisuals(affectedNodes);
            Debug.Log($"[AnomalyFortress] {parentNode?.nodeName} 的异常光环已激活，影响了 {affectedNodes.Count} 个区块。");
        }

        /// <summary>
        /// 密度修改异常：将海洋变为可通行的固态海洋（沿海地形）
        /// </summary>
        private void ActivateDensityAlteration(int centerX, int centerY)
        {
            for (int x = centerX - auraRadius; x <= centerX + auraRadius; x++)
            {
                for (int y = centerY - auraRadius; y <= centerY + auraRadius; y++)
                {
                    if (Vector2.Distance(new Vector2(centerX, centerY), new Vector2(x, y)) > auraRadius)
                        continue;

                    MapNode node = MapManager.Instance.GetNodeAtPosition(x, y);
                    if (node != null && node.Terrain == TerrainType.Sea)
                    {
                        node.ApplyAnomaly(TerrainType.Coastal);
                        affectedNodes.Add(node);
                    }
                }
            }
        }

        /// <summary>
        /// 空间折叠异常：在堡垒处创建虫洞入口，在远处随机位置创建虫洞出口
        /// 形成"捷径"效果，影响路径查找
        /// </summary>
        private void ActivateSpatialFolding(int centerX, int centerY)
        {
            // 1. 找到符合条件的出口节点（距离足够的陆地/沿海节点）
            MapNode exitNode = FindPortalExitNode(centerX, centerY);
            if (exitNode == null)
            {
                Debug.LogWarning($"[AnomalyFortress] {parentNode?.nodeName} 未能找到合适的空间折叠出口节点。");
                return;
            }

            portalExitNode = exitNode;

            // 2. 标记入口节点
            if (parentMapNode != null)
            {
                parentMapNode.IsPortalEntry = true;
                parentMapNode.LinkedPortalExitId = exitNode.NodeId;
                affectedNodes.Add(parentMapNode);
            }

            // 3. 标记出口节点
            exitNode.IsPortalExit = true;
            exitNode.LinkedPortalEntryId = parentMapNode?.NodeId;
            affectedNodes.Add(exitNode);

            // 4. 在入口节点周围生成空间折叠视觉效果（不影响原有地形）
            for (int x = centerX - portalEntryAuraRadius; x <= centerX + portalEntryAuraRadius; x++)
            {
                for (int y = centerY - portalEntryAuraRadius; y <= centerY + portalEntryAuraRadius; y++)
                {
                    if (Vector2.Distance(new Vector2(centerX, centerY), new Vector2(x, y)) > portalEntryAuraRadius)
                        continue;

                    MapNode node = MapManager.Instance.GetNodeAtPosition(x, y);
                    if (node != null && !affectedNodes.Contains(node))
                    {
                        // 标记为空间折叠视觉效果（不改变实际可通行性）
                        node.MarkAsSpatialFoldingVisual();
                        affectedNodes.Add(node);
                    }
                }
            }

            // 5. 在出口节点周围也生成视觉效果
            int exitX = exitNode.CoordinateX;
            int exitY = exitNode.CoordinateY;
            for (int x = exitX - portalEntryAuraRadius; x <= exitX + portalEntryAuraRadius; x++)
            {
                for (int y = exitY - portalEntryAuraRadius; y <= exitY + portalEntryAuraRadius; y++)
                {
                    if (Vector2.Distance(new Vector2(exitX, exitY), new Vector2(x, y)) > portalEntryAuraRadius)
                        continue;

                    MapNode node = MapManager.Instance.GetNodeAtPosition(x, y);
                    if (node != null && !affectedNodes.Contains(node))
                    {
                        node.MarkAsSpatialFoldingVisual();
                        affectedNodes.Add(node);
                    }
                }
            }

            // 6. 注册到全局虫洞注册表
            SpatialFoldRegistry.Register(parentMapNode.NodeId, exitNode.NodeId);

            Debug.Log($"[AnomalyFortress] {parentNode?.nodeName} 激活空间折叠：" +
                      $"入口={parentMapNode?.NodeName} (坐标:{centerX},{centerY})，" +
                      $"出口={exitNode.NodeName} (坐标:{exitX},{exitY})，" +
                      $"曼哈顿距离={parentMapNode?.GetManhattanDistanceTo(exitNode)}");
        }

        /// <summary>
        /// 寻找符合条件的虫洞出口节点
        /// 条件：距离入口足够远、是可通行的陆地节点、未被其他虫洞占用
        /// </summary>
        private MapNode FindPortalExitNode(int centerX, int centerY)
        {
            var allLandNodes = MapManager.Instance.NodeList.Where(n => n.IsLandNode()).ToList();
            var candidates = new List<MapNode>();

            foreach (var node in allLandNodes)
            {
                int dist = Math.Abs(node.CoordinateX - centerX) + Math.Abs(node.CoordinateY - centerY);
                if (dist >= minPortalDistance && dist <= maxPortalDistance && !node.IsPortalEntry && !node.IsPortalExit)
                {
                    candidates.Add(node);
                }
            }

            if (candidates.Count == 0) return null;

            // 优先选择距离适中的节点，避免选到地图边缘
            candidates.Sort((a, b) =>
            {
                int distA = Math.Abs(a.CoordinateX - centerX) + Math.Abs(a.CoordinateY - centerY);
                int distB = Math.Abs(b.CoordinateX - centerX) + Math.Abs(b.CoordinateY - centerY);
                // 倾向于中等距离，而非最远
                int scoreA = Math.Abs(distA - (minPortalDistance + maxPortalDistance) / 2);
                int scoreB = Math.Abs(distB - (minPortalDistance + maxPortalDistance) / 2);
                return scoreA.CompareTo(scoreB);
            });

            return candidates[0];
        }

        public void DeactivateAura()
        {
            // 解除所有受影响节点的状态
            foreach (var node in affectedNodes)
            {
                node.RevertAnomaly();
                node.ClearSpatialFoldingVisual();
            }

            // 如果是空间折叠，注销虫洞注册
            if (anomalyType == AnomalyType.SpatialFolding && parentMapNode != null)
            {
                SpatialFoldRegistry.Unregister(parentMapNode.NodeId);
            }

            portalExitNode = null;
            affectedNodes.Clear();

            MapManager.Instance.RefreshTileVisuals(affectedNodes);
            Debug.Log($"[AnomalyFortress] {parentNode?.nodeName} 的异常光环已解除。");
        }

        private void OnDestroy()
        {
            // 当据点被摧毁时，解除光环
            DeactivateAura();
        }

        private void OnDrawGizmosSelected()
        {
            Gizmos.color = anomalyType switch
            {
                AnomalyType.DensityAlteration => new Color(0, 1, 1, 0.2f),    // 青色
                AnomalyType.SpatialFolding => new Color(0.6f, 0, 1, 0.2f),   // 紫色
                _ => new Color(1, 0, 1, 0.2f)
            };

            Gizmos.DrawSphere(transform.position, auraRadius);

            // 如果是空间折叠，额外画出虫洞连线（到出口）
            if (anomalyType == AnomalyType.SpatialFolding && portalExitNode != null)
            {
                Gizmos.color = new Color(0.6f, 0, 1, 0.8f);
                Vector3 exitWorldPos = portalExitNode.WorldPosition;
                Gizmos.DrawLine(transform.position, exitWorldPos);
                Gizmos.DrawWireSphere(exitWorldPos, 1f);
            }
        }
    }

    /// <summary>
    /// 空间折叠虫洞全局注册表
    /// 管理所有激活的虫洞对，供路径查找系统查询
    /// </summary>
    public static class SpatialFoldRegistry
    {
        private static readonly Dictionary<string, string> activeFolds = new Dictionary<string, string>();
        private static readonly Dictionary<string, string> reverseFolds = new Dictionary<string, string>();

        /// <summary>
        /// 注册一个虫洞对（入口→出口）
        /// </summary>
        public static void Register(string entryNodeId, string exitNodeId)
        {
            activeFolds[entryNodeId] = exitNodeId;
            reverseFolds[exitNodeId] = entryNodeId;
        }

        /// <summary>
        /// 注销指定入口的虫洞
        /// </summary>
        public static void Unregister(string entryNodeId)
        {
            if (activeFolds.TryGetValue(entryNodeId, out string exitId))
            {
                reverseFolds.Remove(exitId);
                activeFolds.Remove(entryNodeId);
            }
        }

        /// <summary>
        /// 获取指定节点的虫洞终点ID（返回 null 表示不是虫洞入口）
        /// </summary>
        public static string GetPortalExit(string nodeId)
        {
            return activeFolds.TryGetValue(nodeId, out string exitId) ? exitId : null;
        }

        /// <summary>
        /// 获取指定节点的虫洞起点ID（返回 null 表示不是虫洞出口）
        /// </summary>
        public static string GetPortalEntry(string nodeId)
        {
            return reverseFolds.TryGetValue(nodeId, out string entryId) ? entryId : null;
        }

        /// <summary>
        /// 检查指定节点是否为虫洞节点（入口或出口）
        /// </summary>
        public static bool IsPortalNode(string nodeId)
        {
            return activeFolds.ContainsKey(nodeId) || reverseFolds.ContainsKey(nodeId);
        }

        /// <summary>
        /// 清除所有虫洞注册（地图重新生成时调用）
        /// </summary>
        public static void ClearAll()
        {
            activeFolds.Clear();
            reverseFolds.Clear();
        }
    }
}
