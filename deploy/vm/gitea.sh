#!/bin/sh
# Installe ou met a jour la forge Gitea partagee (/opt/apps/_gitea) et son site HTTPS dans le proxy.
# Appele par CD - GITEA SSH. Usage : sh deploy/vm/gitea.sh /chemin/vers/source
#   source : deploy/gitea/, deploy/proxy/site-gitea-*.conf.tpl, gitea.env, et DEPLOY_LETSENCRYPT_EMAIL dans l'environnement.
# Idempotent : relancer ne recree ni la base, ni l'administrateur, ni le certificat.
set -eu

fail() {
  echo "ERREUR gitea : $*" >&2
  exit 1
}

SRC="${1:-}"
[ -n "$SRC" ] || fail "chemin source manquant"
[ -d "$SRC/deploy/gitea" ] || fail "dossier deploy/gitea introuvable dans $SRC"
[ -f "$SRC/gitea.env" ] || fail "gitea.env manquant dans $SRC"
[ -f "$SRC/deploy/proxy/site-gitea-http.conf.tpl" ] || fail "gabarit site-gitea-http.conf.tpl manquant"
[ -f "$SRC/deploy/proxy/site-gitea-https.conf.tpl" ] || fail "gabarit site-gitea-https.conf.tpl manquant"
[ -n "${DEPLOY_LETSENCRYPT_EMAIL+x}" ] || fail "DEPLOY_LETSENCRYPT_EMAIL manquant"
[ -n "$DEPLOY_LETSENCRYPT_EMAIL" ] || fail "DEPLOY_LETSENCRYPT_EMAIL vide"

GITEA_DIR=/opt/apps/_gitea
PROXY_DIR=/opt/apps/_proxy

docker network inspect proxy >/dev/null 2>&1 \
  || fail "reseau Docker « proxy » absent (lancer d'abord un deploiement app SSH)."
[ -f "$PROXY_DIR/compose.yml" ] || fail "proxy partage absent dans $PROXY_DIR (lancer d'abord un deploiement app SSH)."

# Un seul deploiement a la fois sur la VM (proxy partage)
exec 9> /opt/apps/.deployer.lock
echo "== Verrou de la VM"
flock -w 1200 9 || fail "un autre deploiement occupe la VM depuis plus de 20 minutes."

# Variables du fichier : GITEA_DOMAIN, GITEA_DB_PASSWORD, GITEA_ADMIN_USER, GITEA_ADMIN_PASSWORD, GITEA_ADMIN_EMAIL
set -a
# shellcheck disable=SC1091
. "$SRC/gitea.env"
set +a
for name in GITEA_DOMAIN GITEA_DB_PASSWORD GITEA_ADMIN_USER GITEA_ADMIN_PASSWORD GITEA_ADMIN_EMAIL; do
  eval "defini=\${$name+x}"
  [ -n "$defini" ] || fail "$name absent de gitea.env"
  eval "value=\$$name"
  [ -n "$value" ] || fail "$name vide dans gitea.env"
done
printf '%s' "$GITEA_DOMAIN" | grep -Eq '^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$' || fail "GITEA_DOMAIN invalide."

compose_gitea() {
  docker compose -p gitea --project-directory "$GITEA_DIR" --env-file "$GITEA_DIR/gitea.env" -f "$GITEA_DIR/compose.yml" "$@"
}

compose_proxy() {
  docker compose -p proxy -f "$PROXY_DIR/compose.yml" "$@"
}

# Ecrit le site depuis un gabarit, teste la configuration, et restaure l'ancienne en cas d'echec.
installer_site() {
  site="$PROXY_DIR/sites/gitea.conf"
  sed -e "s/__DOMAIN__/$GITEA_DOMAIN/g" "$SRC/deploy/proxy/$1" > "$site.new"
  if [ -f "$site" ]; then
    cp "$site" "$site.bak"
  else
    rm -f "$site.bak"
  fi
  mv "$site.new" "$site"
  if ! compose_proxy exec -T nginx nginx -t; then
    if [ -f "$site.bak" ]; then
      mv "$site.bak" "$site"
    else
      rm -f "$site"
    fi
    fail "la configuration nginx de la forge est refusee (ancienne configuration restauree)."
  fi
  compose_proxy exec -T nginx nginx -s reload
}

echo "== Gitea (stack partagee)"
mkdir -p "$GITEA_DIR" "$PROXY_DIR/sites"
find "$GITEA_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
cp -a "$SRC/deploy/gitea/." "$GITEA_DIR/"
cp "$SRC/gitea.env" "$GITEA_DIR/gitea.env"
chmod 600 "$GITEA_DIR/gitea.env"

echo "== Certificat HTTPS ($GITEA_DOMAIN)"
certificat="$(compose_proxy run --rm --no-deps -T --entrypoint sh certbot \
  -c "if [ -d '/etc/letsencrypt/live/$GITEA_DOMAIN' ]; then echo present; else echo absent; fi")" \
  || fail "impossible de verifier le certificat de $GITEA_DOMAIN."
case "$certificat" in
  present|absent) ;;
  *) fail "reponse inattendue en verifiant le certificat de $GITEA_DOMAIN : $certificat" ;;
esac
if [ "$certificat" = "present" ]; then
  echo "Certificat deja present pour $GITEA_DOMAIN."
else
  # Le DNS de GITEA_DOMAIN doit deja pointer vers cette VM (defi HTTP-01)
  installer_site site-gitea-http.conf.tpl
  compose_proxy run --rm --no-deps --entrypoint certbot certbot certonly --webroot -w /var/www/certbot \
    -d "$GITEA_DOMAIN" --email "$DEPLOY_LETSENCRYPT_EMAIL" --agree-tos --no-eff-email --non-interactive
fi

echo "== Gitea et sa base"
compose_gitea pull
compose_gitea up -d --wait --wait-timeout 300

echo "== Site HTTPS"
installer_site site-gitea-https.conf.tpl

echo "== Compte administrateur"
if compose_gitea exec -T -u git gitea gitea admin user list --admin | awk 'NR>1 {print $2}' | grep -qx "$GITEA_ADMIN_USER"; then
  echo "Administrateur $GITEA_ADMIN_USER deja present : conserve tel quel."
else
  compose_gitea exec -T -u git gitea gitea admin user create --admin \
    --username "$GITEA_ADMIN_USER" --password "$GITEA_ADMIN_PASSWORD" --email "$GITEA_ADMIN_EMAIL" \
    --must-change-password=false
fi

echo "Gitea actif : https://$GITEA_DOMAIN (API interne pour Django : http://gitea:3000)."
echo "Suite (a la main, une seule fois) : creer le jeton admin, voir docs/devstreet_hub/gitea-deploy.md."
