from abc import ABC,abstractmethod
import random
from connection_to_server.server_communication import (
    login_request,
    logout_request,
    map_request,
    game_state_request,
    game_actions_request,
    turn_request,
    chat_request,
    move_request,
    shoot_request
)
from scripts.tank import Tank
# from game_logic import GameLogic


class Player(ABC):
    def __init__(self, id, name, is_observer):
        # Basic player attributes
        self.id = id
        self.name = name
        self.is_observer = is_observer


        # Points for destroying vehicles and capturing bases
        self.destruction_points = 0
        self.base_capture_points = 0 # Points for taking base or centar

        # Players vehicles
        self.tanks = [] # list of tank with player manage
        self.last_tank_played = 0 #

        self.vehicles_in_base = {} # Dictionary that tracks vehicles in the base

    @abstractmethod
    def add_tank(self, tank: Tank):
        pass


    # Function to decide if a player can attack an opponent according to the rules of neutrality
    # @abstractmethod
    # def should_attack_enemy(self, game_logic):
    #     pass


    # @abstractmethod
    # def attack_enemy(self, tank_data, game_logic, sock):
    #     """Allows the player to attack an enemy using their tank."""
    #     pass


    # @abstractmethod
    # def move_towards_base(self, tank_data, game_logic, sock):
    #     """Allows the player to move their tank towards the base."""
    #     pass


    @abstractmethod
    def play_turn(self, game_logic,sock,):
        """A method to be implemented in subclasses, allowing the player to play his turn."""
        pass


    # @abstractmethod
    # def calculate_move_direction(self, current_position, base_position):


    # @abstractmethod
    # def choose_enemy_to_attack(self, game_logic):
    #     pass





    def ern_destruction_points(self,points , game_state):
        """Increases destruction points."""
        self.destruction_points += points

    def lose_destruction_points(self, points):
        """Reduces destruction points."""
        self.destruction_points -= points


    def earn_base_capture_points(self,game_state,map_request):
        """Increases points for capturing the base."""
        # Convert a list of base coordinates to a set of tuples
        base_coordinates = map_request['content']['base']
        base_set = set((coordinate['x'], coordinate['y'], coordinate['z']) for coordinate in base_coordinates)

        # Get the identifier of the player the vehicle belongs to (get from game state)
        vehicles = game_state['vehicles']

        for vehicle_id, vehicle_data in vehicles.items():

            current_position = (
                vehicle_data['position']['x'],
                vehicle_data['position']['y'],
                vehicle_data['position']['z']
            )
            # Check if the vehicle is in base
            is_in_base = current_position in base_set

            # Previous state of whether the vehicle was in base
            was_in_base = self.vehicles_in_base.get(vehicle_id, False)

            if is_in_base and not was_in_base:
                # Vehicle just entered the base
                self.base_capture_points += 1
                print(f"Vehicle ID: {vehicle_id} just entered the base and earned a point for the player.")
            elif not is_in_base and was_in_base:
                # Vehicle just left the base
                self.base_capture_points -= 1
                print(f"Vehicle ID: {vehicle_id} just left the base and lost a point for the player.")

            # Update the state of the vehicle in the base
            self.vehicles_in_base[vehicle_id] = is_in_base

            # Print vehicle data for debugging
            print(f"Vehicle ID: {vehicle_id}")
            print(f"Current position: {current_position}")
            print(f"In base: {is_in_base}")
            print(f"Was in base: {was_in_base}")
            print()  # An empty line for readability

    # def remove_vehicle(self,vehicle):
    #     """Removes the vehicle from player ownership."""
    #     self.vehicles.remove(vehicle)
    def __str__(self):
        """Returns player information as a string."""
        return (f"Player:  ID: {self.id}, Name: {self.name}, Is Observer: {self.is_observer}"
                f"  , Destruction Points: {self.destruction_points}, Base Capture Points: {self.base_capture_points}")

