#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/..

cd ${SCRIPT_DIR}

USER_NAME=dev
USER_GID=$(id -g $(id -u -n))
USER_UID=$(id -u $(id -u -n))
printf "USER_NAME=${USER_NAME}\n\
USER_PASSWORD=user\n\
GID_NUMBER=${USER_GID}\n\
UID_NUMBER=${USER_UID}\n\
SSH_PORT=2000\n\
DOCKER_IMAGE_ROOT=ubuntu:22.04\n\
CONAN_USERNAME=\"\"\n\
CONAN_PASS_KEY=\"\"\n" > ${SCRIPT_DIR}/.env

grep -qxF 'xhost +local:' ~/.bashrc || echo "xhost +local:" >>  ~/.bashrc

if ! command -v docker-compose &> /dev/null
then
    docker compose build
else
    docker-compose build
fi

echo "Config done"
