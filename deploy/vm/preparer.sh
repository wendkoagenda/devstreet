#!/bin/sh
# Prepare une VM Ubuntu LTS pour le deploiement. Execute en root, envoye sur stdin :
#   sudo -n env DEPLOY_PUBKEY='ssh-ed25519 ...' bash -s -- a   (SSH direct : installation, cle de deploy, pare-feu)
#   sudo -n bash -s -- b                                        (SSH direct : durcissement SSH, apres test de la cle deploy)
#   sudo -n bash -s -- g                                        (GCP sans IP publique : tout en une fois, SSH limite au tunnel IAP)
# Voir git-cli/deploy_env.py (preparer-vm, preparer-vm-gcp). Idempotent : relancer ne casse rien.
set -eu

phase="$1"

if [ "$(id -u)" -ne 0 ]; then
  echo "ERREUR : ce script doit s'executer en root (sudo)." >&2
  exit 1
fi

. /etc/os-release
if [ "$ID" != "ubuntu" ]; then
  echo "ERREUR : seul Ubuntu LTS est pris en charge (systeme detecte : $PRETTY_NAME)." >&2
  exit 1
fi

# Paquets, Docker, utilisateur deploy (sans cle SSH), dossiers, fail2ban, mises a jour de securite
installer_base() {
  export DEBIAN_FRONTEND=noninteractive

  echo "== Paquets de base"
  apt-get update -y
  apt-get install -y ca-certificates curl gnupg ufw fail2ban unattended-upgrades

  echo "== Docker"
  if ! command -v docker >/dev/null 2>&1; then
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
      > /etc/apt/sources.list.d/docker.list
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  fi
  systemctl enable --now docker

  echo "== Utilisateur deploy"
  if ! id deploy >/dev/null 2>&1; then
    adduser --disabled-password --gecos "" deploy
  fi
  usermod -aG docker deploy
  install -d -m 755 -o deploy -g deploy /opt/apps
  install -d -m 755 -o deploy -g deploy /srv/public

  echo "== fail2ban (SSH)"
  systemctl enable --now fail2ban

  echo "== Mises a jour de securite automatiques"
  printf 'APT::Periodic::Update-Package-Lists "1";\nAPT::Periodic::Unattended-Upgrade "1";\n' \
    > /etc/apt/apt.conf.d/20auto-upgrades
  systemctl enable --now unattended-upgrades
}

# Ports 80 et 443 ouverts a tous ; le port 22 est regle par l'appelant AVANT l'activation, pour ne pas couper la session
activer_pare_feu() {
  ufw default deny incoming
  ufw default allow outgoing
  ufw allow 80/tcp
  ufw allow 443/tcp
  ufw --force enable
}

durcir_ssh() {
  echo "== Durcissement SSH"
  # Le prefixe 00- place ce fichier avant les reglages du fournisseur (50-cloud-init.conf) : sshd garde la premiere valeur lue.
  install -d -m 755 /etc/ssh/sshd_config.d
  cat > /etc/ssh/sshd_config.d/00-deploiement.conf <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
EOF
  sshd -t
  systemctl reload ssh || systemctl reload sshd
}

phase_a() {
  # set -u : l'absence de DEPLOY_PUBKEY arrete deja le script
  if [ -z "$DEPLOY_PUBKEY" ]; then
    echo "ERREUR : DEPLOY_PUBKEY est vide." >&2
    exit 1
  fi
  installer_base

  echo "== Cle SSH de deploiement"
  install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
  printf '%s\n' "$DEPLOY_PUBKEY" > /home/deploy/.ssh/authorized_keys
  chown deploy:deploy /home/deploy/.ssh/authorized_keys
  chmod 600 /home/deploy/.ssh/authorized_keys

  echo "== Pare-feu (ufw) : 22, 80, 443"
  ufw allow 22/tcp
  activer_pare_feu
  echo "Phase a terminee."
}

phase_b() {
  durcir_ssh
  echo "Phase b terminee."
}

phase_g() {
  installer_base

  echo "== Pare-feu (ufw) : SSH reserve au tunnel IAP de Google (35.235.240.0/20), 80, 443"
  ufw allow from 35.235.240.0/20 to any port 22 proto tcp
  activer_pare_feu
  durcir_ssh
  echo "Phase g terminee."
}

case "$phase" in
  a) phase_a ;;
  b) phase_b ;;
  g) phase_g ;;
  *)
    echo "Usage : preparer.sh a|b|g" >&2
    exit 1
    ;;
esac
