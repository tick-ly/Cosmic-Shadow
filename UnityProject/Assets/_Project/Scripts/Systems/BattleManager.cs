using UnityEngine;
using System.Collections.Generic;
using ShadowOfTheUniverse.Core;

namespace ShadowOfTheUniverse.Systems
{
    /// <summary>
    /// 战斗管理器 - MonoBehaviour
    /// 负责Unity战斗流程控制，调用核心CombatResolver处理逻辑
    /// </summary>
    public class BattleManager : MonoBehaviour
    {
        // ========== 单例模式 ==========

        private static BattleManager instance;
        public static BattleManager Instance
        {
            get
            {
                if (instance == null)
                {
                    GameObject go = new GameObject("BattleManager");
                    instance = go.AddComponent<BattleManager>();
                }
                return instance;
            }
        }

        // ========== 战斗数据 ==========

        [Header("战斗设置")]
        [SerializeField] private int turnTimeLimit = 30;
        [SerializeField] private bool showCombatLog = true;

        private Character playerCharacter;
        private Character enemyCharacter;
        private int currentTurn;
        private bool battleActive;
        private List<string> combatLog;

        // ========== 属性 ==========

        public bool IsBattleActive => battleActive;
        public int CurrentTurn => currentTurn;
        public int TurnTimeLimit => turnTimeLimit;
        public IReadOnlyList<string> CombatLog => combatLog.AsReadOnly();

        // ========== 初始化 ==========

        private void Awake()
        {
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }

            instance = this;
            combatLog = new List<string>();
        }

        // ========== 战斗流程 ==========

        public void StartBattle(Character player, Character enemy)
        {
            if (battleActive)
            {
                Debug.LogWarning("[BattleManager] 战斗已在进行中");
                return;
            }

            Debug.Log($"[BattleManager] 开始战斗: {player.Name} vs {enemy.Name}");

            playerCharacter = player;
            enemyCharacter = enemy;
            currentTurn = 1;
            battleActive = true;
            combatLog.Clear();

            // 触发战斗开始事件
            var battleData = new BattleEventData
            {
                Attacker = player,
                Defender = enemy
            };
            EventManager.Instance.Emit(GameEvents.BATTLE_START, battleData);

            // 开始第一回合
            StartTurn();
        }

        private void StartTurn()
        {
            Debug.Log($"[BattleManager] 第 {currentTurn} 回合开始");

            // 触发回合开始事件
            EventManager.Instance.Emit(GameEvents.TURN_START, currentTurn);

            // 减少所有技能冷却
            ReduceAllCooldowns(playerCharacter);
            ReduceAllCooldowns(enemyCharacter);

            // 更新游戏状态
            GameState.Instance.AdvanceTurn();
        }

        public void EndTurn()
        {
            Debug.Log($"[BattleManager] 第 {currentTurn} 回合结束");

            // 触发回合结束事件
            EventManager.Instance.Emit(GameEvents.TURN_END, currentTurn);

            // 检查战斗是否结束
            BattleResult result = CombatResolver.CheckBattleEnd(playerCharacter, enemyCharacter);

            if (result != BattleResult.None)
            {
                EndBattle(result);
            }
            else
            {
                // 继续下一回合
                currentTurn++;
                StartTurn();
            }
        }

        public void EndBattle(BattleResult result)
        {
            Debug.Log($"[BattleManager] 战斗结束，结果: {result}");

            battleActive = false;

            // 触发战斗结束事件
            EventManager.Instance.Emit(GameEvents.BATTLE_END, result);

            // 记录战斗统计
            bool victory = (result == BattleResult.HeroVictory);
            GameState.Instance.RecordBattle(victory);

            // 根据结果触发不同事件
            switch (result)
            {
                case BattleResult.HeroVictory:
                    OnVictory();
                    break;

                case BattleResult.HeroDefeated:
                    EventManager.Instance.Emit(GameEvents.CHARACTER_DIED, playerCharacter);
                    break;

                case BattleResult.DebtCrisis:
                    EventManager.Instance.Emit(GameEvents.DEBT_CRITICAL, playerCharacter);
                    break;
            }
        }

        // ========== 技能使用 ==========

        public CombatResult UseSkill(Character user, SkillBase skill, Character target)
        {
            if (!battleActive)
            {
                Debug.LogWarning("[BattleManager] 战斗未激活，无法使用技能");
                return null;
            }

            Debug.Log($"[BattleManager] {user.Name} 使用技能: {skill.Name}");

            // 调用核心战斗解析器
            CombatResult result = CombatResolver.ResolveSkillUse(user, skill, target);

            // 添加到战斗日志
            if (showCombatLog && !string.IsNullOrEmpty(result.CombatLog))
            {
                combatLog.Add(result.CombatLog);
                Debug.Log(result.CombatLog);
            }

            // 触发技能使用事件
            var eventData = new BattleEventData
            {
                Attacker = user,
                Defender = target,
                SkillUsed = skill,
                Result = result
            };

            EventManager.Instance.Emit(GameEvents.SKILL_USE, eventData);

            if (result.Success)
            {
                EventManager.Instance.Emit(GameEvents.SKILL_SUCCESS, eventData);
            }
            else
            {
                EventManager.Instance.Emit(GameEvents.SKILL_FAILURE, eventData);
                EventManager.Instance.Emit(GameEvents.SKILL_BACKLASH, eventData);
            }

            // 检查债务警告
            CheckDebtWarnings(user);

            // 检查战斗是否结束
            BattleResult battleResult = CombatResolver.CheckBattleEnd(playerCharacter, enemyCharacter);
            if (battleResult != BattleResult.None)
            {
                EndBattle(battleResult);
            }

            return result;
        }

        // ========== 基础攻击 ==========

        public CombatResult UseBasicAttack(Character attacker, Character target, int baseDamage = 15)
        {
            if (!battleActive)
            {
                Debug.LogWarning("[BattleManager] 战斗未激活，无法进行攻击");
                return null;
            }

            Debug.Log($"[BattleManager] {attacker.Name} 进行基础攻击");

            // 调用核心战斗解析器
            CombatResult result = CombatResolver.ResolveBasicAttack(attacker, target, baseDamage);

            // 添加到战斗日志
            if (showCombatLog && !string.IsNullOrEmpty(result.CombatLog))
            {
                combatLog.Add(result.CombatLog);
                Debug.Log(result.CombatLog);
            }

            // 检查战斗是否结束
            BattleResult battleResult = CombatResolver.CheckBattleEnd(playerCharacter, enemyCharacter);
            if (battleResult != BattleResult.None)
            {
                EndBattle(battleResult);
            }

            return result;
        }

        // ========== 敌人AI ==========

        public void EnemyTurn()
        {
            if (!battleActive || enemyCharacter == null)
                return;

            Debug.Log($"[BattleManager] 敌人回合: {enemyCharacter.Name}");

            // 技能AI：优先使用可用技能，否则退化为基础攻击
            SkillBase selectedSkill = SelectEnemySkill();
            CombatResult result;

            if (selectedSkill != null)
            {
                Debug.Log($"[BattleManager] 敌人使用技能: {selectedSkill.Name}");
                result = CombatResolver.ResolveSkillUse(enemyCharacter, selectedSkill, playerCharacter);
            }
            else
            {
                int baseAttackPower = 12;
                result = CombatResolver.ResolveEnemyAttack(enemyCharacter, playerCharacter, baseAttackPower);
            }

            if (result != null && showCombatLog)
            {
                combatLog.Add(result.CombatLog);
                Debug.Log(result.CombatLog);
            }

            // 检查战斗是否结束
            BattleResult battleResult = CombatResolver.CheckBattleEnd(playerCharacter, enemyCharacter);
            if (battleResult != BattleResult.None)
            {
                EndBattle(battleResult);
            }
        }

        /// <summary>
        /// 选择敌人可用的技能。优先选择成功率最高的技能，失败返回null使用基础攻击。
        /// </summary>
        private SkillBase SelectEnemySkill()
        {
            if (enemyCharacter.Skills == null || enemyCharacter.Skills.Count == 0)
                return null;

            SkillBase best = null;
            int bestRate = 0;

            foreach (var skill in enemyCharacter.Skills)
            {
                if (skill.IsOnCooldown() || !enemyCharacter.CanUseSkill(skill))
                    continue;

                int rate = skill.GetModifiedSuccessRate(enemyCharacter);
                if (rate > bestRate)
                {
                    bestRate = rate;
                    best = skill;
                }
            }

            return best;
        }

        // ========== 冷却管理 ==========

        private void ReduceAllCooldowns(Character character)
        {
            foreach (var skill in character.Skills)
            {
                skill.ReduceCooldown();
            }
        }

        // ========== 债务警告检查 ==========

        private void CheckDebtWarnings(Character character)
        {
            DebtStatus status = character.GetDebtStatus();

            var eventData = new CharacterEventData
            {
                Character = character,
                NewDebtValue = character.RealityDebt,
                DebtStatus = status
            };

            switch (status)
            {
                case DebtStatus.Warning:
                    EventManager.Instance.Emit(GameEvents.DEBT_WARNING, eventData);
                    break;

                case DebtStatus.Dangerous:
                case DebtStatus.Critical:
                    EventManager.Instance.Emit(GameEvents.DEBT_CRITICAL, eventData);
                    break;
            }
        }

        // ========== 休息恢复 ==========

        public void PlayerRest()
        {
            if (!battleActive)
                return;

            Debug.Log($"[BattleManager] {playerCharacter.Name} 休息");

            playerCharacter.Rest();

            // 敌人攻击
            EnemyTurn();
        }

        // ========== 胜利处理 ==========

        private void OnVictory()
        {
            Debug.Log("[BattleManager] 战斗胜利！");

            // 奖励结算
            // 可以在这里添加奖励逻辑
        }

        // ========== 调试 ==========

        private void OnGUI()
        {
#if UNITY_EDITOR
            if (!battleActive) return;

            GUILayout.BeginArea(new Rect(Screen.width - 320, 10, 300, 400));
            GUILayout.BeginVertical("box");

            GUILayout.Label("战斗状态");
            GUILayout.Label($"回合: {currentTurn}");
            GUILayout.Label($"玩家: {playerCharacter.Name}");
            GUILayout.Label($"生命: {playerCharacter.CurrentHealth}/{playerCharacter.MaxHealth}");
            GUILayout.Label($"债务: {playerCharacter.RealityDebt}/1000");
            GUILayout.Label($"疲劳: {playerCharacter.Fatigue}/100");

            if (enemyCharacter != null)
            {
                GUILayout.Label($"敌人: {enemyCharacter.Name}");
                GUILayout.Label($"生命: {enemyCharacter.CurrentHealth}/{enemyCharacter.MaxHealth}");
            }

            GUILayout.EndVertical();
            GUILayout.EndArea();
#endif
        }
    }
}
