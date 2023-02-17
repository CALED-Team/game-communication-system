debug = True

server_docker_file = "server_docker_file"
client_docker_file = "client_docker_file"

server_container_working_dir = "/codequest"
client_container_working_dir = "/codequest"

check_game_has_finished_interval = 10  # Wait this many seconds before checking again
end_game_keyword = (
    "END"  # The game sends this to its sidecar or server sidecar sends it to the client
)

wait_for_clients_time = (
    10  # How long should the server sidecar wait for clients initially (in seconds)
)
communication_delay = 0.1  # Wait this much longer for clients to respond because it has to go through sidecars
server_host_name = "cqserver"
server_port = 5000

sidecars_max_message_size = 32767  # In bytes
