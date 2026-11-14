# 🚀 Générateur d'API CRUD Robuste avec State Management

Ce système permet de générer automatiquement des APIs CRUD complètes avec architecture Repository Pattern à partir de modèles JSON. **Version 2.0 - Robuste et Fiable**

## 🆕 Nouveautés Version 2.0

- ✅ **Gestion cumulative** des fichiers partagés (models.py, serializers.py)
- ✅ **Système de backup** automatique avant chaque modification
- ✅ **Validation post-génération** (syntaxe Python + imports)
- ✅ **Synchronisation automatique** avec le système de fichiers
- ✅ **Checksums MD5** pour détecter les modifications manuelles
- ✅ **Rollback automatique** en cas d'erreur
- ✅ **Interface enrichie** avec 8 options interactives
- ✅ **Modes CLI** pour l'automatisation
- ✅ **Rapports d'intégrité** détaillés

## 📁 Structure

```
scripts/
├── generator/
│   ├── state_manager.py         # Gestionnaire de state robuste
│   ├── schema_validator.py      # Validateur de schéma JSON
│   ├── code_generator.py        # Générateur de code amélioré
│   └── templates/               # Templates Jinja2
│       ├── model.py.j2
│       ├── interface.py.j2
│       ├── repository.py.j2
│       ├── service.py.j2
│       ├── viewset.py.j2
│       ├── serializer.py.j2
│       ├── permissions.py.j2
│       └── tests.py.j2
├── models_zones/                # Zones de modèles
│   ├── zone_1/
│   │   └── template.json
│   ├── zone_2/
│   └── ...
├── generate_api.py             # Script principal (v2.0)
├── test_fix.py                 # Tests de validation
├── CORRECTION_REPORT.md        # Documentation des corrections
└── README.md                   # Cette documentation
```

## 🎯 Fonctionnalités Principales

### **Gestion Robuste des Fichiers**

- **Merge intelligent** : Préserve les modèles existants lors de l'ajout de nouveaux
- **Backups automatiques** : Sauvegarde avant chaque modification avec timestamp
- **Validation syntaxique** : Vérifie la syntaxe Python des fichiers générés
- **Rollback automatique** : Restaure les backups en cas d'erreur

### **State Management Avancé**

- **Synchronisation automatique** avec le système de fichiers
- **Détection des modifications** manuelles via checksums MD5
- **Nettoyage automatique** des entrées obsolètes
- **Validation d'intégrité** du state avec rapports détaillés

### **Architecture Complète**

- ✅ **Relations cross-zones** entre modèles de zones différentes
- ✅ **Architecture Repository Pattern** complète
- ✅ **Décorateurs Swagger** automatiques avec tag "V1"
- ✅ **Permissions CRUD** automatiques
- ✅ **Tests unitaires** générés automatiquement
- ✅ **Commentaires en français**

## 📋 Utilisation

### 1. **Mode Interactif (Recommandé)**

```bash
cd backend
python scripts/generate_api.py
```

**Menu interactif (extrait) :**

```text
--- Backend ---
  1. Generer l'API d'un ou plusieurs modeles
  2. Lister les APIs generees
  3. Creer une relation entre modeles existants
  4. Creer une nouvelle application Django
  5. Lancer les tests unitaires d'un modele

--- Frontend ---
  6. Generer l'interface frontend d'un ou plusieurs modeles
  7. Lister les interfaces frontend generees

--- General ---
  8. Generer l'API et l'interface (un ou plusieurs modeles)
  9. Afficher les statistiques
 10. Synchroniser avec le systeme de fichiers
 11. Valider l'integrite du state
 12. Creer un rapport d'integrite
 13. Mode debug - Afficher le state complet
 14. Quitter
```

**Sélection de plusieurs modèles** (options 1, 6 et 8) : saisissez les numéros séparés par des virgules (`1,2,3`), une plage (`1-3`), un mélange (`1, 3-5`) ou `tous`. Les modèles sont traités dans l'ordre saisi et un échec n'interrompt pas les suivants : un résumé final indique, par modèle, le résultat de l'API et de l'interface. Avec l'option 8, l'interface d'un modèle n'est générée que si son API l'a été. La liste affiche le statut API (option 1), le statut interface (option 6), ou les deux (option 8). Si une API ou une interface est déjà générée, une confirmation unique est demandée avant régénération (refuser ignore les modèles concernés, sans bloquer les autres). L'application cible (`app_name`) de chaque modèle s'affiche dans la liste. Le statut interface est mémorisé dans `improved_state.json` (`generated_frontends`) et détecté aussi via `frontend/src/models/<modele>/api.ts`.

### 2. **Mode Non-Interactif (CLI)**

```bash
# Générer une API backend spécifique
python scripts/generate_api.py --generate Elitest --zone zone_1

# Plusieurs modèles à la fois (séparés par des virgules, même zone)
python scripts/generate_api.py --generate Elitest,Dragon,Fusion --zone zone_1

# API et interface en une seule fois
python scripts/generate_api.py --generate Elitest,Dragon --with-frontend

# Générer l'interface frontend pour un modèle (ou plusieurs) déjà décrit en JSON
python scripts/generate_api.py --frontend Elitest
python scripts/generate_api.py --frontend Elitest,Dragon

# Synchroniser le state avec le système de fichiers
python scripts/generate_api.py --sync

# Valider l'intégrité du state
python scripts/generate_api.py --validate

# Générer un rapport d'intégrité
python scripts/generate_api.py --report
```

Codes de sortie de `--generate` et `--frontend` : `0` tout a réussi, `1` JSON du modèle introuvable, `2` schéma invalide (ou option incorrecte), `3` génération échouée. Avec plusieurs modèles, le code le plus élevé parmi les échecs est retourné.

### 3. **Upload des Modèles**

Placez vos fichiers JSON dans les zones appropriées :

```bash
# Exemple pour zone_1
cp votre_modele.json scripts/models_zones/zone_1/
```

### Génération frontend : sécurité

La génération frontend (`--frontend` / option 6) modifie 5 fichiers existants (`store.ts`, `App.tsx`,
`constants.ts`, `use-permissions.tsx`, `general-menu.tsx`) en s'appuyant sur des repères de texte.

- si un repère est introuvable, la génération **s'arrête avec un message explicite** (plus d'insertion ignorée en silence) ;
- tous les fichiers touchés sont alors **restaurés** et les fichiers créés sont supprimés (rollback complet) ;
- après la génération, le générateur relit les fichiers pour vérifier que le modèle y est bien enregistré ;
- les fins de ligne (CRLF/LF) des fichiers existants sont conservées, sans diff parasite ;
- la génération est idempotente : la relancer ne duplique ni route, ni reducer, ni permission.

### 4. **Format JSON des modèles**

Référence complète basée sur `scripts/models_zones/zone_1/elitest.json`.

#### Exemple complet

```json
{
  "model_name": "Elitest",
  "app_name": "metier",
  "fields": [
    {
      "name": "id",
      "type": "AutoField",
      "primary_key": true
    },
    {
      "name": "uuid",
      "type": "UUIDField",
      "default": "uuid.uuid4",
      "editable": false,
      "unique": true,
      "visible_in_table": false,
      "visible_in_dialog": false
    },
    {
      "name": "titre",
      "type": "CharField",
      "max_length": 200,
      "blank": false,
      "null": false
    },
    {
      "name": "description",
      "type": "TextField",
      "blank": true,
      "null": true
    },
    {
      "name": "prix",
      "type": "DecimalField",
      "max_digits": 10,
      "decimal_places": 2,
      "blank": false,
      "null": false
    }
  ],
  "meta": {
    "db_table": "metier_elitest",
    "verbose_name": "Elitest",
    "verbose_name_plural": "Elitests",
    "resource_plural": "elitests",
    "ordering": ["-created_at"]
  }
}
```

#### Attributs à la racine du fichier

| Attribut      | Obligatoire | Description |
| ------------- | ----------- | ----------- |
| `model_name`  | Oui         | Nom du modèle Django (PascalCase recommandé, ex. `Elitest`) |
| `app_name`    | Non         | Application cible (défaut : `metier`), voir « Application cible » ci-dessous |
| `fields`      | Oui         | Liste des champs du modèle |
| `meta`        | Non         | Options `Meta` Django (`db_table`, `verbose_name`, `ordering`, etc.) |
| `permissions` | Non         | Permissions personnalisées supplémentaires (liste) |

#### Application cible (`app_name`)

`app_name` désigne l'application Django qui reçoit tout le code du modèle : `models.py`, `serializers.py`, `urls.py`, interface, repository, service, ViewSet, permissions et seed, ainsi que les imports (`from app.<app_name>.models import ...`), la table par défaut (`<app_name>_<resource_plural>`) et les migrations (`makemigrations <app_name>` puis `migrate`). Sans `app_name`, c'est `metier`. Après les migrations réussies, le générateur exécute aussi `seed_<modele>` (permissions + rôles Admin / Super Admin + données de démo) ; rechargez la session front pour voir les menus.

- **L'application doit exister** : le générateur ne la crée jamais implicitement. Créez-la par le menu interactif (option « Créer une application »), qui ajoute `app.<nom>` à `LOCAL_APPS` et un `include` dans `config/urls.py`. Une application absente fait échouer la génération sans rien écrire.
- **Unicité dans tout le projet** : le nom du modèle, `meta.db_table` et `meta.resource_plural` ne peuvent pas être partagés entre deux applications (les routes sont toutes sous `/api/v1/`). Un conflit refuse la génération, avec le détail. Copier un JSON existant impose donc de changer aussi `meta`.
- **Utilitaires partagés** : `storage_service` et `utils/` (téléversements) restent dans `app/metier/` ; les applications générées les importent depuis là.
- **Relations entre applications** : `--link` (option 3) relie deux modèles même s'ils sont dans des applications différentes (ex. `Produit` dans `metier`, `Categorie` dans `yango`). Le champ est ajouté dans l'application du modèle source et référence `'<app_cible>.<Modèle>'`. Ensuite le générateur lance `makemigrations` puis `migrate` **sans** préciser l'application (Django détecte les changements, y compris cross-app). Le `serializers.py` source importe le modèle cible, et la partie inverse est injectée dans le `serializers.py` de la cible. L'application de chaque modèle est lue dans `improved_state.json`, la relation y est enregistrée avec `app_label` (source) et `target_app_label` (cible) et rejouée si l'un des deux modèles est régénéré. Si une étape de linkage échoue, les fichiers modifiés sont restaurés. Éviter les relations circulaires entre deux applications (A → B et B → A) : leurs migrations deviennent interdépendantes.
- **Changer `app_name` d'un modèle déjà généré** génère le code dans la nouvelle application et laisse l'ancien dans l'ancienne : le supprimer à la main.
- Le fichier d'état `improved_state.json` enregistre l'application de chaque API (`app_name`). Les checksums des applications autres que `metier` sont préfixés (`yango::models.py`).

#### Objet `meta`

| Attribut               | Description |
| ---------------------- | ----------- |
| `db_table`             | Nom de la table SQL |
| `verbose_name`         | Libellé singulier |
| `verbose_name_plural`  | Libellé pluriel |
| `resource_plural`      | **Obligatoire.** Pluriel explicite pour routes API, permissions et frontend (ex. `"analyses"` pour `Analysis`, `"cities"` pour `City`). Override niveau 3 — ne pas laisser le générateur deviner le pluriel |
| `ordering`             | Tri par défaut (ex. `["-created_at"]`) |

#### Pluriel des ressources — override explicite (niveau 3)

`meta.resource_plural` est **obligatoire** dans chaque JSON de modèle. Il pilote les routes API (`/api/v1/{resource_plural}/`), les codes de permissions (`{resource_plural}.view`), le frontend et les dossiers `FileField` par défaut.

Ne pas compter sur une pluralisation automatique : l'anglais a trop d'exceptions (`City` → `cities`, `Analysis` → `analyses`, etc.).

| Modèle      | `resource_plural` |
| ----------- | ----------------- |
| `Elitest`   | `elitests`        |
| `City`      | `cities`          |
| `Analysis`  | `analyses`        |
| `University`| `universities`    |

#### Attributs par champ (`fields[]`)

Chaque entrée doit contenir au minimum `name` et `type`.

**Identification et type**

| Attribut | Backend | Frontend | Description |
| -------- | ------- | -------- | ----------- |
| `name`   | Oui     | Oui      | Nom du champ en Python (snake_case) |
| `type`   | Oui     | Oui      | Type Django (voir tableau ci-dessous) |

**Paramètres Django (transmis au modèle / serializer)**

| Attribut          | Description |
| ----------------- | ----------- |
| `max_length`      | Longueur max (`CharField`) |
| `max_digits`      | Chiffres totaux (`DecimalField`) |
| `decimal_places`  | Décimales (`DecimalField`) |
| `blank`           | Autorise une valeur vide en formulaire Django (`blank=True`) |
| `null`            | Autorise `NULL` en base (`null=True`) |
| `default`         | Valeur par défaut (ex. `"uuid.uuid4"` pour un UUID) |
| `unique`          | Contrainte d'unicité |
| `editable`        | Champ modifiable ou non |
| `verbose_name`    | Libellé du champ |
| `help_text`       | Texte d'aide |
| `choices`         | Liste de choix prédéfinis |
| `upload_folder`   | Dossier de stockage relatif pour `FileField` (snake_case, sans `/` initial) |
| `allowed_extensions` | Extensions autorisées pour `FileField` (ex. `[".pdf", ".png"]`) |
| `max_size_mb`     | Taille max en Mo pour `FileField` (défaut : 10) |
| `auto_now`        | Mise à jour automatique à chaque save (`DateTimeField`) |
| `auto_now_add`    | Renseigné à la création uniquement |
| `to`              | Modèle cible (`ForeignKey`, etc.) |
| `on_delete`       | Comportement à la suppression (`CASCADE`, `RESTRICT`, …) |
| `related_name`    | Nom de la relation inverse |
| `constraints`     | Ancien format : `PK`, `UK`, `NOT NULL`, `AUTO_INCREMENT` (format legacy) |
| `options`         | Objet imbriqué : mêmes clés que ci-dessus si vous préférez les regrouper |

Les clés peuvent être placées **directement sur le champ** ou dans `options` (les deux sont fusionnés par le validateur).

**Affichage frontend uniquement** (ignorées par le générateur backend API)

| Attribut             | Description |
| -------------------- | ----------- |
| `visible_in_table`   | Afficher la colonne dans le tableau de liste React |
| `visible_in_dialog`  | Afficher le champ dans les dialogues **Show**, **Create** et **Edit** |
| `widget`             | Surcharge du composant UI. Valeur supportée : `"textarea"` (force un textarea même sur un `CharField`) |

**Valeurs par défaut de visibilité** (si non précisées dans le JSON)

| Cas | `visible_in_table` | `visible_in_dialog` |
| --- | ------------------ | ------------------- |
| Champ `id` | `false` | `false` |
| `UUIDField`, `AutoField` | `false` | `false` |
| Autres champs | `true` | `true` |

**Comportement UI lié au type** (génération frontend, option 6)

| Type Django   | Composant formulaire par défaut |
| ------------- | ------------------------------- |
| `CharField`   | `<Input>` une ligne |
| `TextField`   | `<Textarea>` multiligne |
| `DecimalField`, `IntegerField`, `FloatField`, `BigIntegerField` | `<Input type="number">` |
| `BooleanField` | `<Checkbox>` |
| `DateField`, `DateTimeField`, `TimeField` | `<Input type="date">` (ou équivalent) |
| `FileField`   | `<Input type="file">` + lien de téléchargement / aperçu image |

Les champs `UUIDField` et `AutoField` ne sont pas proposés dans les formulaires de création / édition (ils restent gérés côté backend).

#### Champs fichier (`FileField`)

Le type `FileField` stocke en base un **chemin relatif** (`CharField` max 512) et délègue le binaire à `StorageService` (disque local ou S3/MinIO). Voir aussi [`00readme/README_STORAGE_FILE_MANAGEMENT.md`](../../00readme/README_STORAGE_FILE_MANAGEMENT.md).

**Comportement :**

- Upload **multipart** sur les endpoints CRUD (`POST` / `PUT` / `PATCH`)
- Le frontend envoie le fichier sous `{field}` et le chemin cible sous `{field}_path` (via `buildFilePath`)
- La réponse API inclut le chemin relatif et un champ calculé `{field}_url`
- À la mise à jour ou suppression, l'ancien fichier est supprimé du storage

**Exemple JSON :**

```json
{
  "name": "document",
  "type": "FileField",
  "upload_folder": "elitest_documents",
  "allowed_extensions": [".pdf", ".png"],
  "max_size_mb": 5,
  "blank": true,
  "null": true,
  "visible_in_table": true,
  "visible_in_dialog": true
}
```

Si `upload_folder` est omis, la valeur par défaut est `{resource_plural}/{field_name}` (ex. `elitests/document`).

**Prérequis infra :** `USE_S3` (et `S3_*` si activé) dans `backend/.env` ; `VITE_USE_S3` dans `frontend/.env` ; parsers multipart activés dans `REST_FRAMEWORK`.

#### Champs système ajoutés automatiquement

Si absents du JSON, le générateur backend ajoute en général :

- `created_by`, `updated_by` (référence utilisateur)
- `created_at`, `updated_at` (horodatage)

Ces champs sont exclus des formulaires frontend générés.

#### Génération frontend

Après l'API backend (option 1), lancez l'option **6** du menu (ou `python scripts/generate_api.py --frontend Elitest`) pour générer pages, tableaux, schémas Zod et dialogues à partir du même JSON.

## Types de champs supportés

| Type JSON         | Type Django        | Usage typique |
| ----------------- | ------------------ | ------------- |
| `AutoField`       | `AutoField`        | Clé primaire auto (souvent `id`) |
| `BigIntegerField` | `BigIntegerField`  | Entier 64 bits |
| `IntegerField`    | `IntegerField`     | Entier 32 bits |
| `DecimalField`    | `DecimalField`     | Montants, prix (`max_digits`, `decimal_places`) |
| `FloatField`      | `FloatField`       | Nombre décimal |
| `CharField`       | `CharField`        | Texte court (titre, code, …) |
| `TextField`       | `TextField`        | Texte long (description, commentaire, …) |
| `BooleanField`    | `BooleanField`     | Oui / non |
| `DateField`       | `DateField`        | Date seule |
| `DateTimeField`   | `DateTimeField`    | Date et heure |
| `TimeField`       | `TimeField`        | Heure seule |
| `UUIDField`       | `UUIDField`        | Identifiant UUID (souvent masqué dans l'UI) |
| `FileField`       | `CharField` (512)  | Fichier média (chemin relatif en base) |

Types également acceptés : `SlugField`, `EmailField`, `URLField`, `SmallIntegerField`, `PositiveIntegerField`,
`PositiveSmallIntegerField`, `DurationField`, `JSONField`.

Règles de validation (le générateur refuse le JSON avant toute écriture) :

- un **type inconnu** est une erreur (il n'est plus converti silencieusement en `CharField`) ;
- `CharField` exige `max_length`, `DecimalField` exige `max_digits` et `decimal_places` (la valeur `0` est acceptée) ;
- les noms de champs sont en `snake_case` et ne peuvent pas être un mot réservé Python ;
- `ForeignKey` / `OneToOneField` / `ManyToManyField` ne se déclarent pas dans le JSON : utilisez `--link` (voir Relations).

### Nommage des fichiers et des modèles

- Le **nom du fichier JSON est libre** (`ligne_commande.json`, `Commande.json`…) : le générateur retrouve le fichier
  par son `model_name`, sans supposer `<model_name>.json`.
- Le `model_name` est unique **sur toutes les zones** : un doublon est signalé au scan et le second fichier est ignoré.
- `model_name` peut être en CamelCase (`OrderItem`). Les fichiers backend sont en minuscules
  (`orderitem_viewset.py`), le frontend en kebab-case (`models/order-item/`), les variables en snake_case.
- `meta.resource_plural` reste obligatoire (ex. `order-items`).

### Interface générée (thème et traductions)

- Les tableaux, formulaires et dialogues n'utilisent que des composants shadcn (`Button`, `Label`, `Skeleton`…)
  et des variables de thème (`bg-muted`, `border`, `text-destructive`…) : aucune couleur en dur,
  ils suivent donc le mode clair/sombre.
- Le **libellé d'une colonne** (en-tête et menu « Filtrer les colonnes ») est le `verbose_name` du champ dans le JSON ;
  à défaut, le nom du champ en texte lisible (`prix_ht` → « Prix ht »).
- Les textes fixes (sélection, « sur », Oui/Non, aucun résultat) viennent de `lib/locales/{fr,en}/common.json`.

## Contraintes supportées (format legacy `constraints[]`)

| Contrainte       | Effet Django approximatif |
| ---------------- | ------------------------- |
| `PK`             | `primary_key=True`        |
| `UK`             | `unique=True`             |
| `NOT NULL`       | `null=False`, `blank=False` |
| `AUTO_INCREMENT` | Champ auto-incrémenté     |

Préférez les attributs explicites (`blank`, `null`, `unique`, etc.) comme dans `elitest.json`.

## 🏗️ Architecture Générée

Pour chaque modèle, le système génère :

```
nom_du_modele/
├── models.py                    # Modèle Django (cumulatif)
├── serializers.py              # Serializer DRF (cumulatif)
├── interfaces/
│   └── nom_du_modele_repository_interface.py
├── repositories/
│   └── nom_du_modele_repository.py
├── services/
│   └── nom_du_modele_service.py
├── views/
│   └── nom_du_modele_viewset.py
├── permissions/
│   └── nom_du_modele_permissions.py
└── tests/
    └── test_nom_du_modele.py    # Tests unitaires
```

## 🎨 API Générée

Chaque API inclut :

- **CRUD complet** (Create, Read, Update, Delete)
- **Décorateurs Swagger** avec tag "V1 - NomDuModèle"
- **Permissions automatiques** (CanView, CanCreate, CanUpdate, CanDelete)
- **Validation des données**
- **Gestion d'erreurs robuste**
- **Tests unitaires**
- **Champs système automatiques** (created_by, updated_by, created_at, updated_at)

## 🔍 Validation et Tests

### **Tests Automatisés**

```bash
# Exécuter les tests de validation
python scripts/test_fix.py
```

**Tests inclus :**

- ✅ Validation des imports
- ✅ Création des instances de modèles
- ✅ Validation des serializers
- ✅ Configuration des URLs
- ✅ Existence des tables en base

### **Validation Django**

```bash
# Vérifier la configuration Django
python manage.py check
```

## 📊 State Management

Le fichier `improved_state.json` garde une trace de :

- ✅ **APIs générées** avec métadonnées complètes
- ✅ **Modèles disponibles** par zone
- ✅ **Checksums des fichiers** pour détecter les modifications
- ✅ **Relations créées** entre modèles
- ✅ **Statistiques d'utilisation** détaillées
- ✅ **Historique des générations** avec timestamps

## 🚨 Sécurité et Robustesse

### **Système de Backup**

- Backup automatique avant chaque modification
- Nommage avec timestamp : `fichier.py.20250813_103000.backup`
- Rollback automatique en cas d'erreur de syntaxe

### **Validation Multi-Niveaux**

1. **Validation du schéma JSON** avant génération
2. **Validation syntaxique Python** après génération
3. **Validation des imports** pour vérifier la cohérence
4. **Validation d'intégrité** du state complet

### **Détection des Modifications**

- Checksums MD5 pour chaque fichier critique
- Alertes en cas de modification manuelle non documentée
- Synchronisation automatique avec le système de fichiers

## 🔗 Relations

Le système supporte tous les types de relations Django :

- **OneToOneField** (One-to-One)
- **ForeignKey** (One-to-Many)
- **ManyToManyField** (Many-to-Many)
- **Relations cross-zones** entre modèles de zones différentes

Les relations créées avec `--link` (ou l'option 3) sont enregistrées dans `improved_state.json` (`relations`).
Quand vous **régénérez** un modèle impliqué dans une relation, elle est rejouée automatiquement
(champ du modèle + serialisation), sans doublon.

## 📈 Avantages Version 2.0

| Aspect                        | Version 1.0           | Version 2.0                    |
| ----------------------------- | --------------------- | ------------------------------ |
| **Gestion fichiers partagés** | ❌ Écrasement complet | ✅ Merge intelligent           |
| **Validation**                | ❌ Aucune             | ✅ Multi-niveaux               |
| **Gestion d'erreurs**         | ❌ Basique            | ✅ Robuste avec rollback       |
| **State management**          | ❌ Déconnecté         | ✅ Synchronisé automatiquement |
| **Backups**                   | ❌ Aucun              | ✅ Automatiques avec timestamp |
| **Interface**                 | ❌ 4 options          | ✅ 8 options + modes CLI       |
| **Debugging**                 | ❌ Limité             | ✅ Logs détaillés + rapports   |
| **Fiabilité**                 | ❌ Problématique      | ✅ Production-ready            |

## 🛠️ Dépannage

### **Problème : Modèles écrasés**

**Solution :** Utilisez toujours `python scripts/generate_api.py` (v2.0), jamais l'ancien générateur.

### **Problème : Erreurs d'import**

**Solution :** Exécutez `python scripts/generate_api.py --sync` pour synchroniser le state.

### **Problème : State incohérent**

**Solution :** Exécutez `python scripts/generate_api.py --validate` pour valider l'intégrité.

### **Problème : Fichiers corrompus**

**Solution :** Les backups automatiques sont dans `scripts/generator/backups/`.

## 📝 Exemple d'Utilisation Complète

```bash
# 1. Uploader un modèle
cp mon_modele.json scripts/models_zones/zone_1/

# 2. Lancer le générateur v2.0
python scripts/generate_api.py

# 3. Choisir l'option 1 pour générer l'API
# 4. Le système fait automatiquement :
#    - Validation du schéma
#    - Génération avec merge intelligent
#    - Backup automatique
#    - Validation post-génération
#    - Synchronisation du state
#    - Rapport d'intégrité

# 5. Vérifier le résultat
python manage.py check
```

## ♻️ Réinitialisation de l'application

Après avoir purgé tous les modèles, fichiers générés et migrations, vous pouvez repartir sur une base saine :

```bash
# Recréer les migrations initiales (une commande par application : metier, et chaque app_name utilisé)
python manage.py makemigrations metier

# Appliquer les migrations à la base de données
python manage.py migrate
```

Vous pouvez ensuite relancer le générateur v2.0 pour créer de nouveaux modèles et APIs.

---

## 🔮 Fonctionnalités Futures

- **Interface web** pour la gestion des APIs
- **Support des relations complexes** avec contraintes avancées
- **Génération de documentation** automatique
- **Intégration CI/CD** avec hooks Git
- **Templates personnalisables** par projet
- **Export/Import** de configurations

## ✅ Conclusion

La version 2.0 du générateur est **production-ready** avec :

- 🛡️ **Robustesse** : Gestion d'erreurs complète avec rollback
- 🔄 **Fiabilité** : Synchronisation automatique et validation
- 🚀 **Performance** : Génération optimisée avec merge intelligent
- 📊 **Monitoring** : Rapports détaillés et logs complets
- 🔧 **Maintenabilité** : Code modulaire et extensible

**Plus jamais de modèles écrasés !** 🎉
