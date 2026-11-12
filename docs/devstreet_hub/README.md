# DevStreet Hub — backend et préparation des interfaces

Cette étape livre la logique métier et les API dans **`backend/app/devstreet_hub`**. Aucun écran React n’est créé ou modifié. Le compte utilisateur, l’authentification, les rôles, les permissions et l’audit sont ceux de la boilerplate.

Le nom affiché est **DevStreet Hub**, et le package Python est `app.devstreet_hub`. Le label Django historique `projects` reste réservé aux migrations et aux tables déjà créées : les données ne sont pas réinitialisées. Les routes `/api/v1/projects` et les permissions `projects.*` désignent la ressource « projet » et restent stables. Les nouvelles variables du module portent le préfixe `DEVSTREET_HUB_`.

## Tester maintenant sur cette machine

- API : [http://127.0.0.1:18000/api/health](http://127.0.0.1:18000/api/health)
- Swagger : [http://127.0.0.1:18000/swagger/](http://127.0.0.1:18000/swagger/)
- Forge locale : [http://127.0.0.1:13000/](http://127.0.0.1:13000/)
- Importer [la collection Postman](testing/devstreet_hub.postman_collection.json), puis l’environnement privé `backend/.local/devstreet_hub.postman_environment.json` généré sur cette machine. Ne jamais commiter ou partager ce dernier.
- Les comptes de démonstration et leur mot de passe applicatif figurent uniquement dans `backend/.local/demo.credentials.json`. Ils utilisent le vrai système d’authentification du core.

La collection effectue 50 requêtes : création, validation des champs, droits IAM, visibilité des brouillons, provisionnement Gitea, publication, étoiles idempotentes, membres, tâche, contribution, revue, profil, preuve sélectionnable, webhooks et archivage. Elle attend explicitement une erreur 503 pour OpenAI non configuré et pour le forum non raccordé. Ce sont des cas dégradés testés, pas des intégrations annoncées comme actives.

Résultats détaillés et limites : [validation.md](validation.md). Les accès Git des seuls comptes de démonstration, préparés par le smoke test local, figurent aussi dans la section `forge` du fichier privé `demo.credentials.json`.

## Ce qui fonctionne

Projets brouillon/public/archivé, technologies sélectionnées dans un catalogue, recherche et pagination, appartenance aux projets, étoiles uniques, accès Git lié à l’utilisateur existant, dépôts Gitea privés avant publication, tâches manuelles ou issues d’une proposition IA, contributions et revue humaine, références publiques sur le profil, sélection de réalisations appartenant au candidat, événements Gitea signés et dédoublonnés.

Une contribution acceptée signifie **« revue par un mainteneur »**. Le backend ne certifie ni la maîtrise d’une technologie ni la fusion de la PR. Être membre du projet dans Django ne donne pas automatiquement le droit de pousser sur la forge.

## IA : code prêt, appel réel à configurer

Ajouter dans `backend/.env` les paramètres facultatifs suivants, puis redémarrer Django :

```dotenv
# Renseigner localement ; ne pas commiter les valeurs.
DEVSTREET_HUB_OPENAI_API_KEY=
DEVSTREET_HUB_OPENAI_MODEL=
# Facultatif : plafond de requêtes par utilisateur et par jour (défaut explicite : 20).
DEVSTREET_HUB_AI_DAILY_LIMIT=20
```

Choisir un modèle accessible à votre compte et compatible avec Responses / Structured Outputs. Aucun modèle ni prix n’est deviné. Aucun appel OpenAI facturé n’a été effectué pendant cette livraison.

Parcours : propriétaire autorise les extraits → mainteneur demande une fiche → HTTP 202 avec ID → le worker traite le SHA demandé → lecture du résultat → adoption d’une suggestion comme tâche **brouillon** → relecture et ouverture explicite.

```powershell
cd backend
.\venv\Scripts\python.exe manage.py process_devstreet_hub_analyses --limit 10
```

Le worker se lance périodiquement avec l’ordonnanceur de votre déploiement ; cette commande ne reste pas en boucle. Contexte borné à 12 fichiers et 16 000 octets au total, secrets détectés et fichiers sensibles exclus, sortie plafonnée à 2 000 tokens. Deux analyses par projet et par jour, plafond utilisateur partagé, cache par projet/version/objectif/langue/modèle/consigne. Les références doivent exister dans les extraits fournis. Aucun code utilisateur n’est exécuté. Les jobs restés en cours plus de cinq minutes sont marqués en échec lors du passage suivant du worker.

## Intégration de Gitea

Gitea est un service séparé de Django. L’app métier utilise son API ; aucun code Go n’est converti en Django.

```dotenv
DEVSTREET_HUB_GITEA_URL=https://git.votre-domaine.example
DEVSTREET_HUB_GITEA_TOKEN=
DEVSTREET_HUB_GITEA_PUBLIC_URL=https://git.votre-domaine.example
DEVSTREET_HUB_GITEA_WEBHOOK_SECRET=
```

`GITEA_PUBLIC_URL` est facultatif si l’URL d’accès interne est aussi l’URL publique. HTTPS est exigé hors développement local. Le token administratif sert au provisioning ; il ne sort jamais dans une réponse API. Le premier `POST /api/v1/forge-access` retourne un mot de passe Git initial une seule fois ; l’utilisateur doit le changer dans Gitea, puis créer son token Git personnel dans Gitea. Le mot de passe Django n’est jamais copié.

Identités Git : login opaque `ds-{instance}-{clé}` lié via `ForgeIdentity` (voir [integrations.md](integrations.md)). Ne pas rattacher un compte Gitea préexistant sur la seule base d’un login historique `devstreet-user-{id}` ou d’un e-mail. Variable optionnelle `DEVSTREET_HUB_INSTANCE_ID` (2–8 caractères `[a-z0-9]`) pour préfixer les logins lorsque plusieurs installations Django partagent la même forge.

Configurer un webhook Gitea vers `/api/v1/integrations/gitea/webhook` avec le secret déclaré et l’événement push. La signature HMAC est obligatoire ; un push met à jour l’information de fraîcheur, mais une analyse relit toujours le SHA dans Gitea.

Pour la démonstration locale, un conteneur dédié `devstreet-chantier-gitea` est utilisé, image `docker.gitea.com/gitea:28.3.0`, volume nommé du même nom, port lié uniquement à `127.0.0.1:13000`. Pas de runners ni Actions. Cette configuration locale n’est pas un déploiement Datacloud livré.

## Reprendre les tests

Depuis la racine, PowerShell :

```powershell
cd backend
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py init_devstreet_hub
.\venv\Scripts\python.exe manage.py test app.tests.test_project app.tests.test_technology app.tests.test_contributiontask app.tests.test_devstreet_hub_integrations app.tests.test_devstreet_hub_rename --keepdb
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe -m scripts.security_scan --changed-since origin/develop --fail-on warning
```

Le rôle métier **DevStreet Hub Developer** est créé dans l’IAM existant, sans être attribué automatiquement aux comptes. Le catalogue de technologies reste administré par les permissions `technologies.*`. La commande de démonstration est réservée à DEBUG et prépare les comptes locaux :

```powershell
.\venv\Scripts\python.exe manage.py seed_devstreet_hub_demo
.\venv\Scripts\python.exe scripts/prepare_devstreet_hub_postman.py
cd ..
npx --yes newman run docs/devstreet_hub/testing/devstreet_hub.postman_collection.json -e backend/.local/devstreet_hub.postman_environment.json
```

Les jetons expirent : régénérer l’environnement privé avant une nouvelle session. Pour tester le parcours IA actif, renseigner la clé et le modèle puis modifier le cas Postman 25 qui vérifie actuellement l’indisponibilité explicite. Les succès IA, sorties invalides, quotas et erreurs sont couverts par les tests automatisés avec doubles contrôlés.

## Générateur et réutilisation

La commande `python scripts/bootstrap_devstreet_hub.py` a appelé `AppCreator` puis `ImprovedCodeGenerator` pour Project, Technology et ContributionTask, avec les JSON de `scripts/models_zones/devstreet_hub`. Le mode documenté `apply_migrations=False` a évité les seeds de données fictives ; la migration finale est produite et appliquée avec les commandes Django. Les templates du générateur n’ont pas été modifiés.

Les fichiers générés sont ensuite spécialisés pour les invariants métier, les relations, la validation et les workflows. **Ne pas relancer ce bootstrap sur l’app spécialisée.** Pour une nouvelle ressource indépendante, utiliser le générateur et son JSON ; pour une régénération, comparer et préserver les adaptations. Les snapshots et analyses ne sont pas des CRUD publics.

Les générateurs frontend seront utilisés quand un écran sera effectivement abordé, à partir des JSON disponibles. Aucune génération frontend n’a été lancée ici.

## Travail avec les deux autres membres

Le forum et la marketplace ne sont pas recréés dans cette app. Les contrats sont dans [integrations.md](integrations.md). Le forum devra fournir un adaptateur idempotent ; la marketplace devra appeler le validateur de preuve et vérifier elle-même la propriété de la candidature.

Les interfaces futures sont décrites dans [interfaces/00-index.md](interfaces/00-index.md), un fichier numéroté par écran, avec regroupement fonctionnel, routes, droits et comportement UX. Aucun écran n’est déclaré implémenté.
