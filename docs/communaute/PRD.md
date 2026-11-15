# PRD : module Communauté DevStreet

15 novembre 2026 · Consolidé depuis le brief du 12 novembre 2026, l’étude préalable, le cadrage espaces/abonnements et la roadmap `docs/PLAN.md`.

## Contexte et objectif

DevStreet réunit trois espaces : la **communauté** (échanges entre membres), la **marketplace** (missions et talents) et le **partage de code / projets**. La communauté est le lieu où un membre publie une discussion, fait essayer une application, demande de l’aide technique, propose un choix, lance un sondage, ou échange en privé.

**Objectif** : permettre aux développeurs de s’entraider publiquement, de construire une présence visible, et de prolonger les échanges utiles (communautés, chaînes, suivis, messagerie), sans dépendre d’outils externes dispersés.

**Différenciateur** : les publications ne sont pas un simple fil de posts. Cinq types structurés (discussion, application, entraide technique, aide au choix, sondage) portent des règles métier propres (réponse acceptée, retour anonyme, option retenue, vote). Les espaces (communauté / chaîne) et les abonnements organisent la découverte sans remplacer le fil général.

## Personas

| Persona | Profil | Besoin principal | Frein actuel |
| --- | --- | --- | --- |
| Awa, dév freelance | 26 ans, Abidjan, React/Node | Partager des questions, faire tester une app, trouver des réponses utiles | Forums génériques bruyants, feedback non structuré |
| Ibrahim, dév junior | 22 ans, Ouagadougou, sorti de formation | Poser des questions techniques et apprendre des réponses acceptées | Peur de poster « mal », réponses noyées dans les commentaires |
| Mariam, lead technique | 32 ans, Dakar, anime une communauté locale | Créer un espace, gérer qui publie, inviter par lien | Groupes WhatsApp / Discord sans historique structuré |
| Kofi, créateur de contenu tech | 29 ans, Accra, publie des nouveautés | Animer une chaîne où seuls les admins publient | Newsletters et réseaux sociaux non liés au profil DevStreet |
| Fatou, recruteuse (lecteur occasionnel) | RH fintech, Dakar | Comprendre la réputation d’un dév via ses contributions | Contributions dispersées hors DevStreet |

## Cas d’utilisation

Priorité : **P0** = indispensable au socle démontrable ; **P1** = si le temps le permet ; **P2** = après le concours / plus tard.

| ID | En tant que | Je veux | Afin de | Priorité |
| --- | --- | --- | --- | --- |
| UC-01 | Membre | Lire le fil et publier une discussion avec images | Partager une idée ou un sujet | P0 |
| UC-02 | Membre | Commenter, répondre à un commentaire et liker | Contribuer à une discussion | P0 |
| UC-03 | Créateur d’app | Partager une application avec un lien d’essai | Recevoir des retours publics ou anonymes | P0 |
| UC-04 | Membre | Poser une question technique et recevoir des réponses dédiées | Débloquer un problème concret | P0 |
| UC-05 | Auteur d’une question technique | Accepter une réponse et laisser confirmer « Ça m’a aidé aussi » | Mettre en avant la solution utile | P0 |
| UC-06 | Membre | Proposer un choix (≥ 2 options), recueillir des avis argumentés et publier la décision | Trancher avec l’aide de la communauté | P0 |
| UC-07 | Membre | Échanger en privé (texte) avec un autre membre | Continuer un échange hors fil public | P0 |
| UC-08 | Membre autorisé | Relier une publication à un projet existant | Contexte projet visible des deux côtés | P1 |
| UC-09 | Membre | Créer et rejoindre une communauté publique | Discuter dans un espace thématique | P0 |
| UC-10 | Administrateur | Inviter par lien (avec ou sans prévisualisation) et révoquer le lien | Contrôler l’accès sans ouvrir l’espace à tous | P0 |
| UC-11 | Super administrateur | Nommer des admins et régler qui peut publier | Modérer l’espace sans perdre la propriété | P0 |
| UC-12 | Membre | Créer une chaîne publique et s’y abonner | Recevoir des nouveautés sans publier soi-même | P0 |
| UC-13 | Créateur de chaîne | Choisir accès public ou lien, ouvrir/fermer les commentaires | Animer un canal de diffusion | P1 |
| UC-14 | Membre | Suivre un autre membre et consulter le fil « Abonnements » | Voir les nouveautés des personnes et chaînes suivies | P1 |
| UC-15 | Membre | Recevoir un résumé quotidien dans l’application | Ne pas rater les nouveautés | P2 |
| UC-16 | Membre | Filtrer et rechercher des publications par type / mots | Retrouver un sujet rapidement | P1 |
| UC-17 | Membre autorisé | Créer un sondage (choix unique ou multiple) et voter | Recueillir une opinion mesurable | P1 |

## Périmètre MVP

### Livré (socle + espaces essentiels)

- Fil général paginé, cinq types de publication (discussion, application, entraide, aide au choix, sondage selon priorité).
- Images sur publication, commentaires imbriqués, likes publication/commentaire.
- Application partagée : lien HTTP(S), retours signés ou anonymes (identité jamais exposée en API publique).
- Entraide technique : réponses dédiées, acceptation, confirmations d’aide.
- Aide au choix : options, avis argumentés, décision finale de l’auteur.
- Messagerie privée à deux (une conversation par paire).
- Espaces `COMMUNAUTE` et `CHAINE` : création, adhésion/abonnement, rôles, liens d’invitation, publications dans un espace.
- Droits serveur : lecture, publication, commentaires, likes selon espace et rôle.

### Non livré (hors MVP / P2+)

- Intelligence artificielle (génération, modération, recommandation).
- Notifications e-mail pour les nouveautés communauté (le résumé est in-app).
- Temps réel obligatoire pour la messagerie (Socket.IO peut exister en plus du rafraîchissement ; le critère MVP est la persistance consultable).
- Paiement, marketplace, administration marketplace.
- Second forum parallèle au Hub : on raccroche `ProjectDiscussionLink`, on ne le duplique pas.
- Blocage / signalement avancé (hors périmètre jusqu’à décision produit).
- Publication dans **plusieurs** espaces à la fois (une publication ≤ un espace ; à trancher avant d’étendre).

## Rôle de l’IA

**Aucune IA dans le MVP Communauté.**

| Zone | Intervention IA | Entrées | Sorties |
| --- | --- | --- | --- |
| Fil, espaces, messagerie, sondages | Non | — | — |
| Marketplace (hors ce PRD) | Oui (offre / matching) | Besoin en langage naturel, profils | Offre rédigée, suggestions |

Si une IA est ajoutée plus tard (ex. résumé de fil, suggestion de tags), elle fera l’objet d’un avenant à ce PRD.

## Modèle de données et API

### Principes

- App Django distincte `communaute` ; réutilise `core.User` et peut référencer `devstreet_hub.Project`.
- Couches : ViewSet → Service → Repository.
- Préfixe API : `/api/communaute/v1/` (routage projet).

### Modèles principaux

| Modèle | Rôle |
| --- | --- |
| `Publication` | Cinq types ; titre, texte, lien app, rattachement optionnel à un `Espace` / `Project` |
| `ImagePublication` | Images ordonnées |
| `Commentaire` | Commentaire, retour d’app, réponse technique ; parent optionnel |
| `OptionPublication` | Options d’aide au choix ou de sondage |
| `AvisChoix` / `VoteSondage` | Avis argumenté / sélection de sondage |
| `LikePublication` / `LikeCommentaire` / `ConfirmationAide` | Unicité par membre et cible |
| `Espace` | Communauté ou chaîne ; accès public ou par lien |
| `ParticipationEspace` | Membre / abonné ; rôles SUPER_ADMIN, ADMIN, MEMBRE |
| `LienInvitation` | Lien révocable ; prévisualisation oui/non |
| `SuiviUtilisateur` | Suivi libre d’un membre |
| `NotificationResume` | Résumé quotidien in-app |
| `Conversation` / `Message` | Messagerie privée à deux |
| `Tag` | Étiquetage (recherche / filtres) |

Détail des attributs : [MODELE_PROPOSE.md](MODELE_PROPOSE.md).

### Endpoints principaux (CRUD + actions métier)

| Ressource | Chemin (relatif à `/api/communaute/v1/`) | Usage |
| --- | --- | --- |
| Publications | `publications` | Fil, détail, création, mise à jour, suppression |
| Images | `images-publication` | Médias de publication |
| Commentaires | `commentaires` | Commentaires / retours / réponses techniques |
| Likes | `likes-publication`, `likes-commentaire` | Ajout / retrait |
| Confirmations d’aide | `confirmations-aide` | « Ça m’a aidé aussi » |
| Options / avis / votes | `options-publication`, `avis-choix`, `votes-sondage` | Choix et sondages |
| Espaces | `espaces` | Communautés et chaînes |
| Participations | `participations-espace` | Adhésion, rôles, départ |
| Liens | `liens-invitation` | Création / révocation / usage |
| Conversations / messages | `conversations`, `messages` | Messagerie privée |
| Suivis | `suivis-utilisateur`, `membres/.../suivre` | Suivre / liste |
| Profils membres | `membres/search`, `membres/<id>`, `membres/u/<username>` | Découverte |
| Résumé | `notifications-resume` | Résumé quotidien |
| Activité | `activity/badges` | Badges non lus (messagerie / espaces) |
| Tags | `tags` | Référentiel |

Les règles métier (unicité, anonymat, droits d’espace, fermeture des votes) sont **vérifiées côté serveur**, pas seulement à l’UI.

## Critères d’acceptation

Critères vérifiables (rechargement, API, droits). Alignés sur la roadmap détaillée dans `docs/PLAN.md`.

### Fil et interactions (UC-01, UC-02)

- Une discussion créée apparaît dans le fil et le détail après rechargement ; images optionnelles conservées dans l’ordre.
- Un commentaire et sa réponse restent visibles ; un parent d’une autre publication est refusé.
- Deux likes du même membre sur la même cible ne comptent qu’une fois ; le retrait met à jour le compteur.

### Application partagée (UC-03)

- « Essayer l’app » ouvre le lien HTTP(S) enregistré ; lien invalide refusé.
- Retour signé : auteur visible. Retour anonyme : libellé « Anonyme » ; **aucune** réponse API publique ne révèle l’identité, y compris dans les objets imbriqués.
- Pas de contact privé proposé depuis un retour anonyme ; réponses publiques et likes restent possibles.

### Entraide technique (UC-04, UC-05)

- Réponses techniques distinctes des commentaires ordinaires à l’affichage.
- Seul l’auteur accepte / change / retire la réponse acceptée ; cible hors publication refusée.
- Confirmation d’aide unique par membre et réponse, retirable.

### Aide au choix (UC-06)

- Moins de deux options refusées ; options figées après le premier avis.
- Au plus un avis par membre, modifiable avant décision.
- Seul l’auteur publie la décision ; ensuite nouveaux avis refusés, commentaires encore ouverts.

### Messagerie (UC-07)

- Une conversation unique par paire, messages persistants après rechargement.
- Un tiers ne peut ni lire ni écrire, même avec l’identifiant de conversation.
- Aucune dépendance obligatoire à une publication ou un espace.

### Projet lié (UC-08)

- Projet inexistant ou non visible : liaison refusée.
- Publication et projet se retrouvent mutuellement sans doublon de sujet.
- Compatible avec le contrat Hub `ProjectDiscussionLink`.

### Communautés et chaînes (UC-09 à UC-13)

- Créateur = super administrateur permanent ; non exclu / non rétrogradé.
- Double adhésion / abonnement : pas de doublon.
- Non-autorisé à publier : refus serveur (pas seulement UI).
- Lien actif + prévisualisation : lecture seule avant adhésion ; sans prévisualisation : adhésion obligatoire ; lien révoqué : plus d’accès.
- Chaîne : abonné lit et like, ne publie pas ; commentaires fermés = création refusée, likes conservés.

### Abonnements et résumé (UC-14, UC-15)

- Suivi libre, pas de suivi de soi-même, pas de doublon.
- Fil / résumé : uniquement contenus autorisés ; déduplication auteur + chaîne.
- Au plus un résumé par membre et journée ; état lu/non lu persisté.

### Recherche et sondages (UC-16, UC-17)

- Filtres par type ; recherche textuelle paginée avec les mêmes droits de lecture que le fil.
- Sondage ≥ 2 options ; options figées après premier vote ; modes UNIQUE / MULTIPLE ; résultats sans identité des votants ; fermeture des votes par l’auteur.

## Décisions ouvertes (à trancher avant extension)

1. Une publication peut-elle appartenir à plusieurs espaces ?
2. Transfert de propriété d’un espace : possible ou jamais ?
3. Qui peut nommer / retirer les admins secondaires et exclure un membre ?
4. Limites chiffrées (longueur texte, nombre d’options, images) pour sondages et publications.
5. Visibilité du fil / détail **sans** connexion.

## Références

- Étude : [ETUDE.md](ETUDE.md)
- Espaces et abonnements : [ESPACES_ET_ABONNEMENTS.md](ESPACES_ET_ABONNEMENTS.md)
- Modèle : [MODELE_PROPOSE.md](MODELE_PROPOSE.md)
- Roadmap d’exécution : [../PLAN.md](../PLAN.md)
