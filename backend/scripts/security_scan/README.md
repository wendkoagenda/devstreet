# Scanner de sécurité

Outil déterministe : mêmes fichiers, mêmes règles, même résultat. Il lit le dépôt (backend, frontend, Docker, CI), applique 43 règles à identifiants stables et calcule un score de 0 à 100. Il ne modifie rien et n'appelle aucun service externe.

## Utilisation

Depuis `backend/` :

```powershell
python -m scripts.security_scan                          # scan complet, rapport texte
python -m scripts.security_scan --fail-on warning        # mode de la CI : bloque dès un avertissement
python -m scripts.security_scan --changed-since origin/develop   # seulement les fichiers modifiés (mode PR)
python -m scripts.security_scan --format markdown --output rapport.md
python -m scripts.security_scan --list-rules             # catalogue des règles
```

`--fail-on` (`critical`, `error`, `warning`, `never`) fixe la gravité minimale d'un problème **non traité** qui rend le scan bloquant. Par défaut : `error`. La CI utilise `warning`.

Code de sortie : `0` rien de bloquant, `1` bloquant, `2` configuration invalide (fichier d'exceptions illisible, par exemple).

## Score

| Gravité | Points perdus par problème |
|---|---|
| critique | 20 |
| erreur | 10 |
| avertissement | 3 |
| info | 0 |

Une même règle retire au plus 3 fois son malus (une cause répétée dans dix fichiers n'écrase pas le score). États : **Sain** (90 et plus), **À surveiller** (75), **Risque élevé** (50), **Bloquant** (en dessous).

## Les règles

`python -m scripts.security_scan --list-rules` donne la liste à jour. Familles : `SEC` (secrets), `DJ` (Django), `PY` (Python), `FE` (frontend), `DOCKER`, `DEP` (dépendances), `CFG` (configuration), `FB` (replis silencieux : valeur par défaut d'une variable, erreur avalée), `RT` (routes et throttling), `API` (versionnement, sérialiseurs, détail d'erreur), `SUP` (chaîne d'approvisionnement). Les secrets trouvés sont masqués dans les rapports.

## Exceptions datées

Un risque accepté s'écrit dans `security-exceptions.json` (racine du dépôt). Il n'existe pas d'exception permanente.

```json
{
  "exceptions": [
    {
      "rule": "DJ-005",
      "path": "backend/app/core/views/auth_views.py",
      "reason": "Routes d'authentification : elles servent à obtenir une session, donc ne peuvent pas l'exiger.",
      "author": "wendkoagenda",
      "expires": "2027-04-01"
    }
  ]
}
```

- `rule` : identifiant existant. `path` : **un fichier précis** (ni joker ni dossier). `line` est facultatif.
- `reason` : 15 caractères minimum. `author` obligatoire.
- `expires` : `AAAA-MM-JJ`, **180 jours maximum** dans le futur.
- Une exception expirée ne protège plus rien : le problème redevient actif et le scan est signalé.
- Une exception qui ne correspond plus à aucun problème est signalée comme inutilisée : à retirer.
- Une entrée invalide arrête le scan (code 2) : jamais d'exception « molle ».

Toute modification de ce fichier est signalée par le contrôle de non-régression (zone `scanner-securite`).

## Baseline (dette connue)

`--update-baseline` enregistre l'état actuel comme dette connue dans un fichier de baseline, et les scans suivants ne bloquent que sur les **nouveaux** problèmes. Ce dépôt n'en utilise pas : tout problème est à corriger ou à excepter. `--no-baseline` ignore la baseline.

## Ajouter une règle

1. Dans `rules/<famille>_rules.py`, écrire une fonction `check(file)` qui renvoie des `Hit`, décorée par `@rule(id=..., title=..., severity=..., category=..., description=..., recommendation=..., globs=...)` (voir `registry.py`). L'identifiant doit être unique et stable.
2. Renseigner `sample_path`, `fail_example` et `pass_example` : les tests vérifient que l'exemple « mauvais » déclenche la règle et que l'exemple « bon » ne la déclenche pas.
3. Ajouter les cas particuliers dans `backend/app/tests/test_security_scan.py`.
4. Lancer `python manage.py test app.tests.test_security_scan` puis le scan complet.

Le code généré par le générateur d'API doit rester conforme aux règles (voir `test_generator_pagination.py`).
