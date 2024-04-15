class Grid:
    def __init__(self, radius: int):
        self.__radius = radius
        self.__partSize = radius * (radius + 1)
        self.__list = [None] * (self.__partSize * 3 + 1)

    def __index_function(self, x: int, y: int, z: int) -> int:
        if x >= 0 > y:
            return x * self.__radius + abs(y)
        elif y >= 0 > z:
            return self.__partSize + y * self.__radius + abs(z)
        elif z >= 0 > x:
            return 2 * self.__partSize + z * self.__radius + abs(x)
        return 0

    def get(self, x: int, y: int, z: int):
        return self.__list[self.__index_function(x, y, z)]

    def set(self, x: int, y: int, z: int, value):
        self.__list[self.__index_function(x, y, z)] = value
