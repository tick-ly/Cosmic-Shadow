# 宇宙之影 - Unity 项目初始化指南

> Phase 1 骨架完成。完成以下步骤即可运行基础框架。

---

## 步骤 0：Unity Hub 创建项目

1. 打开 **Unity Hub**
2. 点击 **New Project**
3. 选择模板：**3D**（或 **2D**，本游戏偏向 2D 俯视角，均可）
4. 项目名称：`ShadowOfTheUniverse`
5. 保存路径：`D:\program\univers\demo\game_unity`
6. Unity 版本：**2022.3 LTS** 或更高
7. 点击 **Create Project**

> 注意：选择 **2022.3 LTS** 或 **6000 LTS**，避免兼容性问题。

---

## 步骤 1：复制脚本文件

将 `Assets/Scripts/` 下的所有文件夹复制到 Unity 项目的 `Assets/` 目录下：

```
Assets/
├── Scripts/
│   ├── Core/          ← GameManager.cs, GameStateMachine.cs, ...
│   ├── Data/          ← GameConfigSO.cs, GameEnums.cs, ...
│   ├── States/        ← MenuState.cs, StrategyMapState.cs, ...
│   └── UI/            ← UIManager.cs
```

---

## 步骤 2：安装 TextMeshPro

1. Unity 菜单：**Window → Package Manager**
2. 左侧选择 **Unity Registry**
3. 搜索 **TextMeshPro**
4. 点击 **Install**（版本 3.x）

---

## 步骤 3：配置 TextMeshPro 中文字体

### 3.1 复制字体文件

```
复制  C:\Windows\Fonts\msyh.ttc  →  项目 Assets/TextMesh Pro/Fonts/
```

### 3.2 生成 TMP Font Asset

1. Unity 菜单：**Window → TextMeshPro → Font Asset Creator**
2. 设置：
   - **Source Font File**：选中上一步复制的 `msyh.ttc`
   - **Sampling Point Size**：根据需要设为 32 或 48
   - **Atlas Resolution**：建议 2048 × 2048
   - **Character Set**：选择 **Unicode Range (Hex)**，填入：`0020-007F, 4E00-9FFF`
     （覆盖基本 ASCII + 常用中文）
3. 点击 **Generate Font Asset**
4. 保存到 `Assets/TextMesh Pro/Fonts/ChineseFont.asset`

### 3.3 设为默认字体

1. **Edit → Project Settings → TextMeshPro Settings**
2. **Default Font Asset**：拖入上一步生成的 `ChineseFont.asset`

> 如果 `msyh.ttc` 不存在，尝试 `C:\Windows\Fonts\msyh.ttc`（微软雅黑）或 `simsun.ttc`（宋体）。

---

## 步骤 4：创建 GameConfigSO 资源

1. 在 `Assets/Resources/Config/` 目录下（**注意**：必须是 `Resources/Config/`）
2. 右键：**Create → Game → GameConfig**
3. Inspector 中可调整配置值（默认值已对齐 Python 版）
4. 拖入 **GameManager** Inspector 的 **Config** 槽位

---

## 步骤 5：创建 GameManager 对象

在 **任意一个场景**（推荐先在 MainMenu）中：

### 5.1 创建空对象

1. 场景中右键：**Create Empty** → 命名为 `GameManager`
2. 添加组件（**Add Component**）：
   - `GameManager`（自动挂载）
   - `GameStateMachine`（自动挂载）
   - `EventManager`（自动挂载）
   - `UIManager`（自动挂载）

### 5.2 挂载状态脚本（主菜单场景）

在 `GameManager` 下创建子对象 `MenuState`，挂载 `MenuState.cs` 组件。

### 5.3 拖入配置

将步骤 4 创建的 `GameConfig` 拖入 **GameManager → Config** 槽位。

---

## 步骤 6：创建三个场景

### 场景 1：MainMenu

1. **File → New Scene**（删除默认的 SampleScene）
2. **File → Save Scene** 保存为 `Assets/Scenes/MainMenu.unity`
3. 创建 Canvas：
   - **Create → UI → Canvas**（Render Mode 选 **Screen Space - Overlay**）
4. 在 Canvas 内创建背景图片（纯色或渐变 Image） + 标题文字

### 场景 2：StrategyMap

1. **File → New Scene** → 保存为 `Assets/Scenes/StrategyMap.unity`
2. 创建 `GameManager` 对象（同步骤 5），挂载 `StrategyMapState`
3. 创建 Camera（Orthographic，2D 俯视角）

### 场景 3：Battle

1. **File → New Scene** → 保存为 `Assets/Scenes/Battle.unity`
2. 创建 `GameManager` 对象，挂载 `BattleState`
3. 创建 Camera（Perspective，俯视角或45度）

---

## 步骤 7：构建场景到 Build Settings

1. **File → Build Settings**
2. 将三个场景依次拖入：
   - `Scenes/MainMenu`
   - `Scenes/StrategyMap`
   - `Scenes/Battle`
3. 确保 **MainMenu 在第一位**（作为启动场景）
4. 点击 **Build** 或 **Build And Run**

---

## 步骤 8：验证运行

运行后应看到：
- 主菜单界面（中文文本正确显示）
- 点击"开始游戏"切换到 StrategyMap 场景
- 控制台无 Error（日志显示"状态切换: StrategyMapState"）

---

## 当前 Phase 1 完成状态

| 组件 | 文件 | 状态 |
|------|------|------|
| 游戏管理器 | `Core/GameManager.cs` | ✅ 完成 |
| 状态机 | `Core/GameStateMachine.cs` | ✅ 完成 |
| 事件总线 | `Core/EventBus.cs` + `GameEvents.cs` | ✅ 完成 |
| 事件数据 | `Core/IEventData.cs` | ✅ 完成 |
| 状态基类 | `Core/StateBase.cs` | ✅ 完成 |
| 枚举定义 | `Data/GameEnums.cs` | ✅ 完成 |
| 颜色常量 | `Data/GameColors.cs` | ✅ 完成 |
| 游戏配置 | `Data/Config/GameConfigSO.cs` | ✅ 完成 |
| 菜单状态 | `States/MenuState.cs` | ✅ 占位（Phase 2 完善） |
| 地图状态 | `States/StrategyMapState.cs` | ✅ 占位（Phase 3 完善） |
| 战斗状态 | `States/BattleState.cs` | ✅ 占位（Phase 4 完善） |
| UI 管理器 | `UI/UIManager.cs` | ✅ 占位（Phase 2 完善） |
| Unity 场景 | `Scenes/*.unity` | ⏳ 需在 Editor 内创建 |
| TextMeshPro 配置 | - | ⏳ 需在 Editor 内配置 |

---

## Phase 2 预告

- 完整菜单 UI（TextMeshPro + Button）
- ScriptableObject 资产批量创建（编辑器工具）
- 场景切换逻辑完善
- SO 数据绑定

---

## 常见问题

### Q: 控制台报 "GameConfigSO not found"
**A**: 确保在 `Assets/Resources/Config/` 下创建了 GameConfig 资源，并拖入 GameManager 的 Config 槽位。

### Q: 中文显示为方块
**A**: 回到步骤 3，确保 TMP Font Asset 的 Character Set 包含 `4E00-9FFF`（中文 Unicode 范围），重新 Generate。

### Q: 场景切换黑屏
**A**: Phase 1 阶段场景内容为空，正常。切换成功会看到日志"状态切换"。

### Q: Unity 版本兼容性
**A**: 推荐 **2022.3 LTS**。如使用 6xxx 版本，部分 API 可能有细微差异。
