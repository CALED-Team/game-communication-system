# Docker Image Requirements

Both the server image and client image(s) need to have some requirements for GCS to run them.

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
