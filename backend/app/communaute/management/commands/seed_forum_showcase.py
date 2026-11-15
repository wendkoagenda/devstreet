"""Peuple le forum avec un jeu showcase qualitatif (personas ouest-africains).

Usage (backend/, venv active) :
  python manage.py seed_forum_showcase
  python manage.py seed_forum_showcase --force
  python manage.py seed_forum_showcase --allow-non-debug   # prod / staging vide

Idempotent via e-mails @showcase.devstreet.local.
Mot de passe commun : SHOWCASE_PASSWORD (test@123).
"""
from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from app.communaute.models import (
    Commentaire,
    Conversation,
    Espace,
    FavoriPublication,
    LikeCommentaire,
    LikePublication,
    Message,
    MessageGroupe,
    ParticipationEspace,
    Publication,
    SuiviUtilisateur,
)

from . import _forum_showcase_data as data

User = get_user_model()
SHOWCASE_PASSWORD = "test@123"


class Command(BaseCommand):
    help = "Seed forum showcase : users, communautés, chaînes, publications, messages."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Réécrit les publications/messages showcase même s'ils existent.",
        )
        parser.add_argument(
            "--allow-non-debug",
            action="store_true",
            help="Autorise l'exécution quand DEBUG=False (prod/staging vide).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["allow_non_debug"]:
            raise CommandError(
                "DEBUG=False : passe --allow-non-debug pour peupler une instance vide "
                "(prod/staging). Commande refusée par sécurité."
            )

        with transaction.atomic():
            users = self._users()
            self.stdout.write(self.style.SUCCESS(f"{len(users)} utilisateurs showcase"))
            espaces = self._espaces(users)
            self.stdout.write(
                self.style.SUCCESS(
                    f"{len(espaces)} espaces "
                    f"({sum(1 for e in espaces.values() if e.type == 'COMMUNAUTE')} communautés, "
                    f"{sum(1 for e in espaces.values() if e.type == 'CHAINE')} chaînes)"
                )
            )
            n_pubs = self._publications(users, espaces, force=options["force"])
            self.stdout.write(self.style.SUCCESS(f"{n_pubs} publications showcase"))
            self._messages(users, espaces, force=options["force"])
            self.stdout.write(self.style.SUCCESS("Messages (DM + groupes) OK"))
            engagement = self._engagement(users, force=options["force"])
            self.stdout.write(
                self.style.SUCCESS(
                    "Engagement OK — "
                    f"{engagement['likes_pub']} likes pubs, "
                    f"{engagement['comments']} commentaires, "
                    f"{engagement['replies']} réponses, "
                    f"{engagement['likes_com']} likes com, "
                    f"{engagement['follows']} suivis, "
                    f"{engagement['favorites']} favoris"
                )
            )

        self.stdout.write(
            self.style.WARNING(
                f"Mot de passe commun des comptes @{data.DOMAIN} : {SHOWCASE_PASSWORD}"
            )
        )

    def _users(self) -> dict[str, User]:
        users: dict[str, User] = {}
        for person in data.USERS:
            email = f"{person['key']}@{data.DOMAIN}"
            user, _created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": person["username"][:30],
                    "first_name": person["first"],
                    "last_name": person["last"],
                    "is_active": True,
                },
            )
            user.first_name = person["first"]
            user.last_name = person["last"]
            user.username = person["username"][:30]
            user.set_password(SHOWCASE_PASSWORD)
            user.save()
            users[person["key"]] = user
        return users

    def _espaces(self, users: dict[str, User]) -> dict[str, Espace]:
        espaces: dict[str, Espace] = {}
        for spec in data.COMMUNITIES:
            espaces[spec["key"]] = self._ensure_espace(
                users,
                nom=spec["nom"],
                type_espace="COMMUNAUTE",
                description=spec["description"],
                creator_key=spec["creator"],
                member_keys=spec["members"],
                membres_peuvent_publier=True,
                commentaires_ouverts=True,
            )
        for spec in data.CHANNELS:
            espaces[spec["key"]] = self._ensure_espace(
                users,
                nom=spec["nom"],
                type_espace="CHAINE",
                description=spec["description"],
                creator_key=spec["creator"],
                member_keys=spec["members"],
                membres_peuvent_publier=False,
                commentaires_ouverts=spec.get("commentaires_ouverts", True),
            )
        return espaces

    def _ensure_espace(
        self,
        users: dict[str, User],
        *,
        nom: str,
        type_espace: str,
        description: str,
        creator_key: str,
        member_keys: list[str],
        membres_peuvent_publier: bool,
        commentaires_ouverts: bool,
    ) -> Espace:
        creator = users[creator_key]
        espace, _ = Espace.objects.update_or_create(
            nom=nom,
            type=type_espace,
            defaults={
                "description": description,
                "acces": "PUBLIC",
                "membres_peuvent_publier": membres_peuvent_publier,
                "commentaires_ouverts": commentaires_ouverts,
                "created_by": creator.id,
                "updated_by": creator.id,
            },
        )
        # Créateur = super admin
        ParticipationEspace.objects.update_or_create(
            espace=espace,
            membre=creator,
            defaults={
                "role": ParticipationEspace.ROLE_SUPER_ADMIN,
                "created_by": creator.id,
                "updated_by": creator.id,
            },
        )
        for key in member_keys:
            membre = users.get(key)
            if not membre or membre.id == creator.id:
                continue
            ParticipationEspace.objects.get_or_create(
                espace=espace,
                membre=membre,
                defaults={
                    "role": ParticipationEspace.ROLE_MEMBRE,
                    "created_by": membre.id,
                    "updated_by": membre.id,
                },
            )
        return espace

    def _publications(
        self,
        users: dict[str, User],
        espaces: dict[str, Espace],
        *,
        force: bool,
    ) -> int:
        ready = 0
        for spec in data.PUBLICATIONS:
            auteur = users[spec["auteur"]]
            espace = espaces.get(spec["espace"]) if spec.get("espace") else None
            defaults = {
                "description": spec["description"],
                "type": spec["type"],
                "espace": espace,
                "lien_app": spec.get("lien_app", ""),
                "plateforme_app": spec.get("plateforme_app", ""),
                "created_by": auteur.id,
                "updated_by": auteur.id,
            }
            existing = Publication.objects.filter(
                auteur=auteur, titre=spec["titre"]
            ).first()
            if existing:
                if force:
                    for field, value in defaults.items():
                        setattr(existing, field, value)
                    existing.save()
                ready += 1
                continue
            Publication.objects.create(auteur=auteur, titre=spec["titre"], **defaults)
            ready += 1
        return ready

    def _messages(
        self,
        users: dict[str, User],
        espaces: dict[str, Espace],
        *,
        force: bool,
    ) -> None:
        for community_key, lines in data.GROUP_MESSAGES.items():
            espace = espaces.get(community_key)
            if not espace:
                continue
            if MessageGroupe.objects.filter(espace=espace).exists() and not force:
                continue
            if force:
                MessageGroupe.objects.filter(espace=espace).delete()
            for auteur_key, texte in lines:
                auteur = users[auteur_key]
                MessageGroupe.objects.create(
                    espace=espace,
                    auteur=auteur,
                    texte=texte,
                    created_by=auteur.id,
                    updated_by=auteur.id,
                )

        for a_key, b_key, lines in data.DIRECT_MESSAGES:
            a, b = users[a_key], users[b_key]
            id1, id2 = sorted([a.id, b.id])
            conv, _ = Conversation.objects.get_or_create(
                membre_1_id=id1,
                membre_2_id=id2,
                defaults={"created_by": a.id, "updated_by": a.id},
            )
            if Message.objects.filter(conversation=conv).exists() and not force:
                continue
            if force:
                Message.objects.filter(conversation=conv).delete()
            for auteur_key, texte in lines:
                auteur = users[auteur_key]
                Message.objects.create(
                    conversation=conv,
                    auteur=auteur,
                    texte=texte,
                    created_by=auteur.id,
                    updated_by=auteur.id,
                )

    def _engagement(self, users: dict[str, User], *, force: bool) -> dict[str, int]:
        stats = {
            "likes_pub": 0,
            "comments": 0,
            "replies": 0,
            "likes_com": 0,
            "follows": 0,
            "favorites": 0,
        }
        pubs = {
            pub.titre: pub
            for pub in Publication.objects.filter(
                titre__in=[p["titre"] for p in data.PUBLICATIONS]
            )
        }

        for titre, liker_keys in data.PUBLICATION_LIKES.items():
            pub = pubs.get(titre)
            if not pub:
                continue
            for key in liker_keys:
                membre = users.get(key)
                if not membre:
                    continue
                _, created = LikePublication.objects.get_or_create(
                    publication=pub,
                    membre=membre,
                    defaults={"created_by": membre.id, "updated_by": membre.id},
                )
                if created:
                    stats["likes_pub"] += 1

        for spec in data.COMMENTS:
            pub = pubs.get(spec["publication"])
            auteur = users.get(spec["auteur"])
            if not pub or not auteur:
                continue
            comment = Commentaire.objects.filter(
                publication=pub, auteur=auteur, parent__isnull=True, texte=spec["texte"]
            ).first()
            if comment and force:
                comment.nature = spec["nature"]
                comment.updated_by = auteur.id
                comment.save(update_fields=["nature", "updated_by", "updated_at"])
            elif not comment:
                comment = Commentaire.objects.create(
                    publication=pub,
                    auteur=auteur,
                    parent=None,
                    nature=spec["nature"],
                    texte=spec["texte"],
                    created_by=auteur.id,
                    updated_by=auteur.id,
                )
                stats["comments"] += 1
            else:
                stats["comments"] += 1

            for liker_key in spec.get("likes", []):
                liker = users.get(liker_key)
                if not liker:
                    continue
                _, created = LikeCommentaire.objects.get_or_create(
                    commentaire=comment,
                    membre=liker,
                    defaults={"created_by": liker.id, "updated_by": liker.id},
                )
                if created:
                    stats["likes_com"] += 1

            for reply_auteur_key, reply_texte in spec.get("replies", []):
                reply_auteur = users.get(reply_auteur_key)
                if not reply_auteur:
                    continue
                reply = Commentaire.objects.filter(
                    publication=pub,
                    auteur=reply_auteur,
                    parent=comment,
                    texte=reply_texte,
                ).first()
                if not reply:
                    Commentaire.objects.create(
                        publication=pub,
                        auteur=reply_auteur,
                        parent=comment,
                        nature="COMMENTAIRE",
                        texte=reply_texte,
                        created_by=reply_auteur.id,
                        updated_by=reply_auteur.id,
                    )
                    stats["replies"] += 1
                else:
                    stats["replies"] += 1

        for suiveur_key, suivi_key in data.FOLLOWS:
            suiveur, suivi = users.get(suiveur_key), users.get(suivi_key)
            if not suiveur or not suivi or suiveur.id == suivi.id:
                continue
            _, created = SuiviUtilisateur.objects.get_or_create(
                suiveur=suiveur,
                suivi=suivi,
                defaults={"created_by": suiveur.id, "updated_by": suiveur.id},
            )
            if created:
                stats["follows"] += 1

        for user_key, titre in data.FAVORITES:
            membre = users.get(user_key)
            pub = pubs.get(titre)
            if not membre or not pub:
                continue
            _, created = FavoriPublication.objects.get_or_create(
                membre=membre,
                publication=pub,
                defaults={"created_by": membre.id, "updated_by": membre.id},
            )
            if created:
                stats["favorites"] += 1

        return stats
