"""Codes de permission des modèles de la marketplace (<ressource>.<action>), utilisés par `init_data`."""

RESOURCES = (
    "companies",
    "skills",
    "profils",
    "offers",
    "candidatures",
    "profil-skills",
    "experiences",
    "prestations",
    "profil-histories",
    "availabilities",
    "reviews",
    "swipes",
    "connections",
)
ACTIONS = ("view", "create", "update", "delete")

MARKETPLACE_PERMISSION_CODES = [f"{resource}.{action}" for resource in RESOURCES for action in ACTIONS]
