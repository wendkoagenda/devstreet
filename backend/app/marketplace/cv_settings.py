"""Réglages de style du CV (couleur, police, mise en page…), propres à chaque profil dev.

Ils sont enregistrés en JSON sur le profil et complétés par des valeurs par défaut : un profil qui n'a rien réglé
garde le style d'origine. Le même contrôle sert à l'enregistrement et à l'aperçu (réglages passés dans l'adresse).
"""
from typing import Any, Dict, Optional

from rest_framework import serializers

# Couleurs principales proposées (clé -> couleur de la bande et des titres). Le violet est celui de l'application.
COLOR_PRESETS: Dict[str, str] = {
    "violet": "#5D487A",
    "bleu": "#1E4E8C",
    "vert": "#1F6F54",
    "orange": "#B5541C",
    "rose": "#A23B72",
    "rouge": "#9B2C2C",
    "ardoise": "#2F3A4A",
}

# Familles de polices : celles de base de la norme PDF, toujours disponibles (aucun fichier de police à embarquer).
FONTS = ("sans", "serif", "mono")
SIDEBARS = ("left", "right")
SIDEBAR_STYLES = ("filled", "light")
PHOTOS = ("round", "square", "none")
SKILL_STYLES = ("bars", "dots", "text")
DENSITIES = ("compact", "standard", "airy")
SECTIONS = ("contact", "skills", "languages", "reputation", "bio", "experiences", "prestations")

DEFAULTS: Dict[str, Any] = {
    "color": "violet",
    "font": "sans",
    "sidebar": "left",
    "sidebar_style": "filled",
    "photo": "round",
    "skills": "bars",
    "density": "standard",
    "hidden_sections": [],
}


class CvSettingsSerializer(serializers.Serializer):
    """Validation des réglages ; tous les champs sont facultatifs (les absents prennent leur valeur actuelle ou par défaut)."""

    color = serializers.CharField(required=False)
    font = serializers.ChoiceField(choices=FONTS, required=False)
    sidebar = serializers.ChoiceField(choices=SIDEBARS, required=False)
    sidebar_style = serializers.ChoiceField(choices=SIDEBAR_STYLES, required=False)
    photo = serializers.ChoiceField(choices=PHOTOS, required=False)
    skills = serializers.ChoiceField(choices=SKILL_STYLES, required=False)
    density = serializers.ChoiceField(choices=DENSITIES, required=False)
    hidden_sections = serializers.ListField(
        child=serializers.ChoiceField(choices=SECTIONS), required=False, allow_empty=True, max_length=len(SECTIONS)
    )

    def validate_color(self, value: str) -> str:
        """Une couleur proposée (par sa clé) ou une couleur personnalisée au format #RRGGBB."""
        value = value.strip()
        if value in COLOR_PRESETS:
            return value
        if len(value) == 7 and value.startswith("#") and all(c in "0123456789abcdefABCDEF" for c in value[1:]):
            return value.upper()
        raise serializers.ValidationError("Couleur invalide : choisissez une couleur proposée ou un code #RRGGBB.")

    def validate_hidden_sections(self, value):
        return list(dict.fromkeys(value))  # sans doublons, ordre conservé


def merged_settings(stored: Optional[dict], overrides: Optional[dict] = None) -> Dict[str, Any]:
    """Réglages complets : valeurs par défaut, puis ce qui est enregistré, puis les valeurs de l'aperçu."""
    result = dict(DEFAULTS)
    for source in (stored, overrides):
        if not isinstance(source, dict):
            continue
        for key, value in source.items():
            if key in DEFAULTS:
                result[key] = value
    return result


def validated_settings(data: Dict[str, Any], stored: Optional[dict] = None) -> Dict[str, Any]:
    """Valide `data` et le fusionne avec ce qui est enregistré ; lève une erreur de validation DRF sinon."""
    serializer = CvSettingsSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return merged_settings(stored, serializer.validated_data)


def color_hex(settings: Dict[str, Any]) -> str:
    """Couleur principale effective (#RRGGBB)."""
    color = settings.get("color", DEFAULTS["color"])
    return COLOR_PRESETS.get(color, color if str(color).startswith("#") else COLOR_PRESETS["violet"])
