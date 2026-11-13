#!/bin/sh
# Controle en lecture seule d'une VM preparee. Execute par l'utilisateur deploy, envoye sur stdin :
#   ssh deploy@hote 'sh -s' < deploy/vm/verifier.sh
# Code de sortie : 0 conforme, 1 ecarts.
set -u

status=0
fail() {
  echo "ECART : $1"
  status=1
}

if docker version --format '{{.Server.Version}}' >/dev/null 2>&1; then
  echo "Docker : $(docker version --format '{{.Server.Version}}')"
else
  fail "Docker injoignable pour l'utilisateur $(id -un) (installe ? membre du groupe docker ?)"
fi

if docker compose version >/dev/null 2>&1; then
  echo "Compose : $(docker compose version --short)"
else
  fail "plugin docker compose absent"
fi

for dir in /opt/apps /srv/public; do
  [ -w "$dir" ] || fail "$dir n'existe pas ou n'est pas modifiable par $(id -un)"
done

# Hors boucle locale : 22/80/443 (app) + 20201/20202 (agents de metriques GCP). Un port publie par Docker contourne ufw.
extra=$(ss -Hltn | awk '{print $4}' | grep -Ev '^(127\.|\[::1\]|\[::ffff:127\.)' | sed 's/.*://' | sort -un | grep -Ev '^(22|80|443|20201|20202)$' || true)
if [ -n "$extra" ]; then
  fail "ports en ecoute sur l'exterieur en plus de 22, 80, 443, 20201 et 20202 : $(echo "$extra" | tr '\n' ' ')"
else
  echo "Ports en ecoute autorises : 22, 80, 443 (+ 20201/20202 metriques GCP si presents)"
fi

exit "$status"
