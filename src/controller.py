import argparse
import json
import logging
import os
import secrets
import time

import docker
from docker.models.containers import Container
from docker.models.networks import Network

import config

logger = logging.getLogger(__name__)
log = logger.info


def create_network(docker_client, game_secret):
    network_name = f"cq_network_{game_secret}"
    return docker_client.networks.create(network_name)


def start_server(
    docker_client,
    network_name,
    server_image,
    game_secret,
    server_args=tuple(),
    sidecar_args=tuple(),
):
    with open(config.server_docker_file, "w") as f:
        f.write(f"FROM {server_image}\n")
        # Make sure the working directory exists
        f.write(f"RUN mkdir -p {config.server_container_working_dir}\n")
        # Put the sidecar and config file in
        f.write(f"COPY config.py {config.server_container_working_dir}\n")
        f.write(f"COPY server_sidecar.py {config.server_container_working_dir}\n")

        if config.debug:
            f.write(
                f"COPY sidecar_debugger_inside.py {config.server_container_working_dir}\n"
            )

        server_args = " ".join(list(server_args))
        sidecar_args = " ".join([game_secret] + list(sidecar_args))

        # If it's debug, connect the sidecar to IO directly
        if config.debug:
            program_exe = f"EXEC:'python {config.server_container_working_dir}/sidecar_debugger_inside.py 6000'"
        else:
            program_exe = (
                f"EXEC:'sh {config.server_container_working_dir}/run.sh {server_args}'"
            )

        # Run the server alongside the sidecar
        f.write(
            f'ENTRYPOINT ["/bin/sh", "-c", "echo STARTED-{game_secret} && '
            f"socat -v "
            f"EXEC:'python {config.server_container_working_dir}/server_sidecar.py {sidecar_args}' "
            f'{program_exe}"]\n'
        )

    # Build the image
    server_image_name = f"cq_server_image_{game_secret}"
    docker_client.images.build(
        path=".",
        dockerfile=config.server_docker_file,
        rm=True,
        forcerm=True,
        tag=server_image_name,
    )

    # Remove the temp files
    os.remove("server_docker_file")

    return docker_client.containers.run(
        server_image_name,
        network=network_name,
        name=f"cq_server_{game_secret}",
        hostname=config.server_host_name,
        ports={6000: 6000} if config.debug else None,
        auto_remove=not config.debug,
        detach=True,
    )


def send_game_started_signal_to_server(server_container: Container):
    server_container.exec_run(
        cmd=f"/bin/sh -c 'touch {config.server_container_working_dir}/GAME_STARTED'",
        detach=True,
        stdout=False,
    )


def start_client(
    docker_client,
    network_name,
    client_index,
    client,
    game_secret,
    client_args=tuple(),
    sidecar_args=tuple(),
):
    with open(config.client_docker_file, "w") as docker_file:
        docker_file.write(f"FROM {client['image']}\n")
        # Make sure the working directory exists
        docker_file.write(f"RUN mkdir -p {config.client_container_working_dir}\n")
        # Put the sidecar and the config file in
        docker_file.write(f"COPY config.py {config.client_container_working_dir}\n")
        docker_file.write(
            f"COPY client_sidecar.py {config.client_container_working_dir}\n"
        )

        if config.debug:
            docker_file.write(
                f"COPY sidecar_debugger_inside.py {config.client_container_working_dir}\n"
            )

        client_args = " ".join(list(client_args))

        # Sidecar args might have weird stuff in them, we have to write in a file then put the file inside image
        sidecar_args = "\n".join(
            [game_secret, client["id"], client["name"]] + list(sidecar_args)
        )
        with open("_temp_sidecar_args_file", "w") as temp_file:
            temp_file.write(sidecar_args)
        sidecar_args_file = f"{config.client_container_working_dir}/sidecar_args"
        docker_file.write(f"COPY _temp_sidecar_args_file {sidecar_args_file}\n")

        # If it's debug, connect the sidecar to IO directly
        if config.debug:
            program_exe = f"EXEC:'python {config.server_container_working_dir}/sidecar_debugger_inside.py 6000'"
        else:
            program_exe = (
                f"EXEC:'sh {config.client_container_working_dir}/run.sh {client_args}'"
            )

        # Run the client alongside the sidecar
        docker_file.write(
            f'ENTRYPOINT ["/bin/sh", "-c", "echo STARTED-{game_secret} && '
            f"socat -v "
            f"EXEC:'python {config.client_container_working_dir}/client_sidecar.py {sidecar_args_file}' "
            f'{program_exe}"]\n'
        )

    # Build the image
    client_image_name = f"cq_client_image_{client['id']}_{game_secret}"
    docker_client.images.build(
        path=".",
        dockerfile=config.client_docker_file,
        rm=True,
        forcerm=True,
        tag=client_image_name,
    )

    # Remove the temp files
    os.remove("_temp_sidecar_args_file")
    os.remove("client_docker_file")

    return docker_client.containers.run(
        client_image_name,
        name=f"cq_client_{str(client_index)}_{game_secret}",
        network=network_name,
        auto_remove=not config.debug,
        detach=True,
        ports={6000: 6001 + client_index} if config.debug else None,
        mem_limit=config.client_memory_limit,
    )


def run_game(server_image: str, clients, server_args=tuple(), client_args=tuple()):
    """
    Runs a game between given images
    :param server_image: The game server image
    :param clients: List of clients like [{"id": "1235", "name": "Team A", "image": "Docker image"}, ...]
    :param server_args: List of positional arguments to be passed to the game server in the CLI.
    :param client_args: List of positional arguments to be passed to each client in the CLI.
    """
    docker_client = docker.from_env()
    game_secret = secrets.token_urlsafe(8).lower()
    network: Network = create_network(docker_client, game_secret)
    network_name = network.name

    log("Starting server...")
    server_container = start_server(
        docker_client, network_name, server_image, game_secret, server_args=server_args
    )
    log(f"Server started: {server_container.short_id}")

    client_containers = []
    for i, client in enumerate(clients):
        log(f"Starting client {client['name']}")
        client_containers.append(
            start_client(
                docker_client,
                network_name,
                i,
                client,
                game_secret,
                client_args=client_args,
            )
        )
        log(f"Client started: {client_containers[-1].short_id}")

    log("All clients started.")

    send_game_started_signal_to_server(server_container)

    server_container.reload()
    while server_container.status == "running":
        time.sleep(config.check_game_has_finished_interval)
        server_container.reload()

    network.remove()
    log("The game has finished!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs the server and clients along with their sidecars inside containers on the same network.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "server_image", help="Server image name and tag e.g. image_name:latest"
    )
    parser.add_argument(
        "clients_file",
        help='JSON file containing clients information like `[{"id": ..., "name": ..., "image": "image:tag"}, ...]`',
    )
    parser.add_argument(
        "--server-arg",
        help="Positional arguments to be passed to the server",
        action="append",
        dest="server_args",
        default=tuple(),
    )
    parser.add_argument(
        "--client-arg",
        help="Positional arguments to be passed to the clients",
        action="append",
        dest="client_args",
        default=tuple(),
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Connects sidecars to IO instead of apps",
        dest="debug",
    )
    args = parser.parse_args()

    config.debug = args.debug

    with open(args.clients_file) as f:
        clients = json.loads(f.read())

    try:
        for client in clients:
            client["id"] = str(client["id"])
            client["name"] = str(client["name"])
            client["image"] = str(client["image"])
    except KeyError:
        raise Exception(
            "Clients are not passed correctly. Make sure you the file has a valid JSON with all the fields."
        )

    run_game(args.server_image, clients, args.server_args, args.client_args)
