from __future__ import annotations

import math
import os
import struct
import zlib
from array import array
from pathlib import Path


MAP_SIZE_METERS = 2000.0
HEIGHTMAP_RESOLUTION = 2049
ZONEMAP_RESOLUTION = 2048
TERRAIN_HEIGHT_METERS = 220.0

OUTPUT_DIR = Path(r"D:\program\univers\UnityProject\Assets\_Project\Resources\Terrain\Battlefield2km")


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    if edge0 == edge1:
        return 0.0
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def gaussian(x: float, y: float, cx: float, cy: float, sx: float, sy: float, amp: float) -> float:
    dx = (x - cx) / sx
    dy = (y - cy) / sy
    return amp * math.exp(-(dx * dx + dy * dy) * 0.5)


def river_center_x(y: float) -> float:
    t = y / MAP_SIZE_METERS
    return 980.0 + 160.0 * math.sin(t * 2.7 * math.pi + 0.35) - 120.0 * math.cos(t * 1.35 * math.pi)


def road_distance(x: float, y: float, points: list[tuple[float, float]]) -> float:
    best = 1e9
    for i in range(len(points) - 1):
        ax, ay = points[i]
        bx, by = points[i + 1]
        abx = bx - ax
        aby = by - ay
        apx = x - ax
        apy = y - ay
        denom = abx * abx + aby * aby
        t = 0.0 if denom == 0.0 else clamp((apx * abx + apy * aby) / denom, 0.0, 1.0)
        qx = ax + abx * t
        qy = ay + aby * t
        best = min(best, math.hypot(x - qx, y - qy))
    return best


def point_distance(x: float, y: float, point: tuple[float, float]) -> float:
    return math.hypot(x - point[0], y - point[1])


CAPTURE_POINTS = {
    "A": (360.0, 1520.0),
    "B": (720.0, 1150.0),
    "C": (1100.0, 1030.0),
    "D": (1460.0, 820.0),
    "E": (1500.0, 1280.0),
}

SPAWNS = {
    "SW": (240.0, 1640.0),
    "EAST": (1590.0, 700.0),
}

VEHICLE_LANES = [
    [(240.0, 1640.0), (360.0, 1520.0), (720.0, 1150.0), (1100.0, 1030.0)],
    [(1590.0, 700.0), (1460.0, 820.0), (1100.0, 1030.0)],
    [(1460.0, 820.0), (1100.0, 1030.0), (1500.0, 1280.0)],
]

INFANTRY_LANES = [
    [(360.0, 1520.0), (520.0, 1370.0), (650.0, 1260.0), (720.0, 1150.0)],
    [(720.0, 1150.0), (820.0, 1080.0), (950.0, 1110.0), (1100.0, 1030.0)],
    [(1460.0, 820.0), (1360.0, 760.0), (1240.0, 860.0), (1100.0, 1030.0)],
    [(1100.0, 1030.0), (1240.0, 1130.0), (1360.0, 1210.0), (1500.0, 1280.0)],
]


def terrain_height_meters(x: float, y: float) -> float:
    base = 34.0
    base += 8.0 * math.sin(x / 210.0) * math.cos(y / 260.0)
    base += 6.0 * math.sin((x + y) / 330.0)
    base += 4.0 * math.cos((x - 0.55 * y) / 190.0)

    # North ridge and ridge shoulders.
    base += gaussian(x, y, 420.0, 1740.0, 280.0, 170.0, 42.0)
    base += gaussian(x, y, 760.0, 1680.0, 340.0, 210.0, 26.0)

    # Quarry rim and basin.
    quarry_cx, quarry_cy = 1540.0, 700.0
    qdx = (x - quarry_cx) / 250.0
    qdy = (y - quarry_cy) / 200.0
    quarry_r = math.sqrt(qdx * qdx + qdy * qdy)
    base -= 32.0 * math.exp(-(quarry_r * quarry_r) * 1.7)
    base += 18.0 * math.exp(-((quarry_r - 1.0) ** 2) / 0.06)

    # South farms remain flatter and lower.
    base -= gaussian(x, y, 400.0, 420.0, 440.0, 260.0, 10.0)

    # East orchard rolling uplift.
    base += gaussian(x, y, 1680.0, 420.0, 280.0, 220.0, 14.0)
    base += gaussian(x, y, 1760.0, 1450.0, 320.0, 280.0, 10.0)

    # Central town slight plateau.
    town_mask = math.exp(-(((x - 760.0) / 190.0) ** 2 + ((y - 980.0) / 170.0) ** 2) * 0.5)
    town_target = 44.0 + 2.2 * math.sin(x / 70.0) * math.cos(y / 65.0)
    base = lerp(base, town_target, 0.58 * town_mask)

    # Bridge hub should sit slightly above the lowland.
    base += gaussian(x, y, 1110.0, 1060.0, 170.0, 120.0, 9.0)

    # River trench and floodplain.
    rcx = river_center_x(y)
    river_dx = x - rcx
    base -= 38.0 * math.exp(-(river_dx * river_dx) / (2.0 * 58.0 * 58.0))
    base -= 12.0 * math.exp(-(river_dx * river_dx) / (2.0 * 150.0 * 150.0))

    # Shape the bridge crossing area so both banks are playable.
    bridge_mask = math.exp(-(((x - 1110.0) / 140.0) ** 2 + ((y - 1060.0) / 110.0) ** 2) * 0.5)
    bridge_target = 28.0 + 3.5 * math.cos(x / 60.0)
    base = lerp(base, bridge_target, 0.50 * bridge_mask)

    # Smooth road beds a bit so vehicles have a readable route.
    for lane in VEHICLE_LANES:
        dist = road_distance(x, y, lane)
        flatten = math.exp(-(dist * dist) / (2.0 * 30.0 * 30.0))
        road_target = base * 0.35 + 31.0
        base = lerp(base, road_target, 0.18 * flatten)

    # Spawn zones need safe slopes.
    base = lerp(base, 38.0, 0.45 * math.exp(-(point_distance(x, y, SPAWNS["SW"]) ** 2) / (2.0 * 120.0 * 120.0)))
    base = lerp(base, 40.0, 0.45 * math.exp(-(point_distance(x, y, SPAWNS["EAST"]) ** 2) / (2.0 * 120.0 * 120.0)))

    # Keep map edges naturally enclosing.
    edge = min(x, y, MAP_SIZE_METERS - x, MAP_SIZE_METERS - y)
    edge_lift = 1.0 - smoothstep(40.0, 220.0, edge)
    base += edge_lift * 12.0

    return clamp(base, 6.0, 148.0)


def normalize_height(height_meters: float) -> float:
    return clamp(height_meters / TERRAIN_HEIGHT_METERS, 0.0, 1.0)


def classify_zone(x: float, y: float) -> tuple[int, int, int]:
    rcx = river_center_x(y)
    if abs(x - rcx) < 85.0:
        return (70, 119, 138)
    if x < 840.0 and y > 1450.0:
        return (62, 86, 63)
    if x > 1220.0 and y < 980.0:
        return (83, 88, 92)
    if x < 760.0 and y < 760.0:
        return (77, 97, 60)
    if x > 1250.0 and y > 1200.0:
        return (74, 98, 61)
    if 560.0 < x < 980.0 and 760.0 < y < 1180.0:
        return (88, 97, 99)
    return (64, 78, 76)


def png_chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path: Path, width: int, height: int, rows: list[bytes], color_type: int) -> None:
    bit_depth = 8
    ihdr = struct.pack("!IIBBBBB", width, height, bit_depth, color_type, 0, 0, 0)
    raw = b"".join(b"\x00" + row for row in rows)
    payload = zlib.compress(raw, level=9)
    with path.open("wb") as fp:
        fp.write(b"\x89PNG\r\n\x1a\n")
        fp.write(png_chunk(b"IHDR", ihdr))
        fp.write(png_chunk(b"IDAT", payload))
        fp.write(png_chunk(b"IEND", b""))


def put_pixel_rgb(buffer: bytearray, width: int, x: int, y: int, color: tuple[int, int, int]) -> None:
    if 0 <= x < width:
        offset = x * 3
        buffer[offset:offset + 3] = bytes(color)


def draw_disc(rows: list[bytearray], width: int, height: int, cx: int, cy: int, radius: int, color: tuple[int, int, int]) -> None:
    y0 = max(0, cy - radius)
    y1 = min(height - 1, cy + radius)
    r2 = radius * radius
    for y in range(y0, y1 + 1):
        dy = y - cy
        dx_limit = int(math.sqrt(max(0, r2 - dy * dy)))
        row = rows[y]
        for x in range(max(0, cx - dx_limit), min(width - 1, cx + dx_limit) + 1):
            put_pixel_rgb(row, width, x, y, color)


def draw_line(rows: list[bytearray], width: int, height: int, points: list[tuple[float, float]], thickness: int, color: tuple[int, int, int], resolution: int) -> None:
    for i in range(len(points) - 1):
        ax, ay = points[i]
        bx, by = points[i + 1]
        length = max(1, int(math.hypot(bx - ax, by - ay) / 6.0))
        for step in range(length + 1):
            t = step / length
            mx = lerp(ax, bx, t)
            my = lerp(ay, by, t)
            px = int(mx / MAP_SIZE_METERS * (resolution - 1))
            py = int((MAP_SIZE_METERS - my) / MAP_SIZE_METERS * (resolution - 1))
            draw_disc(rows, width, height, px, py, thickness, color)


def generate_heightmap() -> tuple[list[int], list[bytes]]:
    raw_values = array("H")
    preview_rows: list[bytes] = []
    for py in range(HEIGHTMAP_RESOLUTION):
        y = (py / (HEIGHTMAP_RESOLUTION - 1)) * MAP_SIZE_METERS
        preview_row = bytearray(HEIGHTMAP_RESOLUTION)
        for px in range(HEIGHTMAP_RESOLUTION):
            x = (px / (HEIGHTMAP_RESOLUTION - 1)) * MAP_SIZE_METERS
            normalized = normalize_height(terrain_height_meters(x, y))
            raw_values.append(int(round(normalized * 65535.0)))
            preview_row[px] = int(round(normalized * 255.0))
        preview_rows.append(bytes(preview_row))
    return raw_values, preview_rows


def generate_zone_map() -> list[bytes]:
    rows: list[bytearray] = []
    for py in range(ZONEMAP_RESOLUTION):
        y = MAP_SIZE_METERS - (py / (ZONEMAP_RESOLUTION - 1)) * MAP_SIZE_METERS
        row = bytearray(ZONEMAP_RESOLUTION * 3)
        for px in range(ZONEMAP_RESOLUTION):
            x = (px / (ZONEMAP_RESOLUTION - 1)) * MAP_SIZE_METERS
            row[px * 3:px * 3 + 3] = bytes(classify_zone(x, y))
        rows.append(row)

    for lane in VEHICLE_LANES:
        draw_line(rows, ZONEMAP_RESOLUTION, ZONEMAP_RESOLUTION, lane, 8, (218, 179, 93), ZONEMAP_RESOLUTION)
    for lane in INFANTRY_LANES:
        draw_line(rows, ZONEMAP_RESOLUTION, ZONEMAP_RESOLUTION, lane, 5, (143, 227, 136), ZONEMAP_RESOLUTION)

    for point in CAPTURE_POINTS.values():
        px = int(point[0] / MAP_SIZE_METERS * (ZONEMAP_RESOLUTION - 1))
        py = int((MAP_SIZE_METERS - point[1]) / MAP_SIZE_METERS * (ZONEMAP_RESOLUTION - 1))
        draw_disc(rows, ZONEMAP_RESOLUTION, ZONEMAP_RESOLUTION, px, py, 24, (230, 236, 207))
        draw_disc(rows, ZONEMAP_RESOLUTION, ZONEMAP_RESOLUTION, px, py, 16, (194, 165, 84))

    spawn_colors = {"SW": (86, 143, 208), "EAST": (184, 110, 82)}
    for key, point in SPAWNS.items():
        px = int(point[0] / MAP_SIZE_METERS * (ZONEMAP_RESOLUTION - 1))
        py = int((MAP_SIZE_METERS - point[1]) / MAP_SIZE_METERS * (ZONEMAP_RESOLUTION - 1))
        draw_disc(rows, ZONEMAP_RESOLUTION, ZONEMAP_RESOLUTION, px, py, 28, spawn_colors[key])

    return [bytes(row) for row in rows]


def write_raw_heightmap(path: Path, values: array) -> None:
    if values.itemsize != 2:
        raise ValueError("Expected 16-bit array.")
    if os.name != "nt":
        values.byteswap()
    with path.open("wb") as fp:
        values.tofile(fp)


def write_import_guide(path: Path) -> None:
    content = f"""# Battlefield 2km Terrain Import Guide

Generated files:

- `Battlefield2km_Height_2049.r16`
- `Battlefield2km_HeightPreview_2049.png`
- `Battlefield2km_ZoneMap_2048.png`

Recommended Unity Terrain settings:

- Terrain Width: `2000`
- Terrain Length: `2000`
- Terrain Height: `{int(TERRAIN_HEIGHT_METERS)}`
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
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_values, preview_rows = generate_heightmap()
    zone_rows = generate_zone_map()

    write_raw_heightmap(OUTPUT_DIR / "Battlefield2km_Height_2049.r16", raw_values)
    write_png(OUTPUT_DIR / "Battlefield2km_HeightPreview_2049.png", HEIGHTMAP_RESOLUTION, HEIGHTMAP_RESOLUTION, preview_rows, color_type=0)
    write_png(OUTPUT_DIR / "Battlefield2km_ZoneMap_2048.png", ZONEMAP_RESOLUTION, ZONEMAP_RESOLUTION, zone_rows, color_type=2)
    write_import_guide(OUTPUT_DIR / "Battlefield2km_ImportGuide.md")

    print("Generated terrain assets:")
    for name in [
        "Battlefield2km_Height_2049.r16",
        "Battlefield2km_HeightPreview_2049.png",
        "Battlefield2km_ZoneMap_2048.png",
        "Battlefield2km_ImportGuide.md",
    ]:
        print(f"- {OUTPUT_DIR / name}")


if __name__ == "__main__":
    main()
