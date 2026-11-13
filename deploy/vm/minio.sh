#!/bin/sh
# Installe ou met a jour la stack MinIO partagee (/opt/apps/_minio).
# Appele par CD - MINIO SSH. Usage : sh deploy/vm/minio.sh /chemin/vers/source
#   source : deploy/minio/, minio.env, et optionnellement minio-app.env (si USE_S3).
set -eu

fail() {
  echo "ERREUR minio : $*" >&2
  exit 1
}

SRC="${1:-}"
[ -n "$SRC" ] || fail "chemin source manquant"
[ -d "$SRC/deploy/minio" ] || fail "dossier deploy/minio introuvable dans $SRC"
[ -f "$SRC/minio.env" ] || fail "minio.env manquant dans $SRC"

MINIO_DIR=/opt/apps/_minio
compose_minio() {
  docker compose -p minio --project-directory "$MINIO_DIR" -f "$MINIO_DIR/compose.yml" "$@"
}

docker network inspect proxy >/dev/null 2>&1 \
  || fail "reseau Docker « proxy » absent (lancer d'abord un deploiement app SSH)."

echo "== MinIO (stack partagee)"
mkdir -p "$MINIO_DIR"
find "$MINIO_DIR" -mindepth 1 -maxdepth 1 ! -name 'minio.env' ! -name 'minio-app.env' -exec rm -rf {} +
cp -a "$SRC/deploy/minio/." "$MINIO_DIR/"
cp "$SRC/minio.env" "$MINIO_DIR/minio.env"
chmod 600 "$MINIO_DIR/minio.env"
chmod 755 "$MINIO_DIR/provisionner.sh" 2>/dev/null || true

if [ -f "$SRC/minio-app.env" ]; then
  cp "$SRC/minio-app.env" "$MINIO_DIR/minio-app.env"
  chmod 600 "$MINIO_DIR/minio-app.env"
else
  rm -f "$MINIO_DIR/minio-app.env"
fi

compose_minio up -d --wait --wait-timeout 180

if [ -f "$MINIO_DIR/minio-app.env" ]; then
  echo "== Provision bucket / utilisateur applicatif"
  compose_minio --profile provision run --rm provision
else
  echo "== Pas de minio-app.env : serveur seul (USE_S3 inactif)."
fi

echo "MinIO actif (API minio-serveur:9000, console 127.0.0.1:9001, tunnel :19001)."
