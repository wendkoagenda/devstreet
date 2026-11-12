# devstreet

devstreet : projet full-stack **Django REST Framework** + **React 19 / TypeScript / Vite** avec authentification JWT et gestion des rôles/permissions.

## Stack

- **Backend** : Django + DRF, PostgreSQL, SimpleJWT, Swagger/ReDoc
- **Frontend** : React 19, Redux Toolkit (RTK Query), Zustand, shadcn/ui, Tailwind, React Hook Form + Zod, i18next

## Architecture

Flux backend : `Client → ViewSet → Service → Repository → DB`

- Backend : `core/` (auth et IAM), `devstreet_hub/` (projets) et `metier/` (utilitaires partagés et extension du générateur)
- Frontend organisé en feature slices sous `frontend/src/models/<feature>/`
- Auth JWT (cookies HttpOnly en same-origin) ; permissions embarquées dans les tokens
- En local, le frontend Vite relaie `/api` vers Django (`VITE_API_URL=/api`)

## Installation rapide

### Backend

```bash
cd backend
python -m venv venv
# Windows : .\venv\Scripts\Activate.ps1
# Linux/Mac : source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # renseigner PostgreSQL et les secrets
python manage.py migrate
python manage.py init_data
python manage.py runserver    # :8000
```

Détail : [`backend/README.md`](backend/README.md)

Module projets DevStreet Hub (backend uniquement) : [`docs/devstreet_hub/README.md`](docs/devstreet_hub/README.md), collection Postman et fiches d'interfaces numérotées incluses.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env          # obligatoire : VITE_API_URL et VITE_API_V1_URL
npm run dev                   # :5173
```

Détail : [`frontend/README.md`](frontend/README.md)

## Workflow Git CLI

Les `git commit` / `git push` directs sont bloqués. Depuis la racine :

```bash
python git-cli/install-hooks.py
python git-cli/commit.py
python git-cli/push.py
python git-cli/pr.py
```

Détail : [`git-cli/README.md`](git-cli/README.md)

## Documentation

| Document | Contenu |
|---|---|
| [`backend/README.md`](backend/README.md) | Install, `.env`, archi backend, commandes |
| [`frontend/README.md`](frontend/README.md) | Install, `.env`, commandes |
| [`backend/scripts/README.md`](backend/scripts/README.md) | Générateur CRUD (backend + frontend) |
| [`git-cli/README.md`](git-cli/README.md) | Workflow Git obligatoire |
| [`00readme/`](00readme/) | Onboarding, CI, CD, sécurité, etc. |
