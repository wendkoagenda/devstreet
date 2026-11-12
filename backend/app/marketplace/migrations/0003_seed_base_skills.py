"""Référentiel de base des compétences, pour que les utilisateurs puissent renseigner leur profil dès le départ.

Les compétences sont gérées par l'administration : les utilisateurs choisissent dans cette liste.
"""
from django.db import migrations
from django.utils.text import slugify

# (nom, type, catégorie) ; liste figée, une migration ne dépend pas du code applicatif
SKILLS = [
    ("Python", "hard", "backend"),
    ("Django", "hard", "backend"),
    ("Node.js", "hard", "backend"),
    ("API REST", "hard", "backend"),
    ("PostgreSQL", "hard", "backend"),
    ("SQL", "hard", "data"),
    ("Java", "hard", "backend"),
    ("PHP", "hard", "backend"),
    ("Laravel", "hard", "backend"),
    ("JavaScript", "hard", "frontend"),
    ("TypeScript", "hard", "frontend"),
    ("React", "hard", "frontend"),
    ("Vue.js", "hard", "frontend"),
    ("CSS", "hard", "frontend"),
    ("Tests", "hard", "frontend"),
    ("React Native", "hard", "mobile"),
    ("Flutter", "hard", "mobile"),
    ("Firebase", "hard", "mobile"),
    ("Géolocalisation", "hard", "mobile"),
    ("API Mobile Money", "hard", "backend"),
    ("Docker", "hard", "devops"),
    ("Kubernetes", "hard", "devops"),
    ("GCP", "hard", "devops"),
    ("CI/CD", "hard", "devops"),
    ("Git", "hard", "devops"),
    ("Pandas", "hard", "data"),
    ("Power BI", "hard", "data"),
    ("Charts", "hard", "data"),
    ("Figma", "hard", "design"),
    ("Gestion de projet", "hard", "management"),
    ("Communication", "soft", "soft"),
    ("Esprit d'équipe", "soft", "soft"),
    ("Curiosité", "soft", "soft"),
    ("Autonomie", "soft", "soft"),
    ("Résolution de problèmes", "soft", "soft"),
]


def seed_skills(apps, schema_editor):
    Skill = apps.get_model("marketplace", "Skill")
    alias = schema_editor.connection.alias
    for name, skill_type, category in SKILLS:
        Skill.objects.using(alias).get_or_create(
            name=name,
            defaults={
                "slug": slugify(name),
                "type": skill_type,
                "category": category,
                # compétence créée par le système, sans utilisateur auteur
                "created_by": 0,
                "updated_by": 0,
            },
        )


def unseed_skills(apps, schema_editor):
    """Retire les compétences de base qui ne sont pas encore utilisées."""
    Skill = apps.get_model("marketplace", "Skill")
    Skill.objects.using(schema_editor.connection.alias).filter(
        name__in=[name for name, _type, _category in SKILLS], profil_skills__isnull=True, offers__isnull=True
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("marketplace", "0002_seed_marketplace_permissions"),
    ]

    operations = [
        migrations.RunPython(seed_skills, unseed_skills),
    ]
