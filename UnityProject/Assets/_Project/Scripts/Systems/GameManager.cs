using UnityEngine;
using UnityEngine.UI; // 修复 'UI', 'Image', 'ScrollRect' 找不到的错误
using TMPro;          // 修复 'TMPro', 'TextMeshProUGUI' 找不到的错误
using ShadowOfTheUniverse.Core;

namespace ShadowOfTheUniverse.Systems
{
    /// <summary>
    /// Unity游戏管理器 - MonoBehaviour
    /// 负责初始化游戏系统、连接Unity与核心C#逻辑
    /// 这是唯一允许直接操作核心数据层的MonoBehaviour类
    /// </summary>
    public class GameManager : MonoBehaviour
    {
        // ========== 单例模式 ==========

        private static GameManager instance;
        public static GameManager Instance
        {
            get
            {
                if (instance == null)
                {
                    GameObject go = new GameObject("GameManager");
                    instance = go.AddComponent<GameManager>();
                    DontDestroyOnLoad(go);
                }
                return instance;
            }
        }

        // ========== 游戏状态 ==========

        [Header("游戏设置")]
        [SerializeField] private bool autoStart = true;
        [SerializeField] private float gameSpeed = 1.0f;

        // ========== 内部状态 ==========

        private bool isInitialized = false;
        private bool isPaused = false;

        // ========== Unity生命周期 ==========

        private void Awake()
        {
            // 单例设置
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }

            instance = this;
            DontDestroyOnLoad(gameObject);

            // 初始化游戏
            InitializeGame();
        }

        private void Start()
        {
            if (autoStart)
            {
                StartGame();
            }
        }

        private void Update()
        {
            if (!isInitialized || isPaused)
                return;

            // 更新游戏逻辑
            GameTime.deltaTime = Time.deltaTime * gameSpeed;

            // 处理事件队列
            EventManager.Instance.ProcessQueue();
        }

        // ========== 初始化 ==========

        private void InitializeGame()
        {
            if (isInitialized)
                return;

            Debug.Log("[GameManager] 初始化游戏系统...");

            // 初始化事件系统
            InitializeEventSystem();

            // 初始化游戏状态
            InitializeGameState();

            // 订阅核心事件
            SubscribeToEvents();

            isInitialized = true;
            Debug.Log("[GameManager] 游戏系统初始化完成");
        }

        private void InitializeEventSystem()
        {
            // 事件系统已在EventManager构造函数中初始化
            Debug.Log("[GameManager] 事件系统已就绪");
        }

        private void InitializeGameState()
        {
            // 重置游戏状态
            GameState.Instance.ResetGame();

            Debug.Log("[GameManager] 游戏状态已重置");
        }

        private void SubscribeToEvents()
        {
            // 订阅核心游戏事件
            EventManager.Instance.Subscribe(GameEvents.GAME_OVER, OnGameOver);
            EventManager.Instance.Subscribe(GameEvents.DEBT_CRITICAL, OnDebtCrisis);
            EventManager.Instance.Subscribe(GameEvents.CHARACTER_DIED, OnCharacterDied);
        }

        // ========== 游戏流程控制 ==========

        public void StartGame()
        {
            Debug.Log("[GameManager] 游戏开始");

            // 触发游戏开始事件
            EventManager.Instance.Emit(GameEvents.GAME_START);

            // 切换到策略地图状态
            GameState.Instance.ChangeState(GameStateType.StrategyMap);
        }

        public void PauseGame()
        {
            if (isPaused) return;

            isPaused = true;
            Time.timeScale = 0f;

            EventManager.Instance.Emit(GameEvents.GAME_PAUSE);
            Debug.Log("[GameManager] 游戏暂停");
        }

        public void ResumeGame()
        {
            if (!isPaused) return;

            isPaused = false;
            Time.timeScale = 1f;

            EventManager.Instance.Emit(GameEvents.GAME_RESUME);
            Debug.Log("[GameManager] 游戏恢复");
        }

        public void RestartGame()
        {
            Debug.Log("[GameManager] 重新开始游戏");

            // 重置游戏状态
            GameState.Instance.ResetGame();

            // 恢复时间流速
            Time.timeScale = 1f;
            isPaused = false;

            // 重新开始
            StartGame();
        }

        public void QuitGame()
        {
            Debug.Log("[GameManager] 退出游戏");

            // 清理事件系统
            EventManager.Instance.ClearAllEvents();

            // 退出应用
            Application.Quit();

#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#endif
        }

        // ========== 事件处理器 ==========

        private void OnGameOver()
        {
            Debug.Log("[GameManager] 游戏结束");

            // 切换到游戏结束状态
            GameState.Instance.ChangeState(GameStateType.GameOver);

            // 暂停游戏
            PauseGame();
        }

        private void OnDebtCrisis()
        {
            Debug.LogWarning("[GameManager] 现实债务危机！");

            // 可以在这里添加特殊处理逻辑
            // 例如：触发特殊事件、显示警告UI等
        }

        private void OnCharacterDied()
        {
            Debug.LogWarning("[GameManager] 角色死亡");

            // 触发游戏结束
            EventManager.Instance.Emit(GameEvents.GAME_OVER);
        }

        // ========== 游戏速度控制 ==========

        public void SetGameSpeed(float speed)
        {
            gameSpeed = Mathf.Clamp(speed, 0.1f, 3.0f);
            Debug.Log($"[GameManager] 游戏速度设置为: {gameSpeed}x");
        }

        // ========== 调试功能 ==========

        private void OnGUI()
        {
#if UNITY_EDITOR || DEBUG_BUILD
            // 显示调试信息
            GUILayout.BeginArea(new Rect(10, 10, 300, 200));
            GUILayout.BeginVertical("box");

            GUILayout.Label($"游戏状态: {GameState.Instance.CurrentState}");
            GUILayout.Label($"当前回合: {GameState.Instance.CurrentTurn}");
            GUILayout.Label($"游戏速度: {gameSpeed}x");

            if (GUILayout.Button("暂停/恢复"))
            {
                if (isPaused)
                    ResumeGame();
                else
                    PauseGame();
            }

            if (GUILayout.Button("重新开始"))
            {
                RestartGame();
            }

            GUILayout.EndVertical();
            GUILayout.EndArea();
#endif
        }

        // ========== 清理 ==========

        private void OnDestroy()
        {
            if (instance == this)
            {
                // 清理事件系统
                EventManager.Instance.ClearAllEvents();
            }
        }
    }

    // ========== 游戏时间辅助类 ==========

    public static class GameTime
    {
        public static float deltaTime { get; set; }
        public static float timeScale => GameManager.Instance != null ? 1.0f : 1.0f;
    }
}
