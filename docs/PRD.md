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
