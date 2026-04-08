using System;
using System.Collections.Generic;
using System.Linq;
using ShadowOfTheUniverse.Core;
using ShadowOfTheUniverse.Data;
using ShadowOfTheUniverse.Strategy;
using UnityEngine;
using UnityEngine.Tilemaps;

namespace ShadowOfTheUniverse.Systems
{
    public class MapManager : MonoBehaviour
    {
        private static MapManager instance;

        public static MapManager Instance
        {
            get
            {
                if (instance == null)
                {
                    GameObject go = new GameObject("MapManager");
                    instance = go.AddComponent<MapManager>();
                }

                return instance;
            }
        }

        [Header("Map")]
        [SerializeField] private int mapWidth = 20;
        [SerializeField] private int mapHeight = 20;
        [SerializeField] private int nodeSpacing = 1;

        [Header("Terrain Ratios")]
        [SerializeField] private float landRatio = 0.5f;
        [SerializeField] private float seaRatio = 0.3f;
        [SerializeField] private float coastalRatio = 0.2f;
        [SerializeField] private int seed = 0;

        [Header("Dual Layer")]
        [SerializeField] private int terrainCellsPerNode = 3;
        [SerializeField] private float terrainCellSize = 1f;

        [Header("Generation")]
        [SerializeField] private bool generateOnStart = true;
        [SerializeField] private bool focusMainCameraOnGenerate = true;
        [SerializeField] private MapGenerationConfigSO generationConfig;

        [Header("3D Terrain")]
        [SerializeField] private bool useTerrainMesh = true;
        [SerializeField] private Material terrainMaterial;
        [SerializeField] private float terrainNoiseScale = 0.08f;
        [SerializeField] private float terrainHeightScale = 4f;
        [SerializeField] private float terrainSeaLevel = 0.35f;
        [SerializeField] private float cameraPadding = 6f;

        [Header("Tilemap Debug")]
        [SerializeField] private bool useTilemapDebugVisuals = false;
        [SerializeField] private Tilemap terrainTilemap;
        [SerializeField] private TileBase landTile;
        [SerializeField] private TileBase seaTile;
        [SerializeField] private TileBase coastalTile;
        [SerializeField] private TileBase solidSeaAnomalyTile;
        [SerializeField] private TileBase spatialFoldingTile;

        [Header("2D Fallback Debug")]
        [SerializeField] private bool useFallbackVisuals = false;
        [SerializeField] private Vector2 fallbackCellScale = new Vector2(0.95f, 0.95f);

        [Header("Capture Points")]
        [SerializeField] private GameObject capturePointPrefab;
        [SerializeField] private int capturePointCount = 5;
        [SerializeField] private Transform capturePointContainer;
        [SerializeField] private float capturePointHeightOffset = 0.2f;

        private Dictionary<string, MapNode> allNodes;
        private List<MapNode> nodeList;
        private Dictionary<string, TerrainCell> terrainCells;
        private List<TerrainCell> terrainCellList;

        private readonly Dictionary<string, StarNode> capturePoints = new Dictionary<string, StarNode>();
        private readonly Dictionary<string, SpriteRenderer> fallbackNodeRenderers = new Dictionary<string, SpriteRenderer>();

        private bool isInitialized;
        private int activeSeed;

        private TerrainHeightField currentHeightField;

        private readonly TerrainHeightGenerator terrainHeightGenerator = new TerrainHeightGenerator();
        private readonly TerrainClassifier terrainClassifier = new TerrainClassifier();
        private readonly StrategyGraphBuilder strategyGraphBuilder = new StrategyGraphBuilder();
        private readonly TerrainMeshBuilder terrainMeshBuilder = new TerrainMeshBuilder();

        private const string TerrainMeshRootName = "_RuntimeTerrainMesh";
        private const string FallbackVisualRootName = "_RuntimeMapVisuals";

        private Transform fallbackVisualRoot;
        private GameObject terrainMeshRoot;
        private MeshFilter terrainMeshFilter;
        private MeshRenderer terrainMeshRenderer;
        private MeshCollider terrainMeshCollider;

        private static Sprite fallbackCellSprite;
        private Material runtimeTerrainMaterial;

        public IReadOnlyDictionary<string, MapNode> AllNodes => allNodes;
        public IReadOnlyList<MapNode> NodeList => nodeList;
        public IReadOnlyList<TerrainCell> TerrainCells => terrainCellList;
        public bool IsInitialized => isInitialized;
        public int ActiveSeed => activeSeed;

        private void Awake()
        {
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }

            instance = this;
            EnsureCollections();
        }

        private void Start()
        {
            if (generateOnStart && !isInitialized)
            {
                GenerateMap();
            }
        }

        public void SetMapSize(int width, int height)
        {
            mapWidth = Mathf.Max(1, width);
            mapHeight = Mathf.Max(1, height);
        }

        public void SetSeed(int newSeed)
        {
            seed = newSeed;
        }

        public void SetTerrainRatios(float land, float sea, float coastal)
        {
            landRatio = Mathf.Max(0f, land);
            seaRatio = Mathf.Max(0f, sea);
            coastalRatio = Mathf.Max(0f, coastal);
        }

        public float GetTerrainCellSize()
        {
            return Mathf.Max(0.01f, terrainCellSize);
        }

        public StarNode GetCapturePoint(string nodeId)
        {
            return capturePoints.TryGetValue(nodeId, out StarNode point) ? point : null;
        }

        public Vector3 GetNodeWorldPosition(string nodeId)
        {
            return allNodes.TryGetValue(nodeId, out MapNode node) ? node.WorldPosition : Vector3.zero;
        }

        public MapNode GetNodeAtWorldPosition(float worldX, float worldY)
        {
            float stride = GetStrategyNodeStride();
            if (stride <= 0f)
            {
                return null;
            }

            int gridX = Mathf.FloorToInt(worldX / stride);
            int gridY = Mathf.FloorToInt(worldY / stride);

            if (gridX < 0 || gridX >= mapWidth || gridY < 0 || gridY >= mapHeight)
            {
                return null;
            }

            return GetNode($"node_{gridX}_{gridY}");
        }

        public bool TryGetNodeFromWorldPoint(Vector3 worldPoint, out MapNode node)
        {
            node = GetNodeAtWorldPosition(worldPoint.x, worldPoint.z);
            return node != null;
        }

        public bool TryGetTerrainCellFromWorldPoint(Vector3 worldPoint, out TerrainCell cell)
        {
            int cellX = Mathf.FloorToInt(worldPoint.x / Mathf.Max(0.01f, terrainCellSize));
            int cellY = Mathf.FloorToInt(worldPoint.z / Mathf.Max(0.01f, terrainCellSize));
            cell = GetTerrainCell(cellX, cellY);
            return cell != null;
        }

        [ContextMenu("Generate Map")]
        public void GenerateMap()
        {
            EnsureCollections();

            SpatialFoldRegistry.ClearAll();
            ClearMapData();

            activeSeed = seed != 0 ? seed : Environment.TickCount;
            UnityEngine.Random.InitState(activeSeed);

            BuildHeightField();
            BuildTerrainCells();
            BuildStrategyNodes();
            GenerateConnections();
            InitializeVisibility();
            GenerateVisuals();

            isInitialized = true;
            Debug.Log($"[MapManager] Map generated. Nodes={allNodes.Count}, Cells={terrainCellList.Count}, Seed={activeSeed}");
        }

        private void BuildHeightField()
        {
            float noiseScale = generationConfig != null ? generationConfig.noiseScale : terrainNoiseScale;
            float heightScale = generationConfig != null ? generationConfig.heightScale : terrainHeightScale;
            float seaLevel = generationConfig != null ? generationConfig.seaLevel : terrainSeaLevel;

            currentHeightField = terrainHeightGenerator.Generate(
                mapWidth,
                mapHeight,
                terrainCellsPerNode,
                terrainCellSize,
                activeSeed,
                noiseScale,
                heightScale,
                seaLevel);
        }

        private void BuildTerrainCells()
        {
            float effectiveLand = generationConfig != null ? generationConfig.landRatio : landRatio;
            float effectiveSea = generationConfig != null ? generationConfig.seaRatio : seaRatio;
            float effectiveCoastal = generationConfig != null ? generationConfig.coastalRatio : coastalRatio;

            terrainCellList = terrainClassifier.BuildCells(currentHeightField, effectiveLand, effectiveSea, effectiveCoastal);
            terrainCells = terrainCellList.ToDictionary(c => c.CellId, c => c);
        }

        private void BuildStrategyNodes()
        {
            nodeList = strategyGraphBuilder.BuildNodes(
                terrainCellList,
                mapWidth,
                mapHeight,
                terrainCellsPerNode,
                terrainCellSize,
                GenerateNodeName,
                () => UnityEngine.Random.Range(1, 10),
                () => UnityEngine.Random.Range(0, 5));

            allNodes = nodeList.ToDictionary(n => n.NodeId, n => n);
        }

        private void GenerateConnections()
        {
            strategyGraphBuilder.BuildConnections(allNodes, mapWidth, mapHeight);
        }

        private void InitializeVisibility()
        {
            foreach (MapNode node in nodeList)
            {
                node.Visibility = NodeVisibility.Hidden;
            }
        }

        private void GenerateVisuals()
        {
            if (useTerrainMesh)
            {
                BuildTerrainMesh();
            }

            if (useTilemapDebugVisuals && CanUseTilemapVisuals())
            {
                terrainTilemap.ClearAllTiles();
                DrawTilemap(nodeList);
            }
            else if (terrainTilemap != null)
            {
                terrainTilemap.ClearAllTiles();
            }

            if (useFallbackVisuals && !useTerrainMesh && !useTilemapDebugVisuals)
            {
                DrawFallbackVisuals(nodeList);
            }
            else
            {
                ClearFallbackVisualsOnly();
            }

            GenerateCapturePoints();

            if (focusMainCameraOnGenerate)
            {
                FocusMainCameraOnMap();
            }
        }

        public void RefreshTileVisuals(IEnumerable<MapNode> nodes)
        {
            List<MapNode> list = nodes?.ToList() ?? new List<MapNode>();

            if (useTerrainMesh && currentHeightField != null)
            {
                BuildTerrainMesh();
            }

            if (useTilemapDebugVisuals && CanUseTilemapVisuals())
            {
                DrawTilemap(list.Count > 0 ? list : nodeList);
            }

            if (useFallbackVisuals && !useTerrainMesh && !useTilemapDebugVisuals)
            {
                DrawFallbackVisuals(list.Count > 0 ? list : nodeList);
            }
        }

        private void BuildTerrainMesh()
        {
            EnsureTerrainMeshComponents();

            Mesh mesh = terrainMeshBuilder.BuildMesh(currentHeightField, terrainCellList);
            terrainMeshFilter.sharedMesh = mesh;

            terrainMeshCollider.sharedMesh = null;
            terrainMeshCollider.sharedMesh = mesh;

            terrainMeshRenderer.sharedMaterial = ResolveTerrainMaterial();
        }

        private Material ResolveTerrainMaterial()
        {
            if (terrainMaterial != null)
            {
                return terrainMaterial;
            }

            if (runtimeTerrainMaterial != null)
            {
                return runtimeTerrainMaterial;
            }

            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
            {
                shader = Shader.Find("Standard");
            }

            if (shader == null)
            {
                shader = Shader.Find("Diffuse");
            }

            if (shader == null)
            {
                shader = Shader.Find("Unlit/Color");
            }

            if (shader == null)
            {
                Debug.LogError("[MapManager] No terrain shader found. Assign terrainMaterial manually.");
                return null;
            }

            runtimeTerrainMaterial = new Material(shader);

            runtimeTerrainMaterial.name = "RuntimeTerrainMaterial";
            return runtimeTerrainMaterial;
        }

        private void GenerateCapturePoints()
        {
            ClearCapturePoints();

            if (capturePointPrefab == null)
            {
                return;
            }

            List<MapNode> validNodes = nodeList.Where(n => n.IsLandNode()).ToList();
            if (validNodes.Count == 0)
            {
                return;
            }

            Transform container = capturePointContainer != null ? capturePointContainer : transform;
            System.Random rng = new System.Random(activeSeed);

            List<MapNode> selectedNodes = validNodes
                .OrderBy(_ => rng.Next())
                .Take(Mathf.Min(capturePointCount, validNodes.Count))
                .ToList();

            char marker = 'A';
            foreach (MapNode node in selectedNodes)
            {
                Vector3 position = useTerrainMesh
                    ? node.WorldPosition + Vector3.up * capturePointHeightOffset
                    : new Vector3(node.CoordinateX, node.CoordinateY, 0f);

                GameObject capturePoint = Instantiate(capturePointPrefab, position, Quaternion.identity, container);
                capturePoint.name = $"CapturePoint_{marker}";

                StarNode starNode = capturePoint.GetComponent<StarNode>();
                if (starNode != null)
                {
                    starNode.Initialize($"Node {marker}", node.Terrain, node.NodeId);
                    starNode.SetVisibility(node.Visibility);
                    capturePoints[node.NodeId] = starNode;
                }

                if (marker == 'C' || marker == 'E')
                {
                    AnomalyFortress fortress = capturePoint.AddComponent<AnomalyFortress>();
                    fortress.anomalyType = AnomalyType.DensityAlteration;
                    fortress.auraRadius = 3;
                }

                marker++;
            }
        }

        public void UpdateVisibility(List<CombatUnit> playerUnits)
        {
            foreach (MapNode node in nodeList)
            {
                if (node.Visibility == NodeVisibility.Visible)
                {
                    node.SetFogged();
                }
            }

            foreach (CombatUnit unit in playerUnits)
            {
                if (string.IsNullOrEmpty(unit.CurrentNodeId))
                {
                    continue;
                }

                List<string> visibleNodeIds = TerrainCombatResolver.CalculateVisibleNodes(unit, allNodes);
                foreach (string nodeId in visibleNodeIds)
                {
                    if (!allNodes.TryGetValue(nodeId, out MapNode node))
                    {
                        continue;
                    }

                    node.SetVisible();
                    node.Explore();
                }
            }

            foreach (KeyValuePair<string, StarNode> kv in capturePoints)
            {
                if (kv.Value != null && allNodes.TryGetValue(kv.Key, out MapNode node))
                {
                    kv.Value.SetVisibility(node.Visibility);
                }
            }
        }

        public MapNode GetNode(string nodeId)
        {
            return allNodes.TryGetValue(nodeId, out MapNode node) ? node : null;
        }

        public MapNode GetNodeAtPosition(int x, int y)
        {
            return GetNodeAtWorldPosition(x, y);
        }

        public List<MapNode> GetNodesByTerrain(TerrainType terrain)
        {
            return nodeList.Where(n => n.Terrain == terrain).ToList();
        }

        public List<MapNode> GetNodesByOwner(NodeOwner owner)
        {
            return nodeList.Where(n => n.Owner == owner).ToList();
        }

        public List<MapNode> GetVisibleNodes()
        {
            return nodeList.Where(n => n.Visibility == NodeVisibility.Visible).ToList();
        }

        public List<MapNode> GetExploredNodes()
        {
            return nodeList.Where(n => n.Visibility != NodeVisibility.Hidden).ToList();
        }

        public List<MapNode> FindPath(MapNode start, MapNode end, UnitDomain unitDomain)
        {
            List<MapNode> path = new List<MapNode>();
            HashSet<string> visited = new HashSet<string>();
            Queue<MapNode> queue = new Queue<MapNode>();
            Dictionary<string, MapNode> cameFrom = new Dictionary<string, MapNode>();

            queue.Enqueue(start);
            visited.Add(start.NodeId);

            while (queue.Count > 0)
            {
                MapNode current = queue.Dequeue();

                if (current.NodeId == end.NodeId)
                {
                    MapNode step = end;
                    while (step.NodeId != start.NodeId)
                    {
                        path.Insert(0, step);
                        step = cameFrom[step.NodeId];
                    }

                    path.Insert(0, start);
                    return path;
                }

                foreach (RouteConnection connection in current.GetConnections())
                {
                    if (visited.Contains(connection.TargetNodeId))
                    {
                        continue;
                    }

                    MapNode neighbor = GetNode(connection.TargetNodeId);
                    if (neighbor == null)
                    {
                        continue;
                    }

                    if (!IsRouteValidForUnit(connection.RouteType, unitDomain))
                    {
                        continue;
                    }

                    visited.Add(neighbor.NodeId);
                    cameFrom[neighbor.NodeId] = current;
                    queue.Enqueue(neighbor);
                }

                string portalExitId = SpatialFoldRegistry.GetPortalExit(current.NodeId);
                if (!string.IsNullOrEmpty(portalExitId) && !visited.Contains(portalExitId))
                {
                    MapNode portalExit = GetNode(portalExitId);
                    if (portalExit != null)
                    {
                        visited.Add(portalExitId);
                        cameFrom[portalExitId] = current;
                        queue.Enqueue(portalExit);
                    }
                }
            }

            return path;
        }

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

        private void DrawTilemap(IEnumerable<MapNode> nodes)
        {
            if (terrainTilemap == null)
            {
                return;
            }

            foreach (MapNode node in nodes)
            {
                Vector3Int tilePosition = new Vector3Int(node.CoordinateX, node.CoordinateY, 0);
                TileBase tile = ResolveTileForNode(node);
                terrainTilemap.SetTile(tilePosition, tile);
            }
        }

        private TileBase ResolveTileForNode(MapNode node)
        {
            if (node.IsAnomalyActive && node.OriginalTerrain == TerrainType.Sea && node.Terrain == TerrainType.Coastal)
            {
                return solidSeaAnomalyTile != null ? solidSeaAnomalyTile : coastalTile;
            }

            if (node.IsSpatialFoldingVisual && spatialFoldingTile != null)
            {
                return spatialFoldingTile;
            }

            return node.Terrain switch
            {
                TerrainType.Sea => seaTile,
                TerrainType.Coastal => coastalTile,
                TerrainType.SpatialFolding => spatialFoldingTile != null ? spatialFoldingTile : landTile,
                _ => landTile
            };
        }

        private void DrawFallbackVisuals(IEnumerable<MapNode> nodes)
        {
            EnsureFallbackVisualRoot();

            foreach (MapNode node in nodes)
            {
                if (!fallbackNodeRenderers.TryGetValue(node.NodeId, out SpriteRenderer renderer) || renderer == null)
                {
                    renderer = CreateFallbackRenderer(node);
                }

                renderer.transform.localPosition = new Vector3(node.CoordinateX, node.CoordinateY, 0f);
                renderer.transform.localScale = new Vector3(fallbackCellScale.x, fallbackCellScale.y, 1f);
                renderer.color = GetFallbackNodeColor(node);
            }
        }

        private SpriteRenderer CreateFallbackRenderer(MapNode node)
        {
            GameObject tileObject = new GameObject($"Tile_{node.NodeId}");
            tileObject.transform.SetParent(fallbackVisualRoot, false);

            SpriteRenderer renderer = tileObject.AddComponent<SpriteRenderer>();
            renderer.sprite = GetFallbackCellSprite();
            renderer.sortingOrder = -10;

            fallbackNodeRenderers[node.NodeId] = renderer;
            return renderer;
        }

        private Color GetFallbackNodeColor(MapNode node)
        {
            Color color = node.Terrain switch
            {
                TerrainType.Land => new Color(0.36f, 0.62f, 0.31f),
                TerrainType.Sea => new Color(0.18f, 0.42f, 0.78f),
                TerrainType.Coastal => new Color(0.89f, 0.78f, 0.45f),
                TerrainType.SpatialFolding => new Color(0.72f, 0.39f, 0.92f),
                _ => Color.white
            };

            if (node.IsAnomalyActive)
            {
                color = Color.Lerp(color, new Color(1f, 0.35f, 0.65f), 0.45f);
            }

            if (node.IsSpatialFoldingVisual)
            {
                color = new Color(0.78f, 0.48f, 1f);
            }

            return color;
        }

        private void FocusMainCameraOnMap()
        {
            Camera targetCamera = Camera.main;
            if (targetCamera == null)
            {
                return;
            }

            if (useTerrainMesh && terrainMeshFilter != null && terrainMeshFilter.sharedMesh != null)
            {
                Bounds bounds = terrainMeshFilter.sharedMesh.bounds;
                bounds.center += terrainMeshRoot != null ? terrainMeshRoot.transform.position : Vector3.zero;
                Vector3 center = bounds.center;
                float maxDimension = Mathf.Max(bounds.size.x, bounds.size.z);
                float elevation = Mathf.Max(bounds.size.y, 1f);

                targetCamera.orthographic = false;

                float distance = maxDimension + elevation + cameraPadding;
                Vector3 direction = new Vector3(-0.55f, 0.85f, -0.55f).normalized;

                targetCamera.transform.position = center - direction * distance;
                targetCamera.transform.LookAt(center);
                return;
            }

            targetCamera.orthographic = true;
            float width = Mathf.Max(1f, mapWidth * nodeSpacing);
            float height = Mathf.Max(1f, mapHeight * nodeSpacing);

            Vector3 cameraPosition = targetCamera.transform.position;
            cameraPosition.x = (mapWidth - 1) * nodeSpacing * 0.5f;
            cameraPosition.y = (mapHeight - 1) * nodeSpacing * 0.5f;
            cameraPosition.z = cameraPosition.z >= -0.1f ? -10f : cameraPosition.z;

            targetCamera.transform.position = cameraPosition;
            targetCamera.transform.rotation = Quaternion.identity;

            float verticalSize = height * 0.5f + 1f;
            float horizontalSize = (width * 0.5f + 1f) / Mathf.Max(0.01f, targetCamera.aspect);
            targetCamera.orthographicSize = Mathf.Max(verticalSize, horizontalSize);
        }

        private void EnsureTerrainMeshComponents()
        {
            if (terrainMeshRoot == null)
            {
                Transform existing = transform.Find(TerrainMeshRootName);
                terrainMeshRoot = existing != null ? existing.gameObject : new GameObject(TerrainMeshRootName);
                terrainMeshRoot.transform.SetParent(transform, false);
            }

            if (!terrainMeshRoot.TryGetComponent(out terrainMeshFilter))
            {
                terrainMeshFilter = terrainMeshRoot.AddComponent<MeshFilter>();
            }

            if (!terrainMeshRoot.TryGetComponent(out terrainMeshRenderer))
            {
                terrainMeshRenderer = terrainMeshRoot.AddComponent<MeshRenderer>();
            }

            if (!terrainMeshRoot.TryGetComponent(out terrainMeshCollider))
            {
                terrainMeshCollider = terrainMeshRoot.AddComponent<MeshCollider>();
            }
        }

        private void EnsureCollections()
        {
            allNodes ??= new Dictionary<string, MapNode>();
            nodeList ??= new List<MapNode>();
            terrainCells ??= new Dictionary<string, TerrainCell>();
            terrainCellList ??= new List<TerrainCell>();
        }

        private void ClearMapData()
        {
            isInitialized = false;

            allNodes.Clear();
            nodeList.Clear();
            terrainCells.Clear();
            terrainCellList.Clear();

            ClearGeneratedVisuals();
            ClearCapturePoints();
        }

        private void ClearGeneratedVisuals()
        {
            if (terrainTilemap != null)
            {
                terrainTilemap.ClearAllTiles();
            }

            ClearFallbackVisualsOnly();

            if (terrainMeshFilter != null)
            {
                terrainMeshFilter.sharedMesh = null;
            }

            if (terrainMeshCollider != null)
            {
                terrainMeshCollider.sharedMesh = null;
            }
        }

        private void ClearFallbackVisualsOnly()
        {
            fallbackNodeRenderers.Clear();

            if (fallbackVisualRoot == null)
            {
                fallbackVisualRoot = transform.Find(FallbackVisualRootName);
            }

            if (fallbackVisualRoot == null)
            {
                return;
            }

            for (int i = fallbackVisualRoot.childCount - 1; i >= 0; i--)
            {
                GameObject child = fallbackVisualRoot.GetChild(i).gameObject;
#if UNITY_EDITOR
                if (!Application.isPlaying)
                {
                    DestroyImmediate(child);
                }
                else
                {
                    Destroy(child);
                }
#else
                Destroy(child);
#endif
            }
        }

        private void ClearCapturePoints()
        {
            foreach (StarNode cp in capturePoints.Values)
            {
                if (cp == null)
                {
                    continue;
                }

#if UNITY_EDITOR
                if (!Application.isPlaying)
                {
                    DestroyImmediate(cp.gameObject);
                }
                else
                {
                    Destroy(cp.gameObject);
                }
#else
                Destroy(cp.gameObject);
#endif
            }

            capturePoints.Clear();
        }

        private void EnsureFallbackVisualRoot()
        {
            if (fallbackVisualRoot != null)
            {
                return;
            }

            fallbackVisualRoot = transform.Find(FallbackVisualRootName);
            if (fallbackVisualRoot != null)
            {
                return;
            }

            GameObject root = new GameObject(FallbackVisualRootName);
            root.transform.SetParent(transform, false);
            fallbackVisualRoot = root.transform;
        }

        private Sprite GetFallbackCellSprite()
        {
            if (fallbackCellSprite != null)
            {
                return fallbackCellSprite;
            }

            Texture2D texture = new Texture2D(1, 1, TextureFormat.RGBA32, false);
            texture.SetPixel(0, 0, Color.white);
            texture.Apply();
            texture.filterMode = FilterMode.Point;

            fallbackCellSprite = Sprite.Create(texture, new Rect(0f, 0f, 1f, 1f), new Vector2(0.5f, 0.5f), 1f);
            fallbackCellSprite.name = "RuntimeMapCell";
            return fallbackCellSprite;
        }

        private string GenerateNodeName(TerrainType terrain, int index)
        {
            string prefix = terrain switch
            {
                TerrainType.Sea => "SEA",
                TerrainType.Coastal => "COAST",
                _ => "LAND"
            };

            return $"{prefix}-{index:D3}";
        }

        private float GetStrategyNodeStride()
        {
            return Mathf.Max(0.01f, terrainCellsPerNode * terrainCellSize);
        }

        private TerrainCell GetTerrainCell(int x, int y)
        {
            string cellId = $"cell_{x}_{y}";
            return terrainCells.TryGetValue(cellId, out TerrainCell cell) ? cell : null;
        }

        private bool CanUseTilemapVisuals()
        {
            return terrainTilemap != null && landTile != null && seaTile != null && coastalTile != null;
        }

        private void OnDrawGizmos()
        {
            if (!isInitialized || nodeList == null)
            {
                return;
            }

            foreach (MapNode node in nodeList)
            {
                Color color = node.Terrain switch
                {
                    TerrainType.Sea => new Color(0.2f, 0.4f, 0.8f),
                    TerrainType.Coastal => new Color(0.2f, 0.7f, 0.7f),
                    _ => new Color(0.6f, 0.4f, 0.2f)
                };

                if (node.Visibility == NodeVisibility.Hidden)
                {
                    color.a = 0.3f;
                }

                Gizmos.color = color;
                Vector3 position = node.WorldPosition;
                Gizmos.DrawSphere(position, 0.2f);

                foreach (RouteConnection conn in node.GetConnections())
                {
                    MapNode neighbor = GetNode(conn.TargetNodeId);
                    if (neighbor == null)
                    {
                        continue;
                    }

                    Gizmos.color = conn.RouteType switch
                    {
                        RouteType.LandRoute => Color.red,
                        RouteType.SeaRoute => Color.blue,
                        RouteType.AirRoute => Color.white,
                        _ => Color.gray
                    };

                    Gizmos.DrawLine(position, neighbor.WorldPosition);
                }
            }
        }
    }
}
