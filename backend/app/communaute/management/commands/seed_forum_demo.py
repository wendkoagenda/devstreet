"""
Génère un jeu de démo forum : utilisateurs, pubs, espaces, messages.
Usage (depuis backend/, venv active) :
  python manage.py seed_forum_demo
  python manage.py seed_forum_demo --publications 200 --users 15
"""
from __future__ import annotations

import random
import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from app.communaute.models import (
    Conversation,
    Espace,
    Message,
    MessageGroupe,
    ParticipationEspace,
    Publication,
)

User = get_user_model()

FIRST_NAMES = [
    "Amina", "Bruno", "Chloé", "Diego", "Emma", "Farid", "Gina", "Hugo",
    "Inès", "Jules", "Karim", "Léa", "Maya", "Noah", "Omar", "Paula",
    "Quinn", "Rania", "Samir", "Tina",
]
LAST_NAMES = [
    "Martin", "Bernard", "Dubois", "Petit", "Moreau", "Laurent", "Simon",
    "Michel", "Lefebvre", "Garcia", "Roux", "Fournier", "Morel", "Girard",
]

DISCUSSION_TITLES = [
    "Comment structurer une API Django propre ?",
    "Vite + React : bonnes pratiques 2026",
    "Qui utilise PostgreSQL en prod ici ?",
    "Retour d'expérience sur RTK Query",
    "Design system : shadcn ou custom ?",
    "CI/CD trop lent, des idées ?",
    "Comment gérer les permissions métier ?",
    "Socket.IO vs SSE pour le chat",
    "Migrer vers Django 6 sans casse",
    "Astuces Tailwind pour le dark mode",
]
APP_TITLES = [
    "Kanban léger pour freelances",
    "Tracker de PR open-source",
    "Agenda partagé d'équipe",
    "Générateur de README",
    "Dashboard métriques Git",
]
ENTRAIDE_TITLES = [
    "Bug CORS en local Vite",
    "Migration Alembic vs Django",
    "JWT refresh qui expire trop tôt",
    "Pagination curseur instable",
    "Upload images trop lourd",
]


class Command(BaseCommand):
    help = "Seed forum : users, publications, espaces, messages de démo"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=15)
        parser.add_argument("--publications", type=int, default=200)
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recrée les données démo même si le marqueur existe",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        n_users = max(5, options["users"])
        n_pubs = max(20, options["publications"])
        force = options["force"]
        # Mot de passe aléatoire propre à cette exécution : aucun secret n'est écrit dans le code.
        self.demo_password = secrets.token_urlsafe(16)
        self.comptes_crees = 0

        marker_email = "seed.forum.demo@devstreet.local"
        if User.objects.filter(email=marker_email).exists() and not force:
            self.stdout.write(
                self.style.WARNING(
                    "Seed déjà présent (seed.forum.demo@…). "
                    "Utilise --force pour réenrichir."
                )
            )
            # On continue quand même pour compléter pubs/users manquants
        else:
            User.objects.get_or_create(
                email=marker_email,
                defaults={
                    "username": "seed_forum_demo",
                    "first_name": "Seed",
                    "last_name": "Demo",
                    "is_active": True,
                },
            )

        users = self._ensure_users(n_users)
        # Inclut aussi les comptes locaux déjà présents (pour tester avec ton login)
        locals_users = list(
            User.objects.exclude(email__endswith="@devstreet.demo")
            .exclude(email="seed.forum.demo@devstreet.local")
            .order_by("id")[:5]
        )
        for local in locals_users:
            if local not in users:
                users.insert(0, local)
        self.stdout.write(self.style.SUCCESS(f"{len(users)} utilisateurs prêts"))

        espaces = self._ensure_espaces(users)
        self.stdout.write(self.style.SUCCESS(f"{len(espaces)} espaces prêts"))

        created_pubs = self._ensure_publications(users, espaces, n_pubs)
        self.stdout.write(
            self.style.SUCCESS(f"{created_pubs} publications créées (total)")
        )

        self._ensure_messages(users, espaces)
        self.stdout.write(self.style.SUCCESS("Messages / chats de démo OK"))

        if self.comptes_crees:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Mot de passe des {self.comptes_crees} comptes *demo* créés "
                    f"à l'instant : {self.demo_password}"
                )
            )
        else:
            self.stdout.write(
                "Aucun compte démo créé : les mots de passe existants sont inchangés."
            )

    def _ensure_users(self, n_users: int) -> list:
        users: list[User] = []
        existing = list(
            User.objects.filter(email__endswith="@devstreet.demo").order_by("id")
        )
        users.extend(existing)

        i = len(existing) + 1
        while len(users) < n_users:
            first = FIRST_NAMES[(i - 1) % len(FIRST_NAMES)]
            last = LAST_NAMES[(i - 1) % len(LAST_NAMES)]
            email = f"{first.lower()}.{last.lower()}{i}@devstreet.demo"
            username = f"{first.lower()}{last.lower()}{i}"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username[:30],
                    "first_name": first,
                    "last_name": last,
                    "is_active": True,
                },
            )
            if created:
                user.set_password(self.demo_password)
                user.save(update_fields=["password"])
                self.comptes_crees += 1
            users.append(user)
            i += 1
        return users

    def _ensure_espaces(self, users: list[User]) -> list[Espace]:
        specs = [
            ("COMMUNAUTE", "DevStreet Chat", "Discussions générales des membres"),
            ("COMMUNAUTE", "React FR", "Tout sur React et TypeScript"),
            ("COMMUNAUTE", "Backend Django", "DRF, ORM, perfs"),
            ("COMMUNAUTE", "Design & UX", "UI, accessibilité, motion"),
            ("CHAINE", "Annonces DevStreet", "Nouveautés produit officielles"),
            ("CHAINE", "Jobs & freelances", "Offres et missions"),
            ("CHAINE", "Tips du jour", "Astuces courtes"),
            ("CHAINE", "Release notes", "Changelog hebdo"),
        ]
        creator = users[0]
        espaces: list[Espace] = []
        for type_espace, nom, description in specs:
            espace, created = Espace.objects.get_or_create(
                nom=nom,
                type=type_espace,
                defaults={
                    "description": description,
                    "acces": "PUBLIC",
                    "membres_peuvent_publier": type_espace == "COMMUNAUTE",
                    "commentaires_ouverts": True,
                    "created_by": creator.id,
                    "updated_by": creator.id,
                },
            )
            espaces.append(espace)
            if created or not ParticipationEspace.objects.filter(
                espace=espace, membre=creator
            ).exists():
                ParticipationEspace.objects.get_or_create(
                    espace=espace,
                    membre=creator,
                    defaults={
                        "role": ParticipationEspace.ROLE_SUPER_ADMIN,
                        "created_by": creator.id,
                        "updated_by": creator.id,
                    },
                )

            # Membres aléatoires pour volume
            sample = random.sample(users, k=min(len(users), random.randint(3, len(users))))
            for membre in sample:
                ParticipationEspace.objects.get_or_create(
                    espace=espace,
                    membre=membre,
                    defaults={
                        "role": ParticipationEspace.ROLE_MEMBRE,
                        "created_by": membre.id,
                        "updated_by": membre.id,
                    },
                )
        return espaces

    def _ensure_publications(
        self, users: list[User], espaces: list[Espace], target: int
    ) -> int:
        existing = Publication.objects.filter(espace__isnull=True).count()
        to_create = max(0, target - existing)
        if to_create == 0:
            return existing

        channels = [e for e in espaces if e.type == "CHAINE"]
        now = timezone.now()
        batch: list[Publication] = []
        for i in range(to_create):
            auteur = random.choice(users)
            roll = random.random()
            if roll < 0.55:
                pub_type = "DISCUSSION"
                titre = random.choice(DISCUSSION_TITLES)
            elif roll < 0.75:
                pub_type = "APPLICATION"
                titre = random.choice(APP_TITLES)
            else:
                pub_type = "ENTRAIDE"
                titre = random.choice(ENTRAIDE_TITLES)

            # ~15% dans une chaîne
            espace = None
            if channels and random.random() < 0.15:
                espace = random.choice(channels)

            created_at = now - timedelta(
                days=random.randint(0, 40),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            batch.append(
                Publication(
                    auteur=auteur,
                    espace=espace,
                    type=pub_type,
                    titre=f"{titre} #{existing + i + 1}",
                    description=(
                        f"Publication de démo par {auteur.first_name}. "
                        f"Contenu de test #{existing + i + 1} pour le fil d'actualité."
                    ),
                    lien_app="https://example.com/app" if pub_type == "APPLICATION" else "",
                    plateforme_app="WEB" if pub_type == "APPLICATION" else "",
                    created_by=auteur.id,
                    updated_by=auteur.id,
                    created_at=created_at,
                    updated_at=created_at,
                )
            )
            if len(batch) >= 50:
                Publication.objects.bulk_create(batch)
                batch = []
        if batch:
            Publication.objects.bulk_create(batch)
        return Publication.objects.filter(espace__isnull=True).count() + Publication.objects.filter(
            espace__isnull=False
        ).count()

    def _ensure_messages(self, users: list[User], espaces: list[Espace]) -> None:
        # Quelques DM
        for a, b in zip(users, users[1:6]):
            id1, id2 = sorted([a.id, b.id])
            conv, _ = Conversation.objects.get_or_create(
                membre_1_id=id1,
                membre_2_id=id2,
                defaults={"created_by": a.id, "updated_by": a.id},
            )
            if not Message.objects.filter(conversation=conv).exists():
                for idx, texte in enumerate(
                    [
                        f"Salut {b.first_name} !",
                        "Tu as vu le dernier post sur Django ?",
                        "On se fait une review demain ?",
                    ]
                ):
                    auteur = a if idx % 2 == 0 else b
                    Message.objects.create(
                        conversation=conv,
                        auteur=auteur,
                        texte=texte,
                        created_by=auteur.id,
                        updated_by=auteur.id,
                    )

        # Messages de groupe dans les communautés
        for espace in [e for e in espaces if e.type == "COMMUNAUTE"]:
            if MessageGroupe.objects.filter(espace=espace).exists():
                continue
            membres = list(
                ParticipationEspace.objects.filter(espace=espace).select_related(
                    "membre"
                )
            )
            if not membres:
                continue
            for i in range(8):
                part = random.choice(membres)
                MessageGroupe.objects.create(
                    espace=espace,
                    auteur=part.membre,
                    texte=f"Message de groupe #{i + 1} dans {espace.nom}",
                    created_by=part.membre_id,
                    updated_by=part.membre_id,
                )
