# Déploiement (CD) : guide opérateur

Décisions et phases : [`PLAN_CD.md`](./PLAN_CD.md). Ce guide couvre : définir les variables et secrets d'une branche, préparer une VM, vérifier l'environnement, construire les images et déployer (SSH ou GCP).

## Principe

Chaque branche déployée (`develop`, `main`, `prod`) a son **environnement GitHub** du même nom, avec ses propres variables et secrets sous leur nom simple (`SECRET_KEY`, `VM_SSH_HOST`…). Une branche peut donc viser sa propre VM. GitHub fait foi : on peut modifier une valeur avec `deploy_env.py` ou dans l'interface (Settings > Environments > `<branche>`), à condition de garder le bon type (secret ou variable).

Chaque environnement est **réservé à sa branche** (Settings > Environments > `<branche>` > Deployment branches and tags : la seule branche `<branche>`). `deploy_env.py` pose cette règle en créant l'environnement et `etat` la contrôle. Sans elle, un workflow de n'importe quelle branche pourrait déclarer `environment: prod` et lire les secrets de `prod`. Conséquence : un workflow qui utilise l'environnement `prod` doit s'exécuter sur la branche `prod` (voir §4 à §6).

La liste des noms attendus est lue dans `backend/.env.example` et `frontend/.env.example` (ligne active = obligatoire, `# NOM=` = facultative, `# @secret` = secret) et dans `backend/scripts/deploy_env/spec.py` (`DEPLOY_*`, `VM_SSH_*`).

## 1. Préparer les fichiers de valeurs

À la racine du dépôt, un jeu de trois fichiers par branche, ignorés par Git (`.gitignore`) : `deploy_env.py` refuse de lire un fichier qui ne le serait pas. Format `.env` : `NOM=valeur`, sans commentaire en fin de ligne (une valeur peut contenir `#`).

| Fichier | Contenu |
|---|---|
| `backend.env.<branche>` | Les noms de `backend/.env.example` (`SECRET_KEY`, `DB_PASSWORD`, `ALLOWED_HOSTS`…) |
| `frontend.env.<branche>` | Les noms de `frontend/.env.example` (`VITE_API_URL`…) |
| `.env.deploy.<branche>` | `DEPLOY_NAMESPACE`, `DEPLOY_DOMAIN`, `DEPLOY_LETSENCRYPT_EMAIL`, `DEPLOY_ACCES` (`ssh` ou `gcp`), `DEPLOY_DB_MODE` (`interne` ou `externe`) ; en mode `gcp` aussi `GCP_PROJECT_ID`, `GCP_ZONE`, `GCP_INSTANCE`, `GCP_WIF_PROVIDER`, `GCP_SERVICE_ACCOUNT` (§7) |

Exemple de `.env.deploy.develop` :

```env
DEPLOY_NAMESPACE=devstreet-develop
DEPLOY_DOMAIN=develop.monapp.com
DEPLOY_LETSENCRYPT_EMAIL=ops@monapp.com
DEPLOY_ACCES=ssh
DEPLOY_DB_MODE=interne
```

Avec `DEPLOY_DB_MODE=interne`, la base est un conteneur du namespace : `DB_HOST=db` dans `backend.env.<branche>`.

## 2. Préparer la VM (une fois par VM)

L'environnement GitHub de la branche est créé (ou mis à jour) et réservé à sa branche avant toute action sur la VM : s'il ne peut pas l'être, le script s'arrête sans rien toucher.

Prérequis : une VM **Ubuntu LTS**, un utilisateur d'administration avec `sudo` sans mot de passe (ex. `ubuntu`, pas `root`) et une connexion SSH par clé (agent SSH ou `--cle-admin`).

Les infos de connexion à la VM vont dans `.env.vm.<branche>`, à la racine du dépôt (`cp .env.vm.example .env.vm.develop`). Ce fichier est ignoré par Git et n'est jamais envoyé à GitHub :

```env
VM_HOTE=203.0.113.10
VM_ADMIN_USER=ubuntu
VM_CLE_ADMIN=~/.ssh/ma_cle_admin
```

`VM_CLE_ADMIN` est le **chemin** de la clé, pas son contenu. Il est facultatif : sans lui, l'agent SSH est utilisé.

```powershell
python git-cli/deploy_env.py preparer-vm --branche develop
```

Les options `--hote`, `--admin-user` et `--cle-admin` restent possibles et priment sur le fichier, qui est alors facultatif.

Ces infos ne sont pas des secrets GitHub pour deux raisons :
- un secret GitHub ne se relit pas depuis le poste ;
- la clé d'administration (`sudo`) doit rester sur le poste.

Seuls les accès du compte `deploy` sont écrits dans GitHub.

Le script :
1. relève l'empreinte SSH de la VM et vous demande de la comparer à celle de votre fournisseur ;
2. installe Docker, crée l'utilisateur `deploy` (groupe `docker`, dossiers `/opt/apps` et `/srv/public`), active `ufw` (22, 80, 443), `fail2ban` et les mises à jour de sécurité ;
3. génère une clé SSH dédiée au déploiement et écrit dans l'environnement GitHub de la branche `VM_SSH_HOST`, `VM_SSH_USER`, `VM_SSH_PRIVATE_KEY` (secrets) et `VM_SSH_KNOWN_HOSTS` (variable, l'empreinte épinglée) ;
4. **seulement après avoir testé la connexion de `deploy`**, désactive le mot de passe SSH et la connexion directe en `root`.

La clé privée de déploiement n'est écrite nulle part ailleurs que dans GitHub : le dossier temporaire est supprimé à la fin.

## 3. Définir et contrôler les valeurs

```powershell
python git-cli/deploy_env.py definir --branche develop --dry-run   # liste les noms, n'écrit rien
python git-cli/deploy_env.py definir --branche develop             # crée l'environnement develop, y écrit après confirmation
python git-cli/deploy_env.py etat --branche develop                # règle de branche et valeurs comparées à la liste de référence
```

`definir` refuse les noms inconnus, les valeurs obligatoires vides ou invalides, et les `VM_SSH_*` (écrits par `preparer-vm`). Les valeurs ne sont jamais affichées.

`definir` est **idempotent** (upsert) : relancé avec les mêmes fichiers, il ne change rien. Il affiche d'abord, pour chaque nom, ce qu'il va faire (`cree`, `mis a jour`, `remplace`), puis n'écrit que cela :
- l'environnement n'est créé que s'il manque, et sa règle de branche n'est ajoutée que si elle manque ; un environnement déjà conforme n'est pas modifié (ses autres réglages sont conservés) ;
- une variable identique n'est pas réécrite ; un secret n'est pas relisible, il est donc réécrit, avec le même résultat ;
- un nom enregistré avec le mauvais type (secret en variable ou l'inverse) est supprimé après l'écriture du bon type ;
- un nom présent sur GitHub mais absent des fichiers locaux n'est **jamais** supprimé, et une règle de branche en trop n'est jamais retirée d'office : `definir` s'arrête et la signale. Ces commandes sont réservées aux `GIT_MASTER_EMAILS` et demandent `gh` connecté avec les droits d'administration du dépôt.

## 4. Vérifier depuis GitHub

Actions > **CD - VERIFIER ENVIRONNEMENT** > Run workflow > « Use workflow from » : la branche à vérifier (`develop`, `main` ou `prod` ; une autre branche est refusée). Le workflow ne reçoit aucune valeur et ne modifie rien : il contrôle la présence et le classement des variables et secrets, le DNS du domaine (il doit pointer vers la VM avant le premier déploiement, pour certbot), la connexion SSH avec l'empreinte épinglée, Docker, et que seuls les ports 22, 80 et 443 écoutent.

## 5. Construire les images

Actions > **CD - BUILD IMAGES** > Run workflow > « Use workflow from » : la branche (et, facultatif, un commit complet de 40 caractères ; vide = dernier commit de la branche). Réservé aux `GIT_MASTER_USERS`. Le workflow est aussi appelé par l'orchestrateur du déploiement. Il publie sur `ghcr.io/<organisation>/<dépôt>-backend` et `-frontend` :

| Image | Tag |
|---|---|
| backend | `<sha>` (identique pour tous les environnements) |
| frontend | `<branche>-<sha>-<empreinte>` : l'empreinte couvre `VITE_API_URL`, `VITE_API_V1_URL` et `VITE_GCS_BUCKET_NAME`, figées dans le JavaScript à la construction |

- Une image déjà publiée n'est **pas** reconstruite : redéployer un ancien commit (retour arrière) ne coûte aucune construction. Changer un `VITE_*` produit un nouveau tag frontend pour le même commit.
- Le commit doit appartenir à l'historique de la branche choisie : impossible de publier pour `prod` un commit absent de `prod`.
- Les variables `VITE_API_URL` et `VITE_API_V1_URL` doivent exister dans l'environnement de la branche (`definir`).
- La connexion au registre utilise le jeton du job, valable pendant l'exécution seulement. Les paquets créés sont privés et rattachés au dépôt.

## 6. Déployer

**Automatique** : un push ou un merge vers `develop`, `main` ou `prod` lance `CI - ORCHESTRATEUR`. Quand backend, frontend, sécurité et non-régression sont verts, son job `deploiement` appelle `CD - ORCHESTRATEUR`, qui construit les images puis déploie la branche selon `DEPLOY_ACCES` (`ssh` ou `gcp`). Le tout s'exécute sur la branche poussée, avec ses propres fichiers de workflow : c'est ce qui lui donne accès à son environnement. Un échec de la CI n'entraîne aucun déploiement ; une pull request non plus. Deux déploiements d'une même branche s'enchaînent, sans jamais s'interrompre ; deux déploiements de branches différentes sur la même VM s'attendent (verrou `/opt/apps/.deployer.lock`, 20 minutes d'attente au plus). Si, une fois la CI verte, le commit n'est plus la pointe de la branche (un push plus récent est arrivé), il n'est pas déployé : le plus récent le remplace, et un retour en arrière silencieux est évité.

**Manuel** (relance ou retour arrière) : Actions > **CD - ORCHESTRATEUR** > Run workflow > « Use workflow from » : la branche à déployer, et un commit complet (40 caractères) pour revenir à une version précédente. Réservé aux `GIT_MASTER_USERS`, lus dans `origin/develop` ; une autre branche que `develop`, `main` ou `prod` est refusée. Si les images de ce commit existent, rien n'est reconstruit. **Les migrations déjà appliquées ne sont pas annulées** : avant un retour arrière, vérifiez que l'ancienne image reste compatible avec le schéma de la base.

Prérequis avant le premier déploiement d'une branche : environnement complet (`etat` et **CD - VERIFIER ENVIRONNEMENT** verts), le DNS de `DEPLOY_DOMAIN` pointe vers la VM, et les ports 80 et 443 sont joignables (certbot valide le domaine en HTTP).

Ce qui se passe, dans l'ordre (`deploy/vm/deployer.sh`, exécuté sur la VM par l'utilisateur `deploy`) :

1. Le runner rend `backend.env` et `compose.env` depuis les variables et secrets (`scripts/deploy_env/render.py`) et refuse : une valeur manquante, une apostrophe ou un retour à la ligne dans une valeur, `DB_HOST` différent de `db` en mode `interne`, ou un `DEPLOY_DOMAIN` absent de `ALLOWED_HOSTS` (Django refuserait alors le contrôle de santé).
2. Il envoie `deploy/` et ces deux fichiers (droits 600) dans `/opt/apps/<namespace>/`, puis lance `deployer.sh`. Le jeton du registre passe par stdin et n'est jamais écrit sur le disque.
3. Sur la VM : téléchargement des images, démarrage du proxy partagé `/opt/apps/_proxy` (nginx et certbot), création de `/srv/public/<namespace>/{static,media}`, certificat Let's Encrypt au premier déploiement (site HTTP seul, puis `certbot certonly`), `docker compose up -d --wait`, puis site HTTPS.
4. Le runner contrôle `https://<domaine>/api/health` et `https://<domaine>/`.

Sur la VM : `/opt/apps/<namespace>/deploiement-actuel` contient le commit en place. Les journaux sont ceux de Docker (`docker compose -p <namespace> logs`), limités à 3 × 10 Mo par conteneur.

## 7. VM GCP sans IP publique (`DEPLOY_ACCES=gcp`)

Même déploiement, autre transport : `cd-deploiement-gcp.yml` atteint la VM par un **tunnel IAP** (`gcloud compute ssh --tunnel-through-iap`) et s'authentifie par **Workload Identity Federation** : aucune clé privée ni secret SSH n'est stocké dans GitHub. Les mêmes scripts (`deploy/vm/*.sh`) s'exécutent sur la VM, en tant que `deploy` (`sudo -u deploy`). Une branche peut rester en `ssh` pendant qu'une autre passe en `gcp`.

Prérequis côté GCP (à faire une fois ; **non vérifié depuis ce dépôt**) :

1. **API et VM** : APIs Compute Engine, IAP et IAM Credentials activées ; VM Ubuntu LTS **sans IP publique**, avec un accès sortant (Cloud NAT) pour télécharger les images et joindre Let's Encrypt ; **OS Login** activé (métadonnée `enable-oslogin=TRUE`).
2. **Pare-feu VPC** : autoriser le TCP 22 depuis `35.235.240.0/20` (plage d'IAP) ; le trafic public (80/443) arrive par un load balancer ou une IP de votre choix, hors du périmètre de ces workflows.
3. **Compte de service** (ex. `deploy@<projet>.iam.gserviceaccount.com`) avec `roles/iap.tunnelResourceAccessor`, `roles/compute.osAdminLogin` (accès `sudo` via OS Login) et `roles/compute.viewer` sur le projet ; `roles/iam.serviceAccountUser` sur le compte de service de la VM si elle en a un.
4. **Workload Identity Federation** : un pool et un fournisseur OIDC (`https://token.actions.githubusercontent.com`) avec l'attribut `attribute.environment=assertion.environment` et la condition `assertion.repository == "wendkoagenda/devstreet"`, puis `roles/iam.workloadIdentityUser` donné au compte de service pour le seul environnement concerné : `principalSet://iam.googleapis.com/projects/<numéro>/locations/global/workloadIdentityPools/<pool>/attribute.environment/<branche>`. Le jeton d'un job lié à l'environnement `prod` porte `environment: prod`, et seul un run sur la branche `prod` peut l'obtenir. `GCP_WIF_PROVIDER` vaut `projects/<numéro>/locations/global/workloadIdentityPools/<pool>/providers/<fournisseur>`.
5. **Préparer la VM** (avec votre propre compte gcloud, qui a les rôles 2 et 3) :

   ```powershell
   python git-cli/deploy_env.py preparer-vm-gcp --branche prod --projet <projet> --zone <zone> --instance <vm>
   ```

   Même préparation que le mode SSH (Docker, utilisateur `deploy`, `fail2ban`, mises à jour), avec le pare-feu `ufw` qui n'autorise le SSH que depuis la plage d'IAP.
6. Renseigner les `GCP_*` dans `.env.deploy.<branche>`, puis `definir` et `etat`, comme pour le mode SSH. Il n'y a ni `VM_SSH_*` ni secret à créer.

À savoir :
- En liant le compte de service à l'environnement (point 4) plutôt qu'au dépôt entier, seul un job de l'environnement de la branche, donc un run sur cette branche, peut l'utiliser.
- La clé SSH créée par `gcloud` pour la session expire après 30 minutes ; le jeton OIDC est échangé une fois contre un accès valable une heure.
- `DEPLOY_DOMAIN` doit être servi par votre load balancer (ou une IP) jusqu'aux ports 80/443 de la VM, sinon certbot ne peut pas valider le domaine.

## Limites à connaître

- **L'isolation tient à la règle de branche de chaque environnement** : si elle est retirée dans l'interface, les secrets redeviennent lisibles depuis toute branche. `etat` la contrôle. Elle repose aussi sur la protection des branches `develop`, `main` et `prod` : quiconque peut y pousser sans revue peut y modifier un workflow.
- **SSH ouvert à tous** sur la VM (les adresses des runners changent) : protégé par la clé seule et `fail2ban`. Le mode `gcp` (§7) supprime ce port public.
- **Un port publié par un conteneur contourne `ufw`** : seul le proxy partagé en publiera (phase 4). Le workflow de vérification le contrôle.
- **`deploy` vaut presque `root`** (groupe `docker`).
- **Rien de ceci n'a été exécuté de bout en bout** au moment de l'écriture : `preparer-vm`, `preparer-vm-gcp`, les workflows (dont le mode GCP, qui suppose une configuration IAM complète), `deployer.sh` et la configuration nginx sont à valider sur une VM de test (branche `develop`) avant `prod`. Seuls ont été contrôlés la syntaxe des scripts et des YAML, `docker compose config` sur les deux fichiers Compose et les tests du rendu.
- **Coupure brève** à chaque déploiement (remplacement des conteneurs, migrations au démarrage). Pas de déploiement sans interruption.
- **Pas de sauvegarde** de la base `interne` : le volume survit aux redéploiements, pas à la perte de la VM. Changer `DB_PASSWORD` après la première initialisation ne change pas le mot de passe déjà enregistré dans le volume.
- Les anciennes images s'accumulent sur la VM (seules les images sans nom sont nettoyées) : `docker image prune -a` à la main de temps en temps.
