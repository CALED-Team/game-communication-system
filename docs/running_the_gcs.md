# Running The GCS

The main entrypoint for GCS is the `src/controller.py` file which can be run like any Python script (you need to be in
`src` directory).

## How to Run
The starting point of GCS is `controller.py`. Here's a sample command to run the server with two clients:

```shell
python controller.py server_image_name:tag clients.json --server-arg map3
```

This example will tell GCS to use the `server_image_name:tag` as the base image for server and read the clients' info
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
