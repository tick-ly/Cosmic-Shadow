using System;
using System.IO;
using System.Collections.Generic;
using ShadowOfTheUniverse.V2.Data;
using ShadowOfTheUniverse.V2.Runtime;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace ShadowOfTheUniverse.V2.Editor
{
    /// <summary>Rebuilds the authored layout through Unity's native serializer.</summary>
    public static class GrayportLevelBuilder
    {
        private const string Folder = "Assets/_ProjectV2/Generated/Levels/Grayport";
        [Serializable] private sealed class Layout { public Piece[] objects; }
        [Serializable] private sealed class Piece
        {
            public string name;
            public float[] position;
            public float[] scale;
            public float[] rotation;
            public string material;
            public bool solid;
        }

        [MenuItem("Shadow/V2/Generate Grayport Level")]
        public static void Rebuild()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            RebuildBatch();
        }

        public static void RebuildBatch()
        {
            Layout layout = JsonUtility.FromJson<Layout>(File.ReadAllText(Folder + "/grayport-layout.json"));
            if (layout == null || layout.objects == null || layout.objects.Length == 0)
                throw new InvalidOperationException("Grayport layout is empty.");
            MissionBootstrapConfigSO config = AssetDatabase.LoadAssetAtPath<MissionBootstrapConfigSO>(Folder + "/Grayport_Bootstrap.asset");
            if (config == null || config.DefaultMission == null)
                throw new InvalidOperationException("Grayport mission assets are missing.");
            // Validate every material before replacing the generated scene.
            var materials = new Dictionary<string, Material>();
            foreach (Piece p in layout.objects)
            {
                if (p.position.Length != 3 || p.rotation.Length != 3 || p.scale.Length != 3)
                    throw new InvalidOperationException("Malformed piece: " + p.name);
                if (materials.ContainsKey(p.material)) continue;
                Material m = AssetDatabase.LoadAssetAtPath<Material>(Folder + "/Materials/" + p.material + ".mat");
                if (m == null) throw new InvalidOperationException("Missing material: " + p.material);
                materials.Add(p.material, m);
            }
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Transform environment = new GameObject("Grayport / Authored Environment").transform;
            foreach (Piece p in layout.objects)
            {
                GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                go.name = p.name;
                go.transform.SetParent(environment, false);
                go.transform.position = V(p.position);
                go.transform.localScale = V(p.scale);
                go.transform.rotation = Quaternion.Euler(V(p.rotation));
                go.GetComponent<Renderer>().sharedMaterial = materials[p.material];
                // The tactical graph constrains walking; scenery must not eat waypoint clicks.
                UnityEngine.Object.DestroyImmediate(go.GetComponent<Collider>());
                go.isStatic = true;
            }
            var runtime = new GameObject("Grayport Mission Runtime").AddComponent<MissionRuntimeController>();
            var serialized = new SerializedObject(runtime);
            serialized.FindProperty("bootstrapConfig").objectReferenceValue = config;
            serialized.FindProperty("authoredEnvironment").boolValue = true;
            serialized.FindProperty("movementSpeed").floatValue = 9;
            serialized.ApplyModifiedPropertiesWithoutUndo();
            new GameObject("Grayport Camera and Controls").AddComponent<GrayportPresentation>();
            Camera camera = RuntimeSceneBootstrap.EnsureCamera();
            camera.orthographic = true;
            camera.orthographicSize = 53;
            camera.transform.position = new Vector3(86, 100, -118);
            camera.transform.LookAt(new Vector3(6, 0, 2));
            camera.farClipPlane = 500;
            RuntimeSceneBootstrap.EnsureLight();
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(.3f, .38f, .43f);
            string path = Folder + "/Grayport_Blackout.unity";
            if (!EditorSceneManager.SaveScene(scene, path)) throw new IOException("Scene save failed.");
            var scenes = new List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
            if (!scenes.Exists(s => s.path == path)) scenes.Add(new EditorBuildSettingsScene(path, true));
            EditorBuildSettings.scenes = scenes.ToArray();
            AssetDatabase.SaveAssets();
            string report = Path.GetFullPath("../docs/grayport/unity-generation.txt");
            File.WriteAllText(report, "Unity " + Application.unityVersion + "\nScene: " + path + "\nObjects: " + layout.objects.Length + "\nNative generation: passed\nPlay Mode: not run\n");
            Debug.Log("GRAYPORT_GENERATION_OK " + layout.objects.Length + " pieces.");
        }

        private static Vector3 V(float[] p) { return new Vector3(p[0], p[1], p[2]); }

        public static void RenderPreviewBatch()
        {
            EditorSceneManager.OpenScene(Folder + "/Grayport_Blackout.unity");
            Camera camera = Camera.main;
            if (camera == null) throw new InvalidOperationException("Scene camera missing.");
            RenderTexture target = new RenderTexture(1600, 1000, 24);
            RenderTexture previous = RenderTexture.active;
            Texture2D image = new Texture2D(1600, 1000, TextureFormat.RGB24, false);
            try
            {
                camera.targetTexture = target;
                camera.Render();
                RenderTexture.active = target;
                image.ReadPixels(new Rect(0, 0, 1600, 1000), 0, 0);
                image.Apply();
                File.WriteAllBytes(Path.GetFullPath("../docs/grayport/unity-preview.png"), image.EncodeToPNG());
            }
            finally
            {
                camera.targetTexture = null;
                RenderTexture.active = previous;
                target.Release();
                UnityEngine.Object.DestroyImmediate(target);
                UnityEngine.Object.DestroyImmediate(image);
            }
        }
    }
}
