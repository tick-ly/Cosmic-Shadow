using UnityEngine;

/// <summary>
/// 游戏颜色常量
/// 对应 Python 版 config.py 的 Colors 类
/// </summary>
public static class GameColors
{
    // 基础色
    public static readonly Color Black     = new Color(0f, 0f, 0f);
    public static readonly Color White    = new Color(1f, 1f, 1f);
    public static readonly Color Gray     = new Color(0.5f, 0.5f, 0.5f);

    // 风险等级
    public static readonly Color RiskLow      = new Color(0.30f, 0.69f, 0.31f); // #4CAF50
    public static readonly Color RiskMedium   = new Color(1.00f, 0.76f, 0.03f); // #FFC107
    public static readonly Color RiskHigh     = new Color(1.00f, 0.60f, 0.00f); // #FF9800
    public static readonly Color RiskCritical = new Color(0.96f, 0.26f, 0.21f); // #F44336

    // UI
    public static readonly Color Background  = new Color(0.12f, 0.12f, 0.16f); // #1F1F29
    public static readonly Color Panel       = new Color(0.20f, 0.20f, 0.27f); // #333346
    public static readonly Color Border      = new Color(0.39f, 0.39f, 0.47f); // #646678
    public static readonly Color Text        = new Color(0.86f, 0.86f, 0.86f); // #DCDCDC
    public static readonly Color Highlight   = new Color(0.39f, 0.59f, 1.00f); // #6496FF

    // 债务等级对应颜色
    public static Color GetDebtColor(DebtLevel level) => level switch
    {
        DebtLevel.Safe     => RiskLow,
        DebtLevel.Moderate => RiskMedium,
        DebtLevel.High     => RiskHigh,
        DebtLevel.Critical => RiskCritical,
        DebtLevel.DeadZone => Background,
        _                  => White
    };
}
