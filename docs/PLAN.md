# Plan : module Communauté DevStreet

> Sources : « DevStreet — PRD du module Communauté » fourni le 12 novembre 2026 ; [étude préalable](communaute/ETUDE.md), [espaces et abonnements](communaute/ESPACES_ET_ABONNEMENTS.md), [modèle de classes proposé](communaute/MODELE_PROPOSE.md). Statut : roadmap de travail validée dans son découpage ; les décisions ouvertes ci-dessous restent à trancher avant les phases concernées. Aucun code n'est engagé par ce plan.

## Décisions architecturales

- **Application** : une app Django `communaute` distincte, avec les couches vues, services et repositories du dépôt. Chaque phase livre un parcours complet dans l'interface, l'API et la persistance, avec vérification des critères.
- **Identité et projet** : réutiliser `core.User`, l'authentification et les droits existants. Une publication peut référencer `devstreet_hub.Project` ; aucun compte ni projet parallèle.
- **Modèle** : `Publication` porte les cinq types discussion, application, entraide technique, aide au choix et sondage. `Commentaire` porte les commentaires, retours d'app et réponses techniques. `OptionPublication` sert aux aides au choix et sondages ; `VoteSondage` enregistre les sélections. `Espace` porte les deux types indépendants communauté et chaîne. Les règles propres aux types sont vérifiées côté serveur.
- **Messagerie** : `Conversation` relie directement deux utilisateurs, sans relation obligatoire avec une publication ou un espace. Pas de temps réel dans le premier parcours.
- **Accès aux espaces** : le créateur choisit public ou par lien. Il reste super administrateur et ne peut être retiré. Un lien peut autoriser ou refuser la prévisualisation avant adhésion et peut être révoqué.
- **Publication dans un espace** : une publication peut rester dans le fil général. Le modèle propose au plus un espace par publication ; le partage vers plusieurs espaces doit être décidé avant la phase 8.
- **Abonnements** : le suivi d'un utilisateur est libre et ne donne aucun droit de lecture supplémentaire. Le fil « Abonnements » déduplique les publications accessibles. Le résumé quotidien est consultable dans l'application, sans e-mail.
- **Routes** : les nouvelles routes devront suivre la famille `/api/v1` et les conventions d'URL du dépôt. Leurs chemins précis seront figés dans le contrat API avant la première implémentation.
- **Frontières** : le contrat `ProjectDiscussionLink` de DevStreet Hub est à raccorder sans créer un second forum. La marketplace et les fonctions IA ne font pas partie de cette roadmap.

## User stories de référence

Le PRD fourni n'attribue pas d'identifiants à ses stories. Les codes suivants sont **provisoires** pour suivre leur couverture ; ils seront alignés sur le PRD consolidé.

| ID | Besoin utilisateur |
| --- | --- |
| US-01 | Lire le fil et publier une discussion avec images. |
| US-02 | Commenter, répondre et liker une publication ou un commentaire. |
| US-03 | Partager une application et recevoir un retour public ou anonyme. |
| US-04 | Poser une question technique et recevoir des réponses. |
| US-05 | Accepter une réponse technique et confirmer « Ça m'a aidé aussi ». |
| US-06 | Proposer un choix, recueillir des avis argumentés et annoncer la décision. |
| US-07 | Échanger en privé avec un autre membre. |
| US-08 | Relier une publication à un projet existant. |
| US-09 | Créer et rejoindre une communauté publique. |
| US-10 | Rejoindre par lien et prévisualiser si le lien le permet. |
| US-11 | Gérer les administrateurs et les droits de publication d'une communauté. |
| US-12 | Créer une chaîne publique et s'y abonner. |
| US-13 | Accéder à une chaîne par lien et régler les commentaires. |
| US-14 | Suivre un utilisateur et consulter un fil « Abonnements ». |
| US-15 | Recevoir un résumé quotidien dans l'application. |
| US-16 | Filtrer et rechercher des publications. |
| US-17 | Créer un sondage à choix unique ou multiple et voter. |

---

## Phase 1 : fil général et discussions

**User stories** : US-01.

### Ce qu'on livre

Un membre publie une discussion avec titre, texte et images facultatives ; elle apparaît dans un fil chronologique paginé et reste consultable après rechargement.

### Critères d'acceptation

- [ ] Une discussion créée par un membre connecté apparaît dans le fil et sa page de détail après rechargement.
- [ ] Titre, texte, auteur et ordre des images sont conservés ; une discussion sans image est acceptée.
- [ ] Le fil paginé ne répète pas une publication lorsque de nouvelles discussions sont ajoutées.

## Bloquée par

Aucune — les comptes et l'authentification existent déjà.

---

## Phase 2 : commentaires et likes

**User stories** : US-02.

### Ce qu'on livre

Les membres commentent une publication, répondent à un commentaire et ajoutent ou retirent leurs likes depuis le fil ou le détail.

### Critères d'acceptation

- [ ] Un commentaire et sa réponse restent visibles après rechargement ; un parent d'une autre publication est refusé.
- [ ] Deux likes du même membre sur une même publication ou un même commentaire ne comptent qu'une fois.
- [ ] Retirer un like met à jour le compteur affiché, y compris pour une réponse à un commentaire.

## Bloquée par

Phase 1.

---

## Phase 3 : applications partagées et retours

**User stories** : US-03.

### Ce qu'on livre

Un créateur publie une application avec un lien HTTP(S) ; un membre ouvre ce lien puis laisse un retour signé ou anonyme, auquel d'autres peuvent répondre.

### Critères d'acceptation

- [ ] Le bouton « Essayer l'app » ouvre le lien enregistré ; une application sans image est acceptée et un lien invalide est refusé.
- [ ] Un retour signé affiche son auteur. Un retour anonyme affiche « Anonyme » et aucune réponse API publique ne révèle son identifiant ou son profil, même dans les objets imbriqués.
- [ ] Un retour anonyme ne propose pas de contact privé avec son auteur ; il reste possible de lui répondre publiquement et de le liker.

## Bloquée par

Phases 1 et 2.

---

## Phase 4 : entraide technique

**User stories** : US-04, US-05.

### Ce qu'on livre

Un membre décrit un problème, reçoit des réponses techniques, accepte celle qui l'a aidé et permet aux autres de confirmer son utilité.

### Critères d'acceptation

- [ ] Une publication technique accepte du texte, du code dans le texte et des captures facultatives ; les réponses techniques restent distinctes des commentaires ordinaires à l'affichage.
- [ ] Seul l'auteur accepte, change ou retire la réponse acceptée ; une réponse d'une autre publication est refusée.
- [ ] « Ça m'a aidé aussi » est unique par membre et par réponse et peut être retiré.

## Bloquée par

Phases 1 et 2.

---

## Phase 5 : aide au choix

**User stories** : US-06.

### Ce qu'on livre

Un membre propose au moins deux options, reçoit un choix argumenté par participant, puis publie l'option retenue avec sa justification.

### Critères d'acceptation

- [ ] Moins de deux options sont refusées ; après le premier avis, les options ne changent plus.
- [ ] Chaque membre a au plus un avis et peut le modifier avant la décision ; une option d'une autre publication est refusée.
- [ ] Seul l'auteur publie la décision. Après celle-ci, les nouveaux avis sont refusés, les résultats et la justification restent visibles, et les commentaires restent ouverts.

## Bloquée par

Phases 1 et 2.

---

## Phase 6 : conversation privée

**User stories** : US-07.

### Ce qu'on livre

Deux membres ouvrent une conversation unique pour leur paire et échangent des messages texte consultables au rafraîchissement.

### Critères d'acceptation

- [ ] Les deux membres retrouvent la même conversation et ses messages après rechargement, quel que soit l'initiateur.
- [ ] Un troisième membre ne peut ni lire ni écrire dans la conversation, même avec son identifiant.
- [ ] Une conversation peut exister sans publication ni espace lié.

## Bloquée par

Aucune phase Communauté — les comptes existants suffisent.

---

## Phase 7 : publication liée à un projet

**User stories** : US-08.

### Ce qu'on livre

Un membre autorisé rattache une publication à un projet existant ; le lien est visible dans le détail de la publication et compatible avec le contrat de discussion de DevStreet Hub.

### Critères d'acceptation

- [ ] Un projet inexistant ou non visible pour l'acteur ne peut pas être lié.
- [ ] Le projet lié et la publication se retrouvent mutuellement sans dupliquer le sujet.
- [ ] Les appels répétés du contrat DevStreet Hub retrouvent le même identifiant de publication ; les droits sont vérifiés dans les deux modules.

## Bloquée par

Phase 1 et validation du raccordement avec `ProjectDiscussionLink`.

---

## Phase 8 : communauté publique

**User stories** : US-09.

### Ce qu'on livre

Un membre crée une communauté publique, en devient super administrateur, d'autres membres la rejoignent et les membres autorisés y publient.

### Critères d'acceptation

- [ ] Le créateur voit sa communauté et son rôle après rechargement ; une seconde adhésion du même membre ne crée pas de doublon.
- [ ] Les publications de la communauté apparaissent dans son espace ; le fil général continue de recevoir des publications sans espace.
- [ ] Une personne non autorisée à publier reçoit un refus côté serveur, même si elle appelle directement l'API.

## Bloquée par

Phases 1 et 2 ; décision sur une publication liée à un ou plusieurs espaces.

---

## Phase 9 : accès par lien

**User stories** : US-10.

### Ce qu'on livre

Une communauté peut être accessible par lien. L'administrateur crée un lien qui autorise ou non la prévisualisation des publications avant adhésion, puis peut le révoquer.

### Critères d'acceptation

- [ ] Sans adhésion ni lien valide, un espace par lien et ses publications ne sont pas lisibles.
- [ ] Un lien actif avec prévisualisation permet de lire, mais pas de publier, commenter ou liker avant adhésion.
- [ ] Un lien sans prévisualisation exige l'adhésion ; un lien révoqué ne donne plus accès.

## Bloquée par

Phase 8.

---

## Phase 10 : administrateurs et droits de communauté

**User stories** : US-11.

### Ce qu'on livre

Le super administrateur nomme des administrateurs et règle si tous les membres ou seulement les administrateurs peuvent publier.

### Critères d'acceptation

- [ ] Changer la règle de publication modifie immédiatement les droits, dans l'interface comme dans l'API.
- [ ] Un administrateur supplémentaire peut publier lorsque seuls les administrateurs y sont autorisés.
- [ ] Le créateur ne peut être exclu, rétrogradé ou perdre son rôle de super administrateur.

## Bloquée par

Phase 8. Les droits précis de nomination et de retrait des autres administrateurs doivent être tranchés avant cette phase.

---

## Phase 11 : chaîne publique

**User stories** : US-12.

### Ce qu'on livre

Un membre crée une chaîne publique, les autres s'y abonnent ou s'en désabonnent, et seuls ses administrateurs y publient des nouveautés.

### Critères d'acceptation

- [ ] Une chaîne reste indépendante d'une communauté ; le créateur est super administrateur permanent.
- [ ] Un abonnement en double ne crée pas de second abonné ; se désabonner retire l'accès lié à l'abonnement.
- [ ] Un abonné ordinaire peut lire et liker, mais ne peut pas publier.

## Bloquée par

Phases 2 et 8, pour réutiliser le parcours des espaces et leurs participations.

---

## Phase 12 : chaîne par lien et commentaires réglables

**User stories** : US-13.

### Ce qu'on livre

Le créateur d'une chaîne choisit l'accès public ou par lien et ouvre ou ferme les commentaires des publications de la chaîne.

### Critères d'acceptation

- [ ] Les liens de chaîne suivent les règles de prévisualisation et de révocation de la phase 9.
- [ ] Commentaires fermés : un abonné ne peut pas en créer par l'interface ni par l'API ; les likes restent disponibles.
- [ ] Commentaires rouverts : les nouveaux commentaires sont à nouveau acceptés sans perdre les anciens.

## Bloquée par

Phases 9 et 11.

---

## Phase 13 : suivi et fil « Abonnements »

**User stories** : US-14.

### Ce qu'on livre

Un membre suit ou cesse de suivre un autre membre et consulte un fil réunissant les publications accessibles des personnes et chaînes suivies.

### Critères d'acceptation

- [ ] Suivre est libre ; suivre deux fois la même personne ne crée pas de doublon et se suivre soi-même est refusé.
- [ ] Le fil n'expose aucune publication d'un espace privé non accessible, même si l'auteur est suivi.
- [ ] Une publication visible par le suivi de l'auteur et par l'abonnement à sa chaîne apparaît une seule fois.

## Bloquée par

Phases 1 et 11.

---

## Phase 14 : résumé quotidien

**User stories** : US-15.

### Ce qu'on livre

Le membre reçoit dans l'application un résumé quotidien des nouvelles publications accessibles de ses abonnements et peut le marquer comme lu.

### Critères d'acceptation

- [x] Au plus un résumé est produit par membre et par journée couverte ; aucune publication n'y est comptée deux fois.
- [x] Le résumé indique le nombre de nouveautés et ouvre le fil « Abonnements » correspondant.
- [x] Le contenu devenu inaccessible n'est pas révélé à l'ouverture du résumé ; l'état lu/non lu persiste.

**Décision heure** : couverture = veille calendaire (timezone Django). Production via `generate_notification_resumes` (cron recommandé ~08:00) + génération lazy sur `GET /notifications-resume/actuel`.

## Bloquée par

Phase 13. L'heure de production doit être choisie avant cette phase.

---

## Phase 15 : recherche et filtres

**User stories** : US-16.

### Ce qu'on livre

Le membre filtre le fil par type de publication et recherche un sujet, sans voir de résultats auxquels il n'a pas accès.

### Critères d'acceptation

- [ ] Les filtres distinguent discussion, application, entraide technique, aide au choix et sondage.
- [ ] Une recherche retrouve un sujet par ses mots et conserve la pagination.
- [ ] La recherche applique les mêmes droits de lecture que le fil aux publications disponibles au moment de cette phase ; ces contrôles restent valables lorsque les espaces sont ajoutés.

## Bloquée par

Phase 1. Cette phase peut être réalisée indépendamment des phases 2 à 14.

---

## Phase 16 : sondages

**User stories** : US-17.

### Ce qu'on livre

Un membre autorisé publie un sondage dans le fil général, une communauté ou une chaîne. Il choisit si chaque participant peut sélectionner une seule option ou plusieurs. Les membres autorisés peuvent voter ou s'abstenir, puis consulter les résultats.

### Critères d'acceptation

- [ ] Un sondage avec moins de deux options est refusé ; un sondage créé reste visible après rechargement.
- [ ] Après le premier vote, l'auteur ne peut plus modifier ni supprimer les options.
- [ ] En mode UNIQUE, un membre n'a qu'une option sélectionnée ; en mode MULTIPLE, il peut en sélectionner plusieurs sans doublon.
- [ ] Avant la fermeture, un membre peut modifier ou retirer son vote ; après fermeture, toute modification est refusée.
- [ ] L'auteur peut voter à son propre sondage selon les mêmes règles que les autres membres.
- [ ] Une option d'un autre sondage est refusée. Le vote suit les droits de lecture et d'interaction de l'espace ; un abonné ordinaire ne peut pas créer de sondage dans une chaîne.
- [ ] Les résultats affichent seulement le nombre de votes par option, sans identité des votants ni doublon ; avant fermeture, seul un membre ayant encore un vote actif les voit, puis tous les lecteurs autorisés les voient après fermeture.
- [ ] L'auteur peut fermer les votes ; après fermeture, aucun vote n'est accepté mais le sondage et ses résultats restent visibles.

## Bloquée par

Phases 1 et 2. Le sondage du fil général est démontrable sans espace ; son placement dans les communautés et chaînes réutilise les phases 8 et 11. Les limites de longueur et de nombre d'options restent à préciser avant cette phase.

---

# Plan : e-mails transactionnels par SMTP

> Source : cadrage du 15 novembre 2026 en conversation (pas de PRD dédié). Les identifiants `US-MAIL-*` sont propres à ce plan et distincts des `US-01…US-17` du plan Communauté et des `US-ONB-*` du PRD d'onboarding.

## Décisions architecturales

- **Point d'envoi unique** : tous les e-mails passent par le service d'e-mails existant du module `core` (gabarit texte + HTML). Les envois en texte brut de la marketplace (acceptation de candidature, invitation d'entreprise) y sont migrés.
- **Moment et mode d'envoi** : l'envoi est déclenché après l'enregistrement de l'action (fin de transaction), dans un fil d'exécution séparé : la réponse à l'utilisateur n'attend pas le serveur SMTP. Pas de file de tâches ni de nouvelle infrastructure, pas de nouvelle tentative automatique.
- **Échecs** : un échec d'envoi est journalisé (destinataire masqué, jamais le contenu ni un code) et n'annule jamais l'action. Seul l'envoi d'un code de confirmation signale l'échec à l'utilisateur, puisqu'il ne peut pas continuer sans.
- **Configuration** : variables existantes `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` (port 587, STARTTLS). En développement, le moteur console affiche les e-mails. Les liens des e-mails sont absolus et construits à partir de `FRONTEND_URL`.
- **Gabarits** : un gabarit de base commun (en-tête DevStreet, carte de contenu, bouton d'action, pied de page) et un gabarit par e-mail, chacun en version HTML et texte, dans le dossier des gabarits d'e-mail du module `core`. HTML compatible avec les clients de messagerie : mise en page en tableaux, styles en ligne, largeur maximale 600 px, lisible sans images et en mode sombre. Textes en français.
- **Codes de confirmation** : le mécanisme de défi du « mot de passe oublié » (code à 6 chiffres haché, durée de vie, tentatives limitées) est réutilisé pour le changement de mot de passe connecté, distingué par un motif (réinitialisation / changement).
- **Destinataires entreprise** : « tous les membres de l'entreprise » désigne le propriétaire et les membres invités, c'est-à-dire tous les profils entreprise rattachés à la société. Chaque destinataire reçoit un e-mail séparé.
- **Aperçu** : une commande de gestion produit chaque e-mail avec des données d'exemple (fichiers HTML locaux ou envoi de test à une adresse), pour vérifier le rendu sans déclencher l'action réelle.
- **Hors périmètre** : préférences et désabonnement, e-mails marketing, résumé quotidien par e-mail, e-mail à chaque message privé, vérification d'adresse à l'inscription, suivi d'ouverture.

## User stories de référence

| ID | Besoin utilisateur |
| --- | --- |
| US-MAIL-1 | Recevoir un e-mail de bienvenue après l'inscription (email, Google ou GitHub), avec un lien vers l'assistant d'onboarding. |
| US-MAIL-2 | Recevoir le code « mot de passe oublié » dans un e-mail moderne. |
| US-MAIL-3 | Confirmer un changement de mot de passe, une fois connecté, avec un code reçu par e-mail. |
| US-MAIL-4 | Être alerté par e-mail quand son mot de passe a été modifié. |
| US-MAIL-5 | ~~Être alerté quand un compte Google ou GitHub est lié à son compte.~~ Abandonné le 15 novembre 2026 : seul l'e-mail de bienvenue est envoyé à la création d'un compte Google/GitHub. |
| US-MAIL-6 | Recevoir un accusé de réception après avoir postulé à une offre. |
| US-MAIL-7 | Être prévenu, côté entreprise, d'une nouvelle candidature à une de ses offres. |
| US-MAIL-8 | Être prévenu que sa candidature est acceptée. |
| US-MAIL-9 | Être prévenu que sa candidature est refusée. |
| US-MAIL-10 | Être prévenu d'une mise en relation réciproque dans le Réseau. |
| US-MAIL-11 | Recevoir une invitation à rejoindre une entreprise dans un e-mail moderne. |
| US-MAIL-12 | Recevoir des e-mails cohérents, propres et lisibles partout (gabarit commun, version texte, aperçu). |
| US-MAIL-13 | Ne jamais voir une action échouer ou ralentir à cause de l'envoi d'un e-mail. |

---

## Phase M1 : socle e-mail et bienvenue

**User stories** : US-MAIL-1, US-MAIL-12, US-MAIL-13.

### Ce qu'on livre

Le gabarit de base moderne, l'envoi après enregistrement en arrière-plan et la commande d'aperçu. Premier e-mail réel : la bienvenue, envoyée à la création d'un compte par inscription ou par Google/GitHub, avec un bouton vers l'assistant d'onboarding.

### Critères d'acceptation

- [ ] Une inscription par email et une première connexion Google/GitHub envoient chacune un seul e-mail de bienvenue ; une reconnexion n'en envoie pas.
- [ ] L'e-mail contient une version HTML et une version texte, le prénom du membre et un lien absolu vers l'assistant d'onboarding.
- [ ] La réponse d'inscription n'attend pas le serveur SMTP ; un serveur SMTP injoignable n'empêche pas la création du compte et laisse une trace dans les journaux sans le contenu de l'e-mail.
- [ ] Aucun e-mail n'est envoyé si la création du compte est annulée (transaction annulée).
- [ ] La commande d'aperçu produit l'e-mail de bienvenue avec des données d'exemple.
- [ ] Le rendu HTML reste lisible sans images, en largeur mobile et en mode sombre (vérifié sur l'aperçu).
- [ ] Le nom d'expéditeur d'exemple de la configuration est DevStreet.

## Bloquée par

Aucune — démarrable immédiatement.

---

## Phase M2 : sécurité du compte

**User stories** : US-MAIL-2, US-MAIL-4 (US-MAIL-5 abandonnée).

### Ce qu'on livre

L'e-mail de code « mot de passe oublié » passe sur le gabarit commun. Une alerte est envoyée quand le mot de passe est modifié (réinitialisation ou changement). Lier un compte Google/GitHub à un compte existant n'envoie aucun e-mail.

### Critères d'acceptation

- [ ] Le code de réinitialisation est lisible d'un coup d'œil (gros caractères), avec sa durée de validité, et n'apparaît jamais dans les journaux.
- [ ] Le parcours « mot de passe oublié » fonctionne comme avant (demande, vérification, nouveau mot de passe).
- [ ] Après une réinitialisation ou un changement de mot de passe, le membre reçoit une alerte datée qui explique quoi faire s'il n'est pas à l'origine du changement.
- [ ] Lier un fournisseur Google ou GitHub à un compte existant n'envoie aucun e-mail.
- [ ] Les alertes n'annulent jamais l'action en cas d'échec d'envoi.

## Bloquée par

- Phase M1.

---

## Phase M3 : changement de mot de passe par code

**User stories** : US-MAIL-3.

### Ce qu'on livre

Un membre connecté qui change son mot de passe demande d'abord un code, le reçoit par e-mail, puis le saisit avec son mot de passe actuel et le nouveau. Le changement n'est accepté qu'avec un code valide.

### Critères d'acceptation

- [ ] Sans code valide, le changement de mot de passe est refusé, même avec le bon mot de passe actuel.
- [ ] Un code expiré, déjà utilisé ou issu d'une demande de réinitialisation est refusé ; les tentatives sont limitées.
- [ ] Une nouvelle demande de code invalide la précédente ; les demandes sont limitées dans le temps.
- [ ] La boîte de dialogue de changement de mot de passe guide le membre (envoi du code, saisie, renvoi possible) et affiche une erreur claire si l'e-mail n'a pas pu partir.
- [ ] Un compte créé par Google/GitHub sans mot de passe garde le comportement actuel (pas de changement possible sans mot de passe défini).
- [ ] Un changement réussi déclenche l'alerte « mot de passe modifié » de la phase M2.

## Bloquée par

- Phase M2.

---

## Phase M4 : candidature déposée

**User stories** : US-MAIL-6, US-MAIL-7.

### Ce qu'on livre

Quand un membre postule à une offre, il reçoit un accusé de réception, et tous les membres de l'entreprise qui publie l'offre reçoivent un e-mail « nouvelle candidature » avec un lien vers la gestion de l'offre.

### Critères d'acceptation

- [ ] Une candidature réussie envoie un accusé au candidat (titre de l'offre, entreprise, lien vers « Mes candidatures »).
- [ ] Chaque membre de l'entreprise (propriétaire et membres invités) reçoit un e-mail séparé (nom du candidat, titre de l'offre, lien vers la gestion de l'offre) ; aucune adresse d'un destinataire n'est visible des autres.
- [ ] Une candidature refusée par le serveur (doublon, offre fermée) n'envoie aucun e-mail.
- [ ] Le dépôt de la candidature n'attend pas l'envoi et ne peut pas échouer à cause de lui.

## Bloquée par

- Phase M1.

---

## Phase M5 : décision sur une candidature

**User stories** : US-MAIL-8, US-MAIL-9.

### Ce qu'on livre

L'e-mail d'acceptation existant passe sur le gabarit commun, et un e-mail de refus, sobre et respectueux, est ajouté quand l'entreprise refuse une candidature.

### Critères d'acceptation

- [ ] Une acceptation envoie un e-mail au candidat (offre, entreprise, mention de l'ajout de la mission à son calendrier, lien vers la candidature).
- [ ] Un refus envoie un e-mail au candidat, sans motif imposé, avec un lien vers les autres offres.
- [ ] Revenir sur une décision déjà prise ou renvoyer la même décision n'envoie pas de second e-mail.
- [ ] Un échec d'envoi n'annule pas la décision ni l'ajout au calendrier.

## Bloquée par

- Phase M1.

---

## Phase M6 : réseau et équipe

**User stories** : US-MAIL-10, US-MAIL-11.

### Ce qu'on livre

Une mise en relation réciproque dans le Réseau prévient les deux membres. L'invitation à rejoindre une entreprise passe sur le gabarit commun.

### Critères d'acceptation

- [ ] Le like qui crée une mise en relation envoie un e-mail à chacun des deux membres (nom de l'autre, lien vers son profil ou la conversation) ; un like sans réciprocité n'envoie rien.
- [ ] Annuler puis refaire une mise en relation n'envoie pas d'e-mail en double dans un court intervalle.
- [ ] L'e-mail d'invitation contient le nom de l'entreprise, celui de la personne qui invite, un bouton vers le lien d'invitation et sa durée de validité.
- [ ] Un échec d'envoi de l'invitation laisse le lien disponible au propriétaire, comme aujourd'hui.

## Bloquée par

- Phase M1.

---

# Plan : correctifs de sécurité issus du rapport Herald

> Source : `herald-devstreet-2026-11-15.md` (Async Herald 0.1.4, analyse statique sur disque du 15 novembre 2026), chaque point vérifié dans le dépôt le même jour. Le rapport analyse aussi `backend/venv/` et `node_modules`, qui ne sont pas du code du projet : la plupart de ses 9934 problèmes en viennent.

## Tri des signalements de sécurité

| Signalement Herald | Verdict | Raison |
| --- | --- | --- |
| Dépendances Python vulnérables (DRF, python-socketio, black) | **Retenu** — phase S1 | Versions confirmées dans `backend/requirements.txt`. DRF : déni de service par l'en-tête Accept, décodage imposé par l'attaquant dans JSONParser. python-socketio : déni de service par accumulation de pièces jointes (la faille RCE par pickle ne s'applique pas : aucun gestionnaire multi-serveur configuré). |
| Dépendance frontend embarquée vulnérable (zod) | **Retenu** — phase S2 | `npm audit --omit=dev` : 1 vulnérabilité haute, zod 4.0.10 (épuisement mémoire), corrigée en 4.6.x, même version majeure. |
| Outillage frontend vulnérable (vite, vitest, shadcn et dépendances transitives) | **Retenu** — phase S3 | `npm audit` : 5 critiques, 16 hautes, uniquement en outils de développement. Le serveur Vite écoute sur le réseau local (`server.host: true`) : ses failles de lecture de fichiers sont exploitables depuis le Wi-Fi d'un développeur. `shadcn` (CLI d'ajout de composants) tire un SDK MCP et une pile Express vulnérables. |
| Secret affiché dans les journaux du pipeline (`ci-backend.yml` l. 75-78) | **Retenu, priorité basse** — phase S4 | Faux positif sur le fond : les valeurs sont générées aléatoirement à chaque exécution et écrites dans `$GITHUB_ENV`, pas dans le journal. Mais elles ne sont pas masquées : un `set -x` ou une erreur futurs les afficheraient. |
| Pas de contrôle de santé du conteneur backend | **Retenu, optionnel** — phase S5 | `backend/Dockerfile` n'a pas de `HEALTHCHECK` alors que la route `/api/health` existe. |
| Fichier `.env` versionné | Écarté | `backend/.env` est dans `.gitignore` et absent de l'index : Herald a lu le disque, pas le dépôt. |
| Jeton / clé privée en clair (`secret_rules.py`) | Écarté | Ce sont les expressions régulières du scanner de sécurité du projet, pas des secrets. Les autres occurrences sont dans `venv`. |
| Cookie sans protections (`core/cookies.py`) | Écarté | Les cookies d'authentification sont HttpOnly, Secure hors développement et SameSite=Lax. |
| Action GitHub non épinglée (×39) | Écarté | Toutes les actions externes sont épinglées par SHA ; seules les références aux workflows locaux (`./.github/workflows/...`) ne le sont pas, ce qui est normal. |
| Requête SQL construite par formatage | Écarté | Occurrences dans les générateurs de code (texte produit, pas de requête exécutée) et dans `venv`. |
| Adresse HTTP non chiffrée, fichiers `.pem`, chemin temporaire | Écarté | Exemple de format dans `deploy_env/spec.py` (URL interne MinIO) ; le reste est dans `venv`. |
| Affichage de débogage dans `settings.py` | Écarté | Messages de démarrage sur la sortie d'erreur (adresses LAN ignorées), sans donnée sensible. |

Les catégories Qualité, Pattern et Versioning (complexité, imports inutilisés, longueur de lignes…) sont hors périmètre de ce plan.

## Décisions architecturales

- **Pas de changement de version majeure** sans phase dédiée : DRF 3.17 → 3.18, python-socketio 5.13 → 5.16, zod 4.0 → 4.6, vite 7.1 → 7.3, vitest 3.2.4 → 3.2.x. Seul `shadcn` (outil, pas de code embarqué) peut changer de majeure ou être retiré.
- **Versions exactes** : les dépendances restent épinglées (`==` côté Python, `--save-exact` côté npm), fichiers de verrouillage mis à jour avec elles.
- **Contrôles de référence** : `python -m scripts.dependency_audit`, `npm audit`, `python -m scripts.security_scan --fail-on warning`, suites de tests backend et frontend, `npm run lint`, `npm run build` (le build sur demande explicite, conformément à CLAUDE.md).
- **Herald** : pour les prochains rapports, exclure `backend/venv/` et `node_modules/` de l'analyse, sinon le bruit masque les vrais problèmes.

---

## Phase S1 : dépendances Python vulnérables

### Ce qu'on livre

`djangorestframework` passe en 3.18.2, `python-socketio` en 5.16.2 et `black` en 26.10.1. L'API, l'authentification, la messagerie temps réel et la CI de formatage fonctionnent comme avant.

### Critères d'acceptation

- [x] `backend/requirements.txt` épingle les trois nouvelles versions (DRF 3.18.2, python-socketio 5.16.2, black 26.10.1) ; `pip check` sans conflit.
- [x] La suite de tests backend ne présente aucun nouvel échec : 1280 tests, les mêmes 243 échecs avant et après (comparaison nominative, avec les anciennes puis les nouvelles versions). Ces échecs préexistants (rôles en double, fabriques de tests communauté incomplètes) sont à traiter à part.
- [ ] La messagerie temps réel (connexion, envoi et réception d'un message) fonctionne en local. *L'application ASGI et socketio se chargent ; parcours dans le navigateur non fait.*
- [x] La documentation d'API se génère toujours (240 routes, mêmes avertissements qu'avec DRF 3.17.2).

## Bloquée par

Aucune — démarrable immédiatement.

---

## Phase S2 : dépendance frontend embarquée (zod)

### Ce qu'on livre

`zod` passe de 4.0.10 à la dernière 4.6.x corrigée. Tous les formulaires valident comme avant.

### Critères d'acceptation

- [x] `npm audit --omit=dev` ne signale plus aucune vulnérabilité (zod 4.6.7).
- [ ] Lint, type-check et tests Vitest sans nouvelle erreur ; build réussi. *Lint, type-check et 119 tests Vitest OK ; build non lancé (demande explicite requise).*
- [ ] Les formulaires d'inscription, de profil, d'entreprise, d'offre et de changement de mot de passe affichent les mêmes messages d'erreur qu'avant. *Non vérifié dans le navigateur.*

## Bloquée par

Aucune — démarrable immédiatement.

---

## Phase S3 : outillage frontend

### Ce qu'on livre

`vite` passe en 7.3.8, `vitest` et `@vitest/coverage-v8` en 3.2.7, et les dépendances transitives vulnérables (tar, rollup, lodash, minimatch, brace-expansion…) sont corrigées sans changement majeur. `shadcn` est retiré des dépendances du projet et utilisé à la demande avec `npx shadcn@<version>` (ou mis à jour en 4.x si l'équipe préfère le garder installé).

### Critères d'acceptation

- [x] `npm audit` : 31 → 14 vulnérabilités, plus aucune haute. Restent 2 critiques (`tinypool`, embarqué par vitest 3 : exécution des tests en local uniquement) et 12 modérées (chaîne `typescript-eslint`/`glob`, vitest) : toutes demandent une version majeure (vitest 5), hors de ce plan.
- [ ] Le serveur de développement démarre, le rechargement à chaud fonctionne et l'accès depuis le réseau local aussi. *Non vérifié.*
- [ ] Tests Vitest (avec couverture), lint et build sans nouvelle erreur. *Tests avec couverture et lint OK ; build non lancé.*
- [x] `frontend/README.md` indique `npx shadcn@2.10.0 add …` (version compatible Tailwind 3).

## Bloquée par

- Phase S2 (même fichier de verrouillage : une mise à jour à la fois).

---

## Phase S4 : secrets générés en CI

### Ce qu'on livre

Dans `ci-backend.yml`, les mots de passe et clés générés pour la CI sont masqués (`::add-mask::`) avant d'être écrits dans l'environnement du job. On vérifie aussi pourquoi l'audit des dépendances déjà présent en CI n'a pas bloqué les versions corrigées en S1 à S3, et on corrige le seuil ou l'exception en cause.

### Critères d'acceptation

- [ ] Un affichage volontaire d'une de ces valeurs dans un job de test apparaît masqué (`***`) dans le journal. *`::add-mask::` ajouté ; à constater sur la prochaine exécution de la CI.*
- [ ] La CI backend passe comme avant. *YAML validé localement ; à constater en CI.*
- [ ] La cause de l'absence d'alerte de l'audit des dépendances est documentée, et l'audit échoue désormais sur une vulnérabilité critique non couverte par une exception datée. *Cause : l'audit a été retiré volontairement de la CI (`00readme/README_CI.md`), absence couverte par deux exceptions datées. Son retour en CI est une décision d'équipe, en attente.*

## Bloquée par

Aucune — démarrable immédiatement (la vérification de l'audit est plus parlante après S1 à S3).

---

## Phase S5 : contrôle de santé du conteneur backend (optionnel) — abandonnée

> Vérifié le 15 novembre 2026 : `deploy/compose/compose.yml` déclare déjà un contrôle de santé du backend sur `/api/health`, avec l'en-tête `Host` exigé par `ALLOWED_HOSTS`. Un `HEALTHCHECK` dans le Dockerfile ferait doublon (le compose le remplace) et passerait « unhealthy » hors de ce compose. Signalement Herald écarté.

### Ce qu'on livre

Le conteneur backend déclare un `HEALTHCHECK` qui interroge `/api/health`, pour que l'orchestrateur redémarre un conteneur bloqué.

### Critères d'acceptation

- [ ] `docker inspect` affiche l'état de santé du conteneur (`healthy` une fois démarré).
- [ ] Un backend arrêté dans le conteneur passe à `unhealthy`.
- [ ] Le déploiement existant (fichiers compose et workflows CD) n'est pas modifié dans son comportement.

## Bloquée par

Aucune — démarrable immédiatement.
