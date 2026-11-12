# Interfaces à construire après validation backend

Tous les écrans ci-dessous sont **à réaliser**. L’ordre proposé sert à avancer un écran à la fois. Ils réutiliseront le layout, les composants, la police, les tokens de thème et l’IAM existants. Les commandes de génération CRUD frontend fourniront les bases utiles ; l’écran final suivra son parcours métier plutôt qu’une juxtaposition de tables.

| N° | Écran | Fichier | Priorité |
| --- | --- | --- | --- |
| 01 | Explorer les projets | [01-explorer.md](01-explorer.md) | P0 |
| 02 | Créer son projet et préparer le dépôt | [02-creer-projet.md](02-creer-projet.md) | P0 |
| 03 | Fiche projet et gestion | [03-fiche-projet.md](03-fiche-projet.md) | P0 |
| 04 | Comprendre une tâche et contribuer | [04-tache-contribution.md](04-tache-contribution.md) | P0 |
| 05 | Examiner les contributions | [05-revue-contributions.md](05-revue-contributions.md) | P0 |
| 06 | Préparer une contribution avec l’IA | [06-atelier-ia.md](06-atelier-ia.md) | P0 |
| 07 | Présenter ses réalisations sur le profil | [07-profil-realisations.md](07-profil-realisations.md) | P0 |

## Règles communes

- Auth : réutiliser les hooks et appels du frontend existant, en particulier `/api/auth/me`. Aucun formulaire de connexion spécifique à Chantier. Un bouton masqué par le rôle ne remplace jamais le contrôle serveur.
- Routes API sans slash final, sous `/api/v1`, pagination `count/next/previous/results` pour les listes. Conserver page, recherche et filtres dans l’URL de l’écran.
- 400 : erreur de champ ; 401 : flux de session existant ; 403 : action non autorisée ; 404 : absent/inaccessible ; 409 : transition impossible ; 429 : attendre sans relance automatique ; 503 : expliquer l’indisponibilité et proposer l’action manuelle disponible.
- Markdown utilisateur ou IA : rendu sécurisé, HTML brut désactivé. URL externe ouverte avec les protections usuelles ; ne jamais afficher un contenu de dépôt comme du HTML exécutable.
- Prévoir chargement, état vide, échec, reprise et succès. Donner un texte utile, pas une console de données techniques. Sur mobile, une colonne et une action principale visible.
- Afficher les preuves avec leur portée exacte : « relu par… », « proposition IA à valider », « basé sur cette version ». Ni étoiles ni suggestions IA ne deviennent un score de compétence.
- Aucun secret Git ne passe dans le stockage navigateur ou les logs. Le mot de passe initial, lorsqu’il est retourné à sa création, a un affichage ponctuel et une consigne de changement dans la forge.
