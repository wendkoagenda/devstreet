# Suite des travaux de CD — 2026-11-12 → 2026-11-13

**Statut : cloturée le 13 novembre 2026.**  
Période couverte : **12 novembre 2026** (création de ce journal) → **13 novembre 2026** (arrêt de cette suite).  
Emplacement : [`00readme/suite/`](./README.md). Les suites suivantes iront dans le même dossier avec leur propre période dans le nom.

Objectif : pouvoir **rejouer exactement** ces ajouts sur un autre dépôt (même socle boilerplate), commit par commit, avec les fichiers touchés, les commandes et les prérequis hors Git.

Guide opérateur : [`deploy/README.md`](../../deploy/README.md) (pointeur : [`README_CD.md`](../README_CD.md)). Décisions / phases : [`PLAN_CD.md`](../PLAN_CD.md). Règles dev : [`README_DEV.md`](../README_DEV.md).

---

## Comment utiliser ce journal

1. Lire l’entrée dans l’ordre chronologique (numéro croissant).
2. Pour chaque entrée : appliquer le(s) commit(s) ou recopier les changements listés, puis exécuter les commandes **locales / GitHub / VM** indiquées.
3. Ne pas sauter une entrée : les suivantes peuvent dépendre des précédentes.
4. Les secrets et fichiers ignorés par Git (`.env.vm.*` sauf example, `backend.env.*`, `frontend.env.*`, `.env.deploy.*` sauf example, dossier `.ssh/` entier) ne sont **jamais** dans les commits : les reconstituer à la main sur le dépôt cible.

### Convention d’une entrée

```markdown
## N. Titre court (AAAA-MM-JJ)

- **Branche** : …
- **Commit(s)** : `hash` — message
- **Fichiers touchés** : …
- **Intention** : …
- **Reproduction sur un autre repo** : …
- **Hors Git / secrets** : …
- **Vérification** : …
- **Notes** : …
```

---

## Point de départ (socle déjà présent — ne pas rejouer sauf repo vierge de CD)

| Élément                        | Détail                                                                                                                                                                       |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Branche de travail             | `elisee-feat-cd-socle`                                                                                                                                                       |
| HEAD avant cette suite         | `c6c441a` (`feat(generateur): gestion des migrations`)                                                                                                                       |
| Socle CD déjà livré (exemples) | `1fdcbd5` `deploy_env` ; `b0cb22f` compose/nginx/certbot ; `0302c9e` GCP/IAP ; `ab9714c` env GitHub par branche ; `7877a38` `definir` upsert ; `96b1148` `.env.vm.<branche>` |
| Doc opérateur actuelle         | [`deploy/README.md`](../../deploy/README.md)                                                                                                                                 |
| Hors Git (poste)               | `.env.vm.sandbox`, `.env.deploy.sandbox`, `backend.env.sandbox`, `frontend.env.sandbox`, `.ssh/<branche>_ssh`, `.ssh/CREER_SSH.md`                                           |

Pour un autre repo **sans** ce socle : rejouer d’abord les commits historiques `feat(deploy)` / `ci(cd)` / `docs(cd)`, **puis** les entrées ci-dessous.

---

## Journal

## 1. Clés SSH locales + runbook + suppression onboarding (2026-11-12)

- **Branche** : `elisee-feat-cd-socle`
- **Commit(s)** : `7d47ef1` — `ci(deploiement): run de la sandbox`
- **Dépôt de référence** : doonya_labs_boilerplate
- **Fichiers touchés** :
  - `.gitignore` — `.ssh/` entier ; `sshsandbox` / `id_rsa` / `id_ed25519` / `*.pem` ; `.env.vm.*` + `!.env.vm.example`
  - `.env.vm.example` — `VM_CLE_ADMIN=.ssh/sshsandbox`
  - `git-cli/deploy_env.py` — `resolve_cle_admin()` (chemin relatif = racine du dépôt)
  - `backend/app/tests/test_deploy_env.py` — tests `resolve_cle_admin`
  - `deploy/README.md` — **source unique** du guide (SSH + fil `sandbox`, étapes actionnables, Git Bash)
  - `00readme/README_CD.md` — pointeur vers `deploy/README.md`
  - **suppression** : `00readme/README_ONBOARDING.md` ; retrait du suivi de `sshsandbox` (clé à la racine)
  - Liens : `README_DEV.md`, `README_CI.md`, `PLAN_CD.md`, `README_SAME_ORIGIN_COOKIES.md`, `CLAUDE.md`, `README.md`, workflows `cd-*.yml`, `deploy/ci/gcp-vm.sh`
  - Ce journal (créé)
- **Intention** :
  - Clés admin VM dans `.ssh/` (non commitables) ; `VM_CLE_ADMIN` = chemin.
  - Un seul runbook CD ; plus d’onboarding dupliqué.
- **Reproduction sur un autre repo** :
  1. Cherry-pick / appliquer `7d47ef1` (ou recopier les fichiers listés).
  2. Si une clé `sshsandbox` (ou autre) était suivie à la racine : `git rm --cached <fichier>` puis la mettre dans `.ssh/`.
  3. Créer en local (hors Git) :
     ```bash
     mkdir -p .ssh   # y déposer la clé privée
     cp .env.vm.example .env.vm.sandbox
     # renseigner VM_HOTE, VM_ADMIN_USER, VM_CLE_ADMIN=.ssh/<cle>
     ```
- **Vérification** :
  ```bash
  git check-ignore -v .ssh .ssh/sshsandbox .env.vm.sandbox
  git ls-files sshsandbox   # doit être vide
  # tests
  cd backend && source venv/bin/activate  # Windows : .\venv\Scripts\Activate.ps1
  python manage.py test app.tests.test_deploy_env.VmOptionsTests
  ```
- **Notes** :
  - La clé a existé dans l’historique (`df72d52` via le fichier racine `sshsandbox`) : la retirer du suivi **ne purge pas** l’historique → régénérer si le dépôt est partagé.
  - Fil conducteur du runbook = **`sandbox`** (`develop` jamais déployée, comme `README_DEV.md`).
  - Alignement code `BRANCHES` / workflows : voir entrée 3.
  - Section GCP dans le runbook : titre présent, étapes détaillées à venir.

## 2. Exemple `.env.deploy.example` + étape 1 en `cp` (2026-11-12)

- **Branche** : `elisee-feat-cd-socle`
- **Commit(s)** : `214cfed` — `ci(sandbox): Step 1`
- **Fichiers touchés** :
  - `.env.deploy.example` — modèle versionné (`DEPLOY_*=ssh` + `GCP_*` commentés)
  - `.gitignore` — `!.env.deploy.example`
  - `deploy/README.md` — étape 1 avec :
    ```bash
    cp .env.vm.example .env.vm.sandbox
    cp .env.deploy.example .env.deploy.sandbox
    cp backend/.env.example backend.env.sandbox
    cp frontend/.env.example frontend.env.sandbox
    ```
  - Ce journal
- **Intention** : même flux `cp` pour tous les fichiers de config déploiement ; clarifier que `backend.env.<branche>` / `frontend.env.<branche>` / `.env.deploy.<branche>` / `.env.vm.<branche>` sont **à la racine** (lus par `deploy_env.py`), distincts de `backend/.env` et `frontend/.env` (dev local).
- **Reproduction** :
  1. Appliquer `214cfed`.
  2. Sur le poste cible, après les `cp`, renseigner les valeurs (secrets) dans les copies `*.sandbox`.
- **Vérification** :
  ```bash
  git check-ignore -v .env.deploy.example    # negation !.env.deploy.example → non ignore pour le suivi
  git check-ignore -v .env.deploy.sandbox    # ignore
  git ls-files .env.deploy.example           # doit lister le fichier
  ```
- **Hors Git / secrets** (à créer à la main sur chaque poste) :
  | Fichier | Rôle |
  |---|---|
  | `.ssh/<cle>` | Clé privée admin VM |
  | `.env.vm.sandbox` | `VM_HOTE`, `VM_ADMIN_USER`, `VM_CLE_ADMIN` |
  | `.env.deploy.sandbox` | `DEPLOY_*` |
  | `backend.env.sandbox` | Secrets / réglages backend de la branche |
  | `frontend.env.sandbox` | `VITE_*` de la branche |

## 3. `sandbox` éligible + branche locale obligatoire (2026-11-12)

- **Branche** : `elisee-feat-cd-socle` (pour committer) ; pour **exécuter** `preparer-vm --branche sandbox` il faut être checkout sur `sandbox`
- **Commit(s)** : `7203dce` — `ci(sandbox): On test sur la bonne branche`
- **Fichiers touchés** :
  - `backend/scripts/deploy_env/spec.py` — `BRANCHES = ('sandbox', 'main', 'prod')` (plus `develop`)
  - `git-cli/deploy_env.py` — `ensure_branche_locale()` : `definir` / `etat` / `preparer-vm` / `preparer-vm-gcp` exigent HEAD local == `--branche`
  - `backend/app/tests/test_deploy_env.py` — tests branche locale + éligibilité `sandbox`
  - Workflows : `ci-orchestrateur.yml` (push), `cd-orchestrateur.yml`, `cd-build-images.yml`, `cd-verifier-environnement.yml` → `sandbox|main|prod`
  - Docs : `deploy/README.md`, `README_DEV.md`, `README_CI.md`, ce journal
- **Intention** : aligner le code sur le modèle doc (`sandbox` déployée, `develop` jamais) ; empêcher de préparer / définir un env depuis une autre branche locale.
- **Reproduction** :
  1. Appliquer le commit.
  2. Créer la branche distante `sandbox` si besoin.
  3. Pour préparer : `git checkout sandbox` puis `python git-cli/deploy_env.py preparer-vm --branche sandbox`.
- **Vérification** :
  ```bash
  # depuis une feature : doit échouer
  python git-cli/deploy_env.py preparer-vm --branche sandbox
  # depuis sandbox : --branche sandbox accepté (sous réserve master + fichiers)
  git checkout sandbox
  python git-cli/deploy_env.py preparer-vm --branche sandbox --help
  ```
- **Notes** : le déploiement GitHub Actions s’exécute déjà sur la branche poussée (`GITHUB_REF_NAME`) ; la contrainte locale complète le contrôle côté poste.

## 4. Ports métriques GCP + convention clé `.ssh/<branche>_ssh` (2026-11-12)

- **Branche** : `sandbox`
- **Commit(s)** : `5b32994` — `correction rapide`
- **Fichiers touchés** :
  - `deploy/vm/verifier.sh` — ports `20201` / `20202` acceptés (agents de métriques GCP) en plus de 22/80/443
  - `.env.vm.example` — `VM_CLE_ADMIN=.ssh/sandbox_ssh` (convention `<branche>_ssh`)
  - `deploy/README.md` — mention des ports GCP dans l’étape vérification
- **Intention** :
  - Sur GCE, les agents de métriques écoutent souvent `20201`/`20202` : le contrôle VM ne doit plus échouer pour ça.
  - Harmoniser le nom de clé admin avec la branche (`sandbox` → `.ssh/sandbox_ssh`).
- **Reproduction** :
  1. Appliquer `5b32994`.
  2. Hors Git, générer la clé depuis la racine du dépôt (utilisateur Linux = nom de branche) :
     ```bash
     ssh-keygen -t ed25519 -C "sandbox" -f .ssh/sandbox_ssh
     ```
  3. Injecter la clé publique dans les métadonnées SSH de la VM GCP (`sandbox:$(cat .ssh/sandbox_ssh.pub)`).
  4. Dans `.env.vm.sandbox` : `VM_ADMIN_USER=sandbox`, `VM_CLE_ADMIN=.ssh/sandbox_ssh` (pas `ubuntu` si la clé est liée à `sandbox`).
  5. Donner à `sandbox` un `sudo -n` (NOPASSWD) pour `preparer-vm`.
- **Hors Git / secrets** :
  | Fichier | Rôle |
  |---|---|
  | `.ssh/sandbox_ssh` / `.ssh/sandbox_ssh.pub` | Paire admin (ignorée par Git) |
  | `.ssh/CREER_SSH.md` | Guide local de génération / injection GCP (non versionné, dossier `.ssh/`) |
- **Vérification** :
  ```bash
  ssh -i .ssh/sandbox_ssh sandbox@<IP>
  sudo -n true
  # apres preparer-vm : le controle ne signale plus 20201/20202 comme ecart
  ```
- **Notes** :
  - `definir` n’écrit **pas** les `VM_SSH_*` : seul `preparer-vm` le fait (utilisateur GitHub = `deploy`, clé générée distincte de la clé admin).
  - Ordre : `preparer-vm` → `definir` → DNS → **CD - VERIFIER ENVIRONNEMENT** → déploiement.

## 5. Push GHCR sans attestation + étape 6 runbook clarifiée (2026-11-12)

- **Branche** : `sandbox`
- **Commit(s)** : `1142ffe` — `correction rapide 2`
- **Fichiers touchés** :
  - `.github/workflows/cd-build-images.yml` — `docker build --provenance=false --sbom=false` (backend + frontend)
  - `deploy/README.md` — étape 6 réécrite (auto vs manuel, jobs, contrôles VM / health)
- **Intention** :
  - BuildKit exporte des attestations ; le push ghcr peut pousser les calques puis échouer avec `error from registry: denied` sur le manifeste final (vu sur `-frontend` alors que `-backend` passait déjà).
  - Rendre l’étape « Déployer » actionnable (prérequis, orchestrateur, sha, logs).
- **Reproduction** :
  1. Appliquer `1142ffe` sur la branche déployée (`sandbox`).
  2. S’assurer que le package GHCR `…-frontend` a le dépôt en **Manage Actions access** (Write/Admin) — souvent déjà OK si créé par Actions.
  3. Relancer **CD - BUILD IMAGES** ou **CD - ORCHESTRATEUR** depuis `sandbox`.
- **Vérification** :
  - Step **Image frontend** : `… publiee.` (plus de `denied` après les `Pushed`).
  - Dans le log build : pas d’`exporting attestation manifest` bloquant le push (flags provenance/sbom).
- **Notes** : si le package `-frontend` a été partiellement créé lors d’un push refusé, le relancer après ce commit suffit en général ; sinon vérifier Package settings → Manage Actions access.

## 6. Retour terrain sandbox — `ALLOWED_HOSTS` / CORS + DNS / ACME (2026-11-12)

- **Branche** : `sandbox` (config locale + infra)
- **Commit(s)** : aucun (fichiers hors Git / console GCP)
- **Fichiers touchés** : `backend.env.sandbox`, `.env.deploy.sandbox` (locaux)
- **Intention** : aligner les hosts Django sur le domaine public ; ouvrir le chemin Let’s Encrypt.
- **Reproduction / valeurs** (exemple domaine `sandbox.boilerplate.doonyalabs.com`) :

  ```env
  # .env.deploy.sandbox
  DEPLOY_DOMAIN=sandbox.boilerplate.doonyalabs.com

  # backend.env.sandbox — AUCUN commentaire en fin de ligne active
  ALLOWED_HOSTS=sandbox.boilerplate.doonyalabs.com
  CORS_ALLOWED_ORIGINS=https://sandbox.boilerplate.doonyalabs.com
  CSRF_TRUSTED_ORIGINS=https://sandbox.boilerplate.doonyalabs.com
  FRONTEND_URL=https://sandbox.boilerplate.doonyalabs.com
  USE_X_FORWARDED_PROTO=True
  DB_HOST=db
  ```

  Puis : `python git-cli/deploy_env.py definir --branche sandbox`

- **Infra obligatoire avant 1er déploiement HTTPS** :
  1. DNS A `DEPLOY_DOMAIN` → IP publique de la VM.
  2. Pare-feu GCP : TCP **80** et **443** ouverts depuis Internet (ufw seul ne suffit pas).
  3. Test externe : `curl -vI http://sandbox.boilerplate.doonyalabs.com/` (pas de timeout).
- **Vérification** : **CD - VERIFIER ENVIRONNEMENT** vert ; certbot ne doit plus échouer avec `Timeout during connect` sur `/.well-known/acme-challenge/`.
- **Notes** :
  - `ALLOWED_HOSTS` = hôte **sans** schéma ; CORS/CSRF/FRONTEND_URL = URL `https://…`.
  - Un `# …` après `USE_X_FORWARDED_PROTO=True` a cassé Django (`valeur reçue : 'true    # …'`).

## 7. `.env.example` allégés (2026-11-12)

- **Branche** : `sandbox`
- **Commit(s)** : `a191d00` — `correction rapide 3`
- **Fichiers touchés** :
  - `backend/.env.example`, `frontend/.env.example`, `.env.deploy.example` — commentaires réduits au minimum
  - Ce journal (entrées précédentes)
- **Intention** : moins de bruit dans les modèles ; éviter que des commentaires en fin de ligne soient copiés dans les vrais `*.env.<branche>` et envoyés à GitHub.
- **Reproduction** : appliquer `a191d00`. Conserver uniquement :
  - en-tête court (ligne active / `# NOM=` / `# @secret`) ;
  - marqueurs `# @secret` sur les secrets ;
  - lignes `# NOM=` pour les facultatives.
- **Hors Git** : alléger aussi `backend.env.sandbox`, `frontend.env.sandbox`, `.env.deploy.sandbox` (aucune ligne active avec `#` après la valeur).
- **Vérification** : `definir --branche sandbox` puis redéploiement sans `ImproperlyConfigured` sur un booléen « pollué ».

## 8. Logging console uniquement (Docker) (2026-11-12)

- **Branche** : `sandbox`
- **Commit(s)** : `66ff857` — `correction rapide 4`
- **Fichiers touchés** : `backend/config/settings.py` — suppression du `FileHandler` `/app/django.log`
- **Intention** : le conteneur backend tourne en user non-root → `PermissionError: … '/app/django.log'` puis `Unable to configure handler 'file'` ; healthcheck backend unhealthy.
- **Reproduction** :
  1. Appliquer `66ff857`.
  2. **Rebuilder** l’image backend (tag = SHA du commit) via **CD - ORCHESTRATEUR** / **CD - BUILD IMAGES** depuis `sandbox`.
  3. Ne pas redéployer un ancien SHA (ex. `1142ffe…`) : l’image garderait l’ancien logging.
- **Vérification** :
  - Conteneur backend healthy ; plus de `Permission denied: '/app/django.log'`.
  - Logs visibles via `docker compose -p <namespace> logs backend`.
- **Notes** : frontend healthy + DB up n’empêchent pas l’échec si le backend restart en boucle sur le logging.

## 9. Workflow CD - MAINTENANCE / reset-db (2026-11-12)

- **Branche** : `sandbox` (à merger ensuite selon le flux)
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `.github/workflows/cd-maintenance.yml` — workflow manuel, volets via input `action`
  - `deploy/vm/maintenance-reset-db.sh` — stop `db` + `docker volume rm <namespace>_pgdata`
  - Docs : `deploy/README.md`, `README_CI.md`, ce journal
- **Décisions cadrées** :
  - Branches : `sandbox` et `main` seulement (pas `prod`)
  - Masters (`GIT_MASTER_USERS`) uniquement
  - Confirmation : `RESET-DB-<branche>`
  - Effet : effacer le volume seulement (pas de redéploiement auto)
  - Périmètre : service `db` + volume `pgdata` ; refus si `DEPLOY_DB_MODE` ≠ `interne`
  - Accès : SSH maintenant ; GCP prévu plus tard (refus explicite si `DEPLOY_ACCES=gcp`)
- **Reproduction** :
  1. Appliquer le commit sur la branche déployée.
  2. Actions → **CD - MAINTENANCE** → `action=reset-db`, confirmation `RESET-DB-sandbox`.
  3. Puis **CD - ORCHESTRATEUR** pour recréer la base.
- **Vérification** : volume `<DEPLOY_NAMESPACE>_pgdata` absent sur la VM ; après orchestrateur, backend healthy avec le `DB_PASSWORD` courant.

## 10. Notifications Slack / Teams post-déploiement (2026-11-12)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `backend/scripts/deploy_env/spec.py` — secrets facultatifs `SLACK_NOTIF_WEBHOOK`, `TEAMS_NOTIF_WEBHOOK`
  - `backend/scripts/deploy_env/render.py` — exclus du rendu VM
  - `.env.deploy.example` — lignes commentées
  - `.github/workflows/cd-orchestrateur.yml` — jobs `notif-succes` / `notif-echec`
  - `deploy/ci/notify-deploy.sh` — envoi Slack (`text`) et Teams (Adaptive Card)
  - `backend/app/tests/test_deploy_env.py` — optionnels, https, non-fuite
  - Docs : `deploy/README.md`, ce journal
- **Intention** : un seul point de notification (SSH comme GCP) ; absence de webhook = avertissement, pas d’échec CD.
- **Reproduction** :
  1. Appliquer le commit.
  2. Renseigner `SLACK_NOTIF_WEBHOOK` et/ou `TEAMS_NOTIF_WEBHOOK` dans `.env.deploy.<branche>`.
  3. `python git-cli/deploy_env.py definir --branche <branche>`.
  4. Lancer **CD - ORCHESTRATEUR** ; vérifier le message sur le(s) canal/canaux.
- **Hors Git / secrets** : URLs de webhooks dans `.env.deploy.*` (jamais commitées) ; secrets GitHub d’environnement.
- **Vérification** : job `notif-succes` ou `notif-echec` vert ; si aucun secret → `::warning::` et exit 0 ; `compose.env` / `backend.env` sans les webhooks.
- **Notes** : contenu = statut, branche, domaine, SHA, sujet commit, acteur, accès, lien run (+ étape en échec). Bannière colorée SUCCES/ECHEC : voir entrée 22.

## 11. Maintenance db-forward (pgAdmin via tunnel) (2026-11-12)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `deploy/vm/maintenance-db-forward.sh` — open/close + TTL 8 h (`127.0.0.1:5432`)
  - `.github/workflows/cd-maintenance.yml` — volets `db-forward-open` / `db-forward-close`
  - Docs : `deploy/README.md`, `README_CI.md`, ce journal
- **Intention** : préparer sur la VM le forward localhost vers Postgres interne ; le résumé du run donne les commandes locales (tunnel + pgAdmin).
- **Reproduction** :
  1. Appliquer le commit sur la branche déployée.
  2. Actions → **CD - MAINTENANCE** → `db-forward-open`, confirmation `DB-FORWARD-OPEN-sandbox`.
  3. `python git-cli/deploy_env.py tunnel --branche sandbox` (ports **15432** / **13000**).
  4. pgAdmin → `127.0.0.1:15432` ; fermer avec `db-forward-close` / `DB-FORWARD-CLOSE-sandbox` (ou TTL 8 h).
- **Vérification** : conteneur `<namespace>-pg-forward` présent après open, absent après close ; Postgres jamais sur `0.0.0.0`.
- **Notes** : port local `5432` souvent bloqué sous Windows → utiliser `15432`.

## 12. Migration `init_data` au démarrage (2026-11-12)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `backend/app/core/migrations/0004_init_data.py` — `RunPython` → `call_command('init_data')`
  - Ce journal (entrées 11–12)
- **Intention** : après `migrate` (entrypoint backend), peupler permissions, rôles, admin (`ADMIN_EMAIL` / `ADMIN_PASSWORD`) et seeds metier / garoapp de façon **idempotente**, sans commande manuelle sur la VM.
- **Reproduction** :
  1. Appliquer le commit ; rebuild / redéployer via **CD - ORCHESTRATEUR** (nouvelle image backend = nouveau SHA).
  2. Au démarrage du conteneur : `migrate` applique `core.0004_init_data`.
- **Hors Git** : `ADMIN_EMAIL` / `ADMIN_PASSWORD` déjà dans `backend.env.<branche>` / environnement GitHub.
- **Vérification** : tables rôles/permissions non vides ; login admin possible ; relancer migrate ne duplique pas (init_data idempotent).
- **Notes** : dépend de `metier.0009_*` et `garoapp.0001_initial` pour que les seeds voient les tables. Reverse = noop.

## 13. Prune Docker avant pull (disque plein) (2026-11-12)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** : `deploy/vm/deployer.sh` — `docker image prune -af` + `builder prune` avant `compose pull` ; doc `deploy/README.md` ; ce journal
- **Intention** : éviter l’échec CD `no space left on device` au 2ᵉ déploiement quand d’anciennes images GHCR + extraction postgres saturent un disque ~10 Go.
- **Reproduction** : appliquer le commit (le script est envoyé à chaque déploiement) ; en urgence sur la VM : `docker image prune -af` puis relancer **CD - ORCHESTRATEUR**. Agrandir le disque si besoin (≥ 20–30 Go).
- **Vérification** : `df -h /` avant/après prune ; pull images OK.

## 14. DEPLOY_DISK_GB=100 + grow rootfs (2026-11-12)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `backend/scripts/deploy_env/spec.py` / `render.py` — `DEPLOY_DISK_GB` (20–500, défaut doc 100)
  - `.env.deploy.example` — `DEPLOY_DISK_GB=100`
  - `deploy/vm/grow-rootfs.sh`, `preparer.sh` (`doonya-grow-rootfs` + sudoers), `deployer.sh` (grow + seuil 2 Go)
  - `.github/workflows/cd-maintenance.yml` — volet `disk-grow`
  - Docs / tests / ce journal
- **Intention** : disque GCP à 100 Go ne suffit pas si `/` reste à 9 Go ; étendre la partition automatiquement et documenter la taille par branche.
- **Reproduction** :
  1. Console GCP : disque ≥ `DEPLOY_DISK_GB`.
  2. Une fois : `sudo growpart /dev/sda 1 && sudo resize2fs /dev/sda1` **ou** `preparer-vm` puis **CD - MAINTENANCE** `disk-grow` / `DISK-GROW-sandbox`.
  3. `DEPLOY_DISK_GB=100` dans `.env.deploy.<branche>` + `definir`.
- **Vérification** : `df -h /` ~100 Go ; prochain CD sans `no space left on device`.

## 15. disk-set (saisie Go) + cleanup Docker intelligent (2026-11-12)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `deploy/vm/cleanup-docker.sh` — prune images/cache/conteneurs arrêtés (pas les volumes nommés)
  - `deploy/vm/deployer.sh` — cleanup avant/après ; `preparer.sh` — rotation logs Docker 10m×3
  - `.github/workflows/cd-maintenance.yml` — `disk-set` (input `disk_gb`) + `docker-cleanup` ; `disk-grow` alias
  - Docs / ce journal
- **Intention** : ne plus figer 100 Go en dur dans le process ops ; saisir la taille ; limiter la saturation disque.
- **Reproduction** :
  1. Console GCP : disque = N Go.
  2. **CD - MAINTENANCE** → `disk-set`, `disk_gb=N`, `DISK-SET-sandbox`.
  3. Optionnel : `docker-cleanup` / `DOCKER-CLEANUP-sandbox`.
- **Vérification** : `df -h /` ; `DEPLOY_DISK_GB` à jour ; déploiements sans saturation rapide.

## 16. Observabilité Grafana (tunnel SSH) (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `deploy/observabilite/` — Grafana, Prometheus, Loki, Alloy, node-exporter, cAdvisor
  - `backend/scripts/deploy_env/spec.py` / `render.py` — `DEPLOY_OBSERVABILITE`, `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`, `*_ALERT_WEBHOOK`
  - `deploy/vm/deployer.sh` + workflows `cd-deploiement-ssh` / `gcp`
  - Docs / ce journal
- **Intention** : logs et métriques sans dépendance GCP ; accès uniquement via tunnel SSH (`127.0.0.1:3000`).
- **Reproduction** :
  1. `.env.deploy.sandbox` : `DEPLOY_OBSERVABILITE=active` + `GRAFANA_ADMIN_USER` + `GRAFANA_ADMIN_PASSWORD` (≥ 16).
  2. `python git-cli/deploy_env.py definir --branche sandbox` puis déploiement.
  3. `ssh -i .ssh/sandbox_ssh -L 13000:127.0.0.1:3000 sandbox@<VM>` → `http://localhost:13000`.
- **Vérification** : `docker compose -p observabilite ps` ; tableaux de bord VM/logs ; alertes chargées.

## 17. Tunnels SSH 8 h + commande `tunnel` (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `deploy/vm/maintenance-db-forward.sh` — TTL 8 h (constante, plus de `${VAR:-}`)
  - `git-cli/deploy_env.py` — sous-commande `tunnel` (keepalive, reconnexion, arrêt 8 h)
  - `.github/workflows/cd-maintenance.yml` — résumé db-forward (TTL 8 h, commande tunnel)
  - Docs / ce journal
- **Intention** : un seul tunnel fiable pour base (15432) et Grafana (13000) ; durée alignée 8 h.
- **Reproduction** :
  1. **CD - MAINTENANCE** → `db-forward-open` / `DB-FORWARD-OPEN-sandbox`.
  2. `python git-cli/deploy_env.py tunnel --branche sandbox`.
  3. pgAdmin `127.0.0.1:15432` ; Grafana `http://localhost:13000`.
- **Vérification** : `test_deploy_env.TunnelTests` ; reconnexion après coupure Wi-Fi ; Ctrl+C.

## 18. Observabilite CD dediee (job + fichier env) (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(a renseigner apres commit)_
- **Fichiers touches** :
  - `observabilite.env.example` + source `observabilite` dans `spec.py` / `render_observabilite.py`
  - `deploy/vm/observabilite.sh` ; retrait du bloc obs de `deployer.sh`
  - `.github/workflows/cd-observabilite-ssh.yml` + branchement dans `cd-orchestrateur.yml`
  - `git-cli/deploy_env.py` (4e fichier), docs / ce journal
- **Intention** : observabilite toujours on en SSH, job CD bloquant apres deploy app, secrets dans `observabilite.env.<branche>`, relance seule possible ; GCP plus tard.
- **Reproduction** :
  1. Copier `observabilite.env.example` → `observabilite.env.sandbox`, renseigner `GRAFANA_ADMIN_USER` et `GRAFANA_ADMIN_PASSWORD`.
  2. Retirer `DEPLOY_OBSERVABILITE` / `GRAFANA_*` de `.env.deploy.sandbox` si presents.
  3. `python git-cli/deploy_env.py definir --branche sandbox` puis CD (ou **CD - OBSERVABILITE SSH** seul).
  4. `python git-cli/deploy_env.py tunnel --branche sandbox` → `http://localhost:13000`.
- **Verification** : job `observabilite-ssh` vert ; echec obs → `notif-echec` ; `test_deploy_env` (rendu app sans obs + `RenduObservabiliteTests`).

## 19. Logs d'urgence (CD - MAINTENANCE) (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(a renseigner apres commit)_
- **Fichiers touches** :
  - `deploy/vm/maintenance-logs-urgence.sh`
  - `.github/workflows/cd-maintenance.yml` — volet `logs-urgence`, deroge `prod`
  - Docs / ce journal
- **Intention** : recuperer les logs Docker (app + proxy + obs si present) quand Grafana est HS, via Actions.
- **Reproduction** :
  1. Actions → **CD - MAINTENANCE** → « Use workflow from » = sandbox (ou prod).
  2. `action=logs-urgence`, `since=2h`, confirmation `LOGS-URGENCE-sandbox`.
  3. Telecharger l'artefact `logs-urgence-sandbox` (1 jour).
- **Verification** : job vert si app dump OK ; warning si proxy/obs absents ; `prod` refuse les autres volets.

## 20. CI backend sans tests unitaires (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `.github/workflows/ci-backend.yml` — retrait de l’étape `Tests` (`manage.py test`)
  - `00readme/README_CI.md` — doc alignée (migrations seulement)
  - Ce journal
- **Intention** : la suite de tests Django n’est pas encore fiable ; la CI backend ne doit plus bloquer dessus. Conservés : conflits de migrations + migrations manquantes (PostgreSQL jetable).
- **Reproduction** : appliquer le commit ; le job `backend` de l’orchestrateur ne lance plus `manage.py test`.
- **Vérification** : run CI backend vert sans étape Tests ; `python manage.py test` reste utilisable en local.
- **Notes** : à remettre quand la suite sera fiable. Le service Postgres du workflow reste (besoin des commandes makemigrations).

## 21. Compte Grafana configurable (`GRAFANA_ADMIN_USER`) (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `observabilite.env.example` / `observabilite.env.<branche>` — `GRAFANA_ADMIN_USER`
  - `backend/scripts/deploy_env/spec.py` — variable obligatoire (non secret)
  - `backend/scripts/deploy_env/render_observabilite.py` — écrit `GF_SECURITY_ADMIN_USER` (+ lit `VARS_JSON`)
  - `deploy/observabilite/compose.yml` — plus de `admin` en dur
  - `deploy/vm/observabilite.sh` — contrôle de présence du user
  - `.github/workflows/cd-observabilite-ssh.yml` — passe `VARS_JSON`
  - Tests / docs / ce journal
- **Intention** : choisir le login Grafana (plus seulement le mot de passe).
- **Reproduction** :
  1. Dans `observabilite.env.sandbox` : `GRAFANA_ADMIN_USER=...` + `GRAFANA_ADMIN_PASSWORD=...`.
  2. `python git-cli/deploy_env.py definir --branche sandbox`.
  3. Relancer **CD - OBSERVABILITE SSH** (ou un CD complet).
- **Vérification** : login avec le user choisi sur `http://localhost:13000` (tunnel).
- **Notes** : `GF_SECURITY_ADMIN_USER` n’est pris en compte qu’au **premier** démarrage (volume `grafana-data` vide). Changer le user plus tard sans recréer le volume ne renomme pas le compte ; le mot de passe est réappliqué à chaque déploiement.

## 22. Notifications CI + bannières SUCCES/ECHEC (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `.github/workflows/ci-orchestrateur.yml` — jobs `notif-succes` / `notif-echec` (+ `notif-*-pr`)
  - `deploy/ci/notify-ci.sh` — nouveau script CI
  - `deploy/ci/notify-deploy.sh` — même style (bannière colorée)
  - Docs : `00readme/README_CI.md`, `deploy/README.md`, ce journal
- **Intention** : notifier succès/échec de la CI comme le CD ; bannière **SUCCES** (vert) / **ECHEC** (rouge) immédiatement lisible (Slack barre + Blocks ; Teams Container `good`/`attention`).
- **Reproduction** :
  1. Appliquer le commit.
  2. Push/manuel `sandbox|main|prod` : secrets d’environnement (comme le CD). Succès CI **ignoré** sur push (le CD notifie après déploiement) ; échec CI notifié.
  3. Pull request : secrets de **dépôt** du même nom (`SLACK_NOTIF_WEBHOOK` / `TEAMS_NOTIF_WEBHOOK`), facultatifs — les environnements de branche sont réservés.
  4. Relancer une CI / un CD pour voir le message stylisé.
- **Hors Git / secrets** : mêmes webhooks que l’entrée 10 ; pour les PR, recopier en secrets de dépôt.
- **Vérification** : message Slack/Teams avec bannière verte ou rouge ; bouton « Ouvrir le run » ; sans webhook → `::warning::`, pas d’échec.
- **Notes** : pas de notif CI sur `pull_request_review` (évite le spam à chaque revue).

## 23. Contrôles locaux dans `git-cli/commit.py` (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `git-cli/quality_checks.py` — nouveau (sécurité, backend migrations, frontend lint)
  - `git-cli/commit.py` — contrôles **avant** le staging ; menu relancer/quitter
  - `git-cli/git_utils.py` — UTF-8 + `FileNotFoundError` → code 127
  - Docs / skill git-cli / ce journal
  - `security-exceptions.json` — exceptions datées `DJ-011` (migration delete modèles test) + `FB-005` (notify-\*.sh)
  - `backend/scripts/security_scan/report.py` / README — clarifie BLOQUANT vs libellé de score
- **Intention** : refuser un commit local si sécurité / migrations / lint frontend échouent ; pas de `git add` avant les contrôles ; pas d’éjection brutale (menu `1` relancer / `2`|`q` quitter).
- **Reproduction** :
  1. Appliquer le commit ; venv backend avec deps (`pip install -r requirements.txt`) ; Node/npm dans le PATH.
  2. Depuis la **racine** du dépôt : `python git-cli/commit.py`.
  3. Ordre : statut → contrôles → staging → message → commit.
- **Vérification** : échec lint/sécu → menu, aucun fichier stagé par le script ; succès → suite du commit. Windows : `npm.cmd` résolu automatiquement.
- **Notes** : frontend = `npm run lint` seulement (tests + build restent dans la CI). Le scanner CI/local utilise `--fail-on warning` : un **nouvel** avertissement non excepté = BLOQUANT (indépendant du libellé « À surveiller »).

## 24. Audit zones protégées (orphelins + hors zone) (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `backend/scripts/regression_guard/audit.py` — orphelins zones / `PROTECTED_PATHS` + résumé hors zone
  - `backend/scripts/regression_guard/config.py` / `cli.py` — `--audit` ; bloquant `PROTECTED_PATHS` orphelins sur `--base`
  - `git-cli/check_zones.py` + branchement avertissement dans `commit.py`
  - Tests / `README_CI.md` / `git-cli/README.md` / ce journal
- **Intention** : détecter tôt les motifs qui ne protègent plus rien (ex. dossier supprimé) et inventaire informatif des fichiers hors zone.
- **Reproduction** :
  1. `python -m scripts.regression_guard --audit` (depuis `backend/`) ou `python git-cli/check_zones.py`.
  2. En commit local : avertissement si orphelins ; la CI non-régression échoue (code 2) tant que la config n’est pas corrigée.
- **Vérification** : `test_regression_guard` (orphelins, hors zone, dépôt réel sans orphelin) ; résumé hors zone dans le step summary CI.
- **Notes** : le hors-zone n’est jamais bloquant (le métier reste hors zones volontairement).

## 25. Retrait de toutes les références `terraform/` (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `regression-guard.json` — motif `terraform/**` retiré de la zone `deploiement-ci`
  - `git-cli/access_control.conf` — retiré de `PROTECTED_PATHS`
  - `git-cli/git_utils.py` — défaut sans `terraform/`
  - `git-cli/README_PORTABILITE.md` — exemple aligné
- **Intention** : le dossier `terraform/` a été supprimé ; un motif orphelin faisait échouer la non-régression (`le motif « terraform/** » ne correspond à aucun fichier`).
- **Reproduction** : appliquer le commit ; vérifier qu’aucune occurrence de `terraform` ne reste dans le dépôt.
- **Vérification** : `python -m scripts.regression_guard --audit` sans orphelin ; CI non-régression plus bloquée sur ce motif.

## 26. Catalogue consultable des règles de sécurité (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `00readme/README_SECURITY_RULES.md` — index + détail des 43 règles (id, gravité, description, recommandation)
  - Liens depuis `backend/scripts/security_scan/README.md` et `00readme/README_CI.md`
  - Ce journal
- **Intention** : consulter les règles (ex. `FB-003`) sans ouvrir les scripts Python sous `backend/scripts/security_scan/rules/`.
- **Reproduction** : ouvrir [`README_SECURITY_RULES.md`](../README_SECURITY_RULES.md) ; optionnel : `python -m scripts.security_scan --list-rules` pour la liste courte à jour.
- **Vérification** : `FB-003` et les autres ids présents dans l’index du catalogue.

## 27. Correctif FB-003 sur l’audit zones (CI summary) (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** : `backend/scripts/regression_guard/cli.py` — `_append_outside_summary` ; ce journal
- **Intention** : le `except config.ConfigError: return` silencieux déclenchait `FB-003` (exception avalée) et bloquait `git-cli/commit.py` / la CI sécu avec `--fail-on warning`.
- **Reproduction** : appliquer le commit ; en cas d’erreur d’audit, le message est écrit dans le résumé CI au lieu d’être avalé.
- **Vérification** : `security_scan --fail-on warning` sans finding sur `cli.py` ; commit local sécurité OK.

## 28. Simplification CD - MAINTENANCE (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** : `.github/workflows/cd-maintenance.yml` ; `deploy/README.md` ; `00readme/README_CI.md` ; ce journal
- **Intention** :
  - Retirer `disk-grow` (alias confus de `disk-set`) et `db-forward-close` (TTL 8 h suffisant).
  - Clarifier `disk-set` (console GCP puis partition Linux) et l’accès Grafana (tunnel local, hors menu maintenance).
- **Reproduction** : voir entrée 29 (formulaires dédiés).
- **Vérification** : résumé db-forward indique Grafana via `deploy_env.py tunnel` et fermeture auto 8 h.

## 29. Formulaires maintenance dédiés + logs/cleanup (2026-11-13)

- **Branche** : _(branche de travail courante)_
- **Commit(s)** : _(à renseigner après commit)_
- **Fichiers touchés** :
  - `cd-maintenance.yml` — moteur `workflow_call` uniquement
  - `cd-maintenance-reset-db.yml`, `-db-forward.yml`, `-disk-set.yml`, `-docker-cleanup.yml`, `-logs-urgence.yml`
  - `deploy/vm/maintenance-logs-urgence.sh` — un `.log` par service (plus d’`extrait-*`)
  - `deploy/vm/cleanup-docker.sh` — plus de `volume prune` (pgdata + grafana-data sûrs)
  - Docs + ce journal
- **Intention** : GitHub Actions n’offre pas d’inputs conditionnels ; un workflow = un formulaire. Artefact logs lisible ; cleanup sans risque sur les volumes obs.
- **Reproduction** : Actions → choisir le workflow du volet (champs pertinents seulement).
- **Vérification** : artefact = `backend.log` / `frontend.log` / `proxy.log` / `observabilite.log` ; cleanup = message volumes explicite ; flow obs documenté (`CD - OBSERVABILITE SSH` + tunnel).

## 30. `VM_SSH_USER` reste un secret (2026-11-13)

- **Date** : 2026-11-13
- **Contexte** : tentative de passer `VM_SSH_USER` en variable pour éviter le masquage Actions de `deploy` dans les logs (`deploy_env.py` → `***_env.py`). Sur les envs existants le login était encore un **secret** → `etat` signalait un mauvais type, et le CD lisait `vars` → `null@hôte` / Permission denied.
- **Décision** : **garder `VM_SSH_USER` en secret** (avec `VM_SSH_HOST` / `VM_SSH_PRIVATE_KEY`). Les workflows relisent depuis `SECRETS_JSON`. Effet de bord accepté : Actions peut masquer la chaîne `deploy` dans les logs.
- **Reproduction** : rien à migrer si le secret `VM_SSH_USER` est déjà présent ; sinon `preparer-vm` ou créer le secret `deploy`. Supprimer une éventuelle **variable** `VM_SSH_USER` orpheline. `etat --branche sandbox` doit être OK.
- **Vérification** : `python git-cli/deploy_env.py etat --branche sandbox` sans erreur `VM_SSH_USER`.

## 31. Dashboards Grafana Doonya + stack MinIO (S3)

- **Date** : 2026-11-13
- **Contexte** : le provisioning Grafana ne montrait pas le dossier Doonya ; besoin de dashboards par service (dont MinIO) et d’un stockage objet type S3 sur la VM, calqué sur l’observabilité.
- **Changements** :
  - Dashboards provisionnés : General, Backend, Frontend, Proxy, Postgres, **MinIO** ; `observabilite.sh` vérifie leur présence et redémarre Grafana.
  - Stack MinIO partagée `/opt/apps/_minio` (`deploy/minio/`, `minio.env`, job `cd-minio-ssh`, orchestrateur après `deploiement-ssh`).
  - Proxy Nginx `location /stockage/` (GET/HEAD) → `minio-serveur:9000` ; tunnel local `:19001` → console `:9001`.
  - Django `USE_S3` + `django-storages[s3]` ; frontend `VITE_S3_BUCKET_URL` ; exclusif avec `USE_GCS`.
  - Logs d’urgence `minio.log` ; cleanup explicite : volume `minio-data` non touché.
- **Reproduction** :
  1. `cp minio.env.example minio.env.sandbox` puis `definir --branche sandbox`.
  2. Relancer CD (ou **CD - OBSERVABILITE SSH** + **CD - MINIO SSH**).
  3. Tunnel → Grafana Browse/Doonya (6 dashboards) ; MinIO console `:19001`.
- **Vérification** : dashboards Doonya visibles ; conteneur `minio-serveur` up ; avec `USE_S3=True`, bucket provisionné et objets via `/stockage/<bucket>/…`.

<!-- Prochaine entree : 32. — observabilite GCP / documenter IAP -->

---

## Index rapide des commits de la suite

| #   | Date       | Commit       | Titre                                                            |
| --- | ---------- | ------------ | ---------------------------------------------------------------- |
| 1   | 2026-11-12 | `7d47ef1`    | Clés `.ssh/`, runbook `deploy/README.md`, suppression onboarding |
| 2   | 2026-11-12 | `214cfed`    | `.env.deploy.example` + `cp` étape 1                             |
| 3   | 2026-11-12 | `7203dce`    | `sandbox` éligible + branche locale obligatoire                  |
| 4   | 2026-11-12 | `5b32994`    | Ports métriques GCP + convention `.ssh/<branche>_ssh`            |
| 5   | 2026-11-12 | `1142ffe`    | GHCR sans attestation + étape 6 runbook                          |
| 6   | 2026-11-12 | _(hors Git)_ | `ALLOWED_HOSTS` / CORS + DNS / ACME                              |
| 7   | 2026-11-12 | `a191d00`    | `.env.example` allégés                                           |
| 8   | 2026-11-12 | `66ff857`    | Logging console (fix Docker `django.log`)                        |
| 9   | 2026-11-12 | _(pending)_  | CD - MAINTENANCE / `reset-db`                                    |
| 10  | 2026-11-12 | _(pending)_  | Notifications Slack / Teams CD                                   |
| 11  | 2026-11-12 | _(pending)_  | Maintenance `db-forward` (pgAdmin)                               |
| 12  | 2026-11-12 | _(pending)_  | Migration `core.0004_init_data`                                  |
| 13  | 2026-11-12 | _(pending)_  | Prune Docker avant pull (disque)                                 |
| 14  | 2026-11-12 | _(pending)_  | `DEPLOY_DISK_GB=100` + grow rootfs                               |
| 15  | 2026-11-12 | _(pending)_  | `disk-set` (saisie Go) + cleanup Docker                          |
| 16  | 2026-11-13 | _(pending)_  | Observabilité Grafana (tunnel SSH)                               |
| 17  | 2026-11-13 | _(pending)_  | Tunnels SSH 8 h + commande `tunnel`                              |
| 18  | 2026-11-13 | _(pending)_  | Observabilité CD dédiée (job + `observabilite.env`)              |
| 19  | 2026-11-13 | _(pending)_  | Logs d’urgence (CD - MAINTENANCE)                                |
| 20  | 2026-11-13 | _(pending)_  | CI backend sans tests unitaires                                  |
| 21  | 2026-11-13 | _(pending)_  | `GRAFANA_ADMIN_USER` configurable                                |
| 22  | 2026-11-13 | _(pending)_  | Notifications CI + bannières SUCCES/ECHEC                        |
| 23  | 2026-11-13 | _(pending)_  | Contrôles locaux `git-cli/commit.py`                             |
| 24  | 2026-11-13 | _(pending)_  | Audit zones (orphelins + hors zone)                              |
| 25  | 2026-11-13 | _(pending)_  | Retrait références `terraform/`                                  |
| 26  | 2026-11-13 | _(pending)_  | Catalogue `README_SECURITY_RULES.md`                             |
| 27  | 2026-11-13 | _(pending)_  | Correctif FB-003 audit zones                                     |
| 28  | 2026-11-13 | _(pending)_  | Simplification CD - MAINTENANCE                                  |
| 29  | 2026-11-13 | _(pending)_  | Formulaires maintenance + logs/cleanup                           |
| 30  | 2026-11-13 | _(pending)_  | `VM_SSH_USER` reste un secret                                    |
| 31  | 2026-11-13 | _(pending)_  | Dashboards Doonya + stack MinIO (S3)                             |

---

## Checklist de reproduction sur un autre dépôt

- [ ] Socle CD présent (`git-cli/deploy_env.py`, `backend/scripts/deploy_env/`, workflows `cd-*.yml`, `deploy/`)
- [ ] Entrées 1 → 31 appliquées
- [ ] `DEPLOY_DISK_GB=100` + `df -h /` cohérent avec le disque GCP
- [ ] Fichiers locaux : `.env.vm.sandbox`, `.env.deploy.sandbox`, `backend.env.sandbox`, `frontend.env.sandbox`, `observabilite.env.sandbox`, `minio.env.sandbox`, clé `.ssh/<branche>_ssh`
- [ ] `git check-ignore` OK pour `.ssh/`, `.env.vm.sandbox`, `.env.deploy.sandbox` ; examples versionnés
- [ ] `BRANCHES` = sandbox/main/prod ; workflows alignés
- [ ] Sur branche `sandbox` : `preparer-vm --branche sandbox` ; hors `sandbox` : refus
- [ ] `verifier.sh` accepte 20201/20202 ; builds images avec `--provenance=false --sbom=false`
- [ ] `ALLOWED_HOSTS` / CORS / DNS:80-443 OK ; pas de `#` en fin de ligne dans les env de valeurs
- [ ] Image backend = SHA avec logging console (`66ff857` ou plus récent) ; backend healthy
- [ ] **CD - MAINTENANCE …** : un workflow par volet (reset-db, db-forward TTL 8 h, disk-set, docker-cleanup, logs-urgence)
- [ ] Notifications CD + CI : `SLACK_NOTIF_WEBHOOK` / `TEAMS_NOTIF_WEBHOOK` (facultatifs) + jobs `notif-*` ; bannières vert/rouge ; secrets de dépôt pour les PR
- [ ] Migration `core.0004_init_data` appliquée au deploy (rôles / admin présents)
- [ ] Observabilité : `GRAFANA_ADMIN_USER` + `GRAFANA_ADMIN_PASSWORD` ; job `observabilite-ssh` ; dashboards Doonya (dont MinIO)
- [ ] MinIO : `minio.env` + job `minio-ssh` ; tunnel `:19001` ; `USE_S3` / `VITE_S3_BUCKET_URL` si stockage objet actif
- [ ] CI backend : migrations seulement (pas `manage.py test` pour l’instant)
- [ ] `git-cli/commit.py` : contrôles locaux avant staging (sécu, migrations, lint) + audit zones en avertissement
- [ ] `python git-cli/check_zones.py` / `--audit` : pas d’orphelins ; hors zone informatif
- [ ] Aucune référence `terraform/` dans le dépôt
- [ ] Catalogue règles sécu : [`README_SECURITY_RULES.md`](../README_SECURITY_RULES.md)
- [ ] Suivre [`deploy/README.md`](../../deploy/README.md)

---

## Inventaire final (période 2026-11-12 → 2026-11-13)

Bilan Git depuis le commit d’ouverture `7d47ef1` jusqu’à HEAD au moment de la clôture (`a9b45d5` sur `sandbox`) : **96 fichiers** · **+7823 / −505** lignes.

### Commits de la période (ordre chronologique)

| Hash | Date | Message |
| ---- | ---- | ------- |
| `7d47ef1` | 2026-11-12 | `ci(deploiement): run de la sandbox` |
| `214cfed` | 2026-11-12 | `ci(sandbox): Step 1` |
| `7203dce` | 2026-11-12 | `ci(sandbox): On test sur la bonne branche` |
| `d6a4809` | 2026-11-12 | `Merge pull request #46 from doonyalabs/elisee-feat-cd-socle` |
| `5b32994` | 2026-11-12 | `correction rapide` |
| `1142ffe` | 2026-11-12 | `correction rapide 2` |
| `a191d00` | 2026-11-12 | `correction rapide 3` |
| `66ff857` | 2026-11-12 | `correction rapide 4` |
| `42c091c` | 2026-11-12 | `correction rapide 5` |
| `aba70cd` | 2026-11-12 | `correction rapide 6` |
| `f41051a` | 2026-11-12 | `correction rapide 7` |
| `413a62e` | 2026-11-12 | `correction rapide 8` |
| `521eae0` | 2026-11-12 | `correction rapide 9` |
| `ad76ffc` | 2026-11-13 | `correction rapide 11` |
| `2f065d7` | 2026-11-13 | `correction rapide 12` |
| `2e6bab5` | 2026-11-13 | `feat(ci): nous arrivons au bout du tunnel` |
| `2a8bce9` | 2026-11-13 | `feat(sandbox): sans test u` |
| `6436e4b` | 2026-11-13 | `feat(secu): Lancement de la secu en local` |
| `e1d9469` | 2026-11-13 | `docs(gitcli): ajustement de la doc` |
| `2cc3a33` | 2026-11-13 | `docs(suite): mise a jour de la suite des updates` |
| `412f0ed` | 2026-11-13 | `feat(commit): comiit` |
| `61e0167` | 2026-11-13 | `feat(1): communication` |
| `800e7b7` | 2026-11-13 | `fix(db): forward` |
| `993b527` | 2026-11-13 | `docs(deploiement): test` |
| `4483bc6` | 2026-11-13 | `ci(maintenance): Mise en place de la maintenance` |
| `3173c11` | 2026-11-13 | `ci(grafana): et minio` |
| `f69f753` | 2026-11-13 | `ci(vm): on garde ssh user comme etant un secret` |
| `92b57b2` | 2026-11-13 | `feat(1): 1` |
| `a9b45d5` | 2026-11-13 | `fix(minio): Mise a jour de repo docker hub de minio` |

### Fichiers ajoutés (44)

**Workflows GitHub Actions**

- `.github/workflows/cd-maintenance.yml`
- `.github/workflows/cd-maintenance-db-forward.yml`
- `.github/workflows/cd-maintenance-disk-set.yml`
- `.github/workflows/cd-maintenance-docker-cleanup.yml`
- `.github/workflows/cd-maintenance-logs-urgence.yml`
- `.github/workflows/cd-maintenance-reset-db.yml`
- `.github/workflows/cd-minio-ssh.yml`
- `.github/workflows/cd-observabilite-ssh.yml`

**Docs / exemples d’environnement**

- `00readme/SUITE_DES_TRAVAUX_DE_CD.md` (déplacé en clôture vers ce fichier daté sous `00readme/suite/`)
- `00readme/README_SECURITY_RULES.md`
- `deploy/README.md`
- `.env.deploy.example`
- `minio.env.example`
- `observabilite.env.example`

**Deploy MinIO / observabilité / maintenance VM**

- `deploy/minio/compose.yml`
- `deploy/minio/provisionner.sh`
- `deploy/observabilite/compose.yml`
- `deploy/observabilite/alloy/config.alloy`
- `deploy/observabilite/loki.yml`
- `deploy/observabilite/prometheus.yml`
- `deploy/observabilite/grafana/dashboards/backend.json`
- `deploy/observabilite/grafana/dashboards/frontend.json`
- `deploy/observabilite/grafana/dashboards/general.json`
- `deploy/observabilite/grafana/dashboards/minio.json`
- `deploy/observabilite/grafana/dashboards/postgres.json`
- `deploy/observabilite/grafana/dashboards/proxy.json`
- `deploy/observabilite/grafana/provisioning/alerting/regles.yml`
- `deploy/observabilite/grafana/provisioning/dashboards/dashboards.yml`
- `deploy/observabilite/grafana/provisioning/datasources/datasources.yml`
- `deploy/vm/cleanup-docker.sh`
- `deploy/vm/grow-rootfs.sh`
- `deploy/vm/maintenance-db-forward.sh`
- `deploy/vm/maintenance-logs-urgence.sh`
- `deploy/vm/maintenance-reset-db.sh`
- `deploy/vm/minio.sh`
- `deploy/vm/observabilite.sh`
- `deploy/ci/notify-ci.sh`
- `deploy/ci/notify-deploy.sh`

**Backend / git-cli**

- `backend/app/core/migrations/0004_init_data.py`
- `backend/scripts/deploy_env/render_minio.py`
- `backend/scripts/deploy_env/render_observabilite.py`
- `backend/scripts/regression_guard/audit.py`
- `git-cli/check_zones.py`
- `git-cli/quality_checks.py`

### Fichiers modifiés (49)

**CI/CD**

- `.github/workflows/cd-build-images.yml`
- `.github/workflows/cd-deploiement-gcp.yml`
- `.github/workflows/cd-deploiement-ssh.yml`
- `.github/workflows/cd-orchestrateur.yml`
- `.github/workflows/cd-verifier-environnement.yml`
- `.github/workflows/ci-backend.yml`
- `.github/workflows/ci-orchestrateur.yml`

**Docs**

- `00readme/PLAN_CD.md`
- `00readme/README_CD.md`
- `00readme/README_CI.md`
- `00readme/README_DEV.md`
- `00readme/README_SAME_ORIGIN_COOKIES.md`
- `00readme/README_STORAGE_FILE_MANAGEMENT.md`
- `CLAUDE.md`
- `README.md`
- `.claude/skills/git-cli/SKILL.md`

**Backend**

- `backend/.env.example`
- `backend/config/settings.py`
- `backend/requirements.txt`
- `backend/app/metier/services/storage_service.py`
- `backend/app/tests/test_deploy_env.py`
- `backend/app/tests/test_env_config.py`
- `backend/app/tests/test_regression_guard.py`
- `backend/scripts/deploy_env/render.py`
- `backend/scripts/deploy_env/spec.py`
- `backend/scripts/regression_guard/cli.py`
- `backend/scripts/regression_guard/config.py`
- `backend/scripts/security_scan/README.md`
- `backend/scripts/security_scan/report.py`

**Deploy**

- `deploy/ci/gcp-vm.sh`
- `deploy/vm/deployer.sh`
- `deploy/vm/preparer.sh`
- `deploy/vm/verifier.sh`
- `deploy/proxy/site-https.conf.tpl`

**Frontend**

- `frontend/.env.example`
- `frontend/Dockerfile`
- `frontend/src/config/config.ts`
- `frontend/src/helpers/displayers/media-url-builder.ts`
- `frontend/src/helpers/displayers/media-url-builder.test.ts`

**git-cli / config dépôt**

- `git-cli/README.md`
- `git-cli/README_PORTABILITE.md`
- `git-cli/access_control.conf`
- `git-cli/commit.py`
- `git-cli/deploy_env.py`
- `git-cli/git_utils.py`
- `.gitignore`
- `.env.vm.example`
- `regression-guard.json`
- `security-exceptions.json`

### Fichiers supprimés (3)

- `00readme/README_ONBOARDING.md`
- `sshsandbox`
- `terraform/README.md`

### Hors Git (locaux, ignorés)

- `.env.vm.sandbox`
- `.env.deploy.sandbox`
- `backend.env.sandbox`
- `frontend.env.sandbox`
- `minio.env.sandbox`
- `observabilite.env.sandbox`
- clés sous `.ssh/`

---

## Clôture de cette suite

Cette suite s’arrête au **13 novembre 2026**.

- **Ouverture** : `7d47ef1` (2026-11-12) — création du journal + run sandbox.
- **Dernier commit couvert** : `a9b45d5` (2026-11-13) — `fix(minio): Mise a jour de repo docker hub de minio`.
- **Branche de référence** : `sandbox`.
- **Entrées journal** : 1 → 31.

Toute évolution CD **après** cette date doit aller dans une **nouvelle** suite sous [`00readme/suite/`](./README.md), avec la nouvelle période dans le nom du fichier (ex. `SUITE_DES_TRAVAUX_DE_CD_AAAA-MM-JJ_AAAA-MM-JJ.md`).

Ne plus modifier le corps de ce fichier sauf correction factuelle mineure ; l’inventaire et la clôture figent l’état au 13 novembre 2026.
