using System;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// 血统等级 - 决定角色能力和代价
    /// </summary>
    public enum BloodlineTier
    {
        Low,     // 低级血统 - 高成功率，低代价
        Medium,  // 中级血统 - 中等成功率和代价
        High     // 高级血统 - 低成功率，高代价
    }

    /// <summary>
    /// 风险等级 - 根据成功率动态计算
    /// </summary>
    public enum RiskLevel
    {
        Safe,       // 安全 (>=85%)
        Low,        // 低风险 (>=70%)
        Medium,     // 中等风险 (>=50%)
        High,       // 高风险 (>=30%)
        Critical    // 极高风险 (<30%)
    }

    /// <summary>
    /// 游戏状态
    /// </summary>
    public enum GameStateType
    {
        Menu,
        StrategyMap,
        Battle,
        CampaignResult,
        GameOver
    }

    /// <summary>
    /// 战斗结果
    /// </summary>
    public enum BattleResult
    {
        None,
        HeroVictory,
        HeroDefeated,
        DebtCrisis
    }
}
