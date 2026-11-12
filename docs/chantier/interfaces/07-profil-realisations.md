# 07 — Projets et réalisations du profil commun

**Statut : à réaliser.** Extension du profil existant, sans seconde page d’identité ou gestion IAM.

## À regrouper

Sections « Projets publiés » et « Contributions acceptées », avec le problème du projet, le rôle déclaré, le travail proposé, le relecteur et la date. Les étoiles restent un indicateur social séparé.

| Route / contrat | Intégration |
| --- | --- |
| GET /api/v1/project-profiles/{user_id} | Aperçu public des 20 dernières entrées par section |
| GET /api/v1/projects?owner={id}&page= | Liste longue des projets ; respect des droits du lecteur |
| GET /api/v1/contributions?author_id={id}&page= | Liste longue des contributions visibles ; ne pas qualifier une soumission en attente comme acceptée |
| GET /api/v1/project-evidence/{contribution_id} | Dans le formulaire de candidature de la marketplace : vérifier que la réalisation est publique, acceptée et appartient au candidat connecté |

## UX proposée

Une carte raconte une réalisation : « Moussa a proposé l’export CSV du projet Stock, relu par Aïcha ». Afficher le lien vers la tâche et la contribution. Le choix d’une preuve se fait dans l’interface de candidature de la marketplace ; ne pas ajouter de bouton qui envoie automatiquement une candidature depuis le profil.

La marketplace conservera sa liaison et recontrôlera l’admissibilité à l’affichage. Si la source est retirée, remplacer le contenu valorisant par « réalisation indisponible ». Aucun classement automatique des personnes.

## Terminé lorsque

Le profil conserve son identité et ses permissions existantes ; seuls les résultats autorisés sont montrés ; la distinction proposé/accepté est lisible ; la réalisation d’autrui ne peut être sélectionnée pour une candidature ; la limite de l’aperçu et l’accès aux pages suivantes sont explicites.
