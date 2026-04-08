using System;
using System.Collections.Generic;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// 游戏事件管理器 - 纯C#类
    /// 实现事件驱动架构，用于模块间解耦通信
    /// </summary>
    public class EventManager
    {
        // ========== 单例模式 ==========

        private static EventManager instance;
        public static EventManager Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = new EventManager();
                }
                return instance;
            }
        }

        // ========== 事件监听器存储 ==========

        private Dictionary<string, List<Delegate>> eventListeners;
        private Dictionary<string, List<Action<object>>> eventListenersWithParam;
        private Queue<GameEvent> eventQueue;
        private int maxQueueSize = 100;

        // ========== 构造函数 ==========

        private EventManager()
        {
            eventListeners = new Dictionary<string, List<Delegate>>();
            eventListenersWithParam = new Dictionary<string, List<Action<object>>>();
            eventQueue = new Queue<GameEvent>();
        }

        // ========== 订阅事件（无参数） ==========

        public void Subscribe(string eventName, Action callback)
        {
            if (!eventListeners.ContainsKey(eventName))
            {
                eventListeners[eventName] = new List<Delegate>();
            }

            if (!eventListeners[eventName].Contains(callback))
            {
                eventListeners[eventName].Add(callback);
            }
        }

        // ========== 订阅事件（带参数） ==========

        public void Subscribe(string eventName, Action<object> callback)
        {
            if (!eventListenersWithParam.ContainsKey(eventName))
            {
                eventListenersWithParam[eventName] = new List<Action<object>>();
            }

            if (!eventListenersWithParam[eventName].Contains(callback))
            {
                eventListenersWithParam[eventName].Add(callback);
            }
        }

        // ========== 取消订阅 ==========

        public void Unsubscribe(string eventName, Action callback)
        {
            if (eventListeners.ContainsKey(eventName))
            {
                eventListeners[eventName].Remove(callback);
            }
        }

        public void Unsubscribe(string eventName, Action<object> callback)
        {
            if (eventListenersWithParam.ContainsKey(eventName))
            {
                eventListenersWithParam[eventName].Remove(callback);
            }
        }

        // ========== 触发事件（立即） ==========

        public void Emit(string eventName)
        {
            if (eventListeners.ContainsKey(eventName))
            {
                // 复制列表以避免在遍历时修改
                var listeners = new List<Delegate>(eventListeners[eventName]);
                foreach (var listener in listeners)
                {
                    try
                    {
                        ((Action)listener)?.Invoke();
                    }
                    catch (Exception ex)
                    {
                        UnityEngine.Debug.LogError($"Error invoking event {eventName}: {ex.Message}");
                    }
                }
            }
        }

        public void Emit(string eventName, object data)
        {
            // 处理带参数的监听器
            if (eventListenersWithParam.ContainsKey(eventName))
            {
                var listeners = new List<Action<object>>(eventListenersWithParam[eventName]);
                foreach (var listener in listeners)
                {
                    try
                    {
                        listener?.Invoke(data);
                    }
                    catch (Exception ex)
                    {
                        UnityEngine.Debug.LogError($"Error invoking event {eventName}: {ex.Message}");
                    }
                }
            }

            // 处理无参数的监听器
            if (eventListeners.ContainsKey(eventName))
            {
                var listeners = new List<Delegate>(eventListeners[eventName]);
                foreach (var listener in listeners)
                {
                    try
                    {
                        ((Action)listener)?.Invoke();
                    }
                    catch (Exception ex)
                    {
                        UnityEngine.Debug.LogError($"Error invoking event {eventName}: {ex.Message}");
                    }
                }
            }
        }

        // ========== 队列事件（延迟处理） ==========

        public void QueueEvent(string eventName, object data = null)
        {
            GameEvent gameEvent = new GameEvent
            {
                EventName = eventName,
                Data = data,
                Timestamp = DateTime.Now
            };

            eventQueue.Enqueue(gameEvent);

            // 限制队列大小
            if (eventQueue.Count > maxQueueSize)
            {
                eventQueue.Dequeue();
            }
        }

        public void ProcessQueue()
        {
            while (eventQueue.Count > 0)
            {
                GameEvent gameEvent = eventQueue.Dequeue();
                Emit(gameEvent.EventName, gameEvent.Data);
            }
        }

        // ========== 清理 ==========

        public void ClearEvent(string eventName)
        {
            if (eventListeners.ContainsKey(eventName))
            {
                eventListeners[eventName].Clear();
            }
            if (eventListenersWithParam.ContainsKey(eventName))
            {
                eventListenersWithParam[eventName].Clear();
            }
        }

        public void ClearAllEvents()
        {
            eventListeners.Clear();
            eventListenersWithParam.Clear();
            eventQueue.Clear();
        }
    }

    // ========== 游戏事件常量 ==========

    public static class GameEvents
    {
        // 游戏流程事件
        public const string GAME_START = "GameStart";
        public const string GAME_PAUSE = "GamePause";
        public const string GAME_RESUME = "GameResume";
        public const string GAME_OVER = "GameOver";
        public const string TURN_START = "TurnStart";
        public const string TURN_END = "TurnEnd";

        // 战斗事件
        public const string BATTLE_START = "BattleStart";
        public const string BATTLE_END = "BattleEnd";
        public const string SKILL_USE = "SkillUse";
        public const string SKILL_SUCCESS = "SkillSuccess";
        public const string SKILL_FAILURE = "SkillFailure";
        public const string SKILL_BACKLASH = "SkillBacklash";

        // 角色事件
        public const string CHARACTER_DAMAGED = "CharacterDamaged";
        public const string CHARACTER_HEALED = "CharacterHealed";
        public const string CHARACTER_DIED = "CharacterDied";
        public const string DEBT_WARNING = "DebtWarning";
        public const string DEBT_CRITICAL = "DebtCritical";

        // UI事件
        public const string UI_PANEL_OPEN = "UIPanelOpen";
        public const string UI_PANEL_CLOSE = "UIPanelClose";
        public const string UI_BUTTON_CLICKED = "UIButtonClicked";

        // 地图事件（旧版）
        public const string NODE_SELECTED = "NodeSelected";
        public const string NODE_DISCOVERED = "NodeDiscovered";
        public const string FLEET_MOVED = "FleetMoved";

        // ========== 扩展：地形与移动事件 ==========

        // 移动事件
        public const string UNIT_MOVED = "UnitMoved";
        public const string UNIT_MOVEMENT_FAILED = "UnitMovementFailed";
        public const string UNIT_EXPLORATION = "UnitExploration";
        public const string ABILITY_USED_FOR_MOVEMENT = "AbilityUsedForMovement";

        // 地图事件
        public const string MAP_GENERATED = "MapGenerated";
        public const string NODE_EXPLORED = "NodeExplored";
        public const string NODE_CAPTURED = "NodeCaptured";
        public const string NODE_VISIBILITY_CHANGED = "NodeVisibilityChanged";

        // 地形事件
        public const string TERRAIN_CROSSED = "TerrainCrossed";
        public const string INVALID_TERRAIN_ACCESS = "InvalidTerrainAccess";

        // 视野事件
        public const string FOG_OF_WAR_UPDATED = "FogOfWarUpdated";
        public const string NEW_NODE_DISCOVERED = "NewNodeDiscovered";

        // 资源变化事件（UI专用）
        public const string CREDITS_CHANGED = "CreditsChanged";
        public const string SUPPRESSION_CHANGED = "SuppressionChanged";
    }

    // ========== 游戏事件数据结构 ==========

    [Serializable]
    public class GameEvent
    {
        public string EventName { get; set; }
        public object Data { get; set; }
        public DateTime Timestamp { get; set; }
    }

    // ========== 战斗事件数据 ==========

    [Serializable]
    public class BattleEventData
    {
        public Character Attacker { get; set; }
        public Character Defender { get; set; }
        public SkillBase SkillUsed { get; set; }
        public CombatResult Result { get; set; }
    }

    [Serializable]
    public class CharacterEventData
    {
        public Character Character { get; set; }
        public int DamageAmount { get; set; }
        public int HealAmount { get; set; }
        public int NewDebtValue { get; set; }
        public DebtStatus DebtStatus { get; set; }
    }

    /// <summary>
    /// 单位移动事件数据
    /// </summary>
    [Serializable]
    public class UnitMoveEventData
    {
        public string UnitName;
        public string TargetNodeName;
        public string TargetNodeId;
    }
}
