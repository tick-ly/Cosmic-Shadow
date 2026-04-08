using System;
using System.Collections.Generic;

namespace ShadowOfTheUniverse.Core
{
    /// <summary>
    /// 全局游戏状态 - 纯C#类，不继承MonoBehaviour
    /// 管理游戏全局数据和资源
    /// </summary>
    [Serializable]
    public class GameState
    {
        // ========== 单例模式 ==========

        private static GameState instance;
        public static GameState Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = new GameState();
                }
                return instance;
            }
        }

        // ========== 游戏进度 ==========

        public int CurrentTurn { get; private set; }
        public int CurrentLevel { get; private set; }
        public GameStateType CurrentState { get; private set; }

        // ========== 全局资源 ==========

        public int Credits { get; set; }                // 信用点（游戏货币）
        public int Suppression { get; set; }           // 镇压值（全局风险指标）
        public int MaxSuppression { get; private set; } = 100;

        // ========== 玩家数据 ==========

        public Character PlayerCharacter { get; set; }
        public List<string> UnlockedSkills { get; private set; }
        public List<string> DiscoveredNodes { get; private set; }

        // ========== 战斗统计 ==========

        public int TotalBattles { get; private set; }
        public int Victories { get; private set; }
        public int Defeats { get; private set; }

        // ========== 构造函数（私有） ==========

        private GameState()
        {
            CurrentTurn = 1;
            CurrentLevel = 1;
            CurrentState = GameStateType.Menu;

            Credits = 0;
            Suppression = 0;

            UnlockedSkills = new List<string>();
            DiscoveredNodes = new List<string>();

            TotalBattles = 0;
            Victories = 0;
            Defeats = 0;
        }

        // ========== 游戏流程控制 ==========

        public void ChangeState(GameStateType newState)
        {
            CurrentState = newState;
        }

        public void AdvanceTurn()
        {
            CurrentTurn++;
        }

        public void AdvanceLevel()
        {
            CurrentLevel++;
            CurrentTurn = 1; // 新关卡重置回合
        }

        // ========== 资源管理 ==========

        public void AddCredits(int amount)
        {
            Credits += amount;
            EventManager.Instance.Emit(GameEvents.CREDITS_CHANGED, Credits);
        }

        public bool SpendCredits(int amount)
        {
            if (Credits >= amount)
            {
                Credits -= amount;
                EventManager.Instance.Emit(GameEvents.CREDITS_CHANGED, Credits);
                return true;
            }
            return false;
        }

        public void AddSuppression(int amount)
        {
            Suppression = Math.Min(MaxSuppression, Suppression + amount);
            EventManager.Instance.Emit(GameEvents.SUPPRESSION_CHANGED, Suppression);
        }

        public void ReduceSuppression(int amount)
        {
            Suppression = Math.Max(0, Suppression - amount);
            EventManager.Instance.Emit(GameEvents.SUPPRESSION_CHANGED, Suppression);
        }

        // ========== 解锁系统 ==========

        public void UnlockSkill(string skillId)
        {
            if (!UnlockedSkills.Contains(skillId))
            {
                UnlockedSkills.Add(skillId);
            }
        }

        public void DiscoverNode(string nodeId)
        {
            if (!DiscoveredNodes.Contains(nodeId))
            {
                DiscoveredNodes.Add(nodeId);
            }
        }

        public bool IsSkillUnlocked(string skillId)
        {
            return UnlockedSkills.Contains(skillId);
        }

        public bool IsNodeDiscovered(string nodeId)
        {
            return DiscoveredNodes.Contains(nodeId);
        }

        // ========== 战斗统计 ==========

        public void RecordBattle(bool victory)
        {
            TotalBattles++;
            if (victory)
            {
                Victories++;
            }
            else
            {
                Defeats++;
            }
        }

        public float GetWinRate()
        {
            if (TotalBattles == 0)
                return 0f;
            return (float)Victories / TotalBattles;
        }

        // ========== 重置游戏 ==========

        public void ResetGame()
        {
            CurrentTurn = 1;
            CurrentLevel = 1;
            CurrentState = GameStateType.Menu;

            Credits = 0;
            Suppression = 0;

            UnlockedSkills.Clear();
            DiscoveredNodes.Clear();

            TotalBattles = 0;
            Victories = 0;
            Defeats = 0;

            PlayerCharacter = null;
        }
    }
}
