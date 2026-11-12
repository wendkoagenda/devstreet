"""
AppCreator: crée le scaffold complet d'une nouvelle application Django.
"""
import os
import re
from pathlib import Path
from typing import Optional

RESERVED_NAMES = {
    'core', 'metier', 'app', 'config', 'admin', 'auth',
    'contenttypes', 'sessions', 'messages', 'staticfiles',
}

APP_NAME_RE = re.compile(r'^[a-z][a-z0-9_]*$')

SUBDIRS = [
    'interfaces',
    'repositories',
    'services',
    'views',
    'permissions',
    'management/commands',
    'migrations',
]


class AppCreator:
    """Crée le scaffold complet d'une nouvelle application Django."""

    def __init__(self):
        # Jinja2 est un outil de développement : l'absence est signalée ici, explicitement
        try:
            from jinja2 import Environment, FileSystemLoader  # type: ignore
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "Jinja2 n'est pas installé. Exécutez: pip install -r requirements.txt"
            ) from error
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.backend_dir = Path(__file__).resolve().parent.parent.parent
        self.app_root = self.backend_dir / 'app'
        self.config_dir = self.backend_dir / 'config'
        self.settings_file = self.config_dir / 'settings.py'
        self.urls_file = self.config_dir / 'urls.py'

    def validate_app_name(self, name: str) -> Optional[str]:
        """Valide le nom de l'app. Retourne un message d'erreur ou None si valide."""
        if not APP_NAME_RE.match(name):
            return (
                "Le nom doit être en snake_case "
                "(lettres minuscules, chiffres, underscores, commençant par une lettre)."
            )
        if name in RESERVED_NAMES:
            return f"'{name}' est un nom réservé."
        app_path = self.app_root / name
        if app_path.exists():
            return f"L'application '{name}' existe déjà dans app/."
        try:
            settings_content = self.settings_file.read_text(encoding='utf-8')
            if f"'app.{name}'" in settings_content:
                return f"'app.{name}' est déjà présent dans LOCAL_APPS."
        except IOError as error:
            # settings.py illisible : impossible de vérifier LOCAL_APPS, on le signale au lieu de répondre « tout va bien »
            return f"Impossible de lire {self.settings_file} pour vérifier LOCAL_APPS : {error}"
        return None

    def create_directory_structure(self, app_name: str):
        """Crée l'arborescence de dossiers pour la nouvelle app."""
        app_path = self.app_root / app_name
        app_path.mkdir(parents=True, exist_ok=True)

        root_init = app_path / '__init__.py'
        if not root_init.exists():
            root_init.write_text('', encoding='utf-8')

        for subdir in SUBDIRS:
            subdir_path = app_path / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)
            init_file = subdir_path / '__init__.py'
            if not init_file.exists():
                init_file.write_text('', encoding='utf-8')

        mgmt_init = app_path / 'management' / '__init__.py'
        if not mgmt_init.exists():
            mgmt_init.write_text('', encoding='utf-8')

    def render_templates(self, app_name: str):
        """Génère les fichiers de base via Jinja2."""
        app_path = self.app_root / app_name
        class_name = ''.join(part.title() for part in app_name.split('_')) + 'Config'

        templates_and_targets = [
            ('app_config.py.j2', app_path / 'apps.py'),
            ('app_urls.py.j2', app_path / 'urls.py'),
            ('app_admin.py.j2', app_path / 'admin.py'),
            ('app_models.py.j2', app_path / 'models.py'),
            ('app_serializers.py.j2', app_path / 'serializers.py'),
        ]

        context = {
            'app_name': app_name,
            'class_name': class_name,
        }

        for template_name, target_path in templates_and_targets:
            template = self.env.get_template(template_name)
            content = template.render(**context)
            target_path.write_text(content, encoding='utf-8')
            print(f"  ✅ {target_path.relative_to(self.backend_dir)}")

    def patch_settings(self, app_name: str):
        """Injecte 'app.{app_name}' dans LOCAL_APPS de config/settings.py."""
        content = self.settings_file.read_text(encoding='utf-8')
        entry = f"    'app.{app_name}',"

        if f"'app.{app_name}'" in content:
            print(f"  ℹ️  settings.py: 'app.{app_name}' déjà présent, ignoré.")
            return

        pattern = re.compile(r'(LOCAL_APPS\s*=\s*\[.*?\])', re.DOTALL)
        match = pattern.search(content)
        if not match:
            print(
                f"  ⚠️  Impossible de localiser LOCAL_APPS dans settings.py. "
                f"Ajoutez manuellement \"'app.{app_name}'\"."
            )
            return

        old_block = match.group(1)
        stripped = old_block.rstrip()
        if not stripped.endswith(']'):
            print(
                f"  ⚠️  Structure LOCAL_APPS non standard. "
                f"Ajoutez manuellement \"'app.{app_name}'\"."
            )
            return

        new_block = stripped[:-1].rstrip() + '\n' + entry + '\n]'
        new_content = content.replace(old_block, new_block)
        self.settings_file.write_text(new_content, encoding='utf-8')
        print(f"  ✅ settings.py: 'app.{app_name}' ajouté à LOCAL_APPS.")

    def patch_urls(self, app_name: str):
        """Injecte le path() dans config/urls.py (urlpatterns + schema_view patterns)."""
        content = self.urls_file.read_text(encoding='utf-8')

        if f"include('app.{app_name}.urls')" in content:
            print(f"  ℹ️  urls.py: 'app.{app_name}.urls' déjà présent, ignoré.")
            return

        # Une ligne de référence par bloc (schema_view puis urlpatterns), indentation conservée.
        # Le motif est ancré sur la ligne entière : une ligne indentée de 8 espaces ne doit pas
        # être confondue avec une ligne de 4 espaces (sinon l'include est inséré en double).
        reference = re.compile(
            r"^(?P<indent>[ \t]*)path\('api/', include\('app\.metier\.urls'\)\),[ \t]*$",
            re.MULTILINE,
        )
        inserted = 0

        def add_include(match):
            nonlocal inserted
            inserted += 1
            indent = match.group('indent')
            return f"{match.group(0)}\n{indent}path('api/', include('app.{app_name}.urls')),"

        content = reference.sub(add_include, content)

        if inserted:
            print(f"  ✅ urls.py: path('api/', include('app.{app_name}.urls')) ajouté ({inserted} bloc(s)).")
            self.urls_file.write_text(content, encoding='utf-8')
        else:
            print(
                f"  ⚠️  Ligne de référence non trouvée dans config/urls.py. "
                f"Ajoutez manuellement: path('api/', include('app.{app_name}.urls')),"
            )

    def create_app(self, app_name: str) -> bool:
        """Orchestre la création complète de l'application."""
        try:
            print(f"\n📁 Création de l'arborescence pour '{app_name}'...")
            self.create_directory_structure(app_name)

            print(f"\n📝 Génération des fichiers de base...")
            self.render_templates(app_name)

            print(f"\n⚙️  Mise à jour de config/settings.py...")
            self.patch_settings(app_name)

            print(f"\n🔗 Mise à jour de config/urls.py...")
            self.patch_urls(app_name)

            print(f"\n✅ Application 'app.{app_name}' créée avec succès !")
            print(f"\n📋 Prochaines étapes:")
            print(f"  1. python manage.py makemigrations {app_name}")
            print(f"  2. python manage.py migrate")
            print(f"  3. python manage.py check")
            return True
        except Exception as e:
            print(f"\n❌ Erreur lors de la création de l'application: {e}")
            import traceback
            traceback.print_exc()
            return False
