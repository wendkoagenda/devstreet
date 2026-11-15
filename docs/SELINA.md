# Selina

Assistante IA globale DevStreet (dock Sidekick) et mentions forum `@selina`.

## Surfaces

- **Topbar** : bouton sparkles (ouvre le dock) ; recherche via icône / Ctrl+K (dialog, pas Selina).
- **Fil (`/`)** : colonne droite style feed (recherche sticky + suggestions) — plus de barre « Demander à Selina… » sous le titre.
- **Toolbar bas** : pill flottante sur toutes les pages authentifiées (masquée quand le dock est ouvert).
- **Dock droit** : panel Sidekick (`role="complementary"`), **sans overlay modal** ; le contenu se décale (`lg:pr-[400px]`). Esc ferme.
- **Ctrl+K** reste la recherche globale — surface séparée.

## API

- `POST /api/v1/ai/conversations` avec `consumer: "selina"`
- `GET /api/v1/ai/conversations?consumer=selina`
- Permission : `ai.chat`

## Forum `@selina`

Réponse enfant dans le fil (badge IA). N’ouvre pas le dock.
