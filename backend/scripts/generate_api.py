#!/usr/bin/env python3
"""
Script principal amélioré pour générer des APIs CRUD avec gestion robuste.
"""
import json
import os
import re
import sys
import argparse
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

GENERATOR_VERSION = "2.0"

# Les messages contiennent des emojis : évite UnicodeEncodeError (console cp1252, sortie redirigée)
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, 'reconfigure'):
        _stream.reconfigure(encoding='utf-8', errors='replace')

from scripts.generator.state_manager import ImprovedStateManager, read_model_name
from scripts.generator.schema_validator import DEFAULT_APP_NAME, SchemaValidator
from scripts.generator.code_generator import ImprovedCodeGenerator
from scripts.generator.app_creator import AppCreator
from scripts.generator.frontend_generator import FrontendCodeGenerator
from scripts.generator.naming_utils import pluralize


def resolve_relation_apps(state_manager: ImprovedStateManager, source: str, target: str) -> tuple:
    """
    Applications Django des deux modèles d'une relation : (source, cible). Elles peuvent différer :
    le champ relationnel vit dans l'application source et référence « app_cible.Modèle ».
    """
    return state_manager.get_api_app_name(source), state_manager.get_api_app_name(target)


def describe_apps(source: str, source_app: str, target: str, target_app: str) -> None:
    """Rappelle les applications concernées quand la relation traverse deux applications."""
    if source_app != target_app:
        print(f"\n🔀 Relation entre applications : {source} (app « {source_app} ») → {target} (app « {target_app} »)")
        print(f"   • Le champ est ajouté dans app/{source_app}/ et référence '{target_app}.{target}'")
        print(f"   • La migration est créée dans « {source_app} » et dépend de « {target_app} »")


def scan_models_in_zones(state_manager: ImprovedStateManager):
    """Scanne les fichiers JSON dans les zones et les ajoute au state."""
    models_dir = Path(__file__).parent / "models_zones"

    if not models_dir.exists():
        print(f"⚠️  Répertoire des modèles non trouvé: {models_dir}")
        return

    seen_names: Dict[str, str] = {}  # model_name.lower() -> "zone/fichier" (unicité globale)

    for zone_dir in sorted(models_dir.iterdir()):
        if not zone_dir.is_dir():
            continue
        zone_name = zone_dir.name
        print(f"🔍 Scan de la zone: {zone_name}")

        for json_file in sorted(zone_dir.glob("*.json")):
            try:
                model_name = read_model_name(json_file)
                if not model_name:
                    print(f"  ⚠️  {json_file.name}: modèle non défini")
                    continue

                # Le state est indexé par model_name : deux JSON ne peuvent pas déclarer le même modèle
                location = f"{zone_name}/{json_file.name}"
                previous = seen_names.get(model_name.lower())
                if previous:
                    print(
                        f"  ❌ {location}: le modèle {model_name} est déjà défini dans {previous} "
                        "(fichier ignoré, renommez le model_name ou supprimez le doublon)"
                    )
                    continue
                seen_names[model_name.lower()] = location

                registered = state_manager.list_available_models().get(zone_name, {}).get(model_name)
                if registered and registered.get("file") == json_file.name:
                    print(f"  ✅ {model_name} (déjà enregistré)")
                else:
                    state_manager.add_model(zone_name, model_name, json_file.name)
                    print(f"  ➕ {model_name} ajouté ({json_file.name})")
            except Exception as e:
                print(f"  ❌ Erreur lors du scan de {json_file.name}: {e}")


def load_model_json(state_manager: ImprovedStateManager, zone: str, model_name: str):
    """
    Charge le JSON d'un modèle sans supposer son nom de fichier.
    Retourne (chemin, données) ou None (message d'erreur déjà affiché).
    Le model_name canonique est celui déclaré dans le JSON (casse comprise).
    """
    model_file = state_manager.find_model_file(zone, model_name)
    if model_file is None:
        print(f"❌ Aucun JSON déclarant le modèle '{model_name}' dans la zone {zone}.")
        known = sorted(state_manager.list_available_models().get(zone, {}))
        if known:
            print(f"   Modèles disponibles dans {zone}: {', '.join(known)}")
        return None
    try:
        with open(model_file, 'r', encoding='utf-8') as f:
            return model_file, json.load(f)
    except (OSError, ValueError) as e:
        print(f"❌ Impossible de lire {model_file}: {e}")
        return None


def interactive_menu(state_manager: ImprovedStateManager):
    """Interface interactive : menus regroupés Backend / Frontend / Général."""
    while True:
        print("\n" + "=" * 60)
        print(f"MENU INTERACTIF - GENERATEUR CRUD v{GENERATOR_VERSION}")
        print("=" * 60)
        print("\n--- Backend ---")
        print("  1. Generer l'API d'un ou plusieurs modeles")
        print("  2. Lister les APIs generees")
        print("  3. Creer une relation entre modeles existants")
        print("  4. Creer une nouvelle application Django")
        print("  5. Lancer les tests unitaires d'un modele")
        print("\n--- Frontend ---")
        print("  6. Generer l'interface frontend d'un ou plusieurs modeles")
        print("  7. Lister les interfaces frontend generees")
        print("\n--- General ---")
        print("  8. Generer l'API et l'interface (un ou plusieurs modeles)")
        print("  9. Afficher les statistiques")
        print(" 10. Synchroniser avec le systeme de fichiers")
        print(" 11. Valider l'integrite du state")
        print(" 12. Creer un rapport d'integrite")
        print(" 13. Mode debug - Afficher le state complet")
        print(" 14. Quitter")

        choice = input("\nChoisissez une option (1-14) : ").strip()

        handlers = {
            "1": generate_api_for_model,
            "2": list_generated_apis,
            "3": link_models_interactive,
            "4": handle_create_app,
            "5": run_unit_tests_for_model,
            "6": handle_generate_frontend,
            "7": list_generated_frontends_menu,
            "8": handle_generate_api_and_frontend,
            "9": show_statistics,
            "10": lambda sm: sm.sync_with_filesystem(),
            "11": lambda sm: sm.validate_state_integrity(),
            "12": show_integrity_report,
            "13": show_debug_info,
        }
        if choice == "14":
            print("Au revoir !")
            break
        handler = handlers.get(choice)
        if handler is None:
            print("❌ Option invalide. Veuillez choisir 1-14.")
            continue
        handler(state_manager)

# Codes de retour d'une génération (aussi utilisés comme codes de sortie du mode non interactif)
EXIT_OK = 0
EXIT_NOT_FOUND = 1          # aucun JSON ne déclare le modèle
EXIT_INVALID_SCHEMA = 2     # JSON illisible ou schéma invalide
EXIT_GENERATION_FAILED = 3  # la génération a échoué (tout a été annulé)

_FAILURE_LABELS = {
    EXIT_NOT_FOUND: "JSON introuvable",
    EXIT_INVALID_SCHEMA: "schéma invalide",
    EXIT_GENERATION_FAILED: "génération échouée",
}


def parse_model_names(raw: str) -> List[str]:
    """Noms de modèles séparés par des virgules (--generate Elitest,Dragon), sans doublon, dans l'ordre."""
    names: List[str] = []
    for name in raw.split(","):
        name = name.strip()
        if name and name not in names:
            names.append(name)
    return names


def parse_selection(raw: str, total: int) -> List[int]:
    """
    Transforme une saisie comme « 1,2,3 », « 1-3 », « 1, 3-5 » ou « tous » en indices (0 = premier),
    sans doublon et dans l'ordre saisi. Lève ValueError avec un message clair si la saisie est invalide.
    """
    text = re.sub(r"\s*-\s*", "-", raw.strip().lower())
    if not text:
        raise ValueError("Aucune sélection.")
    if text in ("tous", "toutes", "all", "*"):
        return list(range(total))

    indices: List[int] = []
    for part in re.split(r"[,\s;]+", text):
        if not part:
            continue
        if re.fullmatch(r"\d+-\d+", part):
            start, end = (int(bound) for bound in part.split("-"))
            if start > end:
                raise ValueError(f"Plage invalide : « {part} » (le début dépasse la fin).")
            numbers = range(start, end + 1)
        elif part.isdecimal():
            numbers = [int(part)]
        else:
            raise ValueError(f"Sélection invalide : « {part} » (attendu : 1,2,3 ou 1-3 ou tous).")
        for number in numbers:
            if not 1 <= number <= total:
                raise ValueError(f"Numéro hors liste : {number} (choisissez entre 1 et {total}).")
            if number - 1 not in indices:
                indices.append(number - 1)
    if not indices:
        raise ValueError("Aucune sélection.")
    return indices


def declared_app_name(state_manager: ImprovedStateManager, zone: str, model_name: str) -> str:
    """Application cible déclarée par le JSON d'un modèle (« ? » si le JSON est introuvable ou illisible)."""
    model_file = state_manager.find_model_file(zone, model_name)
    if model_file is None:
        return "?"
    try:
        with open(model_file, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError) as error:
        print(f"⚠️  {model_file.name} illisible : {error}", file=sys.stderr)
        return "?"
    app_name = data.get("app_name") if isinstance(data, dict) else None
    return app_name if isinstance(app_name, str) and app_name else DEFAULT_APP_NAME


def _status_mark(done: bool) -> str:
    return "✅" if done else "❌"


def select_models(
    state_manager: ImprovedStateManager,
    title: str,
    show_status: bool = False,
    *,
    show_frontend_status: bool = False,
) -> Optional[List[Tuple[str, str]]]:
    """
    Affiche les modèles disponibles et lit une sélection multiple (1,2,3 / 1-3 / tous).
    show_status : pastille API déjà générée.
    show_frontend_status : pastille interface frontend déjà générée.
    Retourne la liste de (zone, modèle) dans l'ordre saisi, ou None (message déjà affiché).
    """
    available_models = state_manager.list_available_models()
    if not available_models:
        print("❌ Aucun modèle disponible.")
        return None

    print(f"\n📋 {title}")
    model_list: List[Tuple[str, str]] = []
    for zone, models in available_models.items():
        for model in models:
            app_name = state_manager.get_api_app_name(model) if state_manager.is_api_generated(model) \
                else declared_app_name(state_manager, zone, model)
            line = f"{len(model_list) + 1}. {model} (Zone: {zone}, app: {app_name})"
            if show_status and show_frontend_status:
                api_mark = _status_mark(state_manager.is_api_generated(model))
                ui_mark = _status_mark(state_manager.is_frontend_generated(model))
                line += f" - API {api_mark}  Interface {ui_mark}"
            elif show_status:
                line += (
                    " - ✅ Généré"
                    if state_manager.is_api_generated(model)
                    else " - ❌ Non généré"
                )
            elif show_frontend_status:
                line += (
                    " - ✅ Interface générée"
                    if state_manager.is_frontend_generated(model)
                    else " - ❌ Interface non générée"
                )
            print(line)
            model_list.append((zone, model))

    raw = input(f"\nChoisissez un ou plusieurs modèles (ex. 1,2,3 ou 1-3 ou « tous ») [1-{len(model_list)}] : ")
    try:
        indices = parse_selection(raw, len(model_list))
    except ValueError as error:
        print(f"❌ {error}")
        return None
    return [model_list[index] for index in indices]


def ask_regenerate(models: List[str]) -> bool:
    """Demande une confirmation unique avant de régénérer des API déjà générées."""
    print(f"⚠️  L'API existe déjà pour : {', '.join(models)}")
    return input("Voulez-vous les régénérer ? (o/N): ").strip().lower() == "o"


def ask_regenerate_frontend(models: List[str]) -> bool:
    """Demande une confirmation unique avant de régénérer des interfaces déjà générées."""
    print(f"⚠️  L'interface frontend existe déjà pour : {', '.join(models)}")
    return input("Voulez-vous les régénérer ? (o/N): ").strip().lower() == "o"


def sync_and_validate(state_manager: ImprovedStateManager) -> None:
    """Synchronise l'état avec les fichiers puis contrôle son intégrité (une fois par lot)."""
    print()
    state_manager.sync_with_filesystem()
    if not state_manager.validate_state_integrity():
        print("⚠️  Génération terminée avec des avertissements.")


def _load_and_validate(state_manager: ImprovedStateManager, zone: str, model_name: str):
    """JSON d'un modèle + schéma validé : (fichier, données, définition, code). Code != EXIT_OK en cas d'échec."""
    loaded = load_model_json(state_manager, zone, model_name)
    if loaded is None:
        return None, None, None, EXIT_NOT_FOUND
    model_file, model_data = loaded
    try:
        definition = SchemaValidator.validate_model(model_data)
    except Exception as error:
        print(f"❌ Schéma invalide: {error}")
        return None, None, None, EXIT_INVALID_SCHEMA
    print(f"✅ Schéma validé pour {definition.model_name}")
    return model_file, model_data, definition, EXIT_OK


def generate_backend_for_model(state_manager: ImprovedStateManager, zone: str, model_name: str) -> int:
    """Génère l'API d'un modèle et l'enregistre dans l'état. Retourne EXIT_OK ou un code d'échec."""
    model_file, model_data, definition, code = _load_and_validate(state_manager, zone, model_name)
    if code != EXIT_OK:
        return code
    model_name = definition.model_name

    generator = ImprovedCodeGenerator()
    success = generator.generate_api(model_data, zone, relations=state_manager.get_relations_for(model_name))
    if not success:
        print(f"❌ Erreur lors de la génération de l'API pour {model_name}.")
        return EXIT_GENERATION_FAILED

    state_manager.add_generated_api(
        model_name,
        zone,
        model_file.name,
        resource_plural=definition.resource_plural,
        app_name=definition.app_name,
    )
    return EXIT_OK


def generate_frontend_for_model(state_manager: ImprovedStateManager, zone: str, model_name: str) -> int:
    """Génère l'interface frontend d'un modèle. Retourne EXIT_OK ou un code d'échec."""
    model_file, model_data, definition, code = _load_and_validate(state_manager, zone, model_name)
    if code != EXIT_OK:
        return code
    if not FrontendCodeGenerator().generate_frontend_interface(model_data, zone):
        print(f"❌ Erreur lors de la génération frontend pour {definition.model_name}.")
        return EXIT_GENERATION_FAILED
    state_manager.add_generated_frontend(
        definition.model_name,
        zone,
        model_file.name if model_file is not None else f"{definition.model_name.lower()}.json",
    )
    return EXIT_OK


def run_generation(
    state_manager: ImprovedStateManager,
    targets: List[Tuple[str, str]],
    backend: bool = True,
    frontend: bool = False,
    confirm_regenerate: Optional[Callable[[List[str]], bool]] = None,
    confirm_regenerate_frontend: Optional[Callable[[List[str]], bool]] = None,
) -> List[Dict[str, Any]]:
    """
    Génère l'API et/ou l'interface de chaque modèle (zone, nom), l'un après l'autre.
    Un échec n'interrompt pas les suivants. Avec backend et frontend, l'interface d'un modèle n'est générée
    que si son API l'a été. confirm_regenerate (liste des API déjà générées) -> False ignore ces modèles ;
    confirm_regenerate_frontend idem pour les interfaces (mode frontend seul, ou modèles dont l'API
    n'est pas déjà filtrée). None régénère sans demander. Retourne une entrée par modèle.
    """
    skipped: List[str] = []
    if backend and confirm_regenerate is not None:
        already = [name for _, name in targets if state_manager.is_api_generated(name)]
        if already and not confirm_regenerate(already):
            skipped = already
            targets = [(zone, name) for zone, name in targets if name not in already]
            print(f"⏭️  Ignorés (API déjà générée) : {', '.join(skipped)}")

    skipped_frontend: List[str] = []
    if frontend and confirm_regenerate_frontend is not None:
        already_ui = [name for _, name in targets if state_manager.is_frontend_generated(name)]
        if already_ui and not confirm_regenerate_frontend(already_ui):
            skipped_frontend = already_ui
            if not backend:
                targets = [(zone, name) for zone, name in targets if name not in already_ui]
                print(f"⏭️  Ignorés (interface déjà générée) : {', '.join(skipped_frontend)}")
            else:
                print(
                    f"⏭️  Interfaces non régénérées (déjà présentes) : {', '.join(skipped_frontend)}"
                )

    results: List[Dict[str, Any]] = []
    total = len(targets)
    for position, (zone, name) in enumerate(targets, start=1):
        if total > 1:
            print(f"\n{'━' * 60}\n[{position}/{total}] {name} (zone {zone})\n{'━' * 60}")
        entry: Dict[str, Any] = {"model": name, "zone": zone, "backend": None, "frontend": None, "skipped": False}
        if backend:
            entry["backend"] = generate_backend_for_model(state_manager, zone, name)
        if frontend:
            if name in skipped_frontend and backend:
                print(f"⏭️  Interface de {name} ignorée : déjà générée (régénération refusée).")
            elif backend and entry["backend"] != EXIT_OK:
                print(f"⏭️  Interface de {name} ignorée : l'API n'a pas pu être générée.")
            else:
                entry["frontend"] = generate_frontend_for_model(state_manager, zone, name)
        results.append(entry)

    results.extend({"model": name, "zone": "", "backend": None, "frontend": None, "skipped": True} for name in skipped)
    if not backend:
        results.extend(
            {"model": name, "zone": "", "backend": None, "frontend": None, "skipped": True}
            for name in skipped_frontend
        )

    if backend and any(entry["backend"] == EXIT_OK for entry in results):
        sync_and_validate(state_manager)
    if len(results) > 1 or (backend and frontend):
        print_generation_summary(results, backend, frontend)
    return results


def _step_label(label: str, code: Optional[int]) -> str:
    if code is None:
        return f"{label} ⏭️"
    if code == EXIT_OK:
        return f"{label} ✅"
    return f"{label} ❌ ({_FAILURE_LABELS.get(code, 'échec')})"


def print_generation_summary(results: List[Dict[str, Any]], backend: bool, frontend: bool) -> None:
    """Résumé final : une ligne par modèle, avec le résultat de chaque étape demandée."""
    print(f"\n{'=' * 60}\n📊 RÉSUMÉ ({len(results)} modèle(s))\n{'=' * 60}")
    failures = 0
    for entry in results:
        if entry["skipped"]:
            print(f"  ⏭️  {entry['model']} : ignoré (régénération refusée)")
            continue
        steps = []
        if backend:
            steps.append(_step_label("API", entry["backend"]))
        if frontend:
            steps.append(_step_label("Interface", entry["frontend"]))
        failed = exit_code_for([entry]) != EXIT_OK
        failures += failed
        print(f"  {'❌' if failed else '✅'} {entry['model']} : {'  '.join(steps)}")
    if failures:
        print(f"\n⚠️  {failures} modèle(s) en échec : corrigez-les puis relancez uniquement ceux-là.")
    else:
        print("\n✅ Tout a été généré avec succès !")


def exit_code_for(results: List[Dict[str, Any]]) -> int:
    """Code de sortie : EXIT_OK si tout a réussi, sinon le code d'échec le plus élevé."""
    codes = [
        code
        for entry in results
        for code in (entry["backend"], entry["frontend"])
        if code is not None and code != EXIT_OK
    ]
    return max(codes) if codes else EXIT_OK


def generate_api_for_model(state_manager: ImprovedStateManager):
    """Menu Backend 1 : génère l'API d'un ou plusieurs modèles."""
    targets = select_models(state_manager, "Modèles disponibles:", show_status=True)
    if targets:
        run_generation(state_manager, targets, backend=True, frontend=False, confirm_regenerate=ask_regenerate)


def handle_generate_frontend(state_manager: ImprovedStateManager):
    """Menu Frontend 6 : génère l'interface frontend d'un ou plusieurs modèles."""
    targets = select_models(
        state_manager,
        "Modèles disponibles pour le frontend:",
        show_frontend_status=True,
    )
    if targets:
        run_generation(
            state_manager,
            targets,
            backend=False,
            frontend=True,
            confirm_regenerate_frontend=ask_regenerate_frontend,
        )


def handle_generate_api_and_frontend(state_manager: ImprovedStateManager):
    """Menu Général 8 : génère l'API puis l'interface d'un ou plusieurs modèles en une seule fois."""
    targets = select_models(
        state_manager,
        "Modèles disponibles (API + interface):",
        show_status=True,
        show_frontend_status=True,
    )
    if targets:
        run_generation(
            state_manager,
            targets,
            backend=True,
            frontend=True,
            confirm_regenerate=ask_regenerate,
            confirm_regenerate_frontend=ask_regenerate_frontend,
        )


def list_generated_apis(state_manager: ImprovedStateManager):
    """Liste les APIs générées avec détails."""
    generated_apis = state_manager.list_generated_apis()

    if not generated_apis:
        print("📋 Aucune API generee.")
        return

    print("\n📋 APIs generees:")
    for api in generated_apis:
        info = state_manager.get_model_info(api)
        if info:
            status_icon = "🟢" if info.get("status") == "active" else "🔴"
            auto_detected = " (auto-detecte)" if info.get("auto_detected") else ""
            app_name = info.get("app_name") or "metier"
            print(
                f"  {status_icon} {api} (zone: {info['zone']}, app: {app_name})"
                f" - {info.get('generated_at', 'N/A')}{auto_detected}"
            )
        else:
            print(f"  ❓ {api} (informations manquantes)")


def list_generated_frontends_menu(state_manager: ImprovedStateManager):
    """Liste les interfaces frontend générées (state + présence disque)."""
    names = state_manager.list_generated_frontends()
    # Inclure aussi les modèles disponibles dont api.ts existe déjà sans entrée state
    seen = {name.lower() for name in names}
    for zone, models in state_manager.list_available_models().items():
        for model_name in models:
            if model_name.lower() in seen:
                continue
            if state_manager.is_frontend_generated(model_name):
                names.append(model_name)
                seen.add(model_name.lower())

    if not names:
        print("📋 Aucune interface frontend generee.")
        return

    print("\n🎨 Interfaces frontend generees:")
    for name in names:
        info = state_manager.get_frontend_info(name)
        on_disk = state_manager.frontend_api_file(name).is_file()
        disk_icon = "🟢" if on_disk else "🔴"
        if info:
            auto_detected = " (auto-detecte)" if info.get("auto_detected") else ""
            path = info.get("path") or f"frontend/src/models/{name.lower()}/"
            print(
                f"  {disk_icon} {name} (zone: {info.get('zone', '?')})"
                f" - {info.get('generated_at', 'N/A')}{auto_detected}"
                f"\n      📁 {path}"
            )
        else:
            path = state_manager.frontend_api_file(name).parent.as_posix()
            print(
                f"  {disk_icon} {name} (non enregistre dans le state)"
                f"\n      📁 {path}/"
            )


def show_statistics(state_manager: ImprovedStateManager):
    """Affiche les statistiques détaillées."""
    stats = state_manager.get_statistics()
    print("\n📊 Statistiques detaillees:")
    print(f"  - Modeles disponibles: {stats.get('total_models', 0)}")
    print(f"  - APIs generees: {stats.get('total_apis', 0)}")
    print(f"  - Interfaces frontend: {stats.get('total_frontends', 0)}")
    print(f"  - Relations creees: {stats.get('total_relations', 0)}")
    print(f"  - Zones utilisees: {', '.join(stats.get('zones_used', []))}")

    available_models = state_manager.list_available_models()
    if available_models:
        print("\n📋 Repartition par zone:")
        for zone, models in available_models.items():
            print(f"  Zone {zone}: {len(models)} modeles ({', '.join(models.keys())})")

def show_integrity_report(state_manager: ImprovedStateManager):
    """Affiche un rapport d'intégrité détaillé."""
    print("\n🔍 Génération du rapport d'intégrité...")
    report = state_manager.create_integrity_report()
    
    print(f"\n📋 RAPPORT D'INTÉGRITÉ")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Version du state: {report['state_version']}")
    print(f"Total APIs: {report['total_apis']}")
    
    if report['issues']:
        print(f"\n❌ Problèmes détectés ({len(report['issues'])}):")
        for issue in report['issues']:
            print(f"  - {issue}")
    
    if report['warnings']:
        print(f"\n⚠️  Avertissements ({len(report['warnings'])}):")
        for warning in report['warnings']:
            print(f"  - {warning}")
    
    print(f"\n📁 État des fichiers par API:")
    for api_name, file_status in report['file_status'].items():
        status_icons = []
        status_icons.append("📄" if file_status['model_exists'] else "❌")
        status_icons.append("🔄" if file_status['serializer_exists'] else "❌")
        status_icons.append("🎯" if file_status['viewset_exists'] else "❌")
        
        modified_info = ""
        if file_status['files_modified']:
            modified_info = f" (modifiés: {', '.join(file_status['files_modified'])})"
        
        print(f"  {api_name}: {''.join(status_icons)}{modified_info}")
    
    print(f"\nLégende: 📄=Modèle, 🔄=Serializer, 🎯=ViewSet")

def link_models_interactive(state_manager: ImprovedStateManager):
    """Crée une relation entre deux modèles existants via des invites utilisateur."""
    try:
        # Lister les APIs générées disponibles
        generated = state_manager.list_generated_apis()
        if not generated:
            print("❌ Aucune API générée. Veuillez d'abord générer au moins deux modèles.")
            return

        print("\n📋 Modèles disponibles pour la relation:")
        for idx, name in enumerate(generated, start=1):
            print(f"  {idx}. {name}")

        def pick_model(prompt: str) -> str:
            while True:
                val = input(prompt).strip()
                if val.isdecimal():
                    i = int(val)
                    if 1 <= i <= len(generated):
                        return generated[i-1]
                # Autoriser saisie directe du nom
                if val in generated:
                    return val
                print("❌ Sélection invalide. Entrez un numéro ou un nom existant.")

        source = pick_model("\nSélectionnez le modèle source (numéro ou nom): ")
        target = pick_model("Sélectionnez le modèle cible (numéro ou nom): ")
        source_app, target_app = resolve_relation_apps(state_manager, source, target)
        describe_apps(source, source_app, target, target_app)

        # Type de relation avec descriptions détaillées
        print("\n📚 Types de relations disponibles:")
        print("\n🔗 ForeignKey (fk) - Relation Un-à-Plusieurs:")
        print(f"   • La clé étrangère sera stockée dans la table '{source.lower()}'")
        print(f"   • Colonne créée: '{target.lower()}_id' (référence vers {target})")
        print(f"   • Un {source} peut référencer un seul {target}")
        print(f"   • Un {target} peut être référencé par plusieurs {source}")
        print(f"   • Exemple: {source}.{target.lower()} → accès au {target} lié")
        print(f"   • Exemple: {target}.{pluralize(source.lower())}.all() → tous les {source} liés")
        
        print("\n🔗 OneToOneField (o2o) - Relation Un-à-Un:")
        print(f"   • La clé étrangère sera stockée dans la table '{source.lower()}'")
        print(f"   • Colonne créée: '{target.lower()}_id' (référence unique vers {target})")
        print(f"   • Un {source} peut référencer un seul {target}")
        print(f"   • Un {target} peut être référencé par un seul {source}")
        print(f"   • Exemple: {source}.{target.lower()} → accès au {target} lié")
        print(f"   • Exemple: {target}.{source.lower()} → accès au {source} lié")
        
        print("\n🔗 ManyToManyField (m2m) - Relation Plusieurs-à-Plusieurs:")
        print(f"   • Table intermédiaire créée: '{source_app}_{source.lower()}_{pluralize(target.lower())}'")
        print(f"   • Colonnes: '{source.lower()}_id' et '{target.lower()}_id'")
        print(f"   • Un {source} peut référencer plusieurs {target}")
        print(f"   • Un {target} peut être référencé par plusieurs {source}")
        print(f"   • Exemple: {source}.{pluralize(target.lower())}.all() → tous les {target} liés")
        print(f"   • Exemple: {target}.{pluralize(source.lower())}.all() → tous les {source} liés")
        
        rel = None
        while rel not in {"fk", "o2o", "m2m"}:
            rel = input("\nType de relation (fk/o2o/m2m) [fk]: ").strip().lower() or "fk"
            if rel not in {"fk", "o2o", "m2m"}:
                print("❌ Type invalide. Choisissez fk, o2o ou m2m.")

        # Nom du champ côté source (optionnel)
        default_field = pluralize(target.lower()) if rel == "m2m" else target.lower()
        field_in = input(f"Nom du champ côté source [{default_field}]: ").strip()
        field_name = field_in if field_in else default_field

        # related_name côté cible (optionnel)
        default_related = pluralize(source.lower()) if rel in {"fk", "m2m"} else source.lower()
        related_in = input(f"related_name côté cible [{default_related}]: ").strip()
        related_name = related_in if related_in else default_related

        # on_delete (FK/O2O)
        on_delete = "models.RESTRICT"
        if rel in {"fk", "o2o"}:
            od = input("on_delete (models.RESTRICT/models.CASCADE/models.PROTECT/models.SET_NULL) [models.RESTRICT]: ").strip()
            if od in {"models.RESTRICT", "models.CASCADE", "models.PROTECT", "models.SET_NULL"}:
                on_delete = od

        # nullable (FK/O2O)
        nullable = True
        if rel in {"fk", "o2o"}:
            nb = input("Champ nullable ? (o/N) [N]: ").strip().lower()
            if nb == "o":
                nullable = True
            elif nb == "n":
                nullable = False

        # Afficher un résumé de ce qui va être implémenté
        print("\n📋 Résumé de l'implémentation:")
        print("="*50)
        
        if rel == "fk":
            print(f"🗃️  Table modifiée: {source_app}_{pluralize(source.lower())}")
            print(f"📝 Colonne ajoutée: {field_name}_id (INTEGER, {'NULL' if nullable else 'NOT NULL'})")
            print(f"🔗 Contrainte FK: REFERENCES {target_app}_{pluralize(target.lower())}(id) ON DELETE {on_delete.split('.')[-1]}")
            print(f"\n🐍 Code Django généré:")
            print(f"   • {source}.{field_name} = models.ForeignKey('{target}', on_delete={on_delete}, related_name='{related_name}', null={nullable}, blank={nullable})")
            print(f"\n📡 API - Utilisation:")
            print(f"   • POST/PUT: {{'..., \"{field_name}\": {target.lower()}_id, ...'}}")
            print(f"   • GET: Données du {target} incluses automatiquement")
            
        elif rel == "o2o":
            print(f"🗃️  Table modifiée: {source_app}_{pluralize(source.lower())}")
            print(f"📝 Colonne ajoutée: {field_name}_id (INTEGER UNIQUE, {'NULL' if nullable else 'NOT NULL'})")
            print(f"🔗 Contrainte FK: REFERENCES {target_app}_{pluralize(target.lower())}(id) ON DELETE {on_delete.split('.')[-1]}")
            print(f"\n🐍 Code Django généré:")
            print(f"   • {source}.{field_name} = models.OneToOneField('{target}', on_delete={on_delete}, related_name='{related_name}', null={nullable}, blank={nullable})")
            print(f"\n📡 API - Utilisation:")
            print(f"   • POST/PUT: {{'..., \"{field_name}\": {target.lower()}_id, ...'}}")
            print(f"   • GET: Données du {target} incluses automatiquement")
            
        elif rel == "m2m":
            print(f"🗃️  Table créée: {source_app}_{source.lower()}_{field_name}")
            print(f"📝 Colonnes: id (PK), {source.lower()}_id (FK), {target.lower()}_id (FK)")
            print(f"🔗 Contraintes FK: REFERENCES {source_app}_{pluralize(source.lower())}(id) et {target_app}_{pluralize(target.lower())}(id)")
            print(f"\n🐍 Code Django généré:")
            print(f"   • {source}.{field_name} = models.ManyToManyField('{target}', related_name='{related_name}', blank=True)")
            print(f"\n📡 API - Utilisation:")
            print(f"   • POST/PUT: {{'..., \"{field_name}\": [{target.lower()}_id1, {target.lower()}_id2], ...'}}")
            print(f"   • GET: Liste des {target} liés incluse automatiquement")
        
        print("\n" + "="*50)
        confirm = input("Confirmer la création de cette relation ? (o/N): ").strip().lower()
        if confirm != 'o':
            print("❌ Création annulée.")
            return

        # Exécuter le lien
        generator = ImprovedCodeGenerator()
        ok = generator.link_models(
            source_model=source,
            target_model=target,
            relation_type=rel,
            field_name=field_name,
            related_name=related_name,
            on_delete=on_delete,
            nullable=nullable,
            app_label=source_app,
            target_app_label=target_app,
        )
        if ok and generator.last_relation:
            state_manager.add_relation(generator.last_relation)
        if ok:
            print("\n✅ Relation créée avec succès!")
            print("\n💡 Rappel:")
            print("   • makemigrations + migrate sont lances automatiquement (sans nom d'app)")
            print("   • Testez l'API avec les nouveaux champs de relation")
            # Sync state
            state_manager.sync_with_filesystem()
        else:
            print("❌ Échec de la création de la relation")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def show_debug_info(state_manager: ImprovedStateManager):
    """Affiche les informations de debug."""
    print("\n🐛 INFORMATIONS DE DEBUG")
    print("="*50)
    
    state = state_manager.state
    print(f"Version du state: {state.get('version', 'N/A')}")
    print(f"Créé le: {state.get('created_at', 'N/A')}")
    print(f"Dernière mise à jour: {state.get('last_updated', 'N/A')}")
    
    print(f"\nAPIs générées ({len(state.get('generated_apis', {}))}):")
    for api_name, api_info in state.get('generated_apis', {}).items():
        print(f"  - {api_name}: {json.dumps(api_info, indent=4, ensure_ascii=False)}")
    
    print(f"\nModèles disponibles:")
    for zone, models in state.get('available_models', {}).items():
        print(f"  Zone {zone}: {json.dumps(models, indent=4, ensure_ascii=False)}")
    
    print(f"\nChecksums des fichiers ({len(state.get('file_checksums', {}))}):")
    for file_path, checksum_info in state.get('file_checksums', {}).items():
        print(f"  - {file_path}: {checksum_info}")

def run_unit_tests_for_model(state_manager: ImprovedStateManager):
    """Lance les tests unitaires pour un modèle sélectionné."""
    generated_apis = state_manager.list_generated_apis()
    
    if not generated_apis:
        print("❌ Aucune API générée trouvée.")
        return
    
    print("\n🧪 Tests unitaires disponibles:")
    api_list = []
    index = 1
    
    for api_name in generated_apis:
        api_info = state_manager.get_model_info(api_name)
        zone = api_info.get('zone', 'N/A') if api_info else 'N/A'
        print(f"{index}. {api_name} (Zone: {zone})")
        api_list.append((api_name, zone))
        index += 1
    
    try:
        choice = int(input(f"\nChoisissez un modèle pour les tests (1-{len(api_list)}): ")) - 1
        if 0 <= choice < len(api_list):
            model_name, zone = api_list[choice]
            
            print(f"\n🚀 Lancement des tests unitaires pour {model_name}...")
            
            # Construire la commande de test avec la bonne structure
            test_command = f"python manage.py test app.tests.test_{model_name.lower()}"
            
            print(f"📋 Commande: {test_command}")
            print("="*60)
            
            # Exécuter les tests
            import subprocess
            import os
            
            # Changer vers le répertoire backend
            backend_dir = Path(__file__).parent.parent
            
            try:
                result = subprocess.run(
                    test_command.split(),
                    cwd=backend_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # Timeout de 5 minutes
                )
                
                print("📤 SORTIE DES TESTS:")
                print("-" * 40)
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print("⚠️  ERREURS:")
                    print(result.stderr)
                
                if result.returncode == 0:
                    print("\n✅ Tests réussis !")
                else:
                    print(f"\n❌ Tests échoués (code de retour: {result.returncode})")
                    
            except subprocess.TimeoutExpired:
                print("⏰ Timeout: Les tests ont pris trop de temps à s'exécuter.")
            except Exception as e:
                print(f"❌ Erreur lors de l'exécution des tests: {e}")
                
        else:
            print("❌ Choix invalide.")
            
    except ValueError:
        print("❌ Veuillez entrer un numéro valide.")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def handle_create_app(state_manager: ImprovedStateManager):
    """Crée une nouvelle application Django via AppCreator."""
    print("\n" + "="*60)
    print("🏗️  CRÉATION D'UNE NOUVELLE APPLICATION DJANGO")
    print("="*60)
    print("Règles: snake_case, pas de nom réservé (core, metier, app, config...)")

    app_name = input("\nNom de la nouvelle application: ").strip()

    creator = AppCreator()
    error = creator.validate_app_name(app_name)
    if error:
        print(f"❌ Nom invalide: {error}")
        return

    print(f"\n📋 L'application suivante va être créée:")
    print(f"  - Dossier : app/{app_name}/")
    print(f"  - Config  : app.{app_name} dans LOCAL_APPS")
    print(f"  - URLs    : path('api/', include('app.{app_name}.urls'))")

    confirm = input("\nConfirmer ? (o/N): ").strip().lower()
    if confirm != 'o':
        print("❌ Création annulée.")
        return

    success = creator.create_app(app_name)
    if success:
        state_manager.add_created_app(app_name)

def main():
    """Fonction principale améliorée."""
    try:
        parser = argparse.ArgumentParser(description=f"Générateur d'API CRUD v{GENERATOR_VERSION}")
        parser.add_argument("--version", action="version", version=f"generate_api.py v{GENERATOR_VERSION}")
        parser.add_argument("--generate", dest="generate", help="Modèle(s) à générer (model_name), séparés par des virgules (ex. Elitest,Dragon)")
        parser.add_argument("--with-frontend", dest="with_frontend", action="store_true", help="Avec --generate : génère aussi l'interface frontend de chaque modèle")
        parser.add_argument("--zone", dest="zone", default="zone_1", help="Zone du modèle (par défaut: zone_1)")
        parser.add_argument("--sync", action="store_true", help="Synchroniser avec le système de fichiers")
        parser.add_argument("--validate", action="store_true", help="Valider l'intégrité du state")
        parser.add_argument("--report", action="store_true", help="Générer un rapport d'intégrité")
        # Nouveau: lien entre modèles
        parser.add_argument("--link", action="store_true", help="Créer une relation entre deux modèles existants")
        parser.add_argument("--from", dest="link_from", help="Modèle source pour la relation (ex: Eliseefor)")
        parser.add_argument("--to", dest="link_to", help="Modèle cible pour la relation (ex: Eliseeone)")
        parser.add_argument("--type", dest="link_type", choices=["fk", "o2o", "m2m"], help="Type de relation")
        parser.add_argument("--name", dest="link_field_name", help="Nom du champ côté source (par défaut dérivé)")
        parser.add_argument("--related_name", dest="link_related_name", help="related_name côté cible (par défaut dérivé)")
        parser.add_argument("--on_delete", dest="link_on_delete", default="models.RESTRICT", help="Stratégie on_delete pour FK/O2O")
        parser.add_argument("--nullable", dest="link_nullable", action="store_true", help="Champ nullable (FK/O2O)")
        parser.add_argument("--frontend", dest="frontend", help="Modèle(s) pour générer l'interface frontend, séparés par des virgules")
        args = parser.parse_args()

        # Initialiser le state manager amélioré
        state_manager = ImprovedStateManager()

        if args.sync:
            # Mode synchronisation
            print("🔄 MODE SYNCHRONISATION")
            print("="*50)
            state_manager.sync_with_filesystem()
            return

        if args.validate:
            # Mode validation
            print("🔍 MODE VALIDATION")
            print("="*50)
            if state_manager.validate_state_integrity():
                print("✅ State valide")
                sys.exit(0)
            else:
                print("❌ Problèmes détectés dans le state")
                sys.exit(1)

        if args.report:
            # Mode rapport
            print("📋 MODE RAPPORT")
            print("="*50)
            show_integrity_report(state_manager)
            return

        if args.link:
            # Mode lien entre modèles
            print("🔗 MODE LIEN ENTRE MODÈLES")
            print("="*50)
            if not (args.link_from and args.link_to and args.link_type):
                print("❌ Paramètres requis: --link --from <Source> --to <Target> --type <fk|o2o|m2m>")
                sys.exit(2)

            source_app, target_app = resolve_relation_apps(state_manager, args.link_from, args.link_to)
            describe_apps(args.link_from, source_app, args.link_to, target_app)

            generator = ImprovedCodeGenerator()
            success = generator.link_models(
                source_model=args.link_from,
                target_model=args.link_to,
                relation_type=args.link_type,
                field_name=args.link_field_name,
                related_name=args.link_related_name,
                on_delete=args.link_on_delete,
                nullable=args.link_nullable,
                app_label=source_app,
                target_app_label=target_app,
            )
            if success:
                if generator.last_relation:
                    state_manager.add_relation(generator.last_relation)
                print("✅ Relation créée avec succès")
                sys.exit(0)
            else:
                print("❌ Échec de la création de la relation")
                sys.exit(3)

        if args.with_frontend and not args.generate:
            print("❌ --with-frontend s'utilise avec --generate (ex. --generate Elitest,Dragon --with-frontend)")
            sys.exit(2)

        if args.generate:
            # Mode non interactif : génération directe d'un ou plusieurs modèles (séparés par des virgules)
            names = parse_model_names(args.generate)
            if not names:
                print("❌ Aucun modèle indiqué pour --generate")
                sys.exit(2)

            print("🚀 GÉNÉRATION NON INTERACTIVE AMÉLIORÉE" + (" (API + INTERFACE)" if args.with_frontend else ""))
            print("="*60)

            # Scanner et synchroniser
            print("\n📁 Scan des modèles disponibles...")
            scan_models_in_zones(state_manager)
            print("\n🔄 Synchronisation avec le système de fichiers...")
            state_manager.sync_with_filesystem()

            results = run_generation(
                state_manager, [(args.zone, name) for name in names], backend=True, frontend=args.with_frontend
            )
            sys.exit(exit_code_for(results))

        if args.frontend:
            names = parse_model_names(args.frontend)
            if not names:
                print("❌ Aucun modèle indiqué pour --frontend")
                sys.exit(2)

            print("🚀 GÉNÉRATION FRONTEND NON INTERACTIVE")
            print("="*60)

            results = run_generation(
                state_manager, [(args.zone, name) for name in names], backend=False, frontend=True
            )
            sys.exit(exit_code_for(results))

        # Mode interactif par défaut
        print(f"🚀 GÉNÉRATEUR D'API CRUD v{GENERATOR_VERSION}")
        print("="*60)

        # Scanner les modèles dans les zones
        print("\n📁 Scan des modèles disponibles...")
        scan_models_in_zones(state_manager)

        # Synchroniser avec le système de fichiers
        print("\n🔄 Synchronisation avec le système de fichiers...")
        state_manager.sync_with_filesystem()

        # Afficher les statistiques
        stats = state_manager.get_statistics()
        print(f"\n📊 Statistiques:")
        print(f"  - Modèles disponibles: {stats.get('total_models', 0)}")
        print(f"  - APIs générées: {stats.get('total_apis', 0)}")
        print(f"  - Interfaces frontend: {stats.get('total_frontends', 0)}")
        print(f"  - Relations créées: {stats.get('total_relations', 0)}")

        # Afficher les modèles disponibles par zone
        available_models = state_manager.list_available_models()
        if available_models:
            print(f"\n📋 Modèles disponibles:")
            for zone, models in available_models.items():
                print(f"  Zone {zone}: {', '.join(models.keys())}")

        # Lancer l'interface interactive
        interactive_menu(state_manager)
    
    except KeyboardInterrupt:
        print("\n\nArret demande par l'utilisateur.")
        sys.exit(0)
    except Exception as e:
        print(f"Erreur critique: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()