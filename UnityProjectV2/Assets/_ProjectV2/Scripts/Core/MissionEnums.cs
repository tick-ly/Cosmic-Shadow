using System;

namespace ShadowOfTheUniverse.V2.Core
{
    public enum MissionType
    {
        Infiltration,
        Frontline,
        Harassment
    }

    public enum UnitDomain
    {
        Land,
        Sea,
        Air
    }

    public enum UnitScale
    {
        Squad,
        Individual
    }

    public enum TerrainType
    {
        Land,
        Sea,
        Coastal,
        DeadZone
    }

    public enum RouteType
    {
        LandRoute,
        SeaRoute,
        AirRoute
    }

    public enum NodeOwner
    {
        Neutral,
        Player,
        Enemy
    }

    public enum MissionOutcome
    {
        Running,
        Victory,
        Failed,
        Evacuated
    }

    public enum SkillRiskLevel
    {
        Safe,
        Low,
        Medium,
        High,
        Critical
    }

    public static class MissionMath
    {
        public static int ClampInt(int value, int min, int max)
        {
            if (value < min)
            {
                return min;
            }

            if (value > max)
            {
                return max;
            }

            return value;
        }
    }
}
