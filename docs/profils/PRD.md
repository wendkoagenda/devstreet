# PRD : profils dev et entreprise

> Source : cadrage du 14 novembre 2026 (10 décisions validées une à une). Aucune implémentation n'est engagée par ce document.

## Problème

Aujourd'hui, le profil d'un membre vit dans le forum : son adresse est `/forum/profil/<numéro>`, alors que la personne existe dans toute l'application (forum, projets, marketplace). Le numéro n'est pas parlant, le mot « forum » laisse croire que le profil appartient à une seule zone, et trois pages de profil différentes coexistent selon l'endroit d'où l'on vient.

Par ailleurs, une personne ne peut pas être à la fois développeuse ou développeur à la recherche de missions et recruteur au nom d'une entreprise. Le profil actuel mélange les deux rôles : une seule fiche par personne, avec une entreprise facultative. Un recruteur ne peut pas avoir son propre profil de développeur, et le profil d'un recruteur affiche des éléments (candidatures, compétences) qui n'ont aucun rapport avec son rôle d'entreprise.

## Solution

Chaque membre a une seule page de profil, à une adresse simple et lisible : `/profil/<nom d'utilisateur>`, la même partout dans l'application. Un membre peut y présenter un **profil dev**, un **profil entreprise**, ou les deux. Le profil entreprise est toujours lié à une entreprise. Les deux profils sont étanches : les candidatures, compétences, expériences, prestations, disponibilités, avis et connexions appartiennent au profil dev ; les offres publiées appartiennent au profil entreprise.

La page de profil réunit l'activité du membre (publications, projets, contributions) et, selon ce qu'il possède, un onglet **Profil dev** et un onglet **Entreprise**. Un membre crée une entreprise (et en devient propriétaire) ou rejoint une entreprise existante sur invitation de son propriétaire. Les anciennes adresses continuent de fonctionner par redirection.

## Utilisateur cible

- **Développeuse ou développeur** inscrit sur DevStreet, actif dans le forum et les projets, qui cherche des missions ou des collaborations et veut un profil présentable à partager par lien.
- **Recruteur ou fondatrice, fondateur d'une entreprise** qui publie des offres au nom d'une entreprise, et qui est souvent aussi développeur à titre personnel.
- **Membre de l'équipe d'une entreprise** qui rejoint la société d'un collègue pour publier des offres avec lui.
- **Tout membre connecté** qui consulte le profil d'un autre membre pour s'informer avant d'échanger, de postuler ou de collaborer.

## User Stories

1. US-1 : En tant que membre, je veux que mon profil soit accessible à `/profil/<mon nom d'utilisateur>`, afin de le partager par un lien lisible.
2. US-2 : En tant que membre, je veux ouvrir `/profil/me` (ou `/profil/moi`), afin d'arriver sur mon propre profil sans connaître mon nom d'utilisateur.
3. US-3 : En tant que membre connecté, je veux consulter le profil d'un autre membre depuis une publication, un message, la recherche ou un projet, afin de savoir à qui j'ai affaire.
4. US-4 : En tant que membre, je veux que `Alice` et `alice` soient considérés comme le même nom d'utilisateur, afin qu'une adresse de profil désigne toujours une seule personne.
5. US-5 : En tant que membre, je veux être empêché de choisir un nom d'utilisateur réservé (par exemple `me`, `moi`, `admin`), afin qu'il ne masque pas une page de l'application.
6. US-6 : En tant que membre, je veux pouvoir changer mon nom d'utilisateur et être averti que mes anciens liens ne fonctionneront plus, afin de décider en connaissance de cause.
7. US-7 : En tant que membre qui suit un ancien lien (`/forum/profil/<numéro>`, `/forum/u/<nom>`, `/hub/profiles/<numéro>`, `/marketplace/profiles/<numéro>`), je veux arriver sur la bonne page de profil, afin que mes liens enregistrés ou partagés continuent de fonctionner.
8. US-8 : En tant que membre, je veux voir sur la page de profil mes onglets Publications, Projets et Contributions, afin de retrouver mon activité.
9. US-9 : En tant que membre ayant un profil dev, je veux un onglet **Profil dev** qui présente mes compétences, expériences, prestations, disponibilités, avis et mon CV, afin de me présenter à des recruteurs.
10. US-10 : En tant que membre sans profil dev, je veux ne pas voir d'onglet Profil dev sur la page des autres, et pouvoir en créer un depuis mon propre profil, afin d'activer ce rôle quand je le souhaite.
11. US-11 : En tant que membre ayant un profil entreprise, je veux un onglet **Entreprise** qui présente la société et les offres que j'ai publiées, afin que les développeurs sachent pour qui je recrute.
12. US-12 : En tant que membre sans profil entreprise, je veux ne pas voir d'onglet Entreprise, afin que ma page ne montre que ce qui existe.
13. US-13 : En tant que membre ayant les deux profils, je veux que mes candidatures, compétences et expériences n'apparaissent jamais dans l'onglet Entreprise, et que mes offres n'apparaissent jamais dans l'onglet Profil dev, afin que mes deux rôles restent séparés.
14. US-14 : En tant que membre, je veux créer une entreprise et en devenir propriétaire, ce qui me donne un profil entreprise, afin de recruter au nom de ma société.
15. US-15 : En tant que propriétaire d'une entreprise, je veux inviter une personne par lien ou par adresse e-mail à rejoindre mon entreprise, afin de recruter à plusieurs.
16. US-16 : En tant que personne invitée, je veux accepter l'invitation et obtenir un profil entreprise rattaché à cette société, afin de publier des offres avec mon équipe.
17. US-17 : En tant que propriétaire, je veux révoquer une invitation en attente, afin qu'un lien ne puisse plus être utilisé.
18. US-18 : En tant que membre, je veux être informé qu'une invitation est expirée, révoquée ou déjà utilisée, afin de comprendre pourquoi je ne peux pas la rejoindre.
19. US-19 : En tant que membre déjà rattaché à une entreprise, je veux être averti que je ne peux avoir qu'une seule entreprise, afin de ne pas rejoindre ou créer une seconde société par erreur.
20. US-20 : En tant que membre connecté, je veux voir le profil entreprise de n'importe quel autre membre, avec un badge lorsque l'entreprise est vérifiée, afin d'évaluer le sérieux d'un recruteur.
21. US-21 : En tant que membre d'une entreprise, je veux que le téléphone et l'e-mail de contact de la société ne soient visibles que pour les membres de cette société, afin de protéger les coordonnées sensibles.
22. US-22 : En tant que membre non connecté, je veux être invité à me connecter avant de voir un profil, afin de respecter la confidentialité actuelle de l'application.
23. US-23 : En tant que visiteur, je veux un message « Profil introuvable » lorsqu'un nom d'utilisateur n'existe pas ou est désactivé, afin de comprendre que le lien est faux.
24. US-24 : En tant que membre, je veux que les anciens profils déjà créés continuent d'afficher leurs données (profils dev et rattachements à une entreprise), afin de ne rien perdre lors de la mise en place.
25. US-25 : En tant que propriétaire d'une entreprise, je veux que mon profil entreprise ne puisse pas recevoir d'avis ni de connexion de type dev, afin que ces éléments restent propres au profil dev.

## Critères de succès

1. Ouvrir `/profil/<nom>` affiche la page de ce membre ; ouvrir `/profil/<NOM en majuscules>` affiche la même page.
2. Les quatre anciennes formes d'adresse (`/forum/profil/<numéro>`, `/forum/u/<nom>`, `/hub/profiles/<numéro>`, `/marketplace/profiles/<numéro>`) redirigent vers `/profil/<nom>`, avec le bon onglet quand l'ancien lien visait un contenu précis.
3. Aucun lien interne de l'application ne contient plus `/forum/profil/`.
4. Créer un second membre dont le nom d'utilisateur ne diffère d'un existant que par la casse est refusé avec un message explicite ; choisir un nom réservé est refusé de la même manière.
5. Un membre ayant un profil dev et un profil entreprise voit deux onglets distincts ; l'onglet Entreprise ne montre aucune candidature, compétence ni expérience, et l'onglet Profil dev ne montre aucune offre.
6. Un membre ne peut posséder qu'un profil dev et qu'un profil entreprise : toute tentative d'en créer un second est refusée.
7. Un profil entreprise ne peut pas exister sans entreprise ; supprimer toutes les données d'entreprise d'un profil est refusé.
8. Un avis ou une connexion visant un profil entreprise est refusé ; une offre dont le recruteur est un profil dev est refusée ; une candidature depuis un profil entreprise est refusée.
9. Une invitation fonctionne une seule fois ; après acceptation, révocation ou expiration, ouvrir le lien affiche le motif précis.
10. Après la mise à jour, 100 % des membres qui avaient un profil avant sont retrouvés avec les mêmes données sur leur onglet Profil dev ; ceux qui étaient rattachés à une entreprise ont en plus un profil entreprise rattaché à la même entreprise.
11. Le téléphone et l'e-mail de contact d'une entreprise sont absents de la réponse vue par un membre extérieur à l'entreprise.
12. La mise à jour est refusée si la base contient deux noms d'utilisateur identiques à la casse près, ou un nom réservé, avec un rapport indiquant les comptes concernés.

## Hors périmètre

- Un identifiant opaque (UUID) dans l'adresse du profil.
- Plusieurs entreprises pour un même membre, et un sélecteur d'entreprise active.
- Conserver l'historique des anciens noms d'utilisateur pour rediriger après un changement.
- Visibilité réglable du profil entreprise par le propriétaire (le profil est visible par tout membre connecté).
- Rattachement libre à une entreprise existante, ou demande d'adhésion soumise à l'approbation du propriétaire.
- Avis « employeur » sur une entreprise, ou connexions entre un dev et une entreprise.
- Vérification des entreprises par un parcours utilisateur (elle reste faite par un administrateur).
- Profils visibles par des visiteurs non connectés.
- Refonte visuelle du forum, des publications ou de la messagerie au-delà des liens vers le profil.

## Décisions d'implémentation

- **Adresse** : `/profil/<nom d'utilisateur>`. Les alias `me` et `moi` mènent au profil du membre connecté.
- **Nom d'utilisateur** : unique sans tenir compte des majuscules ; modifiable ; une liste de noms réservés est refusée à la création et au changement. Un changement de nom invalide les anciens liens, et le membre en est averti avant de confirmer.
- **Un profil dev et un profil entreprise au maximum par membre.** Le profil entreprise est toujours rattaché à une entreprise. Le profil dev porte : candidatures, compétences, expériences, prestations, disponibilités, avis, connexions. Le profil entreprise porte : offres publiées. Les sélections de recrutement (le swipe « recrutement ») vont d'un profil entreprise vers un profil dev ; celles du réseau vont de dev à dev.
- **Page de profil** : une page unique avec des onglets Publications, Projets, Contributions, Profil dev, Entreprise ; les onglets Profil dev et Entreprise n'apparaissent que si le profil correspondant existe (ou, sur son propre profil, avec une invitation à le créer).
- **Entreprise** : un membre crée une entreprise (il en devient propriétaire) ou rejoint une entreprise existante sur invitation du propriétaire, par lien ou par e-mail. Une invitation est à usage unique, révocable, et expire. Un membre n'a qu'une entreprise.
- **Visibilité** : tout membre connecté voit le profil dev et le profil entreprise d'un autre membre. Un badge signale une entreprise vérifiée. Le téléphone et l'e-mail de contact de l'entreprise ne sont visibles que pour ses membres.
- **Anciennes adresses** : elles redirigent de façon permanente vers la nouvelle adresse, et tous les liens internes pointent directement vers `/profil/<nom>`.
- **Migration des données** : les profils existants deviennent des profils dev ; ceux qui avaient une entreprise donnent aussi un profil entreprise ; la mise à jour est refusée, avec rapport, s'il existe des noms d'utilisateur en doublon à la casse près ou réservés.
- **Livraison en trois tranches** : (1) adresse et nom d'utilisateur, (2) profil typé dev ou entreprise avec ses règles, (3) onglets, entreprise et invitations.

## Notes complémentaires

- **Risque principal** : la tranche 2 modifie le schéma d'un modèle dont dépendent offres, candidatures, avis, swipes, connexions, compétences, expériences, prestations et disponibilités. Une sauvegarde de la base avant migration est nécessaire.
- **Dépendance** : le mécanisme d'invitation du forum (lien d'invitation) peut servir de base pour les invitations d'entreprise.
- **Point ouvert** : le pays est aujourd'hui obligatoire sur un profil ; pour un profil entreprise, il faudra décider s'il est repris de l'entreprise.
- **Point ouvert** : la liste exacte des noms d'utilisateur réservés reste à fixer.
- **Hypothèse** : le nom d'utilisateur est déjà unique en base (sensible à la casse) ; il n'y a donc pas de dédoublonnage massif à prévoir, seulement à vérifier.
