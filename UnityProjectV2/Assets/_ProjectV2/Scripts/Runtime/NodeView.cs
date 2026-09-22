using ShadowOfTheUniverse.V2.Core;
using UnityEngine;

namespace ShadowOfTheUniverse.V2.Runtime
{
    public sealed class NodeView : MonoBehaviour
    {
        private MissionRuntimeController controller;
        private NodeDefinition node;
        private Renderer cachedRenderer;
        private Color baseColor;

        public string NodeId
        {
            get { return node != null ? node.Id : string.Empty; }
        }

        public void Initialize(MissionRuntimeController owner, NodeDefinition definition)
        {
            controller = owner;
            node = definition;
            cachedRenderer = GetComponent<Renderer>();
            baseColor = ResolveColor(definition);
            Refresh(false);
        }

        public void Refresh(bool selected)
        {
            if (cachedRenderer == null)
            {
                return;
            }

            cachedRenderer.material.color = selected ? Color.white : baseColor;
        }

        private void OnMouseDown()
        {
            if (controller != null)
            {
                controller.HandleNodeClicked(this);
            }
        }

        private static Color ResolveColor(NodeDefinition definition)
        {
            if (definition == null)
            {
                return Color.gray;
            }

            if (definition.Owner == NodeOwner.Enemy)
            {
                return new Color(0.85f, 0.2f, 0.18f);
            }

            if (definition.Owner == NodeOwner.Player)
            {
                return new Color(0.18f, 0.55f, 0.95f);
            }

            if (definition.Terrain == TerrainType.Sea)
            {
                return new Color(0.16f, 0.38f, 0.75f);
            }

            if (definition.Terrain == TerrainType.Coastal)
            {
                return new Color(0.75f, 0.68f, 0.3f);
            }

            return new Color(0.24f, 0.68f, 0.36f);
        }
    }
}
