# Déploiement (CD)

Exemple suivi : branche `sandbox`. Même enchaînement pour `main` et `prod`. `develop` n’est jamais déployée.

Sous Windows : **Git Bash**. Compte master (`git-cli/access_control.conf`) et `gh auth login` requis.

Références : [`PLAN_CD.md`](../00readme/PLAN_CD.md) · [`README_DEV.md`](../00readme/README_DEV.md) · [`SUITE_DES_TRAVAUX_DE_CD.md`](../00readme/SUITE_DES_TRAVAUX_DE_CD.md)

---

# Déploiement SSH

Accès à la VM par IP publique et clé SSH (`DEPLOY_ACCES=ssh`).

## Prérequis

- Être **sur la branche Git cible en local** (`git checkout sandbox` avant `--branche sandbox`) : `preparer-vm`, `definir` et `etat` refusent sinon
- VM Ubuntu LTS, user admin avec `sudo` sans mot de passe (ex. `ubuntu`), SSH par clé
- Clé SSH admin : générer / injecter selon [`.ssh/CREER_SSH.md`](../.ssh/CREER_SSH.md) (guide local, dossier `.ssh/` ignoré par Git ; convention `.ssh/<branche>_ssh`)
- Git, Python 3.12, `gh` connecté avec droits admin du dépôt

## Étape 1 : Créer les fichiers de configuration locaux

Ils portent les secrets et réglages de la branche. **Tous à la racine du dépôt** (pas dans `backend/` ni `frontend/`) — c’est ce que lit `git-cli/deploy_env.py`. Ignorés par Git. Format `NOM=valeur` (pas de `#` en fin de ligne).

Depuis la racine :

```bash
cp .env.vm.example .env.vm.sandbox
cp .env.deploy.example .env.deploy.sandbox
cp backend/.env.example backend.env.sandbox
cp frontend/.env.example frontend.env.sandbox
cp observabilite.env.example observabilite.env.sandbox
cp minio.env.example minio.env.sandbox
```

| Fichier (racine)            | Usage                                               |
| --------------------------- | --------------------------------------------------- |
| `.env.vm.sandbox`           | Connexion admin VM (`preparer-vm` seulement)        |
| `.env.deploy.sandbox`       | Namespace, domaine, mode accès / DB                 |
| `backend.env.sandbox`       | Variables backend (depuis `backend/.env.example`)   |
| `frontend.env.sandbox`      | Variables frontend (depuis `frontend/.env.example`) |
| `observabilite.env.sandbox` | Mot de passe Grafana (+ webhooks alerte optionnels) |
| `minio.env.sandbox`         | Compte root MinIO (console + provision)             |

### Renseigner `.env.vm.sandbox`

Déposer la clé privée admin dans `.ssh/` puis éditer :

```env
VM_HOTE=203.0.113.10
VM_ADMIN_USER=ubuntu
VM_CLE_ADMIN=.ssh/sshsandbox
```

`VM_CLE_ADMIN` = chemin de la clé (relatif à la racine, ou absolu / `~/...`). Facultatif si la clé est dans l’agent SSH.

### Renseigner `.env.deploy.sandbox`

Variables de déploiement uniquement (`DEPLOY_*`). Exemple déjà dans le fichier d’exemple : `DEPLOY_ACCES=ssh`, `DEPLOY_DB_MODE=interne`.  
`DEPLOY_DB_MODE` n’existe **pas** dans `backend/.env` / `backend.env.sandbox` : il est lu seulement depuis `.env.deploy.<branche>`.

### Renseigner `backend.env.sandbox` et `frontend.env.sandbox`

Noms = ceux de `backend/.env.example` et `frontend/.env.example` (pas de `DEPLOY_*`).

- Si `DEPLOY_DB_MODE=interne` (dans `.env.deploy.sandbox`) : dans `backend.env.sandbox`, mettre `DB_HOST=db` et inclure le domaine (`DEPLOY_DOMAIN`) dans `ALLOWED_HOSTS`.
- `frontend.env.sandbox` : au minimum `VITE_API_URL` et `VITE_API_V1_URL` (ex. `https://sandbox.monapp.com/api`). Si `USE_S3=True` dans `backend.env`, mettre aussi `VITE_USE_S3=true` (sinon le JS figé pointe vers `/media/` alors que les fichiers sont dans MinIO → 404).
- Connexion sociale (facultative) : `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `OAUTH_GITHUB_CLIENT_ID`, `OAUTH_GITHUB_CLIENT_SECRET` dans `backend.env.sandbox`. Les deux `*_CLIENT_ID` sont des variables GitHub, les deux `*_CLIENT_SECRET` des secrets. Le nom GitHub est écrit `OAUTH_GITHUB_*` et non `GITHUB_OAUTH_*` : GitHub refuse tout nom de secret ou de variable commençant par `GITHUB_` (erreur HTTP 422). Un fournisseur n'est actif que si son identifiant **et** son secret sont renseignés ; sans eux, ses boutons restent masqués. L'URL de rappel à déclarer chez le fournisseur est `https://<DEPLOY_DOMAIN>/api/auth/oauth/google/callback` (ou `.../github/callback`) : elle est construite depuis `FRONTEND_URL`, qui doit donc être l'URL publique exacte (`https://...`).

### Renseigner `observabilite.env.sandbox`

`GRAFANA_ADMIN_USER` (compte de connexion) et `GRAFANA_ADMIN_PASSWORD` (min. 16 caractères). Webhooks d’alerte Grafana (`SLACK_ALERT_WEBHOOK` / `TEAMS_ALERT_WEBHOOK`) facultatifs — distincts des `*_NOTIF_WEBHOOK` du CD.

### Renseigner `minio.env.sandbox`

`MINIO_ROOT_USER` et `MINIO_ROOT_PASSWORD` (min. 16 caractères). Poussé par `definir` comme les autres fichiers. Si `USE_S3=True` dans `backend.env.<branche>`, renseigner aussi `S3_*` (bucket + clés applicatives) dans ce même backend env — le job MinIO provisionne le bucket.

## Étape 2 : Préparer la VM

Installe Docker, crée l’utilisateur `deploy`, durcit SSH, et enregistre les accès `VM_SSH_*` dans l’environnement GitHub `sandbox`. La clé admin reste sur le poste.

```bash
git checkout sandbox
python git-cli/deploy_env.py preparer-vm --branche sandbox
```

Comparer l’empreinte SSH affichée à celle du fournisseur avant de confirmer.  
Options `--hote`, `--admin-user`, `--cle-admin` : primaries sur `.env.vm.sandbox`.

## Étape 3 : Envoyer les variables et secrets sur GitHub

Lit les quatre fichiers à la racine (`backend.env.sandbox`, `frontend.env.sandbox`, `.env.deploy.sandbox`, `observabilite.env.sandbox`) et les écrit dans l’environnement GitHub `sandbox`.

```bash
python git-cli/deploy_env.py definir --branche sandbox --dry-run
python git-cli/deploy_env.py definir --branche sandbox
python git-cli/deploy_env.py etat --branche sandbox
```

`definir` est idempotent. Il ne touche pas aux `VM_SSH_*` (déjà posés à l’étape 2) et ne supprime jamais un nom présent sur GitHub mais absent des fichiers locaux.

## Étape 4 : Pointer le DNS vers la VM

Pour que certbot délivre le certificat HTTPS au premier déploiement, faire pointer `DEPLOY_DOMAIN` (ex. `sandbox.monapp.com`) vers l’IP de la VM (ports 80 et 443 joignables).

## Étape 5 : Vérifier l’environnement depuis GitHub

Contrôle en lecture seule : variables, secrets, DNS, SSH, Docker, ports 22/80/443 (et 20201/20202 agents de métriques GCP, acceptés).

Actions → **CD - VERIFIER ENVIRONNEMENT** → Run workflow → « Use workflow from » : `sandbox`.

Enchaîner seulement si le run est vert et que `etat` (étape 3) est OK.

## Étape 6 : Déployer

Prérequis : étapes 2 à 5 OK (`VM_SSH_*` présents, `definir`/`etat` OK, DNS pointé, workflow **CD - VERIFIER ENVIRONNEMENT** vert).

### Déploiement automatique (cas normal)

1. Pousser ou merger du code vers `sandbox` (pas `develop`).
2. Attendre que **CI - ORCHESTRATEUR** soit vert sur ce commit.
3. La CI appelle alors **CD - ORCHESTRATEUR** sur `sandbox` (même commit).
4. Si un commit plus récent est déjà sur `sandbox`, un déploiement « en retard » est ignoré.

Suivre le run dans Actions → **CD - ORCHESTRATEUR** (jobs `images` puis `deploiement-ssh`).

### Déploiement manuel (relance ou retour arrière)

Réservé aux comptes listés dans `GIT_MASTER_USERS` (`git-cli/access_control.conf`).

1. Actions → **CD - ORCHESTRATEUR** → **Run workflow**.
2. « Use workflow from » : `**sandbox**` (obligatoire : l’environnement GitHub `sandbox` n’est utilisable que depuis cette branche).
3. Champ **sha** (optionnel) :
   - vide → déploie le dernier commit de `sandbox` ;
   - sinon → commit complet (40 caractères hex) déjà présent sur `sandbox` (retour arrière).
4. Lancer, puis attendre la fin verte des jobs `images` et `deploiement-ssh`.

Les migrations Django déjà appliquées **ne sont pas annulées** en cas de retour arrière.

### Après un déploiement réussi

Contrôle navigateur / curl (remplacer par votre `DEPLOY_DOMAIN`) :

```text
https://sandbox.monapp.com/api/health  →  200
https://sandbox.monapp.com/            →  200
```

Sur la VM (utilisateur `deploy`) :

```bash
# Commit actuellement déployé
cat /opt/apps/<DEPLOY_NAMESPACE>/deploiement-actuel

# Logs de l'application
docker compose -p <DEPLOY_NAMESPACE> logs
```

Exemple si `DEPLOY_NAMESPACE=boilerplate-sandbox` : `/opt/apps/boilerplate-sandbox/…` et `docker compose -p boilerplate-sandbox logs`.

### Relance des images seules (optionnel)

L’orchestrateur rebuild déjà les images à chaque déploiement. Pour forcer un build **sans** déployer : Actions → **CD - BUILD IMAGES** → « Use workflow from » : `sandbox` (+ sha optionnel).

### Notifications Slack / Teams

En fin de **CD - ORCHESTRATEUR** (et de **CI - ORCHESTRATEUR**, voir `00readme/README_CI.md`), les jobs `notif-succes` / `notif-echec` envoient un message si au moins un secret est présent dans l’environnement GitHub de la branche :

| Secret | Canal |
|---|---|
| `SLACK_NOTIF_WEBHOOK` | Incoming Webhook Slack |
| `TEAMS_NOTIF_WEBHOOK` | Incoming Webhook / Workflows Teams |

Les deux sont **facultatifs**. Absents tous les deux : le déploiement (ou la CI) n’échoue pas ; un avertissement apparaît dans le run (`::warning::`). Un seul renseigné → un canal ; les deux → les deux.

Pour les notifications de **pull request** (CI), les secrets d’environnement ne sont pas accessibles (environnement réservé à sa branche) : recopier les mêmes webhooks en secrets de **dépôt** (Settings > Secrets and variables > Actions) si vous voulez être notifié sur les PR.

Dans `.env.deploy.sandbox` (puis `definir --branche sandbox`) :

```env
SLACK_NOTIF_WEBHOOK=https://hooks.slack.com/services/...
TEAMS_NOTIF_WEBHOOK=https://...
```

Contenu typique : bannière **SUCCES** (vert) ou **ECHEC** (rouge), titre, branche, domaine, SHA court, sujet du commit, acteur, accès (`ssh`/`gcp`), bouton vers le run ; en échec, l’étape en cause. Même style pour les notifications CI.

Ces secrets ne sont **jamais** copiés sur la VM (`backend.env` / `compose.env`).

## Maintenance (CD - MAINTENANCE …)

Un **workflow Actions par volet** (formulaire avec uniquement les champs utiles). Branches **`sandbox`** / **`main`** ; **`prod` uniquement** pour logs-urgence. Masters (`GIT_MASTER_USERS`). Accès SSH.

| Workflow Actions | Confirmation / inputs | Rôle |
|---|---|---|
| **CD - MAINTENANCE reset-db** | `RESET-DB-<branche>` | Effacer le volume Postgres interne |
| **CD - MAINTENANCE db-forward** | `DB-FORWARD-OPEN-<branche>` | Forward Postgres sur la VM (TTL 8 h) |
| **CD - MAINTENANCE disk-set** | `DISK-SET-<branche>` + `disk_gb` | Étendre la partition après resize GCP |
| **CD - MAINTENANCE docker-cleanup** | `DOCKER-CLEANUP-<branche>` | Images/cache/conteneurs arrêtés ; **aucun volume** (pgdata, grafana-data, …) |
| **CD - MAINTENANCE logs-urgence** | `LOGS-URGENCE-<branche>` + `since` | Artefact : `backend.log`, `frontend.log`, `proxy.log`, `observabilite.log` |
| **CD - OBSERVABILITE SSH** | (re)déploie la stack | Grafana / Prometheus / Loki sur la VM (aussi lancé après chaque deploy SSH) |

Accès Grafana / console MinIO (pas un workflow) : tunnel local ci-dessous → http://localhost:13000 et http://localhost:19001. Le moteur maintenance est `cd-maintenance.yml`.

### Reset volume Postgres

Si le mot de passe GitHub (`DB_PASSWORD`) ne correspond plus au volume `pgdata` :

1. Actions → **CD - MAINTENANCE reset-db** → confirmation `RESET-DB-sandbox` (ou `-main`)
2. Effet : arrêt `db` + suppression `<DEPLOY_NAMESPACE>_pgdata`. **Pas** de redéploiement auto.
3. Relancer **CD - ORCHESTRATEUR** pour recréer Postgres avec le `DB_PASSWORD` actuel.

### Accès pgAdmin / client SQL

La base `interne` n’écoute pas sur Internet. **CD - MAINTENANCE db-forward** ouvre `127.0.0.1:5432` → conteneur `db` sur la VM (fermeture auto **8 h**).

1. Confirmation `DB-FORWARD-OPEN-sandbox` (ou `-main`)
2. Tunnel local (section suivante) — Postgres, Grafana **et** console MinIO
3. pgAdmin : Host `127.0.0.1`, Port **`15432`**, Database / User = `DB_NAME` / `DB_USER`, Password = `DB_PASSWORD`

Si `password authentication failed` : secret `DB_PASSWORD` exact, ou **reset-db** / `ALTER USER`.

### Agrandir le disque utilisé

1. **Console GCP** : agrandir le disque (ex. 50 → 100 Go).
2. **CD - MAINTENANCE disk-set** : `disk_gb=100`, confirmation `DISK-SET-sandbox` → `DEPLOY_DISK_GB` + `growpart` / `resize2fs`.

### Nettoyage Docker

**CD - MAINTENANCE docker-cleanup** : images inutilisées, cache build, conteneurs **arrêtés**, réseaux orphelins.

**Message explicite** : aucun volume Docker n’est supprimé — ni `pgdata` (Postgres), ni `grafana-data` (Grafana), ni `minio-data` (MinIO), ni les volumes Loki / Prometheus / Alloy. Les stacks **en cours** (app, proxy, observabilité, minio) ne sont pas arrêtées.

### Logs d’urgence

**CD - MAINTENANCE logs-urgence** : `since` + confirmation `LOGS-URGENCE-<branche>`. Artefact `logs-urgence-<branche>` (rétention 1 j) :

| Fichier | Contenu |
|---|---|
| `backend.log` | Service Compose `backend` |
| `frontend.log` | Service Compose `frontend` |
| `proxy.log` | Stack proxy (si présente) |
| `observabilite.log` | Stack Grafana/Prometheus/Loki (si présente) |
| `minio.log` | Stack MinIO (si présente) |
| `meta.txt` / `statut.txt` | Contexte et bilans |

### Tunnel SSH local (Postgres + Grafana + MinIO)

Grafana écoute déjà `127.0.0.1:3000` sur la VM : **aucun** volet maintenance pour l’ouvrir/fermer. Idem console MinIO (`127.0.0.1:9001`). Postgres a besoin de `db-forward-open` une fois (TTL 8 h), puis le même tunnel local suffit pour les trois.

```powershell
python git-cli/deploy_env.py tunnel --branche sandbox
```

| Service | Sur ton PC |
|---|---|
| Grafana | http://localhost:13000 |
| Console MinIO | http://localhost:19001 |
| Postgres | `127.0.0.1:15432` (après `db-forward-open`) |

Keepalive + reconnexion auto ; arrêt après **8 h** ou Ctrl+C. Lit `.env.vm.sandbox`. N’exige ni compte master ni branche Git locale.

**Alternative manuelle** (Git Bash) :

```bash
ssh -N \
  -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o ExitOnForwardFailure=yes \
  -i .ssh/sandbox_ssh \
  -L 127.0.0.1:15432:127.0.0.1:5432 \
  -L 127.0.0.1:13000:127.0.0.1:3000 \
  -L 127.0.0.1:19001:127.0.0.1:9001 \
  sandbox@<VM_HOTE>
```

Ou entrée dans `~/.ssh/config` :

```
Host doonya-sandbox
  HostName <VM_HOTE>
  User sandbox
  IdentityFile <chemin-absolu>/.ssh/sandbox_ssh
  IdentitiesOnly yes
  ServerAliveInterval 30
  ServerAliveCountMax 3
  ExitOnForwardFailure yes
  LocalForward 127.0.0.1:15432 127.0.0.1:5432
  LocalForward 127.0.0.1:13000 127.0.0.1:3000
  LocalForward 127.0.0.1:19001 127.0.0.1:9001
```

Puis `ssh -N doonya-sandbox`.

**pgAdmin sans terminal** : propriétés du serveur → onglet **SSH Tunnel** (hôte VM, user admin, clé `.ssh/sandbox_ssh`) ; onglet **Connection** → Host `127.0.0.1`, Port `5432`. Le forward VM (`db-forward-open`, TTL 8 h) reste nécessaire. Grafana : même tunnel → http://localhost:13000. MinIO console → http://localhost:19001.

### Observabilité (Grafana) — flow

| Étape | Où |
|---|---|
| Installer / mettre à jour la stack | Auto après chaque deploy SSH, ou Actions → **CD - OBSERVABILITE SSH** |
| Ouvrir la console | En local : `python git-cli/deploy_env.py tunnel --branche sandbox` → http://localhost:13000 |
| Dashboards Doonya | Menu **Dashboards → Browse → dossier Doonya** (pas Starred / Home). Après un changement de JSON : relancer **CD - OBSERVABILITE SSH** (pas de migration). |
| Logs d’urgence de la stack | **CD - MAINTENANCE logs-urgence** → fichier `observabilite.log` |

Stack auto-hébergée **indépendante de GCP** : Grafana, Prometheus, Loki, Alloy, node-exporter, cAdvisor. Une seule instance par VM (`/opt/apps/_observabilite`), partagée comme le proxy. Le dashboard **MinIO** suit le conteneur `minio-serveur` (cAdvisor + logs Loki).

Un échec du job `observabilite-ssh` fait échouer le CD (`notif-echec`). Mode `DEPLOY_ACCES=gcp` : pas encore branché.

**Fichier dédié** `observabilite.env.<branche>` (poussé par `definir`, voir `observabilite.env.example`) :

```env
GRAFANA_ADMIN_USER=admin     # compte de connexion (variable GitHub)
GRAFANA_ADMIN_PASSWORD=...   # secret, min. 16 caractères
# SLACK_ALERT_WEBHOOK=...    # facultatif (alertes Grafana ; distinct des *_NOTIF_WEBHOOK du CD)
# TEAMS_ALERT_WEBHOOK=...
```

Le nom de compte (`GF_SECURITY_ADMIN_USER`) n’est pris en compte qu’au **premier** démarrage Grafana (volume `grafana-data` vide). Un changement ultérieur de `GRAFANA_ADMIN_USER` sans recréer le volume ne renomme pas le compte existant ; le mot de passe, lui, est réappliqué à chaque déploiement.

**Prérequis** : ~1 Go de RAM en plus (VM 4 Go recommandée). Rétention : métriques 15 j / 2 Go max ; logs 7 j.

**Accès** : `python git-cli/deploy_env.py tunnel --branche sandbox`, puis `http://localhost:13000` (utilisateur = `GRAFANA_ADMIN_USER`, mot de passe = `GRAFANA_ADMIN_PASSWORD`). Grafana écoute seulement `127.0.0.1:3000` sur la VM.

Tableaux de bord provisionnés (dossier Grafana **Doonya**) : **General**, **Backend**, **Frontend**, **Proxy**, **Postgres**, **MinIO**. Alertes : disque `/` > 85 %, RAM disponible < 10 %, conteneur backend / proxy-nginx absent, taux 5xx nginx > 5 %.

Arrêt manuel sur la VM : `docker compose -p observabilite --project-directory /opt/apps/_observabilite down`.

### MinIO (stockage objet S3) — flow

| Étape | Où |
|---|---|
| Installer / mettre à jour la stack | Auto après chaque deploy SSH (`minio-ssh`), ou Actions → **CD - MINIO SSH** |
| Console admin | Tunnel → http://localhost:19001 (`MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD`) |
| Lecture des objets | Bucket **privé**, aucune route Nginx vers MinIO : seule l’application lit les objets (`GET /api/v1/files/<chemin>`, utilisateur connecté) |
| Activer l’app Django/frontend | `USE_S3=True` + `S3_ENDPOINT_URL` (`http://minio-serveur:9000`), `S3_BUCKET_NAME`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` dans `backend.env` ; `VITE_USE_S3=true` côté frontend |
| Vérifier | `docker exec <conteneur backend> python manage.py check_storage` |
| Logs d’urgence | **CD - MAINTENANCE logs-urgence** → `minio.log` |

Stack partagée `/opt/apps/_minio` (réseau `proxy`), volume `minio-data` préservé. Si `USE_S3=False`, le serveur tourne quand même (console) sans provisionner de bucket applicatif.

Images Docker : `pgsty/silo` + `pgsty/mc` (forks S3 compatibles). Les images officielles `minio/minio` / `minio/mc` ont été retirées de Docker Hub ; ne pas les rétablir.

### Gitea (forge Git) — flow

Gitea tourne sur la même VM que l'application (`/opt/apps/_gitea`, réseau `proxy`), avec son propre Postgres (`gitea-db`) et son domaine HTTPS (ex. `git.devstreet.ewo-soft.com`). Contrairement à MinIO, le workflow est **manuel** : la forge porte des données, elle n'est pas redéployée à chaque commit.

| Étape | Où |
|---|---|
| Fichier local | `gitea.env.<branche>` (modèle : `gitea.env.example`) : `GITEA_DOMAIN`, `GITEA_DB_PASSWORD`, `GITEA_ADMIN_USER` (pas `admin`, nom réservé), `GITEA_ADMIN_PASSWORD`, `GITEA_ADMIN_EMAIL` |
| Envoyer sur GitHub | `python git-cli/deploy_env.py definir --branche <branche>` (le fichier est facultatif : sans lui, l'environnement n'a pas de forge) |
| DNS | Enregistrement A de `GITEA_DOMAIN` vers la VM, **avant** le workflow (certificat Let's Encrypt) |
| Installer / mettre à jour | Actions → **CD - GITEA SSH** (après un déploiement app SSH, qui crée le réseau `proxy`) |
| Jeton admin API | À la main, une fois (voir [gitea-deploy.md](../docs/devstreet_hub/gitea-deploy.md)) |
| Raccorder Django | `DEVSTREET_HUB_GITEA_*` dans `backend.env.<branche>`, `definir`, puis redéployer l'app |

Django appelle Gitea en interne (`DEVSTREET_HUB_GITEA_URL=http://gitea:3000`, accepté en HTTP pour ce seul hôte) ; les humains et `git clone` passent par `DEVSTREET_HUB_GITEA_PUBLIC_URL=https://<GITEA_DOMAIN>`. SSH de Gitea désactivé : Git par HTTPS uniquement. Le webhook push cible l'URL publique de l'API.

## Limites utiles

- Coupure brève à chaque déploiement ; pas de zero-downtime.
- Base `interne` : pas de sauvegarde auto ; changer `DB_PASSWORD` après la 1re init ne met pas à jour le volume (utiliser **CD - MAINTENANCE reset-db** sur sandbox ou main).
- L’utilisateur `deploy` est quasi-root (groupe `docker`).
- Disque VM : voir **`disk-set`** ci-dessus (console GCP puis maintenance). Aligner `.env.deploy.<branche>` + `definir` si la variable GitHub n’a pas pu être écrite. Urgence admin : `sudo growpart /dev/sda 1 && sudo resize2fs /dev/sda1`. Nettoyage Docker : `docker-cleanup`. Chaque déploiement : grow partition si possible + `cleanup-docker.sh` ; logs Docker limités (10m × 3) via `preparer-vm`.

---

# Déploiement avec stack GCP

VM **sans IP publique**, accès runner → VM par tunnel **IAP** (`DEPLOY_ACCES=gcp`). Pas de clé SSH stockée dans GitHub. Les scripts sur la VM (`deploy/vm/*.sh`) sont les mêmes qu’en SSH.

Les étapes détaillées (IAM, `preparer-vm-gcp`, valeurs `GCP_*`, déploiement) seront ajoutées ici. En attendant : [`PLAN_CD.md`](../00readme/PLAN_CD.md) et le code (`cd-deploiement-gcp.yml`, `deploy/ci/gcp-vm.sh`).

## Ops Agent (métriques VM sur GCP)

Quand la VM tourne sur **Compute Engine**, installer l’[Ops Agent](https://cloud.google.com/stackdriver/docs/solutions/agents/ops-agent) pour remonter métriques et logs vers Cloud Monitoring / Logging (ports agents déjà acceptés par **CD - VERIFIER ENVIRONNEMENT** : 20201 / 20202).

À exécuter dans **Cloud Shell** (adapter `INSTANCE`, `PROJECT`, `ZONE` si besoin) :

```bash
gcloud compute ssh vm-boileurplate \
    --project=doonyalabs-boilerplate \
    --zone=us-central1-c \
    --command="curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh && sudo bash add-google-cloud-ops-agent-repo.sh --also-install"
```

Effet : SSH vers l’instance, dépôt Google Cloud Ops Agent, installation et démarrage de l’agent. Vérifier ensuite dans la console GCP → Monitoring que la VM apparaît avec des métriques.