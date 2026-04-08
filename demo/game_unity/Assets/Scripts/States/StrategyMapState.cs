using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// 战略地图状态
/// 场景：Assets/Scenes/StrategyMap.unity
/// </summary>
public class StrategyMapState : StateBase
{
    public override void OnEnter()
    {
        Log("战略地图进入");
        // TODO (Phase 3): 初始化星图数据、注册节点点击事件
    }

    public override void OnExit()
    {
        Log("战略地图退出");
    }

    public override void OnUpdate(float deltaTime)
    {
        // TODO (Phase 3): 更新 HUD、债务计算、敌方 AI
    }

    /// <summary>
    /// 返回主菜单（由 HUD 按钮调用）
    /// </summary>
    public void OnReturnToMenu()
    {
        Log("返回主菜单");
        RequestSceneChange("MainMenu", LoadSceneMode.Single);
    }

    /// <summary>
    /// 结束玩家回合（由 HUD 按钮调用）
    /// </summary>
    public void OnEndTurn()
    {
        Log("结束玩家回合");
        // TODO (Phase 3): 执行敌方 AI 回合
    }

    public override string StateName => "StrategyMapState";
}
