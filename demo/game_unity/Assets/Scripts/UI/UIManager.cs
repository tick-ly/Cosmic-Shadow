using UnityEngine;

/// <summary>
/// UI 管理器
/// 负责 HUD 的显示/隐藏
/// 在 Phase 2 中扩展为完整的 UI 系统
/// </summary>
public class UIManager : MonoBehaviour
{
    [Header("HUD References")]
    [SerializeField] private GameObject hudRoot;
    [SerializeField] private GameObject menuRoot;
    [SerializeField] private GameObject battleRoot;

    private void Start()
    {
        // 默认全部隐藏，由各 State 控制显示
        HideAll();
    }

    public void ShowHUD() => SetActive(hudRoot, true);
    public void HideHUD() => SetActive(hudRoot, false);

    public void ShowMenu() => SetActive(menuRoot, true);
    public void HideMenu() => SetActive(menuRoot, false);

    public void ShowBattleUI() => SetActive(battleRoot, true);
    public void HideBattleUI() => SetActive(battleRoot, false);

    public void HideAll()
    {
        SetActive(hudRoot, false);
        SetActive(menuRoot, false);
        SetActive(battleRoot, false);
    }

    private static void SetActive(GameObject go, bool active)
    {
        if (go != null && go.activeSelf != active)
            go.SetActive(active);
    }
}
