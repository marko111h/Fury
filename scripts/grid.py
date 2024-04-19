from typing import Tuple

class Grid:
    def __init__(self, radius: int):
        self.__radius = radius
        self.__partSize = radius * (radius + 1)
        self.__list = [None] * (self.__partSize * 3 + 1)

    def index_function(self, q: int, r: int) -> int:
        x: int = q
        y: int = r
        z: int = Grid.get_z(q, r)
        if x >= 0 > y:
            return x * self.__radius + abs(y)
        elif y >= 0 > z:
            return self.__partSize + y * self.__radius + abs(z)
        elif z >= 0 > x:
            return 2 * self.__partSize + z * self.__radius + abs(x)
        return 0

    def get(self, q: int, r: int):
        return self.__list[self.index_function(q, r)]

    def set(self, q: int, r: int, value):
        self.__list[self.index_function(q, r)] = value

    def get_size(self):
        return self.__radius

    @staticmethod
    def get_z(q: int, r: int):
        return -q - r

    @staticmethod
    def get_dist(a: Tuple[int, int], b: Tuple[int, int]):
        return (abs(a[0] - b[0]) + abs(a[0] + a[1] - b[0] - b[1]) + abs(a[1] - b[1])) / 2

    @staticmethod
    def get_point_south(a: Tuple[int, int], dist: int) -> Tuple[int, int]:
        return a[0], a[1] + dist

    @staticmethod
    def get_point_south_east(a: Tuple[int, int], dist: int) -> Tuple[int, int]:
        return a[0] + dist, a[1]

    @staticmethod
    def get_point_south_west(a: Tuple[int, int], dist: int) -> Tuple[int, int]:
        return a[0] - dist, a[1] + dist

    @staticmethod
    def is_reachable(self, a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        return True  # TODO: Implement
