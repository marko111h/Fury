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

    @staticmethod
    def get_z(q: int, r: int):
        return -q - r
