using System;
using UnityEngine;

namespace ShadowOfTheUniverse.Core
{
    [Serializable]
    public class TerrainCell
    {
        public string CellId { get; private set; }
        public int CellX { get; private set; }
        public int CellY { get; private set; }
        public int CellZ => CellY;
        public float WorldX { get; private set; }
        public float WorldY { get; private set; }
        public float WorldZ => WorldY;
        public float Height { get; private set; }
        public float Slope { get; private set; }
        public Vector3 WorldPosition => new Vector3(WorldX, Height, WorldY);
        public TerrainType Terrain { get; private set; }
        public string StrategyNodeId { get; private set; }

        public TerrainCell(
            string cellId,
            int cellX,
            int cellY,
            float worldX,
            float worldY,
            TerrainType terrain,
            float height = 0f,
            float slope = 0f)
        {
            CellId = cellId;
            CellX = cellX;
            CellY = cellY;
            WorldX = worldX;
            WorldY = worldY;
            Terrain = terrain;
            Height = height;
            Slope = slope;
        }

        public void BindToStrategyNode(string nodeId)
        {
            StrategyNodeId = nodeId;
        }

        public void SetTerrainType(TerrainType terrain)
        {
            Terrain = terrain;
        }
    }
}
