# Game Communication System

## Purpose
GCS allows one server and a given number of clients to communicate using standard IO having the server and each client
running in their own container. The communication happens with JSON messages. More about message formats and the
communications cycle in the "Program Cycle" section.

## Full Docs

- [Running the GCS](docs/running_the_gcs.md)
- [Image Requirements](docs/image_requirements.md)
- [Message Formats and Program Cycle](docs/interface.md)

## Debug Mode

You may run the GCS in debug mode by passing the `-d` flag to the controller. This will connect the server and clients
to a port on the network instead of the actual game files. I.e. the `/codequest/run.sh` won't run. You can then run
`sidecar_debugger_outside.py` file to connect to these ports and send messages. The script would require the port
number. The port number in debug mode would be 6000 for the server and will start from 6001 for each client. So if you
have two clients their ports would be 6001 and 6002. Using this script you can either send messages to the sidecar
you have connected to or listen to its next message (write `listen`).

Check out the `bin/debug_run.sh` file. This file runs the server with two clients, all using the same image.

So if you wanted to run GCS in debug mode with one server and two clients you would need to open 4 terminals, each with
one of these commands:

Run the GCS and containers:
```shell
./bin/debug_run.sh
```

Connect to the server container:
```shell
python src/sidecar_debugger_outside.py 6000
```

Connect to the first client container:
```shell
python src/sidecar_debugger_outside.py 6001
```

Connect to the second client container:
```shell
python src/sidecar_debugger_outside.py 6002
```

Then each terminal will expect you to be the program. Enter `listen` to get any incoming messages and enter your command
as what you want "the program" to print. The debug run is useful for debugging and developing the GCS not for debugging
the game server or clients.

## Limits
- The maximum message size that the clients and the server can send to each other is 32kb. If they send larger messages
the other end will only receive the first 32kb of it and will most likely break.

## To Be Tested
- Test what happens if the server or client image has an entrypoint (`ENTRYPOINT` in Dockerfile instead of `CMD`)
- Test what happens when the value for `--server-arg` or `--client-arg` has a space in it.
