# -*- coding: utf-8 -*-
"""
宇宙之影 - 战场地图生成系统
使用噪声算法生成真实战场地图
"""

import random
import math
from typing import List, Tuple, Dict, Optional

# 简单噪声算法实现（无需外部依赖）
class SimplexNoise:
    """简化版Simplex噪声"""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.perm = self._generate_perm()

    def _generate_perm(self) -> List[int]:
        random.seed(self.seed)
        p = list(range(256))
        random.shuffle(p)
        return p * 2

    def _fade(self, t: float) -> float:
        return t * t * t * (t * (t * 6 - 15) + 10)

    def _lerp(self, a: float, b: float, t: float) -> float:
        return a + t * (b - a)

    def _grad(self, hash: int, x: float, y: float) -> float:
        h = hash & 3
        u = x if h < 2 else y
        v = y if h < 2 else x
        return (u if h & 1 == 0 else -u) + (v if h & 2 == 0 else -v)

    def noise2d(self, x: float, y: float) -> float:
        """2D噪声"""
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255

        x -= math.floor(x)
        y -= math.floor(y)

        u = self._fade(x)
        v = self._fade(y)

        A = self.perm[X] + Y
        B = self.perm[X + 1] + Y

        return self._lerp(
            self._lerp(self._grad(self.perm[A], x, y), self._grad(self.perm[B], x - 1, y), u),
            self._lerp(self._grad(self.perm[A + 1], x, y - 1), self._grad(self.perm[B + 1], x - 1, y - 1), u),
            v
        )

    def octave_noise(self, x: float, y: float, octaves: int = 4, persistence: float = 0.5) -> float:
        """八度噪声"""
        total = 0
        frequency = 1
        amplitude = 1
        max_value = 0

        for _ in range(octaves):
            total += self.noise2d(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2

        return total / max_value


class TerrainTile:
    """地形瓦片"""
    PLAINS = 0
    WATER = 1
    MOUNTAIN = 2
    FOREST = 3
    SAND = 4
    SNOW = 5
    URBAN = 6
    SWAMP = 7

    SYMBOLS = {
        PLAINS: ('.', '平原', 30),
        WATER: ('~', '水域', 0),
        MOUNTAIN: ('^', '山地', 80),
        FOREST: ('#', '森林', 50),
        SAND: (',', '沙漠', 10),
        SNOW: ('*', '雪地', 60),
        URBAN: ('O', '城市', 40),
        SWAMP: (';', '沼泽', 20),
    }

    @classmethod
    def from_height(cls, height: float, moisture: float) -> int:
        """根据高度和湿度确定地形"""
        if height < 0.3:
            return cls.WATER
        elif height > 0.75:
            if moisture > 0.5:
                return cls.SNOW
            return cls.MOUNTAIN
        elif height > 0.6:
            return cls.MOUNTAIN
        elif height > 0.5:
            if moisture > 0.6:
                return cls.FOREST
            elif moisture > 0.3:
                return cls.PLAINS
            return cls.SAND
        elif height > 0.4:
            if moisture > 0.7:
                return cls.SWAMP
            elif moisture > 0.4:
                return cls.FOREST
            return cls.PLAINS
        else:
            return cls.WATER


class BattlefieldMap:
    """战场地图"""

    def __init__(self, width: int = 60, height: int = 30, seed: int = None):
        self.width = width
        self.height = height
        self.seed = seed or random.randint(1, 10000)
        self.tiles: List[List[int]] = []
        self.height_map: List[List[float]] = []
        self.moisture_map: List[List[float]] = []
        self.units: Dict[str, Tuple[int, int]] = {}  # 单位位置
        self.markers: Dict[str, str] = {}  # 特殊标记

        self._generate()

    def _generate(self):
        """生成地图"""
        # 创建噪声生成器
        height_noise = SimplexNoise(seed=self.seed)
        moisture_noise = SimplexNoise(seed=self.seed + 1000)

        scale = 0.08

        for y in range(self.height):
            row = []
            height_row = []
            moisture_row = []

            for x in range(self.width):
                # 生成高度
                nx = x * scale
                ny = y * scale
                height = height_noise.octave_noise(nx, ny, octaves=4, persistence=0.5)
                height = (height + 1) / 2  # 归一化到0-1

                # 生成湿度
                moisture = moisture_noise.octave_noise(nx * 0.5, ny * 0.5, octaves=3, persistence=0.6)
                moisture = (moisture + 1) / 2

                # 添加一些随机变化
                height += random.uniform(-0.05, 0.05)
                height = max(0, min(1, height))

                # 确定地形类型
                tile = TerrainTile.from_height(height, moisture)

                row.append(tile)
                height_row.append(height)
                moisture_row.append(moisture)

            self.tiles.append(row)
            self.height_map.append(height_row)
            self.moisture_map.append(moisture_row)

    def place_unit(self, name: str, x: int, y: int):
        """放置单位"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.units[name] = (x, y)

    def add_marker(self, name: str, x: int, y: int):
        """添加标记"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.markers[name] = (x, y)

    def get_tile_at(self, x: int, y: int) -> Optional[int]:
        """获取指定位置的地形"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def get_height_at(self, x: int, y: int) -> float:
        """获取指定位置的高度"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.height_map[y][x]
        return 0

    def is_passable(self, x: int, y: int, is_legion: bool = False) -> bool:
        """检查是否可通行"""
        tile = self.get_tile_at(x, y)
        if tile is None:
            return False

        # 水域不可通行
        if tile == TerrainTile.WATER:
            return False

        # 军团不可进入沼泽和森林
        if is_legion and tile in [TerrainTile.SWAMP, TerrainTile.FOREST]:
            return False

        return True

    def get_defense_bonus(self, x: int, y: int) -> int:
        """获取防御加成"""
        tile = self.get_tile_at(x, y)
        if tile is None:
            return 0

        bonuses = {
            TerrainTile.PLAINS: 0,
            TerrainTile.WATER: 0,
            TerrainTile.MOUNTAIN: 25,
            TerrainTile.FOREST: 15,
            TerrainTile.SAND: 5,
            TerrainTile.SNOW: 10,
            TerrainTile.URBAN: 20,
            TerrainTile.SWAMP: 20,
        }
        return bonuses.get(tile, 0)

    def get_cover_bonus(self, x: int, y: int) -> float:
        """获取掩体加成"""
        tile = self.get_tile_at(x, y)
        if tile is None:
            return 0

        covers = {
            TerrainTile.PLAINS: 0.1,
            TerrainTile.WATER: 0.0,
            TerrainTile.MOUNTAIN: 0.5,
            TerrainTile.FOREST: 0.6,
            TerrainTile.SAND: 0.05,
            TerrainTile.SNOW: 0.3,
            TerrainTile.URBAN: 0.7,
            TerrainTile.SWAMP: 0.4,
        }
        return covers.get(tile, 0)

    def find_path(self, start: Tuple[int, int], end: Tuple[int, int], is_legion: bool = False) -> List[Tuple[int, int]]:
        """简单路径查找"""
        x1, y1 = start
        x2, y2 = end
        path = [(x1, y1)]

        while (x1, y1) != (x2, y2):
            if x1 < x2:
                x1 += 1
            elif x1 > x2:
                x1 -= 1

            if y1 < y2:
                y1 += 1
            elif y1 > y2:
                y1 -= 1

            if self.is_passable(x1, y1, is_legion):
                path.append((x1, y1))

        return path

    def render(self) -> str:
        """渲染地图为ASCII字符串"""
        lines = []

        # 顶部边框
        lines.append("+" + "-" * self.width + "+")

        for y in range(self.height):
            row = "|"
            for x in range(self.width):
                # 检查是否有单位
                for unit_name, (ux, uy) in self.units.items():
                    if ux == x and uy == y:
                        row += "\033[91m" + unit_name[0] + "\033[0m"  # 红色标记单位
                        break
                else:
                    # 检查是否有标记
                    for marker_name, (mx, my) in self.markers.items():
                        if mx == x and my == y:
                            row += "\033[93m" + "X" + "\033[0m"  # 黄色标记
                            break
                    else:
                        # 显示地形
                        tile = self.tiles[y][x]
                        symbol = TerrainTile.SYMBOLS[tile][0]

                        # 高度染色
                        height = self.height_map[y][x]
                        if tile == TerrainTile.PLAINS:
                            if height > 0.55:
                                symbol = "'"  # 高地草原
                            elif height < 0.42:
                                symbol = "."  # 低地草原

                        row += symbol

            row += "|"
            lines.append(row)

        # 底部边框
        lines.append("+" + "-" * self.width + "+")

        return "\n".join(lines)

    def render_fancy(self) -> str:
        """渲染带颜色的地图"""
        lines = []

        # 图例
        lines.append("\n[战场地图] " + f"种子: {self.seed}")
        lines.append("=" * (self.width + 2))
        lines.append("图例: .平原 ~水 ^山 #林 ,沙 *雪 O城 ;沼")

        for y in range(self.height):
            row = ""
            for x in range(self.width):
                # 检查是否有单位
                unit_char = None
                for unit_name, (ux, uy) in self.units.items():
                    if ux == x and uy == y:
                        unit_char = f"[1m{unit_name[0]:1}[22m"
                        break

                if unit_char:
                    row += f"\033[91m{unit_char}\033[0m"  # 红色单位
                else:
                    # 检查标记
                    marker_found = False
                    for marker_name, (mx, my) in self.markers.items():
                        if mx == x and my == y:
                            row += "\033[93m!\033[0m"
                            marker_found = True
                            break

                    if not marker_found:
                        tile = self.tiles[y][x]
                        symbol = TerrainTile.SYMBOLS[tile][0]

                        # 地形颜色
                        colors = {
                            TerrainTile.WATER: "\033[34m",      # 蓝色
                            TerrainTile.MOUNTAIN: "\033[90m",   # 灰色
                            TerrainTile.FOREST: "\033[32m",    # 绿色
                            TerrainTile.SAND: "\033[33m",      # 黄色
                            TerrainTile.SNOW: "\033[97m",      # 白色
                            TerrainTile.URBAN: "\033[90m",     # 深灰
                            TerrainTile.SWAMP: "\033[36m",     # 青色
                        }

                        color = colors.get(tile, "\033[0m")
                        row += f"{color}{symbol}\033[0m"

            lines.append(row)

        lines.append("=" * (self.width + 2))

        # 单位位置信息
        if self.units:
            lines.append("\n[单位部署]")
            for name, (x, y) in self.units.items():
                tile = self.get_tile_at(x, y)
                terrain_name = TerrainTile.SYMBOLS[tile][1]
                defense = self.get_defense_bonus(x, y)
                cover = self.get_cover_bonus(x, y)
                lines.append(f"  {name}: ({x},{y}) {terrain_name} 防御+{defense}% 掩体{cover:.0%}")

        return "\n".join(lines)


class HistoricBattlefieldGenerator:
    """历史战役地图生成器"""

    @staticmethod
    def generate_stalingrad(width: int = 60, height: int = 30) -> BattlefieldMap:
        """斯大林格勒风格 - 城市废墟战"""
        battle_map = BattlefieldMap(width, height, seed=1942)

        # 清理城市区域（中间区域变成城市）
        center_x = width // 2
        for y in range(height // 3, 2 * height // 3):
            for x in range(center_x - 5, center_x + 5):
                if 0 <= x < width and 0 <= y < height:
                    battle_map.tiles[y][x] = TerrainTile.URBAN

        # 伏尔加河（左边缘）
        for y in range(height):
            for x in range(3):
                if 0 <= x < width:
                    battle_map.tiles[y][x] = TerrainTile.WATER

        # 放置单位
        battle_map.place_unit("苏军", 5, height // 2)
        battle_map.place_unit("德军", width - 8, height // 2)
        battle_map.add_marker("火车站", center_x, height // 2)

        return battle_map

    @staticmethod
    def generate_normandy(width: int = 60, height: int = 30) -> BattlefieldMap:
        """诺曼底风格 - 登陆战"""
        battle_map = BattlefieldMap(width, height, seed=1944)

        # 沙滩（下半部分）
        for y in range(2 * height // 3, height):
            for x in range(width):
                if 0 <= y < height:
                    battle_map.tiles[y][x] = TerrainTile.SAND

        # 内陆变成草地
        for y in range(height // 3, 2 * height // 3):
            for x in range(width):
                if battle_map.tiles[y][x] == TerrainTile.PLAINS:
                    battle_map.tiles[y][x] = TerrainTile.FOREST

        # 放置单位
        battle_map.place_unit("盟军", 5, height - 5)
        battle_map.place_unit("德军", width - 8, height // 3)
        battle_map.add_marker("海滩", width // 4, height - 3)
        battle_map.add_marker("桥头堡", width // 4, 2 * height // 3)

        return battle_map

    @staticmethod
    def generate_sparta(width: int = 60, height: int = 30) -> BattlefieldMap:
        """温泉关风格 - 隘口防守战"""
        battle_map = BattlefieldMap(width, height, seed=-480)

        # 中间通道（狭窄通道）
        center_y = height // 2
        for y in range(center_y - 3, center_y + 3):
            for x in range(width // 4, 3 * width // 4):
                battle_map.tiles[y][x] = TerrainTile.PLAINS

        # 两侧变成山地
        for y in range(height):
            for x in range(width):
                if battle_map.tiles[y][x] == TerrainTile.PLAINS:
                    battle_map.tiles[y][x] = TerrainTile.MOUNTAIN

        # 放置单位
        battle_map.place_unit("斯巴达", width // 2, center_y)
        battle_map.place_unit("波斯", width - 5, center_y)
        battle_map.add_marker("隘口", width // 2, center_y)

        return battle_map

    @staticmethod
    def generate_random(width: int = 60, height: int = 30, seed: int = None) -> BattlefieldMap:
        """随机战场"""
        battle_map = BattlefieldMap(width, height, seed=seed)

        # 随机放置一两个单位
        import time
        battle_map.place_unit("蓝军", random.randint(5, 15), random.randint(5, height - 5))
        battle_map.place_unit("红军", random.randint(width - 15, width - 5), random.randint(5, height - 5))

        return battle_map


def demo_battlefield_map():
    """演示战场地图生成"""
    print("\n" + "=" * 70)
    print("[宇宙之影] 战场地图生成系统")
    print("=" * 70)

    # 1. 随机生成
    print("\n[1] 随机战场地图")
    print("-" * 70)
    random_map = HistoricBattlefieldGenerator.generate_random(50, 20)
    print(random_map.render_fancy())

    # 2. 斯大林格勒风格
    print("\n[2] 斯大林格勒风格（城市废墟战）")
    print("-" * 70)
    stalingrad = HistoricBattlefieldGenerator.generate_stalingrad(50, 20)
    print(stalingrad.render_fancy())

    # 3. 诺曼底风格
    print("\n[3] 诺曼底风格（登陆战）")
    print("-" * 70)
    normandy = HistoricBattlefieldGenerator.generate_normandy(50, 20)
    print(normandy.render_fancy())

    # 4. 温泉关风格
    print("\n[4] 温泉关风格（隘口防守）")
    print("-" * 70)
    sparta = HistoricBattlefieldGenerator.generate_sparta(50, 20)
    print(sparta.render_fancy())

    # 5. 地形信息
    print("\n[5] 地形详细分析")
    print("-" * 70)

    # 检查随机地图的某点
    test_x, test_y = 25, 10
    tile = random_map.get_tile_at(test_x, test_y)
    terrain_name = TerrainTile.SYMBOLS[tile][1]
    height = random_map.get_height_at(test_x, test_y)
    defense = random_map.get_defense_bonus(test_x, test_y)
    cover = random_map.get_cover_bonus(test_x, test_y)

    print(f"  位置 ({test_x}, {test_y}):")
    print(f"    地形: {terrain_name}")
    print(f"    高度: {height:.2f}")
    print(f"    防御加成: +{defense}%")
    print(f"    掩体效果: {cover:.0%}")

    # 路径测试
    print("\n[6] 路径测试")
    print("-" * 70)
    start = (5, 10)
    end = (45, 10)
    path = random_map.find_path(start, end)
    print(f"  从 {start} 到 {end}")
    print(f"  路径长度: {len(path)} 步")
    print(f"  路径: {path[:5]}...{path[-5:]}")

    print("\n" + "=" * 70)
    print("[地图系统演示完成]")
    print("=" * 70)


if __name__ == "__main__":
    demo_battlefield_map()
