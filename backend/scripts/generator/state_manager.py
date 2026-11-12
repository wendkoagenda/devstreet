"""
State Manager amélioré avec synchronisation et validation.
"""
import json
import os
import re
import hashlib
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from .naming_utils import get_resource_plural, to_kebab_case
from .schema_validator import DEFAULT_APP_NAME

_ZONE_NAME_RE = re.compile(r'^[A-Za-z0-9_-]+$')

MODELS_ZONES_DIR = Path(__file__).resolve().parent.parent / 'models_zones'

# Séparateur des clés de checksum des applications autres que metier (« yango::models.py »)
CHECKSUM_APP_SEPARATOR = '::'


def read_model_name(json_file: Path) -> Optional[str]:
    """Retourne le model_name (ou model) déclaré dans un fichier JSON de modèle, sinon None."""
    try:
        with open(json_file, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
    except (OSError, ValueError) as error:
        # Le fichier est ignoré mais la raison est visible : un JSON invalide ne doit pas disparaître en silence
        print(f"Attention : fichier de modèle illisible ou invalide, ignoré : {json_file} ({error})", file=sys.stderr)
        return None
    if not isinstance(data, dict):
        return None
    return data.get('model_name') or data.get('model')


class ImprovedStateManager:
    """Gestionnaire de state amélioré avec synchronisation et validation."""
    
    def __init__(self, state_file: str = None):
        if state_file is None:
            state_file = os.path.join(os.path.dirname(__file__), 'improved_state.json')
        
        self.state_file = state_file
        self.state = self.load_state()
        self.app_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'app')
        # Application par défaut (metier) : conservée pour la compatibilité, voir get_app_dir pour les autres
        self.app_dir = os.path.join(self.app_root, DEFAULT_APP_NAME)
    
    def load_state(self) -> Dict[str, Any]:
        """Charge le state depuis le fichier JSON."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Erreur lors du chargement du state: {e}")
                return self.create_empty_state()
            # États antérieurs à generated_frontends
            if isinstance(state, dict):
                state.setdefault("generated_frontends", {})
                return state
            return self.create_empty_state()
        return self.create_empty_state()
    
    def create_empty_state(self) -> Dict[str, Any]:
        """Crée un state vide."""
        return {
            "version": "2.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "generated_apis": {},
            "generated_frontends": {},
            "available_models": {},
            "file_checksums": {},
            "relations": [],
            "apps": {},
            "statistics": {
                "total_models": 0,
                "total_apis": 0,
                "total_frontends": 0,
                "total_relations": 0,
                "zones_used": []
            }
        }
    
    def save_state(self):
        """Sauvegarde le state dans le fichier JSON."""
        try:
            self.state["last_updated"] = datetime.now().isoformat()
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"❌ Erreur lors de la sauvegarde du state: {e}")
    
    def find_model_file(self, zone: str, model_name: str) -> Optional[Path]:
        """
        Retrouve le JSON d'un modèle dans une zone, quel que soit son nom de fichier.
        Ordre : fichier enregistré dans le state, puis scan de la zone par model_name
        (comparaison insensible à la casse).
        """
        if not _ZONE_NAME_RE.match(zone):
            return None
        zone_dir = MODELS_ZONES_DIR / zone
        wanted = model_name.lower()

        for name, info in self.state.get('available_models', {}).get(zone, {}).items():
            if name.lower() == wanted:
                candidate = zone_dir / info['file']
                if candidate.exists() and (read_model_name(candidate) or '').lower() == wanted:
                    return candidate

        if zone_dir.is_dir():
            for json_file in sorted(zone_dir.glob('*.json')):
                if (read_model_name(json_file) or '').lower() == wanted:
                    return json_file
        return None

    def get_app_dir(self, app_name: str = DEFAULT_APP_NAME) -> str:
        """Dossier d'une application Django générée."""
        return os.path.join(self.app_root, app_name)

    def get_api_app_name(self, model_name: str) -> str:
        """Application d'un modèle généré (metier pour les entrées enregistrées avant app_name)."""
        api = self.state.get("generated_apis", {}).get(model_name) or {}
        return api.get("app_name") or DEFAULT_APP_NAME

    def known_app_names(self) -> List[str]:
        """Applications à inspecter : metier, celles des API générées et celles créées par le générateur."""
        names = [DEFAULT_APP_NAME]
        candidates = [api.get("app_name") or DEFAULT_APP_NAME for api in self.state.get("generated_apis", {}).values()]
        candidates += list(self.state.get("apps", {}).keys())
        for name in candidates:
            if name not in names:
                names.append(name)
        return [name for name in names if os.path.isdir(self.get_app_dir(name))]

    @staticmethod
    def checksum_key(app_name: str, relative_path: str) -> str:
        """Clé de checksum : inchangée pour metier (état existant), préfixée par l'application sinon."""
        if app_name == DEFAULT_APP_NAME:
            return relative_path
        return f"{app_name}{CHECKSUM_APP_SEPARATOR}{relative_path}"

    def checksum_key_to_path(self, key: str) -> str:
        """Chemin absolu du fichier désigné par une clé de checksum."""
        if CHECKSUM_APP_SEPARATOR in key:
            app_name, relative_path = key.split(CHECKSUM_APP_SEPARATOR, 1)
        else:
            app_name, relative_path = DEFAULT_APP_NAME, key
        return os.path.join(self.get_app_dir(app_name), relative_path)

    def calculate_file_checksum(self, file_path: str) -> Optional[str]:
        """Calcule le checksum MD5 d'un fichier (lecture par chunks)."""
        if not os.path.exists(file_path):
            return None

        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except IOError as error:
            print(f"Attention : checksum impossible, fichier illisible : {file_path} ({error})", file=sys.stderr)
            return None

    def update_file_checksum(self, file_path: str, relative_path: str):
        """Met à jour le checksum d'un fichier dans le state."""
        checksum = self.calculate_file_checksum(file_path)
        if checksum:
            self.state["file_checksums"][relative_path] = {
                "checksum": checksum,
                "last_updated": datetime.now().isoformat()
            }
    
    def has_file_changed(self, file_path: str, relative_path: str) -> bool:
        """Vérifie si un fichier a changé depuis la dernière sauvegarde."""
        current_checksum = self.calculate_file_checksum(file_path)
        if not current_checksum:
            return False
        
        stored_info = self.state["file_checksums"].get(relative_path)
        if not stored_info:
            return True
        
        return stored_info["checksum"] != current_checksum

    def _refresh_shared_file_checksums(self):
        """Recalcule les checksums des fichiers partagés et des viewsets de chaque application."""
        for app_name in self.known_app_names():
            app_dir = self.get_app_dir(app_name)
            for file_name in ('models.py', 'serializers.py', 'urls.py'):
                file_path = os.path.join(app_dir, file_name)
                if os.path.exists(file_path):
                    self.update_file_checksum(file_path, self.checksum_key(app_name, file_name))

            views_dir = os.path.join(app_dir, 'views')
            if os.path.exists(views_dir):
                for file_name in os.listdir(views_dir):
                    if file_name.endswith('_viewset.py'):
                        file_path = os.path.join(views_dir, file_name)
                        self.update_file_checksum(file_path, self.checksum_key(app_name, f'views/{file_name}'))

    def sync_with_filesystem(self):
        """Synchronise le state avec l'état réel du système de fichiers."""
        print("🔄 Synchronisation avec le système de fichiers...")
        
        for app_name in self.known_app_names():
            app_dir = self.get_app_dir(app_name)

            # Vérifier les modèles dans models.py
            models_file = os.path.join(app_dir, 'models.py')
            if os.path.exists(models_file):
                actual_models = self.extract_models_from_file(models_file)
                self.sync_models_with_state(actual_models, app_name=app_name)

            # Vérifier les serializers dans serializers.py
            serializers_file = os.path.join(app_dir, 'serializers.py')
            if os.path.exists(serializers_file):
                actual_serializers = self.extract_serializers_from_file(serializers_file)
                self.sync_serializers_with_state(actual_serializers)

            # Vérifier les ViewSets
            views_dir = os.path.join(app_dir, 'views')
            if os.path.exists(views_dir):
                actual_viewsets = self.extract_viewsets_from_directory(views_dir)
                self.sync_viewsets_with_state(actual_viewsets)

        self._refresh_shared_file_checksums()

        # Interfaces frontend présentes sur le disque mais absentes du state
        self.sync_frontends_with_state()
        
        # Nettoyer les APIs inexistantes
        self.cleanup_nonexistent_apis()

        # Nettoyer les interfaces frontend dont les fichiers ont disparu
        self.cleanup_nonexistent_frontends()
        
        # Nettoyer les modèles disponibles inexistants
        self.cleanup_nonexistent_models()
        
        # Mettre à jour les statistiques
        self.update_statistics()
        
        # Sauvegarder
        self.save_state()
        print("✅ Synchronisation terminée")
    
    def extract_models_from_file(self, models_file: str) -> List[str]:
        """Extrait la liste des modèles depuis models.py."""
        models = []
        try:
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            # Chercher les classes qui héritent de models.Model
            pattern = r'class\s+(\w+)\s*\([^)]*models\.Model[^)]*\):'
            matches = re.findall(pattern, content)
            models = [match for match in matches if match != 'Model']
            
        except Exception as e:
            print(f"⚠️  Erreur lors de l'extraction des modèles: {e}")
        
        return models
    
    def extract_serializers_from_file(self, serializers_file: str) -> List[str]:
        """Extrait la liste des serializers depuis serializers.py."""
        serializers = []
        try:
            with open(serializers_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            # Chercher les classes qui héritent de serializers.ModelSerializer
            pattern = r'class\s+(\w+)Serializer\s*\([^)]*serializers\.ModelSerializer[^)]*\):'
            matches = re.findall(pattern, content)
            serializers = matches
            
        except Exception as e:
            print(f"⚠️  Erreur lors de l'extraction des serializers: {e}")
        
        return serializers
    
    def extract_viewsets_from_directory(self, views_dir: str) -> List[str]:
        """Extrait la liste des ViewSets depuis le répertoire views."""
        viewsets = []
        try:
            for file_name in os.listdir(views_dir):
                if file_name.endswith('_viewset.py') and file_name != '__init__.py':
                    # Extraire le nom du modèle depuis le nom du fichier
                    model_name = file_name.replace('_viewset.py', '').title()
                    viewsets.append(model_name)
                    
        except Exception as e:
            print(f"⚠️  Erreur lors de l'extraction des ViewSets: {e}")
        
        return viewsets
    
    def _locate_model_json(self, model_name: str):
        """Cherche (zone, fichier) d'un modèle parmi les modèles disponibles ; ("unknown", None) sinon."""
        for zone, models in self.state.get("available_models", {}).items():
            for name, info in models.items():
                if name.lower() == model_name.lower():
                    return zone, info["file"]
        return "unknown", None

    def sync_models_with_state(
        self,
        actual_models: List[str],
        detected_zone: str = "unknown",
        app_name: str = DEFAULT_APP_NAME,
    ):
        """Synchronise les modèles avec le state."""
        if app_name != DEFAULT_APP_NAME and app_name not in self.state.get("apps", {}):
            # Application écrite à la main (ex. core) : ses modèles ne sont pas des API générées.
            # Seuls ceux générés dedans, déjà enregistrés par add_generated_api, sont suivis.
            return
        known ={api["model_name"].lower() for api in self.state["generated_apis"].values()}
        for model in actual_models:
            if model.lower() in known:
                continue
            zone, file_name = self._locate_model_json(model)
            if zone == "unknown":
                zone = detected_zone
            print(f"📝 Modèle détecté non enregistré: {model} (zone: {zone})")
            try:
                self.add_generated_api(
                    model, zone, file_name or f"{model.lower()}.json", auto_detected=True, app_name=app_name
                )
            except ValueError as e:
                print(f"⚠️  {model} ignoré lors de la synchronisation : {e}")

    def sync_serializers_with_state(self, actual_serializers: List[str]):
        """Synchronise les serializers avec le state."""
        for serializer in actual_serializers:
            model_name = serializer  # Le nom du serializer sans "Serializer"
            if model_name.lower() not in [api["model_name"].lower() for api in self.state["generated_apis"].values()]:
                print(f"📝 Serializer détecté non enregistré: {serializer}Serializer")
    
    def sync_viewsets_with_state(self, actual_viewsets: List[str]):
        """Synchronise les ViewSets avec le state (comparaison insensible à la casse)."""
        known = {api["model_name"].lower() for api in self.state["generated_apis"].values()}
        for viewset in actual_viewsets:
            if viewset.lower() not in known:
                print(f"📝 ViewSet détecté non enregistré: {viewset}ViewSet")

    def cleanup_nonexistent_apis(self):
        """Nettoie les APIs qui n'existent plus dans le système de fichiers."""
        apis_to_remove = []
        
        for api_name, api_info in self.state["generated_apis"].items():
            model_name = api_info["model_name"]
            
            # Vérifier si les fichiers existent
            app_dir = self.get_app_dir(api_info.get('app_name') or DEFAULT_APP_NAME)
            viewset_file = os.path.join(app_dir, 'views', f'{model_name.lower()}_viewset.py')
            
            if not os.path.exists(viewset_file):
                print(f"🗑️  API {api_name} marquée pour suppression (fichiers manquants)")
                apis_to_remove.append(api_name)
        
        # Supprimer les APIs inexistantes
        for api_name in apis_to_remove:
            del self.state["generated_apis"][api_name]
    
    def cleanup_nonexistent_models(self):
        """Nettoie les modèles disponibles qui n'existent plus dans le système de fichiers."""
        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'scripts', 'models_zones')
        
        for zone_name, models in list(self.state.get("available_models", {}).items()):
            if not _ZONE_NAME_RE.match(zone_name):
                print(f"⚠️  Nom de zone ignoré (invalide) : '{zone_name}'")
                continue
            zone_dir = os.path.join(models_dir, zone_name)
            models_to_remove = []
            
            for model_name, model_info in models.items():
                json_file = os.path.join(zone_dir, model_info["file"])
                if not os.path.exists(json_file):
                    print(f"🗑️  Modèle {model_name} marqué pour suppression (fichier {model_info['file']} manquant)")
                    models_to_remove.append(model_name)
                elif read_model_name(Path(json_file)) != model_name:
                    print(f"🗑️  Modèle {model_name} marqué pour suppression (le fichier {model_info['file']} déclare maintenant un autre model_name)")
                    models_to_remove.append(model_name)
            
            # Supprimer les modèles inexistants
            for model_name in models_to_remove:
                del self.state["available_models"][zone_name][model_name]
            
            # Supprimer la zone si elle est vide
            if not self.state["available_models"][zone_name]:
                print(f"🗑️  Zone {zone_name} supprimée (aucun modèle)")
                del self.state["available_models"][zone_name]
    
    def _resolve_resource_plural(
        self,
        model_name: str,
        zone: str,
        file: str,
        resource_plural: Optional[str] = None,
    ) -> str:
        if resource_plural:
            return resource_plural

        if zone and file:
            json_path = Path(__file__).resolve().parent.parent / "models_zones" / zone / file
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as handle:
                    model_data = json.load(handle)
                meta = model_data.get("meta") or {}
                return get_resource_plural(model_name, meta)

        raise ValueError(
            f"Impossible de résoudre resource_plural pour {model_name}. "
            f"Ajoutez meta.resource_plural dans le JSON ({zone}/{file})."
        )

    def add_generated_api(
        self,
        model_name: str,
        zone: str,
        file: str,
        auto_detected: bool = False,
        resource_plural: str = None,
        app_name: str = None,
    ):
        """Ajoute une API générée au state (app_name : application Django où le code a été généré)."""
        plural = self._resolve_resource_plural(model_name, zone, file, resource_plural)
        previous = self.state["generated_apis"].get(model_name, {})
        app_name = app_name or previous.get("app_name") or DEFAULT_APP_NAME
        previous_app = previous.get("app_name")
        if previous_app and previous_app != app_name:
            print(
                f"⚠️  {model_name} était généré dans l'application « {previous_app} » et l'est maintenant dans "
                f"« {app_name} » : les anciens fichiers de app/{previous_app}/ ne sont pas supprimés, à nettoyer manuellement."
            )
        api_info = {
            "model_name": model_name,
            "app_name": app_name,
            "zone": zone,
            "file": file,
            "generated_at": datetime.now().isoformat(),
            "status": "active",
            "auto_detected": auto_detected,
            "resource_plural": plural,
            "api_endpoints": [
                f"/api/v1/{plural}/",
                f"/api/v1/{plural}/{{id}}/",
            ],
            "relations": previous.get("relations", [])
        }
        
        self.state["generated_apis"][model_name] = api_info
        
        # Mettre à jour les checksums des fichiers générés
        app_dir = self.get_app_dir(app_name)
        files_to_check = [
            (os.path.join(app_dir, 'models.py'), self.checksum_key(app_name, 'models.py')),
            (os.path.join(app_dir, 'serializers.py'), self.checksum_key(app_name, 'serializers.py')),
            (os.path.join(app_dir, 'urls.py'), self.checksum_key(app_name, 'urls.py')),
            (
                os.path.join(app_dir, 'views', f'{model_name.lower()}_viewset.py'),
                self.checksum_key(app_name, f'views/{model_name.lower()}_viewset.py'),
            ),
        ]
        
        for file_path, relative_path in files_to_check:
            self.update_file_checksum(file_path, relative_path)
        
        self.save_state()
    
    def add_relation(self, relation: Dict[str, Any]):
        """Enregistre une relation créée par link_models (dédoublonnée par source/champ)."""
        relations = self.state.setdefault("relations", [])
        relations[:] = [
            r for r in relations
            if not (r["source"] == relation["source"] and r["field"] == relation["field"])
        ]
        relations.append({**relation, "created_at": datetime.now().isoformat()})
        for model in (relation["source"], relation["target"]):
            api = self.state["generated_apis"].get(model)
            if api is not None:
                label = f"{relation['source']}.{relation['field']} -> {relation['target']} ({relation['type']})"
                if label not in api.setdefault("relations", []):
                    api["relations"].append(label)
        self.update_statistics()
        self.save_state()

    def get_relations_for(self, model_name: str) -> List[Dict[str, Any]]:
        """Relations enregistrées dont le modèle est la source ou la cible."""
        return [
            r for r in self.state.get("relations", [])
            if model_name in (r["source"], r["target"])
        ]

    def is_api_generated(self, model_name: str) -> bool:
        """Vérifie si une API a été générée."""
        return model_name in self.state["generated_apis"]

    def frontend_src_models_dir(self) -> Path:
        """Dossier frontend/src/models (racine dépôt = parent de backend/)."""
        return Path(self.app_root).resolve().parent.parent / "frontend" / "src" / "models"

    def frontend_api_file(self, model_name: str) -> Path:
        """Fichier api.ts de l'interface générée pour un modèle (kebab-case)."""
        return self.frontend_src_models_dir() / to_kebab_case(model_name) / "api.ts"

    def add_generated_frontend(self, model_name: str, zone: str, file: str, auto_detected: bool = False):
        """Enregistre qu'une interface frontend a été générée pour ce modèle."""
        frontends = self.state.setdefault("generated_frontends", {})
        frontends[model_name] = {
            "model_name": model_name,
            "zone": zone,
            "file": file,
            "generated_at": datetime.now().isoformat(),
            "status": "active",
            "auto_detected": auto_detected,
            "path": f"frontend/src/models/{to_kebab_case(model_name)}/",
        }
        self.update_statistics()
        self.save_state()

    def is_frontend_generated(self, model_name: str) -> bool:
        """True si l'interface est enregistrée ou si api.ts existe déjà sur le disque."""
        frontends = self.state.get("generated_frontends") or {}
        if model_name in frontends:
            return True
        wanted = model_name.lower()
        if any(name.lower() == wanted for name in frontends):
            return True
        return self.frontend_api_file(model_name).is_file()

    def list_generated_frontends(self) -> List[str]:
        """Liste les interfaces frontend enregistrées."""
        return list((self.state.get("generated_frontends") or {}).keys())

    def get_frontend_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Informations d'une interface frontend enregistrée."""
        frontends = self.state.get("generated_frontends") or {}
        if model_name in frontends:
            return frontends[model_name]
        wanted = model_name.lower()
        for name, info in frontends.items():
            if name.lower() == wanted:
                return info
        return None

    def sync_frontends_with_state(self):
        """Enregistre les interfaces détectées sur le disque pour les modèles disponibles."""
        known = {name.lower() for name in (self.state.get("generated_frontends") or {})}
        for zone, models in self.state.get("available_models", {}).items():
            for model_name, info in models.items():
                if model_name.lower() in known:
                    continue
                if not self.frontend_api_file(model_name).is_file():
                    continue
                print(f"📝 Interface frontend détectée non enregistrée: {model_name}")
                self.add_generated_frontend(
                    model_name,
                    zone,
                    info.get("file") or f"{model_name.lower()}.json",
                    auto_detected=True,
                )
                known.add(model_name.lower())

    def cleanup_nonexistent_frontends(self):
        """Retire du state les interfaces dont le dossier frontend a disparu."""
        frontends = self.state.setdefault("generated_frontends", {})
        to_remove = [
            name for name, info in frontends.items()
            if not self.frontend_api_file(info.get("model_name") or name).is_file()
        ]
        for name in to_remove:
            print(f"🗑️  Interface frontend {name} retirée du state (fichiers manquants)")
            del frontends[name]
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'un modèle."""
        return self.state["generated_apis"].get(model_name)
    
    def list_generated_apis(self) -> List[str]:
        """Liste les APIs générées."""
        return list(self.state["generated_apis"].keys())
    
    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Liste les modèles disponibles par zone."""
        return self.state.get("available_models", {})
    
    def add_model(self, zone: str, model_name: str, file_name: str):
        """Ajoute un modèle disponible."""
        if not _ZONE_NAME_RE.match(zone):
            raise ValueError(f"Nom de zone invalide : '{zone}'. Seuls les caractères alphanumériques, tirets et underscores sont autorisés.")
        if zone not in self.state["available_models"]:
            self.state["available_models"][zone] = {}
        
        self.state["available_models"][zone][model_name] = {
            "file": file_name,
            "uploaded_at": datetime.now().isoformat()
        }
        self.save_state()
    
    def update_statistics(self):
        """Met à jour les statistiques."""
        self.state["statistics"] = {
            "total_models": sum(
                len(models) for models in self.state.get("available_models", {}).values()
            ),
            "total_apis": len(self.state["generated_apis"]),
            "total_frontends": len(self.state.get("generated_frontends") or {}),
            "total_relations": len(self.state.get("relations", [])),
            "zones_used": list(self.state.get("available_models", {}).keys())
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques."""
        return self.state.get("statistics", {})

    def add_created_app(self, app_name: str):
        """Enregistre une application Django créée via AppCreator."""
        if "apps" not in self.state:
            self.state["apps"] = {}
        self.state["apps"][app_name] = {
            "created_at": datetime.now().isoformat(),
            "dotted_path": f"app.{app_name}",
        }
        self.save_state()

    def list_created_apps(self) -> List[str]:
        """Liste les applications créées."""
        return list(self.state.get("apps", {}).keys())
    
    def validate_state_integrity(self) -> bool:
        """Valide l'intégrité du state."""
        print("🔍 Validation de l'intégrité du state...")
        
        issues = []
        
        # Vérifier que tous les modèles générés existent dans le système de fichiers
        for api_name, api_info in self.state["generated_apis"].items():
            model_name = api_info["model_name"]
            
            # Vérifier les fichiers critiques
            app_dir = self.get_app_dir(api_info.get("app_name") or DEFAULT_APP_NAME)
            critical_files = [
                os.path.join(app_dir, 'views', f'{model_name.lower()}_viewset.py'),
                os.path.join(app_dir, 'services', f'{model_name.lower()}_service.py'),
                os.path.join(app_dir, 'repositories', f'{model_name.lower()}_repository.py')
            ]
            
            for file_path in critical_files:
                if not os.path.exists(file_path):
                    issues.append(f"Fichier manquant pour {api_name}: {file_path}")
        
        # Vérifier les checksums
        for relative_path, checksum_info in self.state["file_checksums"].items():
            file_path = self.checksum_key_to_path(relative_path)
            if os.path.exists(file_path):
                if self.has_file_changed(file_path, relative_path):
                    issues.append(f"Fichier modifié manuellement: {relative_path}")
        
        if issues:
            print("⚠️  Problèmes d'intégrité détectés:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ Intégrité du state validée")
            return True
    
    def create_integrity_report(self) -> Dict[str, Any]:
        """Crée un rapport d'intégrité détaillé."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "state_version": self.state.get("version", "unknown"),
            "total_apis": len(self.state["generated_apis"]),
            "issues": [],
            "warnings": [],
            "file_status": {}
        }
        
        # Analyser chaque API
        for api_name, api_info in self.state["generated_apis"].items():
            model_name = api_info["model_name"]
            api_status = {
                "model_exists": False,
                "serializer_exists": False,
                "viewset_exists": False,
                "files_modified": []
            }
            
            # Vérifier les fichiers
            files_to_check = [
                ("models.py", "model_exists"),
                ("serializers.py", "serializer_exists"),
                (f"views/{model_name.lower()}_viewset.py", "viewset_exists")
            ]
            
            app_name = api_info.get("app_name") or DEFAULT_APP_NAME
            for relative_path, status_key in files_to_check:
                file_path = os.path.join(self.get_app_dir(app_name), relative_path)
                if os.path.exists(file_path):
                    api_status[status_key] = True
                    checksum_key = self.checksum_key(app_name, relative_path)
                    if self.has_file_changed(file_path, checksum_key):
                        api_status["files_modified"].append(checksum_key)
            
            report["file_status"][api_name] = api_status
        
        return report