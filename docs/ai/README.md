# Assistant IA partagé (`app.ai`)

Service LLM réutilisable par DevStreet Hub, et plus tard Forum / Marketplace, sans réécrire le client fournisseurs.

## Principe

- **Grok (xAI)** en primaire, **OpenAI** en secours automatique (timeout, rate limit, 5xx, indisponibilité).
- Clés uniquement côté serveur (variables `AI_*` dans `backend/.env`).
- Permission IAM : `ai.chat`.
- Seed : `python manage.py init_ai` (aussi couvert via `init_devstreet_hub` pour le rôle Developer).

## API générique

Base : `/api/v1/ai/`

| Méthode | Route | Rôle |
|---------|-------|------|
| POST | `/conversations` | Crée une conversation `{ consumer, title? }` |
| GET | `/conversations/{id}` | Historique (propriétaire uniquement) |
| POST | `/conversations/{id}/messages` | `{ content, context_text? }` → réponse synchrone |

Réponse message : `assistant_message`, `provider` (`grok`\|`openai`), `failover_reason`, `conversation_id`.

## Appel depuis une autre app Django

```python
from app.ai.services.chat_service import ChatService

result = ChatService().chat(
    request.user,
    message="Résume ce fil",
    consumer="generic",  # ou un consumer dédié si ajouté
    context_text="…contexte métier…",
)
```

Ou HTTP : `POST /api/v1/ai/conversations` puis `…/messages` avec le JWT / cookies DevStreet.

## Façade Hub

`POST /api/v1/projects/{id}/assistant/chat`

```json
{
  "message": "Propose des critères",
  "conversation_id": null,
  "task_id": 3,
  "include_repo": true
}
```

Le Hub vérifie la visibilité du projet, assemble un contexte (projet / tâche / extraits Gitea bornés), puis délègue à `ChatService`.

## Configuration

Voir `backend/.env.example` (`AI_GROK_*`, `AI_OPENAI_*`, `AI_PRIMARY_PROVIDER`, `AI_DAILY_LIMIT`).

- Grok seul → OK.
- OpenAI seul → OK (si Grok absent).
- Aucun → 503.

## Hors V1

Streaming, migration de l’atelier analyses Hub (`openai_client.py`), RAG vectoriel, consumers forum/marketplace dédiés.
