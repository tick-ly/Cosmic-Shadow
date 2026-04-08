using ShadowOfTheUniverse.Core;
using UnityEngine;

namespace ShadowOfTheUniverse.Systems
{
    public class MapRaycastResolver : MonoBehaviour
    {
        [SerializeField] private MapManager mapManager;

        public bool TryResolveCell(Vector3 worldPoint, out TerrainCell cell)
        {
            MapManager manager = ResolveManager();
            if (manager == null)
            {
                cell = null;
                return false;
            }

            return manager.TryGetTerrainCellFromWorldPoint(worldPoint, out cell);
        }

        public bool TryResolveNode(Vector3 worldPoint, out MapNode node)
        {
            MapManager manager = ResolveManager();
            if (manager == null)
            {
                node = null;
                return false;
            }

            return manager.TryGetNodeFromWorldPoint(worldPoint, out node);
        }

        public Vector2Int WorldToCell(Vector3 worldPoint)
        {
            MapManager manager = ResolveManager();
            float cellSize = manager != null ? manager.GetTerrainCellSize() : 1f;
            int cellX = Mathf.FloorToInt(worldPoint.x / Mathf.Max(0.01f, cellSize));
            int cellZ = Mathf.FloorToInt(worldPoint.z / Mathf.Max(0.01f, cellSize));
            return new Vector2Int(cellX, cellZ);
        }

        private MapManager ResolveManager()
        {
            if (mapManager != null)
            {
                return mapManager;
            }

            if (MapManager.Instance != null && MapManager.Instance.IsInitialized)
            {
                mapManager = MapManager.Instance;
            }

            return mapManager;
        }
    }
}
