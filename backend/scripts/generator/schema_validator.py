"""
Validateur de schéma pour les modèles JSON.
"""
import json
import re
from typing import Dict, Any, List
from dataclasses import dataclass

from .field_utils import (
    normalize_choices,
    MAX_UPLOAD_SIZE_MB,
    normalize_allowed_extensions,
    validate_choices_field,
    validate_upload_folder,
)
from .naming_utils import get_resource_plural, pluralize, validate_resource_plural, to_snake_case

_MODEL_NAME_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_]*$')

# Application Django cible par défaut quand le JSON ne déclare pas « app_name »
DEFAULT_APP_NAME = 'metier'

# Le nom d'application sert à construire des chemins (app/<nom>/) et des imports : snake_case strict
_APP_NAME_RE = re.compile(r'^[a-z][a-z0-9_]*$')

_UPLOAD_FOLDER_RE = re.compile(r'^[a-z][a-z0-9_-]*(/[a-z][a-z0-9_-]*)*$')

_FIELD_NAME_RE = re.compile(r'^[a-z][a-z0-9_]*$')

# Types supportés : type JSON -> champ Django généré.
# Les relations (ForeignKey, OneToOneField, ManyToManyField) passent par link_models.
SUPPORTED_FIELD_TYPES = {
    'AutoField': 'AutoField',
    'CharField': 'CharField',
    'TextField': 'TextField',
    'SlugField': 'SlugField',
    'EmailField': 'EmailField',
    'URLField': 'URLField',
    'UUIDField': 'UUIDField',
    'IntegerField': 'IntegerField',
    'BigIntegerField': 'BigIntegerField',
    'SmallIntegerField': 'SmallIntegerField',
    'PositiveIntegerField': 'PositiveIntegerField',
    'PositiveSmallIntegerField': 'PositiveSmallIntegerField',
    'FloatField': 'FloatField',
    'DecimalField': 'DecimalField',
    'BooleanField': 'BooleanField',
    'DateField': 'DateField',
    'TimeField': 'TimeField',
    'DateTimeField': 'DateTimeField',
    'DurationField': 'DurationField',
    'JSONField': 'JSONField',
    'FileField': 'CharField',
}

_RELATION_TYPES = {'ForeignKey', 'OneToOneField', 'ManyToManyField'}

_PYTHON_KEYWORDS = frozenset({
    'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class',
    'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global',
    'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise',
    'return', 'try', 'while', 'with', 'yield',
})

def _pick(field_data: Dict[str, Any], options: Dict[str, Any], key: str) -> Any:
    """Valeur du champ, avec repli sur options ; conserve les valeurs falsy légitimes (0, '')."""
    value = field_data.get(key)
    return value if value is not None else options.get(key)


@dataclass
class FieldConstraint:
    name: str
    type: str
    constraints: List[str] = None
    verbose_name: str = None
    help_text: str = None
    max_length: int = None
    blank: bool = None
    null: bool = None
    default: Any = None
    choices: List = None
    max_digits: int = None
    decimal_places: int = None
    auto_now: bool = None
    auto_now_add: bool = None
    editable: bool = None
    unique: bool = None
    to: str = None
    on_delete: str = None
    related_name: str = None
    widget: str = None
    visible_in_table: bool = None
    visible_in_dialog: bool = None
    upload_folder: str = None
    allowed_extensions: List[str] = None
    max_size_mb: int = None

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []
        if self.allowed_extensions is None:
            self.allowed_extensions = []

    @property
    def is_file_field(self) -> bool:
        return self.type == 'FileField'

@dataclass
class ModelDefinition:
    model_name: str
    app_name: str
    fields: Dict[str, FieldConstraint]
    meta: Dict[str, Any] = None
    permissions: List[str] = None

    def __post_init__(self):
        if self.meta is None:
            self.meta = {}
        if self.permissions is None:
            self.permissions = []

    @property
    def resource_plural(self) -> str:
        return get_resource_plural(self.model_name, self.meta)

    @property
    def snake_name(self) -> str:
        """Nom du modèle en snake_case (OrderItem -> order_item), pour les variables générées."""
        return to_snake_case(self.model_name)

    def get_django_field_type(self, field_name: str) -> str:
        """Convertit le type Django en type Django."""
        field = self.fields[field_name]
        django_type = field.type

        if django_type not in SUPPORTED_FIELD_TYPES:
            raise ValueError(f"Type non supporté pour le champ {field_name}: {django_type}")
        return SUPPORTED_FIELD_TYPES[django_type]

    def get_file_fields(self) -> Dict[str, 'FieldConstraint']:
        return {name: field for name, field in self.fields.items() if field.is_file_field}

    def has_file_fields(self) -> bool:
        return bool(self.get_file_fields())

    def get_field_params(self, field_name: str) -> Dict[str, Any]:
        """Extrait les paramètres Django pour un champ."""
        field = self.fields[field_name]
        params = {}

        # Utiliser les paramètres du champ directement
        if field.verbose_name is not None:
            params['verbose_name'] = field.verbose_name
        if field.help_text is not None:
            params['help_text'] = field.help_text
        if field.max_length is not None:
            params['max_length'] = field.max_length
        elif field.is_file_field:
            params['max_length'] = 512
        if field.blank is not None:
            params['blank'] = field.blank
        if field.null is not None:
            params['null'] = field.null
        if field.default is not None:
            params['default'] = field.default
        if field.choices:
            params['choices'] = field.choices
        if field.max_digits is not None:
            params['max_digits'] = field.max_digits
        if field.decimal_places is not None:
            params['decimal_places'] = field.decimal_places
        if field.auto_now is not None:
            params['auto_now'] = field.auto_now
        if field.auto_now_add is not None:
            params['auto_now_add'] = field.auto_now_add
        if field.editable is not None:
            params['editable'] = field.editable
        if field.unique is not None:
            params['unique'] = field.unique
        if field.to:
            params['to'] = field.to
        if field.on_delete:
            params['on_delete'] = field.on_delete
        if field.related_name:
            params['related_name'] = field.related_name

        # Gestion des champs spéciaux (setdefault préserve les valeurs explicites du JSON)
        if field_name == 'created_at':
            params.setdefault('auto_now_add', True)
            params.setdefault('auto_now', False)
        elif field_name == 'updated_at':
            params.setdefault('auto_now_add', False)
            params.setdefault('auto_now', True)

        return params

class SchemaValidator:
    """Valide et parse le JSON de définition du modèle."""

    @staticmethod
    def _normalize_meta(meta: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        normalized = dict(meta or {})
        if not normalized.get("resource_plural"):
            raise ValueError(
                f"meta.resource_plural est obligatoire pour le modèle {model_name}. "
                'Définissez explicitement le pluriel API (ex: "elitests", "cities", "analyses").'
            )
        normalized["resource_plural"] = validate_resource_plural(normalized["resource_plural"])
        return normalized

    @staticmethod
    def validate_field(field_name: str, field_data: Dict[str, Any]) -> FieldConstraint:
        """Valide et crée une définition de champ."""
        if 'type' not in field_data:
            raise ValueError(f"Type manquant pour le champ {field_name}")
        if not _FIELD_NAME_RE.match(field_name) or field_name in _PYTHON_KEYWORDS:
            raise ValueError(
                f"Nom de champ invalide : '{field_name}'. "
                "Utilisez du snake_case (lettres minuscules, chiffres, underscores) et pas de mot réservé Python."
            )
        if field_data['type'] in _RELATION_TYPES:
            raise ValueError(
                f"Le champ {field_name} est une relation ({field_data['type']}) : "
                "créez-la avec 'generate_api.py --link' (option 8 du menu) après avoir généré les deux modèles."
            )
        if field_data['type'] not in SUPPORTED_FIELD_TYPES:
            raise ValueError(
                f"Type non supporté pour le champ {field_name}: {field_data['type']}. "
                f"Types disponibles : {', '.join(sorted(SUPPORTED_FIELD_TYPES))}"
            )

        # Extraire les options si elles existent
        options = field_data.get('options', {})
        field_type = field_data['type']
        raw_choices = field_data.get('choices') if field_data.get('choices') is not None else options.get('choices')
        choices = normalize_choices(raw_choices) if raw_choices is not None else None
        if choices is not None:
            validate_choices_field(field_name, field_type, choices)

        raw_upload_folder = field_data.get('upload_folder') or options.get('upload_folder')
        raw_allowed_extensions = field_data.get('allowed_extensions') or options.get('allowed_extensions')
        raw_max_size_mb = field_data.get('max_size_mb') if field_data.get('max_size_mb') is not None else options.get('max_size_mb')

        if field_type == 'CharField' and _pick(field_data, options, 'max_length') is None:
            raise ValueError(f"max_length est obligatoire pour le champ CharField {field_name}")
        if field_type == 'DecimalField' and (
            _pick(field_data, options, 'max_digits') is None
            or _pick(field_data, options, 'decimal_places') is None
        ):
            raise ValueError(f"max_digits et decimal_places sont obligatoires pour le champ DecimalField {field_name}")

        if field_type == 'FileField' and raw_max_size_mb is not None and raw_max_size_mb <= 0:
            raise ValueError(f"max_size_mb invalide pour le champ {field_name}")

        return FieldConstraint(
            name=field_name,
            type=field_type,
            verbose_name=_pick(field_data, options, 'verbose_name'),
            help_text=_pick(field_data, options, 'help_text'),
            max_length=_pick(field_data, options, 'max_length'),
            blank=field_data.get('blank') if field_data.get('blank') is not None else options.get('blank'),
            null=field_data.get('null') if field_data.get('null') is not None else options.get('null'),
            default=field_data.get('default') if field_data.get('default') is not None else options.get('default'),
            choices=choices,
            constraints=field_data.get('constraints', []),
            max_digits=_pick(field_data, options, 'max_digits'),
            decimal_places=_pick(field_data, options, 'decimal_places'),
            auto_now=field_data.get('auto_now') if field_data.get('auto_now') is not None else options.get('auto_now'),
            auto_now_add=field_data.get('auto_now_add') if field_data.get('auto_now_add') is not None else options.get('auto_now_add'),
            editable=field_data.get('editable') if field_data.get('editable') is not None else options.get('editable'),
            unique=field_data.get('unique') if field_data.get('unique') is not None else options.get('unique'),
            to=field_data.get('to') or options.get('to'),
            on_delete=field_data.get('on_delete') or options.get('on_delete'),
            related_name=field_data.get('related_name') or options.get('related_name'),
            widget=field_data.get('widget') or options.get('widget'),
            visible_in_table=(
                field_data['visible_in_table']
                if field_data.get('visible_in_table') is not None
                else options.get('visible_in_table')
            ),
            visible_in_dialog=(
                field_data['visible_in_dialog']
                if field_data.get('visible_in_dialog') is not None
                else options.get('visible_in_dialog')
            ),
            upload_folder=raw_upload_folder,
            allowed_extensions=normalize_allowed_extensions(raw_allowed_extensions) if raw_allowed_extensions else None,
            max_size_mb=raw_max_size_mb,
        )

    @staticmethod
    def _finalize_file_fields(fields: Dict[str, FieldConstraint], resource_plural: str) -> None:
        for field_name, field in fields.items():
            if not field.is_file_field:
                continue
            if not field.upload_folder:
                field.upload_folder = f"{resource_plural}/{field_name}"
            else:
                field.upload_folder = validate_upload_folder(field.upload_folder)
            if not field.allowed_extensions:
                raise ValueError(
                    f"allowed_extensions est obligatoire pour le champ FileField {field_name} "
                    "(ex. [\".pdf\", \".png\"]) : sans liste, aucun contrôle du type de fichier"
                )
            if field.max_size_mb is None:
                field.max_size_mb = 10
            if field.max_size_mb > MAX_UPLOAD_SIZE_MB:
                raise ValueError(
                    f"max_size_mb de {field_name} dépasse le plafond de {MAX_UPLOAD_SIZE_MB} Mo (UPLOAD_MAX_SIZE_MB)"
                )

    @staticmethod
    def resolve_app_name(model_data: Dict[str, Any]) -> str:
        """Application Django cible du modèle : « app_name » du JSON, sinon « metier »."""
        app_name = model_data.get('app_name')
        if app_name is None:
            return DEFAULT_APP_NAME
        if not isinstance(app_name, str) or not _APP_NAME_RE.match(app_name):
            raise ValueError(
                f"app_name invalide : {app_name!r}. "
                "Doit être en snake_case (lettres minuscules, chiffres, underscores, commençant par une lettre)."
            )
        return app_name

    @staticmethod
    def validate_model(model_data: Dict[str, Any]) -> ModelDefinition:
        """Valide et crée une définition de modèle."""
        # Valider le nom du modèle
        raw_name = model_data.get('model_name') or model_data.get('model', '')
        if not _MODEL_NAME_RE.match(raw_name):
            raise ValueError(
                f"Nom de modèle invalide : '{raw_name}'. "
                "Doit commencer par une lettre et ne contenir que des lettres, chiffres et underscores."
            )

        # Support des deux formats : ancien et nouveau
        system_fields = {"created_by", "updated_by", "created_at", "updated_at"}
        if 'model' in model_data:
            # Ancien format
            if 'attributes' not in model_data:
                raise ValueError("Attributs manquants")

            # Valider les champs
            fields = {}
            for field_name, field_data in model_data['attributes'].items():
                # Ignorer les champs système: ils seront ajoutés automatiquement par les templates
                if field_name in system_fields:
                    continue
                fields[field_name] = SchemaValidator.validate_field(field_name, field_data)

            model_name = model_data['model']
            meta = SchemaValidator._normalize_meta(model_data.get('meta', {}), model_name)
            SchemaValidator._finalize_file_fields(fields, get_resource_plural(model_name, meta))

            return ModelDefinition(
                model_name=model_name,
                app_name=SchemaValidator.resolve_app_name(model_data),
                fields=fields,
                meta=meta,
                permissions=model_data.get('permissions', [])
            )
        elif 'model_name' in model_data:
            # Nouveau format
            if 'fields' not in model_data:
                raise ValueError("Champs manquants")

            # Valider les champs
            fields = {}
            for field_data in model_data['fields']:
                field_name = field_data['name']
                # Ignorer les champs système: ils seront ajoutés automatiquement par les templates
                if field_name in system_fields:
                    continue
                fields[field_name] = SchemaValidator.validate_field(field_name, field_data)

            model_name = model_data['model_name']
            meta = SchemaValidator._normalize_meta(model_data.get('meta', {}), model_name)
            SchemaValidator._finalize_file_fields(fields, get_resource_plural(model_name, meta))

            return ModelDefinition(
                model_name=model_name,
                app_name=SchemaValidator.resolve_app_name(model_data),
                fields=fields,
                meta=meta,
                permissions=model_data.get('permissions', [])
            )
        else:
            raise ValueError("Nom du modèle manquant (model ou model_name)")

    @staticmethod
    def load_from_json(json_file_path: str) -> ModelDefinition:
        """Charge et valide un fichier JSON."""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return SchemaValidator.validate_model(data)