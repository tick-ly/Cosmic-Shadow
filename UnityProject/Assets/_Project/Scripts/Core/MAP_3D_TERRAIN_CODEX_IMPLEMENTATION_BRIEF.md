# Codex Implementation Brief: 3D Terrain Surface + Strategy Graph

## Objective

Refactor the current map system so that:

- terrain is rendered as a 3D mesh on the `XZ` plane with `Y` height
- gameplay remains on a separate strategy node graph
- terrain surface clicks resolve back to strategy nodes

Do not move gameplay rules onto the terrain mesh.

## Current Codebase Constraints

Relevant existing files:

- `Assets/_Project/Scripts/Systems/MapManager.cs`
- `Assets/_Project/Scripts/Core/MapNode.cs`
- `Assets/_Project/Scripts/Core/TerrainCell.cs`
- `Assets/_Project/Scripts/Strategy/PlayerCommander.cs`
- `Assets/_Project/Scripts/UI/GameUIManager.cs`

Known current state:

- `MapManager` already contains partial dual-layer work using `terrainCellsPerNode` and `terrainCellSize`
- `MapNode` still uses `CoordinateX / CoordinateY` and `WorldX / WorldY`
- `TerrainCell` is currently a minimal placeholder
- selection and UI still assume old node-position lookup patterns

## Execution Rules

1. Keep the project compiling after each phase.
2. Do not delete the old fallback visual path until the new mesh path is working.
3. Use a compatibility bridge first, then rename coordinates cleanly later.
4. Treat current `WorldX / WorldY` as transitional storage, not final architecture.
5. Keep strategy systems independent from triangle topology.

## Target File Set

### Modify

- `Assets/_Project/Scripts/Systems/MapManager.cs`
- `Assets/_Project/Scripts/Core/MapNode.cs`
- `Assets/_Project/Scripts/Core/TerrainCell.cs`
- `Assets/_Project/Scripts/Strategy/PlayerCommander.cs`
- `Assets/_Project/Scripts/UI/GameUIManager.cs`

### Add

- `Assets/_Project/Scripts/Core/TerrainHeightField.cs`
- `Assets/_Project/Scripts/Systems/TerrainHeightGenerator.cs`
- `Assets/_Project/Scripts/Systems/TerrainClassifier.cs`
- `Assets/_Project/Scripts/Systems/StrategyGraphBuilder.cs`
- `Assets/_Project/Scripts/Systems/TerrainMeshBuilder.cs`
- `Assets/_Project/Scripts/Systems/MapRaycastResolver.cs`
- `Assets/_Project/Scripts/Data/MapGenerationConfigSO.cs`

## Phase Plan

### Phase 1: Introduce Dense Terrain Data

Goal:

- add a proper dense terrain model without breaking current generation

Files:

- add `TerrainHeightField.cs`
- extend `TerrainCell.cs`
- add `TerrainHeightGenerator.cs`
- add `TerrainClassifier.cs`

Classes and responsibilities:

`TerrainHeightField`

- store dense vertex height samples
- fields:
  - `VertexWidth`
  - `VertexHeight`
  - `CellSize`
  - `SeaLevel`
  - `float[,] Heights`

`TerrainHeightGenerator`

- method:
  - `TerrainHeightField Generate(MapGenerationConfigSO config, int nodeWidth, int nodeHeight, int cellsPerNode, int seed)`
- responsibility:
  - create dense height samples

`TerrainClassifier`

- methods:
  - `List<TerrainCell> BuildCells(TerrainHeightField heightField)`
  - `TerrainType ClassifyCell(float averageHeight, float seaLevel, float slope)`
- responsibility:
  - convert height field into terrain cells

`TerrainCell`

- add fields/properties:
  - `CellX`
  - `CellZ`
  - `Vector3 WorldPosition`
  - `float Height`
  - `float Slope`
  - `string StrategyNodeId`

Acceptance:

- project compiles
- `MapManager` can request a height field and build terrain cells
- no gameplay logic depends on mesh yet

### Phase 2: Build Strategy Graph From Terrain Cells

Goal:

- make strategy nodes derive from terrain cells instead of being the only map layer

Files:

- add `StrategyGraphBuilder.cs`
- modify `MapNode.cs`
- modify `MapManager.cs`

Classes and responsibilities:

`StrategyGraphBuilder`

- methods:
  - `List<MapNode> BuildNodes(IReadOnlyList<TerrainCell> terrainCells, int nodeWidth, int nodeHeight, int cellsPerNode)`
  - `TerrainType DetermineNodeTerrain(IReadOnlyList<TerrainCell> nodeCells)`
  - `void BuildConnections(IReadOnlyDictionary<string, MapNode> nodes, int nodeWidth, int nodeHeight)`

`MapNode`

- add:
  - `Vector3 WorldPosition`
  - optional compatibility accessors for `WorldX / WorldY`
- preserve:
  - logical grid coordinates for pathfinding and ids

`MapManager`

- replace direct node generation logic with:
  - dense terrain generation
  - terrain cell classification
  - strategy graph build

Acceptance:

- nodes are generated from aggregated terrain cells
- node world positions are centered on terrain regions
- old systems can still resolve node ids

### Phase 3: Add 3D Terrain Mesh

Goal:

- render the terrain as a real mesh on `XZ`

Files:

- add `TerrainMeshBuilder.cs`
- modify `MapManager.cs`

Classes and responsibilities:

`TerrainMeshBuilder`

- methods:
  - `Mesh BuildMesh(TerrainHeightField heightField, IReadOnlyList<TerrainCell> terrainCells)`
  - `Color ResolveVertexColor(TerrainType terrainType)`
  - `int GetCellIndex(int x, int z, int cellWidth)`

Implementation notes:

- build vertices on `XZ`, height on `Y`
- build triangles per quad
- assign normals and UVs
- optionally assign vertex colors by terrain type

`MapManager`

- create or reuse:
  - `MeshFilter`
  - `MeshRenderer`
  - `MeshCollider`
- add a debug switch:
  - `useTerrainMesh`
- keep old fallback visuals available while verifying

Acceptance:

- scene shows a 3D terrain mesh
- camera frames the actual mesh bounds
- old fallback can be turned off

### Phase 4: Raycast Selection and Node Resolution

Goal:

- make the 3D surface the primary interaction layer

Files:

- add `MapRaycastResolver.cs`
- modify `PlayerCommander.cs`
- modify `GameUIManager.cs`

Classes and responsibilities:

`MapRaycastResolver`

- methods:
  - `bool TryResolveCell(Vector3 worldPoint, out TerrainCell cell)`
  - `bool TryResolveNode(Vector3 worldPoint, out MapNode node)`
  - `Vector2Int WorldToCell(Vector3 worldPoint)`

`PlayerCommander`

- replace current click-to-node path with:
  - raycast to terrain mesh
  - resolve terrain cell
  - resolve strategy node

`GameUIManager`

- read selected node from resolved node reference
- stop relying on transform-position reconstruction

Acceptance:

- clicking the terrain selects the correct strategy node
- UI and selection remain stable on sloped terrain

### Phase 5: Surface Projection and Cleanup

Goal:

- place objects correctly on terrain and remove obsolete assumptions

Files:

- modify `MapManager.cs`
- modify gameplay/object placement call sites as needed

Tasks:

- project forts, markers, units, and objectives to `MapNode.WorldPosition`
- ensure surface height is used consistently
- remove remaining XY-ground assumptions
- keep compatibility shims only where still needed

Acceptance:

- markers do not float or clip into terrain
- node movement and combat remain graph-based
- no critical systems assume tilemap rendering

## Required Public Methods

Codex should prefer these stable orchestration methods:

`MapManager`

- `GenerateMap()`
- `GetNodeAtWorldPosition(float worldX, float worldZ)` or compatible transitional overload
- `TryGetNodeFromWorldPoint(Vector3 worldPoint, out MapNode node)`

`TerrainHeightGenerator`

- `Generate(...)`

`TerrainClassifier`

- `BuildCells(...)`

`StrategyGraphBuilder`

- `BuildNodes(...)`
- `BuildConnections(...)`

`TerrainMeshBuilder`

- `BuildMesh(...)`

`MapRaycastResolver`

- `TryResolveCell(...)`
- `TryResolveNode(...)`

## Guardrails

- do not pathfind on mesh vertices
- do not use `MapNode` as a terrain vertex container
- do not mix `XY` ground and `XZ` ground in the new path
- do not remove fallback debug rendering until mesh interaction is verified
- do not couple strategy node count to terrain vertex resolution

## Definition of Done

- terrain mesh renders correctly
- terrain cells and strategy nodes are both generated
- node density and terrain density are independently configurable
- player click on mesh resolves to node selection
- units and objectives can be placed on terrain surface
- existing gameplay systems still operate on strategy nodes
- project compiles cleanly

## Suggested Commit Sequence

1. add terrain data classes
2. wire `MapManager` to dense terrain generation
3. add strategy graph builder
4. add terrain mesh builder
5. add raycast resolver
6. switch commander selection
7. clean up old coordinate assumptions

This order minimizes regression risk and keeps the project testable throughout the refactor.
