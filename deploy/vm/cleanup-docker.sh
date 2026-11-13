#!/bin/sh
# Nettoyage Docker « intelligent » : libere de l'espace sans toucher aux volumes
# (pgdata, grafana-data, minio-data, et tout volume nomme) ni aux conteneurs en cours. Idempotent.
# Usage (utilisateur deploy) : sh deploy/vm/cleanup-docker.sh
set -eu

echo "== Nettoyage Docker"
df -h / | tail -n 1 || true
docker system df || true

# Conteneurs arretes / reseau orphelins
docker container prune -f >/dev/null 2>&1 || true
docker network prune -f >/dev/null 2>&1 || true

# Images non utilisees par un conteneur (anciens tags GHCR inclus)
docker image prune -af >/dev/null 2>&1 || true

# Cache build / buildx (souvent volumineux apres plusieurs CD)
docker builder prune -af >/dev/null 2>&1 || true
docker buildx prune -af >/dev/null 2>&1 || true

# Pas de « docker volume prune » : apres un container prune, des volumes nommes
# (pgdata, grafana-data, …) pourraient devenir « unused » et etre effaces.

echo "== Apres nettoyage (volumes conserves)"
docker system df || true
df -h / | tail -n 1 || true
