# Git CLI

Scripts Python qui imposent le workflow Git du projet. Les `git commit` / `git push` directs sont bloqués par les hooks.

## Prérequis

- Python 3.10+
- Git
- GitHub CLI `gh` (pour `pr.py`)

## Installation des hooks

Depuis la racine du dépôt :

```bash
python git-cli/install-hooks.py
```

Configure `core.hooksPath=.githooks` (hooks `commit-msg` et `pre-push`).

Restrictions et chemins protégés : [`access_control.conf`](access_control.conf)
(`GIT_MASTER_EMAILS`, `GIT_MASTER_USERS`, `IDENTITY_RESTRICTED_BRANCHES`, `PROTECTED_PATHS`).

## Commandes principales

```bash
python git-cli/commit.py
python git-cli/push.py
python git-cli/pr.py
python git-cli/pull.py
python git-cli/rebase.py
python git-cli/merge.py --from feature/ma-feature
python git-cli/doctor.py
python git-cli/check_zones.py
```

Chaque commande propose un mode interactif (sortie rapide `q`) et un `--dry-run`.

## Flux de branches

- Features → `develop` → `main` → `prod`
- PR vers `main` : uniquement depuis `develop`
- PR vers `prod` : uniquement depuis `main`
- Titre de PR : `pr-<type>(<scope>): <titre>`

## Règles (condensé)

**Commit** — `commit.py` ajoute le trailer `X-Git-CLI: doonya-git-cli/2.0` ; le hook refuse les commits sans ce trailer. Les `PROTECTED_PATHS` sont réservés aux masters (`GIT_MASTER_EMAILS`). Ordre : contrôles locaux (sécurité, migrations backend, lint frontend) → audit zones (avertissement si motifs orphelins / hors zone) → staging → message. Échec des contrôles qualité = pas de `git add`. L’audit zones ne bloque pas le commit local (la CI non-régression bloque les orphelins). Les tests / le build frontend restent dans la CI.

**Zones** — `check_zones.py` lance `python -m scripts.regression_guard --audit` : motifs orphelins dans `regression-guard.json` / `PROTECTED_PATHS`, et résumé des fichiers hors zone.

**Push** — `push.py` positionne `DOONYA_GITCLI_PUSH=1` ; le hook refuse un `git push` direct. Le build frontend est vérifié par la CI, pas au push. Sur `main` / `develop` / `prod`, identité master requise.

**PR** — à lancer depuis la branche source ; marqueur `<!-- X-Git-CLI-PR: … -->` dans le body ; synchronisation de la branche avant création ; blocage s'il n'y a aucun commit à merger.

**Pull** — `pull.py` fait un `git pull --rebase` strict sur la branche courante (refuse les changements locaux non commités ou non poussés).

**Rebase** — `rebase.py` rebase sur `origin/develop` par défaut (`--onto`, `--continue`, `--abort`, `--skip`).

**Merge** — `merge.py --from <branche>` merge vers `develop` ; assistant de conflits intégré (`--continue` / `--abort`). Mode PR : `--sync-pr-head --base develop`.

## CI

Workflows `.github/workflows/git-cli-enforce-*.yml` : contrôle des trailers, chemins protégés, acteurs masters et flux de branches sur push/PR.

Sans rulesets GitHub (mode Free) : les scripts exigent localement `core.hooksPath=.githooks` ; la CI reste informative/contrôlante. En Team/Enterprise, rendre les checks bloquants via branch protection.

## Liens

- Portabilité vers un autre dépôt : [`README_PORTABILITE.md`](README_PORTABILITE.md)
- README racine : [`../README.md`](../README.md)
