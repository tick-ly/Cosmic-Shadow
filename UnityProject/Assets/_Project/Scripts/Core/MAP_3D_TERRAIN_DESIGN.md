# 3D Terrain Refactor Design

## Goal

Replace the current 2D tile/sprite-based map rendering path with a true 3D terrain surface while keeping strategy gameplay on a separate logical graph.

The target result is:

- terrain rendered as a continuous 3D mesh
- gameplay still driven by stable strategy nodes
- terrain visual density independent from gameplay node density
- click, selection, movement, and objective systems mapped from the 3D surface back to logical nodes

## Current Problem

The current map code mixes multiple concerns into `MapManager`:

- strategy node generation
- terrain category generation
- fallback visual creation
- camera framing
- world-position lookup
- partial dual-layer terrain cell binding

It also still assumes a 2D coordinate model:

- `MapNode` stores `CoordinateX / CoordinateY` and `WorldX / WorldY`
- `TerrainCell` stores `CellX / CellY` and `WorldX / WorldY`
- `MapManager` computes node placement from `terrainCellsPerNode` and `terrainCellSize`

This is not compatible with the intended 3D terrain model of:

- points on a plane
- triangle mesh generation
- height displacement
- world interaction on the resulting surface

## Design Principles

1. Separate gameplay topology from render topology.
2. Use `XZ` as ground plane and `Y` as height.
3. Keep pathfinding, combat, visibility, and objectives on the strategy graph.
4. Use a dense terrain layer for surface detail and a sparser strategy layer for game rules.
5. Resolve player interaction from surface hit point to terrain cell, then to strategy node.
6. Keep the old tile/sprite path only as a temporary debug fallback during migration.

## Target Architecture

### Layer 1: Terrain Surface Layer

Responsibilities:

- generate height field
- classify terrain cells
- build render mesh
- provide mesh collider for raycast picking

Granularity:

- high density
- visual detail oriented

Primary data:

- terrain vertices
- terrain triangles
- terrain heights
- terrain cell metadata

### Layer 2: Strategy Graph Layer

Responsibilities:

- movement
- pathfinding
- control points
- objectives
- combat entry points
- visibility

Granularity:

- lower density
- gameplay readability oriented

Primary data:

- `MapNode`
- node connections
- node ownership
- objective bindings

## Coordinate Model

### Short-Term Compatibility

Current code uses `WorldX / WorldY`. To avoid a large disruptive rename at the start:

- keep `WorldX / WorldY` temporarily in the first migration phase
- interpret them as `worldX / worldZ`
- do not use them as screen-space or XY-ground coordinates anymore

### Final Model

Move to:

- `Vector3 WorldPosition` on `MapNode`
- `Vector3 WorldPosition` on `TerrainCell`
- `GridX / GridZ` for strategy graph coordinates
- `CellX / CellZ` for terrain cell coordinates

## Data Model

### TerrainHeightField

Purpose:

- represent the dense continuous terrain sampling data used to build the mesh

Suggested fields:

- `int VertexWidth`
- `int VertexHeight`
- `float CellSize`
- `float[,] Heights`
- `float SeaLevel`

Notes:

- height data should be defined per vertex, not per terrain cell
- mesh generation will derive quads and triangles from adjacent vertices

### TerrainCell

Current class is too thin for 3D use. Extend it with:

- `int CellX`
- `int CellZ`
- `Vector3 WorldPosition`
- `float Height`
- `float Slope`
- `TerrainType Terrain`
- `string StrategyNodeId`

Responsibilities:

- represent the dense terrain unit
- store terrain category and terrain-to-node binding

### MapNode

Keep this as the strategy-layer node and extend it toward:

- `int GridX`
- `int GridZ`
- `Vector3 WorldPosition`
- `TerrainType Terrain`
- `List<string> Connections`
- `string ObjectiveId`

Responsibilities:

- own strategy logic only
- never act as a mesh vertex
- never act as a terrain cell

## Proposed Systems

### TerrainHeightGenerator

Input:

- map size
- cells per strategy node
- random seed
- noise parameters
- sea level
- optional falloff / macro-shape parameters

Output:

- `TerrainHeightField`

Responsibilities:

- generate continuous height values
- support future extension for multiple octaves, erosion, or macro masks

### TerrainClassifier

Input:

- `TerrainHeightField`

Output:

- `List<TerrainCell>`
- optional lookup dictionary by cell coordinate

Responsibilities:

- convert height samples into terrain cells
- determine `Sea / Coastal / Land / Mountain` style categories
- compute slope and other derived metrics

### StrategyGraphBuilder

Input:

- terrain cells
- aggregation settings such as `terrainCellsPerNode`

Output:

- `List<MapNode>`
- connection graph

Responsibilities:

- aggregate high-density terrain cells into sparse strategy nodes
- determine each node's dominant terrain type
- assign node world position at local surface center
- build valid node connections

### TerrainMeshBuilder

Input:

- `TerrainHeightField`
- terrain classification data

Output:

- Unity `Mesh`
- optional `MeshCollider` source mesh

Responsibilities:

- build vertices, triangles, normals, UVs
- support vertex colors or material assignment by terrain type
- remain independent from strategy logic

### MapRaycastResolver

Input:

- world-space hit point from raycast

Output:

- terrain cell
- strategy node

Responsibilities:

- map from mesh surface interaction back into gameplay data
- provide stable lookup API for commander input and UI

## Generation Pipeline

1. Read generation config.
2. Build dense `TerrainHeightField`.
3. Classify terrain cells from the height field.
4. Aggregate terrain cells into strategy nodes.
5. Build node connections.
6. Build the 3D terrain mesh.
7. Assign mesh collider.
8. Place objectives, forts, units, and markers at strategy node world positions.
9. Frame camera based on terrain bounds, not node count alone.

## Interaction Flow

1. Player clicks on terrain.
2. Raycast hits terrain mesh collider.
3. `MapRaycastResolver` converts hit point to terrain cell coordinate.
4. Terrain cell resolves to `StrategyNodeId`.
5. Game systems operate on `MapNode`.

This keeps input tied to the 3D scene without moving gameplay rules onto triangles.

## File-Level Refactor Plan

### Existing Files To Modify

`Assets/_Project/Scripts/Systems/MapManager.cs`

- reduce responsibility to orchestration
- stop owning long-term tile/sprite rendering logic
- call height, classification, graph, mesh, and projection steps

`Assets/_Project/Scripts/Core/MapNode.cs`

- introduce explicit distinction between logical grid coordinates and world position
- move toward `Vector3 WorldPosition`

`Assets/_Project/Scripts/Core/TerrainCell.cs`

- upgrade from 2D placeholder to dense terrain cell model
- add height and slope

`Assets/_Project/Scripts/Strategy/PlayerCommander.cs`

- replace current node lookup assumptions with raycast-based selection

`Assets/_Project/Scripts/UI/GameUIManager.cs`

- stop reconstructing node identity from raw transform position assumptions

`Assets/_Project/Scripts/Strategy/AnomalyFortress.cs`

- make spatial effects operate through world-space radius or terrain/node mapping

### New Files To Add

`Assets/_Project/Scripts/Core/TerrainHeightField.cs`

- data container for dense height samples

`Assets/_Project/Scripts/Systems/TerrainHeightGenerator.cs`

- terrain height generation

`Assets/_Project/Scripts/Systems/TerrainClassifier.cs`

- terrain cell creation and category assignment

`Assets/_Project/Scripts/Systems/StrategyGraphBuilder.cs`

- strategy node aggregation and connection generation

`Assets/_Project/Scripts/Systems/TerrainMeshBuilder.cs`

- mesh construction and material data setup

`Assets/_Project/Scripts/Systems/MapRaycastResolver.cs`

- hit-point-to-cell and hit-point-to-node mapping

`Assets/_Project/Scripts/Data/MapGenerationConfigSO.cs`

- ScriptableObject config for generation parameters

## Migration Strategy

### Phase 1: Structural Separation

- keep current content generation mostly intact
- extract height field and terrain cell generation into separate classes
- stop adding more rendering logic into `MapManager`

### Phase 2: 3D Terrain Rendering

- add mesh generation and mesh collider
- move camera and world placement to `XZ + Y-height`
- keep old fallback path behind a debug toggle

### Phase 3: Input and Gameplay Binding

- swap commander selection to raycast-to-node flow
- project units and objectives onto the terrain surface
- update UI lookup paths

### Phase 4: Cleanup

- remove tilemap as the main rendering path
- remove XY-ground assumptions
- rename remaining transitional `WorldY` semantics to `WorldPosition.z` where appropriate

## Acceptance Criteria

- terrain renders as a continuous 3D mesh
- `MapNode` count remains independent from terrain visual resolution
- units and markers sit on the terrain surface
- clicking the terrain reliably resolves to the correct strategy node
- pathfinding and combat still run only on the strategy graph
- camera framing uses actual terrain bounds
- old fallback rendering can be disabled without breaking map generation

## Non-Goals For First Pass

- full erosion simulation
- chunk streaming
- terrain LOD
- triangle-level pathfinding
- procedural foliage and decoration systems

## Immediate Recommendation

Implement the first production-quality version in this order:

1. add `TerrainHeightField`
2. upgrade `TerrainCell`
3. add `TerrainHeightGenerator`
4. add `TerrainClassifier`
5. add `TerrainMeshBuilder`
6. adapt `MapManager` to orchestrate the pipeline
7. add `MapRaycastResolver`
8. replace commander click lookup

This order minimizes breakage while moving the project from a 2D prototype model to a 3D surface model.
