# 灰港断讯：地图交付与验证记录

## 当前产物

以下路径均相对于仓库根目录。

- Unity 场景：`UnityProjectV2/Assets/_ProjectV2/Generated/Levels/Grayport/Grayport_Blackout.unity`
- 关卡目录：`UnityProjectV2/Assets/_ProjectV2/Generated/Levels/Grayport/`
- 独立三维预览：`docs/grayport/index.html`（可直接用浏览器打开，不需要外部资源）
- 同源布局：`UnityProjectV2/Assets/_ProjectV2/Generated/Levels/Grayport/grayport-layout.json`

地图包含登陆滩、货柜堆场、巡逻道路、维修区、高台中继站、撤离码头六个区域。正门、仓库、沿岸三种接近路线最终接入中继站，再经东侧坡道抵达撤离码头。

这是实际场景资产，不是地图概念图。浏览器预览渲染同一批几何对象，但使用自己的轻量 WebGL 渲染器，灯光表现与 Unity 会有差异。

## 重建

在项目根目录执行：

```powershell
python -m pip install PyYAML
python tools/generate_grayport.py
python tools/verify_grayport.py
dotnet run --project tools/grayport-checks/GrayportChecks.csproj
```

生成器仅使用 Python 标准库；资产验证器使用 PyYAML；Core 测试使用 .NET 10。Unity 内可使用 `Shadow/V2/Generate Grayport Level`，从布局文件调用 Unity 原生序列化重新保存场景并追加到构建列表。旧 `V2_MVP.unity` 保留。

## Unity 内操作

打开新场景后进入 Play Mode。点击相邻战术锚点沿道路移动，在中继站执行风险技能，目标完成后移动到东端撤离点。滚轮缩放、中键拖动平移；左下角可重开、复位镜头、隐藏标识。当前路径由战术图约束，场景建筑不是自由漫游的物理碰撞地图。

## 验证边界

- `validation.json`：连通性、唯一 ID、路线中心线与配置为实体的建筑/掩体间距检查。
- `asset-checks.json`：Unity YAML 可解析、引用闭合、场景几何与预览一致、重复生成字节一致。
- `core-checks.json`：使用真实 Core 源码编译执行三路线移动、目标完成与撤离、失败条件等检查。
- 上述检查不等于 Unity 导入、运行时 UI 或 Play Mode 验收。编辑器验证另行记录。

## 尚待完成

验证环境已安装 Unity 6000.4.0f1。原生验证首次启动后以退出码 198 终止，日志报告没有有效许可证；在 Hub 中激活有效许可证后继续。机器安装路径和本地诊断日志不纳入仓库。

巡逻节点轮换、掩体暴露修正、侦察/配电交互、技能预算和目标后的动态警戒已实现并纳入 114 项 Core 检查，运行时表现仍需 Unity 验证。巡逻采用“抵达节点时结算暴露”的战术抽象，不是连续视线锥射击系统。已有轻量合成警报提示音，正式音效与表现打磨尚未验收。

所有游戏脚本还通过了基于已安装编辑器真实托管程序集的外部编译检查：`external-compile.json`。这项检查使用独立 .NET 编译器，不启动编辑器、不验证场景序列化或实际渲染，也不替代许可证激活和 Play Mode 验收。编译期间发现并修正了 UI 程序集引用名，应为实际包中的 `UnityEngine.UI`。

许可证激活后，在仓库根目录执行以下命令，并将示例路径替换为实际安装位置：

```powershell
./tools/validate_grayport_unity.ps1 -Editor "C:/Unity/6000.4.0f1/Editor/Unity.exe"
```

脚本依次进行原生重建、EditMode、PlayMode 和原生相机渲染，避免与已打开同一工程的编辑器争用；没有结果文件或空测试集均不判定通过。也可通过 `UNITY_EDITOR` 环境变量指定编辑器路径。

仅运行外部 API 编译检查（不代替上述原生验收）：

```powershell
dotnet build tools/unity-compile-check/GameCode.csproj -p:EditorRoot="C:/Unity/6000.4.0f1/Editor/Data"
```

`EditorRoot` 也可由 `UNITY_EDITOR_DATA` 环境变量提供；检查直接读取本机编辑器程序集与内置 UGUI 源码，仓库不包含这些第三方文件。

## 回滚边界

本轮新增地图在独立的 Grayport 生成目录；不要删除共享 SampleData。核心增量包括节点高度、移动预检、阵亡单位检查与战术遭遇；Runtime 增量为已制作环境模式、沿路移动和重开清理。旧样例保留原有瞬时移动路径，旧 `UnityProject/` 保持不变。需要撤回发布时，优先对相应提交使用 `git revert`，保留历史而非强制重写远端。
