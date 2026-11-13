#!/bin/sh
# Installe ou met a jour la stack d'observabilite partagee (/opt/apps/_observabilite).
# Appele par CD - OBSERVABILITE SSH (pas par deployer.sh).
# Usage : sh deploy/vm/observabilite.sh /chemin/vers/source
#   source doit contenir deploy/observabilite/, observabilite.env, et optionnellement alerting-contacts.yml.
# Echec = code non nul (job CD bloquant).

set -eu

fail() {
  echo "ERREUR observabilite : $*" >&2
  exit 1
}

SRC="${1:-}"
[ -n "$SRC" ] || fail "chemin source manquant"
[ -d "$SRC/deploy/observabilite" ] || fail "dossier deploy/observabilite introuvable dans $SRC"
[ -f "$SRC/observabilite.env" ] || fail "observabilite.env manquant dans $SRC"

OBS_DIR=/opt/apps/_observabilite
# Fichiers sur l'hote ; montes dans le conteneur en /etc/grafana/dashboards (hors volume grafana-data)
DASH_DIR="$OBS_DIR/grafana/dashboards"
EXPECTED_DASHBOARDS="general.json backend.json frontend.json proxy.json postgres.json minio.json"

compose_obs() {
  docker compose -p observabilite --project-directory "$OBS_DIR" -f "$OBS_DIR/compose.yml" "$@"
}

echo "== Observabilite (stack partagee)"
mkdir -p "$OBS_DIR"
# Remplace le contenu de config ; conserve les volumes Docker (metriques / logs)
find "$OBS_DIR" -mindepth 1 -maxdepth 1 ! -name 'observabilite.env' -exec rm -rf {} +
cp -a "$SRC/deploy/observabilite/." "$OBS_DIR/"
cp "$SRC/observabilite.env" "$OBS_DIR/observabilite.env"
chmod 600 "$OBS_DIR/observabilite.env"
if [ -f "$SRC/alerting-contacts.yml" ]; then
  mkdir -p "$OBS_DIR/grafana/provisioning/alerting"
  cp "$SRC/alerting-contacts.yml" "$OBS_DIR/grafana/provisioning/alerting/contacts.yml"
  chmod 600 "$OBS_DIR/grafana/provisioning/alerting/contacts.yml"
fi

[ -d "$DASH_DIR" ] || fail "dossier dashboards absent apres copie : $DASH_DIR"
for dash in $EXPECTED_DASHBOARDS; do
  [ -f "$DASH_DIR/$dash" ] || fail "dashboard manquant : $DASH_DIR/$dash"
done
echo "== Dashboards presents : $EXPECTED_DASHBOARDS"

compose_obs up -d --wait --wait-timeout 180

# Force la relecture du provisioning fichier (dossier Doonya)
echo "== Redemarrage Grafana (rechargement des dashboards)"
compose_obs restart grafana
compose_obs up -d --wait --wait-timeout 120 grafana

# Compte admin : lu depuis observabilite.env (GF_SECURITY_ADMIN_USER n'est applique qu'au 1er demarrage ;
# le mot de passe est reapplique a chaque execution)
set -a
# shellcheck disable=SC1091
. "$OBS_DIR/observabilite.env"
set +a
[ -n "${GF_SECURITY_ADMIN_USER+x}" ] || fail "GF_SECURITY_ADMIN_USER absent apres source"
[ -n "$GF_SECURITY_ADMIN_USER" ] || fail "GF_SECURITY_ADMIN_USER vide"
[ -n "${GF_SECURITY_ADMIN_PASSWORD+x}" ] || fail "GF_SECURITY_ADMIN_PASSWORD absent apres source"
[ -n "$GF_SECURITY_ADMIN_PASSWORD" ] || fail "GF_SECURITY_ADMIN_PASSWORD vide"
compose_obs exec -T grafana grafana cli admin reset-admin-password "$GF_SECURITY_ADMIN_PASSWORD"

echo "Observabilite active (Grafana sur 127.0.0.1:3000, tunnel SSH requis)."
echo "Dashboards Doonya : General, Backend, Frontend, Proxy, Postgres, MinIO."
