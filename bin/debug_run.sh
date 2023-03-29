#!/bin/bash

# Creates a test image based on the server_base dockerfile and runs the server + two clients with that image.

# shellcheck disable=SC2164
BASE_DIR="$( dirname "$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )" )"
BIN_DIR="${BASE_DIR}/bin"
SRC_DIR="${BASE_DIR}/src"
DOCKERFILES_DIR="${BASE_DIR}/dockerfiles"

TARGET_IMAGE="game-server-23"
CLIENT_TARGET_IMAGE="game-client-23"

cp "${DOCKERFILES_DIR}/server_base" "$(dirname $BASE_DIR)/game-server-23/Dockerfile"
cd "$BIN_DIR" || exit
docker build $(dirname $BASE_DIR)/game-server-23 -t "$TARGET_IMAGE"

cp "${DOCKERFILES_DIR}/client_base" "$(dirname $BASE_DIR)/game-client-23/Dockerfile"
cd "$BIN_DIR" || exit
docker build $(dirname $BASE_DIR)/game-client-23 -t "$CLIENT_TARGET_IMAGE"

cd "$SRC_DIR" || exit
cat <<EOF > _temp_clients_file.json
[
  {
    "id": "client1",
    "name": "Client One!",
    "image": "$CLIENT_TARGET_IMAGE"
  },
  {
    "id": "client2",
    "name": "Client Two!",
    "image": "$CLIENT_TARGET_IMAGE"
  }
]
EOF
python3 controller.py "$TARGET_IMAGE" _temp_clients_file.json
rm _temp_clients_file.json
