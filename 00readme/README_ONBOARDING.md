# Onboarding : du clonage au déploiement

Détails : CI dans [`README_CI.md`](./README_CI.md), déploiement dans [`README_CD.md`](./README_CD.md), scripts Git dans [`git-cli/README.md`](../git-cli/README.md).

## 0. Prérequis

- Git, Python 3.12, Node.js 20, PostgreSQL.
- GitHub CLI `gh`, connecté : `gh auth login`.
- Pour préparer une VM depuis Windows : lancer les commandes dans **Git Bash**.

## 1. Cloner et installer les hooks

```bash
git clone https://github.com/wendkoagenda/devstreet.git
cd devstreet
python git-cli/install-hooks.py
python git-cli/doctor.py
```

`git commit` et `git push` directs sont bloqués : tout passe par `git-cli/`.

## 2. Lancer en local

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows (Linux/Mac : source venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env             # renseigner la base PostgreSQL
python manage.py migrate
python manage.py init_data
python manage.py runserver       # :8000
```

```bash
cd frontend
npm install
npm run dev                      # :5173
```

## 3. Nouveau projet tiré de devstreet (une fois)

- `git-cli/access_control.conf` : remplacer `GIT_MASTER_EMAILS`, `GIT_MASTER_USERS` et `ZONE_PROTEGEE_USERS` par l'équipe du projet.
- Créer les branches `develop`, `main` et `prod` sur GitHub.
- Settings > Branches : sur `develop`, `main` et `prod`, rendre obligatoires les contrôles `backend`, `frontend`, `securite` et `non-regression` (visibles après une première PR).

## 4. Développer

```bash
git checkout develop
python git-cli/pull.py
git checkout -b <prenom>-feat-<sujet>
# ... modifications ...
python git-cli/commit.py         # Conventional Commits, en français
python git-cli/push.py
python git-cli/pr.py             # cible : develop
```

Avant de pousser, en local (depuis `backend/`, venv active) :

```bash
python manage.py test
python -m scripts.security_scan --fail-on warning
```

Sur la PR, la CI lance `backend`, `frontend`, `securite` et `non-regression`. Une zone protégée touchée (`regression-guard.json`) attend la validation d'un responsable de zone. Merger une fois tout vert.

## 5. Préparer le déploiement d'une branche (une fois par branche, masters)

Exemple avec `develop`. Même chose pour `main` et `prod`.

1. **VM** : Ubuntu LTS, utilisateur `sudo` sans mot de passe (ex. `ubuntu`), accès SSH par clé.
2. **DNS** : `DEPLOY_DOMAIN` pointe vers l'IP de la VM.
3. **Préparer la VM** : copier `.env.vm.example` en `.env.vm.develop`, à la racine du dépôt, et y renseigner les infos de la VM. Ce fichier est ignoré par Git et reste sur le poste :

   ```env
   VM_HOTE=<ip-de-la-vm>
   VM_ADMIN_USER=ubuntu
   VM_CLE_ADMIN=<chemin-de-la-cle-ssh-admin>
   ```

   `VM_CLE_ADMIN` est facultatif si la clé est dans l'agent SSH. Lancer ensuite la commande ci-dessous. Elle crée aussi l'environnement GitHub `develop`, réservé à la branche `develop` :

   ```bash
   python git-cli/deploy_env.py preparer-vm --branche develop
   ```

   Comparer l'empreinte SSH affichée à celle du fournisseur avant de valider. Le script écrit lui-même les `VM_SSH_*` dans l'environnement GitHub.

4. **Fichiers de valeurs** à la racine du dépôt (ignorés par Git) :

   | Fichier | Contenu |
   |---|---|
   | `backend.env.develop` | Noms de `backend/.env.example` (`DB_HOST=db` en base interne, `DEPLOY_DOMAIN` dans `ALLOWED_HOSTS`) |
   | `frontend.env.develop` | Noms de `frontend/.env.example` |
   | `.env.deploy.develop` | `DEPLOY_NAMESPACE`, `DEPLOY_DOMAIN`, `DEPLOY_LETSENCRYPT_EMAIL`, `DEPLOY_ACCES=ssh`, `DEPLOY_DB_MODE=interne` |

5. **Écrire et contrôler les valeurs** :

   ```bash
   python git-cli/deploy_env.py definir --branche develop --dry-run
   python git-cli/deploy_env.py definir --branche develop
   python git-cli/deploy_env.py etat --branche develop
   ```

   `definir` est idempotent : il peut être relancé après chaque changement de valeur.

6. **Vérifier depuis GitHub** : Actions > **CD - VERIFIER ENVIRONNEMENT** > Run workflow > « Use workflow from » : `develop`. Doit être vert.

VM GCP sans IP publique (`DEPLOY_ACCES=gcp`) : voir [`README_CD.md` §7](./README_CD.md#7-vm-gcp-sans-ip-publique-deploy_accesgcp).

## 6. Déployer

- **Automatique** : chaque merge ou push vers `develop`, `main` ou `prod` lance la CI. Si elle est verte, la branche est construite (images `ghcr.io`) puis déployée sur sa VM.
- **Promotion** : PR `develop` → `main`, puis `main` → `prod` :

  ```bash
  git checkout develop
  python git-cli/pull.py
  python git-cli/pr.py --base main
  ```

  Pour `prod`, faire la même chose depuis `main`, avec `--base prod`.

- **Contrôle** : `https://<domaine>/api/health` répond 200.

## 7. Relancer ou revenir en arrière (masters)

Actions > **CD - ORCHESTRATEUR** > Run workflow > « Use workflow from » : la branche, puis le commit complet (40 caractères) à redéployer. Laisser vide pour redéployer la pointe de la branche.

Les migrations déjà appliquées ne sont pas annulées : vérifier que l'ancienne version reste compatible avec la base.
