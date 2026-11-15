"""Compte système Selina (réponses forum @selina)."""

from django.contrib.auth import get_user_model

User = get_user_model()

SELINA_USERNAME = "selina"
SELINA_EMAIL = "selina@system.devstreet.local"
SELINA_MENTION_RE = r"(?i)@selina\b"


def get_selina_user():
    """Retourne le compte Selina s'il existe, sinon None."""
    return User.objects.filter(username__iexact=SELINA_USERNAME).first()


def ensure_selina_user() -> User:
    """
    Crée ou met à jour le compte système Selina.

    Login public impossible (mot de passe inutilisable). Le compte reste actif
    pour pouvoir publier des commentaires système.
    """
    user = get_selina_user()
    if user is None:
        user = User(
            username=SELINA_USERNAME,
            email=SELINA_EMAIL,
            first_name="Selina",
            last_name="IA",
            is_active=True,
            is_staff=False,
            is_superuser=False,
        )
        user.set_unusable_password()
        user.save()
        return user

    updated_fields: list[str] = []
    if user.email != SELINA_EMAIL:
        user.email = SELINA_EMAIL
        updated_fields.append("email")
    if user.first_name != "Selina":
        user.first_name = "Selina"
        updated_fields.append("first_name")
    if user.last_name != "IA":
        user.last_name = "IA"
        updated_fields.append("last_name")
    if not user.has_usable_password():
        pass
    else:
        user.set_unusable_password()
        updated_fields.append("password")
    if updated_fields:
        user.save(update_fields=updated_fields)
    return user
