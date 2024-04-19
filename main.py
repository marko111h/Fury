import socket
from scripts.game_client import GameClient


def main():
    # def address and port server
    server_address = ("wgforge-srv.wargaming.net", 443)

    # create sock connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect on server
    sock.connect(server_address)

    try:
        game_client: GameClient = GameClient.login(sock, "Boris", num_turns=20)
        if not game_client:
            return
        # TODO: check for winner and process winner and test with 5 capture points
        while not game_client.round_finished():
            print("Round:", game_client.get_round())
            print("Turn:", game_client.get_cur_turn(), "out of:", game_client.get_turns_num())
            game_client.play_turn()
            game_client.update_game_state()

        game_client.logout()

    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
