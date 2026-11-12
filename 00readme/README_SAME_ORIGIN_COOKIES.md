# Same-origin et cookies HttpOnly (auth SPA)

Ce document décrit **comment** l’authentification du SPA est branchée sur des cookies JWT HttpOnly, et **pourquoi** le frontend et l’API doivent partager la **même origine** (même schéma + host + port).

Le **contrat du reverse proxy** (routage par chemin, en-têtes) est décrit en section 3.2, quel que soit le proxy choisi. Ici : modèle de sécurité, cookies, CSRF, flux SPA, local vs prod.

---

## 1. Objectif

Le SPA ne stocke **plus** les JWT dans `localStorage`. Les tokens vivent dans des cookies **HttpOnly** posés par Django (`Set-Cookie`). Le JavaScript **ne peut pas les lire** : XSS ne peut pas exfiltrer `access_token` / `refresh_token`.

Pour que le navigateur **envoie** ces cookies sur chaque appel API :

1. La requête doit être **same-site** (idéalement **same-origin**) avec `SameSite=Lax`.
2. `fetch` / RTK Query doivent utiliser `credentials: "include"`.
3. L’URL API vue par le navigateur doit être un **chemin** (`/api/...`), pas un autre host (`https://api.autre-domaine.fr`).

Les permissions **ne sont pas** dans le JWT (limite de taille des cookies ~4 Ko). Elles sont relues en base via `GET /api/auth/me`. Voir §7.

Le profil d’affichage (nom, email, rôles) n’est **pas** recopié dans le `localStorage` ni dans un cookie lisible JS : il vit en mémoire (Zustand) après `/auth/me`. Au boot / login / logout, les anciennes clés (`user`, `user_full_name`, `isAuthenticated`, etc.) sont purgées.

---

## 2. Same-origin vs CORS avec credentials

| | Same-origin (choix actuel) | Cross-origin (`app.` vs `api.`) |
| --- | --- | --- |
| URL dans le SPA | `/api`, `/api/v1` (pas d’hôte) | `https://api.example.com` |
| Cookie `SameSite=Lax` | Envoyé (même origine) | Souvent **non** envoyé sur XHR cross-site |
| CORS | Inutile pour le navigateur (même origine) | `CORS_ALLOW_CREDENTIALS` + origines exactes |
| CSRF | Cookie `csrftoken` + header `X-CSRFToken` | Idem, plus `CSRF_TRUSTED_ORIGINS` strict |
| Alternative cookies | — | `SameSite=None; Secure` + souvent `Domain=.parent` (plus large) |

Le projet a choisi le **routage par chemin** : un seul host public, le reverse proxy dispatch `/api` et `/ws` vers Django, le reste vers le SPA.

```
Navigateur (origine = https://staging.360managerplus.mygalery.fr)
    │
    ├─ GET /                    → frontend (nginx, fichiers statiques + SPA)
    ├─ GET/POST /api/...        → backend (Daphne :8000)
    └─ WS  /ws/...              → backend (Channels)
```

Nginx du frontend **ne proxy pas** `/api` : il ne sert que le SPA (`frontend/nginx.conf`). Le split est **devant** (Vite en local, le reverse proxy en staging/prod).

---

## 3. Comment c’est branché par environnement

### 3.1 Local (Vite)

[`frontend/vite.config.ts`](../frontend/vite.config.ts) :

```ts
server: {
  port: 3000,
  proxy: {
    "/api": { target: "http://localhost:8000", changeOrigin: true },
    "/ws":  { target: "ws://localhost:8000", ws: true, changeOrigin: true },
  },
}
```

Le navigateur parle uniquement à `http://localhost:3000`. Les cookies `Set-Cookie` (sans `Domain`) sont enregistrés pour **`localhost` / le host de la page** (`localhost:3000`). Les appels suivants vers `/api/...` emportent les cookies ; Vite les transmet à Django.

Variables frontend ([`frontend/.env.example`](../frontend/.env.example)) :

```
VITE_API_SAME_ORIGIN_GLOBAL=/api
VITE_API_SAME_ORIGIN_V1=/api/v1
VITE_API_SAME_ORIGIN_V2=/api/v2
```

Résolues dans [`frontend/src/config/config.ts`](../frontend/src/config/config.ts) : **chemin uniquement**, le host vient de `window.location`.

Ne pas mettre `http://localhost:8000` dans ces variables : le login poserait les cookies sur le port 8000, le SPA sur 3000 ne les verrait pas (ou le CSRF / SameSite se casseraient).

### 3.2 Staging / production (reverse proxy)

L'application ne dépend d'aucune plateforme de déploiement. Elle suppose seulement qu'**un reverse proxy** (nginx, Caddy, Traefik…) est placé devant, sur un **seul domaine HTTPS** `https://<host>`, et respecte ce contrat :

| Chemin | Destination | Remarque |
| --- | --- | --- |
| `/api/...` | backend (port 8000) | **Ne pas retirer le préfixe `/api`** : Django attend `/api/auth/login`, pas `/auth/login` |
| `/ws/...` | backend | Seulement si le projet utilise les WebSockets |
| `/admin/`, `/swagger/`, `/redoc/` | backend (port 8000) | Django les refuse déjà s'ils sont désactivés (`ENABLE_ADMIN`, `ENABLE_API_DOCS`) |
| `/static/...`, `/media/...` | fichiers sur disque, servis par le proxy | Django ne les sert qu'avec `DEBUG=True`. Sur `/media/`, ajouter `Content-Disposition: attachment` et `X-Content-Type-Options: nosniff` (un fichier HTML ou SVG envoyé par un utilisateur ne doit pas s'exécuter sur votre domaine) |
| tout le reste | frontend (nginx, port 8080) | Le SPA et ses fichiers statiques |

Le proxy doit aussi :

- terminer le HTTPS et rediriger HTTP vers HTTPS (Django ne le fait pas : `SECURE_SSL_REDIRECT = False`) ;
- poser `X-Forwarded-Proto: https` et ajouter l'adresse du client à `X-Forwarded-For` ;
- être **le seul** proxy devant Django : `USE_X_FORWARDED_PROTO=true` règle `NUM_PROXIES` sur 1 (voir `backend/config/settings.py`). Avec une chaîne de plusieurs proxys, adapter cette valeur, sinon les adresses du journal et de la limitation de débit sont fausses ;
- ne jamais être contourné : si le backend est joignable directement depuis Internet, un client peut forger ces en-têtes.

La route `/api/health` (publique, sans détail) sert aux vérifications de santé. Le déploiement sur VM (Docker Compose, nginx et certbot, HTTPS) est décrit dans [`README_CD.md`](./README_CD.md) ; ce contrat y est appliqué par `deploy/proxy/site-https.conf.tpl`.

### 3.3 Django connaît déjà le préfixe `/api`

[`backend/config/urls.py`](../backend/config/urls.py) monte les apps sous `path('api/', ...)`. Le proxy **ne doit pas** retirer `/api`.

Auth : `/api/auth/login`, `/api/auth/me`, `/api/auth/csrf`, `/api/auth/token/refresh`, `/api/auth/logout`.  
CRUD : `/api/v1/...`.

---

## 4. Les trois cookies

Implémentation : [`backend/app/core/cookies.py`](../backend/app/core/cookies.py), settings dans [`backend/config/settings.py`](../backend/config/settings.py).

| Cookie | HttpOnly | Path | Durée (défaut) | Rôle |
| --- | --- | --- | --- | --- |
| `access_token` | **oui** | `/` | `JWT_ACCESS_TOKEN_LIFETIME` (60 min) | JWT d’identité, envoyé sur **toutes** les requêtes same-origin |
| `refresh_token` | **oui** | **`/api/auth`** | `JWT_REFRESH_TOKEN_LIFETIME` (14 jours) | Uniquement les URLs sous `/api/auth/...` (login, refresh, logout) |
| `csrftoken` | **non** | `/` (défaut Django) | session Django | Lu par le JS → header `X-CSRFToken` |

Attributs JWT (`AUTH_COOKIE_*`) :

- `HttpOnly=True` — JS ne lit pas les tokens.
- `Secure` — `AUTH_COOKIE_SECURE` ou `USE_HTTPS` (obligatoire en HTTPS).
- `SameSite` — défaut `Lax` (`AUTH_COOKIE_SAMESITE`).
- `Domain` — vide par défaut (`AUTH_COOKIE_DOMAIN`). Un domaine parent (`.mygalery.fr`) élargirait l’envoi du cookie : **à éviter** tant que le same-origin par chemin suffit.

CSRF :

- `CSRF_COOKIE_HTTPONLY = False` — le SPA doit lire `csrftoken` (ou utiliser le JSON de `/auth/csrf`).
- `CSRF_COOKIE_SAMESITE` défaut `Lax`.
- `CSRF_TRUSTED_ORIGINS` : origine **exacte** du SPA (`https://staging....` / `http://localhost:3000`). En DEBUG, repli sur localhost:3000 / 5173 si l’env est vide.

`ROTATE_REFRESH_TOKENS = True` + `BLACKLIST_AFTER_ROTATION = True` : chaque refresh émet un nouveau refresh et blacklist l’ancien.

---

## 5. Auth backend : cookie d’abord, Bearer en repli

[`backend/app/core/auth.py`](../backend/app/core/auth.py) — `LenientJWTAuthentication` (classe DRF par défaut) :

1. Si cookie `access_token` présent et JWT valide → utilisateur authentifié, puis **CSRF obligatoire**.
2. Cookie expiré / invalide → on **n’échoue pas tout de suite** (pour laisser `/auth/token/refresh` et le Bearer fonctionner).
3. Repli `Authorization: Bearer <jwt>` (Swagger, tests, scripts). **Pas** de CSRF dans ce cas.

WebSocket : [`backend/app/core/websocket_auth.py`](../backend/app/core/websocket_auth.py) lit le même cookie `access_token` (repli `?token=` pour outils). Le client SPA ouvre `ws(s)://<host-de-la-page>/ws/notifications/` ([`frontend/src/hooks/use-websocket.ts`](../frontend/src/hooks/use-websocket.ts)) pour rester same-origin.

HTTPS derrière proxy : `USE_HTTPS`, `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`, `USE_X_FORWARDED_HOST`, middleware [`ProxyHeadersMiddleware`](../backend/app/core/middleware.py) pour que Django pose `Secure` et accepte CSRF sur HTTPS.

---

## 6. CSRF côté SPA

Un cookie HttpOnly **n’empêche pas** CSRF : le navigateur envoie le cookie sur les requêtes same-site. Django exige donc le **double submit** : cookie `csrftoken` **et** header `X-CSRFToken`.

Flux :

1. `GET /api/auth/csrf` (`AllowAny`, `ensure_csrf_cookie`) pose le cookie et renvoie `{ csrfToken }` — [`csrf_view`](../backend/app/core/views/auth_views.py), [`ensureCsrfCookie`](../frontend/src/models/auth/functions/csrf-api.ts).
2. Le token est mis en mémoire (`csrfTokenMemory`) **et** relisible via `document.cookie`.
3. RTK Query ([`frontend/src/helpers/api/base-query.ts`](../frontend/src/helpers/api/base-query.ts)) : `credentials: "include"` + `prepareHeaders` pose `X-CSRFToken`.
4. Fetch hors RTK : [`credentialsFetch`](../frontend/src/helpers/api/credentials-fetch.ts).

Les GET « sûrs » passent sans header ; les POST/PUT/PATCH/DELETE authentifiés par cookie sans `X-CSRFToken` → **403 CSRF Failed**.

---

## 7. Flux session SPA

Fichiers : [`frontend/src/models/auth/slice.ts`](../frontend/src/models/auth/slice.ts), [`auth_views.py`](../backend/app/core/views/auth_views.py).

```
Boot (F5 / nouvel onglet)
  GET /api/auth/csrf     → cookie csrftoken (+ json)
  GET /api/auth/me       → cookie access_token (identité)
                         → user + permissions depuis la DB (pas le JWT)

Login
  POST /api/auth/login   → Set-Cookie access_token + refresh_token
                         → body JSON : { user } uniquement (plus de access/refresh)
  GET  /api/auth/me      → recharge le store Zustand

API métier (401 access expiré)
  POST /api/auth/token/refresh   → cookie refresh (path /api/auth)
                                 → nouveaux cookies (rotation)
  retry de la requête d’origine
  Si refresh échoue → event auth:session-expired → /login

Logout
  POST /api/auth/logout  → blacklist refresh + Delete-Cookie
```

Le JWT access ne contient que `user_id` / `email` (commentaire dans `CustomTokenObtainPairSerializer`). Un F5 **ne régénère pas** le JWT : `/auth/me` relit les **permissions actuelles** du rôle.

Les endpoints `/auth/login`, `/auth/token/refresh`, `/auth/csrf` et reset mot de passe **ne déclenchent pas** le refresh auto sur 401 (évite une boucle). Un 401 sur `/auth/me` (F5 après expiration de l’access) **tente** le refresh, puis retry.

Purge client : [`clearStorage`](../frontend/src/models/auth/functions/utils.ts) / [`purgeLegacyTokenStorage`](../frontend/src/models/auth/functions/utils.ts) retirent d’anciens tokens **et** d’anciennes infos d’affichage du `localStorage`. Session = cookies HttpOnly ; profil / permissions = Zustand après `/auth/me`.

---

## 8. Variables d’environnement (auth cookies)

Frontend (build Vite, mêmes noms partout) :

| Variable | Valeur attendue |
| --- | --- |
| `VITE_API_SAME_ORIGIN_GLOBAL` | `/api` |
| `VITE_API_SAME_ORIGIN_V1` | `/api/v1` |
| `VITE_API_SAME_ORIGIN_V2` | `/api/v2` |

Backend (runtime) :

| Variable | Prod / staging typique |
| --- | --- |
| `ALLOWED_HOSTS` | host public (sans schéma) |
| `CSRF_TRUSTED_ORIGINS` | `https://<host>` |
| `CORS_ALLOWED_ORIGINS` | même origine (filet ; le SPA same-origin n’en dépend pas) |
| `USE_HTTPS` / `AUTH_COOKIE_SECURE` / `CSRF_COOKIE_SECURE` | `True` |
| `AUTH_COOKIE_SAMESITE` | `Lax` |
| `AUTH_COOKIE_DOMAIN` | vide |
| `JWT_ACCESS_TOKEN_LIFETIME` | minutes (défaut 60) |
| `JWT_REFRESH_TOKEN_LIFETIME` | minutes (défaut 20160) |
| `BASE_CLIENT_URL` | origine SPA (AllowedHosts WebSocket) |
| `SITE_URL` | obligatoire (settings) |

---

## 9. Clients qui ne sont pas le SPA

Swagger, `manage.py test`, scripts : header `Authorization: Bearer <access>`. Pas de CSRF. Le login SPA **n’expose plus** le JWT dans le JSON : pour un Bearer manuel, utiliser un client qui lit le cookie ou un obtention dédiée (tests posent le cookie `access_token` sur `APIClient`).

---

## 10. Diagnostic

| Symptôme | Cause probable |
| --- | --- |
| Login 200 mais `/auth/me` 401, store vide | SPA n’appelle pas `/api` same-origin (URL absolue autre host) ; cookies non posés / non renvoyés |
| Message proxy Vite dans `setLoginInformation` | Cookies absents après login (dev server sans proxy `/api`) |
| 403 `CSRF Failed` | Pas de `GET /auth/csrf` avant la mutation, ou origine hors `CSRF_TRUSTED_ORIGINS` |
| 404 Django `auth/login` (sans `/api`) | Le reverse proxy retire le préfixe `/api` (« strip prefix ») |
| 405 sur `/api/...` | Trafic arrivé sur nginx SPA au lieu de Django |
| Cookies `Secure` absents en HTTP local | normal si `USE_HTTPS=False` ; en HTTPS prod, `Secure` obligatoire |
| WS anonyme | WS ouvert vers un autre host (pas `window.location.host`) ; cookie `access_token` non envoyé |
| Refresh 401 alors que l’utilisateur « est connecté » | Cookie refresh limité au path `/api/auth` ; appeler un autre path ne l’envoie pas |

Vérifier dans DevTools → Application → Cookies : `access_token` HttpOnly, `refresh_token` HttpOnly path `/api/auth`, `csrftoken` lisible. Network : requêtes `/api/...` **même host** que le document, header `Cookie` présent, `X-CSRFToken` sur les POST.

---

## 11. Fichiers de référence

| Couche | Fichier |
| --- | --- |
| Cookies JWT | `backend/app/core/cookies.py` |
| Auth DRF + CSRF cookie | `backend/app/core/auth.py` |
| Login / refresh / csrf / me / logout | `backend/app/core/views/auth_views.py` |
| Settings cookies / JWT / CORS | `backend/config/settings.py` |
| WS JWT cookie | `backend/app/core/websocket_auth.py` |
| Proxy local | `frontend/vite.config.ts` |
| Chemins API | `frontend/src/config/config.ts` |
| credentials + CSRF + refresh 401 | `frontend/src/helpers/api/base-query.ts` |
| Fetch manuel | `frontend/src/helpers/api/credentials-fetch.ts` |
| Session Zustand | `frontend/src/models/auth/slice.ts` |
| WS same-origin | `frontend/src/hooks/use-websocket.ts` |
| Nginx SPA (pas de proxy API) | `frontend/nginx.conf` |
| Contrat du reverse proxy | `00readme/README_SAME_ORIGIN_COOKIES.md` §3.2 |

---

## 12. Règles à ne pas casser

1. **Ne jamais** mettre un host complet dans `VITE_API_SAME_ORIGIN_*` (uniquement `/api...`).
2. **Ne jamais** remettre les JWT dans `localStorage` / le body de login pour le SPA.
3. **Ne pas** retirer le préfixe `/api` dans le reverse proxy (pas de « strip prefix »).
4. **Ne pas** proxy `/api` dans nginx frontend (le reverse proxy s'en charge déjà).
5. **Ne pas** élargir `AUTH_COOKIE_DOMAIN` sans raison (fuite de cookies vers d’autres sous-domaines).
6. **Ne pas** passer `SameSite=None` tant que tout est same-origin + `Lax`.
7. Toute nouvelle API appelée depuis le navigateur : chemin same-origin + `credentials: "include"` + CSRF sur les mutations.
