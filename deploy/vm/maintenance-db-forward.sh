#!/bin/sh
# Forward temporaire Postgres (localhost VM -> conteneur db) pour pgAdmin via tunnel SSH.
# Execute par l'utilisateur deploy :
#   cd /opt/apps/<namespace> && sh -s open|close < deploy/vm/maintenance-db-forward.sh
# open : demarre (ou recree) un conteneur socat sur 127.0.0.1:5432, TTL 8 h.
# close : arrete le conteneur forward.
# Ne publie jamais 0.0.0.0. Reserve a DEPLOY_DB_MODE=interne.
set -eu

ACTION="$1"
TTL_SECONDS=28800
SOCAT_IMAGE=alpine/socat:1.8.0.1

fail() {
  echo "ERREUR : $1" >&2
  exit 1
}

case "$ACTION" in
  open|close) ;;
  *) fail "usage : sh -s open|close (recu : « $ACTION »)" ;;
esac

[ -f ./compose.env ] || fail "compose.env introuvable (deploiement jamais fait ?)."
. ./compose.env

printf '%s' "$DEPLOY_NAMESPACE" | grep -Eq '^[a-z0-9][a-z0-9-]{1,40}$' || fail "DEPLOY_NAMESPACE invalide."
[ "$(pwd)" = "/opt/apps/$DEPLOY_NAMESPACE" ] || fail "ce script doit s'executer dans /opt/apps/$DEPLOY_NAMESPACE (dossier actuel : $(pwd))."
[ "$DEPLOY_DB_MODE" = "interne" ] || fail "DEPLOY_DB_MODE=$DEPLOY_DB_MODE : forward reserve au mode interne."

DB_CONTAINER="${DEPLOY_NAMESPACE}-db"
FORWARD_CONTAINER="${DEPLOY_NAMESPACE}-pg-forward"
NETWORK="${DEPLOY_NAMESPACE}_interne"

stop_forward() {
  rm -f "/tmp/${FORWARD_CONTAINER}.ttl"
  if docker container inspect "$FORWARD_CONTAINER" >/dev/null 2>&1; then
    echo "== Arret de $FORWARD_CONTAINER"
    docker stop "$FORWARD_CONTAINER" >/dev/null 2>&1 || true
    docker rm -f "$FORWARD_CONTAINER" >/dev/null 2>&1 || true
    echo "Forward arrete."
  else
    echo "Conteneur $FORWARD_CONTAINER absent : rien a fermer."
  fi
}

if [ "$ACTION" = "close" ]; then
  stop_forward
  exit 0
fi

docker network inspect "$NETWORK" >/dev/null 2>&1 || fail "reseau Docker $NETWORK introuvable (deploiement interne jamais fait ?)."
docker container inspect "$DB_CONTAINER" >/dev/null 2>&1 || fail "conteneur $DB_CONTAINER introuvable."
state="$(docker inspect -f '{{.State.Running}}' "$DB_CONTAINER")"
[ "$state" = "true" ] || fail "conteneur $DB_CONTAINER n'est pas demarre."

stop_forward

echo "== Demarrage du forward 127.0.0.1:5432 -> $DB_CONTAINER:5432 (reseau $NETWORK)"
docker pull "$SOCAT_IMAGE" >/dev/null
docker run -d --restart=no --name "$FORWARD_CONTAINER" \
  --network "$NETWORK" \
  -p 127.0.0.1:5432:5432 \
  "$SOCAT_IMAGE" \
  TCP-LISTEN:5432,fork,reuseaddr TCP:"${DB_CONTAINER}":5432 >/dev/null

# TTL : coupe le forward meme si close n'est pas lance.
# Jeton : un ancien sleep (apres un re-open) ne doit pas arreter le forward courant.
ttl_marker="/tmp/${FORWARD_CONTAINER}.ttl"
ttl_token="$(date +%s)-$$"
printf '%s\n' "$ttl_token" > "$ttl_marker"
nohup sh -c "
  sleep \"$TTL_SECONDS\"
  if [ -f \"$ttl_marker\" ] && [ \"\$(cat \"$ttl_marker\")\" = \"$ttl_token\" ]; then
    docker stop \"$FORWARD_CONTAINER\" >/dev/null 2>&1 || true
    docker rm -f \"$FORWARD_CONTAINER\" >/dev/null 2>&1 || true
    rm -f \"$ttl_marker\"
  fi
" >/dev/null 2>&1 &

echo "Forward ouvert."
echo "TTL_SECONDS=$TTL_SECONDS"
echo "FORWARD_CONTAINER=$FORWARD_CONTAINER"
echo "DB_CONTAINER=$DB_CONTAINER"
echo "LISTEN=127.0.0.1:5432"
