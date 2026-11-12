# 01 — Explorer les projets

**Statut : à réaliser.** Visiteur ou développeur cherchant un projet à découvrir ou une occasion de contribuer.

## À regrouper sur cet écran

Recherche par besoin, filtre par technologie, cartes projets, nombre d’étoiles et accès à la fiche. Une carte montre problème résolu, technologies et état ; pas le README entier. Le titre de la page porte une invitation concrète : « Sur quoi veux-tu construire avec d’autres ? ».

| Route | Intégration |
| --- | --- |
| GET /api/v1/projects?search=&technology=&page= | Charger la page de cartes ; la liste inclut aussi les projets privés du membre lorsqu’il y a droit : les identifier visuellement comme brouillons |
| GET /api/v1/technologies | Alimenter le filtre avec le catalogue réel ; parcourir ses pages si nécessaire |
| PUT /api/v1/projects/{id}/star | Étoiler après contrôle de session/permission ; utiliser le total retourné |
| DELETE /api/v1/projects/{id}/star | Retirer l’étoile ; même total serveur faisant foi |
| GET /api/auth/me | Connaître la session et les permissions via le socle existant |

## UX proposée

Recherche temporisée, filtres visibles et effaçables, cartes légères en une colonne sur mobile. Différencier « découvrir » et « contribuer » par la présentation du besoin du projet, sans annoncer un filtre serveur de tâches ouvertes qui n’existe pas. Clic sur carte → écran 03 ; « Créer un projet » → écran 02. Le nombre d’étoiles est public ; le serveur ne fournit pas encore l’état personnel de l’étoile dans chaque carte : conserver l’état des actions de la session ou ajouter ce champ lors de l’étape UI.

## Terminé lorsque

Recherche/filtres survivent au rechargement ; pagination réelle ; aucun brouillon inaccessible visible ; double clic ne double pas les étoiles ; visiteur invité à utiliser l’auth existante avant une mutation ; état vide donne une action utile.
