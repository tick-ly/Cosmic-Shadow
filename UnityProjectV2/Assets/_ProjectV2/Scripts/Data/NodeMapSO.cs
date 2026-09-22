using System;
using ShadowOfTheUniverse.V2.Core;
using UnityEngine;

namespace ShadowOfTheUniverse.V2.Data
{
    [CreateAssetMenu(fileName = "V2NodeMap", menuName = "Shadow of the Universe/V2/Node Map")]
    public sealed class NodeMapSO : ScriptableObject
    {
        [Serializable]
        public sealed class NodeConfig
        {
            public string nodeId = "node";
            public string displayName = "Node";
            public TerrainType terrain = TerrainType.Land;
            public NodeOwner owner = NodeOwner.Neutral;
            public int dangerLevel = 1;
            public Vector2 position;
            public float elevation;
            public int exposure;
            public int coverRating;
            public bool poweredGuard;
            public NodeInteraction interaction;
        }

        [Serializable]
        public sealed class RouteConfig
        {
            public string fromNodeId;
            public string toNodeId;
            public RouteType routeType = RouteType.LandRoute;
        }

        [SerializeField] private NodeConfig[] nodes;
        [SerializeField] private RouteConfig[] routes;

        public NodeConfig[] Nodes
        {
            get { return nodes; }
        }

        public RouteConfig[] Routes
        {
            get { return routes; }
        }

        public NodeMap ToRuntimeMap()
        {
            NodeMap map = new NodeMap();

            if (nodes != null)
            {
                for (int i = 0; i < nodes.Length; i++)
                {
                    NodeConfig source = nodes[i];
                    if (source == null || string.IsNullOrWhiteSpace(source.nodeId))
                    {
                        continue;
                    }

                    map.AddNode(new NodeDefinition
                    {
                        Id = source.nodeId,
                        DisplayName = source.displayName,
                        Terrain = source.terrain,
                        Owner = source.owner,
                        DangerLevel = source.dangerLevel,
                        X = source.position.x,
                        Y = source.position.y,
                        Elevation = source.elevation,
                        Exposure = source.exposure,
                        CoverRating = source.coverRating,
                        PoweredGuard = source.poweredGuard,
                        Interaction = source.interaction
                    });
                }
            }

            if (routes != null)
            {
                for (int i = 0; i < routes.Length; i++)
                {
                    RouteConfig source = routes[i];
                    if (source == null || string.IsNullOrWhiteSpace(source.fromNodeId) || string.IsNullOrWhiteSpace(source.toNodeId))
                    {
                        continue;
                    }

                    map.AddRoute(new RouteDefinition
                    {
                        FromNodeId = source.fromNodeId,
                        ToNodeId = source.toNodeId,
                        RouteType = source.routeType
                    });
                }
            }

            return map;
        }

#if UNITY_EDITOR
        public void ConfigureForEditor(NodeConfig[] mapNodes, RouteConfig[] mapRoutes)
        {
            nodes = mapNodes;
            routes = mapRoutes;
        }
#endif
    }
}
