using UnityEngine;

/// <summary>
/// 状态基类
/// 所有游戏状态（Menu、StrategyMap、Battle）继承此类
/// </summary>
public abstract class StateBase : MonoBehaviour
{
    /// <summary>进入状态时调用（首次或每次激活）</summary>
    public virtual void OnEnter() { }

    /// <summary>退出状态时调用</summary>
    public virtual void OnExit() { }

    /// <summary>每帧更新</summary>
    public virtual void OnUpdate(float deltaTime) { }

    /// <summary>处理事件（由 GameStateMachine 转发）</summary>
    public virtual void OnHandleEvent(object eventData) { }

    /// <summary>状态名（用于调试）</summary>
    public virtual string StateName => GetType().Name;

    protected void Log(string message)
    {
        Debug.Log($"[{StateName}] {message}");
    }

    protected void RequestSceneChange(string sceneName, UnityEngine.SceneManagement.LoadSceneMode mode
        = UnityEngine.SceneManagement.LoadSceneMode.Single)
    {
        GameEvents.SceneChangeRequest.Emit(new SceneChangeRequestEvent
        {
            SceneName = sceneName,
            Mode = mode
        });
    }
}
