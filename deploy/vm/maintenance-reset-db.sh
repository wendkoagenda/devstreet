#!/bin/sh
# Reset du volume Postgres (pgdata) d'un namespace. Execute par l'utilisateur deploy :
#   cd /opt/apps/<namespace> && sh -s < deploy/vm/maintenance-reset-db.sh
# Attend compose.env et deploy/compose/compose.yml (deja poses par un deploiement).
# Ne touche pas au proxy ni a /srv/public. Pas de redeploiement.
set -eu

fail() {
  echo "ERREUR : $1" >&2
  exit 1
}

[ -f ./compose.env ] || fail "compose.env introuvable (deploiement jamais fait ?)."
. ./compose.env

printf '%s' "$DEPLOY_NAMESPACE" | grep -Eq '^[a-z0-9][a-z0-9-]{1,40}$' || fail "DEPLOY_NAMESPACE invalide."
[ "$(pwd)" = "/opt/apps/$DEPLOY_NAMESPACE" ] || fail "ce script doit s'executer dans /opt/apps/$DEPLOY_NAMESPACE (dossier actuel : $(pwd))."
[ "$DEPLOY_DB_MODE" = "interne" ] || fail "DEPLOY_DB_MODE=$DEPLOY_DB_MODE : reset pgdata reserve au mode interne."

APP_DIR="/opt/apps/$DEPLOY_NAMESPACE"
COMPOSE_FILE="$APP_DIR/deploy/compose/compose.yml"
[ -f "$COMPOSE_FILE" ] || fail "deploy/compose/compose.yml introuvable dans $APP_DIR."

compose_app() {
  docker compose -p "$DEPLOY_NAMESPACE" --project-directory "$APP_DIR" --env-file "$APP_DIR/compose.env" \
    -f "$COMPOSE_FILE" --profile interne "$@"
}

volume_name="${DEPLOY_NAMESPACE}_pgdata"

echo "== Namespace : $DEPLOY_NAMESPACE"
echo "== Volume cible : $volume_name"

echo "== Arret du service db"
compose_app stop db || true
compose_app rm -f db || true

if docker volume inspect "$volume_name" >/dev/null 2>&1; then
  echo "== Suppression du volume $volume_name"
  docker volume rm "$volume_name"
  echo "Volume $volume_name supprime."
else
  echo "Volume $volume_name absent : rien a supprimer."
fi

echo "Reset BD termine. Relancer CD - ORCHESTRATEUR pour recreer Postgres avec le DB_PASSWORD actuel."
