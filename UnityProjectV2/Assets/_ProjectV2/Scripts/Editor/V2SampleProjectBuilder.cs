using ShadowOfTheUniverse.V2.Core;
using ShadowOfTheUniverse.V2.Data;
using ShadowOfTheUniverse.V2.Runtime;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using System.Collections.Generic;

namespace ShadowOfTheUniverse.V2.Editor
{
    public static class V2SampleProjectBuilder
    {
        private const string SampleDataFolder = "Assets/_ProjectV2/SampleData";
        private const string SceneFolder = "Assets/_ProjectV2/Scenes";
        private const string ScenePath = SceneFolder + "/V2_MVP.unity";

        [MenuItem("Shadow/V2/Create Sample MVP Assets And Scene")]
        public static void CreateSampleMvp()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            CreateSampleMvpInternal(true);
        }

        public static void CreateSampleMvpBatch()
        {
            CreateSampleMvpInternal(false);
        }

        private static void CreateSampleMvpInternal(bool showDialog)
        {
            EnsureFolder("Assets/_ProjectV2", "SampleData");
            EnsureFolder("Assets/_ProjectV2", "Scenes");

            SkillDataSO heatShift = CreateSkill(
                "V2Skill_HeatShift",
                "heat_shift",
                "Heat Shift",
                "Redirect localized thermal energy to disable a key device.",
                90,
                8,
                10,
                8,
                0,
                1,
                1,
                "Heat redirection succeeded.",
                "Thermal feedback injured the operator.");

            SkillDataSO predictiveIntuition = CreateSkill(
                "V2Skill_PredictiveIntuition",
                "predictive_intuition",
                "Predictive Intuition",
                "Read the next few seconds of battlefield motion.",
                82,
                14,
                12,
                12,
                1,
                1,
                1,
                "The route prediction revealed a clean opening.",
                "The prediction fork collapsed into noise.");

            SkillDataSO staticLock = CreateSkill(
                "V2Skill_StaticLock",
                "static_lock",
                "Static Lock",
                "Pin hostile electronics with a controlled static surge.",
                76,
                18,
                16,
                14,
                1,
                2,
                2,
                "The relay was locked and exposed.",
                "The static field arced back through the squad.");

            UnitDataSO operatorUnit = CreateUnit(
                "V2Unit_Operator",
                "operator_zero",
                "Operator Zero",
                UnitDomain.Land,
                UnitScale.Individual,
                2,
                100,
                new[] { heatShift, predictiveIntuition, staticLock });

            UnitDataSO assaultSquad = CreateUnit(
                "V2Unit_AssaultSquad",
                "assault_squad",
                "Assault Squad",
                UnitDomain.Land,
                UnitScale.Squad,
                1,
                140,
                new[] { heatShift });

            UnitDataSO airScout = CreateUnit(
                "V2Unit_AirScout",
                "air_scout",
                "Air Scout",
                UnitDomain.Air,
                UnitScale.Squad,
                3,
                80,
                new[] { predictiveIntuition });

            NodeMapSO map = CreateMap();
            TacticalMissionSO mission = CreateMission(map, operatorUnit, assaultSquad, airScout);
            MissionBootstrapConfigSO bootstrapConfig = CreateBootstrapConfig(mission);
            CreateScene(bootstrapConfig);
            RegisterBuildSettingsScene();

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            if (showDialog)
            {
                EditorUtility.DisplayDialog("V2 MVP Created", "Sample assets and V2_MVP scene were created.", "OK");
            }
        }

        private static SkillDataSO CreateSkill(
            string assetName,
            string id,
            string displayName,
            string description,
            int successRate,
            int debt,
            int backlash,
            int fatigue,
            int cooldown,
            int alertOnFailure,
            int progress,
            string successText,
            string failureText)
        {
            SkillDataSO skill = LoadOrCreate<SkillDataSO>(SampleDataFolder + "/" + assetName + ".asset");
            skill.ConfigureForEditor(id, displayName, description, successRate, debt, backlash, fatigue, cooldown, alertOnFailure, progress, successText, failureText);
            EditorUtility.SetDirty(skill);
            return skill;
        }

        private static UnitDataSO CreateUnit(
            string assetName,
            string id,
            string displayName,
            UnitDomain domain,
            UnitScale scale,
            int movementRange,
            int maxHealth,
            SkillDataSO[] skills)
        {
            UnitDataSO unit = LoadOrCreate<UnitDataSO>(SampleDataFolder + "/" + assetName + ".asset");
            unit.ConfigureForEditor(id, displayName, domain, scale, movementRange, maxHealth, skills);
            EditorUtility.SetDirty(unit);
            return unit;
        }

        private static NodeMapSO CreateMap()
        {
            NodeMapSO map = LoadOrCreate<NodeMapSO>(SampleDataFolder + "/V2Map_RelayRaid.asset");
            map.ConfigureForEditor(
                new[]
                {
                    new NodeMapSO.NodeConfig { nodeId = "base", displayName = "Forward Base", terrain = TerrainType.Land, owner = NodeOwner.Player, dangerLevel = 0, position = new Vector2(-4f, -2f) },
                    new NodeMapSO.NodeConfig { nodeId = "ridge", displayName = "Broken Ridge", terrain = TerrainType.Land, owner = NodeOwner.Neutral, dangerLevel = 1, position = new Vector2(-1.5f, 1f) },
                    new NodeMapSO.NodeConfig { nodeId = "relay", displayName = "Enemy Relay", terrain = TerrainType.Coastal, owner = NodeOwner.Enemy, dangerLevel = 3, position = new Vector2(2f, 1.5f) },
                    new NodeMapSO.NodeConfig { nodeId = "coast", displayName = "Tide Channel", terrain = TerrainType.Coastal, owner = NodeOwner.Neutral, dangerLevel = 1, position = new Vector2(1f, -2.5f) },
                    new NodeMapSO.NodeConfig { nodeId = "extract", displayName = "Extraction Point", terrain = TerrainType.Land, owner = NodeOwner.Player, dangerLevel = 0, position = new Vector2(4.5f, -1f) }
                },
                new[]
                {
                    new NodeMapSO.RouteConfig { fromNodeId = "base", toNodeId = "ridge", routeType = RouteType.LandRoute },
                    new NodeMapSO.RouteConfig { fromNodeId = "ridge", toNodeId = "relay", routeType = RouteType.LandRoute },
                    new NodeMapSO.RouteConfig { fromNodeId = "base", toNodeId = "coast", routeType = RouteType.LandRoute },
                    new NodeMapSO.RouteConfig { fromNodeId = "coast", toNodeId = "relay", routeType = RouteType.LandRoute },
                    new NodeMapSO.RouteConfig { fromNodeId = "relay", toNodeId = "extract", routeType = RouteType.LandRoute },
                    new NodeMapSO.RouteConfig { fromNodeId = "coast", toNodeId = "extract", routeType = RouteType.LandRoute }
                });
            EditorUtility.SetDirty(map);
            return map;
        }

        private static TacticalMissionSO CreateMission(NodeMapSO map, UnitDataSO operatorUnit, UnitDataSO assaultSquad, UnitDataSO airScout)
        {
            TacticalMissionSO mission = LoadOrCreate<TacticalMissionSO>(SampleDataFolder + "/V2Mission_RelayRaid.asset");
            mission.ConfigureForEditor(
                "relay_raid",
                "Relay Raid",
                MissionType.Infiltration,
                "Reach the enemy relay, complete three risk actions, then extract.",
                300,
                3,
                3,
                100,
                "relay",
                "extract",
                map,
                new[]
                {
                    new TacticalMissionSO.UnitSpawnConfig { unit = operatorUnit, startNodeId = "base" },
                    new TacticalMissionSO.UnitSpawnConfig { unit = assaultSquad, startNodeId = "base" },
                    new TacticalMissionSO.UnitSpawnConfig { unit = airScout, startNodeId = "base" }
                });
            EditorUtility.SetDirty(mission);
            return mission;
        }

        private static MissionBootstrapConfigSO CreateBootstrapConfig(TacticalMissionSO mission)
        {
            MissionBootstrapConfigSO config = LoadOrCreate<MissionBootstrapConfigSO>(SampleDataFolder + "/V2Bootstrap_RelayRaid.asset");
            config.ConfigureForEditor(mission, 15f);
            EditorUtility.SetDirty(config);
            return config;
        }

        private static void CreateScene(MissionBootstrapConfigSO bootstrapConfig)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            GameObject runtime = new GameObject("V2 Mission Runtime");
            MissionRuntimeController controller = runtime.AddComponent<MissionRuntimeController>();

            SerializedObject serialized = new SerializedObject(controller);
            serialized.FindProperty("bootstrapConfig").objectReferenceValue = bootstrapConfig;
            serialized.ApplyModifiedPropertiesWithoutUndo();

            EditorSceneManager.SaveScene(scene, ScenePath);
        }

        private static void RegisterBuildSettingsScene()
        {
            var scenes = new List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
            if (!scenes.Exists(scene => scene.path == ScenePath))
                scenes.Add(new EditorBuildSettingsScene(ScenePath, true));
            EditorBuildSettings.scenes = scenes.ToArray();
        }

        private static T LoadOrCreate<T>(string path) where T : ScriptableObject
        {
            T asset = AssetDatabase.LoadAssetAtPath<T>(path);
            if (asset != null)
            {
                return asset;
            }

            asset = ScriptableObject.CreateInstance<T>();
            AssetDatabase.CreateAsset(asset, path);
            return asset;
        }

        private static void EnsureFolder(string parent, string child)
        {
            string full = parent + "/" + child;
            if (!AssetDatabase.IsValidFolder(full))
            {
                AssetDatabase.CreateFolder(parent, child);
            }
        }
    }
}
