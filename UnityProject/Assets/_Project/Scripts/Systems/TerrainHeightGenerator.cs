using ShadowOfTheUniverse.Core;
using ShadowOfTheUniverse.Data;
using UnityEngine;

namespace ShadowOfTheUniverse.Systems
{
    public class TerrainHeightGenerator
    {
        public TerrainHeightField Generate(
            MapGenerationConfigSO config,
            int nodeWidth,
            int nodeHeight,
            int cellsPerNode,
            float cellSize,
            int seed)
        {
            float noiseScale = config != null ? config.noiseScale : 0.08f;
            float heightScale = config != null ? config.heightScale : 4f;
            float seaLevel = config != null ? config.seaLevel : 0.35f;

            return Generate(nodeWidth, nodeHeight, cellsPerNode, cellSize, seed, noiseScale, heightScale, seaLevel);
        }

        public TerrainHeightField Generate(
            int nodeWidth,
            int nodeHeight,
            int cellsPerNode,
            float cellSize,
            int seed,
            float noiseScale,
            float heightScale,
            float seaLevel)
        {
            int terrainCellWidth = Mathf.Max(1, nodeWidth * Mathf.Max(1, cellsPerNode));
            int terrainCellHeight = Mathf.Max(1, nodeHeight * Mathf.Max(1, cellsPerNode));
            TerrainHeightField field = new TerrainHeightField(terrainCellWidth + 1, terrainCellHeight + 1, cellSize, seaLevel);

            float baseScale = Mathf.Max(0.0001f, noiseScale);
            float offsetX = (seed & 1023) * 0.03125f;
            float offsetZ = ((seed >> 10) & 1023) * 0.03125f;

            for (int x = 0; x < field.VertexWidth; x++)
            {
                for (int z = 0; z < field.VertexHeight; z++)
                {
                    float nx = x * baseScale + offsetX;
                    float nz = z * baseScale + offsetZ;

                    float octave0 = Mathf.PerlinNoise(nx, nz);
                    float octave1 = Mathf.PerlinNoise(nx * 2f + 37.17f, nz * 2f + 51.91f) * 0.5f;
                    float octave2 = Mathf.PerlinNoise(nx * 4f + 89.43f, nz * 4f + 13.29f) * 0.25f;
                    float normalized = (octave0 + octave1 + octave2) / 1.75f;

                    // Push the center upward slightly to avoid all-land/all-sea extremes.
                    normalized = Mathf.SmoothStep(0f, 1f, normalized);

                    field.SetHeight(x, z, normalized * Mathf.Max(0f, heightScale));
                }
            }

            return field;
        }
    }
}
