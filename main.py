import pygame
import requests
import json
import socket
import math
from map_display.map_plot import plot_hexagonal_map
from scripts.grid import Grid
from scripts.map import draw_hex_grid
from scripts.map import screen
from scripts.player import Player
from scripts.game_logic import GameLogic

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

def main():
    # def address and port server
    server_address = ("wgforge-srv.wargaming.net", 443)

    # create sock connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect on server
    sock.connect(server_address)

    try:
        response_data = login_request("Marko", sock)
        print(response_data)

        if response_data:
            print(f"Succesfull log in {response_data}")
        else:
            print("Login Fail")

        # 2. Testing GAME_STATE request
        game_state = game_state_request(sock)
        print("\nTesting GAME_STATE request:")
        print(f"Game state: {game_state}")
        game_state_data = game_state['vehicles']
        # print("\nTesting TURN request:")
        # turn_request(sock)


        map_data = map_request(sock)
        game_actions = game_actions_request(sock)

        # GameLogic.update_game_state(game_state['vehicles'])
        #GameLogic.play_game(turn , game_state, game_actions)
        # # 2. Logout request
        # print("\nTesting LOGOUT request:")
        # logout_request(sock)






        print(game_state_data)
        # player_instance.add_tanks(game_state_data)
        #
        # player_instance.earn_base_capture_points(game_state,map_data)

        # Na primer, možete ažurirati igrače na osnovu podataka o stanju igre
        # Ako imate instancu igrača (player_instance):
        # player_instance.update_vehicles(game_state)

        # Dalje operacije...

        # Da biste koristili druge funkcije (na primer, map_request, chat_request, itd.), dodajte ih ovde...
        #
        # 3. Testing GAME_ACTIONS request

        # print("\nTesting GAME_ACTIONS request:")
        # game_actions_request(sock)

        # Assuming map_data contains 'grid' and 'base' info

        base = map_data['content']['base']  # Adjust this according to actual map data format


        # Initialize GameLogic
        game_logic = GameLogic(response_data,base)

        # Start the game
        game_logic.play_game(sock)

        # # 5. Testing CHAT request
        # print("\nTesting CHAT request:")
        # chat_message = "Hello, this is a test message."
        # chat_request(sock, chat_message)
        #
        # # 6. Testing MOVE request
        # print("\nTesting MOVE request:")
        # move_request(sock, vehicle_id=1, target={"x": 1, "y": 1, "z": -2})
        #
        # # 7. Testing SHOOT request
        # print("\nTesting SHOOT request:")
        # shoot_request(sock, vehicle_id=1, target={"x": -1, "y": -1, "z": 2})
        # # 3. Testing MAP request
        # print("Testing MAP request:")
        # map_data = map_request(sock)
        # if map_data:
        #     plot_hexagonal_map(map_data)
        map_data = map_request(sock)

        if map_data:
            print("Map data received.")
        else:
            print("Failed to retrieve map data.")

        # Glavna petlja
        running = True
        while running:
            # Obrada događaja
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Očistite ekran
            screen.fill((0, 0, 0))  # Crna pozadina

            # Pozovite funkciju za crtanje heksagonalne mreže
            draw_hex_grid(screen, map_data)

            # Osvježite ekran
            pygame.display.flip()
    except Exception as e:
        print(f"Error during connection or request: {e}")
    finally:
        # closeing connection
        # sock.close()
        pass
if __name__ == "__main__":
    main()



