# Parcours Git HTTPS navigateur (GCM + DevStreet)

## Architecture

1. Dépôts Gitea **publics** dès la création (clone anonyme).
2. Écriture : propriétaire + collaborateurs Hub synchronisés.
3. Auth push : **Git Credential Manager** → OAuth2 public (PKCE) sur DevStreet → PAT Gitea.
4. JWT Django et mot de passe Django ne sont jamais présentés à Gitea.

## Config initiale (ordinateur neuf)

Affichée aussi via `GET /api/v1/git-oauth/client-config` :

```text
git config --global credential.<GITEA_ORIGIN>.provider generic
git config --global credential.<GITEA_ORIGIN>.oauthClientId devstreet-gcm
git config --global credential.<GITEA_ORIGIN>.oauthAuthorizeEndpoint <HUB>/api/v1/git-oauth/authorize
git config --global credential.<GITEA_ORIGIN>.oauthTokenEndpoint <HUB>/api/v1/git-oauth/token
git config --global credential.<GITEA_ORIGIN>.oauthRedirectUri http://127.0.0.1
git config --global credential.<GITEA_ORIGIN>.oauthUseClientAuthHeader false
git config --global credential.<GITEA_ORIGIN>.oauthDefaultUserName git
git config --global credential.<GITEA_ORIGIN>.oauthScopes git
```

Retirer toute entrée `credential.<GITEA_ORIGIN>.helper` pointant vers `%LOCALAPPDATA%\DevStreet` avant d’utiliser GCM.

## Migration depuis l’ancien connecteur

1. `python -m devstreet auth logout` (si CLI encore présente).
2. Supprimer les helpers :

```powershell
git config --global --get-regexp "credential\..*DevStreet"
# puis pour chaque entrée DevStreet :
git config --global --unset-all credential.http://127.0.0.1:13000.helper
```

3. Appliquer le bloc git config Hub (ci-dessus).
4. Révoquer les anciens ordinateurs dans Mon compte si besoin.
5. Le dossier `%LOCALAPPDATA%\DevStreet\Git` peut être supprimé manuellement.

Ne pas effacer les helpers GitHub / Azure.

## Réconciliation dépôts existants

```powershell
cd backend
python manage.py reconcile_forge_visibility          # aperçu
python manage.py reconcile_forge_visibility --apply  # écriture forge
```

## Limites

- Config Git obligatoire (le navigateur ne l’écrit pas).
- Succès sur un poste déjà pourvu d’un helper DevStreet ne prouve pas le parcours neuf.
- Les comptes forge doivent avoir `visibility=public` (sinon Gitea renvoie 401/404 aux anonymes même si le dépôt est `private=false`). Les nouvelles identités Hub sont créées ainsi ; `reconcile_forge_visibility --apply` corrige les comptes existants.
