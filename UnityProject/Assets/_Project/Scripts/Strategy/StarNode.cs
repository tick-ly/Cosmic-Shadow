using System.Collections.Generic;
using UnityEngine;

using ShadowOfTheUniverse.Core;

namespace ShadowOfTheUniverse.Strategy
{
    public class StarNode : MonoBehaviour
    {
        public string mapNodeId;
        public string nodeName;
        public int dangerLevel;
        public TerrainType terrainType;
        public NodeVisibility visibility = NodeVisibility.Hidden;
        
        public List<StarNode> connectedNodes = new List<StarNode>();

        // 视觉反馈组件
        private SpriteRenderer spriteRenderer;
        private Color originalColor;

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
        }

        public void Initialize(string name, TerrainType type, string boundNodeId = null)
        {
            mapNodeId = boundNodeId;
            nodeName = name;
            terrainType = type;
            
            // 根据地形设置初始颜色
            if (spriteRenderer != null)
            {
                switch (type)
                {
                    case TerrainType.Land: originalColor = new Color(0.4f, 0.8f, 0.4f); break; // 绿色
                    case TerrainType.Sea: originalColor = new Color(0.2f, 0.4f, 0.8f); break;  // 蓝色
                    case TerrainType.Coastal: originalColor = new Color(0.8f, 0.8f, 0.4f); break; // 黄色
                }
                UpdateVisibilityVisuals();
            }
        }

        // 更新视野表现
        public void SetVisibility(NodeVisibility newVisibility)
        {
            visibility = newVisibility;
            UpdateVisibilityVisuals();
        }

        private void UpdateVisibilityVisuals()
        {
            if (spriteRenderer == null) return;

            switch (visibility)
            {
                case NodeVisibility.Hidden:
                    spriteRenderer.color = Color.black; // 完全不可见
                    break;
                case NodeVisibility.Fogged:
                    spriteRenderer.color = originalColor * 0.5f; // 变暗（战争迷雾）
                    break;
                case NodeVisibility.Visible:
                    spriteRenderer.color = originalColor; // 正常显示
                    break;
            }
        }

        // 供玩家交互时高亮显示
        public void Highlight(bool isHighlighted)
        {
            if (spriteRenderer != null && visibility != NodeVisibility.Hidden)
            {
                spriteRenderer.color = isHighlighted ? Color.white : (visibility == NodeVisibility.Visible ? originalColor : originalColor * 0.5f);
            }
        }

        // 检查是否与目标节点相连
        public bool IsConnectedTo(StarNode target)
        {
            return connectedNodes.Contains(target);
        }
    }
}
