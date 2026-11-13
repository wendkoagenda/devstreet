#!/bin/sh
# Collecte d'urgence des logs Docker (backend, frontend, proxy, observabilite).
# Appele par CD - MAINTENANCE logs-urgence. Utilisateur deploy.
#
# Variables d'environnement obligatoires :
#   DEPLOY_NAMESPACE  — projet Compose de l'app (/opt/apps/<namespace>)
#   SINCE             — fenetre docker logs (30m|1h|2h|6h|24h)
#   OUT_DIR           — dossier de sortie (cree si besoin)
#
# Artefact : un fichier .log par service
#   backend.log, frontend.log, proxy.log, observabilite.log
# + meta.txt / statut.txt. Code de sortie : 0 si backend OK ; 1 sinon.
# Services absents : warning dans statut.txt, pas d'echec (sauf backend).

set -eu

MAX_LIGNES=5000
APP_DIR_ROOT=/opt/apps
PROXY_DIR=/opt/apps/_proxy
OBS_DIR=/opt/apps/_observabilite

fail() {
  echo "ERREUR logs-urgence : $*" >&2
  exit 1
}

[ -n "${DEPLOY_NAMESPACE+x}" ] || fail "DEPLOY_NAMESPACE manquant"
[ -n "$DEPLOY_NAMESPACE" ] || fail "DEPLOY_NAMESPACE vide"
[ -n "${SINCE+x}" ] || fail "SINCE manquant"
[ -n "$SINCE" ] || fail "SINCE vide"
[ -n "${OUT_DIR+x}" ] || fail "OUT_DIR manquant"
[ -n "$OUT_DIR" ] || fail "OUT_DIR vide"

case "$SINCE" in
  30m|1h|2h|6h|24h) ;;
  *) fail "SINCE invalide (« $SINCE »), attendu : 30m, 1h, 2h, 6h ou 24h" ;;
esac

printf '%s' "$DEPLOY_NAMESPACE" | grep -Eq '^[a-z0-9][a-z0-9-]{1,40}$' \
  || fail "DEPLOY_NAMESPACE invalide"

APP_DIR="$APP_DIR_ROOT/$DEPLOY_NAMESPACE"
[ -d "$APP_DIR" ] || fail "dossier app introuvable : $APP_DIR"

mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR"
: > "$OUT_DIR/statut.txt"

# $1=libelle $2=project $3=project-directory $4=compose.yml $5=sortie
# $6=env-file ('' si aucun) $7=service Compose ('' = tous les services du projet)
dump_compose() {
  libelle="$1"
  project="$2"
  proj_dir="$3"
  compose_file="$4"
  sortie="$5"
  env_file="$6"
  service="$7"

  if [ ! -d "$proj_dir" ] || [ ! -f "$compose_file" ]; then
    echo "WARNING : $libelle ignoree (dossier ou compose.yml absent)." | tee -a "$OUT_DIR/statut.txt"
    return 1
  fi

  set -- docker compose -p "$project" --project-directory "$proj_dir"
  if [ -n "$env_file" ] && [ -f "$env_file" ]; then
    set -- "$@" --env-file "$env_file"
  fi
  set -- "$@" -f "$compose_file"

  if ! "$@" ps -q >/dev/null 2>&1; then
    echo "WARNING : $libelle ignoree (projet Compose inaccessible)." | tee -a "$OUT_DIR/statut.txt"
    return 1
  fi

  echo "== Logs $libelle (since=$SINCE, tail=$MAX_LIGNES)"
  if [ -n "$service" ]; then
    set -- "$@" logs --timestamps --no-color --since "$SINCE" --tail "$MAX_LIGNES" "$service"
  else
    set -- "$@" logs --timestamps --no-color --since "$SINCE" --tail "$MAX_LIGNES"
  fi
  if ! "$@" > "$sortie" 2>&1; then
    echo "WARNING : echec dump $libelle." | tee -a "$OUT_DIR/statut.txt"
    return 1
  fi
  echo "OK : $libelle -> $(basename "$sortie") ($(wc -l < "$sortie") lignes)" | tee -a "$OUT_DIR/statut.txt"
  return 0
}

echo "== Collecte logs-urgence namespace=$DEPLOY_NAMESPACE since=$SINCE"
date -u "+UTC: %Y-%m-%dT%H:%M:%SZ" > "$OUT_DIR/meta.txt"
{
  echo "namespace=$DEPLOY_NAMESPACE"
  echo "since=$SINCE"
  echo "max_lignes=$MAX_LIGNES"
  echo "fichiers=backend.log frontend.log proxy.log observabilite.log minio.log"
} >> "$OUT_DIR/meta.txt"

compose_app="$APP_DIR/deploy/compose/compose.yml"
env_app="$APP_DIR/compose.env"

backend_ok=0
if dump_compose "backend" "$DEPLOY_NAMESPACE" "$APP_DIR" \
  "$compose_app" "$OUT_DIR/backend.log" "$env_app" "backend"; then
  backend_ok=1
fi

if [ "$backend_ok" -ne 1 ]; then
  fail "impossible de collecter les logs backend ($DEPLOY_NAMESPACE)"
fi

dump_compose "frontend" "$DEPLOY_NAMESPACE" "$APP_DIR" \
  "$compose_app" "$OUT_DIR/frontend.log" "$env_app" "frontend" || true

dump_compose "proxy" "proxy" "$PROXY_DIR" \
  "$PROXY_DIR/compose.yml" "$OUT_DIR/proxy.log" "" "" || true

dump_compose "observabilite" "observabilite" "$OBS_DIR" \
  "$OBS_DIR/compose.yml" "$OUT_DIR/observabilite.log" "" "" || true

MINIO_DIR=/opt/apps/_minio
dump_compose "minio" "minio" "$MINIO_DIR" \
  "$MINIO_DIR/compose.yml" "$OUT_DIR/minio.log" "" "" || true

echo "== Collecte terminee"
cat "$OUT_DIR/statut.txt"
