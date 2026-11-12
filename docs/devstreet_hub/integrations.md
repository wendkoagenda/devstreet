# Contrats entre les apps

## Identité et IAM

Source de vérité : `app.core.User`, `Role`, `Permission`, `user.has_permission`. Authentification par `CookieJWTAuthentication` et endpoints existants `/api/auth/*`. Les cookies HttpOnly conservent les règles CSRF de la boilerplate ; Swagger et Postman peuvent utiliser Bearer. Aucun endpoint d’inscription/connexion ni modèle IAM ajouté par DevStreet Hub.

`init_devstreet_hub` enregistre les permissions métier et le rôle DevStreet Hub Developer ; une personne autorisée lui attribue ce rôle dans l’IAM existant. Posséder une permission globale n’accorde pas l’accès à tous les projets : le propriétaire ou le rôle local de mainteneur reste requis selon l’action.

## Forum — à raccorder par le membre responsable

Déclarer le chemin importable de sa fonction :

```dotenv
DEVSTREET_HUB_FORUM_ADAPTER=app.forum.services.project_topics.create_linked_topic
```

Signature à implémenter dans l’app forum :

```python
def create_linked_topic(*, actor, project, task, title, body, request_key):
    """Vérifie les droits forum et retourne l'ID stable d'un sujet existant ou créé."""
```

`task` est optionnelle et appartient obligatoirement au projet. `request_key` doit aussi être unique dans le forum : si le traitement réussit mais que la réponse est perdue, le même appel doit retourner le même sujet. Le forum reste propriétaire des réponses, de la modération et de ses règles d’accès. Le texte est une proposition humaine à publier, jamais une instruction IA à exécuter.

DevStreet Hub conserve le lien, pas une copie des messages. Sans adaptateur configuré, la route répond 503 et aucun faux sujet n’est créé. Un adaptateur de test est utilisé uniquement dans les tests unitaires ; il ne remplace pas l’app forum.

## Marketplace — à raccorder par le membre responsable

Utiliser ces services Python :

```python
from app.devstreet_hub.services.integration_service import (
    selectable_evidence,
    validate_application_evidence,
)
```

`selectable_evidence(actor)` fournit les contributions publiques et acceptées dont l’acteur est l’auteur. `validate_application_evidence(actor, contribution_id)` retourne la contribution admissible ou 404.

La marketplace doit vérifier séparément que la candidature appartient à `actor`, puis conserver sa propre liaison `ApplicationEvidence`. À chaque affichage, vérifier que la référence reste publique et acceptée. Si le projet est archivé ou retiré, afficher « réalisation indisponible » ; ne pas conserver un badge « valide » immuable.

Pour un client HTTP, `GET /api/v1/project-evidence/{id}` réalise la vérification d’admissibilité de la contribution pour l’utilisateur connecté. Aucun endpoint de candidature n’est créé dans DevStreet Hub.

## Profil commun

`GET /api/v1/project-profiles/{user_id}` retourne les 20 derniers projets publiés et les 20 dernières contributions acceptées publiques. `limit: 20` est explicite. Utiliser les listes paginées `/projects?owner={id}` et `/contributions?author_id={id}` pour les listes longues ; ces routes continuent d’appliquer les droits de visibilité de la personne qui consulte.

## Droits Git distincts des rôles métier

`ForgeIdentity` est un pointeur technique vers le compte de forge. Les droits de push sont ceux de Gitea. Ajouter un mainteneur dans Django permet la gestion de contenu et la revue, sans lui accorder silencieusement un accès Git. L’ouverture d’une PR et l’attribution de droits Git avancés passent par la forge pour ce MVP.

## Provisionnement d’identité Gitea

Gitea ne fournit ni clé d’idempotence ni champ personnalisé à la création d’utilisateur (`POST /admin/users`). Le login dérivé de l’ID Django (`devstreet-user-{pk}`) est abandonné : il collisionne dès qu’une forge est partagée ou qu’un compte historique réutilise le même motif.

Mécanisme retenu :

1. Réserver localement une `ForgeIdentity` en statut `pending` avec un `provisioning_key` (UUID) et un login opaque `ds-{instance}-{12 hex}` (`DEVSTREET_HUB_INSTANCE_ID` ou empreinte de `SECRET_KEY`).
2. Créer le compte distant, puis écrire la preuve `devstreet-hub:pk=<uuid>` dans `description` via `PATCH /admin/users/{username}` (seul champ admin durable sans authentification externe).
3. Confirmer la liaison (`gitea_user_id`, statut `linked`) uniquement si la preuve correspond. Login ou e-mail seuls ne suffisent jamais à adopter un compte préexistant.
4. Réutilisation : résolution par `gitea_user_id` (`GET /users/search?uid=`). Compte manquant ou identité divergente → statut `conflict`, réparation administrative.
5. Reprise après timeout / échec Django : même login et même clé ; si le compte distant porte déjà la preuve, liaison sans doublon et réémission explicite d’un secret (`password_recovery_required`), jamais de reset silencieux d’un compte tiers.

Le secret initial n’est jamais journalisé ni stocké en base. `POST /api/v1/forge-access` le renvoie au plus une fois par création ou reprise contrôlée.
