using System;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// 地形类型 - 节点的基础属性
    /// </summary>
    public enum TerrainType
    {
        Land,       // 陆地
        Sea,        // 水域
        Coastal,    // 沿海（陆地与水域交界）
        SpatialFolding  // 空间折叠区域（视觉表现用，不改变原有地形属性）
    }

    /// <summary>
    /// 路线类型 - 节点之间的连接类型
    /// </summary>
    public enum RouteType
    {
        LandRoute,  // 公路/铁路
        SeaRoute,   // 航道
        AirRoute    // 空中航线（空军专属）
    }

    /// <summary>
    /// 节点可见性 - 战争迷雾系统
    /// </summary>
    public enum NodeVisibility
    {
        Hidden,     // 未探索：完全不可见
        Fogged,     // 已探索但无视野：战争迷雾覆盖
        Visible     // 当前可见：可实时看到动态
    }

    /// <summary>
    /// 单位领域 - 海陆空分类
    /// </summary>
    public enum UnitDomain
    {
        Land,       // 陆军
        Sea,        // 海军
        Air         // 空军
    }

    /// <summary>
    /// 单位编制 - 队伍或单兵
    /// </summary>
    public enum UnitScale
    {
        Squad,      // 作战队伍（受地形严格限制）
        Individual  // 单兵单位（超能力者，机动性强）
    }

    /// <summary>
    /// 节点控制权状态
    /// </summary>
    public enum NodeOwner
    {
        None,       // 中立/未占领
        Player,     // 玩家控制
        Enemy       // 敌方控制
    }
}
