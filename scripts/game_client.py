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

    class Action(Enum):
        LOGIN = 1
        LOGOUT = 2
        MAP = 3
        GAME_STATE = 4
        GAME_ACTIONS = 5
        TURN = 6
        CHAT = 100
        MOVE = 101
        SHOOT = 102

    def __init__(self, player: Player, client_socket: socket):
        self.__client_socket: socket = client_socket
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
        """ Sends login request to the server
        :param name: name of the player
        :param password: user's password, default: no password
        :param game: game's name, default: no name
        :param num_turns: number of turns to be played, default: default value
        :param num_players: number of players in the game, default: 1
        :param is_observer: defines if observer joins server just to watch, default: False
        :param is_full: defines if player wants to play full game with all order combinations, default: False
        :return: new game with provided settings
        """
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
        action_code: bytes = GameClient.Action.LOGIN.value.to_bytes(4, byteorder="little", signed=False)
        login_request: bytes = (action_code + json_params_len.to_bytes(4, byteorder="little", signed=False)
                                + json_params.encode('utf-8'))
        client_socket: socket = None
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            # TODO: create game with provided through args settings
            return GameClient(Player(player_id, player_name), client_socket)
        except socket.error as e:
            print(f"Socket error: {e}")
            if client_socket:
                client_socket.close()
            return None

    def logout(self):
        """ Logouts the player from the game. game_client is meaningless
        :return:
        """
        request: bytes = GameClient.Action.LOGOUT.value.to_bytes(4, byteorder="little", signed=False)


def main():
    game_client: GameClient = GameClient.login("Boris")


if __name__ == "__main__":
    main()
