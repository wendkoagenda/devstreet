"""Génère le socle CRUD Chantier avec les outils existants, sans UI ni seeds."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.generator.app_creator import AppCreator
from scripts.generator.code_generator import ImprovedCodeGenerator
from scripts.generator.state_manager import ImprovedStateManager


def main():
    backend = Path(__file__).resolve().parents[1]
    if (backend / "app/projects").exists():
        raise SystemExit(
            "App déjà créée : ne pas régénérer après spécialisation métier."
        )
    creator = AppCreator()
    assert creator.create_app("projects")
    state = ImprovedStateManager()
    generator = ImprovedCodeGenerator(apply_migrations=False)
    for path in sorted((backend / "scripts/models_zones/chantier").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not generator.generate_api(data, "chantier"):
            raise SystemExit(f"Échec de génération : {path.name}")
        state.add_generated_api(
            data["model_name"],
            "chantier",
            path.name,
            resource_plural=data["meta"]["resource_plural"],
            app_name="projects",
        )


if __name__ == "__main__":
    main()
