# CLI DevStreet — Connecter mon ordinateur

Autorisation Git via le navigateur **DevStreet** (pas l’UI Gitea).  
Mécanisme : **PAT HTTPS Gitea** stocké dans le coffre OS + credential helper Git.

## Installation (Windows / PowerShell)

Depuis la racine du dépôt :

```powershell
cd tools
python -m pip install -r devstreet/requirements.txt
```

Alias pratique (session courante) :

```powershell
function devstreet { python -m devstreet @args }
$env:PYTHONPATH = (Resolve-Path .).Path
```

Ou depuis `tools/` :

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m devstreet --help
```

## Utilisation

```powershell
# 1. Connexion (ouvre le navigateur DevStreet)
python -m devstreet auth login --hub http://localhost:5173

# 2. Statut
python -m devstreet auth status

# 3. Déconnexion locale (retire le secret de cet ordinateur)
python -m devstreet auth logout
```

Après `login`, `git push` / `git fetch` vers l’hôte Gitea de cette instance réutilisent l’accès.

## Révocation serveur

Dans DevStreet → **Mon compte** → **Ordinateurs connectés** → Révoquer.  
Cela invalide le PAT dans Gitea. La déconnexion CLI seule ne révoque pas le serveur.

## Sécurité

- Aucun secret dans l’URL du remote ni dans les arguments affichés.
- Le jeton admin Gitea ne quitte jamais Django.
- L’autorisation navigateur exige un clic explicite (pas d’auto-approve).
