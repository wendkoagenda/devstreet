# Plan du déploiement (CD)

Décisions prises le 2026-10-22, révisées le 2026-10-23 (environnements GitHub). Les workflows de déploiement s'appellent `cd-*.yml` ; ceux qui valident une pull request restent `ci-*.yml` (voir [`README_CI.md`](./README_CI.md)). Le contrat du reverse proxy est décrit dans [`README_SAME_ORIGIN_COOKIES.md`](./README_SAME_ORIGIN_COOKIES.md) §3.2.

## Décisions

| Sujet | Décision |
|---|---|
| Namespace | Une instance déployée de l'application (ex. `devstreet-develop`) : projet Docker Compose (`-p`), conteneurs, réseau et volumes propres, dossier `/opt/apps/<namespace>/` |
| Environnements | Un **environnement GitHub** par branche déployée, du même nom : `develop`, `main`, `prod`, **réservé à cette seule branche** (règle « Deployment branches and tags »). Chaque branche peut viser une VM différente |
| Variables et secrets | Dans l'environnement de la branche, sous leur nom simple (`SECRET_KEY`, `VM_SSH_HOST`…), sans valeur partagée entre branches ni au niveau du dépôt. GitHub fait foi ; modifiables par `deploy_env.py` ou dans l'interface GitHub |
| Liste de référence | `backend/.env.example` et `frontend/.env.example` : ligne active = obligatoire, `# NOM=` = facultative, marqueur `# @secret` = secret GitHub (sinon variable). Seuls les noms listés sont transmis aux conteneurs |
| Définir les valeurs | Script local `git-cli/deploy_env.py`, réservé aux `GIT_MASTER_USERS` : crée l'environnement et sa règle de branche, puis écrit les valeurs. Pas un workflow : les champs d'un lancement manuel ne sont pas masqués, et le jeton d'un workflow ne peut pas créer d'environnement (il faudrait stocker un jeton administrateur) |
| Préparer la VM | `deploy_env.py --preparer-vm`, Ubuntu LTS uniquement : Docker, utilisateur `deploy`, clé SSH dédiée, empreinte épinglée (`VM_SSH_KNOWN_HOSTS`), `ufw` (22, 80, 443), SSH par clé seule, `fail2ban`, mises à jour de sécurité |
| Vérifier | Workflow manuel `cd-verifier-environnement.yml`, sans aucune valeur saisie : variables et secrets présents, SSH, empreinte, DNS, ports ouverts |
| Images | Construites sur GitHub, publiées sur `ghcr.io`, taguées par SHA : `<repo>-backend:<sha>` et `<repo>-frontend:<branche>-<sha>-<empreinte des VITE_*>` (ces valeurs sont figées à la construction). Un tag existant n'est pas reconstruit. Le commit doit appartenir à l'historique de la branche |
| Base de données | PostgreSQL 16 dans le namespace par défaut (réseau interne, aucun port publié). `DEPLOY_DB_MODE=externe` la retire. Sauvegardes : hors périmètre pour l'instant |
| Reverse proxy | nginx et certbot en conteneurs, un proxy partagé par VM (`/opt/apps/_proxy/`), réseau Docker `proxy`, un fichier par namespace généré depuis `DEPLOY_DOMAIN`. Seul le proxy publie des ports |
| Certificats | Validation HTTP-01 par webroot ; premier déploiement en deux temps (HTTP seul, `certbot certonly`, puis HTTPS) ; renouvellement par un conteneur `certbot` en boucle (`DEPLOY_LETSENCRYPT_EMAIL`) |
| `/static` et `/media` | Servis par le proxy depuis `/srv/public/<namespace>/` (monté en lecture seule), avec `Content-Disposition: attachment` et `nosniff` sur `/media` |
| Santé | Route `/api/health` (200 si la base répond, 503 sinon, sans détail), vérifications de santé Docker, contrôle de bout en bout depuis le runner |
| Retour arrière | Manuel seulement (relance avec un SHA) : les migrations déjà appliquées peuvent rendre l'ancienne image incompatible |
| Déclenchement | Automatique uniquement sur un push ou un merge vers `develop`, `main` ou `prod` : le job `deploiement` de `ci-orchestrateur` appelle `cd-orchestrateur` une fois la CI verte, sur la branche poussée (seule à avoir accès à son environnement). Un commit qui n'est plus la pointe de la branche n'est pas déployé. Manuel : « Use workflow from » = la branche, SHA facultatif, réservé aux `GIT_MASTER_USERS` |
| Transport | `DEPLOY_ACCES` : `ssh` (IP publique et clé privée) ou `gcp` (IAP, sans IP publique, sans clé). Les scripts exécutés sur la VM sont communs aux deux |

## Limites assumées

- **L'isolation repose sur la règle de branche de chaque environnement** et sur la protection des branches `develop`, `main` et `prod` : si la règle est retirée dans l'interface, ou si quelqu'un peut pousser sans revue sur une de ces branches, les secrets de son environnement deviennent lisibles. `deploy_env.py etat` contrôle la règle. Atténuation complémentaire : `deploy/`, `git-cli/deploy_env.py` et `cd-*.yml` dans la zone protégée `deploiement-ci` et dans `PROTECTED_PATHS`.
- **Aucune sauvegarde** de la base dans un conteneur.
- **Courte coupure** à chaque déploiement (remplacement des conteneurs, migrations au démarrage).
- **`deploy` vaut presque `root`** : appartenir au groupe `docker` le permet.
- **SSH ouvert à tous** sur la VM : les adresses des runners GitHub changent, le filtrage par origine est impossible. Protection : clé seule et `fail2ban`. Le mode GCP sans IP publique supprime ce port.

## Phases

Chaque phase est livrable seule.

1. **Socle applicatif** : route `/api/health`, marqueurs dans les `.env.example`, contrat du proxy étendu (README), ce plan. *(fait)*
2. **Configuration** : `git-cli/deploy_env.py` (`definir`, `etat`, `preparer-vm`) et `cd-verifier-environnement.yml`, guide dans [`README_CD.md`](./README_CD.md). *(écrit, à valider sur une VM de test)*
3. **Images** : `cd-build-images.yml` et publication sur GHCR. *(écrit, à valider par un premier lancement manuel)*
4. **Déploiement** : scripts `deploy/` (modèle Compose, nginx, certbot), `cd-deploiement-ssh.yml` et `cd-orchestrateur.yml`. *(écrit, à valider sur une VM de test ; voir [`README_CD.md`](./README_CD.md) §6)*
5. **Mode GCP sans IP publique** : `cd-deploiement-gcp.yml` (IAP, Workload Identity Federation), `deploy/ci/gcp-vm.sh`, `preparer-vm-gcp` et valeurs `GCP_*`, guide dans [`README_CD.md`](./README_CD.md) §7. *(écrit, à valider ; suppose la configuration IAM décrite au §7)*

## Notes

- Le constructeur d'URL des médias ([`media-url-builder.ts`](../frontend/src/helpers/displayers/media-url-builder.ts)) déduit déjà l'origine de `VITE_API_URL` : avec des chemins relatifs, les fichiers `/media/` sont servis sur le même domaine. Aucune correction nécessaire.
- `STATIC_ROOT` et `MEDIA_ROOT` restent sous `BASE_DIR` (`/app/staticfiles` et `/app/media` dans l'image) : le Compose y monte `/srv/public/<namespace>/static` et `/media`, sans modifier `settings.py`. Le dossier appartient à l'uid 10001 (utilisateur de l'image), fixé par `deployer.sh` à chaque déploiement.
- Un seul conteneur backend écrit dans `/media` ; une mise à l'échelle sur plusieurs VM demandera `USE_GCS=True`.
