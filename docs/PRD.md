# PRD : adresses en identifiant unique et nom lisible

## Problème

Les adresses des pages de DevStreet exposent des numéros séquentiels : `/hub/projects/12`, `/marketplace/offers/7`, `/messages/45`. Ces adresses n'apprennent rien à qui les reçoit : en voyant le lien d'un projet, d'une offre ou d'un profil, on ne sait pas de quoi il parle avant de l'ouvrir. Elles laissent aussi deviner combien de ressources existent et dans quel ordre elles ont été créées. Les formes d'adresse sont en outre hétérogènes : un identifiant numérique ici, un nom d'utilisateur là, un code ailleurs.

## Solution

Chaque ressource que l'on peut ouvrir par une adresse dispose d'une adresse stable et opaque, et lisible quand elle porte un nom. Pour une ressource nommée (projet, offre, profil, publication, espace…), l'adresse affiche le nom suivi de l'identifiant unique : `/hub/projects/mon-projet-3f2a…`. Pour une ressource sans nom naturel (conversation, candidature…), l'adresse ne contient que l'identifiant unique. Cela ne change rien aux fonctionnalités, aux relations entre les données ni aux droits d'accès.

## Utilisateur cible

Un membre de DevStreet, développeur ou recruteur, qui partage des liens vers un projet, une offre, un profil ou une publication dans une messagerie, un forum ou un CV, et qui veut que le lien se comprenne d'un coup d'œil. Côté interne, l'équipe qui maintient la plateforme et génère de nouvelles ressources, qui attend que toute nouvelle ressource suive la même règle sans effort supplémentaire.

## User Stories

1. US-1 : En tant que membre, je veux que l'adresse d'un projet affiche son nom suivi d'un identifiant unique, afin de reconnaître le projet avant d'ouvrir le lien.
2. US-2 : En tant que membre, je veux la même règle pour les offres, les profils, les entreprises, les publications, les espaces (communautés et chaînes) et les autres ressources nommées, afin d'avoir des liens cohérents partout.
3. US-3 : En tant que membre, je veux que les ressources sans nom (conversations, messages, candidatures, écrans d'administration) aient une adresse composée de leur seul identifiant unique, afin de ne jamais voir un numéro séquentiel dans la barre d'adresse.
4. US-4 : En tant que membre, je veux qu'un lien dont le nom est périmé (ressource renommée) ou modifié à la main ouvre quand même la bonne page, afin que les liens déjà partagés restent utilisables après un renommage.
5. US-5 : En tant que membre, je veux que mon adresse de profil par nom d'utilisateur (`/forum/u/<nom>`) et les liens d'invitation (`/forum/invitation/<code>`) restent identiques, afin de ne pas casser des usages déjà établis.
6. US-6 : En tant que membre, je veux que les pages de retour d'autorisation Git gardent leur adresse actuelle, afin que le parcours de connexion Git continue de fonctionner.
7. US-7 : En tant que membre, je veux que tous les liens internes de l'application (menus, cartes, listes, notifications, fils, messages) pointent vers la nouvelle forme d'adresse, afin de n'atterrir jamais sur une page introuvable en naviguant.
8. US-8 : En tant que membre, je veux obtenir une page « introuvable » claire quand j'ouvre une adresse avec un ancien numéro (`/hub/projects/12`), afin de comprendre que le lien n'est plus valide.
9. US-9 : En tant que membre, je veux obtenir la même page « introuvable » quand l'identifiant unique de l'adresse n'existe pas ou est mal formé, afin de ne pas voir d'erreur technique.
10. US-10 : En tant que membre, je veux que mes droits d'accès soient les mêmes qu'avant (une ressource privée reste privée, même avec son adresse), afin que le changement d'adresse n'ouvre aucune fuite.
11. US-11 : En tant que membre, je veux qu'une ressource sans nom exploitable (vide, caractères spéciaux uniquement) soit adressée par son seul identifiant unique, afin de ne jamais obtenir une adresse cassée.
12. US-12 : En tant que membre, je veux que les noms accentués ou longs soient rendus en minuscules simples, sans accents et de longueur raisonnable dans l'adresse, afin d'avoir des liens propres à copier.
13. US-13 : En tant qu'administrateur, je veux que les écrans d'administration de la marketplace utilisent aussi ces adresses, afin que l'interface d'administration suive la même règle.
14. US-14 : En tant que membre, je veux que toutes les données existantes gardent leur adresse stable après la mise en service, afin de ne perdre ni contenu ni relation.
15. US-15 : En tant que membre de l'équipe, je veux que toute nouvelle ressource créée avec l'outil de génération reçoive automatiquement cette forme d'adresse, afin de ne pas réintroduire de numéros séquentiels.

## Critères de succès

- Aucune adresse affichée dans la barre du navigateur pour une ressource de la liste ne contient un numéro séquentiel (entier seul) en parcourant les écrans principaux (hub, marketplace, forum, messages, administration).
- Pour 100 % des routes de ressources concernées, ouvrir l'adresse `nom-slug-<uuid>` ou `<uuid>` affiche la même page.
- Ouvrir une adresse avec un ancien identifiant numérique ou un identifiant unique inexistant affiche la page « introuvable ».
- Renommer une ressource puis ouvrir l'ancien lien (ancien nom, même identifiant unique) affiche toujours la ressource.
- Les adresses `/forum/u/<nom>`, `/forum/invitation/<code>` et celles de retour d'autorisation Git répondent comme avant.
- Aucune donnée existante n'est perdue : le nombre de lignes de chaque ressource avant et après mise en service est identique.
- Le parcours de test habituel (connexion, création d'un projet, d'une offre, d'une publication, envoi d'un message) fonctionne de bout en bout avec les nouvelles adresses.
- Une ressource créée avec l'outil de génération après mise en service est accessible par une adresse en identifiant unique, sans modification manuelle.

## Hors périmètre

- Masquer les identifiants numériques dans les données échangées entre l'application et le serveur (corps de requête, filtres, réponses). Seule l'adresse change.
- Transformer les identifiants internes en identifiants uniques.
- Rediriger les anciens liens numériques vers les nouveaux, ou conserver leur validité (ils renvoient « introuvable »).
- Mettre à jour le nom dans l'adresse quand une ressource est renommée (pas de redirection vers l'adresse « à jour »).
- Modifier les noms d'utilisateur, les codes d'invitation, les routes d'autorisation Git.
- Ajouter une adresse aux ressources purement internes (likes, votes, réactions, instantanés, webhooks, tables de liaison).
- Modifier les droits, les rôles ou la logique métier.
- Référencement (SEO) avancé et balises de partage.

## Décisions d'implémentation

- Format d'adresse d'une ressource nommée : nom en minuscules, sans accents, mots séparés par des tirets, suivi de l'identifiant unique (`mon-projet-3f2a…`). Le nom est tronqué à une longueur raisonnable.
- Ressource sans nom exploitable ou sans nom naturel : l'identifiant unique seul.
- Seul l'identifiant unique en fin d'adresse détermine la page affichée ; le nom est indicatif.
- Ancien identifiant numérique ou identifiant inconnu : page « introuvable » standard de l'application.
- Les adresses existantes des ressources concernées changent en une seule mise en service par tranche (hub, marketplace, communauté, comptes et IA) ; les liens internes de la tranche sont mis à jour dans la même livraison.
- Les noms d'utilisateur, codes d'invitation et routes d'autorisation Git gardent leur forme actuelle.
- Ressources concernées : comptes et rôles ; projets, tâches, technologies, contributions, analyses ; entreprises, compétences, profils, offres, candidatures, expériences, prestations, disponibilités, avis, swipes, connexions, compétences de profil, historiques de profil ; publications, espaces, conversations, tags, liens d'invitation ; conversations IA.

## Notes complémentaires

- **Anciens liens** : tout lien déjà partagé avec un numéro (messages, favoris, CV, e-mails) devient « introuvable ». Décision actée : pas de redirection. À vérifier avant mise en service si des liens circulent en production.
- **Renommage** : le nom dans l'adresse peut être périmé après un renommage ; le lien fonctionne quand même.
- **Zones protégées** : certains fichiers touchés (routes, outil de génération) sont dans des zones suivies par la CI ; une validation du responsable de zone peut être demandée.
- **Données existantes** : chaque ressource existante reçoit son identifiant unique lors de la mise en service ; la migration doit pouvoir être annulée.
- **Hypothèse** : l'adresse n'est pas considérée comme un secret ; elle n'ouvre aucun accès non autorisé.
- **Branche unique** : tout est livré sur la branche actuelle, en commits par tranche.
- Le plan existant (`docs/PLAN.md`, module Communauté) utilise des codes `US-01…US-17` ; les `US-1…US-15` de ce PRD sont distincts. À traiter à la planification.

---

# PRD : onboarding de création de compte et profils par type

## Problème

Un nouveau membre de DevStreet crée son compte sans qu'on lui demande ce qu'il vient y faire. Il arrive sur le forum, et les espaces dev et entreprise lui sont proposés plus tard, sous forme d'invitations discrètes à « Créer mon profil dev » ou « Créer mon entreprise ». Un recruteur qui ne vient que pour la marketplace voit donc le forum, les communautés, les chaînes et les projets, qui ne le concernent pas. Tous les membres reçoivent par ailleurs les mêmes droits, y compris ceux de la partie administration de la marketplace. Le lien « Marketplace > Administration » apparaît ainsi chez tous.

## Solution

Après la création de son compte (par email, Google ou GitHub), le membre est guidé par un assistant. Il choisit d'abord quel profil il veut : développeur, entreprise, ou les deux. Il est ensuite accompagné pas à pas pour créer l'essentiel de ce profil, et peut terminer plus tard. Le menu et les pages accessibles s'adaptent ensuite à son choix. Un compte entreprise ne voit que la marketplace, plus ce qui la concerne (messagerie, profil). Les comptes dev et « les deux » voient l'ensemble de la plateforme. Aucun de ces comptes ne voit l'administration (utilisateurs, rôles, administration de la marketplace). Un membre peut ajouter plus tard le type manquant.

## Utilisateur cible

- **Développeur** qui vient présenter ses compétences, trouver des offres, participer à des projets et échanger sur le forum.
- **Recruteur ou entreprise** qui vient publier des offres et trouver des talents. Il n'a pas besoin du forum ni des projets, mais doit pouvoir échanger avec les talents et gérer le profil de son entreprise.
- **Profil hybride** qui est les deux à la fois : un indépendant qui recrute aussi, ou un dirigeant de petite structure qui développe lui-même.
- **Personne invitée à rejoindre une entreprise** existante, qui n'a pas à en créer une.
- **Administrateur** de la plateforme, qui conserve son fonctionnement actuel.

## User Stories

1. US-ONB-1 : En tant que nouveau membre, je veux qu'on me demande, juste après la création de mon compte, quel profil je veux (développeur, entreprise ou les deux), afin d'obtenir un espace adapté à mon besoin.
2. US-ONB-2 : En tant que nouveau membre, je veux que cette question soit posée de la même façon quelle que soit la méthode de création de compte (email, Google, GitHub), afin de ne pas vivre un parcours différent selon mon choix.
3. US-ONB-3 : En tant que nouveau membre, je veux que le choix du type de profil soit obligatoire et enregistré dès que je le valide, afin de ne jamais retrouver une plateforme générique ensuite.
4. US-ONB-4 : En tant que développeur, je veux être guidé pour créer l'essentiel de mon profil (titre, pays, ville, compétences clés) en trois écrans au plus, afin d'être visible rapidement.
5. US-ONB-5 : En tant que recruteur, je veux être guidé pour créer mon entreprise (nom, secteur, taille, pays), afin de pouvoir publier des offres rapidement.
6. US-ONB-6 : En tant que membre ayant choisi « les deux », je veux être guidé pour les deux profils l'un après l'autre, afin de tout mettre en place d'une seule session.
7. US-ONB-7 : En tant que membre, je veux pouvoir choisir « Terminer plus tard » à n'importe quelle étape de création, afin de ne pas être bloqué si je n'ai pas les informations sous la main.
8. US-ONB-8 : En tant que membre ayant reporté la création, je veux que mon menu s'adapte déjà à mon choix et qu'un rappel m'invite à finir, afin de savoir ce qu'il me reste à faire.
9. US-ONB-9 : En tant que membre, je veux voir à la fin de l'assistant un récapitulatif avec le niveau de complétion de mon profil et des liens vers les formulaires complets (CV, expériences, liens, logo…), afin de savoir comment l'enrichir.
10. US-ONB-10 : En tant que membre ayant fermé l'assistant avant d'avoir choisi un type, je veux le retrouver à ma prochaine connexion, afin de ne pas rester sans type.
11. US-ONB-11 : En tant que compte entreprise seule, je veux ne voir dans le menu que le groupe Marketplace (Général et Mon espace entreprise) et une entrée Messages, afin de ne pas être noyé sous des fonctionnalités qui ne me concernent pas.
12. US-ONB-12 : En tant que compte entreprise seule, je veux rester sur les pages qui me concernent même si elles sont rangées ailleurs (messagerie, mon profil, mon compte, profils publics des talents, invitation d'entreprise), afin de ne pas être coupé d'un usage essentiel.
13. US-ONB-13 : En tant que compte entreprise seule, je veux que l'ouverture d'une adresse du forum, des communautés, des chaînes ou des projets me renvoie à l'accueil de la marketplace, afin de ne jamais tomber sur une page qui n'est pas pour moi.
14. US-ONB-14 : En tant que compte entreprise seule, je veux arriver sur l'accueil de la marketplace à chaque connexion, afin de commencer directement par mon espace.
15. US-ONB-15 : En tant que compte entreprise seule, je veux que mon profil n'affiche pas les onglets du forum (publications, projets, contributions), afin de ne voir que ce qui me concerne.
16. US-ONB-16 : En tant que développeur ou « les deux », je veux voir tout le menu (Principal, Marketplace, Projets), avec Mon espace dev et, si je suis aussi entreprise, Mon espace entreprise, afin d'accéder à toute la plateforme.
17. US-ONB-17 : En tant que membre dev ou entreprise, je veux ne jamais voir les entrées Utilisateurs, Rôles ni Marketplace > Administration, afin que l'interface ne m'expose aucune fonction d'administration.
18. US-ONB-18 : En tant que membre dev ou entreprise, je veux que ces fonctions d'administration me soient aussi refusées si j'ouvre leur adresse ou les appelle directement, afin que la restriction ne soit pas seulement visuelle.
19. US-ONB-19 : En tant que membre, je veux pouvoir ajouter plus tard le type manquant depuis un bouton « Ajouter un espace entreprise » ou « Ajouter un espace dev », afin de faire évoluer mon usage sans recréer de compte.
20. US-ONB-20 : En tant que compte entreprise qui ajoute un espace dev, je veux que le forum, les communautés, les chaînes et les projets s'ajoutent à mon menu dès l'ajout, afin de profiter immédiatement du nouveau type.
21. US-ONB-21 : En tant que personne invitée à rejoindre une entreprise, je veux que l'acceptation de l'invitation me donne directement le type entreprise sans créer de société, afin de rejoindre l'équipe sans étape superflue.
22. US-ONB-22 : En tant que personne invitée qui n'a pas encore de compte, je veux créer mon compte puis arriver sur l'entreprise qui m'a invité, afin que l'invitation ne soit pas perdue.
23. US-ONB-23 : En tant que membre existant qui a déjà un profil dev et/ou une entreprise, je veux que mon type soit reconnu automatiquement et que mon menu s'adapte sans repasser par l'assistant, afin de ne pas être interrompu.
24. US-ONB-24 : En tant que membre existant sans aucun profil, je veux être invité à l'assistant à ma prochaine connexion, afin d'obtenir un menu adapté.
25. US-ONB-25 : En tant qu'administrateur (Super Admin ou Admin), je veux ne pas passer par l'assistant et conserver mon menu actuel avec l'administration, afin de continuer à gérer la plateforme.
26. US-ONB-26 : En tant que nouveau membre, je veux une erreur claire si la création de mon profil ou de mon entreprise échoue (champ invalide, pays manquant, nom déjà pris), afin de pouvoir corriger sans perdre ma saisie.
27. US-ONB-27 : En tant que nouveau membre, je veux qu'un rafraîchissement de la page en cours d'assistant me ramène à l'étape où j'étais, afin de ne pas tout recommencer.
28. US-ONB-28 : En tant que membre dev ou entreprise, je veux que la visite guidée du premier lancement ne me présente que les entrées de mon menu, afin que les explications correspondent à ce que je vois.

## Critères de succès

- Après création d'un compte par email, Google ou GitHub, l'assistant s'ouvre avant toute autre page, et la question « développeur, entreprise ou les deux » est affichée.
- Le choix est enregistré à la validation : fermer l'onglet puis se reconnecter ne redemande pas le type, mais ramène à la création si elle n'est pas terminée.
- Un parcours dev complet (écrans de création minimale) se termine en trois écrans au plus, et un parcours entreprise en deux écrans de saisie au plus.
- Un compte entreprise seule ne voit, dans son menu, que le groupe Marketplace et l'entrée Messages. Les entrées Forum, Communautés, Chaînes, Favoris et Projets sont absentes.
- Pour un compte entreprise seule, l'ouverture directe d'une adresse du forum, des communautés, des chaînes ou des projets le ramène à l'accueil de la marketplace, tandis que la messagerie, son profil, son compte et les profils des talents restent ouverts.
- Pour un compte entreprise seule, l'adresse `/` et la connexion ouvrent l'accueil de la marketplace.
- Pour un compte dev ou « les deux », le menu contient Principal, Marketplace et Projets ; le groupe Marketplace affiche Mon espace dev, et Mon espace entreprise si le type entreprise est présent.
- Aucun compte dev ou entreprise ne voit les entrées Utilisateurs, Rôles et Marketplace > Administration, et l'ouverture de leurs adresses ou leurs appels directs est refusée.
- Un compte Super Admin ou Admin ne voit pas l'assistant et conserve le menu Administration.
- Après la mise en service, 100 % des comptes existants ayant déjà un profil dev ou une entreprise ont le type correspondant, sans repasser par l'assistant.
- Un compte existant sans profil voit l'assistant à sa première connexion suivante, et seulement à celle-là tant qu'il n'a pas choisi de type.
- Depuis un compte dev, « Ajouter un espace entreprise » lance l'assistant pour le type manquant, et au retour le groupe Marketplace affiche Mon espace entreprise.
- Une personne qui accepte une invitation d'entreprise arrive sur l'entreprise avec le type entreprise, sans passer par la création de société.
- Le parcours de test habituel (création de compte, choix du type, création du profil, connexion suivante) fonctionne de bout en bout pour les trois choix.

## Hors périmètre

- Retirer un type de profil depuis l'interface (un changement de ce genre passe par un administrateur).
- Un sélecteur de mode (dev / entreprise) ou une bascule de contexte dans la barre latérale.
- Modifier les écrans d'administration eux-mêmes ou la gestion des rôles pour les administrateurs.
- Modifier le contenu du forum, des communautés, des chaînes et des projets.
- Donner à l'entreprise un accès au forum, aux communautés, aux chaînes ou aux projets sans ajouter le type dev.
- Un parcours complet de création dans l'assistant (CV, expériences, logo, liens, prestations) : ces éléments restent dans les formulaires existants.
- Vérification d'identité, validation par un administrateur ou facturation de l'entreprise.
- Un nouveau choix de méthode de connexion ou de nouveaux fournisseurs de connexion.
- Une refonte graphique du menu ou de la page de connexion.

## Décisions d'implémentation

- **Moment de l'assistant** : il s'ouvre après la création du compte, une seule fois par compte, quelle que soit la méthode de création. L'inscription par email n'ajoute pas de champ.
- **Choix du type** : trois options visibles, « Développeur », « Entreprise », « Les deux ». Le choix est obligatoire. Il est enregistré dès la validation.
- **Création guidée minimale** :
  - Développeur : titre, pays, ville, compétences clés (trois écrans au plus).
  - Entreprise : nom, secteur, taille, pays.
  - Pour « les deux », les deux parcours s'enchaînent.
- **Report** : chaque étape propose « Terminer plus tard ». Le menu s'adapte au type choisi même sans profil, et un rappel de complétion reste visible tant que la création n'est pas finie.
- **Récapitulatif de fin** : pourcentage de complétion et liens vers les formulaires complets existants.
- **Menu par type** :

| Type | Menu | Arrivée après connexion |
|---|---|---|
| Développeur | Principal, Marketplace (Général + Mon espace dev), Projets | Fil du forum |
| Entreprise seule | Marketplace (Général + Mon espace entreprise) et une entrée Messages | Accueil de la marketplace |
| Les deux | Principal, Marketplace (Général + Mon espace dev + Mon espace entreprise), Projets | Fil du forum |
| Admin | Inchangé, avec Administration | Inchangée |

- **Pages accessibles à l'entreprise seule** : la marketplace, la messagerie, le profil (sans les onglets du forum), le compte, les profils publics et la page d'invitation d'entreprise. Toute autre adresse la renvoie à l'accueil de la marketplace.
- **Administration** : les entrées Utilisateurs, Rôles et Marketplace > Administration ne s'affichent que pour les administrateurs. Elles sont aussi refusées en accès direct pour les autres.
- **Droits** : un rôle par type. Le rôle entreprise couvre la marketplace et la messagerie. Le rôle dev couvre la marketplace, le forum, les communautés et les projets. Ni l'un ni l'autre n'incluent l'administration. Un compte « les deux » cumule les deux rôles.
- **Ajout d'un type** : un bouton « Ajouter un espace entreprise » ou « Ajouter un espace dev » relance l'assistant pour le type manquant. Le menu et les droits s'étendent dès la validation.
- **Invitation d'entreprise** : accepter une invitation donne le type entreprise sans créer de société.
- **Comptes existants** : le type est reconnu automatiquement selon les profils déjà créés. Un compte sans profil passe par l'assistant à sa prochaine connexion. Les administrateurs sont exclus.
- **Reprise** : un rafraîchissement en cours d'assistant ramène à l'étape en cours.
- **Visite guidée** : elle ne présente que les entrées du menu du compte.
- **Erreurs** : messages clairs par champ, la saisie est conservée.

## Notes complémentaires

- **Lien avec le PRD des adresses** : les deux travaux touchent les mêmes écrans (profils, entreprises, marketplace, messagerie). Il faut ordonnancer les deux en planification pour que les adresses d'écran et les règles d'accès par type restent cohérentes, notamment la liste des pages accessibles à l'entreprise.
- **Messagerie ouverte à l'entreprise** : elle reste rattachée au forum et accessible à l'entreprise seule. Il faut vérifier que ses écrans ne dépendent pas de fonctions du forum interdites à l'entreprise (publications, communautés).
- **Onglets forum du profil** : les onglets Publications, Projets et Contributions du profil doivent être masqués pour l'entreprise seule.
- **Droits plus étroits** : le rôle actuel unique donne à tous les membres les mêmes droits larges. Le passage à un rôle par type retire des droits à des comptes existants. Le rattrapage doit leur attribuer le bon rôle pour éviter de les enfermer dehors.
- **Zones protégées** : le menu, les droits et les rôles de base sont dans des fichiers suivis par la CI. Une validation du responsable de zone peut être demandée.
- **Hypothèse** : un compte « entreprise seule » qui ajoute le type dev devient « les deux » et reçoit le menu complet.
