using ShadowOfTheUniverse.V2.Core;
using UnityEngine;
using UnityEngine.UI;

namespace ShadowOfTheUniverse.V2.UI
{
    public sealed class MissionHudController : MonoBehaviour
    {
        [SerializeField] private Text titleText;
        [SerializeField] private Text statusText;
        [SerializeField] private Text logText;

        public void EnsureDefaultLayout(Canvas canvas)
        {
            if (titleText != null && statusText != null && logText != null)
            {
                return;
            }

            Image panel = UiFactory.CreatePanel(
                "Mission HUD",
                canvas.transform,
                new Vector2(0f, 1f),
                new Vector2(0f, 1f),
                new Vector2(24f, -350f),
                new Vector2(520f, -24f));

            titleText = UiFactory.CreateText("Title", panel.transform, 24, TextAnchor.UpperLeft);
            RectTransform titleRect = titleText.GetComponent<RectTransform>();
            titleRect.anchorMin = new Vector2(0f, 1f);
            titleRect.anchorMax = new Vector2(1f, 1f);
            titleRect.offsetMin = new Vector2(18f, -48f);
            titleRect.offsetMax = new Vector2(-18f, -12f);

            statusText = UiFactory.CreateText("Status", panel.transform, 18, TextAnchor.UpperLeft);
            RectTransform statusRect = statusText.GetComponent<RectTransform>();
            statusRect.anchorMin = new Vector2(0f, 0.45f);
            statusRect.anchorMax = new Vector2(1f, 1f);
            statusRect.offsetMin = new Vector2(18f, 0f);
            statusRect.offsetMax = new Vector2(-18f, -56f);

            logText = UiFactory.CreateText("Log", panel.transform, 16, TextAnchor.LowerLeft);
            RectTransform logRect = logText.GetComponent<RectTransform>();
            logRect.anchorMin = new Vector2(0f, 0f);
            logRect.anchorMax = new Vector2(1f, 0.45f);
            logRect.offsetMin = new Vector2(18f, 14f);
            logRect.offsetMax = new Vector2(-18f, -4f);
        }

        public void Refresh(MissionState state, UnitState selectedUnit)
        {
            if (state == null)
            {
                return;
            }

            if (titleText != null)
            {
                titleText.text = state.DisplayName;
            }

            if (statusText != null)
            {
                string unitText = selectedUnit != null
                    ? selectedUnit.DisplayName + " HP " + selectedUnit.CurrentHealth + "/" + selectedUnit.MaxHealth + " Debt " + selectedUnit.RealityDebt
                    : "No unit selected";
                statusText.text =
                    "Outcome: " + state.Outcome + "\n" +
                    "Time: " + state.ElapsedSeconds + "/" + state.TimeLimitSeconds + "\n" +
                    "Alert: " + state.AlertLevel + "/" + state.MaxAlertLevel + "\n" +
                    "Objective: " + state.ObjectiveProgress + "/" + state.ObjectiveRequired + "\n" +
                    "Selected: " + unitText + "\n" +
                    "Budget: " + (selectedUnit != null ? selectedUnit.CompromisePoints.ToString() : "-") +
                    (state.Encounters.Enabled ? " / " + state.Encounters.Phase : "");
            }

            if (logText != null)
            {
                int start = Mathf.Max(0, state.Log.Count - 4);
                string text = string.Empty;
                for (int i = start; i < state.Log.Count; i++)
                {
                    text += state.Log[i] + "\n";
                }

                logText.text = text;
            }
        }
    }
}
