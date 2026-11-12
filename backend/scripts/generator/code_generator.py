"""
Générateur de code amélioré avec gestion cumulative des fichiers partagés.
"""
import ast
import os
import re
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
from .schema_validator import DEFAULT_APP_NAME, ModelDefinition, SchemaValidator
from .field_utils import format_django_field_param
from .naming_utils import get_resource_plural, pluralize
import subprocess
import sys
SERIALIZER_SYSTEM_FIELDS = ['created_by', 'updated_by', 'created_at', 'updated_at']
# Ancre commune des serializers générés : « fields = '__all__' » (anciens fichiers) ou « fields = [...] » (liste explicite)
SERIALIZER_FIELDS_PATTERN = re.compile(r"fields\s*=\s*(?:'__all__'|\[[^\]]*\])")


def serializer_field_names(model_def) -> list:
    """Champs exposés par le serializer : explicitement listés, un champ ajouté plus tard n'est jamais exposé par défaut."""
    names = ['id']
    names += [name for name in model_def.fields if name not in names]
    names += [name for name in SERIALIZER_SYSTEM_FIELDS if name not in names]
    return names


class ImprovedCodeGenerator:
    """Générateur de code amélioré pour l'architecture Repository Pattern."""
    
    def __init__(self, template_dir: str = None, app_root: str = None, apply_migrations: bool = True):
        """
        app_root : dossier contenant les applications Django (défaut : backend/app).
        apply_migrations : False pour ne pas lancer makemigrations/migrate (tests).
        """
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        if app_root is None:
            app_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'app')
        self.app_root = app_root
        self.apply_migrations = apply_migrations

        # Initialisation paresseuse de Jinja2 avec message explicite si manquant
        # Jinja2 est un outil de développement : l'absence est signalée ici, explicitement
        try:
            from jinja2 import Environment, FileSystemLoader  # type: ignore
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "Jinja2 n'est pas installé. Exécutez: .\\backend\\venv\\Scripts\\python.exe -m pip install -r backend\\requirements.txt puis relancez le script avec l'interpréteur du venv."
            ) from error
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, file_path: str) -> str:
        """Crée un backup d'un fichier avant modification."""
        if os.path.exists(file_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{os.path.basename(file_path)}.{timestamp}.backup"
            backup_path = os.path.join(self.backup_dir, backup_name)
            shutil.copy2(file_path, backup_path)
            return backup_path
        return None
    
    def validate_python_syntax(self, file_path: str) -> bool:
        """Valide la syntaxe Python d'un fichier."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, file_path, 'exec')
            return True
        except SyntaxError as e:
            print(f"❌ Erreur de syntaxe dans {file_path}: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de la validation de {file_path}: {e}")
            return False
    
    def validate_imports(self, file_path: str) -> bool:
        """Valide que tous les imports d'un fichier fonctionnent."""
        try:
            import sys
            import importlib.util
            
            # Ajouter le répertoire du projet au path temporairement
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            spec = importlib.util.spec_from_file_location("temp_module", file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return True
            return False
        except ImportError as e:
            print(f"❌ Erreur d'import dans {file_path}: {e}")
            return False
        except Exception as e:
            print(f"❌ Erreur lors de la validation des imports de {file_path}: {e}")
            return False
    
    def merge_models_file(self, model_def: ModelDefinition, app_dir: str) -> bool:
        """Merge un nouveau modèle dans le fichier models.py existant."""
        models_file = os.path.join(app_dir, 'models.py')
        
        # Créer un backup
        backup_path = self.create_backup(models_file)
        if backup_path:
            print(f"📁 Backup créé: {backup_path}")
        
        try:
            if os.path.exists(models_file):
                # Lire le contenu existant
                with open(models_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                # Vérifier si le modèle existe déjà
                existing_model_pattern = rf'class {re.escape(model_def.model_name)}\(models\.Model\):[\s\S]*?(?=\nclass |\Z)'
                if re.search(existing_model_pattern, existing_content):
                    print(f"⚠️  Le modèle {model_def.model_name} existe déjà, remplacement...")
                    # Remplacer le modèle existant
                    new_model_class = self.generate_model_class_only(model_def)
                    updated_content = re.sub(
                        existing_model_pattern,
                        lambda _m: new_model_class + '\n\n',
                        existing_content,
                    )
                else:
                    # Ajouter le nouveau modèle à la fin
                    new_model_class = self.generate_model_class_only(model_def)
                    updated_content = existing_content.rstrip() + '\n\n\n' + new_model_class + '\n'
                
                # Mettre à jour les imports si nécessaire
                updated_content = self.update_imports_in_models(updated_content, model_def)
                
                with open(models_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
            else:
                # Créer le fichier models.py complet
                header = "from django.db import models\n\n\n"
                new_model_content = self.update_imports_in_models(
                    header + self.generate_model_class_only(model_def) + "\n", model_def
                )
                with open(models_file, 'w', encoding='utf-8') as f:
                    f.write(new_model_content)
            
            # Valider le fichier généré
            if not self.validate_python_syntax(models_file):
                # Restaurer le backup en cas d'erreur
                if backup_path and os.path.exists(backup_path):
                    shutil.copy2(backup_path, models_file)
                    print(f"🔄 Backup restauré suite à une erreur de syntaxe")
                return False
            
            print(f"✅ Modèle {model_def.model_name} ajouté/mis à jour dans models.py")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du merge du modèle: {e}")
            # Restaurer le backup en cas d'erreur
            if backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, models_file)
                print(f"🔄 Backup restauré suite à une erreur")
            return False
    
    def generate_model_class_only(self, model_def: ModelDefinition) -> str:
        """Génère uniquement la classe du modèle sans les imports."""
        model_class = f"""class {model_def.model_name}(models.Model):
    \"\"\"
    {model_def.model_name} model.
    \"\"\"
    """
        
        # Ajouter les champs
        for field_name, field in model_def.fields.items():
            if field_name != 'id':  # Skip l'ID car il est auto-généré
                field_type = model_def.get_django_field_type(field_name)
                field_params = model_def.get_field_params(field_name)
                
                model_class += f"\n    {field_name} = models.{field_type}("
                
                param_strings = [
                    format_django_field_param(param_name, param_value)
                    for param_name, param_value in field_params.items()
                ]
                
                model_class += ', '.join(param_strings)
                model_class += ")"
        
        # Ajouter les champs système s'ils n'existent pas
        system_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']
        for sys_field in system_fields:
            if sys_field not in model_def.fields:
                if sys_field in ['created_by', 'updated_by']:
                    model_class += f"""
    {sys_field} = models.IntegerField(
        verbose_name="{'Créé par' if sys_field == 'created_by' else 'Modifié par'}",
        help_text="ID de l'utilisateur {'créateur' if sys_field == 'created_by' else 'ayant modifié'}"
    )"""
                elif sys_field == 'created_at':
                    model_class += f"""
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )"""
                elif sys_field == 'updated_at':
                    model_class += f"""
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )"""
        
        # Déterminer le champ à utiliser dans __str__ (1er CharField non-système, sinon id)
        system_field_names = {'created_by', 'updated_by', 'created_at', 'updated_at'}
        str_field = next(
            (
                name for name, field in model_def.fields.items()
                if field.type == 'CharField' and name not in system_field_names
            ),
            None
        )
        str_field_expr = f"self.{str_field}" if str_field else "self.id"

        # Ajouter la Meta class (forçage du pluriel sur le nom de table)
        provided_db_table = model_def.meta.get('db_table')
        if provided_db_table:
            db_table = provided_db_table
        else:
            db_table = f"{model_def.app_name}_{model_def.resource_plural.replace('-', '_')}"
        verbose_name = model_def.meta.get('verbose_name', model_def.model_name)
        verbose_name_plural = model_def.meta.get(
            'verbose_name_plural',
            model_def.resource_plural.replace('_', ' ').title(),
        )
        
        ordering = model_def.meta.get('ordering') or ['-created_at']
        if isinstance(ordering, str):
            ordering = [ordering]

        model_class += f"""

    class Meta:
        db_table = {db_table!r}
        verbose_name = {verbose_name!r}
        verbose_name_plural = {verbose_name_plural!r}
        ordering = {list(ordering)!r}

    def __str__(self):
        return f"{{{str_field_expr}}}"

    def get_absolute_url(self):
        return f"/{model_def.app_name}/{model_def.resource_plural}/{{self.id}}/" """
        
        return model_class

    def run_management_command(self, args: List[str]) -> bool:
        """Exécute une commande de gestion Django via manage.py dans le bon environnement."""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            manage_py = os.path.join(base_dir, 'manage.py')
            full_cmd = [sys.executable, manage_py] + args
            result = subprocess.run(full_cmd, cwd=base_dir, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Erreur commande {' '.join(args)}:\n{result.stderr.strip()}")
                return False
            print(result.stdout.strip())
            return True
        except Exception as e:
            print(f"❌ Exception lors de l'exécution de {' '.join(args)}: {e}")
            return False

    def create_and_apply_migrations(self, app_label: Optional[str] = DEFAULT_APP_NAME) -> bool:
        """
        Crée et applique les migrations.
        app_label : application ciblée ; None = `makemigrations` sans nom (Django détecte tous les changements,
        utile après une relation entre applications).
        """
        print("🧱 Création des migrations...")
        makemigrations_args = ['makemigrations'] if app_label is None else ['makemigrations', app_label]
        if not self.run_management_command(makemigrations_args):
            return False
        print("🚚 Application des migrations...")
        if not self.run_management_command(['migrate']):
            # Si l'application des migrations échoue, on laisse l'utilisateur corriger (BDD, etc.)
            return False
        return True

    def run_model_seed(self, model_name: str) -> bool:
        """Exécute seed_<modele> (permissions + données de démo + assignation aux rôles Admin)."""
        command = f"seed_{model_name.lower()}"
        print(f"🌱 Exécution des seeds ({command})...")
        return self.run_management_command([command])

    # ==========================
    #        RELATIONS
    # ==========================
    def link_models(
        self,
        source_model: str,
        target_model: str,
        relation_type: str,
        field_name: Optional[str] = None,
        related_name: Optional[str] = None,
        on_delete: str = 'models.RESTRICT',
        nullable: bool = True,
        app_label: str = DEFAULT_APP_NAME,
        replay: bool = False,
        target_app_label: Optional[str] = None,
    ) -> bool:
        """
        Crée une relation entre deux modèles déjà existants et met à jour les serializers
        pour exposer les données liées en lecture (forward et inverse), puis applique les migrations.
        relation_type in {'fk', 'o2o', 'm2m'}
        app_label : application du modèle source (qui porte le champ relationnel).
        target_app_label : application du modèle cible (défaut : la même que la source) ; les deux
        modèles peuvent appartenir à des applications différentes.
        replay=True : rejeu d'une relation déjà enregistrée (après régénération d'un modèle), sans consignes.
        En cas de succès, self.last_relation décrit la relation (à enregistrer dans le state).
        """
        self.last_relation = None
        target_app = target_app_label or app_label
        cross_app = target_app != app_label
        snapshots: Dict[str, str] = {}

        def snapshot(path: str) -> None:
            if path not in snapshots:
                with open(path, 'r', encoding='utf-8') as handle:
                    snapshots[path] = handle.read()

        def rollback() -> None:
            """Remet les fichiers dans leur état d'avant la relation (une relation à moitié écrite casse Django)."""
            for path, original in snapshots.items():
                with open(path, 'w', encoding='utf-8') as handle:
                    handle.write(original)
            if snapshots:
                print("🔄 Rollback : fichiers de la relation restaurés dans leur état initial.")

        try:
            app_dir = os.path.join(self.app_root, app_label)
            models_file = os.path.join(app_dir, 'models.py')
            serializers_file = os.path.join(app_dir, 'serializers.py')
            target_dir = os.path.join(self.app_root, target_app)
            target_models_file = os.path.join(target_dir, 'models.py')
            target_serializers_file = os.path.join(target_dir, 'serializers.py')

            for required in (models_file, serializers_file, target_models_file, target_serializers_file):
                if not os.path.exists(required):
                    print(f"❌ Fichier introuvable : {required} (vérifiez les applications « {app_label} » et « {target_app} »)")
                    return False

            # Normalisations
            source_cls = source_model.strip()
            target_cls = target_model.strip()
            rel_type = relation_type.strip().lower()
            if rel_type not in {'fk', 'o2o', 'm2m'}:
                print("❌ Type de relation invalide (attendu: fk, o2o, m2m)")
                return False

            default_field = pluralize(target_cls.lower()) if rel_type == 'm2m' else target_cls.lower()
            field = field_name.strip() if field_name else default_field
            default_related = (
                pluralize(source_cls.lower()) if rel_type in {'fk', 'm2m'} else source_cls.lower()
            )
            related = related_name.strip() if related_name else default_related

            # 1) Mettre à jour models.py (ajout du champ relationnel dans la classe source)
            with open(models_file, 'r', encoding='utf-8') as f:
                models_content = f.read()

            if cross_app:
                with open(target_models_file, 'r', encoding='utf-8') as f:
                    target_models_content = f.read()
            else:
                target_models_content = models_content

            # Vérifier présence des classes (chacune dans le models.py de son application)
            if f'class {source_cls}(models.Model):' not in models_content:
                print(f"❌ Classe source {source_cls} introuvable dans app/{app_label}/models.py")
                return False
            if f'class {target_cls}(models.Model):' not in target_models_content:
                print(f"❌ Classe cible {target_cls} introuvable dans app/{target_app}/models.py")
                return False

            # Construire la ligne de champ : « app.Modèle » est une référence paresseuse, valable entre applications
            nullable_part = ', null=True, blank=True' if nullable else ''
            if rel_type == 'fk':
                field_line = (
                    f"    {field} = models.ForeignKey('{target_app}.{target_cls}', on_delete={on_delete}, "
                    f"related_name='{related}'{nullable_part})"
                )
            elif rel_type == 'o2o':
                field_line = (
                    f"    {field} = models.OneToOneField('{target_app}.{target_cls}', on_delete={on_delete}, "
                    f"related_name='{related}'{nullable_part})"
                )
            else:  # m2m
                field_line = (
                    f"    {field} = models.ManyToManyField('{target_app}.{target_cls}', related_name='{related}')"
                )

            # Insérer le champ juste avant la Meta de la classe source
            class_pattern = re.compile(rf"class {source_cls}\(models\.Model\):([\s\S]*?)\n\s*class Meta:")
            match = class_pattern.search(models_content)
            if not match:
                print("❌ Impossible de localiser l'emplacement d'insertion dans la classe source")
                return False

            class_body = match.group(1)
            if f"\n    {field} = models." in class_body:
                print("ℹ️  Le champ relationnel existe déjà, aucune modification du modèle nécessaire")
            else:
                snapshot(models_file)
                new_class_body = class_body.rstrip() + "\n" + field_line + "\n"
                models_content = models_content.replace(class_body, new_class_body)

                with open(models_file, 'w', encoding='utf-8') as f:
                    f.write(models_content)
                where = f" → app.{target_app}.{target_cls}" if cross_app else ""
                print(f"✅ Relation ajoutée dans {source_cls}.{field}{where}")

            # 2) Mettre à jour serializers.py (forward et inverse) + depth=1.
            # Entre deux applications : la partie « source » va dans le serializers.py de la source (avec l'import
            # du modèle cible), la partie « inverse » dans celui de la cible.
            snapshot(serializers_file)
            if cross_app:
                snapshot(target_serializers_file)
                serializers_ok = self._update_serializers_for_relation(
                    serializers_file, source_cls, target_cls, rel_type, field, related,
                    part='source', target_app_label=target_app,
                ) and self._update_serializers_for_relation(
                    target_serializers_file, source_cls, target_cls, rel_type, field, related, part='target',
                )
            else:
                serializers_ok = self._update_serializers_for_relation(
                    serializers_file, source_cls, target_cls, rel_type, field, related
                )
            if not serializers_ok:
                rollback()
                return False

            self.last_relation = {
                "source": source_cls,
                "target": target_cls,
                "type": rel_type,
                "field": field,
                "related_name": related,
                "on_delete": on_delete,
                "nullable": nullable,
                "app_label": app_label,
                "target_app_label": target_app,
            }

            # 3) Migrations automatiques (sans nom d'app : Django détecte source et cible, y compris cross-app)
            if replay:
                return True
            if self.apply_migrations:
                if not self.create_and_apply_migrations(app_label=None):
                    print(
                        "⚠️  Migrations non appliquées automatiquement après la relation. "
                        "Exécutez: 'python manage.py makemigrations' puis 'python manage.py migrate'."
                    )
                    return True
                print("✅ Migrations créées et appliquées pour la relation.")
            else:
                print(
                    "ℹ️  Migrations non lancées (apply_migrations=False). "
                    "Exécutez: 'python manage.py makemigrations' puis 'python manage.py migrate'."
                )

            return True
        except Exception as e:
            print(f"❌ Erreur lors du linkage des modèles: {e}")
            try:
                rollback()
            except OSError as restore_error:
                print(f"⚠️  Restauration impossible : {restore_error}")
            return False

    @staticmethod
    def _ensure_model_import(content: str, app_name: str, model_name: str) -> str:
        """Garantit « from app.<app_name>.models import <model_name> » dans un serializers.py (idempotent)."""
        lines = content.split('\n')
        pattern = re.compile(rf'^from app\.{re.escape(app_name)}\.models import (.+)$')
        for index, line in enumerate(lines):
            match = pattern.match(line)
            if match and '(' not in match.group(1):
                imported = [name.strip() for name in match.group(1).split(',')]
                if model_name not in imported:
                    imported.append(model_name)
                    lines[index] = f"from app.{app_name}.models import {', '.join(sorted(imported))}"
                return '\n'.join(lines)

        new_import = f"from app.{app_name}.models import {model_name}"
        insert_at = 0
        try:
            for node in ast.parse(content).body:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    insert_at = node.end_lineno
        except SyntaxError as error:
            print(f"⚠️  serializers.py non analysable ({error}) : import du modèle {model_name} placé en tête de fichier")
        lines.insert(insert_at, new_import)
        return '\n'.join(lines)

    def _update_serializers_for_relation(
        self,
        serializers_file: str,
        source_cls: str,
        target_cls: str,
        rel_type: str,
        field: str,
        related: str,
        part: str = 'both',
        target_app_label: Optional[str] = None,
    ) -> bool:
        """
        Injecte la sérialisation nested forward et inverse dans serializers.py et ajoute depth=1 si absent.
        part : 'both' (source et cible dans le même fichier), 'source' (serializers.py de la source, avec l'import
        du modèle cible de target_app_label) ou 'target' (serializers.py de la cible : partie inverse).
        """
        do_source = part in ('both', 'source')
        do_target = part in ('both', 'target')
        try:
            with open(serializers_file, 'r', encoding='utf-8') as f:
                content = f.read()

            def ensure_depth_in_meta(class_name: str, text: str) -> str:
                # Localiser la classe
                cls_pat = re.compile(rf"class {class_name}Serializer\([\s\S]*?\):([\s\S]*?)\n\n", re.MULTILINE)
                m = cls_pat.search(text + "\n\n")
                if not m:
                    return text
                cls_block = m.group(0)
                # Localiser Meta (avec ou sans méthode def qui suit)
                meta_pat = re.compile(r"\n\s+class Meta:\n([\s\S]*?)(?=\n\s+def |\n\nclass |\Z)")
                mm = meta_pat.search(cls_block)
                if not mm:
                    return text
                meta_block = mm.group(1)
                if 'depth =' in meta_block or 'depth=' in meta_block:
                    return text
                # Insérer depth après fields (« fields = '__all__' » ou liste explicite)
                meta_block_new = SERIALIZER_FIELDS_PATTERN.sub(lambda found: found.group(0) + "\n        depth = 1", meta_block, count=1)
                cls_block_new = cls_block.replace(meta_block, meta_block_new)
                return text.replace(cls_block, cls_block_new)

            def class_text(class_name: str) -> str:
                """Texte de la classe serializer (jusqu'à la classe suivante), pour les contrôles d'idempotence."""
                start = content.find(f"class {class_name}Serializer(")
                if start == -1:
                    return ""
                end = content.find("\nclass ", start + 1)
                return content[start:] if end == -1 else content[start:end]

            def inject_forward(class_name: str, nested_class: str, attr_name: str, many: bool) -> None:
                nonlocal content
                if f"# Ajouter les données de la relation {attr_name} si elle existe" in class_text(class_name):
                    return  # déjà injecté (rejeu après régénération)
                # Localiser to_representation
                cls_start = content.find(f"class {class_name}Serializer(")
                if cls_start == -1:
                    return
                method_start = content.find("def to_representation(self, instance):", cls_start)
                if method_start == -1:
                    return
                return_idx = content.find("return data", method_start)
                if return_idx == -1:
                    return
                injection = []
                injection.append(f"        # Ajouter les données de la relation {attr_name} si elle existe")
                if many:
                    injection.append(f"        if hasattr(instance, '{attr_name}'):")
                    injection.append(f"            {attr_name}_data = []")
                    injection.append(f"            for item in instance.{attr_name}.all():")
                    injection.append(f"                {attr_name}_data.append({{")
                    injection.append(f"                    'id': item.id,")
                    injection.append(f"                    '__str__': str(item),")
                    injection.append(f"                }})")
                    injection.append(f"            data['{attr_name}'] = {attr_name}_data")
                    injection.append(f"        else:")
                    injection.append(f"            data['{attr_name}'] = []")
                else:
                    injection.append(f"        if hasattr(instance, '{attr_name}') and instance.{attr_name}:")
                    injection.append(f"            data['{attr_name}'] = {{")
                    injection.append(f"                'id': instance.{attr_name}.id,")
                    injection.append(f"                '__str__': str(instance.{attr_name}),")
                    injection.append(f"            }}")
                    injection.append(f"        else:")
                    injection.append(f"            data['{attr_name}'] = None")
                injection.append("        ")
                # Préserver l'indentation du 'return data'
                return_line_start = content.rfind('\n', 0, return_idx) + 1
                return_indentation = content[return_line_start:return_idx]
                content = content[:return_idx] + "\n" + "\n".join(injection) + "\n" + return_indentation + content[return_idx:]

            def inject_reverse(class_name: str, nested_class: str, attr_name: str, many: bool) -> None:
                nonlocal content
                if f"# Ajouter les données des relations {attr_name} (reverse FK)" in class_text(class_name):
                    return  # déjà injecté (rejeu après régénération)
                cls_start = content.find(f"class {class_name}Serializer(")
                if cls_start == -1:
                    return
                method_start = content.find("def to_representation(self, instance):", cls_start)
                if method_start == -1:
                    return
                return_idx = content.find("return data", method_start)
                if return_idx == -1:
                    return
                injection = []
                injection.append(f"        # Ajouter les données des relations {attr_name} (reverse FK)")
                if many:
                    injection.append(f"        if hasattr(instance, '{attr_name}'):")
                    injection.append(f"            {attr_name}_data = []")
                    injection.append(f"            for item in instance.{attr_name}.all():")
                    injection.append(f"                {attr_name}_data.append({{")
                    injection.append(f"                    'id': item.id,")
                    injection.append(f"                    '__str__': str(item),")
                    injection.append(f"                }})")
                    injection.append(f"            data['{attr_name}'] = {attr_name}_data")
                    injection.append(f"        else:")
                    injection.append(f"            data['{attr_name}'] = []")
                else:
                    injection.append(f"        if hasattr(instance, '{attr_name}') and instance.{attr_name}:")
                    injection.append(f"            data['{attr_name}'] = {{")
                    injection.append(f"                'id': instance.{attr_name}.id,")
                    injection.append(f"                '__str__': str(instance.{attr_name}),")
                    injection.append(f"            }}")
                    injection.append(f"        else:")
                    injection.append(f"            data['{attr_name}'] = None")
                injection.append("        ")
                # Préserver l'indentation du 'return data'
                return_line_start = content.rfind('\n', 0, return_idx) + 1
                return_indentation = content[return_line_start:return_idx]
                content = content[:return_idx] + "\n" + "\n".join(injection) + "\n" + return_indentation + content[return_idx:]

            def ensure_field_in_meta(class_name: str, field_name: str, text: str) -> str:
                """Ajoute le champ de relation à la liste explicite « fields = [...] » (sans effet avec '__all__')."""
                cls_start = text.find(f"class {class_name}Serializer(")
                if cls_start == -1:
                    return text
                match = re.search(r"fields\s*=\s*\[([^\]]*)\]", text[cls_start:])
                if not match or re.search(r"['\"]" + re.escape(field_name) + r"['\"]", match.group(1)):
                    return text
                start = cls_start + match.start()
                updated = match.group(0)[:-1].rstrip().rstrip(',') + f", '{field_name}']"
                return text[:start] + updated + text[start + len(match.group(0)):]

            if do_source:
                # Le champ de relation doit être exposé par le serializer qui le porte
                content = ensure_field_in_meta(source_cls, field, content)

                # Le modèle cible d'une autre application n'est pas déjà importé par ce serializers.py
                if target_app_label:
                    content = self._ensure_model_import(content, target_app_label, target_cls)

            # Assurer depth=1 dans les serializers concernés
            if do_source:
                content = ensure_depth_in_meta(source_cls, content)
            if do_target:
                content = ensure_depth_in_meta(target_cls, content)

            # Injecter forward dans source
            if do_source:
                inject_forward(source_cls, target_cls, field, many=(rel_type == 'm2m'))

            # Injecter reverse dans target
            if do_target:
                if rel_type == 'fk' or rel_type == 'm2m':
                    inject_reverse(target_cls, source_cls, related, many=True)
                else:  # o2o
                    inject_reverse(target_cls, source_cls, related, many=False)

            # Injecter la logique de conversion ID vers objet dans create/update
            def inject_fk_conversion(class_name: str, fk_field: str, target_model: str) -> None:
                nonlocal content
                # Trouver la classe serializer
                class_pattern = re.compile(rf"class {class_name}Serializer\([^\)]+\):[\s\S]*?(?=\nclass|\Z)", re.MULTILINE)
                class_match = class_pattern.search(content)
                if not class_match:
                    return
                
                class_content = class_match.group(0)
                if f"# Conversion automatique {fk_field} ID vers objet" in class_content:
                    return  # déjà injecté (rejeu après régénération)
                class_start = class_match.start()
                class_end = class_match.end()

                # Vérifier si les méthodes create et update existent
                has_create = "def create(self, validated_data):" in class_content
                has_update = "def update(self, instance, validated_data):" in class_content
                
                conversion_code = f"""        # Conversion automatique {fk_field} ID vers objet
        if '{fk_field}' in validated_data and not isinstance(validated_data['{fk_field}'], {target_model}):
            try:
                pk = int(validated_data['{fk_field}'])  # gère str ou int
                {fk_field}_obj = {target_model}.objects.get(pk=pk)
                validated_data['{fk_field}'] = {fk_field}_obj
            except (ValueError, {target_model}.DoesNotExist):
                raise serializers.ValidationError({{'{fk_field}': '{target_model} avec cet ID n\\'existe pas.'}})
        """
                
                if has_create:
                    # Injecter dans la méthode create existante
                    create_method = re.search(r"def create\(self, validated_data\):[\s\S]*?return super\(\)\.create\(validated_data\)", class_content)
                    if create_method:
                        super_call_pos = create_method.group(0).rfind("return super().create(validated_data)")
                        if super_call_pos != -1:
                            method_start = create_method.start()
                            injection_pos = class_start + method_start + super_call_pos
                            content = content[:injection_pos] + conversion_code + "\n        " + content[injection_pos:]
                else:
                    # Créer la méthode create
                    create_method = f"""    def create(self, validated_data):
        \"\"\"
        Crée une nouvelle instance de {class_name}.
        \"\"\"
{conversion_code}
        
        return super().create(validated_data)
        
"""
                    # Insérer après la classe Meta
                    meta_match = SERIALIZER_FIELDS_PATTERN.search(class_content)
                    meta_end = meta_match.start() if meta_match else -1
                    if meta_end != -1:
                        meta_end = class_content.find("\n", meta_end) + 1
                        insertion_pos = class_start + meta_end
                        content = content[:insertion_pos] + "\n" + create_method + content[insertion_pos:]
                        # Mettre à jour les positions
                        class_content = content[class_start:class_start + len(class_content) + len(create_method) + 1]
                        class_end += len(create_method) + 1
                
                if has_update:
                    # Injecter dans la méthode update existante
                    update_method = re.search(r"def update\(self, instance, validated_data\):[\s\S]*?return super\(\)\.update\(instance, validated_data\)", class_content)
                    if update_method:
                        super_call_pos = update_method.group(0).rfind("return super().update(instance, validated_data)")
                        if super_call_pos != -1:
                            method_start = update_method.start()
                            injection_pos = class_start + method_start + super_call_pos
                            content = content[:injection_pos] + conversion_code + "\n        " + content[injection_pos:]
                else:
                    # Créer la méthode update
                    update_method = f"""    def update(self, instance, validated_data):
        \"\"\"
        Met à jour une instance de {class_name}.
        \"\"\"
{conversion_code}
        
        return super().update(instance, validated_data)
        
"""
                    # Insérer après create ou après Meta si create n'existe pas
                    if has_create or "def create(self, validated_data):" in content[class_start:class_end]:
                        create_end = content.find("return super().create(validated_data)", class_start)
                        if create_end != -1:
                            create_end = content.find("\n", create_end) + 1
                            content = content[:create_end] + "\n" + update_method + content[create_end:]
                    else:
                        meta_match = SERIALIZER_FIELDS_PATTERN.search(class_content)
                        meta_end = meta_match.start() if meta_match else -1
                        if meta_end != -1:
                            meta_end = class_content.find("\n", meta_end) + 1
                            insertion_pos = class_start + meta_end
                            content = content[:insertion_pos] + "\n" + update_method + content[insertion_pos:]
            
            # Injecter la conversion FK/O2O dans le serializer source (qui contient la relation)
            if do_source and rel_type in ('fk', 'o2o'):
                inject_fk_conversion(source_cls, field, target_cls)

            with open(serializers_file, 'w', encoding='utf-8') as f:
                f.write(content)
            if part == 'both':
                print("✅ Serializers mis à jour (forward + inverse + conversion FK)")
            elif part == 'source':
                print(f"✅ Serializer source mis à jour ({os.path.basename(os.path.dirname(serializers_file))} : forward + conversion FK)")
            else:
                print(f"✅ Serializer cible mis à jour ({os.path.basename(os.path.dirname(serializers_file))} : inverse)")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour des serializers: {e}")
            return False
    
    def update_imports_in_models(self, content: str, model_def: ModelDefinition) -> str:
        """Met à jour les imports dans le fichier models.py."""
        lines = content.split('\n')

        # Vérifier si un champ UUIDField est présent dans le modèle
        has_uuid_field = any(
            field.type == 'UUIDField'
            for field in model_def.fields.values()
        )

        # Vérifier si l'import uuid existe déjà
        if has_uuid_field and not any('import uuid' in line for line in lines):
            for i, line in enumerate(lines):
                if 'from django.db import models' in line:
                    lines.insert(i + 1, 'import uuid')
                    break

        # Vérifier si l'import User existe déjà
        has_user_import = any('from django.contrib.auth import get_user_model' in line for line in lines)
        has_user_assignment = any('User = get_user_model()' in line for line in lines)

        # Un models.py qui définit lui-même le modèle User (core, AUTH_USER_MODEL) ne doit pas appeler
        # get_user_model() à l'import : le modèle n'existe pas encore et Django ne démarre plus.
        defines_user_model = re.search(r'^class User\b', content, re.MULTILINE) is not None
        if defines_user_model:
            has_user_import = True
            has_user_assignment = True

        if not has_user_import:
            # Ajouter l'import après les imports Django
            for i, line in enumerate(lines):
                if 'from django.db import models' in line:
                    lines.insert(i + 1, 'from django.contrib.auth import get_user_model')
                    break

        if not has_user_assignment:
            # Ajouter l'assignation User
            for i, line in enumerate(lines):
                if 'from django.contrib.auth import get_user_model' in line:
                    lines.insert(i + 2, '')
                    lines.insert(i + 3, 'User = get_user_model()')
                    break

        return '\n'.join(lines)
    
    def merge_serializers_file(self, model_def: ModelDefinition, app_dir: str) -> bool:
        """Merge un nouveau serializer dans le fichier serializers.py existant."""
        serializers_file = os.path.join(app_dir, 'serializers.py')
        
        # Créer un backup
        backup_path = self.create_backup(serializers_file)
        if backup_path:
            print(f"📁 Backup créé: {backup_path}")
        
        try:
            if os.path.exists(serializers_file):
                # Lire le contenu existant
                with open(serializers_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                # Vérifier si le serializer existe déjà
                existing_serializer_pattern = rf'class {re.escape(model_def.model_name)}Serializer\(serializers\.ModelSerializer\):[\s\S]*?(?=\nclass |\Z)'
                if re.search(existing_serializer_pattern, existing_content):
                    print(f"⚠️  Le serializer {model_def.model_name}Serializer existe déjà, remplacement...")
                    # Remplacer le serializer existant
                    new_serializer_class = self.generate_serializer_class_only(model_def)
                    updated_content = re.sub(
                        existing_serializer_pattern,
                        lambda _m: new_serializer_class + '\n\n',
                        existing_content,
                    )
                else:
                    # Ajouter le nouveau serializer à la fin
                    new_serializer_class = self.generate_serializer_class_only(model_def)
                    updated_content = existing_content.rstrip() + '\n\n\n' + new_serializer_class + '\n'
                
                # Mettre à jour les imports
                updated_content = self.update_imports_in_serializers(updated_content, model_def)
                
                with open(serializers_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
            else:
                # Créer le fichier serializers.py complet
                template = self.env.get_template('serializer.py.j2')
                new_serializer_content = template.render(model=model_def)
                with open(serializers_file, 'w', encoding='utf-8') as f:
                    f.write(new_serializer_content)
            
            # Valider le fichier généré
            if not self.validate_python_syntax(serializers_file):
                # Restaurer le backup en cas d'erreur
                if backup_path and os.path.exists(backup_path):
                    shutil.copy2(backup_path, serializers_file)
                    print(f"🔄 Backup restauré suite à une erreur de syntaxe")
                return False
            
            print(f"✅ Serializer {model_def.model_name}Serializer ajouté/mis à jour dans serializers.py")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du merge du serializer: {e}")
            # Restaurer le backup en cas d'erreur
            if backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, serializers_file)
                print(f"🔄 Backup restauré suite à une erreur")
            return False
    
    def generate_serializer_class_only(self, model_def: ModelDefinition) -> str:
        """Génère uniquement la classe du serializer."""
        file_fields = model_def.get_file_fields()
        file_repr_lines = ""
        if file_fields:
            file_repr_lines = """
        storage = get_storage_service()"""
            for name in file_fields:
                file_repr_lines += f"""
        if getattr(instance, '{name}', None):
            data['{name}_url'] = storage.url(getattr(instance, '{name}'))"""

        serializer_class = f"""class {model_def.model_name}Serializer(serializers.ModelSerializer):
    \"\"\"
    Serializer pour les {model_def.resource_plural}.
    \"\"\"
    
    class Meta:
        model = {model_def.model_name}
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = {serializer_field_names(model_def)!r}

    def get_fields(self):
        \"\"\"
        Marque les champs système en lecture seule s'ils existent.
        \"\"\"
        fields = super().get_fields()
        for sys_field in ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def to_representation(self, instance):
        \"\"\"
        Personnalise la représentation des données.
        \"\"\"
        data = super().to_representation(instance)
        
        data['created_at'] = instance.created_at.isoformat() if hasattr(instance, 'created_at') else None
        data['updated_at'] = instance.updated_at.isoformat() if hasattr(instance, 'updated_at') else None{file_repr_lines}
        
        return data

    def validate(self, data):
        \"\"\"
        Validation personnalisée des données.
        \"\"\"
        return data"""
        
        return serializer_class
    
    def update_imports_in_serializers(self, content: str, model_def: ModelDefinition) -> str:
        """Met à jour les imports dans le fichier serializers.py."""
        lines = content.split('\n')
        
        # Chercher la ligne d'import des modèles
        app_name = model_def.app_name
        model_import_pattern = rf'from app\.{re.escape(app_name)}\.models import (.+)'
        model_import_line_idx = None
        current_imports = []
        
        for i, line in enumerate(lines):
            match = re.match(model_import_pattern, line)
            if match:
                model_import_line_idx = i
                current_imports = [imp.strip() for imp in match.group(1).split(',')]
                break
        
        # Ajouter le nouveau modèle aux imports s'il n'y est pas déjà
        if model_def.model_name not in current_imports:
            current_imports.append(model_def.model_name)
            current_imports.sort()  # Trier alphabétiquement
            
            new_import_line = f"from app.{app_name}.models import {', '.join(current_imports)}"
            
            if model_import_line_idx is not None:
                lines[model_import_line_idx] = new_import_line
            else:
                # Ajouter l'import après les imports rest_framework
                for i, line in enumerate(lines):
                    if 'from rest_framework import' in line:
                        lines.insert(i + 1, new_import_line)
                        break

        # Import du service de stockage en tête de fichier (une seule fois) ; il est partagé et vit dans metier
        storage_import = "from app.metier.services.storage_service import get_storage_service"
        if model_def.has_file_fields() and not any(line.strip() == storage_import for line in lines):
            insert_at = 0
            for i, line in enumerate(lines):
                if line.startswith(('from ', 'import ')):
                    insert_at = i + 1
            lines.insert(insert_at, storage_import)

        return '\n'.join(lines)
    
    def generate_api(
        self,
        model_data: Dict[str, Any],
        zone: str,
        relations: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Génère une API complète pour un modèle avec gestion améliorée et atomicité.
        relations : relations déjà enregistrées impliquant ce modèle, rejouées après la régénération
        pour ne pas perdre les clés étrangères ni leur sérialisation.
        """
        model_name = model_data.get('model_name', 'Unknown')
        print(f"🚀 Génération améliorée de l'API pour {model_name}")

        # Valider et créer la définition du modèle (avant toute écriture)
        try:
            model_def = SchemaValidator.validate_model(model_data)
        except Exception as e:
            print(f"❌ Validation du modèle échouée : {e}")
            return False

        # Définir le répertoire de sortie : l'application cible vient du JSON (app_name, défaut « metier »)
        app_name = model_def.app_name
        output_dir = self.app_root
        app_dir = os.path.join(output_dir, app_name)

        # L'application doit déjà exister (la créer via le menu « Créer une application ») et le modèle
        # ne doit entrer en collision ni avec une autre application, ni avec une route ou une table existante
        if not self.check_target_app_exists(app_name, app_dir):
            return False
        if not self.check_no_conflict_with_other_apps(model_def):
            return False

        # Créer les répertoires nécessaires
        self.create_directories(app_dir, output_dir)

        # Snapshot des fichiers partagés AVANT toute modification (pour rollback global)
        shared_files = [
            os.path.join(app_dir, 'models.py'),
            os.path.join(app_dir, 'serializers.py'),
            os.path.join(app_dir, 'urls.py'),
        ]
        snapshots: Dict[str, Optional[str]] = {}
        for f in shared_files:
            snapshots[f] = self.create_backup(f)

        def rollback_shared():
            """Restaure les fichiers partagés depuis les snapshots pré-génération."""
            for path, backup in snapshots.items():
                if backup and os.path.exists(backup):
                    shutil.copy2(backup, path)
                    print(f"🔄 Rollback : {os.path.basename(path)} restauré")

        try:
            # Générer les fichiers partagés avec merge
            if not self.merge_models_file(model_def, app_dir):
                rollback_shared()
                return False

            if not self.merge_serializers_file(model_def, app_dir):
                rollback_shared()
                return False

            # Rejouer les relations (la régénération remplace les classes modèle et serializer)
            if not self.replay_relations(relations or [], model_def.model_name, app_name):
                rollback_shared()
                return False

            # Générer les fichiers individuels
            if not self.generate_individual_files(model_def, app_dir, output_dir):
                rollback_shared()
                return False

            # Mettre à jour les URLs pour enregistrer le ViewSet
            if not self.update_app_urls(model_def, app_dir):
                rollback_shared()
                return False

            # Validation post-génération
            if not self.post_generation_validation(model_def, app_dir):
                rollback_shared()
                return False

            # Générer et appliquer les migrations automatiquement
            if self.apply_migrations and not self.create_and_apply_migrations(app_name):
                print(
                    f"⚠️  Migrations non appliquées automatiquement. "
                    f"Exécutez: 'python manage.py makemigrations {app_name}' puis 'python manage.py migrate', "
                    f"puis 'python manage.py seed_{model_def.model_name.lower()}'."
                )
            elif self.apply_migrations:
                # Permissions métier + assignation Admin/Super Admin (nécessaires au front hors bypass superuser API)
                if not self.run_model_seed(model_def.model_name):
                    print(
                        f"⚠️  Seeds non appliqués pour {model_def.model_name}. "
                        f"Exécutez: 'python manage.py seed_{model_def.model_name.lower()}'. "
                        f"Sans cela, les permissions UI (hors superuser API) manquent."
                    )
                else:
                    print(
                        f"ℹ️  Permissions créées et assignées aux rôles Admin / Super Admin. "
                        f"Rechargez la session front (/api/auth/me) pour voir les menus."
                    )
            else:
                print(
                    f"ℹ️  Migrations/seeds non lancés (apply_migrations=False). "
                    f"Lancez migrate puis 'python manage.py seed_{model_def.model_name.lower()}'."
                )

            # Générer les tests en dernière étape (non bloquant)
            if not self.generate_tests(model_def, output_dir):
                print(f"⚠️  Tests non générés pour {model_def.model_name}, mais l'API est fonctionnelle.")

            print(f"✅ API générée avec succès pour {model_def.model_name} !")
            return True

        except Exception as e:
            print(f"❌ Erreur lors de la génération: {e}")
            rollback_shared()
            return False

    def replay_relations(
        self,
        relations: List[Dict[str, Any]],
        model_name: str,
        default_app_label: str = DEFAULT_APP_NAME,
    ) -> bool:
        """Réapplique les relations enregistrées qui impliquent model_name (idempotent)."""
        for rel in relations:
            if model_name not in (rel["source"], rel["target"]):
                continue
            print(f"🔗 Rejeu de la relation {rel['source']}.{rel['field']} -> {rel['target']} ({rel['type']})")
            ok = self.link_models(
                source_model=rel["source"],
                target_model=rel["target"],
                relation_type=rel["type"],
                field_name=rel["field"],
                related_name=rel.get("related_name"),
                on_delete=rel.get("on_delete", "models.RESTRICT"),
                nullable=rel.get("nullable", True),
                app_label=rel.get("app_label", default_app_label),
                target_app_label=rel.get("target_app_label"),
                replay=True,
            )
            if not ok:
                print(f"❌ Impossible de rejouer la relation {rel['source']}.{rel['field']}")
                return False
        return True

    def _template_context(self, model_def: ModelDefinition) -> Dict[str, Any]:
        file_fields = model_def.get_file_fields()
        return {
            "model": model_def,
            "resource_plural": model_def.resource_plural,
            "resource_ident": model_def.resource_plural.replace("-", "_"),
            "has_file_fields": model_def.has_file_fields(),
            "file_field_names": list(file_fields.keys()),
            "file_fields": [
                {
                    "name": field.name,
                    "upload_folder": field.upload_folder,
                    "allowed_extensions": field.allowed_extensions,
                    "max_size_mb": field.max_size_mb,
                }
                for field in file_fields.values()
            ],
        }

    # ==========================
    #   APPLICATION CIBLE
    # ==========================
    def check_target_app_exists(self, app_name: str, app_dir: str) -> bool:
        """Vérifie que l'application cible existe : le générateur ne la crée jamais implicitement."""
        required = ['models.py', 'serializers.py', 'urls.py']
        if os.path.isdir(app_dir) and all(os.path.exists(os.path.join(app_dir, name)) for name in required):
            return True
        print(
            f"❌ L'application cible « {app_name} » (app_name du JSON) n'existe pas dans {self.app_root}. "
            f"Créez-la d'abord avec le menu « Créer une application » du générateur, "
            f"ou corrigez app_name dans le JSON (défaut : {DEFAULT_APP_NAME})."
        )
        return False

    @staticmethod
    def _models_db_tables(models_file: str) -> Dict[str, Optional[str]]:
        """Classes de models.py -> db_table explicite de leur Meta (None si absent)."""
        try:
            with open(models_file, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
        except (OSError, SyntaxError) as error:
            # Un models.py illisible n'est pas bloquant ici, mais le contrôle d'unicité ne peut pas l'inspecter
            print(f"⚠️  {models_file} ignoré pour le contrôle d'unicité ({error})")
            return {}
        tables: Dict[str, Optional[str]] = {}
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            table = None
            for inner in node.body:
                if isinstance(inner, ast.ClassDef) and inner.name == 'Meta':
                    for stmt in inner.body:
                        if (
                            isinstance(stmt, ast.Assign)
                            and any(isinstance(t, ast.Name) and t.id == 'db_table' for t in stmt.targets)
                            and isinstance(stmt.value, ast.Constant)
                        ):
                            table = stmt.value.value
            tables[node.name] = table
        return tables

    @staticmethod
    def _registered_routes(urls_file: str) -> List[str]:
        """Noms de routes enregistrées par router.register(...) dans un urls.py."""
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except OSError as error:
            print(f"⚠️  {urls_file} ignoré pour le contrôle d'unicité ({error})")
            return []
        return re.findall(r"router\.register\(\s*r?['\"]([^'\"]+)['\"]", content)

    def expected_db_table(self, model_def: ModelDefinition) -> str:
        """Table du modèle : meta.db_table du JSON, sinon <app>_<resource_plural>."""
        return model_def.meta.get('db_table') or (
            f"{model_def.app_name}_{model_def.resource_plural.replace('-', '_')}"
        )

    def check_no_conflict_with_other_apps(self, model_def: ModelDefinition) -> bool:
        """
        Refuse un modèle qui écraserait celui d'une autre application ou qui partagerait
        sa table ou sa route : db_table et resource_plural doivent être uniques dans tout le projet.
        """
        app_name = model_def.app_name
        table = self.expected_db_table(model_def)
        route = model_def.resource_plural
        problems: List[str] = []

        for entry in sorted(os.listdir(self.app_root)):
            other_dir = os.path.join(self.app_root, entry)
            models_file = os.path.join(other_dir, 'models.py')
            if not os.path.isfile(models_file):
                continue
            for class_name, other_table in self._models_db_tables(models_file).items():
                same_model = entry == app_name and class_name == model_def.model_name
                if same_model:
                    continue
                if entry != app_name and class_name == model_def.model_name:
                    problems.append(
                        f"le modèle {class_name} existe déjà dans l'application « {entry} » "
                        f"(un nom de modèle doit être unique dans le projet)"
                    )
                if other_table == table:
                    problems.append(f"la table « {table} » est déjà utilisée par {entry}.{class_name}")
            other_urls = os.path.join(other_dir, 'urls.py')
            if entry != app_name and os.path.isfile(other_urls) and route in self._registered_routes(other_urls):
                problems.append(
                    f"la route « {route} » est déjà enregistrée par l'application « {entry} » "
                    f"(définissez meta.resource_plural dans le JSON)"
                )

        if problems:
            print(f"❌ Génération de {model_def.model_name} refusée (application « {app_name} ») :")
            for problem in problems:
                print(f"   - {problem}")
            print("   Corrigez le JSON du modèle (meta.db_table, meta.resource_plural ou model_name).")
            return False
        return True

    @staticmethod
    def _is_generator_managed_urls(content: str) -> bool:
        """True si le urls.py ne contient que le format du générateur (aucun path() hors du préfixe v1/)."""
        paths = re.findall(r"\bpath\(\s*['\"]([^'\"]*)['\"]", content)
        return all(path == 'v1/' for path in paths)

    def _insert_route_in_custom_urls(self, model_def: ModelDefinition, urls_file: str, content: str) -> bool:
        """Ajoute l'import du ViewSet et son router.register(...) dans un urls.py écrit à la main (idempotent)."""
        app_name = model_def.app_name
        model_name = model_def.model_name
        viewset_class = f"{model_name}ViewSet"
        route_name = model_def.resource_plural
        module_import = f"from app.{app_name}.views.{model_name.lower()}_viewset import {viewset_class}"
        register_line = f"router.register(r'{route_name}', {viewset_class}, basename='{route_name}')"

        try:
            tree = ast.parse(content)
        except SyntaxError as error:
            print(f"❌ {urls_file} n'est pas analysable ({error}) : route non ajoutée.")
            return False

        last_import_end = None
        last_view_import_end = None
        router_assign_end = None
        last_register_end = None
        registered: List[tuple] = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                last_import_end = node.end_lineno
                if isinstance(node, ast.ImportFrom) and (node.module or '').startswith(f'app.{app_name}.views.'):
                    last_view_import_end = node.end_lineno
            elif (
                isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == 'router' for target in node.targets)
            ):
                router_assign_end = node.end_lineno
            elif (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == 'register'
                and isinstance(node.value.func.value, ast.Name)
                and node.value.func.value.id == 'router'
            ):
                args = node.value.args
                route = args[0].value if args and isinstance(args[0], ast.Constant) else None
                viewset = args[1].id if len(args) > 1 and isinstance(args[1], ast.Name) else None
                registered.append((route, viewset))
                last_register_end = node.end_lineno

        if router_assign_end is None:
            print(f"❌ Aucun « router = DefaultRouter(...) » dans {urls_file} : route non ajoutée.")
            return False
        for route, viewset in registered:
            if route == route_name and viewset != viewset_class:
                print(
                    f"❌ La route « {route_name} » est déjà enregistrée par {viewset} dans app/{app_name}/urls.py : "
                    f"définissez meta.resource_plural dans le JSON de {model_name}."
                )
                return False

        lines = content.split('\n')
        # Insertion de bas en haut : les numéros de ligne des points d'insertion restent valides
        if (route_name, viewset_class) not in registered:
            lines.insert(last_register_end or router_assign_end, register_line)
        if module_import not in content:
            lines.insert(last_view_import_end or last_import_end or 0, module_import)

        with open(urls_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"✅ URLs mises à jour pour {model_name} -> /api/v1/{route_name} (urls.py existant conservé)")
        return True

    def update_app_urls(self, model_def: ModelDefinition, app_dir: str) -> bool:
        """Réécrit app/<app_name>/urls.py dans un format canonique à chaque génération."""
        try:
            app_name = model_def.app_name
            urls_file = os.path.join(app_dir, 'urls.py')
            if not os.path.exists(urls_file):
                print(f"❌ Fichier d'URLs introuvable: {urls_file}")
                return False

            with open(urls_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # urls.py qui contient autre chose que les routes générées (core : authentification, santé,
            # profil...) : on y insère l'import et la route sans réécrire le reste du fichier
            if not self._is_generator_managed_urls(content):
                return self._insert_route_in_custom_urls(model_def, urls_file, content)

            viewset_import_re = re.compile(
                rf'^from app\.{re.escape(app_name)}\.views\.(\w+)_viewset import (\w+ViewSet)\s*$'
            )
            register_re = re.compile(r'^\s*router\.register\(')
            register_route_re = re.compile(r"router\.register\(\s*r?['\"]([^'\"]+)['\"],\s*(\w+)")

            viewset_imports: List[str] = []
            registers: List[str] = []
            seen_imports: set = set()
            seen_registers: set = set()

            for line in content.splitlines():
                stripped = line.strip()
                import_match = viewset_import_re.match(stripped)
                if import_match:
                    import_line = stripped
                    if import_line not in seen_imports:
                        seen_imports.add(import_line)
                        viewset_imports.append(import_line)
                elif register_re.match(line):
                    register_line = stripped
                    if register_line not in seen_registers:
                        seen_registers.add(register_line)
                        registers.append(register_line)

            model_name = model_def.model_name
            viewset_class = f"{model_name}ViewSet"
            module_import = (
                f"from app.{app_name}.views.{model_name.lower()}_viewset import {viewset_class}"
            )
            route_name = model_def.resource_plural
            register_line = (
                f"router.register(r'{route_name}', {viewset_class}, basename='{route_name}')"
            )

            # Une route déjà prise par un autre ViewSet serait écrasée en silence : on refuse
            for existing in registers:
                route_match = register_route_re.search(existing)
                if route_match and route_match.group(1) == route_name and route_match.group(2) != viewset_class:
                    print(
                        f"❌ La route « {route_name} » est déjà enregistrée par {route_match.group(2)} "
                        f"dans app/{app_name}/urls.py : définissez meta.resource_plural dans le JSON de {model_name}."
                    )
                    return False

            if module_import not in seen_imports:
                viewset_imports.append(module_import)
            if register_line not in seen_registers:
                registers.append(register_line)

            new_lines = [
                'from django.urls import include, path',
                'from rest_framework.routers import DefaultRouter',
                '',
            ]
            new_lines.extend(viewset_imports)
            new_lines.extend([
                '',
                'router = DefaultRouter(trailing_slash=False)',
            ])
            new_lines.extend(registers)
            new_lines.extend([
                '',
                'urlpatterns = [',
                "    path('v1/', include(router.urls)),",
                ']',
                '',
                f"app_name = '{app_name}'",
                '',
            ])

            new_content = '\n'.join(new_lines)
            with open(urls_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ URLs mises à jour pour {model_name} -> /api/v1/{route_name}")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour des URLs: {e}")
            return False
    
    def create_directories(self, app_dir: str, output_dir: str):
        """Crée les répertoires nécessaires."""
        directories = [
            os.path.join(app_dir, 'interfaces'),
            os.path.join(app_dir, 'repositories'),
            os.path.join(app_dir, 'services'),
            os.path.join(app_dir, 'views'),
            os.path.join(app_dir, 'permissions'),
            os.path.join(output_dir, 'tests')
        ]
        
        for dir_path in directories:
            os.makedirs(dir_path, exist_ok=True)
            init_file = os.path.join(dir_path, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write('')
    
    def generate_individual_files(self, model_def: ModelDefinition, app_dir: str, output_dir: str) -> bool:
        """Génère les fichiers individuels (non partagés) SANS les tests."""
        try:
            # Créer le répertoire management/commands s'il n'existe pas
            management_dir = os.path.join(app_dir, 'management')
            commands_dir = os.path.join(management_dir, 'commands')
            os.makedirs(commands_dir, exist_ok=True)
            
            # Créer les fichiers __init__.py
            for init_dir in [management_dir, commands_dir]:
                init_file = os.path.join(init_dir, '__init__.py')
                if not os.path.exists(init_file):
                    with open(init_file, 'w') as f:
                        f.write('')
            
            # Fichiers critiques à générer AVANT les migrations (SANS les tests)
            files_to_generate = [
                ('interface.py.j2', os.path.join(app_dir, 'interfaces', f'{model_def.model_name.lower()}_repository_interface.py')),
                ('repository.py.j2', os.path.join(app_dir, 'repositories', f'{model_def.model_name.lower()}_repository.py')),
                ('service.py.j2', os.path.join(app_dir, 'services', f'{model_def.model_name.lower()}_service.py')),
                ('viewset.py.j2', os.path.join(app_dir, 'views', f'{model_def.model_name.lower()}_viewset.py')),
                ('permissions.py.j2', os.path.join(app_dir, 'permissions', f'{model_def.model_name.lower()}_permissions.py')),
                ('seeds.py.j2', os.path.join(commands_dir, f'seed_{model_def.model_name.lower()}.py')),
            ]
            
            for template_name, file_path in files_to_generate:
                # Créer un backup si le fichier existe
                backup_path = self.create_backup(file_path)
                
                try:
                    template = self.env.get_template(template_name)
                    content = template.render(**self._template_context(model_def))
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    # Valider la syntaxe
                    if not self.validate_python_syntax(file_path):
                        if backup_path:
                            shutil.copy2(backup_path, file_path)
                        return False
                    
                    print(f"✅ {os.path.basename(file_path)} généré")
                    
                except Exception as e:
                    print(f"❌ Erreur lors de la génération de {file_path}: {e}")
                    if backup_path:
                        shutil.copy2(backup_path, file_path)
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération des fichiers individuels: {e}")
            return False
    
    def generate_tests(self, model_def: ModelDefinition, output_dir: str) -> bool:
        """Génère les fichiers de tests séparément (dernière étape)."""
        try:
            print(f"🧪 Génération des tests pour {model_def.model_name}...")
            
            # S'assurer que le répertoire tests existe
            tests_dir = os.path.join(output_dir, 'tests')
            os.makedirs(tests_dir, exist_ok=True)
            
            # Créer __init__.py si nécessaire
            init_file = os.path.join(tests_dir, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write('')
            
            # Générer le fichier de test
            test_file_path = os.path.join(tests_dir, f'test_{model_def.model_name.lower()}.py')
            backup_path = self.create_backup(test_file_path)
            
            try:
                template = self.env.get_template('tests.py.j2')
                content = template.render(**self._template_context(model_def))
                
                with open(test_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Valider la syntaxe (non bloquant)
                if not self.validate_python_syntax(test_file_path):
                    print(f"⚠️  Erreur de syntaxe dans {test_file_path}, mais cela ne bloque pas le processus")
                    if backup_path:
                        shutil.copy2(backup_path, test_file_path)
                    return False
                
                print(f"✅ {os.path.basename(test_file_path)} généré avec succès")
                return True
                
            except Exception as e:
                print(f"⚠️  Erreur lors de la génération de {test_file_path}: {e}")
                if backup_path:
                    shutil.copy2(backup_path, test_file_path)
                return False
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la génération des tests: {e}")
            return False
    
    def post_generation_validation(self, model_def: ModelDefinition, app_dir: str) -> bool:
        """Validation post-génération."""
        try:
            print("🔍 Validation post-génération...")
            
            # Valider les fichiers critiques (SANS le fichier de test pour éviter de bloquer les migrations)
            critical_files = [
                os.path.join(app_dir, 'models.py'),
                os.path.join(app_dir, 'serializers.py'),
                os.path.join(app_dir, 'views', f'{model_def.model_name.lower()}_viewset.py')
            ]
            
            for file_path in critical_files:
                if not os.path.exists(file_path):
                    print(f"❌ Fichier manquant: {file_path}")
                    return False
                
                if not self.validate_python_syntax(file_path):
                    return False

            # Vérifier l'enregistrement du ViewSet dans les URLs
            urls_file = os.path.join(app_dir, 'urls.py')
            if os.path.exists(urls_file):
                with open(urls_file, 'r', encoding='utf-8') as f:
                    urls_content = f.read()
                route_name = model_def.resource_plural
                expected = (
                    f"router.register(r'{route_name}', {model_def.model_name}ViewSet, basename='{route_name}')"
                )
                if expected not in urls_content:
                    print("❌ ViewSet non enregistré dans les URLs. Mise à jour requise.")
                    return False
            
            print("✅ Validation post-génération réussie")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la validation post-génération: {e}")
            return False