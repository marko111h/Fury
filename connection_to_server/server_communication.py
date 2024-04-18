import socket
import json

def login_request(name,sock):

    # Create login request
    login_request = b'\x01\x00\x00\x00\x10\x00\x00\x00{"name":"%s"}' % name.encode('utf-8')
    sock.sendall(login_request)

    # Prepering response
    buffer_size = 4096
    response = sock.recv(buffer_size)

    # ParsingJSOn part answer
    json_response = response[8:]

    # Decoder Json Answer
    try:
        response_data = json.loads(json_response)
    except json.JSONDecodeError as e:
        print("Error decode JSON-a:", e)
        response_data = None


    return response_data

def logout_request(sock):

    logout_request = b'\x02\x00\x00\x00\x00\x00\x00\x00' # {action (2)} + {data length (0)}
    sock.sendall(logout_request)


    #Accept response
    response = sock.recv(4096)

    # Decoding the result code
    result_code = int.from_bytes(response[:4], 'little')

    if result_code != 0:
        error_length = int.from_bytes(response[4:8],'little')
        error_message = response[8:8 + error_length].decode('utf-8')
        print(f"Error during logout: {error_message}")

    else:
        print("Logout Succesfull")

def map_request(sock):
    map_request = b'\x03\x00\x00\x00\x00\x00\x00\x00'  # {action (3)} + {data length (0)}
    sock.sendall(map_request)

    #Accept response
    response = sock.recv(4096)

    # Decoding the result code
    result_code = int.from_bytes(response[:4],'little')

    # if result okey, parsing map
    if result_code == 0:
        data_length = int.from_bytes(response[4:8],'little')
        json_data = response[8:8 + data_length].decode('utf-8')
        mapa_data = json.loads(json_data)
        print("Map data:", mapa_data)
        return mapa_data
    else:
        error_length = int.from_bytes(response[4:8], 'little')
        error_message = response[8:8 + error_length].decode('utf-8')
        print(f"Error during map request: {error_message}")
def game_state_request(sock):
    game_state_request = b'\x04\x00\x00\x00\x00\x00\x00\x00'  # {action (4)} + {data length (0)}
    sock.sendall(game_state_request)

    #Accept response
    response = sock.recv(4096)

    result_code = int.from_bytes(response[:4], 'little')

    if result_code == 0:
        data_length = int.from_bytes(response[4:8], 'little')
        json_data = response[8:8 + data_length].decode('utf-8')
        game_state = json.loads(json_data)
        print("Game state:", game_state)
        return game_state
    else:
        error_length = int.from_bytes(response[4:8],'little')
        error_message = response[8:8 + error_length].decode('utf-8')
        print(f"Error during game state request: {error_message}")

def game_actions_request(sock):
    game_actions_request = b'\x05\x00\x00\x00\x00\x00\x00\x00'  # {action (5)} + {data length (0)}
    sock.sendall(game_actions_request)

    # Receiving a response
    response = sock.recv(4096)

    # Decoding the result code

    result_code = int.from_bytes(response[:4], 'little')

    # If the result is OKEY, parsing the list of actions
    if result_code == 0:
        data_length = int.from_bytes(response[4:8], 'little')
        json_data = response[8:8 + data_length].decode('utf-8')
        game_actions = json.loads(json_data)
        print("Game actions:", game_actions)
        return game_actions
    else:
        error_length = int.from_bytes(response[4:8], 'little')
        error_message = response[8:8 + error_length].decode('utf-8')
        print(f"Error during game actions request: {error_message}")
def turn_request(sock):
    turn_request = b'\x06\x00\x00\x00\x00\x00\x00\x00'  # {action (6)} + {data length (0)}
    sock.sendall(turn_request)

    # Receiving a response
    response = sock.recv(4096)

    # Decoding the result code
    result_code = int.from_bytes(response[:4], 'little')

    # If the result is OKEY, confirming the successful move
    if result_code == 0:
        print("Turn successful.")
    else:
        error_length = int.from_bytes(response[4:8], 'little')
        error_message = response[8:8 + error_length].decode('utf-8')
        print(f"Error during turn request: {error_message}")
def chat_request(sock, message):
    message_json = json.dumps({"message": message}).encode('utf-8')
    data_length = len(message_json)

    # Forming a chat request
    chat_request = (b'\x64\x00\x00\x00'  # action (100)
                    + data_length.to_bytes(4, 'little')
                    + message_json)

    sock.sendall(chat_request)

    # Receiving a response
    response = sock.recv(4096)

    # Decoding the result code
    result_code = int.from_bytes(response[:4], 'little')

    # If result is OKEY, success message
    if result_code == 0:
        print("Chat message sent.")
    else:
        error_length = int.from_bytes(response[4:8], 'little')
        error_message = response[8:8 + error_length].decode('utf-8')
        print(f"Error during chat request: {error_message}")
def move_request(sock,vehicle_id, target):
    move_json = json.dumps({"vehicle_id": vehicle_id, "target": target}).encode('utf-8')
    data_length = len(move_json)

    # Formation of move request
    move_request = (b'\x65\x00\x00\x00'  # action (101)
                    + data_length.to_bytes(4, 'little')
                    + move_json)

    sock.sendall(move_request)

    # Receiving a response
    response = sock.recv(4096)

    # Decoding the result code
    result_code = int.from_bytes(response[:4], 'little')

    # If the result is OKEY, successful move
    if result_code == 0:
        print("Move successful.")
    else:
        error_length = int.from_bytes(response[4:8], 'little')
        error_message = response[8:8 + error_length].decode('utf-8')
        print(f"Error during move request: {error_message}")
def shoot_request(sock, vehicle_id, target):
    shoot_json = json.dumps({"vehicle_id": vehicle_id, "target": target}).encode('utf-8')
    data_length = len(shoot_json)

    # Forming a shoot request
    shoot_request = (b'\x66\x00\x00\x00'  # action (102)
                     + data_length.to_bytes(4, 'little')
                     + shoot_json)

    sock.sendall(shoot_request)

    # Receiving a response
    response = sock.recv(4096)

    # Decoding the result code
    result_code = int.from_bytes(response[:4], 'little')

    # If the result is OKEY, successful firing
    if result_code == 0:
        print("Shoot successful.")
    else:
        error_length = int.from_bytes(response[4:8], 'little')
        error_message = response[8:8 + error_length].decode('utf-8')
        print(f"Error during shoot request: {error_message}")
