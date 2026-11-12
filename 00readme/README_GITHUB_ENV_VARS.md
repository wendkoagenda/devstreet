# Remote Devops — Variables d'environnement GitHub Actions

## Objectif

Documenter comment Remote Devops permet de **lire** et **pousser** des variables / secrets GitHub Actions au format `.env`, et le parcours complémentaire pour générer un bloc `VM_SSH_*` depuis une VM GCP.

Ce n'est **pas** la doc des variables Django / Vite du produit lui-même (`backend/.env`, `frontend/.env`). Pour celles-ci, voir notamment :

- [`README_SAME_ORIGIN_COOKIES.md`](./README_SAME_ORIGIN_COOKIES.md) (auth cookies) ;
- [`README_STORAGE_FILE_MANAGEMENT.md`](./README_STORAGE_FILE_MANAGEMENT.md) (`USE_GCS`, etc.) ;
- `backend/.env.example` et `frontend/.env.example`.

Ici : cockpit opérateur pour les **environnements GitHub Actions** liés aux dépôts synchronisés.

---

## Concepts

| Notion | Rôle |
| --- | --- |
| Environnement GitHub | Cible nommée (`staging`, `prod`, …) sur un dépôt ; porte ses propres variables et secrets |
| Variable | Valeur **lisible** après écriture (API GitHub Actions variables) |
| Secret | Valeur **écriture seule** : Remote Devops et l'UI ne relisent jamais la valeur |
| Scope dépôt | Variables / secrets **hors** environnement (niveau repository) |
| Scope environnement | Variables / secrets rattachés à un environnement précis |

Remote Devops ne stocke **pas** les valeurs en base : lecture et écriture passent par l'API GitHub (GitHub App installée pour l'organisation).

---

## Prérequis

1. GitHub connecté pour l'organisation courante (wizard connexions).
2. Dépôts synchronisés (`/depots`).
3. Permissions internes JWT :
   - `github.view` — voir dépôts / environnements ;
   - `github.variables` — lister / pousser / supprimer des **variables** ;
   - `github.secrets` — lister (noms) / pousser / supprimer des **secrets**.
4. L'App GitHub doit avoir les droits Actions nécessaires côté dépôt (sinon erreur IAM GitHub `403`).

Relogin après attribution des permissions.

---

## Parcours UI

### Depuis un dépôt

1. Aller dans **Dépôts** → ouvrir un dépôt (`/depots/:id`).
2. Section **Environnements** : liste live GitHub.
3. **Ajouter** un environnement (crée / met à jour sur GitHub).
4. Cliquer le nom → page `/depots/:id/environments/:name`.
5. Panneau **Variables** + **Secrets** : coller un `.env`, pousser.

Le même panneau existe aussi au niveau dépôt (hors environnement) selon les écrans liés projet / dépôt.

### Depuis une fiche VM (complément SSH)

Pour alimenter un secret GitHub avec les clés SSH d'une VM :

1. Ouvrir une VM → onglet **Accès**.
2. Prérequis : IP publique, OS Login désactivé, pare-feu SSH ouvert, permission `vms.create`.
3. **Générer VM_SSH_HOST / USER / PRIVATE_KEY** → confirmation → bloc `.env` affiché **une seule fois**.
4. Copier le bloc, puis le coller dans l'onglet **Secrets** de l'environnement GitHub cible (voir ci-dessus).

La clé privée n'est **pas** stockée côté Remote Devops.

---

## Format `.env` accepté

Parseur partagé (FE + BE) :

- une paire `NAME=value` par ligne ;
- lignes vides et commentaires `#…` ignorés ;
- préfixe optionnel `export ` ;
- guillemets simples ou doubles autour de la valeur retirés ;
- nom : `[A-Za-z_][A-Za-z0-9_]*` ;
- en cas de doublon de nom, la **dernière** occurrence gagne.

Exemple :

```env
# commentaire ignore
API_URL=https://example.com
DEBUG=false
export FEATURE_FLAG=on
VM_SSH_PRIVATE_KEY="-----BEGIN ..."
```

Fichiers concernés :

- Frontend : `frontend/src/models/cloud/github/parse-dotenv.ts`
- Backend : `backend/app/metier/cloud/github/dotenv.py`

---

## Variables vs secrets (comportement produit)

| | Variables | Secrets |
| --- | --- | --- |
| Liste UI | Nom + **valeur** | Nom (+ date) seulement |
| Copie | Contenu `KEY=value` | Noms seuls `KEY=` (sans valeur) |
| Push | Confirmation légère | Confirmation obligatoire |
| Après push | Relisible via « Actualiser depuis GitHub » | Valeur invisible à jamais |
| Audit | Action journalisée, **valeur non journalisée** | Idem |

---

## Flux technique

```text
UI (coller .env)
  -> parseDotEnv / parse_dotenv
  -> POST /api/v1/cloud/github/variables  { repository_id, environment?, content }
  -> POST /api/v1/cloud/github/secrets    { repository_id, environment?, content, confirmed: true }
    -> GithubVariablesView / GithubSecretsView
      -> GithubAdapter.upsert_variable / put_secret (API GitHub)
      -> AuditLog (set_github_variable | set_github_secret)
```

Endpoints utiles :

| Méthode | Chemin | Rôle |
| --- | --- | --- |
| `GET` | `/api/v1/cloud/github/environments?repository_id=` | Lister les env |
| `PUT` | `/api/v1/cloud/github/environments` | Créer / upsert un env |
| `DELETE` | `/api/v1/cloud/github/environments` | Supprimer un env |
| `GET/POST/PATCH/DELETE` | `/api/v1/cloud/github/variables` | Variables (GET liste, POST bulk via `content`) |
| `GET/POST/DELETE` | `/api/v1/cloud/github/secrets` | Secrets (GET noms, POST bulk via `content`) |

Paramètre de scope : `environment` (query ou body) — absent = niveau dépôt.

Génération SSH VM :

```text
UI fiche VM -> POST /api/v1/vms/actions { action: issue_ssh_env, confirmed: true }
  -> GcpAdapter.issue_ssh_env
  -> reponse { env: "VM_SSH_HOST=...\nVM_SSH_USER=...\nVM_SSH_PRIVATE_KEY=\"...\"" }
```

---

## Recette opératoire recommandée

### Déployer une app via GitHub Actions

1. Créer l'environnement GitHub (`staging` / `prod`) depuis Remote Devops.
2. Pousser les **variables** non sensibles (`API_URL`, flags, etc.).
3. Générer le `.env` SSH sur la VM cible (si le workflow SSH vers la VM).
4. Coller `VM_SSH_*` (et autres secrets) dans **Secrets** de l'environnement.
5. Dans le workflow GitHub, référencer `environment: staging` (ou `prod`) pour charger ces clés.
6. Vérifier l'audit Remote Devops (`set_github_variable`, `set_github_secret`, `issue_vm_ssh_env`).

### Mettre à jour une variable

1. Actualiser depuis GitHub.
2. Copier les variables existantes si besoin.
3. Modifier le textarea / coller un nouveau `.env` partiel.
4. **Pousser** : upsert (création ou mise à jour du même nom).

### Supprimer

Bouton **Supprimer** sur la ligne (secret : confirmation native navigateur).

---

## Garde-fous sécurité

- Valeurs de secrets **jamais** renvoyées par l'API après écriture.
- Payloads d'audit sans valeur (`valeur non journalisee`).
- Secrets : confirmation UI + `confirmed: true` côté API.
- Clé privée SSH : affichage unique dans le Sheet VM ; pas de persistance Remote Devops.
- Ne pas coller de secrets dans le panneau **Variables** (visibles ensuite à tous les lecteurs `github.variables`).

---

## Limites connues

- Pas de synchronisation des variables / secrets au niveau **organisation** GitHub (seulement dépôt + environnement).
- Pas d'historique des valeurs dans Remote Devops (source de vérité = GitHub).
- Les métriques / droits GitHub App insuffisants se traduisent par des erreurs lisibles (`403` / message IAM).
- Le Sheet VM doit rester ouvert après génération SSH pour voir le bloc (correction focus Radix déjà en place côté UI).

---

## Fichiers de référence

| Zone | Chemin |
| --- | --- |
| Panneau vars/secrets | `frontend/src/models/cloud/github/components/github-vars-secrets-panel.tsx` |
| Liste environnements | `frontend/src/models/cloud/github/components/github-environments-panel.tsx` |
| Page env | `frontend/src/models/cloud/github/pages/github-environment-detail.tsx` |
| API FE | `frontend/src/models/cloud/github/api.ts` |
| Vues BE | `backend/app/metier/views/github_oauth_views.py` |
| Adapter GitHub | `backend/app/metier/cloud/github/adapter.py` |
| Parse `.env` BE | `backend/app/metier/cloud/github/dotenv.py` |
| Génération SSH | `backend/app/metier/cloud/gcp/adapter.py` (`issue_ssh_env`) |
| UI SSH | `frontend/src/models/vm/components/vm-detail-sheet.tsx` (onglet Accès) |

---

## Definition de termine (doc)

Cette doc est utile si un opérateur peut :

1. créer un environnement GitHub depuis Remote Devops ;
2. coller un `.env` et pousser variables / secrets ;
3. comprendre la différence variable vs secret ;
4. générer `VM_SSH_*` depuis une VM et le coller en secret d'environnement ;
5. savoir quelles permissions et audits sont en jeu.
