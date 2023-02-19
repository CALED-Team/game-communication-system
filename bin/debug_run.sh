#!/bin/bash

# Creates a test image based on the server_base dockerfile and runs the server + two clients with that image.

# shellcheck disable=SC2164
BASE_DIR="$( dirname "$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )" )"
BIN_DIR="${BASE_DIR}/bin"
SRC_DIR="${BASE_DIR}/src"
DOCKERFILES_DIR="${BASE_DIR}/dockerfiles"

TARGET_IMAGE="cq_test_image:latest"

cp "${DOCKERFILES_DIR}/server_base" "${BIN_DIR}/Dockerfile"

cd "$BIN_DIR" || exit
docker build . -t "$TARGET_IMAGE"
rm "${BIN_DIR}/Dockerfile"

cd "$SRC_DIR" || exit
cat <<EOF > _temp_clients_file.json
[
  {
    "id": "client1",
    "name": "Client One!",
    "image": "cq_test_image:latest"
  },
  {
    "id": "client2",
    "name": "Client Two!",
    "image": "cq_test_image:latest"
  }
]
EOF
python3 controller.py "$TARGET_IMAGE" _temp_clients_file.json -d
rm _temp_clients_file.json
