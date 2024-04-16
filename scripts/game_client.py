from grid import Grid
from player import Player
from typing import List, Tuple, Optional, Dict, Union
import json
import socket
from enum import Enum


class GameClient:
    """ Class is responsible to provide game logic and
        keep up to date the state of the game for client
    """
    server_address = ("wgforge-srv.wargaming.net", 443)

    class Result(Enum):
        OKEY = 0
        BAD_COMMAND = 1
        ACCESS_DENIED = 2
        INAPPROPRIATE_GAME_STATE = 3
        TIMEOUT = 4
        INTERNAL_SERVER_ERROR = 500

    def __init__(self, player: Player):
        self.__grid: Grid
        self.__players: List[Player] = [player]  # stored in order of playing turns
        self.__players_capturing_base: List[Player] = []
        self.__base: List[Tuple[int, int]]
        self.name = None
        self.rounds = 15

    def __update__(self):
        pass

    @classmethod
    def login(cls, name: str, password: Optional[str] = None,
              game: Optional[str] = None, num_turns: Optional[int] = None,
              num_players: Optional[int] = None, is_observer: Optional[bool] = None,
              is_full: Optional[bool] = None) -> Optional['GameClient']:
        # copies dictionary of names and values
        # for all local variables (in our case parameters)
        params = locals().copy()
        # because it is classmethod we need to remove first parameter
        params.pop("cls")
        # removes every None from calls like: login("Boris", password = None)
        filtered_params = {key: value for key, value in params.items()
                           if value is not None}
        # separators to remove spaces between key and value
        json_params: str = json.dumps(filtered_params, separators=(',', ':'))
        json_params_len: int = len(json_params)
        action_code: bytes = b'\x01\x00\x00\x00'
        login_request: bytes = (action_code + json_params_len.to_bytes(4, byteorder="little", signed=False)
                                + json_params.encode('utf-8'))

        client_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(GameClient.server_address)
        client_socket.sendall(login_request)

        # Receiving result code as bytes
        result_code: bytes = client_socket.recv(4)

        # Converting bytes into Enum
        result_enum: GameClient.Result = GameClient.Result(
            int.from_bytes(result_code, byteorder="little", signed=False)
        )
        print("Login result:", result_enum.name)

        if result_enum != GameClient.Result.OKEY:
            return None
        # Read the length of JSON with data
        json_data_length: bytes = client_socket.recv(4)
        json_bytes: bytes = client_socket.recv(int.from_bytes(json_data_length, byteorder="little", signed=False))
        json_data: Dict = json.loads(json_bytes.decode('utf-8'))
        player_id: int = json_data["idx"]
        player_name: str = json_data["name"]
        print("Logged in player")
        print("Name:", player_name, ", id:", player_id)
        return GameClient(Player(player_id, player_name))


def main():
    game_client: GameClient = GameClient.login("Boris")


if __name__ == "__main__":
    main()
