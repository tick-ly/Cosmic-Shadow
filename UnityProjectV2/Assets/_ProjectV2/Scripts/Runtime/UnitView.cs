using ShadowOfTheUniverse.V2.Core;
using UnityEngine;

namespace ShadowOfTheUniverse.V2.Runtime
{
    public sealed class UnitView : MonoBehaviour
    {
        private MissionRuntimeController controller;
        private UnitState unit;
        private Renderer cachedRenderer;

        public string UnitId
        {
            get { return unit != null ? unit.Id : string.Empty; }
        }

        public void Initialize(MissionRuntimeController owner, UnitState state)
        {
            controller = owner;
            unit = state;
            cachedRenderer = GetComponent<Renderer>();
            Refresh(false);
        }

        public void Refresh(bool selected)
        {
            if (cachedRenderer == null)
            {
                return;
            }

            cachedRenderer.material.color = selected ? Color.yellow : new Color(0.96f, 0.92f, 0.72f);
        }

        private void OnMouseDown()
        {
            if (controller != null)
            {
                controller.HandleUnitClicked(this);
            }
        }
    }
}
