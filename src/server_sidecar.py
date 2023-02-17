"""
Arguments needed by the server sidecar:
game_secret: The secret id for the game, created and passed by the controller
client_name: The name of this client, to be used in the game server to identify the playing team
"""

import json
import os
import signal
import socket
import sys
import time
import typing as t
from collections import namedtuple

import config


class CustomTimeout(Exception):
    pass


def raise_timeout(*_):
    raise CustomTimeout


Client = namedtuple("Client", "connection name")


def wait_for_game_start():
    file_path = config.server_container_working_dir + "/GAME_STARTED"
    while not os.path.isfile(file_path):
        time.sleep(3)


def start_listening():
    # host = socket.gethostname()
    host = "0.0.0.0"
    port = config.server_port
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen()
    return server_socket


def accept_connections(server_socket, game_secret):
    """
    Accepts as many incoming connections as they are since the sidecar is not supposed to know the number of players.
    But the connection needs to send the game secret otherwise will be discarded.
    :returns: Named Tuple of clients like (connection, name)
    """
    # Tuples of (connection, name)
    clients = []
    signal.signal(signal.SIGALRM, raise_timeout)
    signal.alarm(config.wait_for_clients_time)

    try:
        while True:
            # Wait until new connection
            conn, address = server_socket.accept()
            # The first data sent should be the game secret
            message = conn.recv(config.sidecars_max_message_size).decode()
            try:
                message = json.loads(message)
                client_secret = message["secret"]
                client_name = message["name"]
            except (KeyError, TypeError):
                client_secret = client_name = None

            if client_secret == game_secret:
                clients.append(Client(conn, client_name))
    except CustomTimeout:
        pass

    return clients


def set_clients_blocking_state(clients, blocking=True):
    for client in clients:
        client.connection.setblocking(blocking)


def accept_client_messages(clients):
    """
    Receives a message from each client if they have a message.
    If they don't, it will return None for that client.
    """
    responses = {}
    for client in clients:
        try:
            message = client.connection.recv(config.sidecars_max_message_size)
            responses[client.name] = json.loads(message)
        except (OSError, TypeError):
            # Either the client hasn't responded or their response isn't json
            responses[client.name] = None
    return responses


def close_clients(clients):
    for client in clients:
        client.connection.send(
            json.dumps({"message": config.end_game_keyword, "time": 0}).encode("utf-8")
        )
        client.connection.close()


def say(thing):
    """
    Says "thing" to the game by printing it.
    Whatever thing is passed it will be converted to json before printing.
    """
    print(json.dumps(thing))


def start_broadcast_cycle(clients: t.List[Client]):
    while True:
        # Receive what the server has to say to each client
        message_for_clients = json.loads(input())
        # How long should we wait for clients response
        turn_wait_time = float(input())

        # If the message is the game finish message just close
        if message_for_clients == config.end_game_keyword:
            return

        # Is there a send to all message?
        send_to_all = "" in message_for_clients.keys()
        for client in clients:
            # Prioritize the targeted message over send to all
            message = message_for_clients[""] if send_to_all else None
            message = (
                message_for_clients[client.name]
                if client.name in message_for_clients.keys()
                else message
            )
            wrapped_message = {"message": message, "time": turn_wait_time}
            client.connection.send(json.dumps(wrapped_message).encode("utf-8"))

        # Give clients processing time
        time.sleep(turn_wait_time + config.communication_delay)
        clients_response = accept_client_messages(clients)
        say(clients_response)


def run(game_secret):
    server_socket = start_listening()
    wait_for_game_start()
    clients: t.List[Client] = accept_connections(server_socket, game_secret)

    say({"clients": [client[1] for client in clients]})
    # From this point, the clients should be non-blocking
    set_clients_blocking_state(clients, False)
    start_broadcast_cycle(clients)
    close_clients(clients)


if __name__ == "__main__":
    secret = sys.argv[-1]
    run(secret)
