using System;
using ShadowOfTheUniverse.V2.Core;
using UnityEngine;
using UnityEngine.UI;

namespace ShadowOfTheUniverse.V2.UI
{
    public sealed class RiskAssessmentPanel : MonoBehaviour
    {
        [SerializeField] private GameObject root;
        [SerializeField] private Text titleText;
        [SerializeField] private Text detailText;
        [SerializeField] private Transform buttonContainer;
        [SerializeField] private Text resultText;

        private Action<SkillData> onSkillChosen;

        public void EnsureDefaultLayout(Canvas canvas)
        {
            if (root != null)
            {
                return;
            }

            Image panel = UiFactory.CreatePanel(
                "Risk Assessment Panel",
                canvas.transform,
                new Vector2(1f, 0f),
                new Vector2(1f, 1f),
                new Vector2(-460f, 24f),
                new Vector2(-24f, -24f));

            root = panel.gameObject;

            titleText = UiFactory.CreateText("Title", panel.transform, 24, TextAnchor.UpperLeft);
            RectTransform titleRect = titleText.GetComponent<RectTransform>();
            titleRect.anchorMin = new Vector2(0f, 1f);
            titleRect.anchorMax = new Vector2(1f, 1f);
            titleRect.offsetMin = new Vector2(18f, -52f);
            titleRect.offsetMax = new Vector2(-18f, -14f);

            detailText = UiFactory.CreateText("Details", panel.transform, 16, TextAnchor.UpperLeft);
            RectTransform detailRect = detailText.GetComponent<RectTransform>();
            detailRect.anchorMin = new Vector2(0f, 0.52f);
            detailRect.anchorMax = new Vector2(1f, 1f);
            detailRect.offsetMin = new Vector2(18f, 0f);
            detailRect.offsetMax = new Vector2(-18f, -64f);

            GameObject containerObject = new GameObject("Skill Buttons");
            containerObject.transform.SetParent(panel.transform, false);
            buttonContainer = containerObject.transform;
            VerticalLayoutGroup layout = containerObject.AddComponent<VerticalLayoutGroup>();
            layout.spacing = 8f;
            layout.childControlWidth = true;
            layout.childControlHeight = false;
            layout.childForceExpandWidth = true;
            layout.childForceExpandHeight = false;
            RectTransform containerRect = containerObject.GetComponent<RectTransform>();
            containerRect.anchorMin = new Vector2(0f, 0.16f);
            containerRect.anchorMax = new Vector2(1f, 0.52f);
            containerRect.offsetMin = new Vector2(18f, 8f);
            containerRect.offsetMax = new Vector2(-18f, -8f);

            resultText = UiFactory.CreateText("Result", panel.transform, 16, TextAnchor.LowerLeft);
            RectTransform resultRect = resultText.GetComponent<RectTransform>();
            resultRect.anchorMin = new Vector2(0f, 0f);
            resultRect.anchorMax = new Vector2(1f, 0.16f);
            resultRect.offsetMin = new Vector2(18f, 14f);
            resultRect.offsetMax = new Vector2(-18f, -6f);

            root.SetActive(false);
        }

        public void Open(MissionState mission, UnitState unit, NodeDefinition node, Action<SkillData> onSkillSelected)
        {
            if (root == null || unit == null || node == null)
            {
                return;
            }

            onSkillChosen = onSkillSelected;
            root.SetActive(true);

            if (titleText != null)
            {
                titleText.text = "Risk Assessment";
            }

            if (detailText != null)
            {
                detailText.text =
                    "Node: " + node.DisplayName + "\n" +
                    "Terrain: " + node.Terrain + "\n" +
                    "Owner: " + node.Owner + "\n" +
                    "Unit: " + unit.DisplayName + "\n" +
                    "Debt: " + unit.RealityDebt + "  Fatigue: " + unit.Fatigue + "\n" +
                    "Objective: " + mission.ObjectiveProgress + "/" + mission.ObjectiveRequired;
            }

            ClearButtons();
            for (int i = 0; i < unit.Skills.Count; i++)
            {
                SkillData skill = unit.Skills[i];
                SkillRiskAssessment assessment = RiskResolver.Assess(unit, skill);
                string label = skill.DisplayName + "  " + assessment.SuccessRate + "%  " + assessment.RiskLevel + " / " + skill.CompromiseCost + " pts";
                Button button = UiFactory.CreateButton("Skill " + skill.Id, buttonContainer, label);
                button.interactable = assessment.CanUse;
                SkillData capturedSkill = skill;
                button.onClick.AddListener(() => ChooseSkill(capturedSkill));
            }

            if (resultText != null)
            {
                resultText.text = "Choose a risk action.";
            }
        }

        public void ShowResult(SkillResolution resolution)
        {
            if (resultText == null || resolution == null)
            {
                return;
            }

            resultText.text =
                (resolution.Success ? "Success" : "Failure") +
                " | Roll " + resolution.Roll +
                " vs " + resolution.Assessment.SuccessRate +
                "\nDebt +" + resolution.DebtAdded +
                " Fatigue +" + resolution.FatigueAdded +
                " Alert +" + resolution.AlertAdded +
                "\n" + resolution.Summary;
        }

        public void ShowMessage(string message)
        {
            if (resultText != null)
            {
                resultText.text = message;
            }
        }

        public void Close()
        {
            if (root != null)
            {
                root.SetActive(false);
            }
        }

        private void ChooseSkill(SkillData skill)
        {
            if (onSkillChosen != null)
            {
                onSkillChosen.Invoke(skill);
            }
        }

        private void ClearButtons()
        {
            if (buttonContainer == null)
            {
                return;
            }

            for (int i = buttonContainer.childCount - 1; i >= 0; i--)
            {
                Destroy(buttonContainer.GetChild(i).gameObject);
            }
        }
    }
}
