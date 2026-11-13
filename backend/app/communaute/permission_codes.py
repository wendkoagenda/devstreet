"""Codes de permission des modèles communauté (<ressource>.<action>), utilisés par `init_data`."""

RESOURCES = (
    "avis-choix",
    "commentaires",
    "confirmations-aide",
    "conversations",
    "espaces",
    "images-publication",
    "liens-invitation",
    "likes-commentaire",
    "likes-publication",
    "messages",
    "notifications-resume",
    "options-publication",
    "participations-espace",
    "publications",
    "suivis-utilisateur",
    "votes-sondage",
)
ACTIONS = ("view", "create", "update", "delete")

COMMUNAUTE_PERMISSION_CODES = [
    f"{resource}.{action}" for resource in RESOURCES for action in ACTIONS
]
