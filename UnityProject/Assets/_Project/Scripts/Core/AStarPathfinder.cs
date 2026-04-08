using System;
using System.Collections.Generic;
using ShadowOfTheUniverse.Core;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// A*路径查找算法 - 高性能路径搜索
    /// 替代原有的简单BFS，提供更优的路径查找性能
    /// </summary>
    public class AStarPathfinder
    {
        // 路径缓存
        private PathCache pathCache;

        public AStarPathfinder()
        {
            pathCache = new PathCache();
        }

        /// <summary>
        /// 查找最优路径
        /// </summary>
        public List<MapNode> FindOptimalPath(
            MapNode start,
            MapNode end,
            UnitDomain domain,
            Dictionary<string, MapNode> allNodes)
        {
            // 检查缓存
            string cacheKey = GenerateCacheKey(start, end, domain);
            List<MapNode> cachedPath = pathCache.GetCachedPath(cacheKey);
            if (cachedPath != null)
            {
                return cachedPath;
            }

            // 执行A*搜索
            List<MapNode> path = ExecuteAStar(start, end, domain, allNodes);

            // 缓存结果
            if (path.Count > 0)
            {
                pathCache.CachePath(cacheKey, path);
            }

            return path;
        }

        /// <summary>
        /// 执行A*算法
        /// </summary>
        private List<MapNode> ExecuteAStar(
            MapNode start,
            MapNode end,
            UnitDomain domain,
            Dictionary<string, MapNode> allNodes)
        {
            // 优先队列（使用简单的列表实现，可优化为二叉堆）
            var openSet = new List<MapNode>();
            var closedSet = new HashSet<string>();
            var cameFrom = new Dictionary<string, MapNode>();
            var gScore = new Dictionary<string, float>();
            var fScore = new Dictionary<string, float>();

            // 初始化
            gScore[start.NodeId] = 0;
            fScore[start.NodeId] = Heuristic(start, end);
            openSet.Add(start);

            while (openSet.Count > 0)
            {
                // 找到fScore最小的节点
                openSet.Sort((a, b) =>
                    (gScore.GetValueOrDefault(a.NodeId, float.MaxValue) + Heuristic(a, end)).CompareTo(
                     gScore.GetValueOrDefault(b.NodeId, float.MaxValue) + Heuristic(b, end)));


                MapNode current = openSet[0];
                openSet.RemoveAt(0);

                // 到达目标
                if (current.NodeId == end.NodeId)
                {
                    return ReconstructPath(cameFrom, current);
                }

                closedSet.Add(current.NodeId);

                // 检查所有相邻节点
                foreach (var connection in current.GetConnections())
                {
                    MapNode neighbor = allNodes.GetValueOrDefault(connection.TargetNodeId);
                    if (neighbor == null || closedSet.Contains(neighbor.NodeId))
                        continue;

                    // 检查路线是否适合该单位
                    if (!IsRouteValidForUnit(connection.RouteType, domain))
                        continue;

                    // 计算移动成本
                    float movementCost = GetMovementCost(current, neighbor, domain);
                    float tentativeGScore = gScore[current.NodeId] + movementCost;

                    if (tentativeGScore < gScore.GetValueOrDefault(neighbor.NodeId, float.MaxValue))
                    {
                        // 找到更优路径
                        cameFrom[neighbor.NodeId] = current;
                        gScore[neighbor.NodeId] = tentativeGScore;
                        fScore[neighbor.NodeId] = tentativeGScore + Heuristic(neighbor, end);

                        if (!openSet.Contains(neighbor))
                        {
                            openSet.Add(neighbor);
                        }
                    }
                }
            }

            // 无法到达
            return new List<MapNode>();
        }

        /// <summary>
        /// 启发式函数（曼哈顿距离）
        /// </summary>
        private float Heuristic(MapNode a, MapNode b)
        {
            return Math.Abs(a.CoordinateX - b.CoordinateX) +
                   Math.Abs(a.CoordinateY - b.CoordinateY);
        }

        /// <summary>
        /// 移动成本计算（考虑地形和单位类型）
        /// </summary>
        private float GetMovementCost(MapNode from, MapNode to, UnitDomain domain)
        {
            // 基础移动成本
            float baseCost = from.GetManhattanDistanceTo(to);

            // 地形修正
            float terrainModifier = GetTerrainMovementCost(to.Terrain, domain);

            // 路线类型修正
            RouteType? routeType = null;
            if (from.HasConnectionTo(to.NodeId, out RouteType foundRoute))
            {
                routeType = foundRoute;
            }

            float routeModifier = GetRouteMovementCost(routeType, domain);

            return baseCost * terrainModifier * routeModifier;
        }

        /// <summary>
        /// 地形移动成本
        /// </summary>
        private float GetTerrainMovementCost(TerrainType terrain, UnitDomain domain)
        {
            return (terrain, domain) switch
            {
                // 陆军地形成本
                (TerrainType.Land, UnitDomain.Land) => 1.0f,
                (TerrainType.Coastal, UnitDomain.Land) => 1.0f,
                (TerrainType.Sea, UnitDomain.Land) => float.MaxValue, // 无法通过

                // 海军地形成本
                (TerrainType.Sea, UnitDomain.Sea) => 1.0f,
                (TerrainType.Coastal, UnitDomain.Sea) => 1.0f,
                (TerrainType.Land, UnitDomain.Sea) => float.MaxValue, // 无法通过

                // 空军地形成本
                (_, UnitDomain.Air) => 0.5f, // 空军移动成本减半

                _ => 1.0f
            };
        }

        /// <summary>
        /// 路线移动成本
        /// </summary>
        private float GetRouteMovementCost(RouteType? routeType, UnitDomain domain)
        {
            if (!routeType.HasValue || domain == UnitDomain.Air)
                return 1.0f;

            return (domain, routeType.Value) switch
            {
                (UnitDomain.Land, RouteType.LandRoute) => 1.0f,
                (UnitDomain.Land, RouteType.SeaRoute) => float.MaxValue,

                (UnitDomain.Sea, RouteType.SeaRoute) => 1.0f,
                (UnitDomain.Sea, RouteType.LandRoute) => float.MaxValue,

                _ => 1.0f
            };
        }

        /// <summary>
        /// 检查路线是否适合单位
        /// </summary>
        private bool IsRouteValidForUnit(RouteType routeType, UnitDomain domain)
        {
            return (domain, routeType) switch
            {
                (UnitDomain.Land, RouteType.LandRoute) => true,
                (UnitDomain.Sea, RouteType.SeaRoute) => true,
                (UnitDomain.Air, _) => true,
                _ => false
            };
        }

        /// <summary>
        /// 重建路径
        /// </summary>
        private List<MapNode> ReconstructPath(Dictionary<string, MapNode> cameFrom, MapNode current)
        {
            var path = new List<MapNode> { current };

            while (cameFrom.ContainsKey(current.NodeId))
            {
                current = cameFrom[current.NodeId];
                path.Insert(0, current);
            }

            return path;
        }

        /// <summary>
        /// 生成缓存键
        /// </summary>
        private string GenerateCacheKey(MapNode start, MapNode end, UnitDomain domain)
        {
            return $"{start.NodeId}_{end.NodeId}_{domain}";
        }

        /// <summary>
        /// 清除缓存
        /// </summary>
        public void ClearCache()
        {
            pathCache?.Clear();
        }
    }

    /// <summary>
    /// 路径缓存（LRU）
    /// </summary>
    public class PathCache
    {
        private Dictionary<string, CacheEntry> cache;
        private const int MAX_CACHE_SIZE = 100;
        private LinkedList<string> accessOrder;

        public PathCache()
        {
            cache = new Dictionary<string, CacheEntry>();
            accessOrder = new LinkedList<string>();
        }

        public List<MapNode> GetCachedPath(string key)
        {
            if (cache.TryGetValue(key, out CacheEntry entry))
            {
                // 更新访问顺序
                accessOrder.Remove(key);
                accessOrder.AddFirst(key);

                return entry.Path;
            }
            return null;
        }

        public void CachePath(string key, List<MapNode> path)
        {
            // 如果缓存已满，移除最少使用的项
            if (cache.Count >= MAX_CACHE_SIZE)
            {
                string lruKey = accessOrder.Last.Value;
                cache.Remove(lruKey);
                accessOrder.RemoveLast();
            }

            cache[key] = new CacheEntry
            {
                Path = path,
                Timestamp = DateTime.Now
            };
            accessOrder.AddFirst(key);
        }

        public void Clear()
        {
            cache.Clear();
            accessOrder.Clear();
        }

        private class CacheEntry
        {
            public List<MapNode> Path { get; set; }
            public DateTime Timestamp { get; set; }
        }
    }
}
