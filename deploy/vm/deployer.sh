#!/bin/sh
# Deploie un namespace sur la VM. Execute par l'utilisateur deploy, depuis /opt/apps/<namespace> :
#   printf '%s\n%s\n' "$UTILISATEUR_REGISTRE" "$JETON_REGISTRE" | sh deploy/vm/deployer.sh
# Fichiers attendus dans le dossier courant (envoyes par le workflow) : compose.env, backend.env, deploy/.
# stdin : ligne 1 = utilisateur du registre, ligne 2 = jeton (valable le temps du job, jamais ecrit sur le disque).
# Le meme script sert quel que soit le transport (SSH direct, IAP de GCP...).
set -eu

fail() {
  echo "ERREUR : $1" >&2
  exit 1
}

. ./compose.env

printf '%s' "$DEPLOY_NAMESPACE" | grep -Eq '^[a-z0-9][a-z0-9-]{1,40}$' || fail "DEPLOY_NAMESPACE invalide."
printf '%s' "$DEPLOY_DOMAIN" | grep -Eq '^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$' || fail "DEPLOY_DOMAIN invalide."
[ "$(pwd)" = "/opt/apps/$DEPLOY_NAMESPACE" ] || fail "ce script doit s'executer dans /opt/apps/$DEPLOY_NAMESPACE (dossier actuel : $(pwd))."

APP_DIR="/opt/apps/$DEPLOY_NAMESPACE"
PROXY_DIR=/opt/apps/_proxy
PUBLIC_DIR="/srv/public/$DEPLOY_NAMESPACE"

# Un seul deploiement a la fois sur la VM : le proxy partage et la session du registre (~/.docker) sont communs a tous les namespaces
exec 9> /opt/apps/.deployer.lock
echo "== Verrou de la VM"
flock -w 1200 9 || fail "un autre deploiement occupe la VM depuis plus de 20 minutes."

profile_args=""
if [ "$DEPLOY_DB_MODE" = "interne" ]; then
  profile_args="--profile interne"
fi

compose_app() {
  # shellcheck disable=SC2086
  docker compose -p "$DEPLOY_NAMESPACE" --project-directory "$APP_DIR" --env-file "$APP_DIR/compose.env" \
    -f "$APP_DIR/deploy/compose/compose.yml" $profile_args "$@"
}

compose_proxy() {
  docker compose -p proxy -f "$PROXY_DIR/compose.yml" "$@"
}

cleanup() {
  status=$?
  docker logout ghcr.io > /dev/null 2>&1 || true
  if [ "$status" -ne 0 ]; then
    echo "== Echec (code $status) : etat et derniers journaux de $DEPLOY_NAMESPACE"
    compose_app ps || true
    compose_app logs --tail 80 || true
  fi
}
trap cleanup EXIT

# Ecrit le site du namespace depuis un gabarit, teste la configuration, et restaure l'ancienne en cas d'echec.
installer_site() {
  site="$PROXY_DIR/sites/$DEPLOY_NAMESPACE.conf"
  sed -e "s/__DOMAIN__/$DEPLOY_DOMAIN/g" -e "s/__NAMESPACE__/$DEPLOY_NAMESPACE/g" "deploy/proxy/$1" > "$site.new"
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
    fail "la configuration nginx de $DEPLOY_NAMESPACE est refusee (ancienne configuration restauree)."
  fi
  compose_proxy exec -T nginx nginx -s reload
}

echo "== Registre"
IFS= read -r registry_user
IFS= read -r registry_token
printf '%s' "$registry_token" | docker login ghcr.io -u "$registry_user" --password-stdin
registry_token=""

echo "== Images"
compose_app pull

echo "== Proxy partage"
mkdir -p "$PROXY_DIR/sites"
cp deploy/proxy/compose.yml deploy/proxy/nginx.conf "$PROXY_DIR/"
compose_proxy up -d

echo "== Dossiers publics (/static et /media)"
mkdir -p "$PUBLIC_DIR/static" "$PUBLIC_DIR/media"
# Le backend s'execute en uid 10001 (backend/Dockerfile) : il doit pouvoir ecrire dans ces deux dossiers
docker run --rm --user 0 --entrypoint sh -v "$PUBLIC_DIR:/data" "$BACKEND_IMAGE" \
  -c 'chown 10001:10001 /data/static /data/media && chmod 755 /data/static /data/media'

echo "== Certificat HTTPS"
# Le test est fait par un shell dans le conteneur : une erreur Docker fait echouer le deploiement au lieu de passer pour « pas de certificat »
certificat="$(compose_proxy run --rm --no-deps -T --entrypoint sh certbot \
  -c "if [ -d '/etc/letsencrypt/live/$DEPLOY_DOMAIN' ]; then echo present; else echo absent; fi")" \
  || fail "impossible de verifier le certificat de $DEPLOY_DOMAIN."
case "$certificat" in
  present|absent) ;;
  *) fail "reponse inattendue en verifiant le certificat de $DEPLOY_DOMAIN : $certificat" ;;
esac
if [ "$certificat" = "present" ]; then
  echo "Certificat deja present pour $DEPLOY_DOMAIN."
else
  # Premier deploiement : nginx ne peut pas demarrer un site HTTPS sans certificat, on sert d'abord le seul defi HTTP-01
  installer_site site-http.conf.tpl
  compose_proxy run --rm --no-deps --entrypoint certbot certbot certonly --webroot -w /var/www/certbot \
    -d "$DEPLOY_DOMAIN" --email "$DEPLOY_LETSENCRYPT_EMAIL" --agree-tos --no-eff-email --non-interactive
fi

echo "== Application"
compose_app up -d --wait --wait-timeout 300 --remove-orphans

echo "== Site HTTPS"
installer_site site-https.conf.tpl

echo "$DEPLOY_SHA" > deploiement-actuel
docker image prune -f > /dev/null
echo "Deploiement termine : $DEPLOY_NAMESPACE sur $DEPLOY_SHA"
