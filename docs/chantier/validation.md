# Validation du backend — 12 novembre 2026

## Résultats vérifiés

| Contrôle | Résultat |
| --- | --- |
| Suite backend complète | **644 tests réussis**, PostgreSQL 18, base Unicode ICU ; environ 95 secondes avec hacheur rapide limité au processus de test |
| Tests ciblés Chantier | **51 tests réussis** : droits, visibilité, transitions, quotas, provenance IA, revue, forum contractuel, webhooks et Swagger |
| Postman / Newman | **50 requêtes, 51 assertions réussies**, contre le serveur Django réel et Gitea local |
| Forge réelle | Lecture Git et push du propriétaire réussis ; push d’un tiers sans droit refusé ; collecte de deux fichiers au SHA réussi ; tokens temporaires révoqués |
| Swagger | Schéma généré et interrogé ; routes de workflows et corps de requêtes présents ; aucune vérification par navigateur automatisé |
| Django check | Aucun problème détecté |
| Migrations | Migration initiale projects appliquée ; `makemigrations --check --dry-run` ne détecte aucun changement manquant |
| Générateur | `--sync` et `--validate` réussis après spécialisation |
| Scanner sur les changements | **100/100, aucun nouveau signalement** ; aucune règle, baseline ou exception de sécurité modifiée pour passer le contrôle |
| Qualité Python | Black et flake8 (erreurs F) réussis sur l’app et ses nouveaux tests/scripts |
| Frontend | Aucun fichier modifié, aucun écran généré, aucun build frontend lancé |

La suite complète utilise le hacheur MD5 exclusivement dans son processus de test afin d’accélérer les fixtures. Aucun réglage serveur ni mot de passe de démonstration n’a été converti en MD5. La connexion réelle Postman a utilisé le hachage normal de la boilerplate.

## Incident d’environnement résolu

Une première exécution complète a échoué sur un test existant de recherche « CAFÉ » dans la boilerplate. La base locale initiale utilisait la collation `C` : `upper('café')` renvoyait `CAFé`. Une base ICU Unicode a été préparée avec `TEMPLATE template0`, les données locales ont été préservées, puis les 644 tests ont réussi sans modification du code du module existant. L’ancienne base locale a été conservée.

Sur cette machine : base de développement `devstreet_chantier_unicode`, port PostgreSQL local dédié `55432`. Le rôle et les secrets figurent uniquement dans `.env` et `.local`. Les commandes de reprise utilisent `--keepdb` pour réutiliser la base de tests Unicode préparée. Sur une autre machine, vérifier la collation de la base si la recherche avec accents échoue. [Référence PostgreSQL](https://www.postgresql.org/docs/18/sql-createdatabase.html)

## Limites vérifiées et déclarées

- **OpenAI : aucun appel réel facturé.** Le client SDK, la file, les références et les erreurs sont testés avec des doubles contrôlés. Clé et modèle doivent être renseignés localement avant un test réel. La collection vérifie actuellement le 503 attendu sans configuration.
- **Forum : app absente à ce stade.** Le contrat et l’idempotence sont testés avec un adaptateur de test ; en fonctionnement normal, l’absence d’adaptateur donne 503 et ne crée aucun faux sujet.
- **Marketplace : app absente à ce stade.** Le service de validation et la route d’admissibilité sont livrés ; le membre responsable doit créer sa liaison aux candidatures et vérifier la propriété de celles-ci.
- Le test Git utilise seulement un dépôt synthétique dans la forge locale. Le dépôt source devstreet n’y a pas été poussé.
- Aucun déploiement Datacloud, test de charge, audit complet des dépendances/licences ni interface React n’est revendiqué.

Les erreurs 400/401/403/404/409/429/503 affichées pendant les tests correspondent aux cas négatifs contrôlés. Un rapport temporaire produit par un test de scanner n’est pas le résultat du scanner réel des changements.
