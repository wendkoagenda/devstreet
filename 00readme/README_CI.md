# Intégration continue (GitHub Actions)

La CI est découpée en workflows par sujet, que l'on peut lancer seuls (Actions > le workflow > Run workflow). Le workflow `ci-orchestrateur` les appelle sur chaque pull request et chaque push vers `develop`, `main` et `prod`.

| Workflow | Rôle | Déclenché par |
|---|---|---|
| `ci-orchestrateur` | Appelle `ci-backend`, `ci-frontend`, `ci-securite` et `ci-non-regression` ; sur un push vers `develop`/`main`/`prod`, appelle ensuite `cd-orchestrateur` si tout est vert | pull request, revue de pull request, push `develop`/`main`/`prod`, manuel (sans la non-régression) |
| `ci-backend` | Conflits de migrations, migrations manquantes, tests Django | orchestrateur, manuel |
| `ci-frontend` | Lint, tests vitest, build de production | orchestrateur, manuel |
| `ci-securite` | Scanner de sécurité | orchestrateur, manuel |
| `ci-non-regression` | Signale les zones protégées touchées et bloque jusqu'à la validation d'un responsable | orchestrateur, manuel (comparaison de deux références) |
| `cd-verifier-environnement` | Contrôle en lecture seule d'un environnement de déploiement (variables, secrets, DNS, SSH, ports). Voir [`README_CD.md`](./README_CD.md) | manuel (depuis la branche à vérifier) |
| `cd-build-images` | Construit et publie les images backend et frontend d'un commit sur `ghcr.io`. Voir [`README_CD.md`](./README_CD.md) | manuel (masters, depuis la branche à construire), `cd-orchestrateur` |
| `cd-orchestrateur` | Déploie une branche après une CI verte sur un push (images puis déploiement), avec l'environnement GitHub de la branche. Voir [`README_CD.md`](./README_CD.md) | job `deploiement` de `ci-orchestrateur` sur un push `develop`/`main`/`prod`, manuel (masters, depuis la branche à déployer) |
| `cd-deploiement-ssh` | Envoie la configuration et exécute le déploiement sur la VM par SSH | `cd-orchestrateur` |
| `cd-deploiement-gcp` | Même déploiement par le tunnel IAP de GCP, sans IP publique ni clé (Workload Identity Federation) | `cd-orchestrateur` |
| `git-cli-enforce-*` | Règles `git-cli` (flux de branches, trailer des commits, chemins protégés) | existants, inchangés |

Les actions GitHub sont épinglées par empreinte de commit (SHA), pas par étiquette de version. Les secrets de test (base, clés Django, mot de passe admin) sont générés à chaque exécution : aucun secret réel n'est utilisé.

## Contrôles à rendre obligatoires

À régler une fois dans GitHub : Settings > Branches (ou Rulesets) > règle pour `develop`, `main` et `prod` > « Require status checks to pass before merging ». Après la **première** exécution sur une PR, les contrôles apparaissent dans la liste de recherche ; choisir ceux-ci (le nom exact s'affiche dans la PR) :

- `backend` (appelé depuis `ci-orchestrateur`)
- `frontend`
- `securite` (le job `scanner`)
- `non-regression`

Un contrôle ne peut être choisi qu'après s'être exécuté au moins une fois dans le dépôt.

## Backend

- **Conflit de migrations** : `makemigrations --merge --dry-run` doit répondre « No conflicts detected to merge. » Sinon, deux migrations partent de la même base : lancer `python manage.py makemigrations --merge` en local et commiter la migration de fusion.
- **Migration manquante** : `makemigrations --check --dry-run` échoue si un modèle a changé sans migration.
- **Tests** : toute la suite `manage.py test`, sur PostgreSQL 16 jetable. Pas de mesure de couverture côté backend pour l'instant (jugée peu fiable).

## Frontend

`npm run lint`, `npm test` puis `npm run build` avec `VITE_API_URL=/api` et `VITE_API_V1_URL=/api/v1`. Les composants shadcn générés (`src/components/ui`, `use-toast.ts`) sont exclus de deux règles ESLint, dans `eslint.config.js` : tout le reste du code est lint-bloquant.

## Scanner de sécurité

- **Scanner** : `python -m scripts.security_scan --fail-on warning` (voir `backend/scripts/security_scan/README.md`). Exceptions datées dans `security-exceptions.json`.
- **Audit des dépendances** : retiré de la CI pour le moment (ni sur les pull requests, ni en planifié) ; il sera traité plus tard. L'outil `backend/scripts/dependency_audit` et `dependency-audit-exceptions.json` restent dans le dépôt. La règle `SUP-001` du scanner (aucune analyse des dépendances) est donc couverte par deux exceptions datées dans `security-exceptions.json` : à retirer quand l'audit reviendra.

En local, depuis `backend/` :

```powershell
pip-audit -r requirements.txt --format json -o pip-audit.json
cd ..rontend; npm audit --omit=dev --json > ..
pm-audit.json; cd ..ackend
python -m scripts.dependency_audit --pip pip-audit.json --npm ..
pm-audit.json
```

## Non-régression

`regression-guard.json` (racine) décrit des **zones protégées**. Modifier un fichier d'une zone n'est jamais interdit : le contrôle le **signale** et demande la validation d'un super responsable.

Chaque zone a :

| Champ | Rôle |
|---|---|
| `name` | Nom court en minuscules et tirets |
| `reason` | Pourquoi la zone est sensible (affiché dans le commentaire) |
| `paths` | Motifs de chemins : `*` reste dans un dossier, `**` traverse les dossiers, un `/` final désigne un dossier entier |
| `tests` | Tests qui couvrent la zone. Un test modifié ne déclenche pas la zone ; un test **supprimé** la déclenche. Si le code change sans qu'aucun de ces tests change, le commentaire le signale |
| `verify` | Consigne de vérification affichée dans le commentaire |
| `owners` | Facultatif : responsables ajoutés à ceux de `ZONE_PROTEGEE_USERS` |

Les responsables par défaut viennent de `ZONE_PROTEGEE_USERS` dans `git-cli/access_control.conf` (distinct de `GIT_MASTER_USERS`, qui règle qui peut pousser et merger sur les branches protégées). Un motif qui ne correspond à aucun fichier est refusé (une zone qui protège le vide serait trompeuse).

**Sur une pull request**, le workflow pose un commentaire unique (mis à jour à chaque push), le label `zone-protegee`, et **échoue** tant que :
- l'auteur de la PR n'est pas dans `ZONE_PROTEGEE_USERS`, ou
- aucun utilisateur de `ZONE_PROTEGEE_USERS` n'a approuvé la PR **sur son dernier commit** (un nouveau push annule l'approbation ; l'orchestrateur se relance à chaque revue).

Les règles et l'outil sont lus sur la **branche cible** : une PR ne peut pas réécrire `regression-guard.json` pour se rendre invisible (sauf à la toute première introduction de l'outil). Les PR venant d'un fork n'ont pas de commentaire ni de label (droits en lecture seule), mais le contrôle échoue de la même façon.

**Sur un push** vers `develop`, `main` ou `prod`, et en lancement manuel (comparer par exemple `main` et `prod` avant une mise en production), le résultat va dans le résumé du job sans bloquer : le changement est déjà intégré.

En local, avant de pousser :

```powershell
cd backend
python -m scripts.regression_guard --base origin/develop
python -m scripts.regression_guard --base origin/develop --format markdown   # texte du commentaire
```

Code de sortie : `0` aucune zone touchée, `1` au moins une, `2` configuration invalide.

## Ne pas confondre avec `git-cli`

`PROTECTED_PATHS` dans `git-cli/access_control.conf` limite **qui** peut modifier certains chemins (workflows, hooks, `git-cli`). La non-régression signale **que** des fichiers sensibles ont changé, pour tout le monde, y compris les super responsables.

## Ce que la CI ne fait pas encore

- Aucune mesure de couverture des tests (backend et frontend), jugée peu fiable pour l'instant.
- Aucun audit des dépendances (pip-audit, npm audit) : prévu plus tard, hors des pull requests.
- Aucune construction d'image Docker pendant les pull requests : les images sont construites au déploiement (`cd-build-images`).
