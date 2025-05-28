#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 [env]"
  echo "Please provide an environment: prod, staging, or local."
  exit 1
fi

ENV=$1

case $ENV in
    prod)
    echo "Running production Docker Compose stack..."
    git pull
    docker compose -f deployments/docker-compose.production.yml build
    docker compose -f deployments/docker-compose.production.yml down
    docker compose -f deployments/docker-compose.production.yml up -d
    ;;
    staging)
    echo "Running staging Docker Compose stack..."
    git pull
    docker compose -f deployments/docker-compose.staging.yml build
    docker compose -f deployments/docker-compose.staging.yml down
    docker compose -f deployments/docker-compose.staging.yml up -d
    ;;
    local)
    echo "Running local Docker Compose stack..."
    git pull
    docker compose -f deployments/docker-compose.local.yml build
    docker compose -f deployments/docker-compose.local.yml down
    docker compose -f deployments/docker-compose.local.yml up
    ;;
    *)
    echo "Invalid environment: $ENV"
    echo "Please provide a valid environment: prod, staging, or local."
    exit 1
    ;;
esac