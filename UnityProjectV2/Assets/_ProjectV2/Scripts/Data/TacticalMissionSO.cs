using System;
using ShadowOfTheUniverse.V2.Core;
using UnityEngine;

namespace ShadowOfTheUniverse.V2.Data
{
    [CreateAssetMenu(fileName = "V2TacticalMission", menuName = "Shadow of the Universe/V2/Tactical Mission")]
    public sealed class TacticalMissionSO : ScriptableObject
    {
        [Serializable]
        public sealed class UnitSpawnConfig
        {
            public UnitDataSO unit;
            public string startNodeId;
        }

        [SerializeField] private string missionId = "mission_id";
        [SerializeField] private string displayName = "Tactical Mission";
        [SerializeField] private MissionType missionType = MissionType.Infiltration;
        [TextArea(3, 6)]
        [SerializeField] private string briefingText = "Secure the objective and extract.";
        [SerializeField] private int timeLimitSeconds = 300;
        [SerializeField] private int maxAlertLevel = 3;
        [SerializeField] private int objectiveRequired = 3;
        [SerializeField] private int startingCompromisePoints = 100;
        [SerializeField] private string targetNodeId = "target";
        [SerializeField] private string extractionNodeId = "extract";
        [SerializeField] private NodeMapSO nodeMap;
        [SerializeField] private UnitSpawnConfig[] startingUnits;
        [SerializeField] private bool tacticalEncountersEnabled;
        [SerializeField] private PatrolDefinition[] patrols;

        public string DisplayName
        {
            get { return displayName; }
        }

        public string BriefingText
        {
            get { return briefingText; }
        }

        public NodeMapSO NodeMap
        {
            get { return nodeMap; }
        }

        public MissionState CreateInitialState()
        {
            MissionState state = new MissionState
            {
                MissionId = missionId,
                DisplayName = displayName,
                Type = missionType,
                TimeLimitSeconds = timeLimitSeconds,
                MaxAlertLevel = maxAlertLevel,
                ObjectiveRequired = objectiveRequired,
                TargetNodeId = targetNodeId,
                ExtractionNodeId = extractionNodeId,
                Map = nodeMap != null ? nodeMap.ToRuntimeMap() : new NodeMap()
            };

            if (startingUnits != null)
            {
                for (int i = 0; i < startingUnits.Length; i++)
                {
                    UnitSpawnConfig spawn = startingUnits[i];
                    if (spawn != null && spawn.unit != null)
                    {
                        state.Units.Add(spawn.unit.ToRuntimeState(spawn.startNodeId, startingCompromisePoints));
                    }
                }
            }

            state.Encounters.Enabled = tacticalEncountersEnabled;
            if (patrols != null)
            {
                foreach (PatrolDefinition patrol in patrols)
                {
                    if (patrol == null) continue;
                    state.Patrols.Add(new PatrolDefinition {
                        Id = patrol.Id, Nodes = patrol.Nodes == null ? new string[0] : (string[])patrol.Nodes.Clone(),
                        SecondsPerLeg = patrol.SecondsPerLeg, PhaseOffsetSeconds = patrol.PhaseOffsetSeconds,
                        ExtractionOnly = patrol.ExtractionOnly
                    });
                }
            }
            state.Log.Add("Mission started: " + displayName);
            return state;
        }

        private void OnValidate()
        {
            timeLimitSeconds = Mathf.Max(30, timeLimitSeconds);
            maxAlertLevel = Mathf.Max(1, maxAlertLevel);
            objectiveRequired = Mathf.Max(1, objectiveRequired);
            startingCompromisePoints = Mathf.Max(0, startingCompromisePoints);
        }

#if UNITY_EDITOR
        public void ConfigureForEditor(
            string id,
            string missionName,
            MissionType type,
            string briefing,
            int durationSeconds,
            int alertLimit,
            int requiredObjectiveProgress,
            int compromisePoints,
            string targetNode,
            string extractionNode,
            NodeMapSO map,
            UnitSpawnConfig[] unitSpawns)
        {
            missionId = id;
            displayName = missionName;
            missionType = type;
            briefingText = briefing;
            timeLimitSeconds = durationSeconds;
            maxAlertLevel = alertLimit;
            objectiveRequired = requiredObjectiveProgress;
            startingCompromisePoints = compromisePoints;
            targetNodeId = targetNode;
            extractionNodeId = extractionNode;
            nodeMap = map;
            startingUnits = unitSpawns;
            OnValidate();
        }
#endif
    }
}
