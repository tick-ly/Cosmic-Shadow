# Battlefield 2km Terrain Import Guide

Generated files:

- `Battlefield2km_Height_2049.r16`
- `Battlefield2km_HeightPreview_2049.png`
- `Battlefield2km_ZoneMap_2048.png`

Recommended Unity Terrain settings:

- Terrain Width: `2000`
- Terrain Length: `2000`
- Terrain Height: `220`
- Heightmap Resolution: `2049`
- Alphamap Resolution: `2048`
- Base Map Resolution: `2048`
- Detail Resolution: start with `1024`

RAW import settings:

- Depth: `16-bit`
- Byte Order: `Windows`
- Resolution: `2049`
- Flip Vertically: `Off`

If the imported terrain looks upside down, import again with `Flip Vertically` enabled.

Capture point coordinates in meters:

- A: `(360, 1520)`
- B: `(720, 1150)`
- C: `(1100, 1030)`
- D: `(1460, 820)`
- E: `(1500, 1280)`

Spawn anchors in meters:

- Southwest Spawn: `(240, 1640)`
- East Quarry Spawn: `(1590, 700)`

Suggested Terrain layer usage from the zone map:

- Blue corridor: river and lowland
- Dark green: ridge or orchard vegetation
- Gray: quarry rock and exposed ground
- Slate: town and hard surface zone
- Olive: open fields and mixed soil

Suggested next steps:

1. Import the RAW heightmap into a new Terrain.
2. Use the zone map as a Scene view reference or splat-paint guide.
3. Block out capture areas, roads, and cover modules first.
4. Keep the first playable version grayboxed before adding foliage.
