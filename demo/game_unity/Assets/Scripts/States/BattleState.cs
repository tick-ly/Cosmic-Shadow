using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// 战斗状态
/// 场景：Assets/Scenes/Battle.unity
/// </summary>
public class BattleState : StateBase
{
    public override void OnEnter()
    {
        Log("战斗进入");
        // TODO (Phase 4): 初始化战场数据、启动战斗循环
    }

    public override void OnExit()
    {
        Log("战斗退出");
    }

    public override void OnUpdate(float deltaTime)
    {
        // TODO (Phase 4): 回合循环、技能使用、伤害结算
    }

    /// <summary>
    /// 退出战斗，返回战略地图
    /// </summary>
    public void OnBattleEnd(bool playerWon)
    {
        Log($"战斗结束，胜负: {(playerWon ? "胜利" : "失败")}");
        RequestSceneChange("StrategyMap", LoadSceneMode.Single);
    }

    public override string StateName => "BattleState";
}
