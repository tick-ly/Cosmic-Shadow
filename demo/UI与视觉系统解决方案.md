# 宇宙之影：UI与视觉系统解决方案

## 一、 视觉基调：秩序与崩塌的对立 (Order vs. Collapse)

《宇宙之影》的核心冲突在于“常规物理规则”与“物理妥协/现实债务”之间的矛盾。因此，整体视觉与 UI 风格应采用**“对立美学”**：

*   **常规状态（秩序）：** 极简的科幻冷色调（深蓝、幽绿、银白）。UI 边缘锐利，字体清晰，类似全息投影（Hologram）和军用控制台（HUD）。
*   **高债务状态（崩塌）：** 当现实债务积累或玩家使用“物理妥协”时，画面和 UI 必须出现**“故障艺术 (Glitch Art)”**。颜色向暖色调或极端的紫色/猩红偏移，UI 边缘产生色差（Chromatic Aberration）、像素撕裂和噪点。

## 二、 宏观层：大战略沙盘视觉 (Grand Strategy Sandbox)

在沙盘模式下，玩家是战场指挥官，视觉核心在于“信息的清晰传达”与“局势的动态反馈”。

### 1. 节点与地图表现
*   **节点 (Nodes)：** 放弃写实的星球/城市模型，采用**抽象的几何发光体**。
    *   *安全节点：* 稳定的蓝色光环。
    *   *交战节点：* 闪烁的橙色/红色脉冲。
    *   *死区 (Dead Zone)：* 黑色空洞，周围伴随紫色的空间扭曲特效（Shader: 局部黑洞/引力透镜效果）。
*   **连线 (Connections)：** 使用 `LineRenderer` 绘制。连线的流动速度代表部队的移动，当连接到“死区”时，连线会变得扭曲、断断续续。
*   **战争迷雾 (Fog of War)：** 采用“全息数据遮罩”而非传统的黑云。未探索区域显示为布满代码乱码或六边形网格的灰色区域。

### 2. 沙盘 UI 布局 (UI Layout)
*   **顶部栏 (Top Bar)：** 全局资源监控（建材、能源、异星物质、妥协点数池）。
*   **左侧面板 (Left Panel - 动态与战报)：** 滚动显示敌军动向、动态事件提醒、报告式战斗的实时击杀数字。
*   **右侧面板 (Right Panel - 详情器)：** 当选中节点或单位时滑出，显示当前局部的“现实债务浓度”、地形属性（海/陆/空）以及驻扎小队信息。
*   **底部动作栏 (Bottom Bar)：** 指挥官视角的“物理妥协”技能按钮（如：轨道轰炸、局部现实重置）。

## 三、 微观层：FPS即时战术视觉 (Tactical FPS)

进入 5 分钟快节奏战斗后，UI 必须**极简 (Minimalist)**，将屏幕空间还给激烈的战斗，沉浸感优先。

### 1. 战斗 HUD (Heads Up Display)
*   **动态准星 (Dynamic Crosshair)：** 根据武器类型和后坐力实时收缩/扩散。
*   **环形状态条 (Diegetic UI)：** 尽量将血量和弹药集成到玩家角色的模型上（类似《死亡空间》），或者在准星周围用极细的半透明环形条表示，避免视线偏离屏幕中心。
*   **妥协点数槽 (Compromise Meter)：** 屏幕底部的能量条，满载时发出危险的高光。

### 2. “物理妥协”视觉特效 (VFX)
*   微观模式下，玩家的超能力必须有强烈的视觉冲击。
*   **释放技能瞬间：** 屏幕发生强烈的镜头畸变 (Lens Distortion) 和色散。
*   **高现实债务反馈：** 如果玩家在同一区域过度使用技能，该区域的空气会变得“粘稠”，屏幕边缘常驻红色/紫色的警示噪点，提示玩家现实正在崩塌。

## 四、 架构设计与数据结构模板 (C# / Unity)

为了应对未来可能的修改和迭代，UI 系统必须与游戏核心逻辑（Model）解耦。推荐使用 MVC/MVP 模式。

### 1. UI 管理器基类
建议为所有的 UI 面板定义一个统一的接口，方便通过脚本动态控制它们的滑入/滑出和数据绑定。

```csharp
using UnityEngine;

namespace ShadowOfTheUniverse.UI
{
    // 所有 UI 面板（如右侧节点详情、左侧战报）都要实现此接口
    public interface IUIView
    {
        void Show();
        void Hide();
        void UpdateData(object data); // 传入 ScriptableObject 或 Model
    }

    // 视觉特效数据配置（方便美术和策划直接在 Inspector 中调整表现）
    [CreateAssetMenu(fileName = "VisualThemeSO", menuName = "Shadow/UI/Visual Theme")]
    public class VisualThemeSO : ScriptableObject
    {
        [Header("常规秩序状态")]
        public Color safeNodeColor = Color.cyan;
        public Color normalUIThemeColor = new Color(0, 0.8f, 1f, 0.8f);

        [Header("现实债务崩塌状态")]
        public Color deadZoneColor = Color.black;
        public Color dangerUIThemeColor = Color.red;
        
        [Range(0f, 1f)]
        public float glitchIntensityThreshold = 0.7f; // 债务达到70%开始出现UI故障
    }
}
```

### 2. 故障艺术特效 (Post-Processing)
强烈建议使用 Unity 的 **Post-Processing Stack v2** 或 **URP/HDRP Volume** 系统。
策划可以通过代码动态修改 Volume 中的 `Chromatic Aberration` (色差)、`Lens Distortion` (镜头畸变) 和 `Film Grain` (胶片噪点) 的权重，来完美呈现“现实债务”的浓度。
