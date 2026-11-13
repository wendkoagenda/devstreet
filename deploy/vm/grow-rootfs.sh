#!/bin/sh
# Etend la partition et le systeme de fichiers root pour occuper tout le disque.
# Cas typique GCP : disque agrandi a 100 Go dans la console, partition / encore a ~9 Go.
# Execute en root :
#   sudo -n sh deploy/vm/grow-rootfs.sh
# Idempotent : sans espace libre sur le disque, ne change rien (code 0).
set -eu

if [ "$(id -u)" -ne 0 ]; then
  echo "ERREUR : grow-rootfs.sh doit s'executer en root (sudo)." >&2
  exit 1
fi

echo "== Place avant"
df -h / | tail -n 1 || true
lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS || true

root_src="$(findmnt -n -o SOURCE /)"
# /dev/sda1 ou /dev/mapper/...
case "$root_src" in
  /dev/*) ;;
  *)
    echo "ERREUR : peripherique root inattendu : $root_src" >&2
    exit 1
    ;;
esac

# Partitions classiques /dev/sda1 (pas LVM)
if [ ! -b "$root_src" ] || echo "$root_src" | grep -q mapper; then
  echo "AVERTISSEMENT : root=$root_src (LVM/complexe) : agrandissement auto non gere."
  exit 0
fi

disk_name="$(lsblk -no PKNAME "$root_src" 2>/dev/null || true)"
if [ -z "$disk_name" ]; then
  echo "AVERTISSEMENT : disque parent introuvable pour $root_src."
  exit 0
fi
disk="/dev/$disk_name"
part_num="$(echo "$root_src" | sed -n 's/.*[^0-9]\([0-9][0-9]*\)$/\1/p')"
if [ -z "$part_num" ]; then
  echo "AVERTISSEMENT : numero de partition introuvable pour $root_src."
  exit 0
fi

if ! command -v growpart >/dev/null 2>&1; then
  echo "== Installation de cloud-guest-utils (growpart)"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -y
  apt-get install -y cloud-guest-utils
fi

echo "== growpart $disk $part_num"
set +e
growpart "$disk" "$part_num"
grow_rc=$?
set -e
# 0 = agrandi, 1 = deja a la taille max
if [ "$grow_rc" -ne 0 ] && [ "$grow_rc" -ne 1 ]; then
  echo "ERREUR : growpart a echoue (code $grow_rc)." >&2
  exit 1
fi

fstype="$(findmnt -n -o FSTYPE /)"
echo "== Agrandissement filesystem ($fstype)"
case "$fstype" in
  ext2|ext3|ext4)
    resize2fs "$root_src"
    ;;
  xfs)
    xfs_growfs /
    ;;
  *)
    echo "AVERTISSEMENT : fstype $fstype non gere automatiquement."
    ;;
esac

echo "== Place apres"
df -h / | tail -n 1 || true
