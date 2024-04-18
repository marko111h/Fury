from scripts.grid import Grid
from scripts.player import Player
from typing import List, Tuple


class Tank:  # Temp class
    def __init__(self):
        self.curr_position = 0, 0
        self.speed_points = 2

    def get_curr_position(self):
        return self.curr_position

    def move(self, q: int, r: int):
        pass

    def get_speed_points(self):
        return self.speed_points


class GameClient:  # Temp class
    def __init__(self):
        self.__base: List[Tuple[int, int]] = []
        self.__grid: Grid = Grid(5)

    def get_bases(self):
        return self.__base

    def get_grid(self):
        return self.__grid


class Bot(Player):
    def __init__(self, id, name, grid: Grid, game: GameClient):
        super().__init__(id, name)
        self.__client = game
        self.__paths: List[List[Tuple[int, int]]] = [None] * len(self.vehicles)

    def find_path(self, tank: Tank) -> List[Tuple[int, int]]:
        gridSize = self.__client.get_grid().get_size()
        map = [float('inf')] * gridSize * (gridSize + 1)
        tankPos = tank.curr_position
        map[self.__client.get_grid().index_function(tankPos[0], tankPos[1])] = 0
        basePos = None

        queue = [tankPos]
        while len(queue) > 0:
            currentPos = queue.pop(0)
            neighbors = [Grid.get_point_south(currentPos, -1), Grid.get_point_south_east(currentPos, -1),
                         Grid.get_point_south_west(currentPos, 1), Grid.get_point_south(currentPos, 1),
                         Grid.get_point_south_east(currentPos, 1), Grid.get_point_south_west(currentPos, -1)]
            for neighbor in neighbors:
                if neighbor[0] <= gridSize and neighbor[1] <= gridSize and self.__client.get_grid().get(neighbor[0], neighbor[1]) is None:
                    if float('inf') > map[self.__client.get_grid().index_function(neighbor[0], neighbor[1])] > 0:
                        queue.append(neighbor)
                    if map[self.__client.get_grid().index_function(neighbor[0], neighbor[1])] + 1 > map[
                        self.__client.get_grid().index_function(currentPos[0], currentPos[1])]:
                        map[self.__client.get_grid().index_function(currentPos[0], currentPos[1])] = map[self.__client.get_grid().index_function(neighbor[0], neighbor[1])] + 1
                    if neighbor in self.__client.get_bases():
                        basePos = neighbor
                        queue.clear()
                        break

        if basePos is None:
            return None

        path = []
        itr = basePos
        while map[self.__client.get_grid().index_function(itr[0], itr[1])] == 0:
            path.append(itr)
            neighbors = [Grid.get_point_south(itr, -1), Grid.get_point_south_east(itr, -1),
                         Grid.get_point_south_west(itr, 1), Grid.get_point_south(itr, 1),
                         Grid.get_point_south_east(itr, 1), Grid.get_point_south_west(itr, -1)]
            for neighbor in neighbors:
                if map[self.__client.get_grid().index_function(neighbor[0], neighbor[1])] < map[
                    self.__client.get_grid().index_function(itr[0], itr[1])]:
                    itr = neighbor
                    break

        return path

    def is_clear(self, path: List[Tuple[int, int]]) -> bool:
        for point in path:
            if self.__client.get_grid().get(point[0], point[1]) is not None:
                return False
        return True

    def play_turn(self):
        for i in range(len(self.vehicles)):
            if self.__paths[i] is None or not self.is_clear(self.__paths[i]):
                self.__paths[i] = self.find_path(self.vehicles[i])

            if self.__paths[i] is not None:
                dist = min(self.vehicles[i].get_speed_points(), len(self.__paths[i]))
                self.vehicles[i].move(self.__paths[i][len(self.__paths[i]) - dist])
                for j in range(dist):
                    self.__paths[i].pop()
