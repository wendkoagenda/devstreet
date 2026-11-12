# 03 — Fiche projet

**Statut : partiellement livré.** Fiche commune aux visiteurs, contributeurs et mainteneurs, avec actions selon les droits. L’explorateur de fichiers **dans** DevStreet est l’**étape 2** (à venir) ; les PR / diffs / merge sont une étape ultérieure.

## À regrouper

En-tête : nom, problème résolu, technologies, étoiles et démo. Puis onglets **Présentation · Code · Contribuer · Équipe**. Le visiteur comprend d’abord l’utilité ; le contributeur trouve ensuite une tâche. Le propriétaire dispose d’un menu de gestion discret.

| Route | Intégration |
| --- | --- |
| GET /api/v1/projects/{id} | Source de vérité de la fiche et des états |
| PATCH /api/v1/projects/{id} | Modifier la présentation pour propriétaire/mainteneur avec IAM |
| GET /api/v1/projects/{id}/repository | Métadonnées + URL de clone ; `is_empty` / `current_sha` pour l’état du dépôt |
| GET /api/v1/projects/{id}/tasks | Onglet Contribuer paginé ; clic → écran 04 |
| GET /api/v1/projects/{id}/members | Équipe, paginée |
| POST /api/v1/projects/{id}/members | Propriétaire : attribuer un rôle métier à un ID utilisateur existant |
| DELETE /api/v1/projects/{id}/members/{user_id} | Propriétaire : retirer une appartenance ; ne pas retirer le propriétaire |
| PUT /api/v1/projects/{id}/star ; DELETE même route | Étoiles |
| POST /api/v1/projects/{id}/publish ; /archive | Propriétaire : transitions confirmées par le serveur |
| POST /api/v1/projects/{id}/tasks | Créer une tâche manuelle brouillon |

## UX proposée

Le bouton « Préparer une contribution avec l’IA » mène à l’écran 06 ; « Examiner les propositions » à l’écran 05. L’onglet **Code** affiche pour l’instant l’état du dépôt et les commandes de clone/push dans DevStreet (pas d’iframe Gitea). L’explorateur de fichiers / branches / README live sera ajouté en **étape 2**, toujours via Django → Gitea (droits contrôlés, sans jeton admin navigateur). Les interfaces PR / diff / merge ne doivent **pas** être annoncées avant leur livraison.

L’ajout d’un membre par nom requiert un sélecteur du compte commun ; `/api/v1/users` est soumis aux permissions IAM et ne doit pas être rendu public par le frontend. Tant qu’un annuaire public n’existe pas, accepter un ID utilisateur communiqué par le membre.

Ne pas confondre rôle de mainteneur métier et droit de push Git. Confirmer l’archivage avec son effet sur la visibilité et les preuves de candidature. Le propriétaire conserve l’accès à son projet archivé. Les blobs et commits restent la vérité Gitea : **pas de copie** dans les tables Django.

## Terminé lorsque

Les onglets gardent le même projet ; aucun formulaire ne permet de changer owner/status directement ; les listes sont paginées ; les mutations refusées sont expliquées ; les tâches manuelles restent disponibles sans IA ; aucune redirection forcée vers l’UI Gitea.
