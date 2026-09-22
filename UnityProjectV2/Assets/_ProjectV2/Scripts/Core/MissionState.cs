using System;
using System.Collections.Generic;

namespace ShadowOfTheUniverse.V2.Core
{
    public sealed class MissionState
    {
        public string MissionId;
        public string DisplayName;
        public MissionType Type;
        public int ElapsedSeconds;
        public int TimeLimitSeconds;
        public int AlertLevel;
        public int MaxAlertLevel;
        public int ObjectiveProgress;
        public int ObjectiveRequired;
        public string TargetNodeId;
        public string ExtractionNodeId;
        public MissionOutcome Outcome = MissionOutcome.Running;
        public NodeMap Map = new NodeMap();
        public readonly TacticalEncounterState Encounters = new TacticalEncounterState();
        public readonly List<PatrolDefinition> Patrols = new List<PatrolDefinition>();
        public readonly List<UnitState> Units = new List<UnitState>();
        public readonly List<string> Log = new List<string>();

        public UnitState GetUnit(string unitId)
        {
            for (int i = 0; i < Units.Count; i++)
            {
                if (Units[i].Id == unitId)
                {
                    return Units[i];
                }
            }

            return null;
        }

        public bool HasLivingUnits()
        {
            for (int i = 0; i < Units.Count; i++)
            {
                if (Units[i].IsAlive)
                {
                    return true;
                }
            }

            return false;
        }
    }
}
