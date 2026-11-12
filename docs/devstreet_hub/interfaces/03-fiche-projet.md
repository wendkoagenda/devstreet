# 03 — Fiche projet

**Statut : livré** pour la fiche et l’onglet **Code** (exploration / lecture). Les PR / diffs / merge restent une étape ultérieure.

## À regrouper

En-tête : nom, problème résolu, technologies, étoiles et démo. Puis onglets **Présentation · Code · Contribuer · Équipe**. Le visiteur comprend d’abord l’utilité ; le contributeur trouve ensuite une tâche. Le propriétaire dispose d’un menu de gestion discret.

| Route | Intégration |
| --- | --- |
| GET /api/v1/projects/{id} | Source de vérité de la fiche et des états |
| PATCH /api/v1/projects/{id} | Modifier la présentation pour propriétaire/mainteneur avec IAM |
| GET /api/v1/projects/{id}/repository | Métadonnées + URL de clone ; `is_empty` / `current_sha` pour l’état du dépôt |
| GET /api/v1/projects/{id}/code/summary | Résumé dépôt (branche, stats, langues, clone) via Django → Gitea |
| GET /api/v1/projects/{id}/code/branches | Liste des branches |
| GET /api/v1/projects/{id}/code/tree?ref=&path= | Arborescence + bandeau commit + README |
| GET /api/v1/projects/{id}/code/blob?ref=&path= | Contenu fichier (texte, limites taille/binaire) |
| GET /api/v1/projects/{id}/tasks | Onglet Contribuer paginé ; clic → écran 04 |
| GET /api/v1/projects/{id}/members | Équipe, paginée |
| POST /api/v1/projects/{id}/members | Propriétaire : attribuer un rôle métier à un ID utilisateur existant |
| DELETE /api/v1/projects/{id}/members/{user_id} | Propriétaire : retirer une appartenance ; ne pas retirer le propriétaire |
| PUT /api/v1/projects/{id}/star ; DELETE même route | Étoiles DevStreet (seule source de vérité « favoris ») |
| POST /api/v1/projects/{id}/publish ; /archive | Propriétaire : transitions confirmées par le serveur |
| POST /api/v1/projects/{id}/tasks | Créer une tâche manuelle brouillon |

## UX proposée

Le bouton « Préparer une contribution avec l’IA » mène à l’écran 06 ; « Examiner les propositions » à l’écran 05. L’onglet **Code** est **interne à DevStreet** : explorateur de fichiers, sélecteur de branche, fil d’Ariane, lecteur de fichiers (numéros de ligne, HTML affiché comme texte), menu de copie d’URL de clone, README Markdown sécurisé, description et langages. L’en-tête de fiche affiche les **langues détectées** du dépôt (plus les tags manuels type Go/Django choisis à la création). Aucune redirection vers l’UI Gitea, aucun iframe. Les paramètres `tab`, `ref`, `path` et `mode` restent dans l’URL (branches avec slashs via `ref`). Les interfaces PR / diff / merge ne doivent **pas** être annoncées avant leur livraison.

L’ajout d’un membre par nom requiert un sélecteur du compte commun ; `/api/v1/users` est soumis aux permissions IAM et ne doit pas être rendu public par le frontend. Tant qu’un annuaire public n’existe pas, accepter un ID utilisateur communiqué par le membre.

Ne pas confondre rôle de mainteneur métier et droit de push Git. Confirmer l’archivage avec son effet sur la visibilité et les preuves de candidature. Le propriétaire conserve l’accès à son projet archivé. Les blobs et commits restent la vérité Gitea : **pas de copie** dans les tables Django. Les métadonnées d’auteur Git ne créent pas de lien automatique vers un profil DevStreet.

## Terminé lorsque

Les onglets gardent le même projet ; aucun formulaire ne permet de changer owner/status directement ; les listes sont paginées ; les mutations refusées sont expliquées ; les tâches manuelles restent disponibles sans IA ; le parcours Code est consultable sans quitter DevStreet ; aucune redirection forcée vers l’UI Gitea.
