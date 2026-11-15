# Communauté — étude préalable

Statut : document de travail historique. Le PRD consolidé est désormais [PRD.md](PRD.md). Source initiale : brief « DevStreet — PRD du module Communauté », 12 novembre 2026.

## Intention produit

Permettre à un membre de publier une discussion, de faire essayer une application ou de demander de l'aide. Les autres membres peuvent contribuer publiquement ; l'auteur peut signaler la réponse technique ou l'option qui a finalement été retenue. Une conversation privée peut prolonger un échange entre deux comptes.

## Décisions et éléments déjà établis

- Le module sera une **application Django `communaute` distincte**. Il réutilisera les comptes existants et pourra référencer un projet existant.
- `core.User` gère déjà les comptes, les rôles et les permissions. `devstreet_hub.Project` existe déjà ; il n'y a pas lieu de recréer ces deux modèles.
- L'architecture du dépôt sépare vues, services et repositories. Les conventions Django demandent des classes au singulier en PascalCase et des champs en snake_case.
- La première étape est le cadrage en Markdown. Aucun code métier, migration ou endpoint Communauté n'est engagé à ce stade.

## Parcours à préciser avant de figer le PRD

| Sujet | Proposition de travail | Décision attendue |
| --- | --- | --- |
| Fil | Publications chronologiques, paginées ; cinq types : discussion, application, entraide technique, aide au choix et sondage. | Déterminer si le fil et les détails sont visibles sans connexion. |
| Essayer une app | Le créateur publie un lien HTTP(S) ; l'essai a lieu sur le site externe ou la page mobile indiquée. | Clarifier ce que signifie « lien mobile » : page web, boutique, lien profond ? |
| Entraide technique | Une demande reçoit des réponses dédiées ; l'auteur peut en accepter une et les membres peuvent confirmer son utilité. | Clarifier si une réponse technique peut aussi recevoir des commentaires imbriqués. |
| Aide au choix | Au moins deux options, un avis argumenté par membre, puis décision de l'auteur. | Préciser si l'auteur peut voter et si la décision finale peut être corrigée. |
| Sondage | Une publication dans le fil général, une communauté ou une chaîne, avec au moins deux options et un vote unique ou multiple. « Répondre » signifie choisir une ou plusieurs options ; le membre peut s'abstenir. L'auteur vote selon les mêmes règles que les autres. Les options sont figées après le premier vote. Chacun peut modifier ou retirer son vote avant la fermeture ; l'auteur peut fermer les votes. Les résultats sont visibles après avoir voté ou après fermeture, sous forme de nombres sans identité des votants. | Règles principales décidées ; préciser les limites de longueur et de nombre d'options avant implémentation. |
| Retour anonyme | L'auteur reste connu du serveur, mais jamais exposé par l'API publique, même au créateur de l'app. | Décider si le membre peut modifier ou supprimer son propre retour. |
| Messages privés | Une conversation relie directement deux membres, indépendamment de toute publication. Une conversation par paire, texte seul, actualisation au rafraîchissement. | Confirmer que ce parcours est indispensable à la première démo compte tenu du volume P0. |
| Communautés | Espaces créés par un membre, publics ou accessibles par lien selon son choix, avec adhésion, administrateurs et règle de publication configurable : tous les membres ou administrateurs seulement. | Définir les rôles et le retrait des membres. |
| Chaînes | Espaces indépendants des communautés, publics ou accessibles par lien ; on s'y abonne et seuls les administrateurs publient. Les commentaires sont réglables, les likes possibles. | Définir qui peut administrer une chaîne. |
| Abonnement à un membre | Un membre peut suivre un autre membre ; ses nouvelles publications visibles arrivent dans un fil « Abonnements ». | Définir les restrictions éventuelles du suivi. |
| Notifications | Les nouvelles publications des chaînes et membres suivis donnent lieu à un résumé quotidien dans l'application. | Préciser l'heure de génération et les règles pour éviter les doublons. |
| Profil public | Le PRD demande pseudo et avatar ; `core.User` contient `username`, nom et prénom, mais pas d'avatar. | Utiliser les champs existants ou prévoir une évolution du profil commun. |
| Projet lié | Une publication peut référencer `Project`. `ProjectDiscussionLink` attend par ailleurs un identifiant de sujet de forum. | Définir la correspondance entre une publication Communauté et ce contrat existant. |

## Périmètre proposé pour la première démonstration

Le PRD classe déjà onze parcours en P0. L'ordre de travail proposé, sans changer leur priorité, est :

1. Publication, images et fil.
2. Commentaires, réponses aux commentaires et likes.
3. Application partagée et retour public ou anonyme.
4. Demande technique, réponse acceptée et confirmation d'aide.
5. Aide au choix, avis argumenté et décision finale.
6. Conversation privée à deux.

Dans le PRD initial, la recherche et les filtres sont en P1, tandis que le suivi et les notifications sont en P2. Les nouvelles décisions sur le suivi et le résumé quotidien demandent de **revoir leur priorité** avant de figer le MVP. L'IA n'est pas prévue pour le MVP.

Les communautés, les chaînes, les sondages, l'abonnement à un membre et les notifications sont des ajouts au PRD fourni. Ils seront abordés **par étapes**, après le socle des publications et échanges. Voir [ESPACES_ET_ABONNEMENTS.md](ESPACES_ET_ABONNEMENTS.md) et la [roadmap](../PLAN.md).

### Étapes de travail proposées

| Étape | Parcours livrable | Dépendance |
| --- | --- | --- |
| 1 — Socle Communauté | Fil général, publications, interactions, applications partagées, entraide technique, aide au choix et conversations privées. | Comptes existants. |
| 2 — Espaces | Création des communautés et chaînes, adhésion ou abonnement, liens d'accès, rôles et publications dans un espace. | Publications et contrôle des droits de l'étape 1. |
| 3 — Suivis et nouveautés | Suivi d'utilisateurs, fil « Abonnements » et résumé quotidien dans l'application. | Publications et espaces des étapes précédentes. |

Ces trois étapes donnent la vue d'ensemble. La [roadmap détaillée](../PLAN.md) les découpe en 15 tranches démontrables avec critères d'acceptation et dépendances. Aucun délai n'est engagé.

## Points à préserver dans les contrats futurs

- Un parent de commentaire appartient à la même publication.
- Une réponse acceptée appartient à la demande technique concernée ; une option votée ou retenue appartient à la demande d'aide au choix concernée.
- Un seul like, avis ou confirmation par membre et par cible correspondante.
- La décision finale ferme les nouveaux avis, mais laisse les commentaires ouverts.
- Un tiers ne peut ni lire ni écrire dans une conversation privée ; l'auteur d'un message en est membre.
- Les données d'identité d'un retour anonyme ne figurent dans aucune réponse API publique, y compris dans les objets imbriqués.
- Les règles qui concernent plusieurs lignes doivent être contrôlées dans le service métier, dans une transaction lorsque nécessaire ; la simple relation entre tables ne suffit pas.

## Prochaine étape de cadrage

Les décisions encore ouvertes sont listées dans [PRD.md](PRD.md). La [roadmap détaillée](../PLAN.md) reste la base d'exécution. Le diagramme dans `MODELE_PROPOSE.md` détaille le schéma de travail.
