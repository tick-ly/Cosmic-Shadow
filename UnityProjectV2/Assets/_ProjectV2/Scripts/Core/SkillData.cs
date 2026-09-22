using System;

namespace ShadowOfTheUniverse.V2.Core
{
    [Serializable]
    public sealed class SkillData
    {
        public string Id;
        public string DisplayName;
        public string Description;
        public int BaseSuccessRate;
        public int CompromiseCost;
        public int RealityDebtCost;
        public int BacklashDamage;
        public int FatigueCost;
        public int CooldownTurns;
        public int AlertOnFailure;
        public int ObjectiveProgressOnSuccess;
        public string SuccessDescription;
        public string FailureDescription;

        public SkillData Clone()
        {
            return (SkillData)MemberwiseClone();
        }
    }
}
