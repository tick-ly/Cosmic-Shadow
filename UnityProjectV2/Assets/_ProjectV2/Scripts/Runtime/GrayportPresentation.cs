using UnityEngine;
using System.Collections.Generic;
using ShadowOfTheUniverse.V2.Core;

namespace ShadowOfTheUniverse.V2.Runtime
{
    /// <summary>Camera and navigation overlay for the authored harbor, not game rules.</summary>
    public sealed class GrayportPresentation : MonoBehaviour
    {
        private Camera viewCamera;
        private MissionRuntimeController controller;
        private Vector3 focus = new Vector3(6, 0, 2);
        private bool showLabels = true;
        private GUIStyle labelStyle;
        private MissionState displayedState;
        private readonly List<GameObject> patrolViews = new List<GameObject>();
        private readonly List<LineRenderer> routeViews = new List<LineRenderer>();
        private Material routeMaterial;
        private Material patrolMaterial;
        private AudioSource audioSource;
        private AudioClip warningTone;
        private TacticalPhase previousPhase;
        private bool paused;

        private void Start()
        {
            controller = FindAnyObjectByType<MissionRuntimeController>();
            viewCamera = Camera.main;
            if (viewCamera == null) viewCamera = RuntimeSceneBootstrap.EnsureCamera();
            viewCamera.orthographic = true;
            viewCamera.orthographicSize = 53;
            UpdateCamera();
            routeMaterial = new Material(Shader.Find("Sprites/Default"));
            patrolMaterial = new Material(Shader.Find("Standard"));
            patrolMaterial.color = new Color(.9f, .24f, .13f);
            audioSource = gameObject.AddComponent<AudioSource>();
            audioSource.volume = .12f;
            warningTone = AudioClip.Create("Harbor alert", 13230, 1, 22050, false);
            float[] samples = new float[13230];
            for (int i = 0; i < samples.Length; i++)
                samples[i] = Mathf.Sin(i * 2f * Mathf.PI * 620f / 22050f) * (1f - i / (float)samples.Length) * .35f;
            warningTone.SetData(samples, 0);
        }

        private void Update()
        {
            MissionState state = controller != null ? controller.State : null;
            if (state == null) return;
            if (state != displayedState)
            {
                foreach (GameObject go in patrolViews) Destroy(go);
                foreach (LineRenderer line in routeViews) Destroy(line.gameObject);
                patrolViews.Clear(); routeViews.Clear();
                displayedState = state;
                previousPhase = state.Encounters.Phase;
                foreach (PatrolDefinition p in state.Patrols)
                {
                    GameObject go = GameObject.CreatePrimitive(PrimitiveType.Capsule);
                    go.name = "Patrol / " + p.Id;
                    go.transform.SetParent(transform, false);
                    go.transform.localScale = new Vector3(.8f, 1.1f, .8f);
                    Destroy(go.GetComponent<Collider>());
                    go.GetComponent<Renderer>().sharedMaterial = patrolMaterial;
                    patrolViews.Add(go);
                }
                foreach (RouteDefinition route in state.Map.Routes)
                {
                    var go = new GameObject("Reachable route " + route.FromNodeId + " / " + route.ToNodeId);
                    go.transform.SetParent(transform, false);
                    LineRenderer line = go.AddComponent<LineRenderer>();
                    line.sharedMaterial = routeMaterial;
                    line.positionCount = 2;
                    line.startWidth = line.endWidth = .13f;
                    NodeDefinition a = state.Map.GetNode(route.FromNodeId), b = state.Map.GetNode(route.ToNodeId);
                    line.SetPosition(0, Position(a, .2f)); line.SetPosition(1, Position(b, .2f));
                    routeViews.Add(line);
                }
            }
            for (int i = 0; i < state.Patrols.Count; i++)
            {
                string id = TacticalEncounterResolver.PatrolNodeAt(state, state.Patrols[i], state.ElapsedSeconds);
                NodeDefinition node = id != null ? state.Map.GetNode(id) : null;
                patrolViews[i].SetActive(node != null);
                if (node != null) patrolViews[i].transform.position = Position(node, 1.1f) + Vector3.right * .9f;
            }
            UnitState unit = controller.SelectedUnit;
            for (int i = 0; i < routeViews.Count; i++)
            {
                RouteDefinition route = state.Map.Routes[i];
                bool adjacent = unit != null && (route.FromNodeId == unit.CurrentNodeId || route.ToNodeId == unit.CurrentNodeId);
                string target = unit != null && route.FromNodeId == unit.CurrentNodeId ? route.ToNodeId : route.FromNodeId;
                bool valid = adjacent && !controller.IsMoving && MissionResolver.ValidateMove(state, unit.Id, target).Success;
                routeViews[i].enabled = valid;
                Color c = valid && TacticalEncounterResolver.ArrivalAlert(state, state.Map.GetNode(target), state.ElapsedSeconds) > 0
                    ? new Color(1f, .65f, .2f) : new Color(.35f, .85f, .7f);
                routeViews[i].startColor = routeViews[i].endColor = c;
            }
            if (state.Encounters.Phase != previousPhase)
            {
                audioSource.PlayOneShot(warningTone);
                previousPhase = state.Encounters.Phase;
            }
        }

        private static Vector3 Position(NodeDefinition n, float height)
        {
            return new Vector3(n.X, n.Elevation + height, n.Y);
        }

        private void UpdateCamera()
        {
            viewCamera.transform.position = focus + new Vector3(80, 100, -120);
            viewCamera.transform.LookAt(focus);
        }

        private void OnGUI()
        {
            if (viewCamera == null || controller == null) return;
            Event e = Event.current;
            if (e.type == EventType.ScrollWheel)
            {
                viewCamera.orthographicSize = Mathf.Clamp(viewCamera.orthographicSize + e.delta.y * 2, 18, 80);
                e.Use();
            }
            if (e.type == EventType.MouseDrag && e.button == 2)
            {
                Vector3 right = viewCamera.transform.right;
                Vector3 forward = Vector3.ProjectOnPlane(viewCamera.transform.up, Vector3.up).normalized;
                focus += (-right * e.delta.x + forward * e.delta.y) * viewCamera.orthographicSize / 400f;
                UpdateCamera();
                e.Use();
            }
            GUILayout.BeginArea(new Rect(24, Screen.height - 130, 760, 120), GUI.skin.box);
            GUILayout.Label("GRAYPORT  /  Scroll: zoom   Middle drag: pan   Click adjacent waypoints to move");
            GUILayout.BeginHorizontal();
            if (GUILayout.Button("Restart mission")) { paused = false; Time.timeScale = 1; controller.RestartMission(); }
            if (GUILayout.Button("Reset camera")) { focus = new Vector3(6, 0, 2); viewCamera.orthographicSize = 53; UpdateCamera(); }
            if (GUILayout.Button(showLabels ? "Hide labels" : "Show labels")) showLabels = !showLabels;
            if (GUILayout.Button(paused ? "Resume" : "Tactical pause")) { paused = !paused; Time.timeScale = paused ? 0 : 1; }
            GUILayout.EndHorizontal();
            MissionState state = controller.State;
            UnitState selected = controller.SelectedUnit;
            NodeDefinition current = state != null && selected != null ? state.Map.GetNode(selected.CurrentNodeId) : null;
            if (current != null && current.Interaction != NodeInteraction.None)
            {
                bool used = state.Encounters.UsedInteractions.Contains(current.Id);
                GUI.enabled = !used && !controller.IsMoving && state.Outcome == MissionOutcome.Running;
                string action = current.Interaction == NodeInteraction.ReconTerminal ? "Download patrol recon (+8s)" : "Disable checkpoint power (10 pts, +8s)";
                if (GUILayout.Button(used ? "Terminal already used" : action)) controller.InteractAtCurrentNode();
                GUI.enabled = true;
            }
            else if (state != null && state.Encounters.Phase == TacticalPhase.ExtractionWarning)
                GUILayout.Label("WARNING: pier patrol mobilizes in " + Mathf.Max(0, state.Encounters.ExtractionStartsAt - state.ElapsedSeconds) + " seconds. East exit remains open.");
            else GUILayout.Label("Amber route: current exposure. Patrol detection is checked on arrival; cover reduces alert.");
            GUILayout.EndArea();
            if (!showLabels || controller.State == null) return;
            if (labelStyle == null)
            {
                labelStyle = new GUIStyle(GUI.skin.box) { fontSize = 11, alignment = TextAnchor.MiddleCenter };
                labelStyle.normal.textColor = new Color(.8f, .94f, .95f);
            }
            foreach (NodeDefinition node in controller.State.Map.Nodes.Values)
            {
                bool adjacent = selected != null && state.Map.TryGetRoute(selected.CurrentNodeId, node.Id, out RouteDefinition unusedRoute);
                bool landmark = node.Id == state.TargetNodeId || node.Id == state.ExtractionNodeId || node.Interaction != NodeInteraction.None;
                if (!adjacent && !landmark && node.Id != selected?.CurrentNodeId) continue;
                Vector3 p = viewCamera.WorldToScreenPoint(new Vector3(node.X, node.Elevation + .3f, node.Y));
                int exposure = TacticalEncounterResolver.ArrivalAlert(state, node, state.ElapsedSeconds);
                string text = node.DisplayName + (adjacent ? " / +" + exposure + " alert now" : "");
                if (p.z > 0) GUI.Label(new Rect(p.x - 98, Screen.height - p.y + 10, 196, 22), text, labelStyle);
            }
            if (state.Encounters.ReconDownloaded)
            {
                GUILayout.BeginArea(new Rect(Screen.width - 325, 24, 300, 145), GUI.skin.box);
                GUILayout.Label("PATROL RECON / waypoint watch");
                foreach (PatrolDefinition patrol in state.Patrols)
                {
                    string now = TacticalEncounterResolver.PatrolNodeAt(state, patrol, state.ElapsedSeconds);
                    if (now != null) GUILayout.Label(patrol.Id + ": " + now + " -> " + TacticalEncounterResolver.PatrolNodeAt(state, patrol, state.ElapsedSeconds + patrol.SecondsPerLeg));
                }
                GUILayout.EndArea();
            }
        }

        private void OnDestroy()
        {
            if (paused) Time.timeScale = 1;
            if (routeMaterial != null) Destroy(routeMaterial);
            if (patrolMaterial != null) Destroy(patrolMaterial);
            if (warningTone != null) Destroy(warningTone);
        }
    }
}
