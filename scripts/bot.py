from scripts.grid import Grid, Vec2
from scripts.player import Player
from typing import List, Tuple

class Tank: #Temp class
    def __init__(self):
        self.curr_position = Vec2(0, 0)
        self.speed_points = 2

    def get_curr_position(self):
        return self.curr_position

    def move(self, q: int, r: int):
        pass

    def get_speed_points(self):
        return self.speed_points


class GameClient: #Temp class
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
        self.__goals: List[Vec2] = [None] * len(self.vehicles)
        self.__paths: List[List[Vec2]] = [None] * len(self.vehicles)

    def find_path(self, tank: Tank, goal: Vec2) -> List[Vec2]:
        pass #TODO: Implement

    def is_clear(self, path: List[Vec2]) -> bool:
        for point in path:
            if self.__client.get_grid().get(point.q, point.r) is not None:
                return False
        return True

    def play_turn(self):
        for i in range(len(self.vehicles)):
            if self.__goals[i] is None or not self.is_clear(self.__paths[i]):
                self.__goals[i] = self.find_base(self.vehicles[i])
                self.__paths[i] = self.find_path(self.vehicles[i], self.__goals[i])

            if self.__paths[i] is not None:
                dist = min(self.vehicles[i].get_speed_points(), len(self.__paths[i]))
                self.vehicles[i].move(self.__paths[i][len(self.__paths[i]) - dist])
                for j in range(dist):
                    self.__paths[i].pop()


    def find_base(self, tank: Tank):
        pos = tank.get_curr_position()
        closest = None
        dist = float('inf')
        for base in self.__client.get_bases():
            if Grid.get_dist(pos, Vec2(base[0], base[1])) < dist:
                dist = Grid.get_dist(pos, Vec2(base[0], base[1]))
                closest = base

        return closest
