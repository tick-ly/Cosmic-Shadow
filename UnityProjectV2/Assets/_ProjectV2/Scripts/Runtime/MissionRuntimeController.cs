using System.Collections;
using System.Collections.Generic;
using ShadowOfTheUniverse.V2.Core;
using ShadowOfTheUniverse.V2.Data;
using ShadowOfTheUniverse.V2.UI;
using UnityEngine;
using UnityEngine.UI;

namespace ShadowOfTheUniverse.V2.Runtime
{
    public enum MissionRuntimeStatus
    {
        Unloaded,
        Running,
        Victory,
        Failed
    }

    public sealed class MissionRuntimeController : MonoBehaviour
    {
        [SerializeField] private MissionBootstrapConfigSO bootstrapConfig;
        [SerializeField] private TacticalMissionSO mission;
        [SerializeField] private MissionHudController hud;
        [SerializeField] private RiskAssessmentPanel riskPanel;
        [SerializeField] private float secondsPerMove = 15f;
        [SerializeField] private bool authoredEnvironment;
        [SerializeField] private float movementSpeed = 9f;
        private bool moving;
        public bool IsMoving { get { return moving; } }
        public UnitState SelectedUnit { get { return selectedUnit; } }

        private readonly Dictionary<string, NodeView> nodeViews = new Dictionary<string, NodeView>();
        private readonly Dictionary<string, UnitView> unitViews = new Dictionary<string, UnitView>();
        private MissionState state;
        private UnitState selectedUnit;
        private float timeAccumulator;
        private MissionRuntimeStatus status = MissionRuntimeStatus.Unloaded;

        public MissionState State
        {
            get { return state; }
        }

        public MissionRuntimeStatus Status
        {
            get { return status; }
        }

        private void Start()
        {
            RuntimeSceneBootstrap.EnsureCamera();
            RuntimeSceneBootstrap.EnsureLight();
            Canvas canvas = UiFactory.EnsureCanvas();

            if (hud == null)
            {
                hud = gameObject.AddComponent<MissionHudController>();
            }

            if (riskPanel == null)
            {
                riskPanel = gameObject.AddComponent<RiskAssessmentPanel>();
            }

            hud.EnsureDefaultLayout(canvas);
            riskPanel.EnsureDefaultLayout(canvas);

            if (bootstrapConfig != null)
            {
                mission = bootstrapConfig.DefaultMission;
                secondsPerMove = bootstrapConfig.SecondsPerMove;
            }

            if (mission == null)
            {
                Debug.LogError("[V2] MissionRuntimeController needs a TacticalMissionSO.");
                status = MissionRuntimeStatus.Unloaded;
                return;
            }

            LoadMission(mission);
        }

        private void Update()
        {
            if (state == null || state.Outcome != MissionOutcome.Running)
            {
                return;
            }

            timeAccumulator += Time.deltaTime;
            if (timeAccumulator >= 1f)
            {
                int seconds = Mathf.FloorToInt(timeAccumulator);
                timeAccumulator -= seconds;
                MissionResolver.AdvanceTime(state, seconds);
                RefreshAllViews();
            }
        }

        public void LoadMission(TacticalMissionSO sourceMission)
        {
            if (sourceMission == null) return;
            StopAllCoroutines();
            moving = false;
            timeAccumulator = 0f;
            mission = sourceMission;
            if (riskPanel != null) riskPanel.Close();
            ClearRuntimeObjects();
            state = sourceMission.CreateInitialState();
            selectedUnit = state.Units.Count > 0 ? state.Units[0] : null;
            status = MissionRuntimeStatus.Running;
            SpawnMap();
            SpawnUnits();
            RefreshAllViews();
        }

        public void HandleNodeClicked(NodeView nodeView)
        {
            if (state == null || nodeView == null || moving || state.Outcome != MissionOutcome.Running)
            {
                return;
            }

            if (selectedUnit == null)
            {
                selectedUnit = FindUnitAtNode(nodeView.NodeId);
                RefreshAllViews();
                return;
            }

            if (selectedUnit.CurrentNodeId == nodeView.NodeId)
            {
                OpenRiskPanelIfRelevant(nodeView.NodeId);
                RefreshAllViews();
                return;
            }

            if (authoredEnvironment)
            {
                MoveResult validation = MissionResolver.ValidateMove(state, selectedUnit.Id, nodeView.NodeId);
                if (validation.Success) StartCoroutine(WalkToNode(selectedUnit, nodeView.NodeId));
                else { state.Log.Add(validation.Reason); RefreshAllViews(); }
                return;
            }

            MoveResult result = MissionResolver.MoveUnit(state, selectedUnit.Id, nodeView.NodeId);
            state.Log.Add(result.Reason);
            if (result.Success)
            {
                MissionResolver.AdvanceTime(state, Mathf.RoundToInt(secondsPerMove));
                MoveUnitView(selectedUnit);
                OpenRiskPanelIfRelevant(nodeView.NodeId);
            }
            else
            {
                if (riskPanel != null)
                {
                    riskPanel.ShowMessage(result.Reason);
                }
            }

            RefreshAllViews();
        }

        public void HandleUnitClicked(UnitView unitView)
        {
            if (state == null || unitView == null || moving || state.Outcome != MissionOutcome.Running)
            {
                return;
            }

            selectedUnit = state.GetUnit(unitView.UnitId);
            RefreshAllViews();
        }

        private void ResolveSkill(SkillData skill)
        {
            if (state == null || selectedUnit == null || skill == null || moving || state.Outcome != MissionOutcome.Running)
            {
                return;
            }

            if (state.Encounters.Enabled && (selectedUnit.CurrentNodeId != state.TargetNodeId || state.ObjectiveProgress >= state.ObjectiveRequired))
            {
                riskPanel.Close();
                return;
            }

            SkillResolution resolution = RiskResolver.Resolve(selectedUnit, skill);
            MissionResolver.ApplySkillResolution(state, selectedUnit, resolution);

            NodeDefinition node = state.Map.GetNode(selectedUnit.CurrentNodeId);
            if (resolution.Success && node != null && node.Id == state.TargetNodeId && state.ObjectiveProgress >= state.ObjectiveRequired)
            {
                node.Owner = NodeOwner.Player;
            }

            if (state.Outcome == MissionOutcome.Running && node != null && state.ObjectiveProgress < state.ObjectiveRequired)
            {
                riskPanel.Open(state, selectedUnit, node, ResolveSkill);
            }

            riskPanel.ShowResult(resolution);
            if (state.Encounters.Enabled && state.ObjectiveProgress >= state.ObjectiveRequired) riskPanel.Close();
            RefreshAllViews();
        }

        private void OpenRiskPanelIfRelevant(string nodeId)
        {
            if (selectedUnit == null || state == null)
            {
                return;
            }

            NodeDefinition node = state.Map.GetNode(nodeId);
            if (node == null)
            {
                return;
            }

            bool targetNode = node.Id == state.TargetNodeId;
            bool hostileNode = node.Owner == NodeOwner.Enemy;
            if (targetNode || hostileNode)
            {
                riskPanel.Open(state, selectedUnit, node, ResolveSkill);
            }
            else
            {
                riskPanel.Close();
            }
        }

        private void SpawnMap()
        {
            foreach (NodeDefinition node in state.Map.Nodes.Values)
            {
                GameObject nodeObject = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                nodeObject.name = "Node_" + node.Id;
                nodeObject.transform.SetParent(transform, false);
                nodeObject.transform.position = new Vector3(node.X, node.Elevation + 0.06f, node.Y);
                nodeObject.transform.localScale = authoredEnvironment ? new Vector3(1.5f, 0.06f, 1.5f) : new Vector3(1.2f, 0.16f, 1.2f);
                NodeView view = nodeObject.AddComponent<NodeView>();
                view.Initialize(this, node);
                nodeViews[node.Id] = view;
            }

            if (authoredEnvironment) return;

            for (int i = 0; i < state.Map.Routes.Count; i++)
            {
                RouteDefinition route = state.Map.Routes[i];
                NodeDefinition from = state.Map.GetNode(route.FromNodeId);
                NodeDefinition to = state.Map.GetNode(route.ToNodeId);
                if (from == null || to == null)
                {
                    continue;
                }

                GameObject routeObject = new GameObject("Route_" + from.Id + "_" + to.Id);
                routeObject.transform.SetParent(transform, false);
                LineRenderer line = routeObject.AddComponent<LineRenderer>();
                line.positionCount = 2;
                line.SetPosition(0, new Vector3(from.X, 0.05f, from.Y));
                line.SetPosition(1, new Vector3(to.X, 0.05f, to.Y));
                line.startWidth = 0.08f;
                line.endWidth = 0.08f;
                line.material = new Material(Shader.Find("Sprites/Default"));
                line.startColor = RouteColor(route.RouteType);
                line.endColor = RouteColor(route.RouteType);
            }
        }

        private void SpawnUnits()
        {
            for (int i = 0; i < state.Units.Count; i++)
            {
                UnitState unit = state.Units[i];
                GameObject unitObject = GameObject.CreatePrimitive(PrimitiveType.Capsule);
                unitObject.name = "Unit_" + unit.Id;
                unitObject.transform.SetParent(transform, false);
                unitObject.transform.localScale = new Vector3(0.5f, 0.8f, 0.5f);
                UnitView view = unitObject.AddComponent<UnitView>();
                view.Initialize(this, unit);
                unitViews[unit.Id] = view;
                MoveUnitView(unit);
            }
        }

        private void MoveUnitView(UnitState unit)
        {
            if (unit == null || !unitViews.TryGetValue(unit.Id, out UnitView view))
            {
                return;
            }

            NodeDefinition node = state.Map.GetNode(unit.CurrentNodeId);
            if (node != null)
            {
                view.transform.position = new Vector3(node.X, node.Elevation + 0.9f, node.Y);
            }
        }

        private void RefreshAllViews()
        {
            foreach (KeyValuePair<string, NodeView> pair in nodeViews)
            {
                bool selected = selectedUnit != null && selectedUnit.CurrentNodeId == pair.Key;
                pair.Value.Refresh(selected);
            }

            foreach (KeyValuePair<string, UnitView> pair in unitViews)
            {
                bool selected = selectedUnit != null && selectedUnit.Id == pair.Key;
                pair.Value.Refresh(selected);
            }

            if (hud != null)
            {
                hud.Refresh(state, selectedUnit);
            }

            if (state != null)
            {
                if (state.Outcome == MissionOutcome.Victory)
                {
                    status = MissionRuntimeStatus.Victory;
                    if (riskPanel != null)
                    {
                        riskPanel.Close();
                    }
                }
                else if (state.Outcome == MissionOutcome.Failed)
                {
                    status = MissionRuntimeStatus.Failed;
                    if (riskPanel != null)
                    {
                        riskPanel.ShowMessage("Mission failed. Check HUD log for reason.");
                    }
                }
                else
                {
                    status = MissionRuntimeStatus.Running;
                }
            }
        }

        private UnitState FindUnitAtNode(string nodeId)
        {
            if (state == null)
            {
                return null;
            }

            for (int i = 0; i < state.Units.Count; i++)
            {
                if (state.Units[i].CurrentNodeId == nodeId)
                {
                    return state.Units[i];
                }
            }

            return null;
        }

        private void ClearRuntimeObjects()
        {
            nodeViews.Clear();
            unitViews.Clear();

            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                transform.GetChild(i).gameObject.SetActive(false);
                Destroy(transform.GetChild(i).gameObject);
            }
        }

        public void RestartMission()
        {
            LoadMission(mission);
        }

        public InteractionResult InteractAtCurrentNode()
        {
            if (moving || selectedUnit == null) return new InteractionResult { Message = "Wait for arrival." };
            InteractionResult result = TacticalEncounterResolver.Interact(state, selectedUnit.Id);
            if (!result.Success && state != null) state.Log.Add(result.Message);
            RefreshAllViews();
            return result;
        }

        private IEnumerator WalkToNode(UnitState unit, string targetId)
        {
            moving = true;
            riskPanel.Close();
            NodeDefinition target = state.Map.GetNode(targetId);
            Transform view = unitViews[unit.Id].transform;
            Vector3 destination = new Vector3(target.X, target.Elevation + .9f, target.Y);
            while (Vector3.Distance(view.position, destination) > .01f && state.Outcome == MissionOutcome.Running)
            {
                view.position = Vector3.MoveTowards(view.position, destination, Mathf.Max(1, movementSpeed) * Time.deltaTime);
                yield return null;
            }
            if (state.Outcome == MissionOutcome.Running)
            {
                MissionResolver.MoveUnit(state, unit.Id, targetId);
                MoveUnitView(unit);
                OpenRiskPanelIfRelevant(targetId);
            }
            else MoveUnitView(unit);
            moving = false;
            RefreshAllViews();
        }

        private static Color RouteColor(RouteType routeType)
        {
            if (routeType == RouteType.SeaRoute)
            {
                return new Color(0.2f, 0.5f, 1f);
            }

            if (routeType == RouteType.AirRoute)
            {
                return new Color(0.8f, 0.8f, 1f);
            }

            return new Color(0.85f, 0.8f, 0.52f);
        }
    }
}
