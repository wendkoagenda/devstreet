"""Codes de permission des modèles communauté (<ressource>.<action>), utilisés par `init_data`."""

RESOURCES = (
    "avis-choix",
    "commentaires",
    "confirmations-aide",
    "conversations",
    "espaces",
    "favoris-publication",
    "images-publication",
    "liens-invitation",
    "likes-commentaire",
    "likes-publication",
    "medias-commentaire",
    "messages",
    "notifications-resume",
    "options-publication",
    "participations-espace",
    "publications",
    "suivis-tag",
    "suivis-utilisateur",
    "tags",
    "votes-sondage",
)
ACTIONS = ("view", "create", "update", "delete")

COMMUNAUTE_PERMISSION_CODES = [
    f"{resource}.{action}" for resource in RESOURCES for action in ACTIONS
]

# Sous-ensemble « membre public » : interactions sociales (like, commenter, rejoindre…).
MEMBER_SOCIAL_PERMISSION_CODES = tuple(
    code
    for code in COMMUNAUTE_PERMISSION_CODES
    if code.endswith((".view", ".create"))
)
