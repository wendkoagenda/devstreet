# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Full-stack project (devstreet): **Django REST Framework** backend (`backend/`) + **React 19 / TypeScript / Vite** frontend (`frontend/`), with JWT auth and role/permission management. Docs, commit messages, and generated code comments are in **French**.

## Mandatory Git workflow (git-cli)

Direct `git commit` / `git push` are **blocked** by hooks (`.githooks/`) and CI workflows. All Git operations must go through the Python scripts in `git-cli/`:

```powershell
python git-cli/install-hooks.py   # one-time setup (sets core.hooksPath=.githooks)
python git-cli/commit.py          # commit (adds required trailer X-Git-CLI: doonya-git-cli/2.0)
python git-cli/push.py            # push (sets DOONYA_GITCLI_PUSH=1; the frontend build is checked by CI, not at push)
python git-cli/pr.py              # create PR (title format: pr-<type>(<scope>): <titre>)
python git-cli/pull.py            # strict pull --rebase of current branch
python git-cli/merge.py --from <branch>   # merge feature into develop
python git-cli/doctor.py          # diagnose setup
python git-cli/deploy_env.py      # deployment variables/secrets and VM preparation (masters only, see 00readme/README_CD.md)
```

Branch flow: features → `develop` → `main` → `prod`. PRs to `main` only from `develop`; PRs to `prod` only from `main`. Protected paths and master emails/users are configured in `git-cli/access_control.conf`. Commit messages follow Conventional Commits (`feat`, `fix`, `docs`, `refactor`, etc. — see `00conventions/conventions-git.md`).

## Actions interdites sans demande explicite

Ne jamais lancer de build (`npm run build`, `tsc -b`, `docker build`) ni de test dans le navigateur (outils Chrome) sans demande explicite de l'utilisateur dans le message en cours. `.claude/settings.json` impose une validation (`ask`) pour ces commandes et ces outils : ne jamais la contourner, et indiquer dans le résumé que ces vérifications n'ont pas été faites.

## Commands

### Backend (from `backend/`, with venv activated: `.\venv\Scripts\Activate.ps1`)

```powershell
python manage.py runserver                     # dev server on :8000
python manage.py migrate
python manage.py makemigrations
python manage.py init_data                     # seed default roles & permissions
python manage.py test                          # all tests
python manage.py test app.tests.test_project   # single test module
python manage.py check
```

Requires PostgreSQL; DB credentials go in `backend/.env` (copy from `.env.example`).

### Frontend (from `frontend/`)

```powershell
npm run dev       # Vite dev server on :5173
npm run build     # tsc -b + vite build (run by the ci-frontend workflow on every pull request)
npm run lint      # ESLint
```

`npm test` runs Vitest (`npm run test:coverage` adds the coverage summary).

## Contrôles de qualité et CI

Détail dans `00readme/README_CI.md`. En local, depuis `backend/` (venv active) :

```powershell
python -m scripts.security_scan --fail-on warning            # scanner de sécurité (exceptions datées : security-exceptions.json)
python -m scripts.regression_guard --base origin/develop     # zones protégées touchées (regression-guard.json)
python -m scripts.dependency_audit --pip pip-audit.json --npm ..
pm-audit.json   # audit des dépendances
```

Modifier un fichier d'une zone protégée est permis, mais la CI le signale et demande la validation d'un responsable de zone (`ZONE_PROTEGEE_USERS`). Ne jamais retirer une zone ni affaiblir une règle du scanner pour faire passer un changement.

## CRUD generator

The core productivity tool: `backend/scripts/generate_api.py` generates the entire backend Repository Pattern stack **and** the frontend feature slice from a JSON model definition placed in `backend/scripts/models_zones/zone_N/`.

```powershell
# from backend/, venv active
python scripts/generate_api.py                              # interactive menu (option 1 = backend, 11 = frontend)
python scripts/generate_api.py --generate <Model> --zone zone_1   # backend stack
python scripts/generate_api.py --frontend <Model> --zone zone_1   # frontend slice
python scripts/generate_api.py --sync                       # resync state with filesystem
python scripts/generate_api.py --validate                   # check state integrity
```

The generator tracks state in `scripts/generator/improved_state.json` (MD5 checksums detect manual edits), takes backups in `scripts/generator/backups/`, and merges cumulatively into shared files (`models.py`, `serializers.py`, `urls.py`). Templates are Jinja2 files in `scripts/generator/templates/`; frontend generation lives in `scripts/generator/frontend_generator.py`. After frontend generation: run `npm run lint` and `npm run build`.

## Architecture

### Backend — Repository Pattern (layered)

Flow: `Client → ViewSet → Service → Repository → DB`. Never put business logic in views or ORM calls in services.

Django apps under `backend/app/`, each with the same layout:
- `core/` — auth, users, roles, permissions (the devstreet base)
- `metier/` — shared storage utilities and generator extension points; demo migration history only
- `devstreet_hub/` — project collaboration module (historical Django label: `projects`)

Each app contains: `interfaces/` (repository contracts), `repositories/` (ORM access), `services/` (business logic), `permissions/` (code-based checks like `users.view`), `views/` (DRF ViewSets), `serializers.py`, `models.py`, `management/commands/` (seeders). Tests live in `backend/app/tests/`.

Auth: JWT via SimpleJWT (`/api/token/`, `/api/token/refresh`), email as username, permissions embedded in tokens. API docs at `/swagger/` and `/redoc/`. Settings in `backend/config/settings.py`, driven by `.env`.

### Frontend — feature slices

Each feature lives in `frontend/src/models/<feature>/` with: `api.ts` (RTK Query endpoints), `schema.ts` (Zod schemas), `slice.ts` (Redux slice), `pages/`, `components/`. Existing features: `auth`, `user`, `roles-permissions`, `common`. Demo feature slices were removed.

Cross-cutting files the generator also updates (touch carefully — they must stay parseable by the generator):
- `src/redux/store.ts` — store registration
- `src/App.tsx` — routes
- `src/models/auth/permissions/constants.ts` and `src/hooks/use-permissions.tsx` — permission codes
- `src/components/sidebar/components/menu-groups/*` — sidebar menus

State: Redux Toolkit + RTK Query (server state) and Zustand. UI: shadcn/ui (Radix) + Tailwind. Police: **Poppins** (auto-hébergée via `@fontsource/poppins`, `font-sans` dans `tailwind.config.js`) — ne pas redéfinir `font-family` ailleurs ; pas de couleurs en dur (utiliser les variables de thème : `bg-muted`, `text-destructive`…). Forms: React Hook Form + Zod. i18n: i18next.

## Conventions

Detailed conventions in `00conventions/` (Django, React, Git). Key points:
- Python: PEP 8, snake_case fields/functions, PascalCase models/serializers (`XxxSerializer`, `XxxViewSet`), docstrings in French
- React: PascalCase components, kebab-case file/folder names (`user-profile.tsx`), hooks prefixed `use`, handlers prefixed `handle`
- URLs: kebab-case
