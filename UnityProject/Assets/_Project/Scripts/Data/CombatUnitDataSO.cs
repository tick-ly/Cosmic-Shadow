using UnityEngine;
using ShadowOfTheUniverse.Core;

namespace ShadowOfTheUniverse.Data
{
    /// <summary>
    /// 战斗单位数据模板 - ScriptableObject
    /// 用于配置海陆空三军单位
    /// </summary>
    [CreateAssetMenu(fileName = "NewCombatUnit", menuName = "Shadow of the Universe/Combat Unit Data")]
    public class CombatUnitDataSO : ScriptableObject
    {
        [Header("基础信息")]
        [SerializeField] private string unitId;
        [SerializeField] private string unitName;
        [SerializeField] private UnitDomain domain;
        [SerializeField] private UnitScale scale;
        [SerializeField] private BloodlineTier tier;
        [TextArea(3, 6)]
        [SerializeField] private string description;

        [Header("基础属性")]
        [SerializeField] private int maxHealth;
        [SerializeField] private int baseAttackPower;
        [SerializeField] private int baseDefense;

        [Header("移动属性")]
        [SerializeField] private int movementRange;     // 陆军/海军移动范围
        [SerializeField] private int operationRange;    // 空军作战半径
        [SerializeField] private int visionRange;

        [Header("超能力属性（单兵单位专用）")]
        [SerializeField] private bool canCrossTerrain;
        [SerializeField] private int terrainCrossingDebtCost;

        [Header("视觉效果")]
        [SerializeField] private Sprite unitIcon;
        [SerializeField] private GameObject unitPrefab;

        // ========== 属性访问 ==========

        public string UnitId => unitId;
        public string UnitName => unitName;
        public UnitDomain Domain => domain;
        public UnitScale Scale => scale;
        public BloodlineTier Tier => tier;
        public string Description => description;

        public int MaxHealth => maxHealth;
        public int BaseAttackPower => baseAttackPower;
        public int BaseDefense => baseDefense;

        public int MovementRange => movementRange;
        public int OperationRange => operationRange;
        public int VisionRange => visionRange;

        public bool CanCrossTerrain => canCrossTerrain;
        public int TerrainCrossingDebtCost => terrainCrossingDebtCost;

        public Sprite UnitIcon => unitIcon;
        public GameObject UnitPrefab => unitPrefab;

        // ========== 创建单位实例 ==========

        /// <summary>
        /// 创建运行时CombatUnit实例
        /// </summary>
        public CombatUnit CreateUnitInstance()
        {
            CombatUnit unit = new CombatUnit(
                unitName,
                tier,
                null,  // classData（可选）
                domain,
                scale,
                maxHealth
            );

            // 设置自定义移动属性
            if (domain != UnitDomain.Air)
            {
                // 通过反射设置私有属性（或添加公共setter方法）
                // 这里简化处理，实际应该在CombatUnit中添加初始化方法
            }

            return unit;
        }

        // ========== 编辑器预设 ==========

#if UNITY_EDITOR
        [ContextMenu("配置为陆军队伍")]
        public void ConfigureAsLandSquad()
        {
            domain = UnitDomain.Land;
            scale = UnitScale.Squad;
            canCrossTerrain = false;
            movementRange = 2;
            operationRange = 0;
            visionRange = 2;
            maxHealth = 100;
            baseAttackPower = 20;
            baseDefense = 15;
        }

        [ContextMenu("配置为海军队伍")]
        public void ConfigureAsSeaSquad()
        {
            domain = UnitDomain.Sea;
            scale = UnitScale.Squad;
            canCrossTerrain = false;
            movementRange = 3;
            operationRange = 0;
            visionRange = 3;
            maxHealth = 120;
            baseAttackPower = 25;
            baseDefense = 20;
        }

        [ContextMenu("配置为空军队伍")]
        public void ConfigureAsAirSquad()
        {
            domain = UnitDomain.Air;
            scale = UnitScale.Squad;
            canCrossTerrain = false;
            movementRange = 0;
            operationRange = 4;
            visionRange = 4;
            maxHealth = 80;
            baseAttackPower = 30;
            baseDefense = 10;
        }

        [ContextMenu("配置为陆战单兵（超能力者）")]
        public void ConfigureAsLandIndividual()
        {
            domain = UnitDomain.Land;
            scale = UnitScale.Individual;
            tier = BloodlineTier.Low;
            canCrossTerrain = true;
            terrainCrossingDebtCost = 30;
            movementRange = 3;
            operationRange = 0;
            visionRange = 3;
            maxHealth = 100;
            baseAttackPower = 35;
            baseDefense = 10;
        }

        private void OnValidate()
        {
            // 验证数据合理性
            if (domain == UnitDomain.Air && operationRange <= 0)
            {
                Debug.LogWarning($"[{unitName}] 空军单位必须设置作战半径");
            }

            if (domain != UnitDomain.Air && movementRange <= 0)
            {
                Debug.LogWarning($"[{unitName}] 陆军/海军单位必须设置移动范围");
            }

            if (scale == UnitScale.Individual && !canCrossTerrain)
            {
                Debug.LogWarning($"[{unitName}] 单兵单位通常应该能够跨越地形");
            }
        }
#endif
    }
}
