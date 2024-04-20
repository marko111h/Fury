from scripts.game_client import GameClient
from scripts.grid import Grid
from scripts.bot_player import BotPlayer
from typing import List, Tuple
from scripts.tank import Tank


class Bot(BotPlayer):
    def __init__(self, id, name):
        super().__init__(id, name)
        self.__paths: List[List[Tuple[int, int]]] = []

    def find_path(self, tank: Tank, client: GameClient) -> List[Tuple[int, int]]:
        gridSize = client.get_grid().get_size()
        map = [float('inf')] * gridSize
        tankPos = tank.curr_position
        map[client.get_grid().index_function(tankPos[0], tankPos[1])] = 0
        basePos = None

        queue = [tankPos]
        while len(queue) > 0:
            currentPos = queue.pop(0)
            neighbors = [Grid.get_point_south(currentPos, -1), Grid.get_point_south_east(currentPos, -1),
                         Grid.get_point_south_west(currentPos, 1), Grid.get_point_south(currentPos, 1),
                         Grid.get_point_south_east(currentPos, 1), Grid.get_point_south_west(currentPos, -1)]
            for neighbor in neighbors:
                if neighbor[0] <= gridSize and neighbor[1] <= gridSize and client.get_grid().get(neighbor[0],
                                                                                                 neighbor[1]) is None:
                    if float('inf') > map[client.get_grid().index_function(neighbor[0], neighbor[1])] > 0:
                        queue.append(neighbor)
                    if map[client.get_grid().index_function(neighbor[0], neighbor[1])] + 1 < map[
                        client.get_grid().index_function(currentPos[0], currentPos[1])]:
                        map[client.get_grid().index_function(currentPos[0], currentPos[1])] = map[client.get_grid().index_function(
                                                                                                      neighbor[0], neighbor[1])] + 1
                    if neighbor in client.get_base():
                        basePos = neighbor
                        queue.clear()
                        break

        if basePos is None:
            return None

        path = []
        itr = basePos
        while map[client.get_grid().index_function(itr[0], itr[1])] != 0:
            path.append(itr)
            neighbors = [Grid.get_point_south(itr, -1), Grid.get_point_south_east(itr, -1),
                         Grid.get_point_south_west(itr, 1), Grid.get_point_south(itr, 1),
                         Grid.get_point_south_east(itr, 1), Grid.get_point_south_west(itr, -1)]
            for neighbor in neighbors:
                if map[client.get_grid().index_function(neighbor[0], neighbor[1])] < map[
                    client.get_grid().index_function(itr[0], itr[1])]:
                    itr = neighbor
                    break

        return path

    def is_clear(self, path: List[Tuple[int, int]], client: GameClient) -> bool:
        for point in path:
            if client.get_grid().get(point[0], point[1]) is not None:
                return False
        return True

    def add_tank(self, tank: Tank):
        self.tanks.append(tank)

    def play_turn(self, client, socket):
        turn_actions = []
        while len(self.__paths) < len(self.tanks):
            self.__paths.append(None)

        for i in range(len(self.tanks)):
            if self.__paths[i] is None or not self.is_clear(self.__paths[i], client):
                self.__paths[i] = self.find_path(self.tanks[i], client)

            if self.__paths[i] is not None:
                dist = min(self.tanks[i].get_speed_points(), len(self.__paths[i]))
                if dist == 0:
                    return turn_actions
                # temporarily commented until game is played on client
                # self.tanks[i].move(self.__paths[i][len(self.__paths[i]) - dist])
                turn_actions.append(GameClient.GameAction(GameClient.ActionType.MOVE,
                                                          self, self.tanks[i],
                                                          self.__paths[i][len(self.__paths[i]) - dist]))
                for j in range(dist):
                    self.__paths[i].pop()

        return turn_actions
