#!/bin/bash

# Creates a test image based on the server_base dockerfile and runs the server + two clients with that image.

# shellcheck disable=SC2164
GCS_DIR="$( dirname "$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )" )"
BIN_DIR="${GCS_DIR}/bin"
SRC_DIR="${GCS_DIR}/src"
DOCKERFILES_DIR="${GCS_DIR}/dockerfiles"
BASE_DIR="$(dirname $GCS_DIR)"

SERVER_TARGET_IMAGE=$1
SERVER_DIR="$BASE_DIR/$SERVER_TARGET_IMAGE"

CLIENT1_TARGET_IMAGE=$2
CLIENT1_DIR="$BASE_DIR/$CLIENT1_TARGET_IMAGE"

CLIENT2_TARGET_IMAGE=$2
CLIENT2_DIR="$BASE_DIR/$CLIENT2_TARGET_IMAGE"

cp "${DOCKERFILES_DIR}/server_base" "$SERVER_DIR/Dockerfile"
docker build $SERVER_DIR -t "$SERVER_TARGET_IMAGE"

cp "${DOCKERFILES_DIR}/client_base" "$CLIENT1_DIR/Dockerfile"
docker build $CLIENT1_DIR -t "$CLIENT1_TARGET_IMAGE"

cp "${DOCKERFILES_DIR}/client_base" "$CLIENT2_DIR/Dockerfile"
docker build $CLIENT2_DIR -t "$CLIENT2_TARGET_IMAGE"

cd "$SRC_DIR" || exit
cat <<EOF > _temp_clients_file.json
[
  {
    "id": "client1",
    "name": "Client One!",
    "image": "$CLIENT1_TARGET_IMAGE"
  },
  {
    "id": "client2",
    "name": "Client Two!",
    "image": "$CLIENT2_TARGET_IMAGE"
  }
]
EOF
python3 controller.py "$SERVER_TARGET_IMAGE" _temp_clients_file.json
rm _temp_clients_file.json
