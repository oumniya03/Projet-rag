#!/bin/bash

# Vérifier quel argument est passé au script
COMMAND=$1

case $COMMAND in
  up)
    echo "🚀 Démarrage des services..."
    docker-compose up -d
    ;;
  down)
    echo "🛑 Arrêt des services..."
    docker-compose down
    ;;
  build)
    echo "🔨 Construction des images..."
    docker-compose up --build -d
    ;;
  logs)
    echo "📋 Affichage des logs..."
    docker-compose logs -f
    ;;
  ingest)
    echo "ℹ️  L'ingestion se fait actuellement via l'interface web (http://localhost:3000)."
    echo "Si vous voulez tester l'ingestion API, utilisez le script de test python ou curl."
    ;;
  *)
    echo "Usage: ./docker.sh {up|down|build|ingest|logs}"
    exit 1
    ;;
esac