using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// 游戏状态机
/// 支持 Scene 切换模式和同 Scene 状态切换模式
/// 推荐使用 Scene 切换模式
/// </summary>
public class GameStateMachine : MonoBehaviour
{
    public StateBase CurrentState { get; private set; }
    private readonly Queue<StateBase> _history = new(); // FIFO：返回上一状态

    public event Action<string> OnStateChanged;

    private void Awake()
    {
        // 订阅场景切换请求
        GameEvents.SceneChangeRequest.Subscribe(OnSceneChangeRequest);
        // 订阅场景加载完成
        SceneManager.sceneLoaded += OnSceneLoaded;
    }

    private void OnDestroy()
    {
        GameEvents.SceneChangeRequest.Unsubscribe(OnSceneChangeRequest);
        SceneManager.sceneLoaded -= OnSceneLoaded;
    }

    // ==================== Scene 切换模式（推荐）====================

    /// <summary>
    /// 切换到指定场景（推荐方式）
    /// </summary>
    public void ChangeScene(string sceneName, LoadSceneMode mode = LoadSceneMode.Single)
    {
        Log($"请求切换场景: {sceneName}");
        CurrentState?.OnExit();
        CurrentState = null;
        _history.Clear();

        LoadingScreen.Show();
        SceneManager.LoadScene(sceneName, mode);
    }

    /// <summary>
    /// 异步加载场景（可选）
    /// </summary>
    public void ChangeSceneAsync(string sceneName, LoadSceneMode mode = LoadSceneMode.Single)
    {
        Log($"请求异步切换场景: {sceneName}");
        CurrentState?.OnExit();
        CurrentState = null;
        _history.Clear();

        LoadingScreen.Show();
        StartCoroutine(LoadSceneAsync(sceneName, mode));
    }

    private System.Collections.IEnumerator LoadSceneAsync(string sceneName, LoadSceneMode mode)
    {
        var op = SceneManager.LoadSceneAsync(sceneName, mode);
        while (!op.isDone)
            yield return null;
        LoadingScreen.Hide();
    }

    // ==================== 同 Scene 状态切换模式 =====================

    /// <summary>
    /// 在当前 Scene 内切换状态（需要 State Prefab）
    /// </summary>
    public void ChangeState<T>() where T : StateBase
    {
        ChangeState(typeof(T));
    }

    public void ChangeState(Type stateType)
    {
        if (!typeof(StateBase).IsAssignableFrom(stateType))
        {
            Debug.LogError($"[GameStateMachine] {stateType.Name} 不是 StateBase 的子类");
            return;
        }

        // 从 Resources 加载 State Prefab
        string prefabPath = $"States/{stateType.Name}";
        var prefab = Resources.Load<GameObject>(prefabPath);

        if (prefab == null)
        {
            // 尝试在当前场景查找
            var existing = FindObjectOfType(stateType) as StateBase;
            if (existing != null)
            {
                SwitchTo(existing);
                return;
            }
            Debug.LogError($"[GameStateMachine] 无法切换到 {stateType.Name}，" +
                $"场景中没有该组件，也没有找到 Prefab: {prefabPath}");
            return;
        }

        var instance = Instantiate(prefab, transform);
        var state = instance.GetComponent<StateBase>();
        SwitchTo(state);
    }

    private void SwitchTo(StateBase newState)
    {
        CurrentState?.OnExit();
        _history.Enqueue(CurrentState);
        CurrentState = newState;
        CurrentState.OnEnter();
        Log($"状态切换: {CurrentState.StateName}");
        OnStateChanged?.Invoke(CurrentState.StateName);
    }

    // ==================== 状态历史（用于返回）====================

    /// <summary>返回上一个状态</summary>
    public void PopState()
    {
        if (_history.Count == 0)
        {
            Log("状态历史为空，无法返回");
            return;
        }

        CurrentState?.OnExit();
        CurrentState = _history.Dequeue();
        CurrentState?.OnEnter();
        Log($"返回状态: {CurrentState?.StateName}");
    }

    /// <summary>清空历史</summary>
    public void ClearHistory() => _history.Clear();

    // ==================== 内部方法 =====================

    private void OnSceneChangeRequest(SceneChangeRequestEvent e)
    {
        ChangeScene(e.SceneName, e.Mode);
    }

    private void OnSceneLoaded(Scene s, LoadSceneMode mode)
    {
        LoadingScreen.Hide();
        GameEvents.SceneLoaded.Emit(new SceneLoadedEvent { SceneName = s.name });
        Log($"场景加载完成: {s.name}");

        // 在新场景中查找并激活状态
        var state = GetComponentInChildren<StateBase>();
        if (state != null && CurrentState == null)
        {
            CurrentState = state;
            CurrentState.OnEnter();
            Log($"状态激活: {CurrentState.StateName}");
        }
    }

    private static void Log(string msg) => Debug.Log($"[GameStateMachine] {msg}");
}

// ==================== 加载屏幕（可选）====================

/// <summary>
/// 简单的加载屏幕管理器
/// 场景切换时自动显示/隐藏
/// </summary>
public static class LoadingScreen
{
    private static GameObject _loadingGO;

    public static void Show()
    {
        if (_loadingGO != null) return;
        var prefab = Resources.Load<GameObject>("UI/LoadingScreen");
        if (prefab != null)
            _loadingGO = UnityEngine.Object.Instantiate(prefab);
    }

    public static void Hide()
    {
        if (_loadingGO == null) return;
        UnityEngine.Object.Destroy(_loadingGO);
        _loadingGO = null;
    }
}
