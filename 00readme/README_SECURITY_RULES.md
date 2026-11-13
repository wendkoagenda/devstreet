# Catalogue des règles du scanner de sécurité

Liste consultable des **43 règles** appliquées par `python -m scripts.security_scan` — sans ouvrir les scripts Python.

Pour un rappel rapide des identifiants seulement :

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m scripts.security_scan --list-rules
```

Exceptions datées : `security-exceptions.json` (racine). Fonctionnement du scanner : [backend/scripts/security_scan/README.md](../backend/scripts/security_scan/README.md).

| Gravité | Signification |
|---|---|
| critique | Risque majeur (secrets, clés) |
| erreur | Problème sérieux à corriger |
| avertissement | Risque à traiter ou excepter avec justification datée |
| info | Signal informatif |

## Index par identifiant

| Id | Gravité | Catégorie | Titre |
|---|---|---|---|
| [API-001](#api-001) | erreur | exposure | Détail d'exception renvoyé au client |
| [API-002](#api-002) | avertissement | exposure | Sérialiseur trop large (fields = "__all__" ou exclude) |
| [API-003](#api-003) | avertissement | exposure | Liste sans pagination |
| [API-004](#api-004) | avertissement | exposure | Téléversement sans contrôle de taille ou de type |
| [CFG-001](#cfg-001) | avertissement | production | En-têtes de sécurité nginx absents |
| [CFG-002](#cfg-002) | erreur | secrets | .env non ignoré par git |
| [CFG-003](#cfg-003) | avertissement | production | Source maps publiques |
| [DEP-001](#dep-001) | avertissement | supply-chain | Dépendances Python non figées |
| [DEP-002](#dep-002) | info | supply-chain | Dépendances npm en intervalle de versions |
| [DEP-003](#dep-003) | avertissement | supply-chain | package-lock.json absent |
| [DJ-001](#dj-001) | critique | production | Clé de signature avec valeur par défaut |
| [DJ-002](#dj-002) | erreur | production | DEBUG activé par défaut |
| [DJ-003](#dj-003) | erreur | production | ALLOWED_HOSTS ouvert à tous |
| [DJ-004](#dj-004) | erreur | production | CORS ouvert à toutes les origines |
| [DJ-005](#dj-005) | avertissement | auth | Route publique (AllowAny) |
| [DJ-006](#dj-006) | erreur | production | Documentation de l'API toujours exposée |
| [DJ-007](#dj-007) | avertissement | auth | Protection CSRF désactivée |
| [DJ-008](#dj-008) | avertissement | production | Réglages HTTP sécurisés absents |
| [DJ-009](#dj-009) | avertissement | auth | Politique de mot de passe trop faible |
| [DJ-010](#dj-010) | erreur | production | Admin Django toujours exposé |
| [DJ-011](#dj-011) | avertissement | data | Migration destructive |
| [DOCKER-001](#docker-001) | avertissement | supply-chain | Conteneur exécuté en root |
| [DOCKER-002](#docker-002) | erreur | supply-chain | Secret passé par ARG ou ENV |
| [DOCKER-003](#docker-003) | avertissement | supply-chain | Image de base non épinglée |
| [FB-001](#fb-001) | avertissement | fallback | Variable d'environnement Python avec valeur de repli |
| [FB-002](#fb-002) | avertissement | fallback | Variable d'environnement JS/TS avec valeur de repli |
| [FB-003](#fb-003) | avertissement | fallback | Exception avalée en Python |
| [FB-004](#fb-004) | avertissement | fallback | Erreur avalée en JS/TS |
| [FB-005](#fb-005) | avertissement | fallback | Valeur de repli dans un script ou un Dockerfile |
| [FE-001](#fe-001) | erreur | frontend | Jeton stocké dans le navigateur |
| [FE-002](#fe-002) | avertissement | frontend | Injection HTML directe |
| [FE-003](#fe-003) | avertissement | frontend | Lien target="_blank" sans rel |
| [FE-004](#fe-004) | erreur | frontend | Variable VITE_ au nom de secret |
| [PY-001](#py-001) | erreur | injection | Appel Python dangereux |
| [PY-002](#py-002) | erreur | injection | SQL construit par concaténation |
| [RT-001](#rt-001) | erreur | api | Route d'API sans version |
| [RT-002](#rt-002) | erreur | api | Aucune limitation de débit par défaut |
| [RT-003](#rt-003) | avertissement | api | Route publique ou limitation désactivée sans limite propre |
| [RT-004](#rt-004) | avertissement | api | Tag Swagger incorrect |
| [RT-005](#rt-005) | avertissement | api | Route sans tag Swagger |
| [SEC-001](#sec-001) | critique | secrets | Secret codé en dur |
| [SEC-002](#sec-002) | critique | secrets | Fichier sensible versionné |
| [SUP-001](#sup-001) | avertissement | supply-chain | Aucune analyse des dépendances vulnérables |

## Categorie : api

### RT-001

**Route d'API sans version**

- **Gravite** : erreur
- **Categorie** : api
- **Description** : Une route est déclarée sans préfixe de version (v1/, v2/…). Sans version, tout changement de contrat casse les clients existants (frontend déployé séparément, intégrations, mobiles).
- **Recommandation** : Placer la route sous un préfixe versionné (path("v1/", include(...)) ou /api/v1/...). Les routes d'administration et de documentation sont exclues.

### RT-002

**Aucune limitation de débit par défaut**

- **Gravite** : erreur
- **Categorie** : api
- **Description** : REST_FRAMEWORK ne définit pas DEFAULT_THROTTLE_CLASSES : les routes qui ne déclarent pas leur propre limite (toute l'API métier) peuvent être appelées sans restriction (force brute, scraping, déni de service).
- **Recommandation** : Définir DEFAULT_THROTTLE_CLASSES (AnonRateThrottle et UserRateThrottle) et les taux anon / user dans DEFAULT_THROTTLE_RATES.

### RT-003

**Route publique ou limitation désactivée sans limite propre**

- **Gravite** : avertissement
- **Categorie** : api
- **Description** : Une vue accessible sans authentification (AllowAny, vues SimpleJWT) ne déclare pas de throttle_classes propre, ou une vue désactive la limitation avec throttle_classes = []. Les routes publiques sont les plus attaquées.
- **Recommandation** : Déclarer throttle_classes avec un taux dédié (comme LoginThrottle) sur chaque route publique, et ne jamais vider throttle_classes.

### RT-004

**Tag Swagger incorrect**

- **Gravite** : avertissement
- **Categorie** : api
- **Description** : Le tag d'une route Swagger ne suit pas la convention : « V<n> - <Ressource> » pour un ViewSet (version du router et nom de la ressource), « Auth » pour les vues d'authentification. Un mauvais tag range la route dans le mauvais groupe de la documentation (copier-coller entre ressources, version obsolète).
- **Recommandation** : Corriger tags=[...] dans @swagger_auto_schema : par exemple RoleViewSet monté sous v1/ -> tags=["V1 - Role"].

### RT-005

**Route sans tag Swagger**

- **Gravite** : avertissement
- **Categorie** : api
- **Description** : Une action de ViewSet (list, create, retrieve, update, partial_update, destroy, @action) ou une vue d'API n'a pas de @swagger_auto_schema avec tags : drf-yasg la range dans un groupe par défaut, sans version ni nom de ressource.
- **Recommandation** : Ajouter @swagger_auto_schema(tags=["V1 - <Ressource>"]) (ou ["Auth"]) sur l'action.

## Categorie : auth

### DJ-005

**Route publique (AllowAny)**

- **Gravite** : avertissement
- **Categorie** : auth
- **Description** : Une vue DRF est accessible sans authentification. C'est parfois voulu (connexion, mot de passe oublié), mais doit être justifié.
- **Recommandation** : Utiliser IsAuthenticated ou une permission métier. Si la route doit rester publique, l'ajouter aux exceptions avec une justification et ajouter une limitation de débit.

### DJ-007

**Protection CSRF désactivée**

- **Gravite** : avertissement
- **Categorie** : auth
- **Description** : csrf_exempt retire la protection CSRF d'une vue.
- **Recommandation** : Retirer le décorateur ; pour une API à jetons Bearer le risque est faible mais doit être justifié.

### DJ-009

**Politique de mot de passe trop faible**

- **Gravite** : avertissement
- **Categorie** : auth
- **Description** : AUTH_PASSWORD_VALIDATORS est absent, incomplet, ou MinimumLengthValidator accepte moins de 10 caractères (8 par défaut dans Django). Les mots de passe courts ou prévisibles se devinent en quelques essais.
- **Recommandation** : Garder les 4 validateurs de Django et fixer OPTIONS {"min_length": 12} (au moins 10).

## Categorie : data

### DJ-011

**Migration destructive**

- **Gravite** : avertissement
- **Categorie** : data
- **Description** : Une migration supprime un champ, un modèle ou des données (RemoveField, DeleteModel, RunSQL DROP/DELETE/TRUNCATE) : les données sont perdues et l'ancienne version du code, encore en ligne pendant le déploiement, casse.
- **Recommandation** : Déployer d'abord une version qui n'utilise plus le champ, sauvegarder la base, puis déclarer la migration dans security-exceptions.json (relue, datée, attribuée).

## Categorie : exposure

### API-001

**Détail d'exception renvoyé au client**

- **Gravite** : erreur
- **Categorie** : exposure
- **Description** : Une réponse HTTP contient le message d'une exception interne (str(e), e.args, traceback) : chemins, noms de tables, requêtes SQL ou détails de configuration deviennent visibles par l'appelant. Les erreurs de validation (*ValidationError), faites pour être lues par l'utilisateur, sont exclues.
- **Recommandation** : Journaliser l'exception côté serveur (logger.exception) et renvoyer un message générique et stable (« Opération impossible »), avec un code d'erreur si le client doit réagir.

### API-002

**Sérialiseur trop large (fields = "__all__" ou exclude)**

- **Gravite** : avertissement
- **Categorie** : exposure
- **Description** : fields = "__all__" ou exclude exposent automatiquement tout nouveau champ du modèle (mot de passe haché, champs internes, données personnelles) et l'acceptent en écriture (assignation en masse).
- **Recommandation** : Lister explicitement les champs exposés (fields = [...]) et déclarer read_only_fields.

### API-003

**Liste sans pagination**

- **Gravite** : avertissement
- **Categorie** : exposure
- **Description** : Une route renvoie une collection entière : pagination désactivée (pagination_class = None), absente des réglages, taille de page excessive, ou action de ViewSet qui sérialise une liste (many=True) sans paginer. Une table volumineuse devient un déni de service (mémoire, temps de réponse) et une fuite en masse.
- **Recommandation** : Définir DEFAULT_PAGINATION_CLASS et un PAGE_SIZE raisonnable (100 au plus), et dans chaque action de liste appeler self.paginate_queryset(...) puis self.get_paginated_response(...).

### API-004

**Téléversement sans contrôle de taille ou de type**

- **Gravite** : avertissement
- **Categorie** : exposure
- **Description** : Un fichier qui traite des téléversements (request.FILES, UploadedFile, FileField de sérialiseur) ne contrôle pas sa taille ou son type : saturation du disque, fichiers exécutables ou HTML servis depuis votre domaine (XSS stocké).
- **Recommandation** : Vérifier la taille maximale ET une liste blanche d'extensions/types avant d'enregistrer le fichier (voir app/metier/utils/file_field_utils.py), et limiter la taille du corps de requête au proxy.

## Categorie : fallback

### FB-001

**Variable d'environnement Python avec valeur de repli**

- **Gravite** : avertissement
- **Categorie** : fallback
- **Description** : os.getenv(nom, defaut), os.environ.get(nom, defaut), os.getenv(nom) or defaut ou getattr(settings, nom, defaut) : une variable oubliée est remplacée en silence par une valeur qui peut être fausse en production.
- **Recommandation** : Lire la variable sans valeur par défaut et échouer au démarrage si elle manque (os.environ[nom], ou une fonction qui lève ImproperlyConfigured). Un défaut réellement voulu se justifie en exception.

### FB-002

**Variable d'environnement JS/TS avec valeur de repli**

- **Gravite** : avertissement
- **Categorie** : fallback
- **Description** : import.meta.env.X ?? defaut ou process.env.X || defaut : une variable de build oubliée est remplacée en silence (URL d'API vide, mauvais serveur, fonctionnalité muette).
- **Recommandation** : Vérifier la variable au démarrage et lever une erreur explicite si elle manque, plutôt que de la remplacer.

### FB-003

**Exception avalée en Python**

- **Gravite** : avertissement
- **Categorie** : fallback
- **Description** : Un bloc except ne fait que pass/continue, ou renvoie une valeur constante (avec ou sans journal) : l'erreur disparaît pour l'appelant et le programme continue avec un état faux.
- **Recommandation** : Relancer l'erreur, ou la traiter précisément (message à l'utilisateur, réessai). Un journal seul ne suffit pas quand une valeur de repli est renvoyée.

### FB-004

**Erreur avalée en JS/TS**

- **Gravite** : avertissement
- **Categorie** : fallback
- **Description** : catch vide, catch qui renvoie une constante (même après un console.error) et .catch(() => null) font disparaître l'erreur : l'interface continue avec des données fausses sans que personne ne le sache.
- **Recommandation** : Journaliser, afficher un message à l'utilisateur ou relancer. Si l'erreur est vraiment ignorable, le dire dans un commentaire et une exception.

### FB-005

**Valeur de repli dans un script ou un Dockerfile**

- **Gravite** : avertissement
- **Categorie** : fallback
- **Description** : ${VAR:-defaut} dans un script, un fichier compose ou un workflow, ou ARG NOM=valeur dans un Dockerfile : la variable manquante est remplacée en silence au lieu de faire échouer le déploiement.
- **Recommandation** : Exiger la variable (${VAR:?message}) pour échouer avec un message clair.

## Categorie : frontend

### FE-001

**Jeton stocké dans le navigateur**

- **Gravite** : erreur
- **Categorie** : frontend
- **Description** : Un JWT lu ou écrit dans localStorage/sessionStorage est exfiltrable par n'importe quelle faille XSS.
- **Recommandation** : Utiliser des cookies HttpOnly posés par le serveur (voir 00readme/README_SAME_ORIGIN_COOKIES.md).

### FE-002

**Injection HTML directe**

- **Gravite** : avertissement
- **Categorie** : frontend
- **Description** : dangerouslySetInnerHTML ou innerHTML insèrent du HTML non filtré : risque de XSS.
- **Recommandation** : Afficher du texte via React, ou assainir le HTML (DOMPurify) avant insertion.

### FE-003

**Lien target="_blank" sans rel**

- **Gravite** : avertissement
- **Categorie** : frontend
- **Description** : Un lien qui s'ouvre dans un nouvel onglet sans rel="noopener noreferrer" donne un accès à la page d'origine.
- **Recommandation** : Ajouter rel="noopener noreferrer".

### FE-004

**Variable VITE_ au nom de secret**

- **Gravite** : erreur
- **Categorie** : frontend
- **Description** : Toute variable VITE_* est copiée dans le JavaScript public. Un secret qui y est placé est lisible par tous.
- **Recommandation** : Ne jamais préfixer un secret par VITE_ : il doit rester côté serveur.

## Categorie : injection

### PY-001

**Appel Python dangereux**

- **Gravite** : erreur
- **Categorie** : injection
- **Description** : eval, exec, os.system, pickle ou subprocess avec shell=True permettent l'injection de code ou de commande.
- **Recommandation** : Utiliser une alternative sûre (ast.literal_eval, json, subprocess avec une liste d'arguments).

### PY-002

**SQL construit par concaténation**

- **Gravite** : erreur
- **Categorie** : injection
- **Description** : Une requête SQL (execute, raw, extra) est construite avec une f-string, un format ou une concaténation.
- **Recommandation** : Utiliser des paramètres : cursor.execute("... %s", [valeur]) ou l'ORM.

## Categorie : production

### CFG-001

**En-têtes de sécurité nginx absents**

- **Gravite** : avertissement
- **Categorie** : production
- **Description** : Le serveur web ne pose ni X-Content-Type-Options, ni X-Frame-Options, ni politique de sécurité de contenu.
- **Recommandation** : Ajouter les en-têtes (add_header ... always) ou inclure un fichier security-headers.conf.

### CFG-003

**Source maps publiques**

- **Gravite** : avertissement
- **Categorie** : production
- **Description** : sourcemap: true publie le code source lisible du frontend en production.
- **Recommandation** : Désactiver les source maps de production, ou les téléverser vers un outil de suivi d'erreurs privé.

### DJ-001

**Clé de signature avec valeur par défaut**

- **Gravite** : critique
- **Categorie** : production
- **Description** : SECRET_KEY ou JWT_SIGNING_KEY a une valeur littérale ou une valeur de repli : en production, tout le monde la connaît.
- **Recommandation** : Lire la clé sans valeur par défaut et refuser de démarrer si elle manque (voir config/env_secrets.py).

### DJ-002

**DEBUG activé par défaut**

- **Gravite** : erreur
- **Categorie** : production
- **Description** : DEBUG vaut True en dur ou par défaut : pages d'erreur détaillées, variables et chemins exposés.
- **Recommandation** : Lire DEBUG depuis l'environnement avec False comme valeur par défaut.

### DJ-003

**ALLOWED_HOSTS ouvert à tous**

- **Gravite** : erreur
- **Categorie** : production
- **Description** : ALLOWED_HOSTS contient "*" : attaques par en-tête Host (liens de réinitialisation empoisonnés, cache).
- **Recommandation** : Lister les noms de domaine réels.

### DJ-004

**CORS ouvert à toutes les origines**

- **Gravite** : erreur
- **Categorie** : production
- **Description** : CORS_ALLOW_ALL_ORIGINS à True : n'importe quel site peut appeler l'API depuis le navigateur d'un utilisateur.
- **Recommandation** : Lister les origines autorisées dans CORS_ALLOWED_ORIGINS.

### DJ-006

**Documentation de l'API toujours exposée**

- **Gravite** : erreur
- **Categorie** : production
- **Description** : Les routes Swagger/ReDoc sont déclarées sans condition : le schéma complet de l'API est public en production.
- **Recommandation** : Ne les ajouter que si un réglage (ENABLE_API_DOCS) l'autorise, ou les protéger par une permission.

### DJ-008

**Réglages HTTP sécurisés absents**

- **Gravite** : avertissement
- **Categorie** : production
- **Description** : Cookies Secure et HSTS ne sont pas configurés (ou sont désactivés en dur) : cookies et sessions peuvent circuler en clair.
- **Recommandation** : Définir SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE et SECURE_HSTS_SECONDS (actifs hors DEBUG).

### DJ-010

**Admin Django toujours exposé**

- **Gravite** : erreur
- **Categorie** : production
- **Description** : La route /admin/ est déclarée sans condition : l'interface d'administration est publique en production et contourne les règles d'accès de l'API.
- **Recommandation** : Ne l'ajouter que si un réglage (ENABLE_ADMIN) l'autorise.

## Categorie : secrets

### CFG-002

**.env non ignoré par git**

- **Gravite** : erreur
- **Categorie** : secrets
- **Description** : Aucune règle du .gitignore racine ne protège les fichiers .env : ils risquent d'être commités.
- **Recommandation** : Ajouter .env et .env.* (sauf *.example) au .gitignore.

### SEC-001

**Secret codé en dur**

- **Gravite** : critique
- **Categorie** : secrets
- **Description** : Une clé, un mot de passe ou un token figure en clair dans un fichier versionné.
- **Recommandation** : Retirer la valeur du dépôt, la révoquer/régénérer (elle est compromise), puis la lire depuis une variable d'environnement.

### SEC-002

**Fichier sensible versionné**

- **Gravite** : critique
- **Categorie** : secrets
- **Description** : Un fichier d'environnement, une clé privée, une base locale ou un journal est suivi par git.
- **Recommandation** : Le retirer du suivi (git rm --cached), l'ajouter à .gitignore, et régénérer les secrets qu'il contenait.

## Categorie : supply-chain

### DEP-001

**Dépendances Python non figées**

- **Gravite** : avertissement
- **Categorie** : supply-chain
- **Description** : Des dépendances sont déclarées avec >=, ~= ou sans version : le build peut installer une version différente ou compromise.
- **Recommandation** : Figer chaque version avec == (et mettre à jour volontairement).

### DEP-002

**Dépendances npm en intervalle de versions**

- **Gravite** : info
- **Categorie** : supply-chain
- **Description** : package.json utilise des intervalles (^, ~, *, latest). Avec un package-lock.json et npm ci le build reste reproductible (voir DEP-003 si le lock manque).
- **Recommandation** : Versionner package-lock.json et installer avec npm ci.

### DEP-003

**package-lock.json absent**

- **Gravite** : avertissement
- **Categorie** : supply-chain
- **Description** : Sans package-lock.json, deux installations successives peuvent donner des versions différentes.
- **Recommandation** : Générer et versionner package-lock.json.

### DOCKER-001

**Conteneur exécuté en root**

- **Gravite** : avertissement
- **Categorie** : supply-chain
- **Description** : L'étage final n'a pas d'instruction USER (ou utilise root) : une faille dans l'application donne les droits root du conteneur.
- **Recommandation** : Créer un utilisateur sans privilèges et l'activer avec USER avant CMD.

### DOCKER-002

**Secret passé par ARG ou ENV**

- **Gravite** : erreur
- **Categorie** : supply-chain
- **Description** : Un ARG ou ENV au nom de secret est enregistré dans les couches de l'image et lisible avec docker history.
- **Recommandation** : Fournir le secret à l'exécution (variable du conteneur) ou, au build, avec RUN --mount=type=secret.

### DOCKER-003

**Image de base non épinglée**

- **Gravite** : avertissement
- **Categorie** : supply-chain
- **Description** : L'image de base n'a pas de tag (ou utilise :latest) : le build n'est pas reproductible et peut changer sans prévenir.
- **Recommandation** : Indiquer une version précise (python:3.12-slim-bookworm), idéalement avec son digest @sha256.

### SUP-001

**Aucune analyse des dépendances vulnérables**

- **Gravite** : avertissement
- **Categorie** : supply-chain
- **Description** : Ni Dependabot (.github/dependabot.yml) ni une étape d'audit (pip-audit, npm audit, osv-scanner) dans un workflow : une dépendance avec une faille connue reste en production sans que personne ne soit prévenu.
- **Recommandation** : Ajouter .github/dependabot.yml (écosystèmes pip et npm) et/ou un workflow qui lance pip-audit et npm audit.

