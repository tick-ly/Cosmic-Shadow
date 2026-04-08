using UnityEngine;
using ShadowOfTheUniverse.Core;
using ShadowOfTheUniverse.Data;

namespace ShadowOfTheUniverse.Systems
{
    /// <summary>
    /// 游戏演示脚本 - MonoBehaviour
    /// 展示如何使用游戏系统创建角色、技能并进行战斗
    /// </summary>
    public class GameDemo : MonoBehaviour
    {
        [Header("演示设置")]
        [SerializeField] private bool autoStartDemo = true;
        [SerializeField] private CharacterClassSO playerClassData;
        [SerializeField] private SkillDataSO[] playerSkills;

        public bool AutoStartDemo
        {
            get => autoStartDemo;
            set => autoStartDemo = value;
        }

        private Character playerCharacter;
        private Character enemyCharacter;

        private void Start()
        {
            if (autoStartDemo)
            {
                InitializeDemo();
            }
        }

        private void InitializeDemo()
        {
            Debug.Log("=== 宇宙之影 - 游戏系统演示 ===");

            // 1. 创建玩家角色
            CreatePlayerCharacter();

            // 2. 创建敌人
            CreateEnemyCharacter();

            // 3. 开始战斗
            StartBattleDemo();
        }

        private void CreatePlayerCharacter()
        {
            // 如果没有指定类别数据，使用默认值
            if (playerClassData == null)
            {
                Debug.LogWarning("未指定玩家类别数据，使用默认低级血统");
                playerCharacter = new Character(
                    "零号实验体",
                    BloodlineTier.Low,
                    null,  // 暂时使用null
                    100     // 最大生命值
                );
            }
            else
            {
                playerCharacter = new Character(
                    "零号实验体",
                    playerClassData.Tier,
                    playerClassData,
                    playerClassData.BaseMaxHealth
                );
            }

            // 添加技能
            if (playerSkills != null && playerSkills.Length > 0)
            {
                foreach (var skillData in playerSkills)
                {
                    if (skillData != null)
                    {
                        SkillBase skill = skillData.CreateSkillInstance();
                        playerCharacter.AddSkill(skill);
                        Debug.Log($"添加技能: {skill.Name} (成功率: {skill.GetBaseSuccessRate()}%)");
                    }
                }
            }
            else
            {
                // 创建默认技能
                CreateDefaultSkills();
            }

            Debug.Log($"玩家角色创建完成: {playerCharacter.Name}");
            Debug.Log($"血统等级: {playerCharacter.Tier}");
            Debug.Log($"生命值: {playerCharacter.CurrentHealth}/{playerCharacter.MaxHealth}");
        }

        private void CreateDefaultSkills()
        {
            // 热量转移
            SkillBase heatSkill = new SkillBase(
                "heat_transfer",
                "热量转移",
                BloodlineTier.Low,
                "轻微违反热力学第二定律，转移局部热量",
                90,  // 基础成功率
                8,   // 现实债务
                25,  // 成功伤害
                10,  // 失败反噬
                0,   // 冷却
                new SkillEffect(
                    "你成功转移热量，敌人皮肤灼伤！",
                    "热量转移失控！你自己也被灼伤了！"
                )
            );
            playerCharacter.AddSkill(heatSkill);

            // 静电聚集
            SkillBase chargeSkill = new SkillBase(
                "static_charge",
                "静电聚集",
                BloodlineTier.Low,
                "轻微违反库伦定律，聚集静电电荷",
                85,
                10,
                20,
                8,
                0,
                new SkillEffect(
                    "电荷成功聚集！敌人被电击！",
                    "电荷失控！你自己也被电到了！"
                )
            );
            playerCharacter.AddSkill(chargeSkill);

            // 反应增强
            SkillBase reactionSkill = new SkillBase(
                "reaction_boost",
                "反应增强",
                BloodlineTier.Low,
                "轻微提升神经传导速度",
                95,
                5,
                30,
                5,
                0,
                new SkillEffect(
                    "反应速度大幅提升！攻击精准命中！",
                    "神经负担过重！反应混乱！"
                )
            );
            playerCharacter.AddSkill(reactionSkill);
        }

        private void CreateEnemyCharacter()
        {
            enemyCharacter = new Character(
                "失控实验体",
                BloodlineTier.Low,
                null,
                80
            );

            Debug.Log($"敌人角色创建完成: {enemyCharacter.Name}");
        }

        private void StartBattleDemo()
        {
            Debug.Log("\n=== 战斗开始 ===");

            // 初始化战斗管理器
            BattleManager.Instance.StartBattle(playerCharacter, enemyCharacter);

            // 演示技能使用
            DemonstrateSkillUse();
        }

        private void DemonstrateSkillUse()
        {
            if (playerCharacter.Skills.Count == 0)
            {
                Debug.LogWarning("玩家没有可用技能");
                return;
            }

            // 使用第一个技能
            SkillBase skill = playerCharacter.Skills[0];

            Debug.Log($"\n--- 演示技能: {skill.Name} ---");
            Debug.Log($"描述: {skill.Description}");
            Debug.Log($"基础成功率: {skill.GetBaseSuccessRate()}%");

            // 计算修正后的成功率
            int modifiedRate = skill.GetModifiedSuccessRate(playerCharacter);
            RiskLevel risk = skill.GetRiskLevel(playerCharacter);

            Debug.Log($"修正后成功率: {modifiedRate}%");
            Debug.Log($"风险等级: {risk}");

            // 执行技能
            CombatResult result = BattleManager.Instance.UseSkill(
                playerCharacter,
                skill,
                enemyCharacter
            );

            if (result != null)
            {
                Debug.Log($"\n--- 技能结果 ---");
                Debug.Log($"成功: {result.Success}");
                Debug.Log($"投掷: {result.Roll} / {result.SuccessRate}");
                Debug.Log($"伤害: {result.DamageDealt}");
                Debug.Log($"现实债务: +{result.DebtIncurred}");
                Debug.Log($"疲劳: +{result.FatigueIncurred}");

                // 显示角色状态
                DisplayCharacterStatus();
            }
        }

        private void DisplayCharacterStatus()
        {
            Debug.Log($"\n--- 角色状态 ---");
            Debug.Log($"玩家: {playerCharacter.Name}");
            Debug.Log($"  生命: {playerCharacter.CurrentHealth}/{playerCharacter.MaxHealth}");
            Debug.Log($"  债务: {playerCharacter.RealityDebt}/1000 [{playerCharacter.GetDebtStatus()}]");
            Debug.Log($"  疲劳: {playerCharacter.Fatigue}/100");

            if (enemyCharacter != null)
            {
                Debug.Log($"敌人: {enemyCharacter.Name}");
                Debug.Log($"  生命: {enemyCharacter.CurrentHealth}/{enemyCharacter.MaxHealth}");
            }
        }

        // ========== GUI控制面板 ==========

        private void OnGUI()
        {
            GUILayout.BeginArea(new Rect(10, Screen.height - 200, 400, 180));
            GUILayout.BeginVertical("box");

            GUILayout.Label("=== 游戏演示控制 ===");

            if (GUILayout.Button("重新初始化演示"))
            {
                InitializeDemo();
            }

            if (GUILayout.Button("使用技能"))
            {
                if (playerCharacter != null && playerCharacter.Skills.Count > 0)
                {
                    DemonstrateSkillUse();
                }
            }

            if (GUILayout.Button("基础攻击"))
            {
                if (playerCharacter != null && enemyCharacter != null)
                {
                    BattleManager.Instance.UseBasicAttack(playerCharacter, enemyCharacter);
                    DisplayCharacterStatus();
                }
            }

            if (GUILayout.Button("敌人回合"))
            {
                if (BattleManager.Instance.IsBattleActive)
                {
                    BattleManager.Instance.EnemyTurn();
                    DisplayCharacterStatus();
                }
            }

            if (GUILayout.Button("休息"))
            {
                if (BattleManager.Instance.IsBattleActive)
                {
                    BattleManager.Instance.PlayerRest();
                    DisplayCharacterStatus();
                }
            }

            GUILayout.EndVertical();
            GUILayout.EndArea();
        }
    }
}
