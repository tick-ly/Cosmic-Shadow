using UnityEngine;
using ShadowOfTheUniverse.Core;
using ShadowOfTheUniverse.Systems;
using ShadowOfTheUniverse.UI;

namespace ShadowOfTheUniverse.Strategy
{
    public class PlayerCommander : MonoBehaviour
    {
        [Header("Prefabs")]
        public GameObject unitPrefab;

        private CombatUnitController selectedUnit;
        private Camera mainCamera;

        private void Start()
        {
            mainCamera = Camera.main;
            Invoke(nameof(SpawnInitialUnit), 0.5f);
        }

        private void SpawnInitialUnit()
        {
            if (MapManager.Instance == null || MapManager.Instance.NodeList.Count == 0)
            {
                return;
            }

            StarNode startVisualNode = null;
            foreach (MapNode node in MapManager.Instance.NodeList)
            {
                startVisualNode = MapManager.Instance.GetCapturePoint(node.NodeId);
                if (startVisualNode != null)
                {
                    break;
                }
            }

            if (startVisualNode == null || unitPrefab == null)
            {
                return;
            }

            if (!string.IsNullOrEmpty(startVisualNode.mapNodeId))
            {
                MapNode startNode = MapManager.Instance.GetNode(startVisualNode.mapNodeId);
                if (startNode != null)
                {
                    startNode.Owner = NodeOwner.Player;
                    startNode.GarrisonStrength = 0;
                }
            }

            GameObject unitObj = Instantiate(unitPrefab, startVisualNode.transform.position, Quaternion.identity);
            unitObj.name = "Player Land Squad";

            CombatUnitController unitCtrl = unitObj.GetComponent<CombatUnitController>();
            if (unitCtrl == null)
            {
                return;
            }

            CombatUnitModel model = new CombatUnitModel("Land Squad Alpha", UnitDomain.Land, UnitScale.Squad, startVisualNode, speed: 3f);
            unitCtrl.Initialize(model);
        }

        private void Update()
        {
            if (Input.GetMouseButtonDown(0))
            {
                HandleClick();
            }
        }

        private void HandleClick()
        {
            if (mainCamera == null)
            {
                mainCamera = Camera.main;
            }

            if (mainCamera == null)
            {
                return;
            }

            // 3D picking path for terrain mesh and 3D colliders.
            Ray ray = mainCamera.ScreenPointToRay(Input.mousePosition);
            if (Physics.Raycast(ray, out RaycastHit hit3D, 500f))
            {
                CombatUnitController clickedUnit3D = hit3D.collider.GetComponentInParent<CombatUnitController>();
                if (clickedUnit3D != null)
                {
                    SelectUnit(clickedUnit3D);
                    return;
                }

                StarNode clickedNode3D = hit3D.collider.GetComponentInParent<StarNode>();
                if (clickedNode3D != null)
                {
                    HandleNodeClick(clickedNode3D);
                    return;
                }

                if (MapManager.Instance != null &&
                    MapManager.Instance.IsInitialized &&
                    MapManager.Instance.TryGetNodeFromWorldPoint(hit3D.point, out MapNode mapNodeFromMesh))
                {
                    HandleMapNodeSelection(mapNodeFromMesh);
                    return;
                }
            }

            // 2D fallback path.
            Vector2 mousePos = mainCamera.ScreenToWorldPoint(Input.mousePosition);
            RaycastHit2D hit2D = Physics2D.Raycast(mousePos, Vector2.zero);

            if (hit2D.collider != null)
            {
                CombatUnitController clickedUnit2D = hit2D.collider.GetComponent<CombatUnitController>();
                if (clickedUnit2D != null)
                {
                    SelectUnit(clickedUnit2D);
                    return;
                }

                StarNode clickedNode2D = hit2D.collider.GetComponent<StarNode>();
                if (clickedNode2D != null)
                {
                    HandleNodeClick(clickedNode2D);
                    return;
                }
            }

            if (MapManager.Instance != null && MapManager.Instance.IsInitialized)
            {
                int gridX = Mathf.RoundToInt(mousePos.x);
                int gridY = Mathf.RoundToInt(mousePos.y);
                MapNode mapNode = MapManager.Instance.GetNodeAtPosition(gridX, gridY);
                if (mapNode != null)
                {
                    HandleMapNodeSelection(mapNode);
                    return;
                }
            }

            DeselectUnit();
        }

        private void HandleMapNodeSelection(MapNode mapNode)
        {
            if (mapNode == null || MapManager.Instance == null)
            {
                DeselectUnit();
                return;
            }

            StarNode cp = MapManager.Instance.GetCapturePoint(mapNode.NodeId);
            if (cp != null)
            {
                HandleNodeClick(cp);
                return;
            }

            if (selectedUnit != null)
            {
                Debug.Log($"Current units still move between capture points. Clicked terrain: {mapNode.Terrain}");
                return;
            }

            DeselectUnit();
        }

        private void HandleNodeClick(StarNode clickedNode)
        {
            if (selectedUnit != null)
            {
                if (selectedUnit.Model.TryMoveTo(clickedNode))
                {
                    Debug.Log($"Move command: {selectedUnit.Model.UnitName} -> {clickedNode.nodeName}");
                    if (GameUIManager.Instance != null)
                    {
                        GameUIManager.Instance.AppendBattleLog($"{selectedUnit.Model.UnitName} moved to {clickedNode.nodeName}");
                    }
                }
                else
                {
                    Debug.LogWarning("Move failed: node not connected, terrain mismatch, or unit is already moving.");
                }
            }
            else
            {
                if (GameUIManager.Instance != null)
                {
                    if (GameUIManager.Instance.TryOpenRiskAssessmentForStarNode(clickedNode))
                    {
                        return;
                    }
                    GameUIManager.Instance.ShowNodeInfo(clickedNode);
                }
            }
        }

        private void SelectUnit(CombatUnitController unit)
        {
            DeselectUnit();
            selectedUnit = unit;
            selectedUnit.Highlight(true);

            Debug.Log($"Selected unit: {selectedUnit.Model.UnitName} [{selectedUnit.Model.Domain} {selectedUnit.Model.Scale}]");
            if (GameUIManager.Instance != null)
            {
                GameUIManager.Instance.ShowUnitInfo(selectedUnit);
            }
        }

        private void DeselectUnit()
        {
            if (selectedUnit != null)
            {
                selectedUnit.Highlight(false);
                selectedUnit = null;
            }
        }
    }
}
