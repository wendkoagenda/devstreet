# 05 — Examiner les contributions

**Statut : à réaliser.** Espace du mainteneur pour lire et décider, sans score automatique.

## À regrouper

Liste paginée des propositions du projet ; panneau de lecture montrant auteur, tâche, résumé, lien PR/SHA et critères ; formulaire de décision avec motif obligatoire. Le contexte de la tâche reste visible pendant la revue.

| Route | Intégration |
| --- | --- |
| GET /api/v1/contributions?project_id={id} | Propositions autorisées pour le mainteneur ; filtrage serveur |
| GET /api/v1/contributions/{id} | Détail de la proposition |
| GET /api/v1/contribution-tasks/{task_id} | Rappeler les critères attendus |
| GET /api/v1/projects/{project_id}/repository | Construire la transition vers la PR native dans la forge |
| POST /api/v1/contributions/{id}/review | `status: accepted/rejected`, `note` obligatoire |

## UX proposée

Une lecture « proposition à gauche, critères à droite » sur écran large ; empilement sur mobile. Actions « Accepter la réalisation » et « Refuser avec explication ». Aucun bouton « Fusionner » dans cette interface : la route ne réalise pas de merge Git. Une décision déjà prise est présentée en lecture seule.

L’étiquette exacte est « Relu et accepté par… » avec date et motif. Ne pas remplacer par « Développeur certifié ». L’auteur de la proposition ne voit pas d’action d’auto-revue, même s’il est propriétaire du projet.

## Terminé lorsque

Une proposition inaccessible n’apparaît pas ; le motif vide est refusé ; la double décision donne un conflit compréhensible ; l’acceptation rend la réalisation consultable dans le profil et sélectionnable par son auteur.
