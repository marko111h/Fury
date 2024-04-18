from scripts.player import Player
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
class BotPlayer(Player):
    def __init__(self, idx, name):
        super().__init__(idx, name, is_observer=False)
        self.tanks = []  # Lista tenkova koje bot kontrolira
        self.last_tank_played = []  # Last tank played
        self.vehicles_in_base = {}  # dictionary  tracks  vehicles in  base


    def add_tanks(self, tank_data):
        # Implementation of adding tanks

        self.tanks.extend(tank_data)
        print(f"Tank_data: {tank_data} ")
        print(f"Successfully added {self.tanks} tanks .")

    def play_turn(self, game_logic, sock):
        # Implement bot move logic
        for tank_id in self.tanks:
            tank_data = game_logic.game_state['vehicles'][tank_id]
            print(f"Tank/vehicle number {tank_id}")
            # The bot can decide whether to attack the opponent or move towards the base
            if self.should_attack_enemy(game_logic, tank_data):
                self.attack_enemy(tank_data, game_logic, sock)
            elif self.should_move_towards_base(game_logic, tank_data):
                self.move_towards_base(tank_data, game_logic, sock)

            # Update game state after moves
            game_logic.update_game_state(sock)
            # Add the ID of the last played tank
            self.last_tank_played.append(tank_id)

        # At the end of each move request game actions from the server
        actions = game_actions_request(sock)
        #### mislim da moram da ubacim neke akcije cisto da vidim kako bi reagovao process_game_actions
        # Process game actions
        game_logic.process_game_actions(actions, game_logic)

        # Send a turn request
        self.send_turn_request(sock)

    def should_attack_enemy(self, game_logic, tank_data):


        #Check your opponent's previous attacks first
        opponent_attacks = game_logic.previous_attacks
        print(f"we check previous attacks {opponent_attacks}")
        print(f"Type of opponent_attacks: {type(opponent_attacks)}")
        print(f"opponent_attacks contents: {opponent_attacks}")


        # We collect the opponent's attacks in the previous round
        attacked_opponents = set()
        for player_id, attacks in opponent_attacks.items():
            print(f"Player ID: {player_id}")
            print(f"attacks contents: {attacks}")
            if player_id != self.id:
                for attack in attacks:
                    print(f"Processing attack: {attack}")
                    attacked_opponents.add(player_id)
            # if player_id != self.id:
            #     try:
            #         attacked_opponents.update(attacks.get('attacked', []))
            #     except Exception as e:
            #         print(f"Error during attacks update: {e}")


        # Check which opponents the real player attacked in the previous round
        current_player_attacks = opponent_attacks.get(self.id, [])

        # Neutrality Rule 1: Only the opponent who attacked the player in the previous move can be attacked
        # Or an opponent that the third player did not attack in the previous move

        for opponent in attacked_opponents:
            if opponent in current_player_attacks:
                return True ## The opponent attacked the player in the previous move

        # Neutrality Rule 2: An opponent who did not attack a player in the previous move may not be attacked
        # or was attacked by a third player in the previous move

        for opponent in current_player_attacks:
            if opponent not in attacked_opponents:
                return False ## The opponent did not attack the player in the previous move or was attacked by a third player

        return False ## Not eligible for attack

    def attack_enemy(self, tank_data, game_logic, sock):

        pass

    def should_move_towards_base(self, game_logic, tank_data):

        pass

    def move_towards_base(self, tank_data, game_logic, sock):

        pass

    def calculate_move_direction(self, current_position, base_position):
        # Calculate direction of movement from the current position to the base
        return {
            "x": base_position['x'] - current_position['x'],
            "y": base_position['y'] - current_position['y'],
            "z": base_position['z'] - current_position['z']
        }

    def choose_enemy_to_attack(self, game_logic):
        # Implement logic for choosing an opponent to attack
        pass

    def send_turn_request(self, sock):
        """Send a move request to the server."""
        turn_request(sock)
