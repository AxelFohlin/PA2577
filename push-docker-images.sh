#!/bin/bash

# Set your Docker Hub username and the repository name
DOCKER_USERNAME="axelfohlin"
REPOSITORY_NAME="pa2577"

# Build, tag, and push frontend image
echo "Building frontend image..."
docker build -t pa2577_frontend ./frontend
docker tag pa2577_frontend:latest ${DOCKER_USERNAME}/${REPOSITORY_NAME}:frontend
docker push ${DOCKER_USERNAME}/${REPOSITORY_NAME}:frontend

# Build, tag, and push user-management image
echo "Building user-management image..."
docker build -t pa2577_user-management ./user-management
docker tag pa2577_user-management:latest ${DOCKER_USERNAME}/${REPOSITORY_NAME}:user-management
docker push ${DOCKER_USERNAME}/${REPOSITORY_NAME}:user-management

# Build, tag, and push database image
echo "Building database image..."
docker build -t pa2577_db ./db
docker tag pa2577_db:latest ${DOCKER_USERNAME}/${REPOSITORY_NAME}:db
docker push ${DOCKER_USERNAME}/${REPOSITORY_NAME}:db

echo "All images have been built, tagged, and pushed to ${DOCKER_USERNAME}/${REPOSITORY_NAME}."
