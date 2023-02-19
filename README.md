# Game Communication System

## Purpose
GCS allows one server and a given number of clients to communicate using standard IO having the server and each client
running in their own container.

## How to use
The starting point of GCS is `controller.py`. Here's a sample command to run the server with two clients:

```shell
python src/controller.py server_image_name:tag clients.json --server-arg map3
```

This example will tell GCS to use the `server_image_name:tag` as the base image for server and read the clients info
from the file `clients.json`.

Note that all Docker images should either be available on the host machine or the host should be able to pull them.
I.e. GCS doesn't know anything about the images and where they are.

## Clients File
The clients file should look like this:

```json
[
  {
    "id": "client1",
    "name": "Client One!",
    "image": "repo_name/client_one_image:tag"
  },
  {
    "id": "client2",
    "name": "Client Two!",
    "image": "client_two_image:tag"
  }
]
```

You can put as many clients as you want in the file - each will run in a separate container.

## Available Arguments

The controller scripts expects 2 required arguments and 3 optional arguments.
You can see all arguments in the CLI by running `python controller.py -h`. Here's a list of them with their description:

**Required Arguments**
- Server Image: the image name for the game server - must be passed as the first argument
- Clients File: the file that contains information about all clients - must be passed as the second argument

**Optional Arguments**
- `-d`: Pass if you want to run in debug mode. Refer to the "Debug Mode" section of the docs for more details.
- `--server-arg`: Any arguments you pass here will be passed directly to the game server. You
may use this several times to provide several arguments. Read the "Server Image" section of the docs for more details.
- `--client-arg`: Any arguments you pass here will be passed directly to each of the clients. You
may use this several times to provide several arguments. Read the "Client Image" section of the docs for more details.

## Server Image

The server image should be passed in the CLI arguments but it needs to have a few requirements:
- It must be a Linux based image.
- It must have `socat` installed.
- It must have a file `/codequest/run.sh` which runs the game server. This file should not do anything more than running
the actual game file because the standard IO of this file is going to be linked to the GCS. So if you run a command
that doesn't accept standard input (e.g. `pip install ...`) the GCS will crash or if you print logs in the file, they
will be sent to the GCS as it's listening to this file's standard output. If all you need to do is run a Python file,
write `python your_file.py` in this file.
- You may use the `dockerfiles/server_base` file as a starting point for your Dockerfile.

## Client Image

The client image for each client should be specified in the clients JSON file but each image needs a few requirements:
- It must be a Linux based image.
- It must have `socat` installed.
- It must have a file `/codequest/run.sh` which runs the client. This file should not do anything more than running
the actual client because the standard IO of this file is going to be linked to the GCS. So if you run a command
that doesn't accept standard input (e.g. `pip install ...`) the GCS will crash or if you print logs in the file, they
will be sent to the GCS as it's listening to this file's standard output. If all you need to do is run a Python file,
write `python your_file.py` in this file.
- You may use the `dockerfiles/client_base` file as a starting point for your Dockerfile.

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
