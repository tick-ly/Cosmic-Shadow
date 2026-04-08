using System.Collections.Generic;
using ShadowOfTheUniverse.Core;
using UnityEngine;
using UnityEngine.Rendering;

namespace ShadowOfTheUniverse.Systems
{
    public class TerrainMeshBuilder
    {
        public Mesh BuildMesh(TerrainHeightField heightField, IReadOnlyList<TerrainCell> terrainCells)
        {
            int vertexWidth = heightField.VertexWidth;
            int vertexHeight = heightField.VertexHeight;
            int vertexCount = vertexWidth * vertexHeight;

            Vector3[] vertices = new Vector3[vertexCount];
            Vector2[] uvs = new Vector2[vertexCount];
            Color[] colors = new Color[vertexCount];

            Dictionary<Vector2Int, TerrainType> terrainLookup = new Dictionary<Vector2Int, TerrainType>(terrainCells.Count);
            foreach (TerrainCell cell in terrainCells)
            {
                terrainLookup[new Vector2Int(cell.CellX, cell.CellY)] = cell.Terrain;
            }

            for (int z = 0; z < vertexHeight; z++)
            {
                for (int x = 0; x < vertexWidth; x++)
                {
                    int index = x + z * vertexWidth;
                    float worldX = x * heightField.CellSize;
                    float worldZ = z * heightField.CellSize;

                    vertices[index] = new Vector3(worldX, heightField.GetHeight(x, z), worldZ);
                    uvs[index] = new Vector2(
                        vertexWidth > 1 ? (float)x / (vertexWidth - 1) : 0f,
                        vertexHeight > 1 ? (float)z / (vertexHeight - 1) : 0f);

                    int cellX = Mathf.Clamp(x, 0, heightField.CellWidth - 1);
                    int cellZ = Mathf.Clamp(z, 0, heightField.CellHeight - 1);
                    TerrainType terrainType = terrainLookup.TryGetValue(new Vector2Int(cellX, cellZ), out TerrainType t)
                        ? t
                        : TerrainType.Land;
                    colors[index] = ResolveVertexColor(terrainType);
                }
            }

            int quadCount = (vertexWidth - 1) * (vertexHeight - 1);
            int[] triangles = new int[quadCount * 6];
            int triangleIndex = 0;

            for (int z = 0; z < vertexHeight - 1; z++)
            {
                for (int x = 0; x < vertexWidth - 1; x++)
                {
                    int bottomLeft = x + z * vertexWidth;
                    int bottomRight = bottomLeft + 1;
                    int topLeft = bottomLeft + vertexWidth;
                    int topRight = topLeft + 1;

                    triangles[triangleIndex++] = bottomLeft;
                    triangles[triangleIndex++] = topLeft;
                    triangles[triangleIndex++] = topRight;
                    triangles[triangleIndex++] = bottomLeft;
                    triangles[triangleIndex++] = topRight;
                    triangles[triangleIndex++] = bottomRight;
                }
            }

            Mesh mesh = new Mesh();
            mesh.name = "RuntimeTerrainMesh";

            if (vertexCount > 65000)
            {
                mesh.indexFormat = IndexFormat.UInt32;
            }

            mesh.vertices = vertices;
            mesh.uv = uvs;
            mesh.colors = colors;
            mesh.triangles = triangles;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        public Color ResolveVertexColor(TerrainType terrainType)
        {
            return terrainType switch
            {
                TerrainType.Sea => new Color(0.20f, 0.44f, 0.82f),
                TerrainType.Coastal => new Color(0.86f, 0.78f, 0.46f),
                TerrainType.SpatialFolding => new Color(0.78f, 0.48f, 1.00f),
                _ => new Color(0.36f, 0.63f, 0.34f)
            };
        }
    }
}
