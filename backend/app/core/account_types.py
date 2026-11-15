"""Types de compte (développeur / entreprise) et rôles associés.

Module de données pures : aucun import de modèle, afin de pouvoir l'utiliser
aussi bien dans les modèles que dans les migrations de données.
"""

TYPE_NONE = ''
TYPE_DEV = 'dev'
TYPE_ENTREPRISE = 'entreprise'
TYPE_BOTH = 'both'

# Types qu'un membre peut choisir (le type vide signifie « pas encore choisi »)
CHOOSABLE_TYPES =(TYPE_DEV, TYPE_ENTREPRISE, TYPE_BOTH)

ACCOUNT_TYPE_CHOICES = (
    (TYPE_NONE, 'Non choisi'),
    (TYPE_DEV, 'Développeur'),
    (TYPE_ENTREPRISE, 'Entreprise'),
    (TYPE_BOTH, 'Développeur et entreprise'),
)

ROLE_DEV = 'Membre Dev'
ROLE_ENTREPRISE = 'Membre Entreprise'

# Rôles IAM de base : leurs porteurs sont des comptes d'administration
# (pas d'onboarding, menu Administration conservé).
ADMIN_ROLE_NAMES = ('Super Admin', 'Admin', 'Manager', 'Editor', 'Viewer')

# Ancien rôle unique donné à tous les membres avant l'onboarding par type.
LEGACY_MEMBER_ROLE = 'DevStreet Hub Developer'

ROLE_DESCRIPTIONS = {
    ROLE_DEV: 'Membre développeur : forum, communautés, messagerie, projets et marketplace.',
    ROLE_ENTREPRISE: 'Membre entreprise : marketplace et messagerie uniquement.',
}

# Codes de messagerie accessibles à l'entreprise (les vues exigent seulement d'être connecté,
# ces codes décrivent l'accès côté interface).
ENTREPRISE_CODES = (
    'conversations.view',
    'conversations.create',
    'messages.view',
    'messages.create',
    'notifications-resume.view',
)


def split_types(account_type: str) -> set:
    """Retourne l'ensemble des types simples ('dev', 'entreprise') portés par un type de compte."""
    if account_type == TYPE_BOTH:
        return {TYPE_DEV, TYPE_ENTREPRISE}
    if account_type in (TYPE_DEV, TYPE_ENTREPRISE):
        return {account_type}
    return set()


def join_types(types: set) -> str:
    """Inverse de `split_types` : reconstruit le type de compte à partir d'un ensemble de types simples."""
    if TYPE_DEV in types and TYPE_ENTREPRISE in types:
        return TYPE_BOTH
    if TYPE_DEV in types:
        return TYPE_DEV
    if TYPE_ENTREPRISE in types:
        return TYPE_ENTREPRISE
    return TYPE_NONE


def merge_account_type(current: str, requested: str) -> str:
    """Fusionne le type actuel et le type demandé : un type n'est jamais retiré, seulement ajouté."""
    return join_types(split_types(current) | split_types(requested))


def role_names_for(account_type: str) -> list:
    """Noms des rôles à attribuer pour un type de compte."""
    types = split_types(account_type)
    names = []
    if TYPE_DEV in types:
        names.append(ROLE_DEV)
    if TYPE_ENTREPRISE in types:
        names.append(ROLE_ENTREPRISE)
    return names


def permission_codes_for_role(role_name: str) -> set:
    """Codes de permission d'un rôle de membre (import différé : modules de codes des autres apps)."""
    if role_name == ROLE_ENTREPRISE:
        return set(ENTREPRISE_CODES)
    if role_name == ROLE_DEV:
        from app.communaute.permission_codes import COMMUNAUTE_PERMISSION_CODES
        from app.devstreet_hub.management.commands.init_devstreet_hub import DEVELOPER_CODES

        return set(COMMUNAUTE_PERMISSION_CODES) | set(DEVELOPER_CODES)
    return set()
