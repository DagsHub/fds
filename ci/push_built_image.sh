#!/usr/bin/env bash

# This is run inside CircleCI, which exports the needed environment
# variables. See .circleci/config.yaml.

docker login -u "$DOCKER_USER" -p "$DOCKER_PASS"

echo "Pushing ff image '${IMAGE_NAME}'..."

# Push images with names like hub.docker.com/mohithg/furiousflemingo:<branch>.<sha>
docker push "${IMAGE_NAME}"

echo "'${IMAGE_NAME}' pushed successfully."
