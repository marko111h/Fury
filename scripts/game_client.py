from grid import Grid
from typing import List, Tuple, Optional, Dict, Any
import json
import socket
from enum import Enum


# To run the code
class Tank:
    def __init__(self, id, curr_position, spawn_position, capture_points, speed_points, hit_points, fire_power,
                 destruction_points, owner):
        self.id = id
        self.curr_position = curr_position
        self.spawn_position = spawn_position
        self.capture_points = capture_points
        self.speed_points = speed_points
        self.starting_hit_points = hit_points  # added this beacuse we will need it in respawning
        self.hit_points = hit_points
        self.fire_power = fire_power
        self.destruction_points = destruction_points
        self.owner = owner
        self.prev_attacker = None
        self.order_position = None

    def get_id(self):
        return self.id

    def get_curr_position(self):
        return self.curr_position

    def get_spawn_position(self):
        return self.spawn_position

    def get_capture_points(self):
        return self.capture_points

    def get_speed_points(self):
        return self.speed_points

    def get_starting_hit_points(self):
        return self.starting_hit_points

    def get_hit_points(self):
        return self.hit_points

    def get_fire_power(self):
        return self.fire_power

    def get_destruction_points(self):
        return self.destruction_points

    def get_owner(self):
        return self.owner

    def get_prev_attacker(self):
        return self.prev_attacker

    def get_order_position(self):
        return self.order_position

    def add_destruction_points(self, value):
        self.destruction_points += value

    def shoot(self, target):
        target.take_damage(self)

    def move(self, new_position):
        self.curr_position = new_position

        if new_position not in []:
            self.capture_points = 0

    def earn_capture_point(self):
        if self.curr_position in []:
            self.capture_points += 1

    def take_damage(self, shooter):
        self.hit_points -= 1

        if self.hit_points == 0:
            self.capture_points = 0
            self.curr_position = self.spawn_position
            self.hit_points = self.starting_hit_points
            shooter.add_destruction_points(self.hit_points)


class Player:
    def __init__(self, player_id, name):
        # Basic player attributes
        self.player_id = player_id
        self.name = name

        # Points for destroying vehicles and capturing bases
        self.destruction_points = 0
        self.base_capture_points = 0

        # Players vehicles
        self.vehicles = []

    def add_vehicle(self, vehicle):
        """Adds a vehicle to the player's ownership."""
        self.vehicles.append(vehicle)

    def remove_vehicle(self, vehicle):
        """Removes the vehicle from player ownership."""
        self.vehicles.remove(vehicle)

    def earn_destruction_points(self, points):
        """Increases destruction points."""
        self.destruction_points += points

    def lose_destruction_points(self, points):
        """Reduces destruction points."""
        self.destruction_points -= points

    def earn_base_capture_points(self, points):
        """Increases points for capturing the base."""
        self.base_capture_points += points

    def lose_base_capture_points(self, points):
        """Reduces points for capturing a base."""
        self.base_capture_points -= points

    def __str__(self):
        """Returns player information as a string."""
        return f"Player: {self.name}, ID: {self.player_id}, Destruction Points: {self.destruction_points}, Base Capture Points: {self.base_capture_points}"


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
                     target: Tuple[int, int]):
            self.type: 'GameClient.ActionType' = action_type
            self.player: Player = player
            self.vehicle: Tank = vehicle
            self.target: Tuple[int, int] = target

    def __init__(self, client_player: Player, client_socket: socket):
        self.__client_socket: socket = client_socket
        self.__grid: Grid = Grid(0)
        self.__players: List[Player] = []
        self.__players_capturing_base: List[Player] = []
        self.__client_player: Player = client_player
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
        print("Result of game_state", result_enum)
        # Read the length of JSON with data
        json_data_length: int = int.from_bytes(client_socket.recv(4), byteorder="little")
        print("Length of json_data:", json_data_length)
        if result_enum != GameClient.Result.OKEY or json_data_length == 0:
            return result_enum, None

        json_bytes: bytes = client_socket.recv(json_data_length)
        json_data: Dict = json.loads(json_bytes.decode('utf-8'))
        return result_enum, json_data

    def __find_player__(self, idx: int) -> Optional[Player]:
        for player in self.__players:
            if player.player_id == idx:
                return player
        return None

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

        client_socket: socket = None
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(GameClient.server_address)
            # sends login request to the server
            GameClient.__send_request__(client_socket, GameClient.ActionType.LOGIN, json_params)
            # gets response from the server
            result_enum, json_data = GameClient.__process_response__(client_socket)

            print("Login result:", result_enum.name)

            if result_enum != GameClient.Result.OKEY:
                return None
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

    def logout(self) -> None:
        """ Logouts the player from the game and closes the socket
        """
        try:
            GameClient.__send_request__(self.__client_socket, GameClient.ActionType.LOGOUT)
            result_enum, _ = GameClient.__process_response__(self.__client_socket)
            print("Logout result:", result_enum.name)
        except socket.error as e:
            print(f"Socket error: {e}")
        finally:
            self.__client_socket.close()

    def update_game_state(self) -> None:
        """ Updates the state of the game by requesting GAME_STATE
        """
        try:
            GameClient.__send_request__(self.__client_socket, GameClient.ActionType.GAME_STATE)
            result_enum, json_game_state = GameClient.__process_response__(self.__client_socket)
            print("Game State request result:", result_enum.name)

            if result_enum == GameClient.Result.OKEY:
                self.__turns = json_game_state["num_turns"]
                self.__rounds = json_game_state["num_rounds"]
                self.__cur_turn = json_game_state["current_turn"]
                self.__cur_round = json_game_state["current_round"]
                self.__players.clear()
                for player in json_game_state["players"]:
                    self.__players.append(Player(player["idx"], player["name"]))
                    if self.__players[-1].player_id == self.__client_player.player_id:
                        self.__client_player = self.__players[-1]
                    print(player["idx"], player["name"])
                vehicles = json_game_state["vehicles"]
                # key: vehicle id, value: vehicle features as dictionary
                for key, value in vehicles.items():
                    owner: Player = self.__find_player__(value["player_id"])
                    if not owner:
                        print("No player found error!")
                        return
                    cur_pos: Tuple[int, int] = (value["position"]["x"], value["position"]["y"])
                    spawn_pos: Tuple[int, int] = (value["spawn_position"]["x"], value["spawn_position"]["y"])
                    vehicle = Tank(key, cur_pos, spawn_pos,
                                   value["capture_points"], 2, 2, 1,
                                   2, owner)
                    owner.add_vehicle(vehicle)
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
                obstacles: List[Dict[str, int]] = map_content["obstacle"]
                self.__base.clear()
                for base_cell in base:
                    self.__base.append((base_cell["x"], base_cell["y"]))
                self.__obstacles.clear()
                for obstacle_cell in obstacles:
                    self.__obstacles.append((obstacle_cell["x"], obstacle_cell["y"]))
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
                player: Player = self.__find_player__(action["player_id"])
                action_type: GameClient.ActionType = GameClient.ActionType(action["action_type"])
                action_data: str = action["data"]
                action.append(GameClient.Action(action_type, player, action_data))
        return actions

    def play_turn(self, action: 'GameClient.Action'):
        assert (action.player == self.__client_player)
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
            for vehicle in player.vehicles:
                if vehicle.curr_position == action.target:
                    target = vehicle
        if not target:
            raise ValueError
        action.vehicle.shoot(target)

    def __execute_chat__(self, action: Action):
        assert (action.type == GameClient.ActionType.CHAT)
        pass

    # just simple function to send moves to the server
    def print_pos(self) -> Action:
        vehicle: Tank = self.__client_player.vehicles[0]
        print(vehicle.id)
        print(vehicle.curr_position)
        x = int(input())
        y = int(input())
        return GameClient.Action(GameClient.ActionType.MOVE,
                                 self.__client_player,
                                 vehicle,
                                 (x, y))

    def get_base(self) -> List[Tuple[int, int]]:
        return self.__base

def main():
    game_client: GameClient = GameClient.login("Boris")
    actions = game_client.get_game_actions()
    for i in range(3):
        game_client.play_turn(game_client.print_pos())
    game_client.logout()


if __name__ == "__main__":
    main()
