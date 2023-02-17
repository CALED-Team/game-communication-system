"""
Arguments needed by the client sidecar:
game_secret: The secret id for the game, created and passed by the controller
client_name: The name of this client, to be used in the game server to identify the playing team
"""

import json
import select
import socket
import sys

import config


def connect_to_server_sidecar(game_secret, client_name):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((config.server_host_name, config.server_port))
    message = json.dumps({"secret": game_secret, "name": client_name})
    client_socket.send(message.encode("utf-8"))
    return client_socket


def say(thing):
    """
    Says "thing" to the client by printing it.
    Whatever thing is passed it will be converted to json before printing.
    """
    print(json.dumps(thing), flush=True)


def start_game_cycle(connection):
    while True:
        server_message = connection.recv(config.sidecars_max_message_size).decode()
        try:
            server_message = json.loads(server_message)
            message = server_message["message"]
            turn_time = server_message["time"]
        except (KeyError, TypeError):
            # Well, seems like server is sending nonsense. I suppose we crash?
            raise

        if message == config.end_game_keyword:
            # Game finished!
            return

        # Flush any prints from previous turn
        while select.select([sys.stdin], [], [], 0)[0]:
            sys.stdin.readline()

        # Give the new information to the client
        say(server_message)

        # Time to wait for the client's response
        client_responded, _, __ = select.select([sys.stdin], [], [], turn_time)
        if client_responded:
            response = sys.stdin.readline().strip()
            try:
                json.loads(response)
            except TypeError:
                # Bad message, too bad.
                pass
            else:
                connection.send(response.encode("utf-8"))
        else:
            # Client didn't respond in time, or at all.
            pass


def run(game_secret, client_name):
    connection = connect_to_server_sidecar(game_secret, client_name)
    start_game_cycle(connection)
    connection.close()


if __name__ == "__main__":
    secret, name = sys.argv[1:]
    run(secret, name)
