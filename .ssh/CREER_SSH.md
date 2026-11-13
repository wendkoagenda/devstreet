# Créer la clé SSH admin d'une VM

Ce guide est le seul fichier versionné de `.ssh/` : les clés (`.ssh/<branche>_ssh`) restent hors Git.

## 1. Générer la paire (depuis la racine du dépôt)

```bash
ssh-keygen -t ed25519 -C "sandbox" -f .ssh/sandbox_ssh
```

Convention : `.ssh/<branche>_ssh`, et le commentaire `-C` = utilisateur Linux de la VM.

## 2. Injecter la clé publique

VM GCP : ajouter dans les métadonnées SSH de l'instance la ligne `sandbox:<contenu de .ssh/sandbox_ssh.pub>`.

Autre fournisseur : ajouter la clé publique dans `~/.ssh/authorized_keys` de l'utilisateur admin.

## 3. Renseigner `.env.vm.<branche>`

```
VM_HOTE=<IP>
VM_ADMIN_USER=sandbox
VM_CLE_ADMIN=.ssh/sandbox_ssh
```

`VM_ADMIN_USER` peut être `root`, ou un utilisateur avec `sudo -n` sans mot de passe.

## 4. Vérifier

```bash
ssh -i .ssh/sandbox_ssh sandbox@<IP>
sudo -n true
```
