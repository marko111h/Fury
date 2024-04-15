from grid import Grid
from player import Player
from typing import List, Tuple


class GameClient:
    """ Class is responsible to provide game logic and
        keep up to date the state of the game for client
    """

    def __init__(self):
        self.__radius: int  # alias from server: size
        self.__grid: Grid
        self.__players: List[Player]
        self.__players_capturing_base: List[Player] = []
        self.__base: List[Tuple[int, int]] = [(0, 0)]

    def __update__(self):
        pass
