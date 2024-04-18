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
from scripts.bot_player import BotPlayer
from scripts.real_player import RealPlayer


# from player import Player
class GameLogic:
    def __init__(self,real_player_data,base, max_rounds=15, ):
        # Real palyer

        self.real_player = RealPlayer(real_player_data['idx'], real_player_data['name'], real_player_data.get('is_observer', False))
        # Craete imaginare bot
        self.bot1 = BotPlayer(idx=1, name="Bot1")
        self.bot2 = BotPlayer(idx=2, name="Bot2")
        print(f"Real_player {self.real_player}")
        print(f"Bot 1 {self.bot1}")
        print(f"Bot2 {self.bot2}")

        self.players = [self.real_player, self.bot1, self.bot2]

        # self.grid = grid
        self.base = base
        self.max_rounds = max_rounds
        self.rounds =0
        #random choise player
        self.current_player_index = random.randint(0, len(self.players) -1) # Randomly choice player
        self.current_player = self.players[self.current_player_index]
        self.previous_attacks = {} # dictionary to trace attacks in the previous turn
        self.game_state = None  # Initialize game state as None
        self.tank_state = None  # Initialize tank state as None
        self.previous_round_state = {}  # Add an attribute for the previous state of the game
        self.num_turns = 0

        # First player play
        print(f"First player who play is :{self.current_player.name} ")



    def play_game(self, sock):
        """Starts the game and controls its flow."""
        # Update game status
        self.update_game_state(sock)

        self.num_turns = self.game_state['num_turns']
        print(f"{self.num_turns} asdas dsaasda num_turn")

        while self.num_turns > 0:

            # Initialize `current_attacks` for each round
            current_attacks = {}

            #Current player # when we randomly deidec
            current_player = self.players[self.current_player_index]
            print(f"Player who plays {current_player}")

            # Ensure tanks are added to the current player if not already done
            # that should come form Tank Class or vehicle
            # Tank.add_tanks_to_player(current_player, self.tank_state)
            if not current_player.tanks:
                current_player.add_tanks(self.tank_state)


            # Call play_turn() for currnetly player
            current_player.play_turn(self,sock)

            # Process game actions
            actions = game_actions_request(sock)
            # Testing actions
            if self.current_player.name == "Marko":
                actions = {
                              "actions": [
                                {
                                  "player_id": 7,
                                  "action_type": 102,
                                  "data": {
                                    "vehicle_id": 1,
                                    "target": {
                                      "x": -5,
                                      "y": -3,
                                      "z": 10
                                    }
                                  }
                                }
                              ]
                            }
            elif self.current_player.name == "Bot1":
                actions = {
                          "actions": [
                            {
                              "player_id": 1,
                              "action_type": 102,
                              "data": {
                                "vehicle_id": 3,
                                "target": {
                                  "x": 5,
                                  "y": 2,
                                  "z": -1
                                }
                              }
                            }
                        ]
                    }
            elif self.current_player.name == "Bot2":
                actions = {
                            "actions": [
                                {
                                  "player_id": 2,
                                  "action_type": 102,
                                  "data": {
                                    "vehicle_id": 4,
                                    "target": {
                                      "x": 3,
                                      "y": -2,
                                      "z": 0
                                    }
                                  }
                                }
                              ]
                            }
            print(f"Testing Action {actions}")
            self.process_game_actions(actions,self)


            # # Check for new attacks in `current_attacks`
            # if current_player.id not in self.previous_attacks:
            #     self.previous_attacks[current_player.id] = set()
            # new_attacks = current_attacks.get(current_player.id, [])
            # if new_attacks:
            #     for attack in new_attacks:
            #         # Add player_id to the set
            #         player_id = attack['player_id']
            #         self.previous_attacks[current_player.id].add(player_id)
            # Store the current attacks in the history of attacks
            # self.previous_attacks[current_player.id] = current_attacks.get(current_player.id, [])
            print("Updated previous_attacks:", self.previous_attacks)

            # Checking conditional win
            if self.check_victory():
                winner = self.get_winner()
                print(f"The winner is player {winner.name} with ID {winner.id}")
                return
            elif self.check_draw():
                print("Draw")
                return


            self.num_turns -= 1

            # Move clockwise to the next player
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

            #Game state update
            self.update_game_state(sock)

            # Updating the previous state of the game
            self.update_previous_round_state()

            turn_request(sock)

        if self.num_turns == 0:
            print(f"Next Round")
            self.start_new_round(sock)

    def start_new_round(self,sock):
        """Starts a new round of the game."""
        # Increase number of rounds
        self.rounds +=1

        # Check if max rounds reached
        if self.rounds >= self.max_rounds:
            print(f"Maximum Number of round reached. Game Over")
            return

        # Reset number of turns for new round
        self.num_turns = self.game_state['num_turns']

        # Call play_game to start new round
        print(f"Starrting a new round: {self.rounds}")
        self.play_game(sock)
    def update_game_state(self,sock):
        """Updates the game state after each move."""
        # Retrieve the latest game state data
        # Assuming `sock` is passed in as an argument to `play_game()`
        self.game_state = game_state_request(sock)
        self.tank_state = self.game_state['vehicles']


    def update_previous_round_state(self):
        """# Updating the previous state of the game"""
        self.previous_round_state = self.game_state

    def check_victory(self):
        """Checking victory conditions."""

        # Victory condition 1: Win 5 points to conquer the base

        for player in self.players:
            if player.base_capture_points >= 5 or player.destruction_points >= self.get_max_destruction_points() :
                return True
        return False
        # Uslov pobede 2: Osvojiti maksimalni broj poena za uništavanje protivničkih vozila
        # (Koristi se maksimalni broj poena definisan u ovoj klasi)
        # Victory condition 2: Score the maximum number of points for #destroying enemy vehicles
        # (The maximum number of points defined in this class is used)
        # if players.destruction_points >= self.max_destruction_points:
        #     return True
    def check_draw(self):
        """Checks conditions for a tie."""
        # If the game has just started (everyone has 0 points at the start), avoid declaring a tie
        if self.rounds < 2:
            return None
        # create list poen for base
        base_points_list = [player.base_capture_points for player in self.players]
        destruction_points_list = [player.destruction_points for player in self.players]
        # max poen for base
        max_base_points = max(base_points_list)
        max_destruction_points = max(destruction_points_list)

        # find a player who have max number poen for base
        players_with_max_base_points = [player for player in self.players if player.base_capture_points == max_base_points]


        # If there is more than one player with maximum points to win the base
        if len(players_with_max_base_points) > 1:
            # Check the points for destroying the opp veh for those players
            players_with_max_destruction_points = [player for player in players_with_max_base_points if player.destruction_points == max_destruction_points]

            # if poen for dest opp veh is same
            if len(players_with_max_destruction_points) >1:
                # Draw for player with same points
                print("Tie between players with the same score to capture the base and destroy the oppo veh.")
                return players_with_max_destruction_points
            if len(players_with_max_base_points) == len(self.players):
                print("Draw for all players")
                return players_with_max_base_points

            # if there no draw
            return None

    def get_winner(self):
        """Returns the winner of the game."""
        """Vraća pobjednika igre."""
        # Checks which player has the most points or the most destroyed vehicles
        max_base_points = max(player.base_capture_points for player in self.players)
        max_destruction_points = max(player.destruction_points for player in self.players)

        for player in self.players:
            if player.base_capture_points == max_base_points or player.destruction_points == max_destruction_points:
                return player
        return None

    def get_previous_round_state(self):
        # Restores the previous state of the game
        return self.previous_round_state


    def process_game_actions(self, actions, game_logic):
        """Process the game actions after each turn."""
        # If there are no actions in response, log in and continue
        if not actions['actions']:
            print("No game actions received from server.")
            return  # Nastavite na sledeći korak igre
        # record of attacks in the current round
        current_attacks = {}
        # Iterate over the actions and process them
        for action in actions['actions']:
            player_id = action['player_id']
            action_type = action['action_type']
            data = action['data']

            if action_type == 101:  # move action
                vehicle_id = data['vehicle_id']
                target = data['target']

                # Update vehicle position in the game state
                try:
                    game_logic.game_state['vehicles'][vehicle_id]['position'] = target
                except Exception as e:
                    print(f"Error for move action is {e}")

            elif action_type == 102:  # Shoot action
                vehicle_id = data['vehicle_id']
                target = data['target']

                # Shooting action update the health od the targert vehicle
                #Implement additional logic to handle the shooting action

                if player_id not in current_attacks:
                    current_attacks[player_id] = []
                current_attacks[player_id].append(target)

        # Log the current attacks before updating previous_attacks
        print("Current attacks:", current_attacks)

        # Save current attacks as previous attacks
        self.previous_attacks.update(current_attacks)

        # Log the updated previous_attacks for debugging purposes
        print("Updated previous_attacks:", self.previous_attacks)

    def get_max_destruction_points(self):
        """Maximal number of points for destroying opponets vehical... can change."""
        return 10  # Example of max number points

