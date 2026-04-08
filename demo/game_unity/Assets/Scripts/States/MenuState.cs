using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// 主菜单状态
/// 入口场景：Assets/Scenes/MainMenu.unity
/// </summary>
public class MenuState : StateBase
{
    public override void OnEnter()
    {
        Log("主菜单进入");
        // TODO: 绑定 UI 按钮事件
        // 在 Phase 2 中通过 Inspector 绑定
    }

    public override void OnExit()
    {
        Log("主菜单退出");
    }

    /// <summary>
    /// 开始游戏按钮回调（由 UI Button 调用）
    /// </summary>
    public void OnStartGame()
    {
        Log("开始游戏");
        RequestSceneChange("StrategyMap", LoadSceneMode.Single);
    }

    /// <summary>
    /// 退出游戏按钮回调
    /// </summary>
    public void OnQuitGame()
    {
        Log("退出游戏");
#if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
#else
        Application.Quit();
#endif
    }

    public override string StateName => "MenuState";
}
