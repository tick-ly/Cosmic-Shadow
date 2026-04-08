using System.Collections.Generic;
using ShadowOfTheUniverse.Core;
using ShadowOfTheUniverse.Data;
using ShadowOfTheUniverse.Systems;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

namespace ShadowOfTheUniverse.UI
{
    public class RiskAssessmentPanel : MonoBehaviour
    {
        [Header("Panel Root")]
        [SerializeField] private GameObject panelRoot;

        [Header("Node Info")]
        [SerializeField] private TextMeshProUGUI nodeNameText;
        [SerializeField] private TextMeshProUGUI nodeDetailText;

        [Header("Debt")]
        [SerializeField] private Slider debtSlider;
        [SerializeField] private TextMeshProUGUI debtValueText;

        [Header("Skill List")]
        [SerializeField] private Transform skillButtonContainer;
        [SerializeField] private Button skillButtonPrefab;

        [Header("Selection")]
        [SerializeField] private TextMeshProUGUI selectedSkillNameText;
        [SerializeField] private TextMeshProUGUI selectedSkillDescText;
        [SerializeField] private TextMeshProUGUI successRateText;
        [SerializeField] private TextMeshProUGUI riskLevelText;

        [Header("Actions")]
        [SerializeField] private Button executeButton;
        [SerializeField] private Button cancelButton;
        [SerializeField] private TextMeshProUGUI executionResultText;

        [Header("Defaults")]
        [SerializeField] private CharacterClassSO defaultPlayerClass;
        [SerializeField] private SkillDataSO[] defaultPlayerSkills;
        [SerializeField] private SkillDataSO[] defaultEnemySkills;
        [SerializeField] private string fallbackPlayerName = "Operator Zero";

        private readonly List<Button> spawnedSkillButtons = new List<Button>();

        private MapNode currentNode;
        private Character currentPlayer;
        private Character currentEnemy;
        private SkillBase selectedSkill;
        private bool settlementCompleted;

        public bool IsVisible => panelRoot != null && panelRoot.activeSelf;
        public string CurrentNodeId => currentNode != null ? currentNode.NodeId : string.Empty;

        private void Awake()
        {
            if (panelRoot == null)
            {
                panelRoot = gameObject;
            }

            if (executeButton != null)
            {
                executeButton.onClick.AddListener(OnExecuteClicked);
            }

            if (cancelButton != null)
            {
                cancelButton.onClick.AddListener(ClosePanel);
            }

            SetPanelVisible(false);
        }

        private void OnDestroy()
        {
            if (executeButton != null)
            {
                executeButton.onClick.RemoveListener(OnExecuteClicked);
            }

            if (cancelButton != null)
            {
                cancelButton.onClick.RemoveListener(ClosePanel);
            }

            ClearSkillButtons();
        }

        public void OpenForNode(MapNode node, string fallbackNodeName = null)
        {
            if (node == null)
            {
                return;
            }

            currentNode = node;
            currentPlayer = EnsurePlayerCharacter();
            currentEnemy = CreateEnemyForNode(node);
            selectedSkill = null;
            settlementCompleted = false;

            UpdateNodeInfo(fallbackNodeName);
            UpdateDebtUI();
            RebuildSkillButtons();
            RefreshSelectionUI();

            if (executionResultText != null)
            {
                executionResultText.text = string.Empty;
            }

            SetPanelVisible(true);
        }

        public void ClosePanel()
        {
            settlementCompleted = false;
            selectedSkill = null;
            currentNode = null;
            currentEnemy = null;

            ClearSkillButtons();
            SetPanelVisible(false);
        }

        private void OnExecuteClicked()
        {
            if (settlementCompleted)
            {
                return;
            }

            if (currentNode == null || currentPlayer == null || currentEnemy == null || selectedSkill == null)
            {
                SetResultText("Missing battle context. Reopen the panel and try again.");
                return;
            }

            if (selectedSkill.IsOnCooldown() || !currentPlayer.CanUseSkill(selectedSkill))
            {
                SetResultText("Selected skill cannot be used right now.");
                RefreshSelectionUI();
                return;
            }

            if (BattleManager.Instance.IsBattleActive)
            {
                SetResultText("Another battle is currently active. Finish it first.");
                return;
            }

            BattleManager.Instance.StartBattle(currentPlayer, currentEnemy);
            CombatResult result = BattleManager.Instance.UseSkill(currentPlayer, selectedSkill, currentEnemy);

            if (result == null)
            {
                SetResultText("Combat resolution failed.");
                return;
            }

            if (!string.IsNullOrEmpty(result.Error))
            {
                SetResultText(result.Error);
                return;
            }

            ApplyNodeSettlement(result);

            if (BattleManager.Instance.IsBattleActive)
            {
                BattleResult endResult = result.Success ? BattleResult.HeroVictory : BattleResult.HeroDefeated;
                BattleManager.Instance.EndBattle(endResult);
            }

            settlementCompleted = true;
            UpdateDebtUI();
            RefreshSelectionUI();
        }

        private void ApplyNodeSettlement(CombatResult result)
        {
            if (currentNode == null)
            {
                return;
            }

            if (result.Success)
            {
                currentNode.Owner = NodeOwner.Player;
                currentNode.GarrisonStrength = 0;
                GameState.Instance.DiscoverNode(currentNode.NodeId);
                EventManager.Instance.Emit(GameEvents.NODE_CAPTURED, currentNode.NodeId);
                GameState.Instance.AddCredits(Mathf.Max(1, currentNode.StrategicValue));

                SetResultText($"Success: {currentNode.NodeName} captured.");
                if (GameUIManager.Instance != null)
                {
                    GameUIManager.Instance.AppendBattleLog($"[Node Captured] {currentNode.NodeName}");
                }
            }
            else
            {
                currentNode.Owner = NodeOwner.Enemy;
                currentNode.GarrisonStrength = Mathf.Max(currentNode.GarrisonStrength, 1);
                GameState.Instance.AddSuppression(2);

                SetResultText($"Failure: assault on {currentNode.NodeName} failed.");
                if (GameUIManager.Instance != null)
                {
                    GameUIManager.Instance.AppendBattleLog($"[Assault Failed] {currentNode.NodeName}");
                }
            }

            UpdateNodeInfo(currentNode.NodeName);
        }

        private void RebuildSkillButtons()
        {
            ClearSkillButtons();

            if (skillButtonContainer == null || skillButtonPrefab == null || currentPlayer == null)
            {
                return;
            }

            foreach (SkillBase skill in currentPlayer.Skills)
            {
                SkillBase localSkill = skill;
                Button button = Instantiate(skillButtonPrefab, skillButtonContainer);
                button.onClick.RemoveAllListeners();
                button.onClick.AddListener(() => SelectSkill(localSkill));

                TextMeshProUGUI label = button.GetComponentInChildren<TextMeshProUGUI>();
                if (label != null)
                {
                    label.text = localSkill.Name;
                }
                else
                {
                    Text legacyLabel = button.GetComponentInChildren<Text>();
                    if (legacyLabel != null)
                    {
                        legacyLabel.text = localSkill.Name;
                    }
                }

                bool usable = !localSkill.IsOnCooldown() && currentPlayer.CanUseSkill(localSkill);
                button.interactable = usable;

                spawnedSkillButtons.Add(button);
            }

            if (spawnedSkillButtons.Count == 0)
            {
                SetResultText("No skills available. Configure SkillDataSO for the player.");
            }
        }

        private void ClearSkillButtons()
        {
            for (int i = 0; i < spawnedSkillButtons.Count; i++)
            {
                if (spawnedSkillButtons[i] != null)
                {
                    Destroy(spawnedSkillButtons[i].gameObject);
                }
            }

            spawnedSkillButtons.Clear();
        }

        private void SelectSkill(SkillBase skill)
        {
            selectedSkill = skill;
            RefreshSelectionUI();
        }

        private void RefreshSelectionUI()
        {
            if (selectedSkillNameText != null)
            {
                selectedSkillNameText.text = selectedSkill != null ? selectedSkill.Name : "Select a skill";
            }

            if (selectedSkillDescText != null)
            {
                selectedSkillDescText.text = selectedSkill != null ? selectedSkill.Description : "-";
            }

            if (successRateText != null)
            {
                successRateText.text = selectedSkill != null && currentPlayer != null
                    ? $"{selectedSkill.GetModifiedSuccessRate(currentPlayer)}%"
                    : "--";
            }

            if (riskLevelText != null)
            {
                riskLevelText.text = selectedSkill != null && currentPlayer != null
                    ? selectedSkill.GetRiskLevel(currentPlayer).ToString()
                    : "--";
            }

            bool canExecute = !settlementCompleted &&
                              selectedSkill != null &&
                              currentPlayer != null &&
                              currentEnemy != null &&
                              !selectedSkill.IsOnCooldown() &&
                              currentPlayer.CanUseSkill(selectedSkill);

            if (executeButton != null)
            {
                executeButton.interactable = canExecute;
            }
        }

        private void UpdateNodeInfo(string fallbackNodeName)
        {
            if (currentNode == null)
            {
                return;
            }

            if (nodeNameText != null)
            {
                nodeNameText.text = string.IsNullOrEmpty(currentNode.NodeName) ? fallbackNodeName : currentNode.NodeName;
            }

            if (nodeDetailText != null)
            {
                nodeDetailText.text =
                    $"Owner: {currentNode.Owner}\n" +
                    $"Terrain: {currentNode.Terrain}\n" +
                    $"Garrison: {currentNode.GarrisonStrength}\n" +
                    $"Strategic Value: {currentNode.StrategicValue}";
            }
        }

        private void UpdateDebtUI()
        {
            if (currentPlayer == null)
            {
                return;
            }

            if (debtValueText != null)
            {
                debtValueText.text = $"{currentPlayer.RealityDebt}/1000";
            }

            if (debtSlider != null)
            {
                debtSlider.minValue = 0f;
                debtSlider.maxValue = 1000f;
                debtSlider.value = currentPlayer.RealityDebt;
            }
        }

        private Character EnsurePlayerCharacter()
        {
            Character player = GameState.Instance.PlayerCharacter;
            if (player == null)
            {
                BloodlineTier tier = defaultPlayerClass != null ? defaultPlayerClass.Tier : BloodlineTier.Low;
                int hp = defaultPlayerClass != null ? defaultPlayerClass.BaseMaxHealth : 100;
                player = new Character(fallbackPlayerName, tier, defaultPlayerClass, hp);
                GameState.Instance.PlayerCharacter = player;
            }

            if (player.Skills.Count == 0)
            {
                AddSkillsFromAssets(player, defaultPlayerSkills);

                if (player.Skills.Count == 0)
                {
                    AddFallbackPlayerSkills(player);
                }
            }

            return player;
        }

        private Character CreateEnemyForNode(MapNode node)
        {
            int pressure = Mathf.Max(1, node.GarrisonStrength) + Mathf.Max(0, node.StrategicValue / 2);
            int maxHealth = Mathf.Clamp(45 + pressure * 10, 45, 220);
            Character enemy = new Character($"{node.NodeName} Guard", BloodlineTier.Low, null, maxHealth);

            AddSkillsFromAssets(enemy, defaultEnemySkills);
            if (enemy.Skills.Count == 0)
            {
                enemy.AddSkill(new SkillBase(
                    "enemy_suppress_fire",
                    "Suppressive Fire",
                    BloodlineTier.Low,
                    "Basic suppression attack.",
                    75,
                    6,
                    12,
                    8,
                    0,
                    new SkillEffect("Suppressive fire landed.", "Suppressive fire scattered.")
                ));
            }

            return enemy;
        }

        private static void AddSkillsFromAssets(Character character, SkillDataSO[] skillAssets)
        {
            if (character == null || skillAssets == null)
            {
                return;
            }

            for (int i = 0; i < skillAssets.Length; i++)
            {
                SkillDataSO skillData = skillAssets[i];
                if (skillData == null)
                {
                    continue;
                }

                character.AddSkill(skillData.CreateSkillInstance());
            }
        }

        private static void AddFallbackPlayerSkills(Character player)
        {
            player.AddSkill(new SkillBase(
                "heat_shift",
                "Heat Shift",
                BloodlineTier.Low,
                "Redirect localized thermal energy.",
                90,
                8,
                24,
                10,
                0,
                new SkillEffect("Thermal shift succeeded.", "Thermal feedback injured the user.")
            ));

            player.AddSkill(new SkillBase(
                "static_charge",
                "Static Charge",
                BloodlineTier.Low,
                "Gather static charge and release a directed strike.",
                85,
                10,
                20,
                8,
                0,
                new SkillEffect("Static burst hit the target.", "Static backlash struck the user.")
            ));

            player.AddSkill(new SkillBase(
                "reflex_boost",
                "Reflex Boost",
                BloodlineTier.Low,
                "Momentary overclock for precision attack windows.",
                95,
                5,
                30,
                5,
                0,
                new SkillEffect("Reflex timing was perfect.", "Neural load caused self-disruption.")
            ));
        }

        private void SetResultText(string message)
        {
            if (executionResultText != null)
            {
                executionResultText.text = message;
            }
        }

        private void SetPanelVisible(bool visible)
        {
            if (panelRoot != null)
            {
                panelRoot.SetActive(visible);
            }
        }
    }
}
