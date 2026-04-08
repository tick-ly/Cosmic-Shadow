using System;
using System.Collections.Generic;
using System.Linq;
using ShadowOfTheUniverse.Core;
using UnityEngine;

namespace ShadowOfTheUniverse.Systems
{
    public class StrategyGraphBuilder
    {
        public List<MapNode> BuildNodes(
            IReadOnlyList<TerrainCell> terrainCells,
            int nodeWidth,
            int nodeHeight,
            int cellsPerNode,
            float terrainCellSize,
            Func<TerrainType, int, string> nodeNameFactory,
            Func<int> strategicValueFactory,
            Func<int> resourceValueFactory)
        {
            Dictionary<Vector2Int, TerrainCell> cellLookup = terrainCells.ToDictionary(
                cell => new Vector2Int(cell.CellX, cell.CellY),
                cell => cell);

            List<MapNode> nodes = new List<MapNode>(nodeWidth * nodeHeight);
            int nodeCounter = 0;

            for (int x = 0; x < nodeWidth; x++)
            {
                for (int y = 0; y < nodeHeight; y++)
                {
                    List<TerrainCell> blockCells = CollectBlockCells(cellLookup, x, y, cellsPerNode);
                    if (blockCells.Count == 0)
                    {
                        continue;
                    }

                    TerrainType nodeTerrain = DetermineNodeTerrain(blockCells);
                    float averageHeight = blockCells.Average(cell => cell.Height);
                    string nodeId = $"node_{x}_{y}";

                    float centerX = (x * cellsPerNode + cellsPerNode * 0.5f) * terrainCellSize;
                    float centerZ = (y * cellsPerNode + cellsPerNode * 0.5f) * terrainCellSize;

                    MapNode node = new MapNode(
                        nodeId,
                        nodeNameFactory != null ? nodeNameFactory(nodeTerrain, nodeCounter) : nodeId,
                        nodeTerrain,
                        x,
                        y,
                        strategicValueFactory != null ? strategicValueFactory() : 0,
                        resourceValueFactory != null ? resourceValueFactory() : 0,
                        worldX: centerX,
                        worldY: centerZ,
                        worldHeight: averageHeight);

                    nodes.Add(node);
                    nodeCounter++;

                    foreach (TerrainCell cell in blockCells)
                    {
                        cell.BindToStrategyNode(nodeId);
                    }
                }
            }

            return nodes;
        }

        public void BuildConnections(IReadOnlyDictionary<string, MapNode> nodes, int nodeWidth, int nodeHeight)
        {
            for (int x = 0; x < nodeWidth; x++)
            {
                for (int y = 0; y < nodeHeight; y++)
                {
                    string nodeId = $"node_{x}_{y}";
                    if (!nodes.TryGetValue(nodeId, out MapNode node))
                    {
                        continue;
                    }

                    TryConnect(node, x - 1, y, nodes);
                    TryConnect(node, x + 1, y, nodes);
                    TryConnect(node, x, y - 1, nodes);
                    TryConnect(node, x, y + 1, nodes);
                }
            }
        }

        public TerrainType DetermineNodeTerrain(IReadOnlyList<TerrainCell> cells)
        {
            int landCount = 0;
            int seaCount = 0;
            int coastalCount = 0;

            foreach (TerrainCell cell in cells)
            {
                switch (cell.Terrain)
                {
                    case TerrainType.Land:
                        landCount++;
                        break;
                    case TerrainType.Sea:
                        seaCount++;
                        break;
                    case TerrainType.Coastal:
                        coastalCount++;
                        break;
                }
            }

            if (landCount >= seaCount && landCount >= coastalCount)
            {
                return TerrainType.Land;
            }

            return seaCount >= coastalCount ? TerrainType.Sea : TerrainType.Coastal;
        }

        private static List<TerrainCell> CollectBlockCells(
            IReadOnlyDictionary<Vector2Int, TerrainCell> cellLookup,
            int nodeX,
            int nodeY,
            int cellsPerNode)
        {
            List<TerrainCell> result = new List<TerrainCell>(cellsPerNode * cellsPerNode);
            int startX = nodeX * cellsPerNode;
            int startY = nodeY * cellsPerNode;

            for (int x = startX; x < startX + cellsPerNode; x++)
            {
                for (int y = startY; y < startY + cellsPerNode; y++)
                {
                    if (cellLookup.TryGetValue(new Vector2Int(x, y), out TerrainCell cell))
                    {
                        result.Add(cell);
                    }
                }
            }

            return result;
        }

        private void TryConnect(MapNode node, int neighborX, int neighborY, IReadOnlyDictionary<string, MapNode> nodes)
        {
            string neighborId = $"node_{neighborX}_{neighborY}";
            if (!nodes.TryGetValue(neighborId, out MapNode neighbor))
            {
                return;
            }

            RouteType routeType = DetermineRouteType(node, neighbor);
            node.AddConnection(neighbor, routeType);
        }

        private static RouteType DetermineRouteType(MapNode node1, MapNode node2)
        {
            if ((node1.IsLandNode() && node2.IsLandNode()) &&
                !(node1.Terrain == TerrainType.Sea || node2.Terrain == TerrainType.Sea))
            {
                return RouteType.LandRoute;
            }

            if (node1.IsSeaNode() && node2.IsSeaNode())
            {
                return RouteType.SeaRoute;
            }

            if (node1.Terrain == TerrainType.Coastal || node2.Terrain == TerrainType.Coastal)
            {
                if (node1.IsLandNode() && node2.IsLandNode())
                {
                    return RouteType.LandRoute;
                }

                return RouteType.SeaRoute;
            }

            return RouteType.LandRoute;
        }
    }
}
