using UnityEngine;

namespace ShadowOfTheUniverse.V2.Runtime
{
    public static class RuntimeSceneBootstrap
    {
        public static Camera EnsureCamera()
        {
            Camera camera = Camera.main;
            if (camera != null)
            {
                if (Object.FindAnyObjectByType<AudioListener>() == null) camera.gameObject.AddComponent<AudioListener>();
                return camera;
            }

            GameObject cameraObject = new GameObject("Main Camera");
            camera = cameraObject.AddComponent<Camera>();
            cameraObject.AddComponent<AudioListener>();
            camera.tag = "MainCamera";
            camera.transform.position = new Vector3(0f, 12f, -12f);
            camera.transform.rotation = Quaternion.Euler(55f, 0f, 0f);
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.05f, 0.06f, 0.07f);
            return camera;
        }

        public static void EnsureLight()
        {
            if (Object.FindAnyObjectByType<Light>() != null)
            {
                return;
            }

            GameObject lightObject = new GameObject("Directional Light");
            Light light = lightObject.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.2f;
            light.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
        }
    }
}
