from scripts.grid import Grid
from typing import List, Tuple, Optional, Dict, Any
import json
import socket
from enum import Enum

from scripts.player import Player
from scripts.real_player import RealPlayer
from scripts.tank import Tank
from scripts.medium_tank import MediumTank


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

    class ActionType(Enum):
        LOGIN = 1
        LOGOUT = 2
        MAP = 3
        GAME_STATE = 4
        GAME_ACTIONS = 5
        TURN = 6
        CHAT = 100
        MOVE = 101
        SHOOT = 102

    # TODO: Make it to support CHAT
    class Action:
        def __init__(self, action_type: 'GameClient.ActionType', player: Player, vehicle: Tank,
                     target: Tuple[int, int] = None):
            self.type: 'GameClient.ActionType' = action_type
            self.player: Player = player
            self.vehicle: Tank = vehicle
            self.target: Optional[Tuple[int, int]] = target

    def __init__(self, client_player_id: int, client_socket: socket):
        self.__client_socket: socket = client_socket
        self.__client_player_id: int = client_player_id
        self.__grid: Grid = Grid(0)
        self.__players: List[Player] = []
        self.observers: List[Player] = []

        self.__players_capturing_base: List[Player] = []
        self.__base: List[Tuple[int, int]] = [(0, 0)]
        self.__name: Optional[str] = None
        self.__rounds: int = 15
        self.__turns: int = 10
        self.__cur_round: int = 1  # rounds start with 1
        self.__cur_turn: int = 0  # turns start with 0
        self.__cur_player_index: int = 0
        self.__obstacles: List[Tuple[int, int]] = []

        self.update_game_state()
        self.update_map()

    @staticmethod
    def __send_request__(client_socket: socket, action: 'GameClient.ActionType', json_data: str = "") -> None:
        request: bytes = (action.value.to_bytes(4, byteorder="little")
                          + len(json_data).to_bytes(4, byteorder="little"))
        if json_data != "":
            request += json_data.encode('utf-8')
        print(request)
        client_socket.sendall(request)

    @staticmethod
    def __process_response__(client_socket: socket) -> Tuple['GameClient.Result', Optional[Dict]]:
        # Receiving result code as bytes
        result_code: bytes = client_socket.recv(4)

        # Converting bytes into Enum
        result_enum: GameClient.Result = GameClient.Result(
            int.from_bytes(result_code, byteorder="little")
        )
        print("Result of request:", result_enum)
        # Read the length of JSON with data
        json_data_length: int = int.from_bytes(client_socket.recv(4), byteorder="little")
        if result_enum != GameClient.Result.OKEY or json_data_length == 0:
            return result_enum, None

        json_bytes: bytes = client_socket.recv(json_data_length)
        json_data: Dict = json.loads(json_bytes.decode('utf-8'))
        return result_enum, json_data

    def __find_player__(self, idx: int) -> Optional[Player]:
        for player in self.__players:
            if player.id == idx:
                return player
        return None

    @classmethod
    def login(cls, client_socket: socket, name: str, password: Optional[str] = None,
              game: Optional[str] = None, num_turns: Optional[int] = None,
              num_players: Optional[int] = None, is_observer: Optional[bool] = None,
              is_full: Optional[bool] = None) -> Optional['GameClient']:
        """ Sends login request to the server
        :param client_socket socket to communicate with server
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
        params.pop("client_socket")
        # removes every None from calls like: login("Boris", password = None)
        filtered_params = {key: value for key, value in params.items()
                           if value is not None}
        # separators to remove spaces between key and value
        json_params: str = json.dumps(filtered_params, separators=(',', ':'))
        client_socket: socket = None
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(GameClient.server_address)
            # sends login request to the server
            GameClient.__send_request__(client_socket, GameClient.ActionType.LOGIN, json_params)
            # gets response from the server
            result_enum, json_data = GameClient.__process_response__(client_socket)

            if result_enum != GameClient.Result.OKEY:
                return None

            player_id: int = json_data["idx"]
            player_name: str = json_data["name"]
            is_observer: bool = json_data["is_observer"]
            # TODO: create game with provided through args settings
            return GameClient(player_id, client_socket)
        except socket.error as e:
            print(f"Socket error: {e}")
            return None

    def logout(self) -> None:
        """ Logouts the player from the game and closes the socket
        """
        try:
            GameClient.__send_request__(self.__client_socket, GameClient.ActionType.LOGOUT)
            result_enum, _ = GameClient.__process_response__(self.__client_socket)
            print("Logout result:", result_enum.name)
        except socket.error as e:
            print(f"Socket error: {e}")

    def update_game_state(self) -> None:
        """ Updates the state of the game by requesting GAME_STATE
        """
        try:
            GameClient.__send_request__(self.__client_socket, GameClient.ActionType.GAME_STATE)
            result_enum, json_game_state = GameClient.__process_response__(self.__client_socket)

            if result_enum == GameClient.Result.OKEY:
                self.__turns = json_game_state["num_turns"]
                self.__rounds = json_game_state["num_rounds"]
                self.__cur_turn = json_game_state["current_turn"]
                self.__cur_round = json_game_state["current_round"]

                # clears players list in order to update with server data
                self.__players.clear()
                for player in json_game_state["players"]:
                    # TODO: creates only BOTs, need default player for opponents
                    self.__players.append(RealPlayer(player["idx"], player["name"], player["is_observer"]))
                vehicles = json_game_state["vehicles"]
                # key: vehicle id, value: vehicle features as dictionary
                for vehicle_id, vehicle_features in vehicles.items():
                    owner: Player = self.__find_player__(vehicle_features["player_id"])
                    if not owner:
                        print("No vehicle owner found error!")
                        raise ValueError
                    cur_pos: Tuple[int, int] = (vehicle_features["position"]["x"], vehicle_features["position"]["y"])
                    spawn_pos: Tuple[int, int] = (vehicle_features["spawn_position"]["x"],
                                                  vehicle_features["spawn_position"]["y"])
                    vehicle_type: str = vehicle_features["vehicle_type"]
                    # TODO: only medium tanks now
                    if vehicle_type == "medium_tank":
                        vehicle: Tank = MediumTank(vehicle_id, cur_pos, spawn_pos, vehicle_features["capture_points"],
                                                   owner, None, 1)
                        owner.add_tank(vehicle)
                # TODO: order players correctly, finished, attack matrix, winner, win_points
                # TODO: player_result_points, catapult_usage
        except socket.error as e:
            print(f"Socket error: {e}")

    def update_map(self) -> None:
        """ Updates the map by requesting MAP
        """
        try:
            GameClient.__send_request__(self.__client_socket, GameClient.ActionType.MAP)
            result_enum, json_data = GameClient.__process_response__(self.__client_socket)
            if result_enum == GameClient.Result.OKEY:
                self.__grid: Grid = Grid(json_data["size"])
                # TODO: spawns
                map_content: Dict[str, Any] = json_data["content"]
                base: List[Dict[str, int]] = map_content["base"]
                # TODO: fix KeyError: 'obstacle'
                #obstacles: List[Dict[str, int]] = map_content["obstacle"]
                self.__base.clear()
                for base_cell in base:
                    self.__base.append((base_cell["x"], base_cell["y"]))
                # self.__obstacles.clear()
                # for obstacle_cell in obstacles:
                #     self.__obstacles.append((obstacle_cell["x"], obstacle_cell["y"]))
        except socket.error as e:
            print(f"Socket error: {e}")

    def get_game_actions(self) -> List['GameClient.Action']:
        """ Requests game actions from the server and returns them
        @:return returns list of actions got from server
        """
        GameClient.__send_request__(self.__client_socket, GameClient.ActionType.GAME_ACTIONS)
        result_enum, json_data = GameClient.__process_response__(self.__client_socket)
        actions: List['GameClient.Action'] = []
        if result_enum == GameClient.Result.OKEY:
            for action in json_data["actions"]:
                player: Optional[RealPlayer] = self.__find_player__(action["player_id"])
                action_type: GameClient.ActionType = GameClient.ActionType(action["action_type"])
                action_data: str = action["data"]
                action.append(GameClient.Action(action_type, player, action_data))
        return actions

    def __get_turn__(self) -> Action:
        type_: GameClient.ActionType = GameClient.ActionType.MOVE
        player: Player = self.__find_player__(self.__client_player_id)
        vehicle: Tank = player.tanks[0]
        x, y = vehicle.curr_position
        z = -x - y
        print("Cur pos: ", x, y, z)
        if x == 0 and y == 0 and z == 0:
            return GameClient.Action(type_, player, vehicle)
        # Calculate the differences between current position and origin
        dist_x = abs(x)
        dist_y = abs(y)
        dist_z = abs(z)
        if dist_x >= dist_y and dist_x >= dist_z:
            if dist_y > dist_z:
                if x > 0:
                    x -= 1
                    y += 1
                else:
                    x += 1
                    y -= 1
            elif x > 0:
                x -= 1
            else:
                x += 1
        elif dist_y >= dist_x and dist_y >= dist_z:
            if dist_x > dist_z:
                if y > 0:
                    y -= 1
                    x += 1
                else:
                    y += 1
                    x -= 1
            elif y > 0:
                y -= 1
            else:
                y += 1
        else:
            if dist_y > dist_x:
                if z > 0:
                    y += 1
                else:
                    y -= 1
            elif z > 0:
                x += 1
            else:
                x -= 1
        return GameClient.Action(type_, player, vehicle, (x, y))

    def play_turn(self):
        action: GameClient.Action = self.__get_turn__()
        if not action.target:
            GameClient.__send_request__(self.__client_socket, GameClient.ActionType.TURN)
            result_enum, _ = GameClient.__process_response__(self.__client_socket)
            print("End of turn send", result_enum.name)
            return
        # I don't know if we have to do that in client logic
        # self.__execute_action__(action)
        # send the action to the server
        action_data_dict: Dict[str, Any] = {
            "vehicle_id": action.vehicle.id,
            "target": {
                "x": action.target[0],
                "y": action.target[1],
                "z": Grid.get_z(action.target[0], action.target[1])
            }
        }
        action_data_json: str = json.dumps(action_data_dict, separators=(',', ':'))
        GameClient.__send_request__(self.__client_socket, action.type, action_data_json)
        result_enum, _ = GameClient.__process_response__(self.__client_socket)
        print("Move result", result_enum.name)
        if result_enum == GameClient.Result.OKEY:
            GameClient.__send_request__(self.__client_socket, GameClient.ActionType.TURN)
            result_enum, _ = GameClient.__process_response__(self.__client_socket)
            print("End of turn send", result_enum.name)
        else:
            print("Something went wrong, turn wasn't played")

    def __execute_action__(self, action: 'GameClient.Action'):
        if action.type == GameClient.ActionType.MOVE:
            self.__execute_move__(action)
        elif action.type == GameClient.ActionType.SHOOT:
            self.__execute_shoot__(action)
        # TODO: chat action
        elif action.type == GameClient.ActionType.CHAT:
            pass
        else:
            # Not a game action
            raise ValueError

    # TODO: mb add inheritance and execute() overridden method
    def __execute_move__(self, action: 'GameClient.Action'):
        assert (action.type == GameClient.ActionType.MOVE)
        action.vehicle.move(action.target)

    def __execute_shoot__(self, action: 'GameClient.Action'):
        assert (action.type == GameClient.ActionType.SHOOT)
        # TODO: make method shoot take coordinates of the cell
        target: Optional[Tank] = None
        for player in self.__players:
            if player == action.player:
                continue
            for vehicle in player.tanks:
                if vehicle.curr_position == action.target:
                    target = vehicle
        if not target:
            raise ValueError
        action.vehicle.shoot(target)

    def __execute_chat__(self, action: Action):
        assert (action.type == GameClient.ActionType.CHAT)
        pass

    def update_turn(self):
        self.__cur_turn += 1

    def round_finished(self):
        return self.__cur_turn == self.__turns

    def get_base(self) -> List[Tuple[int, int]]:
        return self.__base

    def get_cur_turn(self) -> int:
        return self.__cur_turn

    def get_turns_num(self) -> int:
        return self.__turns

    def get_round(self) -> int:
        return self.__cur_round


def main():
    # def address and port server
    server_address = ("wgforge-srv.wargaming.net", 443)

    # create sock connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect on server
    sock.connect(server_address)

    game_client: GameClient = GameClient.login(sock, "Boris")
    actions = game_client.get_game_actions()
    game_client.logout()
    sock.close()


if __name__ == "__main__":
    main()
