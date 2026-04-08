using UnityEngine;

namespace ShadowOfTheUniverse.Data
{
    [CreateAssetMenu(fileName = "MapGenerationConfig", menuName = "Shadow Of The Universe/Map Generation Config")]
    public class MapGenerationConfigSO : ScriptableObject
    {
        [Header("Height Field")]
        [Min(0.005f)] public float noiseScale = 0.08f;
        [Min(0f)] public float heightScale = 4f;
        [Range(0f, 1f)] public float seaLevel = 0.35f;

        [Header("Terrain Split")]
        [Min(0f)] public float landRatio = 0.5f;
        [Min(0f)] public float seaRatio = 0.3f;
        [Min(0f)] public float coastalRatio = 0.2f;
    }
}
