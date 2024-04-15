from grid import Grid
from player import Player
from typing import List, Tuple


class GameClient:
    """ Class is responsible to provide game logic and
        keep up to date the state of the game for client
    """

    def __init__(self):
        self.radius: int  # alias from server: size
        self.grid: Grid
        self.players: List[Player]
        self.players_capturing_base: List[Player] = []
        self.base: List[Tuple[int, int]] = [(0, 0)]

    def __update__(self):
        pass
