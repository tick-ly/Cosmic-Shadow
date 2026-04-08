using System.Collections.Generic;
using System.Linq;
using ShadowOfTheUniverse.Core;
using UnityEngine;

namespace ShadowOfTheUniverse.Systems
{
    public class TerrainClassifier
    {
        public List<TerrainCell> BuildCells(TerrainHeightField heightField, float landRatio, float seaRatio, float coastalRatio)
        {
            List<CellSample> samples = new List<CellSample>(heightField.CellWidth * heightField.CellHeight);

            for (int x = 0; x < heightField.CellWidth; x++)
            {
                for (int z = 0; z < heightField.CellHeight; z++)
                {
                    float avgHeight = heightField.GetCellAverageHeight(x, z);
                    float slope = heightField.GetCellSlope(x, z);
                    samples.Add(new CellSample(x, z, avgHeight, slope));
                }
            }

            ResolveHeightThresholds(samples, landRatio, seaRatio, coastalRatio, out float seaThreshold, out float coastalThreshold);

            List<TerrainCell> cells = new List<TerrainCell>(samples.Count);
            float half = heightField.CellSize * 0.5f;

            foreach (CellSample sample in samples)
            {
                TerrainType terrain = ClassifyCell(sample.Height, seaThreshold, coastalThreshold);
                string cellId = $"cell_{sample.X}_{sample.Z}";
                float worldX = sample.X * heightField.CellSize + half;
                float worldZ = sample.Z * heightField.CellSize + half;

                cells.Add(new TerrainCell(
                    cellId,
                    sample.X,
                    sample.Z,
                    worldX,
                    worldZ,
                    terrain,
                    sample.Height,
                    sample.Slope));
            }

            return cells;
        }

        public TerrainType ClassifyCell(float height, float seaThreshold, float coastalThreshold)
        {
            if (height <= seaThreshold)
            {
                return TerrainType.Sea;
            }

            if (height <= coastalThreshold)
            {
                return TerrainType.Coastal;
            }

            return TerrainType.Land;
        }

        private static void ResolveHeightThresholds(
            List<CellSample> samples,
            float landRatio,
            float seaRatio,
            float coastalRatio,
            out float seaThreshold,
            out float coastalThreshold)
        {
            if (samples.Count == 0)
            {
                seaThreshold = 0f;
                coastalThreshold = 0f;
                return;
            }

            float totalRatio = Mathf.Max(0.001f, landRatio + seaRatio + coastalRatio);
            float normalizedSea = Mathf.Clamp01(seaRatio / totalRatio);
            float normalizedCoastal = Mathf.Clamp01(coastalRatio / totalRatio);

            int totalCells = samples.Count;
            int seaCount = Mathf.Clamp(Mathf.RoundToInt(totalCells * normalizedSea), 0, totalCells - 1);
            int coastalCount = Mathf.Clamp(Mathf.RoundToInt(totalCells * normalizedCoastal), 0, totalCells - seaCount);

            List<CellSample> sorted = samples.OrderBy(s => s.Height).ToList();

            int seaIndex = Mathf.Clamp(seaCount - 1, 0, sorted.Count - 1);
            int coastalIndex = Mathf.Clamp(seaCount + coastalCount - 1, 0, sorted.Count - 1);

            seaThreshold = sorted[seaIndex].Height;
            coastalThreshold = sorted[Mathf.Max(seaIndex, coastalIndex)].Height;
        }

        private readonly struct CellSample
        {
            public CellSample(int x, int z, float height, float slope)
            {
                X = x;
                Z = z;
                Height = height;
                Slope = slope;
            }

            public int X { get; }
            public int Z { get; }
            public float Height { get; }
            public float Slope { get; }
        }
    }
}
