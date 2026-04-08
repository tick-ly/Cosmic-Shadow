# Pygame → Unity C# 迁移方案：宇宙之影

## Context

现有项目 `game_project/` 是 Python + pygame 实现，核心系统（状态机、事件、战斗、数据模型）已完整。需要将其架构完整翻译为 Unity C#，同时保留 Python 版作为参考和持续开发分支。

---

## 一、核心架构映射

| Python/pygame | Unity C# | 说明 |
|---|---|---|
| `Game.run()` 主循环 | `MonoBehaviour.Update()` | Unity 自带帧循环，无需手动 `pygame.display.flip()` |
| `StateManager` | `GameStateMachine : MonoBehaviour` | 状态切换改用 Scene 加载或 `StateBase` 组件 |
| `BaseState` | `StateBase : MonoBehaviour` | 含 `OnEnter()`, `OnExit()`, `Update()` |
| `EventSystem` (pub/sub) | `EventManager : Singleton` + C# `event`/`Action` | 用 `Dictionary<Type, List<Action<IEvent>>>` |
| `pygame.Rect` + 手动绘制 | `RectTransform` + `Image`/`TextMeshPro` | UGUI 自动处理缩放和布局 |
| `@dataclass` 数据结构 | C# `class` + `ScriptableObject` | 参考数据用 SO，运行时实例用普通类 |
| `List[T]` / `Dict[K,V]` | `List<T>` / `Dictionary<K,V>` | 语法几乎一致 |
| `pygame.font` | `TextMeshPro` (TMP) | 中文字体支持更好 |
| `SimplexNoise` (手写) | `FastNoiseLite` (NuGet) 或 `Mathf.PerlinNoise` | Unity 版性能更好 |
| `threading` | `Coroutine` / `async-await` | Unity 原生异步 |
| `pygame.draw.*` | `LineRenderer`, `SpriteRenderer`, Mesh API | 2D 用 UGUI，3D 用 Mesh |

---

## 二、数据层翻译（Data → ScriptableObject）

### 策略：分层建模

```
配置数据（只读）  → ScriptableObject 资产（CreateAssetMenu）
运行时数据（可变） → 普通 C# class，引用 SO 作为模板
```

### 核心 SO 类型对照

| Python 数据类 | Unity SO 类 | 资产文件 |
|---|---|---|
| `SkillData` | `SkillDataSO : ScriptableObject` | `Assets/Data/Skills/*.asset` |
| `CharacterClassSO` | `CharacterClassSO : ScriptableObject` | `Assets/Data/Classes/*.asset` |
| `CombatUnitDataSO` | `CombatUnitDataSO : ScriptableObject` | `Assets/Data/Units/*.asset` |
| `StarNode` | `NodeDataSO : ScriptableObject` | `Assets/Data/Map/Nodes/*.asset` |
| `TerrainTile` | `TerrainDataSO : ScriptableObject` | `Assets/Data/Terrain/*.asset` |
| `ModernWeapon` | `WeaponSO : ScriptableObject` | `Assets/Data/Weapons/*.asset` |
| `Operator` | `OperatorDataSO : ScriptableObject` | `Assets/Data/Operators/*.asset` |
| 配置常量 | `GameConfigSO : ScriptableObject` | 单例资源 |

### SO 示例结构

```csharp
// SkillDataSO.cs
[CreateAssetMenu(fileName = "NewSkill", menuName = "Game/Skill")]
public class SkillDataSO : ScriptableObject
{
    public string skillId;
    public string skillName;
    public string description;
    public SkillType skillType;
    public SkillTarget target;
    public int power;
    public int range;
    public int cooldown;
    public CompromiseDimension compromiseDimension;
    public RealityDebtCost debtCost;
    [Range(0f, 1f)] public float backlashRisk;
}

// 运行时实例（不含 [CreateAssetMenu]）
[System.Serializable]
public class SkillInstance
{
    public SkillDataSO Template;
    public int CurrentCooldown;

    public bool CanUse(int currentDebt) =>
        CurrentCooldown == 0 &&
        Template.debtCost.MinCost + currentDebt <= GameConfig.MaxRealityDebt;

    public void Use() => CurrentCooldown = Template.cooldown;
}
```

---

## 三、核心系统翻译

### 3.1 游戏管理器 (GameManager)

```csharp
// GameManager.cs
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    [Header("Core Systems")]
    public GameStateMachine StateMachine;
    public EventManager EventManager;
    public UIManager UI;

    [Header("Game Data")]
    public GameConfigSO Config;
    public List<StarNode> AllNodes = new();
    public Fleet PlayerFleet;
    public Fleet EnemyFleet;

    void Awake()
    {
        if (Instance != null) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);

        StateMachine = GetComponent<GameStateMachine>();
        EventManager = GetComponent<EventManager>();
        UI = GetComponent<UIManager>();
    }

    void Update()
    {
        StateMachine.CurrentState?.OnUpdate(Time.deltaTime);
    }
}
```

### 3.2 状态机 (GameStateMachine)

方案 A（推荐）：Scene 切换模式

```csharp
// StateBase.cs
public abstract class StateBase : MonoBehaviour
{
    public virtual void OnEnter() { }
    public virtual void OnExit() { }
    public virtual void OnUpdate(float dt) { }
    public virtual void OnHandleEvent(Event e) { }
}

// GameStateMachine.cs
public class GameStateMachine : MonoBehaviour
{
    public StateBase CurrentState { get; private set; }
    private readonly Queue<StateBase> _history = new();  // FIFO：返回上一状态

    // 方案A：Scene 切换
    public void ChangeScene(string sceneName)
    {
        CurrentState?.OnExit();
        CurrentState = null;
        UnityEngine.SceneManagement.SceneManager.LoadScene(sceneName);
    }

    // 方案B：同Scene状态切换（Prefab Instantiate）
    public void ChangeState<T>() where T : StateBase
    {
        CurrentState?.OnExit();
        Destroy(CurrentState?.gameObject);

        var prefab = Resources.Load<T>($"States/{typeof(T).Name}");
        var instance = Instantiate(prefab, transform);
        CurrentState = instance;
        CurrentState.OnEnter();
    }
}
```

> 注：两种方案不要混用。推荐**方案 A**（Scene 切换），因为 Unity 原生支持场景隔离、内存清理更干净。

### 3.3 事件系统 (EventManager)

```csharp
// GameEvents.cs
public static class GameEvents
{
    public static readonly EventBus<UnitDamagedEvent> UnitDamaged = new();
    public static readonly EventBus<SkillUsedEvent> SkillUsed = new();
    public static readonly EventBus<BattleStartEvent> BattleStart = new();
    public static readonly EventBus<NodeSelectedEvent> NodeSelected = new();
}

// EventBus.cs
public class EventBus<T> where T : IEventData
{
    private readonly List<Action<T>> _listeners = new();

    public void Subscribe(Action<T> callback) => _listeners.Add(callback);
    public void Unsubscribe(Action<T> callback) => _listeners.Remove(callback);
    public void Emit(T data) { foreach (var l in _listeners) l(data); }
}

// IEventData.cs
public interface IEventData { }

// 事件数据类示例
public struct UnitDamagedEvent : IEventData
{
    public WarfareUnit Unit;
    public int Damage;
}

public struct NodeSelectedEvent : IEventData
{
    public StarNode Node;
}
```

使用示例：
```csharp
// 发送事件
GameEvents.UnitDamaged.Emit(new UnitDamagedEvent { Unit = unit, Damage = dmg });

// 接收事件
void OnEnable() => GameEvents.UnitDamaged.Subscribe(OnUnitDamaged);
void OnDisable() => GameEvents.UnitDamaged.Unsubscribe(OnUnitDamaged);
void OnUnitDamaged(UnitDamagedEvent e) => Debug.Log($"{e.Unit.name} 受到 {e.Damage} 伤害");
```

### 3.4 UI 系统

放弃 pygame 手动绘制，改用 Unity UGUI：

| pygame 组件 | Unity 组件 | 迁移说明 |
|---|---|---|
| `Widget` | `MonoBehaviour` | 基类含 RectTransform |
| `Button` | `Button` (UGUI) + `EventTrigger` | OnClick 直接绑定回调 |
| `Panel` | `Panel : MonoBehaviour` | 含子 UI 元素引用 |
| `ProgressBar` | 自定义组件 + `Image.fillAmount` | 脚本控制 fill |
| `TextDisplay` | `TextMeshProUGUI` | 中文字体直接支持 |

```csharp
// HUDManager.cs（替换 strategy_map_state 的 HUD 逻辑）
public class HUDManager : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI debtText;
    [SerializeField] private TextMeshProUGUI resourceText;
    [SerializeField] private Image debtBar;
    [SerializeField] private Button menuButton;

    void Start()
    {
        menuButton.onClick.AddListener(OnReturnToMenu);
        GameEvents.NodeSelected.Subscribe(OnNodeSelected);
    }

    public void UpdateHUD(int debt, int maxDebt, int resources)
    {
        debtText.text = $"现实债务: {debt}/{maxDebt}";
        debtBar.fillAmount = (float)debt / maxDebt;
        resourceText.text = $"资源: {resources}";
    }

    void OnReturnToMenu()
    {
        GameEvents.RequestSceneChange.Emit(new SceneChangeEvent { SceneName = "MainMenu" });
    }
}
```

---

## 四、战斗系统翻译（map_combat + modern_warfare_system）

采用接口 + 实现类：

```csharp
// IWeapon.cs
public interface IWeapon
{
    string Name { get; }
    int Damage { get; }
    int Accuracy { get; }
    float ApplyDamage(WarfareUnit target, IWeaponTargetContext ctx);
}

// BallisticWeaponSO.cs
[CreateAssetMenu]
public class BallisticWeaponSO : WeaponDataSO, IWeapon
{
    public float ProjectileSpeed;
    public float FalloffStart;
    public float FalloffRate;

    public float ApplyDamage(WarfareUnit target, IWeaponTargetContext ctx)
    {
        float dist = ctx.GetDistance(target);
        float falloff = dist > FalloffStart
            ? 1f - (dist - FalloffStart) * FalloffRate
            : 1f;
        return Damage * falloff * ctx.GetHitRoll(target);
    }
}

// WarfareUnit.cs
public class WarfareUnit : MonoBehaviour
{
    [Header("Data")]
    public WarfareUnitDataSO Template;
    public OperatorDataSO OperatorData;  // 注：避免用 operator 做字段名

    [Header("Runtime")]
    public int Health;
    public int Energy;
    public int RealityDebt;
    public List<IWeapon> Weapons = new();

    public float Evasion => Template.BaseEvasion + (Agility - 10) * 2;
    public bool IsAlive => Health > 0;

    public void TakeDamage(float dmg)
    {
        float actual = Mathf.Max(1, dmg - Defense / 2f);
        Health = Mathf.Max(0, Health - (int)actual);
        GameEvents.UnitDamaged.Emit(new UnitDamagedEvent { Unit = this, Damage = (int)actual });
    }
}
```

### 现实债务系统（核心特色，必须保留）

```csharp
// RealityDebtSystem.cs
public class RealityDebtSystem
{
    public List<string> CalculateConsequences(int debt)
    {
        var consequences = new List<string>();
        if (debt > 200)  consequences.Add("能力效率 -10%");
        if (debt > 400)  consequences.Add("随机失灵风险 +15%");
        if (debt > 600)  consequences.Add("视野扭曲");
        if (debt > 800)  consequences.Add("现实崩塌临界警告");
        return consequences;
    }

    public float GetAbilityMultiplier(int debt) =>
        1f - (debt / 1000f) * 0.5f;  // 债务越高，能力越弱

    public float GetDebtMultiplier(int debt) =>
        1f + (debt / 1000f) * 0.3f;  // 债务越高，代价越大
}
```

---

## 五、战略地图翻译（strategy_map_state）

### 节点系统

```csharp
// Owner.cs（替换字符串，避免拼写错误）
public enum Owner { Neutral, Player, Enemy }

// StarNode.cs
public class StarNode : MonoBehaviour, IPointerClickHandler
{
    public string NodeId;
    public string NodeName;
    public NodeType NodeType;
    public Vector2 MapPosition;

    [Header("Runtime")]
    public int RealityDebt;
    public DebtLevel DebtLevel;
    public Owner Owner;  // 用枚举替代字符串
    public List<string> Connections = new();

    [Header("References")]
    public SpriteRenderer NodeRenderer;
    public LineRenderer[] ConnectionLines;

    public Color GetNodeColor() => DebtLevel switch
    {
        DebtLevel.SAFE     => new Color(0.3f, 0.69f, 0.31f),   // #4CAF50
        DebtLevel.MODERATE => new Color(1.0f, 0.76f, 0.03f),   // #FFC107
        DebtLevel.HIGH     => new Color(1.0f, 0.6f, 0f),        // #FF9800
        DebtLevel.CRITICAL=> new Color(0.96f, 0.26f, 0.21f),   // #F44336
        DebtLevel.DEAD_ZONE=> new Color(0.12f, 0.12f, 0.16f),  // #1F1F29
        _                  => Color.white
    };

    void Update()
    {
        NodeRenderer.color = GetNodeColor();
    }

    public void OnPointerClick(PointerEventData eventData)
    {
        GameEvents.NodeSelected.Emit(new NodeSelectedEvent { Node = this });
    }
}
```

### 地图生成

```csharp
// StarMapGenerator.cs
public class StarMapGenerator : MonoBehaviour
{
    public StarNode NodePrefab;
    public Transform MapRoot;

    public List<StarNode> GenerateMap(List<NodeDataSO> templates)
    {
        var nodes = new List<StarNode>();
        foreach (var tmpl in templates)
        {
            var node = Instantiate(NodePrefab, MapRoot);
            node.NodeId = tmpl.NodeId;
            node.NodeName = tmpl.NodeName;
            node.MapPosition = tmpl.MapPosition;
            node.Connections = new List<string>(tmpl.Connections);
            nodes.Add(node);
        }
        // 绘制连接线
        foreach (var n in nodes)
            DrawConnections(n, nodes);
        return nodes;
    }

    private void DrawConnections(StarNode node, List<StarNode> allNodes)
    {
        var drawn = new HashSet<string>();
        foreach (var connId in node.Connections)
        {
            var edgeKey = string.Compare(node.NodeId, connId, StringComparison.Ordinal) < 0
                ? $"{node.NodeId}-{connId}"
                : $"{connId}-{node.NodeId}";

            if (drawn.Contains(edgeKey)) continue;
            drawn.Add(edgeKey);

            var conn = allNodes.FirstOrDefault(n => n.NodeId == connId);
            if (conn == null) continue;

            var lr = node.gameObject.AddComponent<LineRenderer>();
            lr.positionCount = 2;
            lr.SetPosition(0, node.MapPosition);
            lr.SetPosition(1, conn.MapPosition);
            lr.startColor = node.Owner == conn.Owner
                ? new Color(0.2f, 0.2f, 0.31f)
                : new Color(0.31f, 0.16f, 0.16f);
            lr.endColor = lr.startColor;
            lr.lineWidth = 2f;
        }
    }
}
```

---

## 六、Unity 项目目录结构

```
Assets/
├── Scripts/
│   ├── Core/
│   │   ├── GameManager.cs
│   │   ├── GameStateMachine.cs
│   │   ├── StateBase.cs
│   │   ├── EventManager.cs
│   │   └── EventBus.cs
│   ├── Data/
│   │   ├── Config/
│   │   │   ├── GameConfigSO.cs
│   │   │   └── GameColors.cs
│   │   ├── Skills/
│   │   │   ├── SkillDataSO.cs
│   │   │   ├── SkillInstance.cs
│   │   │   └── SkillFactory.cs
│   │   ├── Units/
│   │   │   ├── CombatUnitDataSO.cs
│   │   │   ├── WarfareUnit.cs
│   │   │   └── Fleet.cs
│   │   ├── Characters/
│   │   │   ├── CharacterClassSO.cs
│   │   │   └── StatModifier.cs
│   │   ├── Weapons/
│   │   │   ├── WeaponDataSO.cs
│   │   │   ├── BallisticWeaponSO.cs
│   │   │   ├── CruiseWeaponSO.cs
│   │   │   └── EnergyWeaponSO.cs
│   │   ├── Operators/
│   │   │   ├── OperatorDataSO.cs
│   │   │   ├── PredictionAbility.cs
│   │   │   ├── SpatialAbility.cs
│   │   │   └── EvolutionProgress.cs
│   │   └── Map/
│   │       ├── NodeDataSO.cs
│   │       └── StarMapGenerator.cs
│   ├── Combat/
│   │   ├── CombatSystem.cs
│   │   ├── RealityDebtSystem.cs
│   │   ├── TerrainSystem.cs
│   │   ├── EnhancedCombatUnit.cs
│   │   └── AI/
│   │       ├── EnemyAI.cs
│   │       └── TacticalAI.cs
│   ├── States/
│   │   ├── MenuState.cs
│   │   ├── StrategyMapState.cs
│   │   └── BattleState.cs
│   ├── UI/
│   │   ├── UIManager.cs
│   │   ├── HUDManager.cs
│   │   ├── NodeInfoPanel.cs
│   │   └── Components/
│   │       ├── SkillButton.cs
│   │       └── UnitStatusBar.cs
│   └── Persistence/
│       └── SaveLoadSystem.cs      ← 新增：存档系统
├── Prefabs/
│   ├── UI/
│   ├── Map/
│   └── Units/
├── ScriptableObjects/
│   └── (所有 .asset 文件)
├── Scenes/
│   ├── MainMenu.scene
│   ├── StrategyMap.scene
│   └── Battle.scene
├── TextMesh Pro/
│   └── Fonts/
│       └── ChineseFont.ttf        ← 微软雅黑
├── ThirdParty/
│   └── FastNoiseLite/
└── Editor/                       ← 新增：编辑器工具
    └── SOGeneratorMenu.cs
```

---

## 七、迁移阶段（4 阶段）

### 阶段 1：项目骨架（1 周）
- [ ] 创建 Unity 项目（Unity 2022 LTS+），安装 TextMeshPro
- [ ] 实现 `GameManager` 单例（DontDestroyOnLoad）
- [ ] 实现 `EventBus<T>` + `GameEvents` 静态类
- [ ] 实现 `GameStateMachine`（Scene 切换方案）
- [ ] 迁移 `config.py` → `GameConfigSO.asset`
- [ ] 搭建 3 个场景：`MainMenu`、`StrategyMap`、`Battle`
- [ ] 配置 TextMeshPro 中文字体（微软雅黑）

### 阶段 2：数据层 + 菜单（1.5 周）
- [ ] 实现所有 SO 类型（Skill, Class, Unit, Node, Weapon, Operator）
- [ ] 编写编辑器菜单工具 `SOGeneratorMenu`：一键从 JSON 生成 50+ SO 资产
- [ ] 实现 `MenuState`：Canvas + TextMeshPro + Button，切换到 StrategyMap
- [ ] **双版本并行**：Python 版作为数据规范，Unity SO 资产值对标

### 阶段 3：战略地图（1.5 周）
- [ ] 实现 `StarNode` 组件 + `LineRenderer` 连接线
- [ ] 实现点击检测（`IPointerClickHandler`）
- [ ] 实现 `StarMapGenerator` 从 SO 生成地图
- [ ] 实现 HUD（现实债务条、资源、妥协点数）
- [ ] 实现 `NodeInfoPanel`：显示节点详情
- [ ] 实现舰队标记 + 移动到相邻节点逻辑
- [ ] 实现敌方简单 AI 回合（向玩家方向移动）

### 阶段 4：战斗系统（2 周）
- [ ] 实现 `WarfareUnit` + `WeaponDataSO` 系列（Ballistic / Cruise / Energy）
- [ ] 实现物理妥协能力系统（重力/时空/因果）
- [ ] 实现预测能力 + 空间操控能力
- [ ] 实现阶段进化系统（基础→魔→神）
- [ ] 实现 `BattleState`：战场切换、回合循环
- [ ] 实现 `RealityDebtSystem`：后果显示、扭曲视觉效果
- [ ] 实现 `EnemyAI`：敌军决策逻辑

### 阶段 5：持久化（0.5 周，补充）
- [ ] 实现 `SaveLoadSystem`：JSON 序列化 GameState
- [ ] 实现存档/读档 UI
- [ ] 实现游戏循环闭环：开始→游玩→存档→退出

---

## 八、关键技术决策

### 决策 1：状态管理方式

| 方案 | 优点 | 缺点 |
|---|---|---|
| **A. Scene 切换（推荐）** | Unity 原生，场景隔离，内存自动清理 | 跨场景数据需 DontDestroy |
| B. Prefab Instantiate | 热更新友好，内存可控 | 需手动清理，需 Resources/Addressables |

**推荐方案 A**：Menu / StrategyMap / Battle 各用独立 Scene，通过 `SceneManager.LoadScene()` 切换。数据放 `GameManager`（DontDestroyOnLoad）。

### 决策 2：UI 框架选择

| 方案 | 优点 | 缺点 |
|---|---|---|
| **A. UGUI + TextMeshPro（推荐）** | 成熟、文档多、与 Unity 深度集成 | 布局需编辑器配置 |
| B. UI Toolkit | 代码驱动，StyleSheet | 学习曲线，2019+ 才有 |

### 决策 3：寻路

- 战略地图（节点网络）：手动 A* 在 `StarNode` 连接图上实现
- 战场地图（网格）：使用 `NavMesh` 或 `A* Pathfinding Project` 插件

### 决策 4：中文支持

1. 将 `C:\Windows\Fonts\msyh.ttc`（微软雅黑）复制到 `Assets/TextMesh Pro/Fonts/`
2. Unity 菜单：`Window → TextMeshPro → Font Asset Creator`，Source Font File 指向该文件，生成 `.asset`
3. 将生成的 TMP Font Asset 设为默认字体（或按需指定）

### 决策 5：owner 字段

**用枚举替代字符串**，避免运行时拼写错误无提示：

```csharp
public enum Owner { Neutral, Player, Enemy }
public Owner Owner { get; set; }  // 而非 public string Owner
```

---

## 九、AI 系统设计（补充）

### 敌军 AI（EnemyAI）

```csharp
public class EnemyAI : MonoBehaviour
{
    public void ExecuteTurn(Fleet enemyFleet, List<StarNode> allNodes, Fleet playerFleet)
    {
        var currentNode = allNodes.FirstOrDefault(n => n.NodeId == enemyFleet.CurrentNodeId);
        if (currentNode == null) return;

        // 简单策略：向玩家方向移动
        var playerNode = allNodes.FirstOrDefault(n => n.NodeId == playerFleet.CurrentNodeId);
        if (playerNode == null) return;

        StarNode bestTarget = null;
        float bestScore = float.MinValue;

        foreach (var connId in currentNode.Connections)
        {
            var conn = allNodes.FirstOrDefault(n => n.NodeId == connId);
            if (conn == null || !conn.IsPassable()) continue;

            float score = 0;
            // 向玩家靠近 +1 分
            score -= Vector2.Distance(conn.MapPosition, playerNode.MapPosition);
            // 高债务节点 -0.5 分
            score -= conn.RealityDebt * 0.005f;
            // 有驻军 -0.3 分
            score -= conn.GarrisonStrength * 0.003f;

            if (score > bestScore) { bestScore = score; bestTarget = conn; }
        }

        if (bestTarget != null)
        {
            enemyFleet.MoveTo(bestTarget.NodeId);
            Debug.Log($"[敌方移动] {enemyFleet.Name} -> {bestTarget.NodeName}");
        }
    }
}
```

### 战术 AI（Battle AI，待扩展）

```csharp
public class TacticalAI
{
    // 根据战场地形、敌方站位、自身能力选择最优技能
    public SkillDataSO SelectBestSkill(WarfareUnit self, List<WarfareUnit> enemies, List<WarfareUnit> allies)
    {
        // 简单实现：优先使用冷却好、伤害高的技能
        // 扩展：可用 Monte Carlo Tree Search 或评分函数
        return self.Skills
            .Where(s => s.CurrentCooldown == 0)
            .OrderByDescending(s => s.Template.Power)
            .FirstOrDefault()?.Template;
    }
}
```

---

## 十、编辑器工具设计（补充）

手动创建 50+ SO 资产不现实，编写 Unity 菜单项从 JSON 自动生成：

```csharp
// Editor/SOGeneratorMenu.cs
public static class SOGeneratorMenu
{
    [MenuItem("Game/生成所有技能SO资产")]
    public static void GenerateAllSkillAssets()
    {
        var skills = JsonUtility.FromJson<SkillDataList>(
            Resources.Load<TextAsset>("Data/skills.json").text);

        foreach (var skill in skills.items)
        {
            var so = ScriptableObject.CreateInstance<SkillDataSO>();
            so.skillId = skill.id;
            so.skillName = skill.name;
            so.power = skill.power;
            // ... 映射其他字段

            AssetDatabase.CreateAsset(so,
                $"Assets/ScriptableObjects/Skills/{skill.id}.asset");
        }
        AssetDatabase.SaveAssets();
    }
}
```

对应 JSON 数据文件存于 `Resources/Data/`，由 Python 版 `data/` 模块导出生成。

---

## 十一、双版本并行策略

迁移期间 Python 版和 Unity 版**并行维护**：

```
demo/
├── game_project/           ← Python 版（当前可运行）
│   ├── data/              ← 数据规范（JSON export）
│   └── ...
│
└── game_unity/            ← Unity 项目（迁移目标，新建）
    ├── Assets/
    │   ├── Scripts/       ← C# 脚本
    │   ├── Resources/Data/ ← Python 导出的 JSON
    │   └── ...
    └── ProjectSettings/
```

每次 Unity 阶段完成后：
1. Python 版运行单元测试验证逻辑
2. Unity 版对应实现，数值对齐 Python 输出
3. 双版战斗结算数据一致性验证

---

## 十二、验证计划

每个阶段完成后执行：
1. **编译检查**：Unity Console 无 Error
2. **功能验证**：场景切换、节点点击、战斗结算
3. **数据对齐**：Python 和 Unity 输出相同战斗数值（随机种子固定）
4. **中文显示**：TextMeshPro 正确渲染所有中文文本
5. **存档测试**：Save → Quit → Load → 状态一致
