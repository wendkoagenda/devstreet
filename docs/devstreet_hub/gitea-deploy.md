# Installer Gitea pour DevStreet Hub (déploiement & local)

Gitea est un **service externe** : il n’est pas embarqué dans le monorepo DevStreet. Django / le Hub l’appellent via son API admin. Même principe que PostgreSQL : tu installes la forge, tu configures l’URL et les secrets dans `backend/.env`.

Ce guide s’adresse à la personne qui **déploie** ou **prépare un environnement** (local, staging, prod).

## Architecture (rappel)

```
DevStreet (API Django + front) ──HTTPS/API──► Gitea (image officielle, version épinglée)
```

- Pas de dossier `services/gitea` dans le repo.
- Version **épinglée** (ne pas utiliser `:latest`).
- Les maj Gitea se font **volontairement** (test Hub + smoke Git avant upgrade).

Image de référence documentée pour la démo locale : `docker.gitea.com/gitea:28.3.0`.

## Variables d’environnement requises

À renseigner dans `backend/.env` (jamais dans Git) :

| Variable | Obligatoire | Rôle |
|----------|-------------|------|
| `DEVSTREET_HUB_GITEA_URL` | oui | URL **interne** que Django utilise pour l’API (ex. `http://127.0.0.1:13000` en local, `https://git.interne` en prod) |
| `DEVSTREET_HUB_GITEA_TOKEN` | oui | Token **admin** Gitea (création users / dépôts / collaborateurs). Secret. |
| `DEVSTREET_HUB_GITEA_WEBHOOK_SECRET` | oui | Secret partagé pour signer les webhooks push. Secret. |
| `DEVSTREET_HUB_GITEA_PUBLIC_URL` | recommandé hors local | URL **publique** vue par les humains / `git clone` (HTTPS en prod). Si absente, le Hub réutilise `GITEA_URL`. |
| `DEVSTREET_HUB_INSTANCE_ID` | optionnel | Préfixe 2–8 caractères `[a-z0-9]` pour les logins forge `ds-…` si plusieurs Django partagent la même forge. |

Exemple local :

```dotenv
DEVSTREET_HUB_GITEA_URL=http://127.0.0.1:13000
DEVSTREET_HUB_GITEA_PUBLIC_URL=http://127.0.0.1:13000
DEVSTREET_HUB_GITEA_TOKEN=<token_admin>
DEVSTREET_HUB_GITEA_WEBHOOK_SECRET=<secret_long_aleatoire>
```

Exemple prod (Gitea sur la même VM, déployé par `CD - GITEA SSH`) :

```dotenv
DEVSTREET_HUB_GITEA_URL=http://gitea:3000
DEVSTREET_HUB_GITEA_PUBLIC_URL=https://git.votre-domaine.example
DEVSTREET_HUB_GITEA_TOKEN=<token_admin>
DEVSTREET_HUB_GITEA_WEBHOOK_SECRET=<secret_long_aleatoire>
```

Générer un secret webhook (PowerShell) :

```powershell
# 32+ octets aléatoires, base64 URL-safe possible
[Convert]::ToBase64String((1..48 | ForEach-Object { Get-Random -Maximum 256 }) -as [byte[]])
```

Sans ces variables, le Hub démarre mais le provisionnement Git / dépôts répond en erreur (souvent 503 / conflit forge).

---

## 1. Installer Gitea (Docker)

### Local (démo)

```powershell
docker run -d --name devstreet-chantier-gitea `
  -p 127.0.0.1:13000:3000 `
  -v devstreet-chantier-gitea:/data `
  docker.gitea.com/gitea:28.3.0
```

- UI : http://127.0.0.1:13000/
- Relancer plus tard : `docker start devstreet-chantier-gitea`

### Staging / prod

Sur une VM gérée par le CD du dépôt : workflow **CD - GITEA SSH** (voir `deploy/README.md`, section Gitea). Il installe Gitea et son Postgres, obtient le certificat, crée le compte administrateur (`GITEA_ADMIN_*`) et verrouille l'installation (`INSTALL_LOCK`, inscriptions fermées, SSH Gitea désactivé). L'assistant web n'est donc pas utilisé.

L'URL interne `http://gitea:3000` n'est acceptée en HTTP que pour l'hôte `gitea` (réseau Docker de la VM) ; tout autre hôte exige HTTPS.

Jeton admin API, à créer une fois sur la VM (le jeton ne passe pas par les journaux du CD) :

```bash
docker exec -u git gitea gitea admin user generate-access-token   --username <GITEA_ADMIN_USER> --token-name devstreet-hub-provisioning --scopes all --raw
```

Le copier dans `DEVSTREET_HUB_GITEA_TOKEN` de `backend.env.<branche>`, ajouter `DEVSTREET_HUB_GITEA_WEBHOOK_SECRET`, puis `definir` et redéployer l'app.

Principes (installation manuelle ou autre hébergeur) :

- Même image **épinglée** (ou tag équivalent validé).
- Exposer Gitea derrière un reverse proxy **HTTPS**.
- Persister le volume `/data` (sauvegardes avant toute maj d’image).
- Pas besoin de runners / Actions Gitea pour le Hub actuel.

Au premier accès navigateur : assistant d’installation Gitea (SQLite acceptable en démo ; Postgres/MySQL recommandé en prod). Créer le **compte administrateur** quand demandé.

---

## 2. Créer le token admin API

Le Hub a besoin d’un token avec droits d’administration pour :

- créer les comptes forge liés aux utilisateurs DevStreet ;
- créer les dépôts de projet ;
- ajouter / retirer des collaborateurs selon l’équipe Hub.

### Dans l’UI Gitea (compte admin)

1. Se connecter avec le compte **administrateur**.
2. Menu utilisateur (avatar) → **Settings** / Paramètres.
3. Onglet **Applications**.
4. Section **Generate New Token** / Générer un nouveau jeton :
   - Nom : ex. `devstreet-hub-provisioning`
   - Scopes : cocher au minimum ce qui permet l’admin API (selon version : **all** / droits admin, ou équivalent « administration » + dépôt / utilisateur). En pratique, pour le provisioning Hub, un token **admin** (compte admin + scopes étendus) est attendu.
5. **Générer**, **copier immédiatement** le token (il n’est plus réaffiché en clair).
6. Coller la valeur dans `DEVSTREET_HUB_GITEA_TOKEN`.

Ne jamais committer ce token. En prod : coffre / secrets du déploiement (`deploy_env`, variables CI, etc.).

### Vérification rapide

```powershell
# Remplacer URL et TOKEN
curl -s -H "Authorization: token VOTRE_TOKEN" http://127.0.0.1:13000/api/v1/admin/users | Select-Object -First 5
```

Une réponse JSON (liste d’utilisateurs) confirme que le token admin fonctionne. Une 401/403 indique un mauvais token ou un compte non admin.

---

## 3. Configurer le webhook push

Le Hub écoute :

`POST /api/v1/integrations/gitea/webhook`

(ex. local : `http://host.docker.internal:8000/api/v1/integrations/gitea/webhook` si Gitea est en Docker et Django sur l’hôte ; en prod : `https://api.votre-domaine.example/api/v1/integrations/gitea/webhook`).

### Secret

1. Choisir une longue chaîne aléatoire.
2. La mettre dans `DEVSTREET_HUB_GITEA_WEBHOOK_SECRET` **et** dans la config webhook Gitea (même valeur).

### Dans Gitea

Deux approches possibles selon votre politique :

**A. Webhook système / admin** (si disponible sur votre version) pour tous les dépôts, ou  
**B. Webhook par organisation / dépôt** créé manuellement ou via procédure d’exploitation.

Pour chaque webhook pertinent :

| Champ | Valeur |
|-------|--------|
| Target URL | `https://<hôte-api-devstreet>/api/v1/integrations/gitea/webhook` |
| HTTP Method | POST |
| Content type | `application/json` |
| Secret | = `DEVSTREET_HUB_GITEA_WEBHOOK_SECRET` |
| Événement | **Push** (minimum) |

La signature attendue côté Hub est l’en-tête `X-Gitea-Signature` (HMAC). Sans secret correct → 403.

Le push met à jour la « fraîcheur » côté Hub ; une analyse IA relit toujours le SHA depuis Gitea.

> Note : selon la version et la config, Gitea peut aussi envoyer `X-Gitea-Event` / `X-Gitea-Delivery`. Ne pas désactiver ces en-têtes au proxy.

---

## 4. Checklist avant d’ouvrir le Hub

1. [ ] Conteneur / service Gitea up, version épinglée.
2. [ ] Compte admin créé, UI accessible (HTTP local ou HTTPS prod).
3. [ ] Token admin généré → `DEVSTREET_HUB_GITEA_TOKEN`.
4. [ ] `DEVSTREET_HUB_GITEA_URL` (et `PUBLIC_URL` si besoin) renseignés.
5. [ ] Secret webhook identique Gitea ↔ `DEVSTREET_HUB_GITEA_WEBHOOK_SECRET`.
6. [ ] Webhook push pointe vers l’API DevStreet joignable **depuis** Gitea.
7. [ ] Redémarrer Django après modification du `.env`.
8. [ ] Smoke : créer un projet Hub → dépôt Gitea provisionné ; `git push` HTTPS selon [git-https-browser.md](git-https-browser.md).

---

## 5. Mises à jour Gitea (sans se faire surprendre)

1. Lire le changelog de la version cible.
2. Backup du volume `/data`.
3. Monter la nouvelle image **épinglée** sur un environnement de test.
4. Relancer smoke Hub (création dépôt, push, webhook).
5. Seulement ensuite : prod.

Ne jamais basculer prod sur `:latest`.

---

## Liens utiles

- Contrats forge / identités : [integrations.md](integrations.md)
- Git HTTPS navigateur (GCM / OAuth Hub) : [git-https-browser.md](git-https-browser.md)
- Auth ordinateur / PAT : [git-computer-auth.md](git-computer-auth.md)
- Vue d’ensemble Hub : [README.md](README.md)
