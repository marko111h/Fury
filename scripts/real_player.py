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
from scripts.tank import Tank
from typing import List


class RealPlayer(Player):
    def __init__(self, idx, name, is_observer=False):
        super().__init__(idx, name, is_observer)
        self.tanks: List[Tank] = []  # list of tank with player manage
        self.last_tank_played: List[Tank] = []  #List of last played tanks
        self.vehicles_in_base = {}  # Dictionary that tracks vehicles in the base

    def play_turn(self, game_logic, sock):
        """Defines how a real player plays their turn."""
        for tank_id in self.tanks:
            tank_data = game_logic.game_state['vehicles'][tank_id]

            if self.should_attack_enemy(game_logic, tank_data):
                self.attack_enemy(tank_data, game_logic, sock)
            # move to base
            elif self.should_move_towards_base(game_logic, tank_data):
                self.move_towards_base(tank_data, game_logic, sock)

            # Update game state after moves
            game_logic.update_game_state(sock)
            # Update the last tank that played
            self.last_tank_played.append(tank_id)

        # After each turn, request the game actions from the server
        actions = game_actions_request(sock)

        #Process the game actions
        game_logic.process_game_actions(actions, game_logic)
        # Send a turn request
        self.send_turn_request(sock)

    def add_tank(self, tank: Tank):
        # Implementation of adding tank
        if tank not in self.tanks:
            self.tanks.append(tank)

    def should_attack_enemy(self, game_logic, tank_data):
        #Check your opponent's previous attacks first
        opponent_attacks = game_logic.previous_attacks
        print(f"we check previous attacks {opponent_attacks}")

        # We collect the opponent's attacks in the previous round
        attacked_opponents = set()
        for player_id, attacks in opponent_attacks.items():
            print(f"Player ID: {player_id}")
            print(f"attacks contents: {attacks}")
            if player_id != self.id:
                if isinstance(attacks, list):
                    for attack in attacks:
                        print(f"Processing attack: {attack}")

                        # Umesto dodavanja celog attack objekta u set, koristite odgovarajuću vrednost kao ključeve
                        # Na primer, možete dodati player_id, koji je nepromenljiv tip podataka
                        attacked_opponents.add(player_id)
                else:
                    print(f"Unexpected type in attacks: {type(attacks)}")

        # Check which opponents the real player attacked in the previous round
        current_player_attacks = opponent_attacks.get(self.id, [])

        # Neutrality Rule 1: Only the opponent who attacked the player in the previous move can be attacked
        # Or an opponent that the third player did not attack in the previous move

        for opponent in attacked_opponents:
            if opponent in current_player_attacks:
                return True  ## The opponent attacked the player in the previous move

        # Neutrality Rule 2: An opponent who did not attack a player in the previous move may not be attacked
        # or was attacked by a third player in the previous move

        for opponent in current_player_attacks:
            if opponent not in attacked_opponents:
                return False  ## The opponent did not attack the player in the previous move or was attacked by a third player

        return False  ## Not eligible for attack

    def should_move_towards_base(self, game_logic, tank_data):
        pass

    def attack_enemy(self, tank_data, game_logic, sock):
        pass
        # Implementation of attacks on the opponent
        target_tank_id = self.choose_enemy_to_attack(game_logic)

        if target_tank_id:
            # Send a shooting request
            shoot_request(sock, tank_data['id'], target_tank_id)

            #  Update the game state
            game_logic.update_game_state(sock)

            # Check if the targeted tank is destroyed
            if game_logic.game_state['vehicles'][target_tank_id]['hp'] == 0:
                self.earn_destruction_points(1)

    def should_move_towards_base(self, game_logic, tank_data):
        # Logika koja određuje kada se tenk treba kretati prema bazi
        # Ovde možete dodati više kriterijuma kao što su udaljenost do baze, stanje tenka itd.
        # Na primer, ako je tenk teško oštećen, vratite ga bazi
        # Logic that determines when the tank should move towards the base
        # Here you can add more criteria like distance to base, tank condition etc.
        pass
        # # For example, if a tank is badly damaged, return it to base
        # base_position = game_logic.base
        # current_position = tank_data['position']
        # distance_to_base = self.calculate_distance(current_position, base_position)
        #
        # # Možete podesiti pragove prema svojim potrebama
        # if distance_to_base < 10 and tank_data['health'] < 50:
        #     return True
        # return False

    def move_towards_base(self, tank_data, game_logic, sock):
        pass
        # # Implementacija kretanja ka bazi
        # base_position = game_logic.base
        # current_position = tank_data['position']
        #
        # move_direction = self.calculate_move_direction(current_position, base_position)
        # move_request(sock, tank_data['id'], move_direction)
        # game_logic.update_game_state(sock)

    def calculate_move_direction(self, current_position, base_position):
        pass
        # # Implementacija izračuna pravca kretanja ka bazi
        # return {
        #     "x": base_position['x'] - current_position['x'],
        #     "y": base_position['y'] - current_position['y'],
        #     "z": base_position['z'] - current_position['z']
        # }

    def choose_enemy_to_attack(self, game_logic):
        pass
        # # Implementation of choosing an opponent to attack
        # enemy_tanks = []
        # for player in game_logic.players:
        #     if player.id != self.id:
        #         enemy_tanks.extend(player.tanks)
        #
        # if enemy_tanks:
        #     return random.choice(enemy_tanks)
        # return None

    def send_turn_request(self, sock):
        """Send a move request to the server."""
        turn_request(sock)
