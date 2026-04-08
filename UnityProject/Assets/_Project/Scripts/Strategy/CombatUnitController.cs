using UnityEngine;
using ShadowOfTheUniverse.Core;

namespace ShadowOfTheUniverse.Strategy
{
    /// <summary>
    /// 舰队/作战单位的 MonoBehaviour 组件，负责视觉表现和更新（符合 MVC 架构的 View/Controller 层）
    /// 适配新的 CombatUnitModel 和地形移动逻辑
    /// </summary>
    public class CombatUnitController : MonoBehaviour
    {
        public CombatUnitModel Model { get; private set; }

        // 视觉反馈组件
        private SpriteRenderer spriteRenderer;
        private Color originalColor;

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            if (spriteRenderer != null)
            {
                originalColor = spriteRenderer.color;
            }
        }

        // 初始化单位
        public void Initialize(CombatUnitModel model)
        {
            Model = model;
            
            // 设定不同类型单位的外观颜色
            if (spriteRenderer != null)
            {
                switch (Model.Domain)
                {
                    case UnitDomain.Land: originalColor = new Color(0.8f, 0.4f, 0.2f); break;
                    case UnitDomain.Sea:  originalColor = new Color(0.2f, 0.4f, 0.8f); break;
                    case UnitDomain.Air:  originalColor = new Color(0.8f, 0.8f, 0.8f); break;
                }
                
                if (Model.Scale == UnitScale.Individual)
                {
                    // 单兵使用不同颜色或者明度区分
                    originalColor = Color.Lerp(originalColor, Color.white, 0.5f);
                }
                
                spriteRenderer.color = originalColor;
            }

            if (Model.CurrentNode != null)
            {
                transform.position = Model.CurrentNode.transform.position;
            }
        }

        private void Update()
        {
            if (Model == null) return;

            // 处理移动逻辑
            if (Model.State == UnitState.Moving && Model.TargetNode != null)
            {
                Vector3 targetPos = Model.TargetNode.transform.position;
                
                // 移动插值
                transform.position = Vector3.MoveTowards(
                    transform.position, 
                    targetPos, 
                    Model.MovementSpeed * Time.deltaTime
                );

                // 检查是否到达
                if (Vector3.Distance(transform.position, targetPos) < 0.01f)
                {
                    Model.OnArrival();
                    Debug.Log($"{Model.UnitName} 抵达了 {Model.CurrentNode.nodeName}");
                }
            }
        }

        // 供玩家交互时高亮显示
        public void Highlight(bool isHighlighted)
        {
            if (spriteRenderer != null)
            {
                spriteRenderer.color = isHighlighted ? Color.white : originalColor;
            }
        }
    }
}
