using System;
using System.Collections.Generic;

namespace ShadowOfTheUniverse.V2.Core
{
    [Serializable]
    public sealed class UnitState
    {
        public string Id;
        public string DisplayName;
        public UnitDomain Domain;
        public UnitScale Scale;
        public string CurrentNodeId;
        public int MovementRange;
        public int MaxHealth;
        public int CurrentHealth;
        public int RealityDebt;
        public int Fatigue;
        public int CompromisePoints;
        public readonly List<SkillData> Skills = new List<SkillData>();
        public readonly Dictionary<string, int> Cooldowns = new Dictionary<string, int>();
        public readonly Dictionary<string, int> ConsecutiveUses = new Dictionary<string, int>();

        public bool IsAlive
        {
            get { return CurrentHealth > 0; }
        }

        public UnitState Clone()
        {
            UnitState clone = new UnitState
            {
                Id = Id,
                DisplayName = DisplayName,
                Domain = Domain,
                Scale = Scale,
                CurrentNodeId = CurrentNodeId,
                MovementRange = MovementRange,
                MaxHealth = MaxHealth,
                CurrentHealth = CurrentHealth,
                RealityDebt = RealityDebt,
                Fatigue = Fatigue,
                CompromisePoints = CompromisePoints
            };

            for (int i = 0; i < Skills.Count; i++)
            {
                clone.Skills.Add(Skills[i].Clone());
            }

            foreach (KeyValuePair<string, int> pair in Cooldowns)
            {
                clone.Cooldowns[pair.Key] = pair.Value;
            }

            foreach (KeyValuePair<string, int> pair in ConsecutiveUses)
            {
                clone.ConsecutiveUses[pair.Key] = pair.Value;
            }

            return clone;
        }

        public int GetCooldown(string skillId)
        {
            return Cooldowns.TryGetValue(skillId, out int value) ? value : 0;
        }

        public int GetConsecutiveUses(string skillId)
        {
            return ConsecutiveUses.TryGetValue(skillId, out int value) ? value : 0;
        }

        public void ReduceCooldowns()
        {
            List<string> keys = new List<string>(Cooldowns.Keys);
            for (int i = 0; i < keys.Count; i++)
            {
                string key = keys[i];
                Cooldowns[key] = MissionMath.ClampInt(Cooldowns[key] - 1, 0, 99);
                if (Cooldowns[key] == 0)
                {
                    ConsecutiveUses[key] = 0;
                }
            }
        }
    }
}
