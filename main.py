import socket
from scripts.game_client import GameClient
from scripts.player import Player
from scripts.bot import Bot


def main():
    # def address and port server
    server_address = ("wgforge-srv.wargaming.net", 443)

    # create sock connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect on server
    sock.connect(server_address)

    try:
        player_name: str = "Boris"
        game_client: GameClient = GameClient.login(sock, player_name, num_turns=20)
        if not game_client:
            return
        bot: Bot = Bot(game_client.get_client_player_id(), player_name)
        while not game_client.game_over():
            while not game_client.round_finished():
                print("Round:", game_client.get_round(), "out of:", game_client.get_rounds())
                print("Turn:", game_client.get_cur_turn(), "out of:", game_client.get_turns_num())
                # provides bot his current state. Needs to be changed
                game_client.update_bot(bot)
                game_client.play_turn(bot.play_turn(game_client, sock))
                game_client.update_game_state()
            if not game_client.game_over():
                # To start next round
                game_client.send_turn_end()
        winner: Player = game_client.get_winner()
        if not winner:
            print("Game over. Result: Draw")
        else:
            print("WINNER WINNER CHICKEN DINNER:", winner.name)
        game_client.logout()

    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
