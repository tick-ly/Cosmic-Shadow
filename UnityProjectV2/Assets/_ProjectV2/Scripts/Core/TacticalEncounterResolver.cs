using System;
using System.Collections.Generic;

namespace ShadowOfTheUniverse.V2.Core
{
    public enum NodeInteraction { None, ReconTerminal, PowerSwitch }
    public enum TacticalPhase { Approach, ExtractionWarning, Extraction }

    [Serializable]
    public sealed class PatrolDefinition
    {
        public string Id;
        public string[] Nodes;
        public int SecondsPerLeg = 12;
        public int PhaseOffsetSeconds;
        public bool ExtractionOnly;
    }

    public sealed class TacticalEncounterState
    {
        public bool Enabled;
        public bool ReconDownloaded;
        public bool PowerDisabled;
        public TacticalPhase Phase;
        public int ExtractionStartsAt;
        public readonly HashSet<string> UsedInteractions = new HashSet<string>();
    }

    public sealed class InteractionResult
    {
        public bool Success;
        public string Message;
    }

    /// <summary>Waypoint-based detection, not continuous line-of-sight combat.</summary>
    public static class TacticalEncounterResolver
    {
        public static bool PatrolActive(MissionState mission, PatrolDefinition patrol)
        {
            return mission != null && patrol != null && mission.Encounters.Enabled &&
                (!patrol.ExtractionOnly || mission.Encounters.Phase == TacticalPhase.Extraction) &&
                patrol.Nodes != null && patrol.Nodes.Length > 0;
        }

        public static string PatrolNodeAt(MissionState mission, PatrolDefinition patrol, int seconds)
        {
            if (!PatrolActive(mission, patrol)) return null;
            int leg = Math.Max(1, patrol.SecondsPerLeg);
            int phase = Math.Max(0, seconds + patrol.PhaseOffsetSeconds);
            return patrol.Nodes[(phase / leg) % patrol.Nodes.Length];
        }

        public static int ArrivalAlert(MissionState mission, NodeDefinition node, int atSeconds)
        {
            if (mission == null || node == null || !mission.Encounters.Enabled) return 0;
            int exposure = node.PoweredGuard && mission.Encounters.PowerDisabled ? 0 : Math.Max(0, node.Exposure);
            foreach (PatrolDefinition patrol in mission.Patrols)
                if (PatrolNodeAt(mission, patrol, atSeconds) == node.Id) exposure++;
            return Math.Max(0, exposure - node.CoverRating);
        }

        public static void OnArrival(MissionState mission, NodeDefinition node)
        {
            if (!mission.Encounters.Enabled || mission.Outcome != MissionOutcome.Running) return;
            int added = ArrivalAlert(mission, node, mission.ElapsedSeconds);
            if (added > 0)
            {
                mission.AlertLevel = MissionMath.ClampInt(mission.AlertLevel + added, 0, mission.MaxAlertLevel);
                mission.Log.Add("Exposed at " + node.DisplayName + ": alert +" + added + ".");
            }
            else if (node.CoverRating > 0) mission.Log.Add("Cover screened your arrival at " + node.DisplayName + ".");
        }

        public static void UpdatePhase(MissionState mission)
        {
            if (mission == null || !mission.Encounters.Enabled || mission.Outcome != MissionOutcome.Running) return;
            TacticalEncounterState state = mission.Encounters;
            if (state.Phase == TacticalPhase.Approach && mission.ObjectiveProgress >= mission.ObjectiveRequired)
            {
                state.Phase = TacticalPhase.ExtractionWarning;
                state.ExtractionStartsAt = mission.ElapsedSeconds + 8;
                mission.Log.Add("RELAY OFFLINE. Harbor patrol mobilizes in 8 seconds. East pier remains open.");
            }
            if (state.Phase == TacticalPhase.ExtractionWarning && mission.ElapsedSeconds >= state.ExtractionStartsAt)
            {
                state.Phase = TacticalPhase.Extraction;
                mission.Log.Add("Extraction phase: patrol now covers the east approach. Check arrival exposure.");
            }
        }

        public static InteractionResult Interact(MissionState mission, string unitId)
        {
            if (mission == null || !mission.Encounters.Enabled || mission.Outcome != MissionOutcome.Running)
                return Fail("No active tactical interaction.");
            UnitState unit = mission.GetUnit(unitId);
            if (unit == null || !unit.IsAlive) return Fail("Select a living unit.");
            NodeDefinition node = mission.Map.GetNode(unit.CurrentNodeId);
            if (node == null || node.Interaction == NodeInteraction.None) return Fail("No terminal at this location.");
            if (mission.Encounters.UsedInteractions.Contains(node.Id)) return Fail("Already used.");
            int cost = node.Interaction == NodeInteraction.PowerSwitch ? 10 : 0;
            if (unit.CompromisePoints < cost) return Fail("Insufficient compromise points.");
            unit.CompromisePoints -= cost;
            mission.Encounters.UsedInteractions.Add(node.Id);
            string message;
            if (node.Interaction == NodeInteraction.ReconTerminal)
            {
                mission.Encounters.ReconDownloaded = true;
                message = "Recon downloaded: current and next patrol waypoints are visible. Time +8s.";
            }
            else
            {
                mission.Encounters.PowerDisabled = true;
                message = "Power disabled: powered checkpoint guards suppressed. Budget -10; time +8s.";
            }
            mission.Log.Add(message);
            MissionResolver.AdvanceTime(mission, 8);
            return new InteractionResult { Success = true, Message = message };
        }

        private static InteractionResult Fail(string text)
        {
            return new InteractionResult { Success = false, Message = text };
        }
    }
}
