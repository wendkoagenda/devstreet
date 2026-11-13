# Acces a une VM GCP sans IP publique, depuis un workflow GitHub : tunnel IAP et Workload Identity Federation (aucune cle).
# A sourcer avec bash : . deploy/ci/gcp-vm.sh
#   gcp_auth                  authentifie gcloud avec le jeton OIDC du job (le job doit avoir « permissions: id-token: write »)
#   vm_gcp "commande"         execute la commande sur la VM en tant qu'utilisateur deploy ; stdin est transmis
# Variables attendues (deja validees par scripts.deploy_env) : GCP_PROJECT_ID, GCP_ZONE, GCP_INSTANCE, GCP_WIF_PROVIDER,
# GCP_SERVICE_ACCOUNT, RUNNER_TEMP, ACTIONS_ID_TOKEN_REQUEST_URL, ACTIONS_ID_TOKEN_REQUEST_TOKEN.
# Prerequis cote GCP : 00readme/PLAN_CD.md (hors perimetre du runbook SSH deploy/README.md).

gcp_auth() {
  local dir="$RUNNER_TEMP/gcp"
  umask 077
  mkdir -p "$dir"
  curl -fsS -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
    "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=//iam.googleapis.com/$GCP_WIF_PROVIDER" | jq -r .value > "$dir/oidc-token"
  gcloud iam workload-identity-pools create-cred-config "$GCP_WIF_PROVIDER" \
    --service-account="$GCP_SERVICE_ACCOUNT" \
    --credential-source-file="$dir/oidc-token" \
    --output-file="$dir/credentials.json" --quiet
  gcloud auth login --cred-file="$dir/credentials.json" --quiet
  gcloud config set project "$GCP_PROJECT_ID" --quiet
}

# Les roles de connexion OS Login donnent un compte sudo ; docker et les dossiers appartiennent a deploy.
# -H : HOME de deploy (docker login y ecrit sa configuration).
vm_gcp() {
  gcloud compute ssh "$GCP_INSTANCE" \
    --project "$GCP_PROJECT_ID" --zone "$GCP_ZONE" \
    --tunnel-through-iap --ssh-key-expire-after=30m --quiet \
    --command "sudo -n -H -u deploy bash -c $(printf '%q' "$1")"
}

gcp_cleanup() {
  gcloud auth revoke --all --quiet > /dev/null 2>&1 || true
  rm -rf "$RUNNER_TEMP/gcp"
}
