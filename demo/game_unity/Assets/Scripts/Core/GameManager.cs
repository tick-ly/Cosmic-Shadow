using UnityEngine;

/// <summary>
/// 游戏主管理器（单例）
/// 跨场景存在，管理核心系统引用和全局游戏数据
/// </summary>
public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    [Header("Core Systems")]
    public GameStateMachine StateMachine;
    public EventManager EventManager;
    public UIManager UI;

    [Header("Game Data")]
    public GameConfigSO Config;
    public int NormalResource { get; set; } = 500;
    public int CompromisePoints { get; set; } = 50;
    public int CurrentRealityDebt { get; set; } = 0;

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        DontDestroyOnLoad(gameObject);

        InitializeSystems();
    }

    private void InitializeSystems()
    {
        StateMachine = GetComponent<GameStateMachine>();
        EventManager = GetComponent<EventManager>();
        UI = GetComponent<UIManager>();

        if (Config == null)
            Debug.LogWarning("[GameManager] GameConfigSO 未配置，请在 Inspector 中拖入配置资源。");
    }

    private void Update()
    {
        StateMachine?.CurrentState?.OnUpdate(Time.deltaTime);
    }

    public T GetSystem<T>() where T : class
    {
        if (typeof(T) == typeof(GameStateMachine)) return StateMachine as T;
        if (typeof(T) == typeof(EventManager)) return EventManager as T;
        if (typeof(T) == typeof(UIManager)) return UI as T;
        return null;
    }
}
