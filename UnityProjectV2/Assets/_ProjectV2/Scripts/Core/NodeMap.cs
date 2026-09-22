using System;
using System.Collections.Generic;

namespace ShadowOfTheUniverse.V2.Core
{
    [Serializable]
    public sealed class NodeDefinition
    {
        public string Id;
        public string DisplayName;
        public TerrainType Terrain;
        public NodeOwner Owner;
        public int DangerLevel;
        public float X;
        public float Y;
        public float Elevation;
        public int Exposure;
        public int CoverRating;
        public bool PoweredGuard;
        public NodeInteraction Interaction;
    }

    [Serializable]
    public sealed class RouteDefinition
    {
        public string FromNodeId;
        public string ToNodeId;
        public RouteType RouteType;
    }

    public sealed class NodeMap
    {
        private readonly Dictionary<string, NodeDefinition> nodes = new Dictionary<string, NodeDefinition>();
        private readonly List<RouteDefinition> routes = new List<RouteDefinition>();

        public IReadOnlyDictionary<string, NodeDefinition> Nodes
        {
            get { return nodes; }
        }

        public IReadOnlyList<RouteDefinition> Routes
        {
            get { return routes; }
        }

        public void AddNode(NodeDefinition node)
        {
            if (node == null || string.IsNullOrWhiteSpace(node.Id))
            {
                throw new ArgumentException("Node must have an id.");
            }

            nodes[node.Id] = node;
        }

        public void AddRoute(RouteDefinition route)
        {
            if (route == null || string.IsNullOrWhiteSpace(route.FromNodeId) || string.IsNullOrWhiteSpace(route.ToNodeId))
            {
                throw new ArgumentException("Route must have from/to node ids.");
            }

            routes.Add(route);
        }

        public NodeDefinition GetNode(string nodeId)
        {
            return nodes.TryGetValue(nodeId, out NodeDefinition node) ? node : null;
        }

        public bool TryGetRoute(string fromNodeId, string toNodeId, out RouteDefinition route)
        {
            for (int i = 0; i < routes.Count; i++)
            {
                RouteDefinition candidate = routes[i];
                bool forward = candidate.FromNodeId == fromNodeId && candidate.ToNodeId == toNodeId;
                bool backward = candidate.FromNodeId == toNodeId && candidate.ToNodeId == fromNodeId;
                if (forward || backward)
                {
                    route = candidate;
                    return true;
                }
            }

            route = null;
            return false;
        }

        public bool CanUnitUseRoute(UnitState unit, RouteDefinition route)
        {
            if (unit == null || route == null)
            {
                return false;
            }

            if (unit.Domain == UnitDomain.Air)
            {
                return true;
            }

            if (unit.Domain == UnitDomain.Land)
            {
                return route.RouteType == RouteType.LandRoute;
            }

            return route.RouteType == RouteType.SeaRoute;
        }

        public bool CanUnitEnterNode(UnitState unit, NodeDefinition node)
        {
            if (unit == null || node == null || node.Terrain == TerrainType.DeadZone)
            {
                return false;
            }

            if (unit.Domain == UnitDomain.Air || unit.Scale == UnitScale.Individual)
            {
                return true;
            }

            if (unit.Domain == UnitDomain.Land)
            {
                return node.Terrain == TerrainType.Land || node.Terrain == TerrainType.Coastal;
            }

            return node.Terrain == TerrainType.Sea || node.Terrain == TerrainType.Coastal;
        }
    }
}
