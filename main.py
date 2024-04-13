import pygame
import requests
import json
import socket

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
        # # connecting with server
        # sock.connect(server_address)

        # 1. Login
        response_data = login_request("Marko", sock)

        if response_data:
            print(f"Succesfull log in {response_data}")
        else:
            print("Login Fail")

        # # 2. Logout request
        # print("\nTesting LOGOUT request:")
        # logout_request(sock)

        # 3. Testing MAP request
        print("Testing MAP request:")
        map_request(sock)

        # 2. Testing GAME_STATE request
        print("\nTesting GAME_STATE request:")
        game_state_request(sock)
        #
        # 3. Testing GAME_ACTIONS request
        print("\nTesting GAME_ACTIONS request:")
        game_actions_request(sock)

        # 4. Testing TURN request
        print("\nTesting TURN request:")
        turn_request(sock)

        # 5. Testing CHAT request
        print("\nTesting CHAT request:")
        chat_message = "Hello, this is a test message."
        chat_request(sock, chat_message)

        # 6. Testing MOVE request
        print("\nTesting MOVE request:")
        move_request(sock, vehicle_id=1, target={"x": 1, "y": 1, "z": -2})

        # 7. Testing SHOOT request
        print("\nTesting SHOOT request:")
        shoot_request(sock, vehicle_id=1, target={"x": -1, "y": -1, "z": 2})
    except Exception as e:
        print(f"Error during connection or request: {e}")
    finally:
        # closeing connection
        # sock.close()
        pass
if __name__ == "__main__":
    main()



