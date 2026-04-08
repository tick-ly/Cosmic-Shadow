using UnityEngine;

/// <summary>
/// 游戏配置 ScriptableObject
/// 对应 Python 版 config.py 的所有常量
/// 在 Unity Editor 中创建单例资源：Create > Game > GameConfig
/// </summary>
[CreateAssetMenu(fileName = "GameConfig", menuName = "Game/GameConfig")]
public class GameConfigSO : ScriptableObject
{
    [Header("屏幕设置")]
    public int ScreenWidth = 1280;
    public int ScreenHeight = 720;
    public string WindowTitle = "宇宙之影 - Shadow of the Universe";
    public int TargetFPS = 60;

    [Header("战斗设置")]
    public int BattleTurnTime = 30;
    public int MaxRealityDebt = 1000;
    public int DebtWarningThreshold = 500;
    public int DebtCriticalThreshold = 800;

    [Header("能力设置")]
    public int[] SkillBaseSuccessRate = { 90, 70, 50 }; // LOW / MEDIUM / HIGH

    [Header("现实债务代价")]
    public Vector2Int[] DebtCostRange = {
        new Vector2Int(5, 15),   // LOW
        new Vector2Int(20, 50), // MEDIUM
        new Vector2Int(100, 300) // HIGH
    };

    [Header("调试模式")]
    public bool DebugMode = true;
    public bool ShowFPS = true;
    public bool LogCombat = true;

    // 辅助方法
    public int GetDebtCost(AbilityTier tier) => tier switch
    {
        AbilityTier.Basic   => Random.Range(DebtCostRange[0].x, DebtCostRange[0].y + 1),
        AbilityTier.Advanced=> Random.Range(DebtCostRange[1].x, DebtCostRange[1].y + 1),
        AbilityTier.Elite   => Random.Range(DebtCostRange[2].x, DebtCostRange[2].y + 1),
        _                   => 0
    };

    public int GetSuccessRate(AbilityTier tier) => tier switch
    {
        AbilityTier.Basic   => SkillBaseSuccessRate[0],
        AbilityTier.Advanced=> SkillBaseSuccessRate[1],
        AbilityTier.Elite   => SkillBaseSuccessRate[2],
        _                   => 50
    };

    public DebtLevel GetDebtLevel(int debt)
    {
        if (debt >= 800) return DebtLevel.DeadZone;
        if (debt >= 600) return DebtLevel.Critical;
        if (debt >= 400) return DebtLevel.High;
        if (debt >= 200) return DebtLevel.Moderate;
        return DebtLevel.Safe;
    }

    /// <summary>获取全局单例实例（运行时）</summary>
    public static GameConfigSO? Instance
    {
        get
        {
            if (_instance == null)
                _instance = Resources.Load<GameConfigSO>("Config/GameConfig");
            return _instance;
        }
    }
    private static GameConfigSO? _instance;
}
