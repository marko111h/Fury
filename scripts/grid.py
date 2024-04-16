class Vec2:
    def __init__(self, q: int, r: int):
        self.q = q
        self.r = r

class Grid:
    def __init__(self, radius: int):
        self.__radius = radius
        self.__partSize = radius * (radius + 1)
        self.__list = [None] * (self.__partSize * 3 + 1)

    def __index_function(self, q: int, r: int) -> int:
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
        return self.__list[self.__index_function(q, r)]

    def set(self, q: int, r: int, value):
        self.__list[self.__index_function(q, r)] = value

    def get_size(self):
        return self.__radius

    @staticmethod
    def get_z(q: int, r: int):
        return -q - r

    @staticmethod
    def get_dist(a: Vec2, b: Vec2):
        return (abs(a.q - b.q) + abs(a.q + a.r - b.q - b.r) + abs(a.r - b.r)) / 2

    @staticmethod
    def get_point_south(a: Vec2, dist: int) -> Vec2:
        return Vec2(a.q, a.r + dist)

    @staticmethod
    def get_point_south_east(a: Vec2, dist: int) -> Vec2:
        return Vec2(a.q + dist, a.r)

    @staticmethod
    def get_point_south_west(a: Vec2, dist: int) -> Vec2:
        return Vec2(a.q - dist, a.r + dist)

    @staticmethod
    def is_reachable(self, a: Vec2, b: Vec2) -> bool:
        return True #TODO: Implement