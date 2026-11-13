# Git CLI - Portabilite vers un autre projet

Ce guide explique comment reutiliser `git-cli` dans un autre depot Git, avec le comportement actuel.

## 1) Copier les fichiers dans le nouveau repo

Depuis ce projet, copier dans la racine du nouveau projet:

- `git-cli/`
- `.githooks/`
- (optionnel mais recommande) `.github/workflows/git-cli-*.yml`

Structure attendue dans le nouveau repo:

```text
<nouveau-repo>/
  git-cli/
  .githooks/
  .github/workflows/   # si vous activez aussi la validation CI
```

## 2) Prerequis a installer sur la machine

- Python 3.10+
- Git
- GitHub CLI `gh` (pour `pr.py`)

## 3) Initialiser les hooks dans le nouveau repo

Depuis la racine du nouveau repo:

```powershell
python git-cli/install-hooks.py
```

Ce script configure:

- `core.hooksPath=.githooks`
- hook `commit-msg`
- hook `pre-push`

## 4) Configurer les regles d'acces

Adapter `git-cli/access_control.conf` selon le nouveau projet:

- `GIT_MASTER_EMAILS`
- `GIT_MASTER_USERS`
- `IDENTITY_RESTRICTED_BRANCHES`
- `PROTECTED_PATHS`

Exemple:

```dotenv
GIT_MASTER_EMAILS="lead@company.com,devops@company.com"
GIT_MASTER_USERS="lead-user,devops-user"
IDENTITY_RESTRICTED_BRANCHES="main,develop,prod"
PROTECTED_PATHS=".github/workflows/,.githooks/,git-cli/"
```

## 5) Verifier l'identite Git locale

Dans le nouveau repo, verifier:

```powershell
git config user.name
git config user.email
```

L'email local doit etre coherent avec `GIT_MASTER_EMAILS` pour certaines operations sensibles.

## 6) Workflow de branches impose actuellement

Tel quel, `pr.py` applique ces regles:

- `develop -> main` uniquement
- `main -> prod` uniquement
- autres branches: cible par defaut `develop`

Si le nouveau projet n'utilise pas ce flux, il faudra adapter `git-cli/pr.py`.

## 7) Build frontend

`push.py` et le hook `pre-push` ne lancent plus de build frontend : il est verifie par la CI
(`.github/workflows/ci-frontend.yml`) sur chaque pull request. Rien a configurer dans git-cli pour un projet
sans frontend. Pour garder une verification locale, lancer `npm run build` dans `frontend/` avant de pousser.

## 8) Commandes de verification rapide

Depuis la racine du nouveau repo:

```powershell
python git-cli/doctor.py
python git-cli/commit.py --dry-run
python git-cli/push.py --dry-run
python git-cli/pr.py --dry-run
```

## 9) Checklist finale

- [ ] `git-cli/` copie dans le nouveau repo
- [ ] `.githooks/` copie dans le nouveau repo
- [ ] `python git-cli/install-hooks.py` execute
- [ ] `git-cli/access_control.conf` adapte
- [ ] `gh auth status` OK
- [ ] workflow branches compatible (`develop -> main -> prod`)
- [ ] `python git-cli/doctor.py` OK
