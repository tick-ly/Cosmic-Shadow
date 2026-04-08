using UnityEngine;
using UnityEngine.SceneManagement;
using System.IO;
#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.SceneManagement;
#endif

namespace ShadowOfTheUniverse.Systems
{
    /// <summary>
    /// 场景初始化辅助工具
    /// 自动创建演示场景所需的基础GameObject结构
    /// </summary>
    public class SceneInitializer : MonoBehaviour
    {
        [Header("自动创建结构")]
        [SerializeField] private bool createOnAwake = false;
        [SerializeField] private bool createGameManagers = true;
        [SerializeField] private bool createDemoController = true;
        [SerializeField] private bool createEventSystem = true;

        [Header("UI设置")]
        [SerializeField] private bool createBasicUI = true;
        [SerializeField] private bool createCanvas = true;

        private void Awake()
        {
            if (createOnAwake)
            {
                InitializeScene();
            }
        }

        [ContextMenu("初始化场景")]
        public void InitializeScene()
        {
            Debug.Log("[SceneInitializer] 开始初始化场景...");

            // 创建管理器容器
            GameObject managers = GameObject.Find("_Managers");
            if (managers == null)
            {
                managers = new GameObject("_Managers");
                Debug.Log("[SceneInitializer] 创建管理器容器");
            }

            // 创建各个管理器
            if (createGameManagers)
            {
                CreateGameManager(managers);
                CreateBattleManager(managers);
            }

            if (createDemoController)
            {
                CreateGameDemo(managers);
            }

            if (createEventSystem)
            {
                CreateUnityEventSystem();
            }

            if (createBasicUI)
            {
                CreateBasicUI();
            }

            Debug.Log("[SceneInitializer] 场景初始化完成！");
        }

        private void CreateGameManager(GameObject parent)
        {
            GameObject gm = new GameObject("GameManager");
            gm.transform.SetParent(parent.transform);
            gm.AddComponent<GameManager>();
            Debug.Log("[SceneInitializer] 创建GameManager");
        }

        private void CreateBattleManager(GameObject parent)
        {
            GameObject bm = new GameObject("BattleManager");
            bm.transform.SetParent(parent.transform);
            bm.AddComponent<BattleManager>();
            Debug.Log("[SceneInitializer] 创建BattleManager");
        }

        private void CreateGameDemo(GameObject parent)
        {
            GameObject demo = new GameObject("GameDemo");
            demo.transform.SetParent(parent.transform);
            GameDemo demoScript = demo.AddComponent<GameDemo>();
            demoScript.AutoStartDemo = false; // 手动启动
            Debug.Log("[SceneInitializer] 创建GameDemo");
        }

        private void CreateUnityEventSystem()
        {
            // Unity会自动创建EventSystem，这里只是确保存在
            UnityEngine.EventSystems.EventSystem eventSystem =
                UnityEngine.Object.FindAnyObjectByType<UnityEngine.EventSystems.EventSystem>();

            if (eventSystem == null)
            {
                GameObject es = new GameObject("EventSystem");
                es.AddComponent<UnityEngine.EventSystems.EventSystem>();
                es.AddComponent<UnityEngine.EventSystems.StandaloneInputModule>();
                Debug.Log("[SceneInitializer] 创建Unity EventSystem");
            }
        }

        private void CreateBasicUI()
        {
            if (!createCanvas) return;

            // 查找或创建Canvas
            Canvas canvas = UnityEngine.Object.FindAnyObjectByType<Canvas>();
            if (canvas == null)
            {
                GameObject canvasGo = new GameObject("Canvas");
                canvas = canvasGo.AddComponent<Canvas>();
                canvas.renderMode = RenderMode.ScreenSpaceOverlay;
                canvasGo.AddComponent<UnityEngine.UI.CanvasScaler>();
                canvasGo.AddComponent<UnityEngine.UI.GraphicRaycaster>();

                // 创建EventSystem（如果不存在）
                CreateUnityEventSystem();

                Debug.Log("[SceneInitializer] 创建Canvas");
            }

            // 创建基本信息面板
            CreateInfoPanel(canvas);
        }

        private void CreateInfoPanel(Canvas canvas)
        {
            GameObject panelGo = new GameObject("InfoPanel");
            panelGo.transform.SetParent(canvas.transform, false);

            // 添加RectTransform
            RectTransform rect = panelGo.AddComponent<RectTransform>();
            rect.anchorMin = new Vector2(0, 1);
            rect.anchorMax = new Vector2(0, 1);
            rect.pivot = new Vector2(0, 1);
            rect.anchoredPosition = new Vector2(10, -10);
            rect.sizeDelta = new Vector2(300, 200);

            // 添加背景图片（可选）
            // panelGo.AddComponent<UnityEngine.UI.Image>();

            // 创建标题文本
            CreateTitleText(panelGo);

            Debug.Log("[SceneInitializer] 创建信息面板");
        }

        private void CreateTitleText(GameObject parent)
        {
            GameObject textGo = new GameObject("TitleText");
            textGo.transform.SetParent(parent.transform, false);

            RectTransform rect = textGo.AddComponent<RectTransform>();
            rect.anchorMin = Vector2.zero;
            rect.anchorMax = Vector2.one;
            rect.sizeDelta = Vector2.zero;

            UnityEngine.UI.Text text = textGo.AddComponent<UnityEngine.UI.Text>();
            text.text = "宇宙之影 - Unity迁移项目\n\n使用GameDemo面板控制演示";
            text.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            text.fontSize = 16;
            text.alignment = TextAnchor.UpperLeft;
            text.color = Color.white;

            Debug.Log("[SceneInitializer] 创建标题文本");
        }
    }

#if UNITY_EDITOR
    /// <summary>
    /// 编辑器菜单扩展
    /// </summary>
    public class SceneInitializerMenu
    {
        [MenuItem("GameObject/Shadow of the Universe/Initialize Demo Scene")]
        public static void InitializeDemoScene()
        {
            // 查找或创建SceneInitializer
            SceneInitializer initializer = UnityEngine.Object.FindAnyObjectByType<SceneInitializer>();

            if (initializer == null)
            {
                GameObject go = new GameObject("SceneInitializer");
                initializer = go.AddComponent<SceneInitializer>();
            }

            initializer.InitializeScene();
        }

        [MenuItem("GameObject/Shadow of the Universe/Create Demo Scene Structure")]
        public static void CreateFullDemoScene()
        {
            // 创建新场景
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            // 添加场景初始化器
            GameObject initializerGo = new GameObject("SceneInitializer");
            SceneInitializer initializer = initializerGo.AddComponent<SceneInitializer>();

            // 初始化场景
            initializer.InitializeScene();

            // 保存场景
            string scenePath = "Assets/_Project/Scenes/DemoScene.unity";
            if (!Directory.Exists(Path.GetDirectoryName(scenePath)))
            {
                Directory.CreateDirectory(Path.GetDirectoryName(scenePath));
            }

            EditorSceneManager.SaveScene(scene, scenePath);
            Debug.Log($"[SceneInitializer] 演示场景已创建: {scenePath}");
        }
    }
#endif
}
