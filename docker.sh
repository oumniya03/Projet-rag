#!/bin/bash

# Script de gestion du projet RAG
case "$1" in
  build)
    docker-compose build
    ;;
  up)
    docker-compose up -d
    ;;
  down)
    docker-compose down
    ;;
  ingest)
    docker-compose run --rm backend python ingest.py
    ;;
  logs)
    docker-compose logs -f
    ;;
  *)
    echo "Usage: ./docker.sh {build|up|down|ingest|logs}"
    exit 1
    ;;
esac