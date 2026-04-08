#nullable enable

// ==================== 技能 ====================

public enum SkillType
{
    Attack, Defense, Support, PhysicsCompromise
}

public enum SkillTarget
{
    Self, SingleEnemy, AllEnemies, SingleAlly, AllAllies, Area
}

public enum CompromiseDimension
{
    None, Gravity, Electromagnetism, NuclearForce,
    Thermodynamics, Spacetime, Causality
}

// ==================== 单位 ====================

public enum UnitScale
{
    Solo, Squad, Platoon, Company, Battalion
}

public enum CombatRole
{
    Assault, Support, Recon, Command, Engineer, Special
}

public enum Owner
{
    Neutral, Player, Enemy
}

// ==================== 节点 ====================

public enum NodeType
{
    Normal, Strategic, Resource, Danger, JumpGate, HomeBase
}

public enum DebtLevel
{
    Safe,     // 0-199
    Moderate,  // 200-399
    High,     // 400-599
    Critical, // 600-799
    DeadZone  // 800+
}

// ==================== 战场 ====================

public enum TerrainType
{
    Plains, Mountain, Jungle, Urban, Desert, Snow, Swamp, Coastal, SpaceStation, Orbital
}

public enum WeatherCondition
{
    Clear, Rainy, Stormy, Foggy
}

// ==================== 武器 ====================

public enum WeaponCategory
{
    Ballistic, Cruise, Energy
}

public enum AbilityTier
{
    Basic, Advanced, Elite
}

public enum MachineScale
{
    Individual, Squad, Legion
}
