"""
Generateur d'interface CRUD frontend (React/TypeScript) base sur les modeles JSON.
"""
import os
import re
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List

from .field_utils import choices_labels_json, choices_to_frontend_options
from .schema_validator import ModelDefinition, SchemaValidator
from .naming_utils import pluralize, to_kebab_case


SYSTEM_FIELDS = {"id", "uuid", "created_at", "updated_at", "created_by", "updated_by"}


class FrontendCodeGenerator:
    """Genere les fichiers frontend CRUD en suivant le pattern models/user."""

    def __init__(self, template_dir: str = None):
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), "templates", "frontend")

        # Jinja2 est un outil de développement : l'absence est signalée ici, explicitement
        try:
            from jinja2 import Environment, FileSystemLoader  # type: ignore
        except ModuleNotFoundError as error:
            raise RuntimeError(
                "Jinja2 n'est pas installe. Activez le venv backend puis installez les dependances."
            ) from error

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.backend_dir = Path(__file__).resolve().parent.parent.parent
        self.frontend_dir = self.backend_dir.parent / "frontend"
        self.frontend_src_dir = self.frontend_dir / "src"
        self._eols: Dict[Path, str] = {}
        self._loaded: Dict[Path, str] = {}

    @staticmethod
    def _to_pascal_case(name: str) -> str:
        parts = re.split(r"[_\-\s]+", name)
        return "".join(part[:1].upper() + part[1:] for part in parts if part)

    @staticmethod
    def _to_camel_case(name: str) -> str:
        pascal = FrontendCodeGenerator._to_pascal_case(name)
        if not pascal:
            return name
        return pascal[0].lower() + pascal[1:]

    @staticmethod
    def _to_sentence_label(name: str) -> str:
        return name.replace("_", " ").strip().capitalize()

    @staticmethod
    def _default_visible_in_table(field_name: str, django_type: str) -> bool:
        if field_name == "id":
            return False
        if django_type in {"UUIDField", "AutoField"}:
            return False
        return True

    @staticmethod
    def _default_visible_in_dialog(field_name: str, django_type: str) -> bool:
        if field_name == "id":
            return False
        if django_type in {"UUIDField", "AutoField"}:
            return False
        return True

    @staticmethod
    def _zod_required_string() -> str:
        return 'z.string(t("validation.required")).min(1, t("validation.required"))'

    @staticmethod
    def _zod_optional_nullable_string() -> str:
        return "z.string().nullable().optional()"

    @staticmethod
    def _zod_required_number() -> str:
        return """z.preprocess(
      (val) =>
        val === undefined || val === null || val === ""
          ? undefined
          : Number(val),
      z
        .union([z.number(), z.undefined()])
        .refine(
          (val): val is number => typeof val === "number" && !Number.isNaN(val),
          { message: t("validation.number.required") },
        ),
    )"""

    @staticmethod
    def _zod_optional_number() -> str:
        return """z.preprocess(
      (val) =>
        val === undefined || val === null || val === ""
          ? undefined
          : Number(val),
      z
        .number({ message: t("validation.number.required") })
        .optional(),
    )"""

    @staticmethod
    def _zod_choices_expr(choices: list, django_type: str, is_optional: bool, is_nullable: bool) -> str:
        values = [choice[0] for choice in choices]
        if django_type in {"IntegerField", "BigIntegerField", "PositiveIntegerField"}:
            literals = ", ".join(f"z.literal({value})" for value in values)
            base = f"z.union([{literals}])"
        else:
            quoted = ", ".join(json.dumps(str(value)) for value in values)
            base = f"z.enum([{quoted}])"

        if is_nullable:
            base = f"{base}.nullable()"
        if is_optional:
            base = f"{base}.optional()"
        return base

    def _map_field(self, field_name: str, field: Any) -> Dict[str, Any]:
        django_type = field.type
        is_nullable = bool(field.null)
        is_optional = bool(field.blank) or is_nullable
        is_required = not is_optional
        field_choices = field.choices or []
        has_choices = bool(field_choices)
        zod_base = "z.string()"
        ts_type = "string"
        default_value = "''"
        input_type = "text"
        input_kind = "input"
        is_select = False
        is_file = getattr(field, "is_file_field", False)
        upload_folder = ""
        allowed_extensions: List[str] = []
        max_size_mb = 10
        accept_attr = ""

        if has_choices:
            is_select = True
            input_kind = "select"
            first_value = field_choices[0][0]
            if django_type in {"IntegerField", "BigIntegerField", "PositiveIntegerField", "DecimalField", "FloatField"}:
                zod_base = "z.coerce.number()"
                ts_type = "number"
                default_value = str(first_value)
            else:
                zod_base = "z.string()"
                ts_type = "string"
                default_value = json.dumps(str(first_value))
        elif is_file:
            is_file = True
            input_kind = "file"
            zod_base = "z.string()"
            ts_type = "string"
            default_value = "undefined"
            upload_folder = getattr(field, "upload_folder", "") or ""
            allowed_extensions = list(getattr(field, "allowed_extensions", None) or [])
            max_size_mb = int(getattr(field, "max_size_mb", None) or 10)
            accept_attr = ",".join(allowed_extensions) if allowed_extensions else ""
        elif django_type in {"IntegerField", "BigIntegerField", "PositiveIntegerField", "DecimalField", "FloatField"}:
            zod_base = "z.coerce.number()"
            ts_type = "number"
            default_value = "undefined"
            input_type = "number"
        elif django_type == "BooleanField":
            zod_base = "z.boolean()"
            ts_type = "boolean"
            default_value = "false"
            input_kind = "checkbox"
        elif django_type in {"DateField", "DateTimeField", "TimeField"}:
            zod_base = "z.string()"
            ts_type = "string"
            default_value = "''"
            input_type = "date" if django_type in {"DateField", "DateTimeField"} else "time"
        elif django_type == "TextField":
            zod_base = "z.string()"
            ts_type = "string"
            default_value = "''"
            input_type = "text"
            input_kind = "textarea"
        elif django_type == "UUIDField":
            zod_base = "z.string().uuid()"
            ts_type = "string"
            default_value = "''"
            input_type = "text"
        elif django_type in {"AutoField"}:
            zod_base = "z.number()"
            ts_type = "number"
            default_value = "0"
            input_type = "number"

        zod_type = zod_base
        ts_field_type = ts_type
        if not has_choices:
            if is_nullable:
                zod_type = f"{zod_type}.nullable()"
                ts_field_type = f"{ts_field_type} | null"
            if is_optional:
                zod_type = f"{zod_type}.optional()"
                ts_field_type = f"{ts_field_type} | undefined"
        else:
            if is_nullable:
                ts_field_type = f"{ts_field_type} | null"
            if is_optional:
                ts_field_type = f"{ts_field_type} | undefined"

        field_widget = getattr(field, "widget", None)
        is_textarea = (
            not has_choices
            and (django_type == "TextField" or field_widget == "textarea")
        )
        if is_textarea:
            input_kind = "textarea"

        output_ts_type = ts_field_type.replace(" | undefined", "")
        if is_nullable and " | null" not in output_ts_type:
            output_ts_type = f"{output_ts_type} | null"

        if has_choices:
            zod_type = self._zod_choices_expr(
                field_choices, django_type, is_optional, is_nullable
            )
            zod_form_expr = zod_type
        elif is_file:
            zod_form_expr = "z.any().optional()"
        else:
            if django_type in {"IntegerField", "BigIntegerField", "DecimalField", "FloatField"}:
                zod_form_expr = (
                    self._zod_optional_number() if is_optional else self._zod_required_number()
                )
            elif is_nullable or (is_optional and django_type in {"CharField", "TextField"}):
                zod_form_expr = self._zod_optional_nullable_string()
            elif is_required and django_type in {"CharField", "TextField"}:
                zod_form_expr = self._zod_required_string()
            elif is_optional:
                zod_form_expr = "z.string().optional()"
            else:
                zod_form_expr = zod_type.replace(".optional()", "").replace(".nullable()", "")

        visible_in_table = (
            field.visible_in_table
            if field.visible_in_table is not None
            else self._default_visible_in_table(field_name, django_type)
        )
        visible_in_dialog = (
            field.visible_in_dialog
            if field.visible_in_dialog is not None
            else self._default_visible_in_dialog(field_name, django_type)
        )

        return {
            "name": field_name,
            "label": field.verbose_name or self._to_sentence_label(field_name),
            "django_type": django_type,
            "zod_type": zod_type,
            "zod_form_expr": zod_form_expr,
            "ts_type": ts_field_type,
            "form_ts_optional": is_optional or django_type in {
                "IntegerField",
                "BigIntegerField",
                "DecimalField",
                "FloatField",
            },
            "output_ts_type": output_ts_type,
            "default_value": default_value,
            "is_required": is_required,
            "is_optional": is_optional,
            "input_kind": input_kind,
            "input_type": input_type,
            "is_boolean": django_type == "BooleanField",
            "is_number": (
                django_type in {"IntegerField", "BigIntegerField", "DecimalField", "FloatField"}
                and not has_choices
            ),
            "is_date": django_type in {"DateField", "DateTimeField", "TimeField"},
            "is_select": is_select,
            "choices": choices_to_frontend_options(field_choices) if has_choices else [],
            "choices_labels_json": choices_labels_json(field_choices) if has_choices else "{}",
            "is_nullable": is_nullable,
            "is_textarea": is_textarea,
            "is_file": is_file,
            "upload_folder": upload_folder,
            "allowed_extensions": allowed_extensions,
            "accept_attr": accept_attr,
            "max_size_mb": max_size_mb,
            "visible_in_table": visible_in_table,
            "visible_in_dialog": visible_in_dialog,
        }

    def _build_context(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        model_def: ModelDefinition = SchemaValidator.validate_model(model_data)

        model_name = model_def.model_name
        # Dossiers / fichiers en kebab-case (OrderItem -> order-item) ; composants en PascalCase
        model_name_lower = to_kebab_case(model_name)
        model_name_plural = model_def.resource_plural
        model_name_pascal = self._to_pascal_case(model_name)
        model_name_plural_pascal = self._to_pascal_case(model_name_plural)
        model_name_camel = self._to_camel_case(model_name)
        model_name_plural_camel = self._to_camel_case(model_name_plural)
        permission_key = model_name_pascal.upper()
        permission_category = model_name_plural

        mapped_fields: List[Dict[str, Any]] = []
        for field_name, field in model_def.fields.items():
            mapped_fields.append(self._map_field(field_name, field))

        table_fields = [
            f for f in mapped_fields if f["visible_in_table"] and f["name"] != "id"
        ]
        dialog_fields = [
            f for f in mapped_fields if f["visible_in_dialog"] and f["name"] != "id"
        ]
        if not table_fields:
            table_fields = [f for f in mapped_fields if f["name"] != "id"]
        if not dialog_fields:
            dialog_fields = table_fields

        form_fields = [
            f
            for f in mapped_fields
            if f["visible_in_dialog"]
            and f["name"] not in SYSTEM_FIELDS
            and f["django_type"] not in {"UUIDField", "AutoField"}
        ]

        create_default_values_lines = []
        for f in form_fields:
            if f.get("is_file"):
                continue
            create_default_values_lines.append(f"      {f['name']}: {f['default_value']},")

        file_fields = [f for f in mapped_fields if f.get("is_file")]
        has_file_fields = bool(file_fields)
        scalar_form_fields = [f for f in form_fields if not f.get("is_file")]

        return {
            "model_name": model_name,
            "model_name_lower": model_name_lower,
            "model_name_kebab": model_name_lower,
            "model_name_camel": model_name_camel,
            "model_name_pascal": model_name_pascal,
            "model_name_plural": model_name_plural,
            "model_name_plural_pascal": model_name_plural_pascal,
            "model_name_plural_camel": model_name_plural_camel,
            "model_title": self._to_sentence_label(model_name_plural),
            "fields": mapped_fields,
            "table_fields": table_fields,
            "dialog_fields": dialog_fields,
            "form_fields": form_fields,
            "scalar_form_fields": scalar_form_fields,
            "file_fields": file_fields,
            "has_file_fields": has_file_fields,
            "file_fields_descriptor_json": json.dumps(
                [{"name": f["name"], "uploadFolder": f["upload_folder"]} for f in file_fields]
            ),
            "api_endpoint": f"/{model_name_plural}",
            "tag_name": model_name_plural_pascal,
            "permission_key": permission_key,
            "permission_category": permission_category,
            "permission_view_var": f"canView{model_name_plural_pascal}",
            "permission_create_var": f"canCreate{model_name_plural_pascal}",
            "permission_update_var": f"canUpdate{model_name_plural_pascal}",
            "permission_delete_var": f"canDelete{model_name_plural_pascal}",
            "create_default_values_lines": create_default_values_lines,
        }

    def _write_file_from_template(self, template_name: str, target_path: Path, context: Dict[str, Any]):
        target_path.parent.mkdir(parents=True, exist_ok=True)
        template = self.env.get_template(template_name)
        content = template.render(**context)
        target_path.write_text(content, encoding="utf-8")
        rel = target_path.relative_to(self.frontend_dir)
        print(f"  ✅ frontend/{rel.as_posix()} généré")

    # ------------------------------------------------------------------
    # Modification des fichiers frontend existants.
    # Chaque mise a jour leve RuntimeError si son repere est introuvable
    # (plus d'echec silencieux) ; l'appelant restaure alors tous les fichiers.
    # ------------------------------------------------------------------
    def _existing_files(self) -> Dict[str, Path]:
        src = self.frontend_src_dir
        return {
            "store": src / "redux" / "store.ts",
            "routes": src / "App.tsx",
            "permission_constants": src / "models" / "auth" / "permissions" / "constants.ts",
            "permissions_hook": src / "hooks" / "use-permissions.tsx",
            "sidebar_menu": src / "components" / "sidebar" / "components" / "menu-groups" / "general-menu.tsx",
        }

    def _load(self, path: Path) -> str:
        """Lit un fichier existant en normalisant les fins de ligne (CRLF conserve a l'ecriture)."""
        if not path.exists():
            raise RuntimeError(
                f"{path.name} introuvable ({path}) : impossible d'enregistrer le modèle dans le frontend."
            )
        raw = path.read_bytes().decode("utf-8")
        self._eols[path] = "\r\n" if "\r\n" in raw else "\n"
        content = raw.replace("\r\n", "\n")
        self._loaded[path] = content
        return content

    def _save(self, path: Path, content: str):
        eol = self._eols.get(path, "\n")
        path.write_bytes((content.replace("\n", eol) if eol != "\n" else content).encode("utf-8"))

    def _save_and_report(self, path: Path, content: str, label: str):
        """Écrit le fichier s'il a changé et l'indique : mis à jour, ou déjà à jour (relance idempotente)."""
        if content == self._loaded.get(path):
            print(f"  ℹ️  {label} déjà à jour")
            return
        self._save(path, content)
        print(f"  ✅ {label} mis à jour")

    @staticmethod
    def _missing_marker(file_label: str, marker: str) -> RuntimeError:
        return RuntimeError(
            f"Repère introuvable dans {file_label} : {marker!r}. "
            "Le fichier a été restructuré ; adaptez le générateur ou ajoutez le repère."
        )

    def _update_store(self, context: Dict[str, Any]):
        store_file = self._existing_files()["store"]
        content = self._load(store_file)
        camel = context["model_name_camel"]

        import_line = f'import {{ {camel}Api }} from "@/models/{context["model_name_lower"]}/api";'
        if import_line not in content:
            content = import_line + "\n" + content

        reducer_line = f"    [{camel}Api.reducerPath]: {camel}Api.reducer,"
        reducer_match = re.search(r"(reducer:\s*\{)([\s\S]*?)(\n\s*\},)", content)
        if not reducer_match:
            raise self._missing_marker("store.ts", "reducer: {")
        if reducer_line not in reducer_match.group(2):
            reducer_block = reducer_match.group(2).rstrip() + "\n" + reducer_line + "\n  "
            content = content[: reducer_match.start(2)] + reducer_block + content[reducer_match.end(2) :]

        middleware_line = f"      {camel}Api.middleware,"
        middleware_match = re.search(r"(concat\()([\s\S]*?)(\)\s*,\s*\n\s*\}\)\s*;)", content)
        if not middleware_match:
            raise self._missing_marker("store.ts", "getDefaultMiddleware().concat(")
        if middleware_line not in middleware_match.group(2):
            middleware_block = middleware_match.group(2).rstrip() + "\n" + middleware_line + "\n    "
            content = content[: middleware_match.start(2)] + middleware_block + content[middleware_match.end(2) :]

        self._save_and_report(store_file, content, "frontend/src/redux/store.ts")

    def _update_app_routes(self, context: Dict[str, Any]):
        app_file = self._existing_files()["routes"]
        content = self._load(app_file)

        page_component = f'{context["model_name_pascal"]}List'
        import_line = (
            f'import {page_component} from "./models/{context["model_name_lower"]}'
            f'/pages/{context["model_name_lower"]}-list";'
        )
        if import_line not in content:
            content = import_line + "\n" + content

        route_path = f'path="/{context["model_name_plural"]}"'
        if route_path not in content:
            route_line = f'          <Route element={{<{page_component} />}} {route_path} />'
            marker = '<Route element={<MyAccount />} path="/my-account" />'
            routes_marker = "</Route>\n      </Route>"
            if marker in content:
                content = content.replace(marker, route_line + "\n\n" + marker, 1)
            elif routes_marker in content:
                content = content.replace(routes_marker, route_line + "\n" + routes_marker, 1)
            else:
                raise self._missing_marker("App.tsx", marker)

        self._save_and_report(app_file, content, "frontend/src/App.tsx")

    def _update_permission_constants(self, context: Dict[str, Any]):
        constants_file = self._existing_files()["permission_constants"]
        content = self._load(constants_file)

        key = context["permission_key"]
        category = context["permission_category"]
        if not re.search(rf"^  {re.escape(key)}: \{{", content, re.MULTILINE):
            permission_block = (
                f"  {key}: {{\n"
                f'    category: "{category}",\n'
                f"    actions: {{\n"
                f'      VIEW: "{category}.view",\n'
                f'      CREATE: "{category}.create",\n'
                f'      DELETE: "{category}.delete",\n'
                f'      UPDATE: "{category}.update",\n'
                "    },\n"
                "  },\n"
            )
            if "} as const;" not in content:
                raise self._missing_marker("constants.ts", "} as const;")
            content = content.replace("} as const;", permission_block + "} as const;", 1)

        export_block = (
            f"\nexport const {key}_VIEW = PERMISSIONS.{key}.actions.VIEW;\n"
            f"export const {key}_CREATE = PERMISSIONS.{key}.actions.CREATE;\n"
            f"export const {key}_DELETE = PERMISSIONS.{key}.actions.DELETE;\n"
            f"export const {key}_UPDATE = PERMISSIONS.{key}.actions.UPDATE;\n"
        )
        if f"export const {key}_VIEW" not in content:
            content += export_block

        self._save_and_report(constants_file, content, "frontend/src/models/auth/permissions/constants.ts")

    def _update_permissions_hook(self, context: Dict[str, Any]):
        hook_file = self._existing_files()["permissions_hook"]
        content = self._load(hook_file)

        key = context["permission_key"]
        unauth_lines = [
            f'        {context["permission_view_var"]}: false,',
            f'        {context["permission_create_var"]}: false,',
            f'        {context["permission_update_var"]}: false,',
            f'        {context["permission_delete_var"]}: false,',
        ]
        auth_lines = [
            f'      {context["permission_view_var"]}: hasPermission(permissions, getPermission("{key}", "VIEW")),',
            f'      {context["permission_create_var"]}: hasPermission(permissions, getPermission("{key}", "CREATE")),',
            f'      {context["permission_update_var"]}: hasPermission(permissions, getPermission("{key}", "UPDATE")),',
            f'      {context["permission_delete_var"]}: hasPermission(permissions, getPermission("{key}", "DELETE")),',
        ]

        if unauth_lines[0] not in content:
            marker = "        canDeleteRoles: false,"
            if marker not in content:
                raise self._missing_marker("use-permissions.tsx", marker)
            content = content.replace(marker, marker + "\n\n" + "\n".join(unauth_lines), 1)

        if auth_lines[0] not in content:
            marker = '      canDeleteRoles: hasPermission(permissions, getPermission("ROLE", "DELETE")),'
            if marker not in content:
                raise self._missing_marker("use-permissions.tsx", marker)
            content = content.replace(marker, marker + "\n\n" + "\n".join(auth_lines), 1)

        self._save_and_report(hook_file, content, "frontend/src/hooks/use-permissions.tsx")

    def _update_sidebar_menu(self, context: Dict[str, Any]):
        menu_file = self._existing_files()["sidebar_menu"]
        content = self._load(menu_file)

        if 'from "@/hooks/use-permissions"' not in content:
            icons_import = 'import { Icons } from "@/lib/constants/icons";'
            if icons_import not in content:
                raise self._missing_marker("general-menu.tsx", icons_import)
            content = content.replace(
                icons_import,
                'import { usePermissions } from "@/hooks/use-permissions";\n' + icons_import,
                1,
            )

        permission_var = context["permission_view_var"]
        destructure_match = re.search(r"const \{ ([^}]+) \} = usePermissions\(\);", content)
        if not re.search(rf"\b{permission_var}\b", content):
            if destructure_match:
                vars_str = destructure_match.group(1).strip()
                new_destructure = f"const {{ {vars_str}, {permission_var} }} = usePermissions();"
                content = content.replace(destructure_match.group(0), new_destructure, 1)
            else:
                marker = "const { isMobile, setOpenMobile } = useSidebar();"
                if marker not in content:
                    raise self._missing_marker("general-menu.tsx", "const { ... } = usePermissions();")
                content = content.replace(
                    marker, f"{marker}\n  const {{ {permission_var} }} = usePermissions();", 1
                )

        item_url = context["model_name_plural"]
        item_block = (
            "        {\n"
            f'          title: "{context["model_title"]}",\n'
            f'          url: "{item_url}",\n'
            "          isActive: false,\n"
            "          icon: Icons.FileText,\n"
            f"          permission: {permission_var},\n"
            "        },\n"
        )
        if f'url: "{item_url}"' not in content:
            if "items: [] as {" in content:
                content = content.replace("items: [] as {", "items: [\n" + item_block + "      ] as {", 1)
            else:
                closing = "      ] as {"
                idx = content.find(closing)
                if idx == -1:
                    raise self._missing_marker("general-menu.tsx", "items: [ ... ] as {")
                content = content[:idx] + item_block + content[idx:]

        self._save_and_report(
            menu_file, content, "frontend/src/components/sidebar/components/menu-groups/general-menu.tsx"
        )

    def _update_existing_files(self, context: Dict[str, Any]):
        self._update_store(context)
        self._update_app_routes(context)
        self._update_permission_constants(context)
        self._update_permissions_hook(context)
        self._update_sidebar_menu(context)

    def generate_frontend_interface(self, model_data: Dict[str, Any], zone: str = "unknown") -> bool:
        """Genere une interface CRUD frontend complete pour un modele."""
        try:
            context = self._build_context(model_data)
            print(
                f"🚀 Génération frontend pour {context['model_name_pascal']} "
                f"(zone: {zone})"
            )

            model_root = self.frontend_src_dir / "models" / context["model_name_lower"]
            generated_files = [
                ("api.ts.j2", model_root / "api.ts"),
                ("schema.ts.j2", model_root / "schema.ts"),
                ("slice.ts.j2", model_root / "slice.ts"),
                ("pages-list.tsx.j2", model_root / "pages" / f"{context['model_name_lower']}-list.tsx"),
                (
                    "data-table.tsx.j2",
                    model_root / "components" / f"{context['model_name_lower']}-data" / f"{context['model_name_lower']}-data-table.tsx",
                ),
                (
                    "data-columns.tsx.j2",
                    model_root / "components" / f"{context['model_name_lower']}-data" / f"{context['model_name_lower']}-data-columns.tsx",
                ),
                (
                    "data-filter.tsx.j2",
                    model_root / "components" / f"{context['model_name_lower']}-data" / f"{context['model_name_lower']}-data-filter.tsx",
                ),
                (
                    "create-dialog.tsx.j2",
                    model_root / "components" / f"create-{context['model_name_lower']}" / f"create-{context['model_name_lower']}-dialog.tsx",
                ),
                (
                    "create-dialog-content.tsx.j2",
                    model_root / "components" / f"create-{context['model_name_lower']}" / f"create-{context['model_name_lower']}-dialog-content.tsx",
                ),
                (
                    "show-dialog.tsx.j2",
                    model_root
                    / "components"
                    / f"show-edit-or-delete-{context['model_name_lower']}"
                    / f"show-{context['model_name_lower']}-dialog.tsx",
                ),
                (
                    "show-dialog-content.tsx.j2",
                    model_root
                    / "components"
                    / f"show-edit-or-delete-{context['model_name_lower']}"
                    / f"show-{context['model_name_lower']}-dialog-content.tsx",
                ),
                (
                    "edit-dialog-content.tsx.j2",
                    model_root
                    / "components"
                    / f"show-edit-or-delete-{context['model_name_lower']}"
                    / f"edit-{context['model_name_lower']}-dialog-content.tsx",
                ),
                (
                    "delete-alert-dialog.tsx.j2",
                    model_root
                    / "components"
                    / f"show-edit-or-delete-{context['model_name_lower']}"
                    / f"delete-{context['model_name_lower']}-alert-dialog.tsx",
                ),
            ]

        except Exception as e:
            print(f"❌ Erreur pendant la génération frontend: {e}")
            return False

        # Instantane de tout ce qui va etre cree ou modifie, pour pouvoir annuler en cas d'echec
        touched = [path for _, path in generated_files] + list(self._existing_files().values())
        snapshot = {path: (path.read_bytes() if path.exists() else None) for path in touched}
        model_root_existed = model_root.exists()

        try:
            print(f"\n📁 Création des fichiers du modèle ({len(generated_files)})...")
            for template_name, file_path in generated_files:
                self._write_file_from_template(template_name, file_path, context)

            print(f"\n⚙️  Enregistrement du modèle dans le frontend ({len(self._existing_files())} fichiers existants)...")
            self._update_existing_files(context)

            print("\n🔍 Vérification de l'enregistrement...")
            self._verify_registration(context)
            print("  ✅ Vérification réussie (store, routes, permissions, menu)")

            print(f"\n✅ Interface frontend générée pour {context['model_name_pascal']} !")
            print("ℹ️  Étapes suivantes, depuis frontend/ : npm run lint puis npm run build")
            return True
        except Exception as e:
            print(f"\n❌ Erreur pendant la génération frontend: {e}")
            self._restore(snapshot, model_root, model_root_existed)
            return False

    def _verify_registration(self, context: Dict[str, Any]):
        """Relit les fichiers modifies et verifie que le modele y est bien enregistre."""
        files = self._existing_files()
        camel = context["model_name_camel"]
        checks = [
            ("store", f"{camel}Api.reducer"),
            ("store", f"{camel}Api.middleware"),
            ("routes", f'path="/{context["model_name_plural"]}"'),
            ("permission_constants", f'{context["permission_key"]}_VIEW'),
            ("permissions_hook", context["permission_view_var"]),
            ("sidebar_menu", f'url: "{context["model_name_plural"]}"'),
        ]
        for key, needle in checks:
            if needle not in files[key].read_text(encoding="utf-8"):
                raise RuntimeError(f"Vérification échouée : {needle!r} absent de {files[key].name}")

    def _restore(self, snapshot: Dict[Path, Any], model_root: Path, model_root_existed: bool):
        """Annule une generation partielle : restaure les fichiers modifies, supprime les nouveaux."""
        for path, original in snapshot.items():
            try:
                if original is None:
                    if path.exists():
                        path.unlink()
                else:
                    path.write_bytes(original)
            except OSError as restore_error:
                print(f"  ⚠️  Restauration impossible pour {path}: {restore_error}")
        if not model_root_existed and model_root.exists():
            shutil.rmtree(model_root, ignore_errors=True)
        print("🔄 Rollback : fichiers frontend restaurés dans leur état initial.")
