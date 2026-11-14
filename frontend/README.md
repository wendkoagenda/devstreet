# Frontend React (Vite + TypeScript)

Interface utilisateur de devstreet (React 19, RTK Query, shadcn/ui, Tailwind).

## Prérequis

- Node.js 20+
- npm
- Backend disponible (local ou distant) pour consommer l'API

## Installation

Depuis `frontend/` :

```bash
npm install
cp .env.example .env
npm run dev    # :5173
```

Sans fichier `.env`, l'application refuse de démarrer (variables Vite obligatoires).

## Variables d'environnement

Modèle : [`frontend/.env.example`](.env.example).

Toutes ces valeurs sont **publiques** (intégrées au JavaScript) : jamais de secret ici.

| Variable | Obligatoire | Description |
|---|---|---|
| `VITE_API_URL` | oui | Base API (ex. `/api` en local ; le serveur Vite relaie vers Django) |
| `VITE_API_V1_URL` | oui | Base API v1 (ex. `/api/v1`) |
| `VITE_USE_S3` | non | `true` si le backend a `USE_S3=True` : les fichiers sont lus via `/api/v1/files/` (utilisateur connecté). Absente = `/media/` |

Exemple local typique :

```env
VITE_API_URL=/api
VITE_API_V1_URL=/api/v1
```

## Commandes

```bash
npm run dev      # serveur de développement
npm run build    # tsc -b + build Vite
npm run lint     # ESLint
```

## Générateur d'écrans CRUD

La génération des slices frontend (API RTK Query, schémas Zod, pages…) se lance depuis le backend.

Voir [`../backend/scripts/README.md`](../backend/scripts/README.md).
