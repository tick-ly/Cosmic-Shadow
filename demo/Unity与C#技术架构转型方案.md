# 《宇宙之影》Unity与C#技术架构转型方案 (V2 修订版)

为了确保团队从 Pygame (Python) 顺利过渡到 Unity (C#)，并为后续的开发奠定坚实的基础，特制定本技术架构与开发规范。本修订版已修复早期设计的状态管理缺陷，并补全了非功能性需求与 AI 系统设计。

**核心原则：全面拥抱 C#，采用数据驱动设计 (Data-Driven Design)，实现逻辑与表现的彻底解耦。**

---

## 一、 核心范式转换与代码规范 (Paradigm Shift & Standards)

### 1. 从“主循环”到“组件化”
*   **Pygame 时代：** 整个游戏是一个巨大的 `while True` 循环，程序员手动调用 `update()` 和 `draw()`。
*   **Unity 时代：** 游戏由场景 (Scene) 中的游戏物体 (GameObject) 组成。程序员编写 C# 脚本（继承自 `MonoBehaviour`）作为**组件 (Component)** 挂载到物体上。

### 2. 从“硬编码”到“数据驱动” (ScriptableObject)
*   **规范要求：** 所有的静态配置数据（如：战术任务参数、武器伤害）全部做成 `ScriptableObject` (SO) 资产。配置用 SO，运行时用普通 class 包装以防修改原始数据。

### 3. C# 避坑与代码规范 (P0 级修复)
*   **禁用保留关键字：** 绝对不要使用 C# 关键字作为变量名（如 `operator`）。
    ```csharp
    // ❌ 错误：operator 是关键字
    // public OperatorDataSO operator; 
    // ✅ 正确：使用大写或带前缀
    public OperatorDataSO Operator { get; set; } 
    ```
*   **严谨的数据结构语义：**
    ```csharp
    // ❌ 错误：如果需要先进先出 (FIFO) 的行为，不能用 Stack
    // private readonly Stack<StateBase> _history = new(); 
    // ✅ 正确：根据实际需求选择 Queue (FIFO) 或明确为撤销操作使用 Stack (LIFO)
    private readonly Queue<StateBase> _commandQueue = new(); 
    ```
*   **禁用魔法字符串 (Magic Strings)：** 凡是涉及状态、归属、阵营的标识，必须使用 `enum`，严禁使用字符串。
    ```csharp
    // ❌ 错误：极易拼写错误，IDE 无提示
    // public string owner = "player"; 
    // ✅ 正确：使用强类型枚举
    public enum Owner { Neutral, Player, Enemy }
    public Owner currentOwner = Owner.Player;
    ```

---

## 二、 场景与状态管理系统 (State Management)

之前混用了 Scene 切换和组件查找，现在明确《宇宙之影》的架构规范：**单一核心场景 + Prefab 实例化 (Single Core Scene + Prefab Instantiation)**。

### 1. 场景划分策略
放弃频繁的 `SceneManager.LoadScene`。游戏只包含两个主场景：
1.  **`MainMenuScene`：** 负责主菜单、设置、加载存档。
2.  **`CoreGameScene`：** 负责所有的游戏流程。
    *   **无缝切换方案：** 从“宏观沙盘”到“微观 FPS”，**不切换 Scene**。而是通过动态加载和卸载特定的 Prefab 环境，结合相机的 Zoom In/Out 实现无缝过渡。

### 2. 依赖注入与服务定位器 (Service Locator)
为了解决 `GetComponent<T>()` 找不到对象和跨系统调用的问题，引入轻量级的依赖注入方案（Service Locator）：
```csharp
public static class ServiceLocator
{
    private static readonly Dictionary<Type, object> _services = new();

    public static void Register<T>(T service) { _services[typeof(T)] = service; }
    public static T Get<T>() { return (T)_services[typeof(T)]; }
}

// 使用方式：
// 在 GameManager 的 Awake 中： ServiceLocator.Register<SaveLoadSystem>(new SaveLoadSystem());
// 在其他脚本中： var saveSys = ServiceLocator.Get<SaveLoadSystem>();
```

---

## 三、 非功能性需求补全 (Non-Functional Requirements)

### 1. 保存与加载系统 (Save/Load System)
*   **数据隔离：** 所有需要持久化的数据必须剥离出 MonoBehaviour，放入纯 C# 的 `GameStateData` 类中。
*   **序列化：** 使用 `Newtonsoft.Json` (通过 UPM 引入) 将 `GameStateData` 序列化为 JSON 文件，存储在 `Application.persistentDataPath`。

### 2. 编辑器工具 (Editor Tools)
为了避免策划手动创建成百上千个 SO 资产，必须开发自定义的 Editor 工具：
*   **批量生成：** 使用 `[ContextMenu]` 或自定义 `EditorWindow`，通过读取策划配置的 CSV 或 JSON 外部文件，一键批量生成对应的 `SkillDataSO`、`WeaponDataSO` 资产。

### 3. 包管理 (Package Management)
*   使用 **UPM (Unity Package Manager)** 管理第三方库。
*   **核心依赖：** `Newtonsoft Json` (序列化)、`Cinemachine` (镜头控制)、`Post Processing` (视觉特效)。

---

## 四、 核心 AI 系统设计 (AI Systems)

针对《宇宙之影》的硬核战斗，AI 系统分为三套独立的子系统：

1.  **宏观敌军指挥官 AI (Enemy Commander AI)：**
    *   **架构：** 基于**效用 AI (Utility AI)**。
    *   **逻辑：** 根据 `CommanderPersonaSO` 中定义的人设权重（如：进攻、防守、焦土倾向）和当前的“焦虑值”，对可用行动打分，选择最高分的战略行动（如调兵、呼叫增援）。
2.  **微观小队/单兵 AI (Tactical Unit AI)：**
    *   **架构：** 层次状态机 (HFSM) 或行为树 (Behavior Tree)。
    *   **逻辑：** 负责具体的 FPS 战斗行为（巡逻、掩蔽、射击、投掷手雷）。具备“视野锥”和“听觉范围”检测。
3.  **空间操控与预测 AI (Spatial & Predictive AI)：**
    *   **预测系统：** 配合玩家的“预算直觉”超能力。AI 需要在内存中超前模拟 3 秒钟的移动轨迹，并将其渲染为虚线投射在玩家屏幕上。
    *   **寻路系统：** 基于 A* 算法，不仅要避开常规障碍，还要动态避开高现实债务的“死区 (Dead Zone)”。

---

## 五、 时间估算与阶段划分 (修订版)

考虑到海量 SO 资产的制作和复杂 AI 系统的开发，时间估算已调整 (1.2x - 1.5x)：

*   **阶段一：底层骨架与核心重构 (约 1.5 周)**
    *   修复所有编译错误，搭建 Service Locator，实现单一核心场景切换方案。
*   **阶段二：数据驱动与编辑器工具 (约 2 周)**
    *   编写所有 SO 数据模板。开发批量生成 SO 的 Editor 工具。导入外部设定数据。
*   **阶段三：沙盘地图与宏观 AI (约 1.5 周)**
    *   实现 A* 寻路，沙盘节点连线可视化，接入宏观敌军指挥官效用 AI。
*   **阶段四：双轨制战斗与微观 AI (约 2.5 周)**
    *   实现 FPS 即时伤害判定、武器池。开发小队战术 AI 及轨迹预测 AI 系统。
*   **阶段五：闭环与打磨 (约 1 周)**
    *   接入 Save/Load 系统、主菜单 UI、以及 Post-Processing 故障艺术视觉特效。