# Générateur de CRUD (backend et frontend)

À partir d'un fichier JSON décrivant un modèle, le générateur crée l'API Django (Repository Pattern) et l'interface React correspondante. Référence détaillée des champs : [`backend/scripts/README.md`](../backend/scripts/README.md).

## Principe

```text
models_zones/zone_N/<modele>.json ─► validation ─► backend (app/<app_name>/) ─► migrations
                                                └► frontend (frontend/src/models/<modele>/)
```

Le backend se génère avant le frontend. Les deux lisent le même JSON.

Les anciens CRUD de démonstration ne sont plus installés. Pour essayer le générateur, copier `backend/scripts/examples/model.json` dans une nouvelle zone sous `scripts/models_zones/`, adapter ses noms, puis utiliser `ExampleRecord` à la place des noms illustratifs ci-dessous. Les exemples du guide ne sont pas des routes actives.

## 1. Décrire le modèle

Créer le fichier dans `backend/scripts/models_zones/zone_N/` (nom libre). Modèle de départ : `zone_1/elitest.json`.

```json
{
  "model_name": "Elitest",
  "app_name": "metier",
  "fields": [
    { "name": "titre", "type": "CharField", "max_length": 200, "blank": false, "null": false },
    { "name": "prix", "type": "DecimalField", "max_digits": 10, "decimal_places": 2 }
  ],
  "meta": {
    "resource_plural": "elitests",
    "verbose_name": "Elitest",
    "verbose_name_plural": "Elitests",
    "ordering": ["-created_at"]
  }
}
```

Règles que le générateur vérifie avant d'écrire quoi que ce soit :

- `model_name` est unique sur toutes les zones et dans toutes les applications.
- `app_name` (facultatif, défaut `metier`) est l'application Django qui reçoit le code. Elle doit exister : la créer avant par le menu interactif. `meta.db_table` et `meta.resource_plural` doivent être uniques dans tout le projet : en copiant un JSON, les changer aussi.
- `meta.resource_plural` est obligatoire : il fixe les routes (`/api/v1/<resource_plural>/`), les permissions (`<resource_plural>.view`) et le dossier frontend. Le pluriel n'est jamais deviné.
- Type de champ inconnu = erreur. `CharField` exige `max_length`, `DecimalField` exige `max_digits` et `decimal_places`.
- Noms de champs en `snake_case`.
- Les relations (`ForeignKey`, `OneToOneField`, `ManyToManyField`) ne se déclarent pas dans le JSON : voir §4.
- `id`, `uuid`, `created_at`, `updated_at`, `created_by` et `updated_by` ne sont pas proposés dans les formulaires.

Pour le frontend, deux clés facultatives par champ : `visible_in_table` et `visible_in_dialog`. Le libellé d'une colonne est le `verbose_name` du champ.

## 2. Générer

Depuis `backend/`, venv active, base PostgreSQL démarrée :

```powershell
python scripts/generate_api.py --generate Elitest --zone zone_1   # backend
python scripts/generate_api.py --frontend Elitest --zone zone_1   # frontend
python scripts/generate_api.py --generate Elitest,Dragon --with-frontend   # plusieurs modèles, API + interface
python scripts/generate_api.py                                    # menu interactif (1 = backend, 6 = frontend, 8 = les deux)
```

**Plusieurs modèles à la fois** : dans le menu (options 1, 6 et 8), saisir `1,2,3`, une plage `1-3` ou `tous`. En ligne de commande, séparer les noms par des virgules. Les modèles sont traités l'un après l'autre : un échec n'arrête pas les suivants, et un résumé final liste le résultat de chacun (API ✅/❌, interface ✅/❌). L'option 8 (« Générer l'API et l'interface ») ne génère l'interface d'un modèle que si son API a réussi. Code de sortie : `0` si tout a réussi, sinon le code d'échec le plus élevé (`1` JSON introuvable, `2` schéma invalide, `3` génération échouée).

**Backend** : le générateur crée dans `app/<app_name>/` (par défaut `app/metier/`) l'interface, le repository, le service, le ViewSet, les permissions, les tests et la commande `seed_<modele>`. Il ajoute le modèle à `models.py`, `serializers.py` et `urls.py` de cette application sans écraser l'existant, puis lance `makemigrations <app_name>`, `migrate`, et **`seed_<modele>`** (permissions + assignation aux rôles Admin / Super Admin + données de démo).

**Frontend** : il crée `frontend/src/models/<modele>/` (`api.ts`, `schema.ts`, `slice.ts`, `pages/`, `components/`) et modifie cinq fichiers : `redux/store.ts`, `App.tsx`, `models/auth/permissions/constants.ts`, `hooks/use-permissions.tsx` et le menu du sidebar.

Ensuite :

```powershell
cd ../frontend
npm run lint
```

Rechargez la session front (ou rappels `/api/auth/me`) pour voir les nouveaux menus. `seed_<modele>` crée aussi des données de test : en staging/prod, relisez la commande avant de la laisser s'exécuter (ou régénérez avec `apply_migrations=False` puis migrez/seedez à la main).

## 3. Ce que le générateur garantit

- **Rien d'écrasé** : `models.py`, `serializers.py` et `urls.py` sont fusionnés. Un backup horodaté est pris dans `scripts/generator/backups/` avant chaque modification, et restauré si la génération échoue.
- **Frontend atomique** : si un repère de texte est introuvable dans l'un des cinq fichiers, la génération s'arrête, restaure tout et supprime les fichiers créés. Relancer ne duplique ni route, ni reducer, ni permission.
- **Modifications manuelles détectées** : l'état est suivi dans `scripts/generator/improved_state.json` (checksums MD5).

```powershell
python scripts/generate_api.py --sync       # resynchronise l'état avec les fichiers
python scripts/generate_api.py --validate   # contrôle l'intégrité de l'état
python scripts/generate_api.py --report     # rapport d'intégrité
```

## 4. Relations entre modèles

Après avoir généré les deux modèles :

```powershell
python scripts/generate_api.py --link --from Commande --to Client --type fk --nullable
```

`--type` vaut `fk`, `o2o` ou `m2m`. Options : `--name`, `--related_name`, `--on_delete` (défaut `models.RESTRICT`). La relation est enregistrée dans l'état et rejouée si l'un des deux modèles est régénéré.

Les deux modèles peuvent appartenir à **deux applications différentes** (`app_name` de leurs JSON) : le champ est ajouté dans l'application du modèle source. Après le linkage, le générateur lance automatiquement `makemigrations` (sans nom d'app) puis `migrate`, pour couvrir aussi les relations cross-app. Si une étape de linkage échoue, les fichiers sont restaurés.

## 5. Modifier du code généré

- Régénérer un modèle réécrit ses fichiers dédiés (interface, repository, service, ViewSet, permissions, seed), après un backup dans `scripts/generator/backups/`. Une modification manuelle y est donc perdue : reporter le changement dans le JSON, ou ne plus régénérer ce modèle.
- Ne pas modifier les templates (`scripts/generator/templates/`, `frontend_generator.py`) pour un besoin ponctuel.
- Les cinq fichiers du frontend doivent rester analysables par le générateur : ne pas supprimer ni reformuler ses repères (commentaires, lignes d'import et tableaux de routes).

## 6. Avec le CD

Le générateur ne produit que du code et des migrations. Tout le reste suit les règles de [`README_DEV.md`](./README_DEV.md).

- Commiter ensemble : le JSON, le code backend, les migrations, le frontend et `improved_state.json`. Un commit sans les migrations fait échouer `CI - BACKEND`.
- `backend/scripts/generator/**` et `generate_api.py` forment la zone protégée `generateur` : les modifier demande l'approbation d'un responsable de zone.
- Le déploiement n'exécute que `migrate` et `collectstatic`, jamais les seeds : les permissions du modèle (`<resource_plural>.view`, `.create`, `.update`, `.delete`) n'existent pas dans `sandbox`, `main` et `prod` tant qu'elles n'y sont pas créées. Prévenir un master avant de merger.
- La CI exécute `makemigrations --check` : une migration manquante fait échouer `CI - BACKEND`.

## Problèmes courants

| Symptôme | Action |
|---|---|
| « Schéma invalide » | Corriger le JSON selon le message : aucun fichier n'a été écrit |
| Génération frontend arrêtée sur un repère introuvable | Restaurer le fichier cité tel qu'il est dans `develop`, puis relancer. Tout a été annulé |
| Migrations non appliquées | `python manage.py makemigrations <app_name>` puis `python manage.py migrate` (`metier` par défaut) |
| « L'application cible … n'existe pas » | Créer l'application (menu interactif) ou corriger `app_name` dans le JSON |
| Génération refusée : table, route ou modèle déjà utilisé | Changer `meta.db_table`, `meta.resource_plural` ou `model_name` dans le JSON |
| État incohérent | `--sync`, puis `--validate` |
