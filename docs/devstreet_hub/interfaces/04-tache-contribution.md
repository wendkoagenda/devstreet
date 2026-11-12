# 04 — Comprendre une tâche et proposer son travail

**Statut : à réaliser.** Moussa doit comprendre quoi faire et comment proposer son résultat.

## À regrouper

Titre et objectif, consignes, liste des critères de réussite, sources du contexte lorsque la tâche vient de l’IA, lien vers le dépôt, demande d’aide et formulaire de proposition.

| Route | Intégration |
| --- | --- |
| GET /api/v1/contribution-tasks/{id} | Tâche ; `source_references` correspond au contexte de la proposition, pas à une validation du code |
| GET /api/v1/projects/{project_id} | Contexte et dépôt du projet |
| POST /api/v1/contribution-tasks/{id}/contributions | Résumé, numéro de PR optionnel, SHA optionnel ; aucun champ de décision envoyé par l’auteur |
| POST /api/v1/projects/{project_id}/discussions | Sujet réel via adaptateur forum ; envoyer task_id, titre, corps et UUID request_key |
| PATCH /api/v1/contribution-tasks/{id} | Mainteneur : modifier consignes/critères, ouvrir ou fermer la tâche |
| GET /api/v1/contributions?task_id={id} | Propositions visibles selon l’utilisateur et les règles métier |

## UX proposée

Un panneau « Ta première étape » met en évidence le point d’entrée décrit par la tâche. Une checklist affiche les critères sans les marquer automatiquement réussis. Les sources s’ouvrent sur le SHA de l’analyse ; préciser que le dépôt peut avoir évolué depuis.

« Demander de l’aide » ouvre un brouillon modifiable, puis publie après une action explicite. Réutiliser le même request_key en cas de timeout ; en cas de 503 forum, garder le brouillon local en mémoire et expliquer que le raccordement manque. Ne pas afficher une discussion inexistante.

« Proposer mon travail » explique qu’une revue reste nécessaire et qu’un numéro de PR sera vérifié dans le dépôt lié. Sans PR, la réalisation reste une déclaration soumise à la revue du mainteneur. L’auteur ne peut pas s’auto-accepter.

## Terminé lorsque

Moussa identifie le résultat attendu ; les références sont consultables ; le formulaire ne fabrique ni fusion ni validation ; la fermeture de la tâche bloque les nouvelles soumissions ; le forum dégradé ne masque pas la tâche.
