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

## Limits
- The maximum message size that the clients and the server can send to each other is 32kb. If they send larger messages
the other end will only receive the first 32kb of it and will most likely break.

## To Be Tested
- Test what happens if the server or client image has an entrypoint (`ENTRYPOINT` in Dockerfile instead of `CMD`)
- Test what happens when the value for `--server-arg` or `--client-arg` has a space in it.
