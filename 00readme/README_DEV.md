# Coder avec devstreet : règles du CD

Pour les développeurs. Mise en place de la VM et des environnements : [`README_ONBOARDING.md`](./README_ONBOARDING.md) et [`README_CD.md`](./README_CD.md).

## Principe

Trois branches sont déployées, chacune sur son propre environnement.

| Branche   | Environnement | Déployée |
| --------- | ------------- | -------- |
| `sandbox` | sandbox       | oui      |
| `main`    | staging       | oui      |
| `prod`    | production    | oui      |
| `develop` | aucun         | jamais   |

Un push ou un merge vers `sandbox`, `main` ou `prod` lance la CI. Si elle est verte, la branche est construite puis déployée sur sa VM. Un merge dans `develop` ou une PR ne déploie jamais.

```text
ta branche → PR → develop            (intégration, jamais déployée)
develop → PR → sandbox               (déploie sandbox)
develop → PR → main → PR → prod      (déploie staging, puis production)
```

## 1. Installation (une fois)

```bash
python git-cli/install-hooks.py
python git-cli/doctor.py
```

`git commit` et `git push` directs sont bloqués : tout passe par `git-cli/`.

## 2. Cycle de travail

```bash
git checkout develop
python git-cli/pull.py
git checkout -b <prenom>-feat-<sujet>
# ... code ...
python git-cli/commit.py     # Conventional Commits, en français
python git-cli/push.py
python git-cli/pr.py         # cible develop, titre : pr-<type>(<scope>): <titre>
```

Promotion, depuis `develop` : `python git-cli/pr.py --base sandbox` ou `--base main`. Vers la production : `--base prod` depuis `main`. Aucune autre voie n'est acceptée.

## 3. Avant de pousser

Depuis `backend/`, venv active :

```bash
python manage.py test
python manage.py makemigrations --check --dry-run
python -m scripts.security_scan --fail-on warning
python -m scripts.regression_guard --base origin/develop
```

Depuis `frontend/` : `npm run lint` et `npm test`.

La PR ne peut être mergée que si `backend`, `frontend`, `securite` et `non-regression` sont verts.

## 4. Règles qui touchent le déploiement

**Variables d'environnement**

- Toute nouvelle variable s'ajoute dans `backend/.env.example` ou `frontend/.env.example`. Ces fichiers sont la liste de référence du déploiement.
- Ligne active (`NOM=`) : obligatoire. Ligne commentée (`# NOM=`) : facultative. `# @secret` en fin de ligne : stockée comme secret GitHub.
- Aucune valeur de repli dans le code : Django refuse de démarrer si une variable manque.
- Les `VITE_*` sont publiques (intégrées au JavaScript) : jamais de secret.
- Une variable obligatoire ajoutée doit être créée dans l'environnement GitHub de chaque branche **avant** de merger, sinon le déploiement échoue. Demander à un master de lancer `python git-cli/deploy_env.py definir --branche <branche>`.

**Migrations**

- Elles s'appliquent au démarrage du conteneur et ne sont jamais annulées par un retour arrière.
- Une migration déjà mergée ne se modifie pas : en créer une nouvelle.
- Deux migrations de même base se fusionnent avec `python manage.py makemigrations --merge`.
- Garder la version précédente du code compatible avec le schéma (ajouter avant de supprimer).

**Santé**

- `/api/health` doit répondre 200 : le déploiement vérifie cette URL et `/`.
- En production : `DEBUG=False` et `ENABLE_API_DOCS=False`.

**Fichiers sensibles**

- Une zone protégée touchée (`regression-guard.json`) demande l'approbation d'un responsable de zone sur le dernier commit.
- Les workflows, `.githooks/` et `git-cli/` sont réservés aux masters.
- Ne jamais retirer une zone, une règle du scanner ni une règle de branche pour faire passer une PR.

## 5. Les workflows sur GitHub

Ils sont dans `.github/workflows/` et se suivent dans l'onglet **Actions**.

```text
pull request ─► CI - ORCHESTRATEUR ─► backend, frontend, securite, non-regression

push sandbox / main / prod ─► CI - ORCHESTRATEUR ─► (CI verte) ─► CD - ORCHESTRATEUR
                                                                   ├─► CD - BUILD IMAGES
                                                                   └─► CD - DEPLOIEMENT SSH ou GCP
```

| Workflow                           | Rôle                                                                                | Se lance                                      |
| ---------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------- |
| `CI - ORCHESTRATEUR`               | Appelle les quatre contrôles ci-dessous, puis le CD sur un push de branche déployée | PR, revue de PR, push `develop`/`main`/`prod` |
| `CI - BACKEND`                     | Conflits de migrations, migrations manquantes, tests Django                         | par l'orchestrateur                           |
| `CI - FRONTEND`                    | Lint, tests, build de production                                                    | par l'orchestrateur                           |
| `CI - SECURITE`                    | Scanner de sécurité                                                                 | par l'orchestrateur                           |
| `CI - NON-REGRESSION`              | Signale les zones protégées touchées, bloque jusqu'à l'approbation d'un responsable | par l'orchestrateur                           |
| `CD - ORCHESTRATEUR`               | Construit les images puis déploie la branche                                        | CI verte sur un push, ou manuel (masters)     |
| `CD - BUILD IMAGES`                | Publie les images backend et frontend du commit sur `ghcr.io`                       | par le CD, ou manuel (masters)                |
| `CD - DEPLOIEMENT SSH` / `GCP`     | Déploie sur la VM selon `DEPLOY_ACCES`                                              | par le CD                                     |
| `CD - VERIFIER ENVIRONNEMENT`      | Contrôle en lecture seule : variables, secrets, DNS, SSH, ports                     | manuel                                        |
| `GIT-CLI - ENFORCEMENT` (pr, push) | Flux de branches, trailer `X-Git-CLI` des commits, auteurs autorisés                | PR et push                                    |

À savoir :

- Les quatre contrôles de la CI sont obligatoires pour merger.
- Une CI rouge ne déploie rien. Une PR ne déploie jamais.
- Un workflow manuel s'exécute sur la branche choisie dans « Use workflow from » : c'est elle qui donne accès à l'environnement GitHub du même nom (`develop`, `main`, `prod`).
- Si un push plus récent arrive pendant la CI, le commit plus ancien n'est pas déployé.
- Si `GIT-CLI - ENFORCEMENT` échoue, un commit ou une PR n'est pas passé par `git-cli/`, ou le flux de branches n'est pas respecté.

## 6. Après le merge

- Suivre le run `CI - ORCHESTRATEUR` dans Actions : le job `deploiement` suit la CI.
- Contrôler `https://<domaine>/api/health`.
- Un déploiement plus ancien est remplacé par le plus récent. Il y a une coupure brève à chaque déploiement.

## 7. Relance et retour arrière (masters)

Actions > **CD - ORCHESTRATEUR** > Run workflow > branche à déployer + commit complet (40 caractères). Vérifier d'abord que l'ancienne version reste compatible avec la base.

## Interdits

- `git commit` / `git push` directs.
- Pousser un secret, un `.env`, `backend.env.*`, `frontend.env.*`, `.env.deploy.*` ou `.env.vm.*`.
- Créer un workflow qui déclare `environment: prod` hors de la branche `prod`.
- Merger avec une CI rouge.
