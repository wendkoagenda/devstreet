# Communautés, chaînes et abonnements — cadrage

Statut : document de travail. Ces besoins complètent le PRD initial ; aucun code n'est engagé.

## Ce qui est décidé

- Un membre peut créer une **communauté** et en devient le créateur responsable.
- Le créateur peut nommer d'autres administrateurs, mais il reste **super administrateur** : personne ne peut le retirer de son espace ni lui enlever ce rôle.
- Une communauté possède des membres et des droits. Son créateur choisit si **tous les membres** peuvent publier ou si **seuls les administrateurs** le peuvent.
- Le créateur choisit pour sa communauté un accès **public ou par lien d'invitation**. Un lien peut être révoqué.
- Une **chaîne** est indépendante des communautés. Elle est publique ou accessible par lien, au choix de son créateur. On peut s'y abonner ; seuls ses administrateurs y publient. Les abonnés peuvent liker ; les commentaires sont ouverts ou fermés selon le réglage de la chaîne.
- Pour chaque lien d'un espace accessible par lien, l'administrateur choisit si le détenteur du lien peut **prévisualiser les publications avant de rejoindre** ou s'il doit **rejoindre d'abord**. La prévisualisation ne donne pas le droit de publier, commenter ou liker.
- Un membre peut **suivre librement un autre membre**, sans demande d'accord préalable, puis arrêter de le suivre.
- Les publications restent possibles dans le **fil général** sans être rattachées à un espace.
- Un sondage est un type de publication : il peut apparaître dans le fil général, une communauté ou une chaîne, sous les mêmes droits de publication que les autres contenus de cet espace.
- Les nouveautés des chaînes et membres suivis apparaissent dans un **fil « Abonnements »** et dans un **résumé quotidien dans l'application**. Aucun e-mail n'est demandé à ce stade.
- Une conversation privée reste un échange direct entre deux personnes, sans appartenance à une publication, communauté ou chaîne.
- La réalisation est progressive : d'abord le socle des publications et échanges, ensuite les espaces, enfin le suivi des membres et le résumé quotidien.

## Parcours envisagés

### Communauté

1. Un membre crée une communauté avec un nom et une description.
2. Le créateur configure qui peut publier et obtient un lien à partager.
3. Un autre membre rejoint la communauté selon sa règle d'accès.
4. Un membre autorisé publie dans la communauté ; les autres consultent et contribuent selon les droits décidés.
5. Un administrateur peut gérer les membres, les rôles et les liens d'invitation. Un membre peut quitter la communauté.

### Chaîne

1. Un membre crée une chaîne et en devient responsable.
2. Les autres membres s'abonnent ou se désabonnent.
3. Un administrateur publie une nouveauté. Les abonnés la retrouvent dans la chaîne et dans leur fil « Abonnements » ; le résumé quotidien signale les nouveautés accessibles.

### Suivi d'un membre

1. Un membre suit un autre membre ou arrête de le suivre.
2. Toutes les nouvelles publications de cette personne auxquelles le suiveur a accès, dans le fil général ou un espace, apparaissent dans son fil « Abonnements » et dans le résumé quotidien.

## Modèle minimal à discuter

Pour éviter deux structures presque identiques, une piste est un **`Espace`** avec un type `COMMUNAUTE` ou `CHAINE`. Ce type est fixe après création. Les espaces sont distincts du point de vue des utilisateurs, même s'ils partagent une structure de données.

| Classe proposée | Rôle |
| --- | --- |
| `Espace` | Nom, description, type, accès public ou par lien ; règle de publication configurable pour une communauté, administrateurs seulement pour une chaîne ; commentaires ouverts ou fermés pour une chaîne. |
| `ParticipationEspace` | Lien unique entre membre et espace ; rôle super administrateur, administrateur ou membre/abonné ; date d'entrée. L'unique participation super administrateur identifie le créateur de l'espace. |
| `LienInvitation` | Lien révocable pour rejoindre une communauté ou s'abonner à une chaîne lorsque l'accès par lien est activé ; règle de prévisualisation choisie pour chaque lien. |
| `SuiviUtilisateur` | Lien unique entre le suiveur et le membre suivi ; interdit de se suivre soi-même. |
| `NotificationResume` | Résumé quotidien dans l'application pour un destinataire ; période couverte, nombre de nouveautés et état lu/non lu. Un lien ouvre le fil « Abonnements » correspondant. |
| `Publication` existante | Rattachement facultatif à un seul espace ; les publications du fil général restent possibles. |

Ce regroupement est **provisoire**. Si les communautés et les chaînes obtiennent des règles ou des cycles de vie très différents, deux classes distinctes seront plus lisibles. Aucun modèle supplémentaire n'est nécessaire pour l'abonnement à une chaîne : `ParticipationEspace` le représente. Les attributs de chaque modèle figurent dans [MODELE_PROPOSE.md](MODELE_PROPOSE.md).

## Règles à préserver

- La création d'un espace crée simultanément sa participation super administrateur. Le rôle et les droits sont vérifiés côté serveur pour chaque action.
- Le créateur conserve le rôle de super administrateur. Il ne peut être exclu, rétrogradé ou supprimer sa participation tant que l'espace existe. Des administrateurs supplémentaires peuvent être nommés.
- Pour une communauté réglée « administrateurs seulement », un membre ordinaire peut consulter mais ne peut pas publier. Pour une chaîne, les abonnés ne publient pas ; le réglage des commentaires ne change pas le droit de liker.
- Une publication liée à un espace obéit à ses droits de lecture et de publication. Les commentaires et les retours ne doivent pas révéler du contenu d'un espace non accessible.
- Rejoindre deux fois le même espace ou suivre deux fois la même personne ne crée qu'une relation.
- Un lien d'invitation doit pouvoir être révoqué ; une URL devinée ou révoquée ne doit pas donner accès.
- Pour un espace accessible par lien, un non-membre ne peut lire les publications que s'il possède un lien actif qui autorise la prévisualisation. Le contrôle vaut aussi pour l'API ; le lien ne donne aucun droit d'interaction avant l'adhésion.
- Le fil d'abonnements et les notifications ne montrent que des contenus que le membre est autorisé à voir. L'identifiant d'une publication privée ne doit pas révéler son contenu à un non-membre.
- Suivre une personne ne donne pas accès aux publications d'un espace privé auquel on n'a pas accès. Une publication visible via le suivi de l'auteur et via l'abonnement à sa chaîne apparaît une seule fois dans le fil et le résumé.

## Décisions encore ouvertes

1. Une publication peut-elle être publiée dans plusieurs espaces à la fois ?
2. Le créateur peut-il transférer sa propriété, ou celle-ci reste-t-elle attachée définitivement à son compte ? Qui peut nommer ou retirer les autres administrateurs, retirer un membre ou bloquer un abonné ?
3. À quelle heure produire le résumé quotidien ? Comment éviter de compter deux fois le même contenu lorsqu'on suit l'auteur et sa chaîne ?
4. Faut-il prévoir un blocage pour empêcher une personne donnée de suivre ou de contacter un membre ?
5. Quels critères d'acceptation précis et quelles limites de volume fixer pour chaque étape avant implémentation ?
