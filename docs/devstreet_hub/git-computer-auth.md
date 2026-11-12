# Connecter mon ordinateur (Git via DevStreet)

## Mécanisme retenu

**PAT HTTPS Gitea** créé pour le compte lié (`ForgeIdentity`), remis au CLI après confirmation navigateur **DevStreet**, stocké dans le coffre OS (keyring) et servi à Git via un credential helper.

Pourquoi pas `gt auth login --oauth` ? Le CLI officiel Gitea ouvre l’autorisation **Gitea**, pas DevStreet ([docs](https://docs.gitea.com/cli/authentication/)).  
Pourquoi pas JWT Django ? Gitea ne l’accepte pas pour `git push` / `git fetch`.  
Pourquoi pas device-flow OAuth Gitea ? Non requis ici : Django orchestre la confirmation, puis appelle l’API Gitea (BasicAuth temporaire → PAT utilisateur → invalidation du mot de passe).

Le jeton **admin** Gitea ne quitte jamais Django.

## Parcours

1. Installer le CLI (`tools/devstreet`, voir README).
2. `python -m devstreet auth login --hub <FRONTEND_URL>`
3. Le navigateur ouvre `/hub/git-auth/authorize?request=<uuid>` (UI DevStreet uniquement).
4. Connexion Django si besoin, puis clic explicite **Autoriser** / **Refuser** (pas d’auto-approve).
5. Le CLI poll avec PKCE, reçoit le PAT une seule fois, l’enregistre, configure Git.
6. `git push` / `git fetch` HTTPS réutilisent le helper.

## Commandes (Windows / PowerShell)

```powershell
cd tools
python -m pip install -r devstreet/requirements.txt
$env:PYTHONPATH = (Get-Location).Path

python -m devstreet auth login --hub http://localhost:5173
# optionnel si le proxy Vite n'est pas utilisé :
# python -m devstreet auth login --hub http://localhost:5173 --api http://localhost:8000/api/v1

python -m devstreet auth status
python -m devstreet auth logout
```

## Révocation

| Action | Effet |
|--------|--------|
| `auth logout` (CLI) | Retire le secret local + nettoie le credential Git pour ce compte. Les autres helpers / comptes restent. |
| Mon compte → Ordinateurs connectés → Révoquer | Supprime le PAT correspondant dans Gitea. N’efface ni dépôts ni autres ordinateurs. |

## Sécurité

- PKCE (S256), TTL 10 min, polling min. 2 s, max ~90 polls, grant à usage unique.
- `hub_base_url` limité aux origines CORS / `FRONTEND_URL`.
- Aucun secret dans l’URL du remote ni dans les arguments Git.
- Droits = permissions Gitea du compte utilisateur (scopes `read/write:repository`, `read:user`).

## Limites restantes

- Le credential helper DevStreet est ajouté en tête de `credential.helper` global ; les autres helpers sont conservés.
- En local, le CLI appelle `{hub}/api/v1` (proxy Vite) sauf `--api`.
- Pas de SSH dans cette version.
- Pas de refresh automatique du PAT (révocation + reconnexion).
- Vérification push/fetch réelle : dépôt de test dédié uniquement (pas le dépôt `devstreet`).
