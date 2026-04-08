using System;
using System.Collections.Generic;

/// <summary>
/// 全局事件静态类
/// 使用 GameEvents.XXX.Emit(data) 发送事件
/// 使用 GameEvents.XXX.Subscribe(callback) 订阅
/// </summary>
public static class GameEvents
{
    private static readonly Dictionary<Type, object> _buses = new();

    public static EventBus<T> Get<T>() where T : IEventData
    {
        var type = typeof(T);
        if (!_buses.TryGetValue(type, out var bus))
        {
            bus = new EventBus<T>();
            _buses[type] = bus;
        }
        return (EventBus<T>)bus;
    }

    // ==================== 游戏事件 ====================

    public static EventBus<GameStartEvent> GameStart => Get<GameStartEvent>();
    public static EventBus<GameOverEvent> GameOver => Get<GameOverEvent>();

    // ==================== 场景事件 ====================

    public static EventBus<SceneChangeRequestEvent> SceneChangeRequest => Get<SceneChangeRequestEvent>();
    public static EventBus<SceneLoadedEvent> SceneLoaded => Get<SceneLoadedEvent>();

    // ==================== 战斗事件 ====================

    public static EventBus<BattleStartEvent> BattleStart => Get<BattleStartEvent>();
    public static EventBus<BattleEndEvent> BattleEnd => Get<BattleEndEvent>();
    public static EventBus<TurnStartEvent> TurnStart => Get<TurnStartEvent>();
    public static EventBus<TurnEndEvent> TurnEnd => Get<TurnEndEvent>();
    public static EventBus<UnitDamagedEvent> UnitDamaged => Get<UnitDamagedEvent>();
    public static EventBus<UnitDiedEvent> UnitDied => Get<UnitDiedEvent>();
    public static EventBus<SkillUsedEvent> SkillUsed => Get<SkillUsedEvent>();

    // ==================== 地图事件 ====================

    public static EventBus<NodeSelectedEvent> NodeSelected => Get<NodeSelectedEvent>();
    public static EventBus<NodeHoveredEvent> NodeHovered => Get<NodeHoveredEvent>();
    public static EventBus<FleetArrivedEvent> FleetArrived => Get<FleetArrivedEvent>();
    public static EventBus<FleetMovedEvent> FleetMoved => Get<FleetMovedEvent>();

    // ==================== 现实债务事件 ====================

    public static EventBus<DebtChangedEvent> DebtChanged => Get<DebtChangedEvent>();
    public static EventBus<DebtWarningEvent> DebtWarning => Get<DebtWarningEvent>();
}

// ==================== 事件数据类型 ====================

// 游戏
public struct GameStartEvent : IEventData { }
public struct GameOverEvent : IEventData { public string Reason; }

// 场景
public struct SceneChangeRequestEvent : IEventData { public string SceneName; public LoadSceneMode Mode; }
public struct SceneLoadedEvent : IEventData { public string SceneName; }

// 战斗
public struct BattleStartEvent : IEventData { public string NodeId; }
public struct BattleEndEvent : IEventData { public bool PlayerWon; public int RemainingHealth; }
public struct TurnStartEvent : IEventData { public int TurnNumber; public string Team; }
public struct TurnEndEvent : IEventData { public int TurnNumber; }
public struct UnitDamagedEvent : IEventData
{
    public object Unit; // WarfareUnit
    public int Damage;
    public bool WasCritical;
}
public struct UnitDiedEvent : IEventData { public object Unit; public string KillerName; }
public struct SkillUsedEvent : IEventData { public object Unit; public string SkillId; public bool Success; }

// 地图
public struct NodeSelectedEvent : IEventData { public object Node; } // StarNode
public struct NodeHoveredEvent : IEventData { public object Node; }
public struct FleetArrivedEvent : IEventData { public object Fleet; public string NodeId; }
public struct FleetMovedEvent : IEventData { public object Fleet; public string FromNodeId; public string ToNodeId; }

// 现实债务
public struct DebtChangedEvent : IEventData { public int OldDebt; public int NewDebt; }
public struct DebtWarningEvent : IEventData { public int CurrentDebt; public int Threshold; }

using UnityEngine.SceneManagement;
