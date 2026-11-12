"""Génère le socle CRUD DevStreet Hub avec les outils existants, sans UI ni seeds."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.generator.app_creator import AppCreator
from scripts.generator.code_generator import ImprovedCodeGenerator
from scripts.generator.state_manager import ImprovedStateManager


def main():
    backend = Path(__file__).resolve().parents[1]
    if (backend / "app/devstreet_hub").exists():
        raise SystemExit(
            "App déjà créée : ne pas régénérer après spécialisation métier."
        )
    creator = AppCreator()
    assert creator.create_app("devstreet_hub")
    state = ImprovedStateManager()
    generator = ImprovedCodeGenerator(apply_migrations=False)
    for path in sorted((backend / "scripts/models_zones/devstreet_hub").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not generator.generate_api(data, "devstreet_hub"):
            raise SystemExit(f"Échec de génération : {path.name}")
        state.add_generated_api(
            data["model_name"],
            "devstreet_hub",
            path.name,
            resource_plural=data["meta"]["resource_plural"],
            app_name="devstreet_hub",
        )


if __name__ == "__main__":
    main()
