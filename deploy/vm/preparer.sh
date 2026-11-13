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
  apt-get install -y ca-certificates curl gnupg ufw fail2ban unattended-upgrades cloud-guest-utils

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

  echo "== Rotation des journaux Docker (evite de saturer le disque)"
  mkdir -p /etc/docker
  if [ ! -f /etc/docker/daemon.json ]; then
    cat > /etc/docker/daemon.json <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
    systemctl restart docker
  elif ! grep -q '"max-size"' /etc/docker/daemon.json 2>/dev/null; then
    echo "AVERTISSEMENT : /etc/docker/daemon.json existe deja sans max-size — rotation non injectee automatiquement."
  fi

  echo "== Utilisateur deploy"
  if ! id deploy >/dev/null 2>&1; then
    adduser --disabled-password --gecos "" deploy
  fi
  usermod -aG docker deploy
  install -d -m 755 -o deploy -g deploy /opt/apps
  install -d -m 755 -o deploy -g deploy /srv/public

  echo "== sudo : deploy peut agrandir la partition root (apres resize disque GCP)"
  # Script fixe : le depot sous /opt/apps/<ns>/ change a chaque deploy ; sudoers pointe ici.
  cat > /usr/local/sbin/doonya-grow-rootfs <<'GROW'
#!/bin/sh
set -eu
if [ "$(id -u)" -ne 0 ]; then
  echo "ERREUR : doonya-grow-rootfs doit s'executer en root." >&2
  exit 1
fi
echo "== Place avant" ; df -h / | tail -n 1 || true
root_src="$(findmnt -n -o SOURCE /)"
case "$root_src" in /dev/*) ;; *) echo "root inattendu : $root_src" ; exit 0 ;; esac
echo "$root_src" | grep -q mapper && { echo "LVM non gere" ; exit 0 ; }
disk_name="$(lsblk -no PKNAME "$root_src" 2>/dev/null || true)"
part_num="$(echo "$root_src" | sed -n 's/.*[^0-9]\([0-9][0-9]*\)$/\1/p')"
[ -n "$disk_name" ] && [ -n "$part_num" ] || { echo "disque/partition introuvable" ; exit 0 ; }
command -v growpart >/dev/null || { apt-get update -y && apt-get install -y cloud-guest-utils ; }
set +e ; growpart "/dev/$disk_name" "$part_num" ; rc=$? ; set -e
[ "$rc" -eq 0 ] || [ "$rc" -eq 1 ] || exit 1
fstype="$(findmnt -n -o FSTYPE /)"
case "$fstype" in ext2|ext3|ext4) resize2fs "$root_src" ;; xfs) xfs_growfs / ;; esac
echo "== Place apres" ; df -h / | tail -n 1 || true
GROW
  chmod 755 /usr/local/sbin/doonya-grow-rootfs
  cat > /etc/sudoers.d/deploy-grow-rootfs <<'EOF'
deploy ALL=(root) NOPASSWD: /usr/local/sbin/doonya-grow-rootfs
EOF
  chmod 440 /etc/sudoers.d/deploy-grow-rootfs
  visudo -cf /etc/sudoers.d/deploy-grow-rootfs

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

  echo "== Systeme de fichiers root (occupe tout le disque deja alloue)"
  # Script embarque : preparer.sh est envoye seul sur stdin, pas le depot entier.
  # growpart/resize2fs sont appeles ici directement (meme logique que grow-rootfs.sh).
  root_src="$(findmnt -n -o SOURCE /)"
  disk_name="$(lsblk -no PKNAME "$root_src" 2>/dev/null || true)"
  part_num="$(echo "$root_src" | sed -n 's/.*[^0-9]\([0-9][0-9]*\)$/\1/p')"
  if [ -n "$disk_name" ] && [ -n "$part_num" ]; then
    set +e
    growpart "/dev/$disk_name" "$part_num"
    set -e
    fstype="$(findmnt -n -o FSTYPE /)"
    case "$fstype" in
      ext2|ext3|ext4) resize2fs "$root_src" || true ;;
      xfs) xfs_growfs / || true ;;
    esac
    df -h / | tail -n 1 || true
  fi

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
