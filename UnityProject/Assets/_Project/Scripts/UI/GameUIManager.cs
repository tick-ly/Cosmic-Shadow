using UnityEngine;
using UnityEngine.UI;
using TMPro;
using ShadowOfTheUniverse.Core;
using ShadowOfTheUniverse.Systems;
using ShadowOfTheUniverse.Strategy;

namespace ShadowOfTheUniverse.UI
{
    public class GameUIManager : MonoBehaviour
    {
        private static GameUIManager instance;
        public static GameUIManager Instance => instance;

        [Header("HUD")]
        public TextMeshProUGUI creditsText;
        public TextMeshProUGUI suppressionText;
        public TextMeshProUGUI turnText;
        public Image suppressionFillImage;

        [Header("Info Panel")]
        public GameObject infoPanelRoot;
        public TextMeshProUGUI infoPanelTitle;
        public TextMeshProUGUI infoPanelBody;

        [Header("Battle Report")]
        public GameObject battleReportRoot;
        public ScrollRect battleScrollRect;
        public TextMeshProUGUI battleLogText;
        public int maxLogLines = 50;

        private StringCache logCache = new StringCache();
        private int logLineCount;
        private object currentSelection;

        private void Awake()
        {
            if (instance != null && instance != this) { Destroy(gameObject); return; }
            instance = this;
            if (infoPanelRoot != null) infoPanelRoot.SetActive(false);
            if (battleReportRoot != null) battleReportRoot.SetActive(false);
        }

        private void Start()
        {
            EventManager.Instance.Subscribe(GameEvents.TURN_START, OnTurnStart);
            EventManager.Instance.Subscribe(GameEvents.CREDITS_CHANGED, OnCreditsChanged);
            EventManager.Instance.Subscribe(GameEvents.SUPPRESSION_CHANGED, OnSuppressionChanged);
            EventManager.Instance.Subscribe(GameEvents.BATTLE_START, OnBattleStart);
            EventManager.Instance.Subscribe(GameEvents.BATTLE_END, OnBattleEnd);
            EventManager.Instance.Subscribe(GameEvents.SKILL_USE, OnSkillUsed);
            EventManager.Instance.Subscribe(GameEvents.UNIT_MOVED, OnUnitMoved);
            RefreshHUD();
        }

        private void OnDestroy()
        {
            if (EventManager.Instance != null)
            {
                EventManager.Instance.Unsubscribe(GameEvents.TURN_START, OnTurnStart);
                EventManager.Instance.Unsubscribe(GameEvents.CREDITS_CHANGED, OnCreditsChanged);
                EventManager.Instance.Unsubscribe(GameEvents.SUPPRESSION_CHANGED, OnSuppressionChanged);
                EventManager.Instance.Unsubscribe(GameEvents.BATTLE_START, OnBattleStart);
                EventManager.Instance.Unsubscribe(GameEvents.BATTLE_END, OnBattleEnd);
                EventManager.Instance.Unsubscribe(GameEvents.SKILL_USE, OnSkillUsed);
                EventManager.Instance.Unsubscribe(GameEvents.UNIT_MOVED, OnUnitMoved);
            }
            if (instance == this) instance = null;
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.Escape)) CloseInfoPanel();
        }

        public void RefreshHUD()
        {
            var gs = GameState.Instance;
            if (creditsText != null) creditsText.text = "淇＄敤鐐? " + gs.Credits;
            if (suppressionText != null) suppressionText.text = "濡ュ崗: " + gs.Suppression + "/" + gs.MaxSuppression;
            if (turnText != null) turnText.text = "鍥炲悎 " + gs.CurrentTurn;
            if (suppressionFillImage != null)
            {
                suppressionFillImage.fillAmount = (float)gs.Suppression / gs.MaxSuppression;
                if (gs.Suppression < 30)
                    suppressionFillImage.color = new Color(0.2f, 0.8f, 0.2f);
                else if (gs.Suppression < 70)
                    suppressionFillImage.color = new Color(0.9f, 0.7f, 0.2f);
                else
                    suppressionFillImage.color = new Color(0.9f, 0.2f, 0.2f);
            }
        }

        public void ShowNodeInfo(StarNode node)
        {
            if (infoPanelRoot == null || node == null) return;
            currentSelection = node;
            if (infoPanelTitle != null) infoPanelTitle.text = node.nodeName;
            if (infoPanelBody != null)
            {
                string body = "<b>鍦板舰:</b> " + node.terrainType + "\n" +
                              "<b>瑙嗛噹鐘舵€?</b> " + node.visibility + "\n" +
                              "<b>鍧愭爣:</b> (" + Mathf.RoundToInt(node.transform.position.x) + ", " + Mathf.RoundToInt(node.transform.position.z) + ")\n" +
                              "<b>杩炴帴鑺傜偣:</b> " + node.connectedNodes.Count;
                if (MapManager.Instance != null)
                {
                    var mn = !string.IsNullOrEmpty(node.mapNodeId)
                        ? MapManager.Instance.GetNode(node.mapNodeId)
                        : MapManager.Instance.GetNodeAtWorldPosition(node.transform.position.x, node.transform.position.z);
                    if (mn != null)
                    {
                        body += "\n<b>鎴樼暐浠峰€?</b> " + mn.StrategicValue;
                        body += "\n<b>鎺у埗鑰?</b> " + mn.Owner;
                    }
                }
                infoPanelBody.text = body;
            }
            SetInfoPanelVisible(true);
        }

        public void ShowUnitInfo(CombatUnitController unit)
        {
            if (infoPanelRoot == null || unit == null || unit.Model == null) return;
            currentSelection = unit;
            var model = unit.Model;
            if (infoPanelTitle != null) infoPanelTitle.text = model.UnitName;
            if (infoPanelBody != null)
            {
                string domainIcon = model.Domain switch
                {
                    UnitDomain.Land => "[L]",
                    UnitDomain.Sea  => "[S]",
                    UnitDomain.Air  => "[A]",
                    _ => "[?]"
                };
                string body = domainIcon + " <b>" + model.Domain + "</b> x <b>" + model.Scale + "</b>\n" +
                              "<b>鐘舵€?</b> " + model.State + "\n" +
                              "<b>褰撳墠浣嶇疆:</b> " + (model.CurrentNode != null ? model.CurrentNode.nodeName : "鏈煡");
                if (model.State == UnitState.Moving && model.TargetNode != null)
                    body += "\n<b>绉诲姩涓?</b> " + model.TargetNode.nodeName;
                body += "\n<b>閫熷害:</b> " + model.MovementSpeed.ToString("F1");
                infoPanelBody.text = body;
            }
            SetInfoPanelVisible(true);
        }

        public void CloseInfoPanel()
        {
            currentSelection = null;
            SetInfoPanelVisible(false);
        }

        private void SetInfoPanelVisible(bool visible)
        {
            if (infoPanelRoot != null) infoPanelRoot.SetActive(visible);
        }

        public void AppendBattleLog(string message)
        {
            if (battleLogText == null) return;
            string turnLabel = "[" + GameState.Instance.CurrentTurn + "] ";
            string entry = turnLabel + message + "\n";
            logCache.Append(entry);
            logLineCount++;
            if (logLineCount > maxLogLines)
            {
                logCache.TrimOldest(maxLogLines / 2);
                logLineCount = maxLogLines;
            }
            battleLogText.text = logCache.ToString();
            if (battleScrollRect != null)
            {
                Canvas.ForceUpdateCanvases();
                battleScrollRect.verticalNormalizedPosition = 0f;
            }
        }

        public void ClearBattleLog()
        {
            logCache.Clear();
            logLineCount = 0;
            if (battleLogText != null) battleLogText.text = "";
        }

        public void ToggleBattleReport()
        {
            if (battleReportRoot != null) battleReportRoot.SetActive(!battleReportRoot.activeSelf);
        }

        public bool IsBattleReportVisible() => battleReportRoot != null && battleReportRoot.activeSelf;

        private void OnTurnStart(object data)
        {
            RefreshHUD();
            AppendBattleLog("===== 绗?" + GameState.Instance.CurrentTurn + " 鍥炲悎寮€濮?=====");
        }

        private void OnCreditsChanged(object data) { RefreshHUD(); }
        private void OnSuppressionChanged(object data) { RefreshHUD(); }

        private void OnBattleStart(object data)
        {
            if (data is BattleEventData bd)
            {
                if (!IsBattleReportVisible()) ToggleBattleReport();
                AppendBattleLog("** 鎴樻枟寮€濮? " + (bd.Attacker != null ? bd.Attacker.Name : "?") + " vs " + (bd.Defender != null ? bd.Defender.Name : "?"));
            }
        }

        private void OnBattleEnd(object data)
        {
            if (data is BattleResult result)
            {
                string msg = result switch
                {
                    BattleResult.HeroVictory => "[鑳滃埄] 鎴樻枟鑾疯儨!",
                    BattleResult.HeroDefeated => "[澶辫触] 鎴樻枟澶辫触...",
                    BattleResult.DebtCrisis => "[鍗辨満] 鐜板疄鍊哄姟宕╂簝!",
                    _ => "鎴樻枟缁撴潫"
                };
                AppendBattleLog(msg);
            }
        }

        private void OnSkillUsed(object data)
        {
            if (data is BattleEventData bd && bd.Result != null)
            {
                string tag = bd.Result.Success ? "[鎴愬姛]" : "[澶辫触]";
                AppendBattleLog(tag + " " + (bd.SkillUsed != null ? bd.SkillUsed.Name : "?") + ": " + bd.Result.CombatLog);
            }
        }

        private void OnUnitMoved(object data)
        {
            if (data is UnitMoveEventData md)
                AppendBattleLog(">> " + md.UnitName + " 绉诲姩鑷?" + md.TargetNodeName);
        }

        private class StringCache
        {
            private System.Text.StringBuilder sb = new System.Text.StringBuilder();
            public void Append(string text) { sb.Append(text); }
            public void TrimOldest(int keepLines)
            {
                string[] lines = sb.ToString().Split('\n');
                sb.Clear();
                int start = Mathf.Max(0, lines.Length - keepLines);
                for (int i = start; i < lines.Length; i++)
                {
                    sb.Append(lines[i]);
                    if (i < lines.Length - 1) sb.Append('\n');
                }
            }
            public void Clear() { sb.Clear(); }
            public override string ToString() => sb.ToString();
        }
    }
}

