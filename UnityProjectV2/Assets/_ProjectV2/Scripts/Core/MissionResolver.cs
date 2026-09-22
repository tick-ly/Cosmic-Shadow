using System;

namespace ShadowOfTheUniverse.V2.Core
{
    public sealed class MoveResult
    {
        public bool Success;
        public string Reason;
        public string FromNodeId;
        public string ToNodeId;
    }

    public static class MissionResolver
    {
        public static MoveResult MoveUnit(MissionState mission, string unitId, string targetNodeId)
        {
            MoveResult result = ValidateMove(mission, unitId, targetNodeId);
            if (!result.Success) return result;
            UnitState unit = mission.GetUnit(unitId);
            unit.CurrentNodeId = targetNodeId;
            unit.ReduceCooldowns();
            mission.Log.Add(unit.DisplayName + " moved to " + mission.Map.GetNode(targetNodeId).DisplayName + ".");
            TacticalEncounterResolver.OnArrival(mission, mission.Map.GetNode(targetNodeId));
            CheckOutcome(mission);
            return result;
        }

        public static MoveResult ValidateMove(MissionState mission, string unitId, string targetNodeId)
        {
            if (mission == null || mission.Outcome != MissionOutcome.Running)
            {
                return new MoveResult { Success = false, Reason = "Mission is not running." };
            }

            UnitState unit = mission.GetUnit(unitId);
            NodeDefinition targetNode = mission.Map.GetNode(targetNodeId);
            if (unit == null || targetNode == null)
            {
                return new MoveResult { Success = false, Reason = "Missing unit or node." };
            }

            if (!unit.IsAlive)
            {
                return new MoveResult { Success = false, Reason = "Unit is down." };
            }

            if (!mission.Map.TryGetRoute(unit.CurrentNodeId, targetNodeId, out RouteDefinition route))
            {
                return new MoveResult { Success = false, Reason = "Nodes are not connected." };
            }

            if (!mission.Map.CanUnitUseRoute(unit, route))
            {
                return new MoveResult { Success = false, Reason = "Unit cannot use this route." };
            }

            if (!mission.Map.CanUnitEnterNode(unit, targetNode))
            {
                return new MoveResult { Success = false, Reason = "Unit cannot enter this terrain." };
            }

            string from = unit.CurrentNodeId;
            return new MoveResult
            {
                Success = true,
                Reason = "Moved",
                FromNodeId = from,
                ToNodeId = targetNodeId
            };
        }

        public static void ApplySkillResolution(MissionState mission, UnitState unit, SkillResolution resolution)
        {
            if (mission == null || unit == null || resolution == null || mission.Outcome != MissionOutcome.Running)
            {
                return;
            }

            mission.AlertLevel = MissionMath.ClampInt(mission.AlertLevel + resolution.AlertAdded, 0, mission.MaxAlertLevel);
            if (unit.CurrentNodeId == mission.TargetNodeId)
            {
                mission.ObjectiveProgress = MissionMath.ClampInt(
                    mission.ObjectiveProgress + resolution.ObjectiveProgressAdded,
                    0,
                    mission.ObjectiveRequired);
            }

            mission.Log.Add(unit.DisplayName + " used " + resolution.Assessment.Skill.DisplayName + ": " + resolution.Summary);
            TacticalEncounterResolver.UpdatePhase(mission);
            CheckOutcome(mission);
        }

        public static void AdvanceTime(MissionState mission, int seconds)
        {
            if (mission == null || mission.Outcome != MissionOutcome.Running)
            {
                return;
            }

            mission.ElapsedSeconds = MissionMath.ClampInt(mission.ElapsedSeconds + Math.Max(0, seconds), 0, mission.TimeLimitSeconds);
            TacticalEncounterResolver.UpdatePhase(mission);
            CheckOutcome(mission);
        }

        public static void CheckOutcome(MissionState mission)
        {
            if (mission == null || mission.Outcome != MissionOutcome.Running)
            {
                return;
            }

            if (!mission.HasLivingUnits())
            {
                mission.Outcome = MissionOutcome.Failed;
                mission.Log.Add("Mission failed: all units are down.");
                return;
            }

            if (mission.AlertLevel >= mission.MaxAlertLevel)
            {
                mission.Outcome = MissionOutcome.Failed;
                mission.Log.Add("Mission failed: alert threshold exceeded.");
                return;
            }

            if (mission.ElapsedSeconds >= mission.TimeLimitSeconds)
            {
                mission.Outcome = MissionOutcome.Failed;
                mission.Log.Add("Mission failed: time limit reached.");
                return;
            }

            if (mission.ObjectiveProgress >= mission.ObjectiveRequired && HasLivingUnitAt(mission, mission.ExtractionNodeId))
            {
                mission.Outcome = MissionOutcome.Victory;
                mission.Log.Add("Mission complete: objective secured and unit extracted.");
            }
        }

        private static bool HasLivingUnitAt(MissionState mission, string nodeId)
        {
            for (int i = 0; i < mission.Units.Count; i++)
            {
                UnitState unit = mission.Units[i];
                if (unit.IsAlive && unit.CurrentNodeId == nodeId)
                {
                    return true;
                }
            }

            return false;
        }
    }
}
