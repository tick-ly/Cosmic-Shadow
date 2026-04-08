using System;
using UnityEngine;

namespace ShadowOfTheUniverse.Core
{
    [Serializable]
    public class TerrainHeightField
    {
        public int VertexWidth { get; }
        public int VertexHeight { get; }
        public float CellSize { get; }
        public float SeaLevel { get; }
        public float[,] Heights { get; }

        public int CellWidth => Mathf.Max(0, VertexWidth - 1);
        public int CellHeight => Mathf.Max(0, VertexHeight - 1);

        public TerrainHeightField(int vertexWidth, int vertexHeight, float cellSize, float seaLevel)
        {
            VertexWidth = Mathf.Max(2, vertexWidth);
            VertexHeight = Mathf.Max(2, vertexHeight);
            CellSize = Mathf.Max(0.01f, cellSize);
            SeaLevel = seaLevel;
            Heights = new float[VertexWidth, VertexHeight];
        }

        public void SetHeight(int x, int z, float value)
        {
            if (x < 0 || z < 0 || x >= VertexWidth || z >= VertexHeight)
            {
                return;
            }

            Heights[x, z] = value;
        }

        public float GetHeight(int x, int z)
        {
            int clampedX = Mathf.Clamp(x, 0, VertexWidth - 1);
            int clampedZ = Mathf.Clamp(z, 0, VertexHeight - 1);
            return Heights[clampedX, clampedZ];
        }

        public float GetCellAverageHeight(int cellX, int cellZ)
        {
            int x = Mathf.Clamp(cellX, 0, CellWidth - 1);
            int z = Mathf.Clamp(cellZ, 0, CellHeight - 1);

            float h00 = GetHeight(x, z);
            float h10 = GetHeight(x + 1, z);
            float h01 = GetHeight(x, z + 1);
            float h11 = GetHeight(x + 1, z + 1);
            return (h00 + h10 + h01 + h11) * 0.25f;
        }

        public float GetCellSlope(int cellX, int cellZ)
        {
            int x = Mathf.Clamp(cellX, 0, CellWidth - 1);
            int z = Mathf.Clamp(cellZ, 0, CellHeight - 1);

            float h00 = GetHeight(x, z);
            float h10 = GetHeight(x + 1, z);
            float h01 = GetHeight(x, z + 1);

            float dx = Mathf.Abs(h10 - h00);
            float dz = Mathf.Abs(h01 - h00);
            return Mathf.Max(dx, dz);
        }
    }
}
