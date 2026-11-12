---
name: git-cli
description: Utiliser les scripts git-cli/ du projet (commit, push, pull, rebase, merge, pr, doctor) à la place de git commit/push, qui sont bloqués par les hooks. À utiliser dès que l'utilisateur demande de commiter, pousser, ouvrir une PR, tirer, rebaser ou merger, ou quand un git commit/push est refusé par un hook, même s'il ne cite pas git-cli.
---

# git-cli : commiter, pousser, ouvrir une PR sans gaspiller de tokens

`git commit` et `git push` directs sont bloqués par les hooks (`.githooks/`) et la CI. Tout passe par `python git-cli/<script>.py` depuis la racine du dépôt. Les scripts sont **interactifs** (menus numérotés) : on les pilote en leur envoyant les réponses sur stdin, sans jamais les ouvrir ni les relire.

## Règles d'économie

- Ne pas lire le code de `git-cli/` ni les README : tout ce qu'il faut est ci-dessous.
- Un seul `git status --short` avant de commiter (utile pour choisir le staging), puis aller droit au script. Pas de `git log`/`git diff` superflus.
- Enchaîner les commandes dépendantes dans un seul appel Bash. Lire seulement la fin de la sortie (`| tail -15`) : les bannières et menus ne servent à rien.
- Ne jamais lancer `--help` : les options utiles sont listées plus bas.
- Aucune action distante (`push`, `pr`) sans demande explicite de l'utilisateur. Commiter localement ne demande pas de confirmation si l'utilisateur l'a demandé.

## Commit : `commit.py`

Ordre des questions (envoyer les réponses une par ligne avec `printf`) :

1. **Staging**, seulement s'il existe des fichiers non stagés : `1` = tout ajouter, `2` = choisir (puis numéros `1,3`), `3` = rien. Pour un commit ciblé, stager avant avec `git add <fichiers>` (autorisé) : la question n'apparaît alors que pour le reste, répondre `3`.
2. **Type** (numéro) : 1 feat, 2 fix, 3 docs, 4 style, 5 refactor, 6 perf, 7 test, 8 chore, 9 ci, 10 revert.
3. **Scope** : un mot (`auth`, `securite`, `ci`, `git`…).
4. **Description** : 100 caractères max, sans point final, en français, sans accents inutiles (le projet n'en met pas dans les messages).
5. **Confirmer** : `o`.

```bash
# 3 = ne rien ajouter au staging (déjà stagé) ; 2 = fix ; o = confirmer
printf '3\n2\nauth\ncorrection du refresh du cookie\no\n' | python git-cli/commit.py | tail -8
# Si tout est à ajouter : première réponse 1 au lieu de 3
```

Si rien n'est non stagé, la question 1 n'est pas posée : retirer la première ligne. En cas de doute, `--dry-run` (simule sans committer). Un message de commit se limite à `type(scope): description` ; le trailer `X-Git-CLI` est ajouté par le script.

## Push : `push.py`

```bash
printf 'o\n' | python git-cli/push.py | tail -10
```

Le script demande une confirmation finale (`o`) : sans elle il plante avec `EOFError` (stdin vide).

Contrôle la branche et l'identité. Pas de build du frontend : c'est la CI qui le fait. Option : `--branch <nom>`, `--dry-run`. Ne pousse pas sur `main`, `develop` ni `prod` sans droits (voir `git-cli/access_control.conf`).

## Pull request : `pr.py`

Flux de branches : features → `develop` → `main` → `prod`. PR vers `main` uniquement depuis `develop`, vers `prod` uniquement depuis `main`. Impossible de faire une PR depuis une branche protégée.

Questions dans l'ordre : confirmation éventuelle de pousser la branche (`o`), branche cible (`1` = cible par défaut, `develop` pour une feature), type de PR (mêmes numéros que les commits), scope, titre (sans préfixe ; le titre final est `pr-<type>(<scope>): <titre>`, 100 caractères au total), description multiligne terminée par une ligne contenant seulement `.`.

```bash
# (poussée o si la branche n'est pas sur origin), cible 1, type 3 (docs), scope ci, titre,
# description, point final, puis o = confirmation finale de création
printf '1\n3\nci\ncontrole de non-regression\nResume de la PR\n.\no\n' | python git-cli/pr.py | tail -10
```

La dernière réponse `o` (« Confirmer la création de la pull request ») est obligatoire. Pour une description longue, écrire les réponses dans un fichier du scratchpad et le passer avec `< fichier`.

Si la branche est déjà poussée et à jour, la question de poussée n'apparaît pas : adapter. Options : `--base <branche>` (saute la question de la cible), `--draft`, `--dry-run`. Terminer la description par la ligne d'attribution demandée par l'environnement s'il y en a une.

## Autres scripts (sans question en général)

| Besoin | Commande |
|---|---|
| Mettre à jour la branche courante (working tree propre, rien à pousser) | `python git-cli/pull.py` |
| Rebaser sur `origin/develop` | `python git-cli/rebase.py` (`--onto`, `--continue`, `--abort`, `--skip`) |
| Merger une feature dans `develop` | `python git-cli/merge.py --from <branche>` (`--continue`, `--abort`) |
| Resynchroniser la branche d'une PR avec sa base | `python git-cli/merge.py --sync-pr-head --base develop` |
| Diagnostiquer l'installation | `python git-cli/doctor.py` |
| Installer les hooks (une fois) | `python git-cli/install-hooks.py` |

## Quand ça échoue

- Un hook refuse un `git commit`/`git push` : relancer par le script correspondant, ne jamais contourner avec `--no-verify`.
- « Aucun fichier stagé » : stager d'abord (réponse `1` ou `git add`).
- « Fichier protégé » : le script exige une identité listée dans `GIT_MASTER_USERS`/`GIT_MASTER_EMAILS` (`access_control.conf`). Le dire à l'utilisateur au lieu de forcer.
- Les réponses sont décalées (menu inattendu) : relancer avec `--dry-run` et afficher la sortie complète une fois, puis corriger la séquence.
- Les fichiers de zones protégées (`regression-guard.json`) peuvent être commités ; la CI les signalera à la PR, c'est normal.
