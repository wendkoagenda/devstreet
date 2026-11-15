"""Données de démonstration complètes de la marketplace : toutes les tables, avec des liens cohérents.

Crée des entreprises, des recruteurs, des développeurs (compétences, expériences, prestations, calendriers, historique),
des offres, des candidatures, des avis, des swipes et des connexions. Les comptes partagent le mot de passe `test@123`.

La commande est idempotente : relancée, elle met à jour les mêmes enregistrements (identifiés par e-mail, slug…).
`--reset` supprime d'abord toutes les données de démonstration (comptes en @marketplace.example.test).
"""
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from app.marketplace.models import (
    Availability,
    Candidature,
    Company,
    Connection,
    Experience,
    Offer,
    Prestation,
    Profil,
    ProfilHistory,
    ProfilSkill,
    Review,
    Skill,
    Swipe,
)
from app.marketplace.services.scoring import mission_period

from . import _demo_data as demo

User = get_user_model()
SYSTEM_ID = 0  # created_by / updated_by des objets créés par le système (pas d'utilisateur auteur)
SHOWCASE_PASSWORD = "test@123"


def _email(key: str) -> str:
    return f"{key}@{demo.DOMAIN}"


class Command(BaseCommand):
    help = "Insère des données de démonstration pour toutes les tables de la marketplace (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Supprime d'abord les données de démonstration existantes.")
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
        if options["reset"] and not settings.DEBUG and not options["allow_non_debug"]:
            raise CommandError("--reset hors DEBUG nécessite aussi --allow-non-debug.")
        self.today = timezone.localdate()
        self.now = timezone.now()
        with transaction.atomic():
            if options["reset"]:
                self._reset()
            self.users = self._users()
            self.skills = self._skills()
            self.companies = self._companies()
            self.profils = self._profils()
            self._profil_skills()
            self._experiences()
            self._prestations()
            self._histories()
            self.offers = self._offers()
            self._candidatures()
            self._availabilities()
            self._reviews()
            self._swipes_and_connections()
        self._report()

    # ── Nettoyage ────────────────────────────────────────────────────────────

    def _reset(self):
        """Supprime les données de démonstration dans l'ordre imposé par les clés étrangères protégées (RESTRICT)."""
        users = User.objects.filter(email__endswith=f"@{demo.DOMAIN}")
        profils = Profil.objects.filter(user__in=users)
        companies = Company.objects.filter(slug__in=[item["key"] + "-demo" for item in demo.COMPANIES])
        Offer.objects.filter(company__in=companies).delete()  # supprime aussi leurs candidatures
        Review.objects.filter(author__in=profils).delete()
        Review.objects.filter(target__in=profils).delete()
        companies.delete()
        profils.delete()  # compétences, expériences, prestations, calendriers, swipes, connexions, historique
        users.delete()
        self.stdout.write(self.style.WARNING("Données de démonstration supprimées."))

    # ── Comptes ──────────────────────────────────────────────────────────────

    def _users(self) -> dict:
        users = {}
        for person in demo.RECRUITERS + demo.DEVS:
            user, _created = User.objects.get_or_create(
                email=_email(person["key"]),
                defaults={"username": f"mp-{person['key']}", "first_name": person["first"], "last_name": person["last"]},
            )
            user.first_name = person["first"]
            user.last_name = person["last"]
            user.set_password(SHOWCASE_PASSWORD)
            user.save()
            users[person["key"]] = user
        return users

    # ── Référentiel ──────────────────────────────────────────────────────────

    def _skills(self) -> dict:
        """Compétences utilisées par le jeu de données : celles du référentiel de base, créées si elles manquent."""
        names = {name for dev in demo.DEVS for name in dev["skills"]} | {name for offer in demo.OFFERS for name in offer["skills"]}
        skills = {}
        for name in sorted(names):
            skills[name], _ = Skill.objects.get_or_create(
                name=name,
                defaults={"slug": slugify(name), "type": "hard", "category": "", "created_by": SYSTEM_ID, "updated_by": SYSTEM_ID},
            )
        return skills

    def _companies(self) -> dict:
        companies = {}
        for item in demo.COMPANIES:
            company, _ = Company.objects.update_or_create(
                slug=f"{item['key']}-demo",
                defaults={
                    "name": item["name"], "description": item["description"], "sector": item["sector"], "size": item["size"],
                    "website": item["website"], "contact_email": item["contact_email"], "phone": item["phone"],
                    "country": item["country"], "city": item["city"], "address": item["address"],
                    "is_verified": item["verified"], "verified_at": self.now if item["verified"] else None,
                    "created_by": SYSTEM_ID, "updated_by": SYSTEM_ID,
                },
            )
            companies[item["key"]] = company
        return companies

    # ── Profils ──────────────────────────────────────────────────────────────

    def _profils(self) -> dict:
        profils = {}
        for person in demo.RECRUITERS:
            base = {
                "headline": person["headline"], "country": person["country"], "city": person["city"], "timezone": person["tz"],
                "bio": "", "is_open_to_work": False, "cv_visibility": "private", "years_of_experience": 0,
            }
            # Comme après la migration des profils existants : un profil dev (vide) et un profil entreprise
            self._save_profil(person, {**base, "company": None, "is_company_owner": False})
            profils[person["key"]] = self._save_profil(
                person,
                {**base, "company": self.companies[person["company"]], "is_company_owner": person["owner"]},
                type="entreprise",
            )
        for dev in demo.DEVS:
            profils[dev["key"]] = self._save_profil(
                dev,
                {
                    "headline": dev["headline"], "bio": dev["bio"], "country": dev["country"], "city": dev["city"],
                    "timezone": dev["tz"], "remote": dev["remote"], "is_open_to_work": dev["open"],
                    "years_of_experience": dev["years"], "daily_rate": dev["rate"], "currency": "XOF",
                    "languages": [{"language": name} for name in dev["languages"]], "github_url": dev["github"],
                    "cv_visibility": dev["cv"], "company": None, "is_company_owner": False,
                },
            )
        return profils

    def _save_profil(self, person: dict, fields: dict, type: str = "dev") -> Profil:
        user = self.users[person["key"]]
        slug = f"{slugify(person['first'])}-{slugify(person['last'])}"
        if type == "entreprise":
            slug += "-entreprise"
        if Profil.objects.filter(slug=slug).exclude(user=user, type=type).exists():
            slug += "-demo"  # le slug est déjà pris par un vrai profil
        profil, _ = Profil.objects.update_or_create(
            user=user, type=type, defaults={"slug": slug, "created_by": user.id, "updated_by": user.id, **fields}
        )
        return profil

    def _profil_skills(self):
        for dev in demo.DEVS:
            profil = self.profils[dev["key"]]
            for name, (level, years) in dev["skills"].items():
                ProfilSkill.objects.update_or_create(
                    profil=profil, skill=self.skills[name],
                    defaults={"level": level, "years": years, "created_by": profil.user_id, "updated_by": profil.user_id},
                )

    def _experiences(self):
        for dev in demo.DEVS:
            profil = self.profils[dev["key"]]
            for title, company, location, contract, start, end, description, technologies in dev["experiences"]:
                Experience.objects.update_or_create(
                    profil=profil, title=title, company_name=company,
                    defaults={
                        "location": location, "contract_type": contract, "start_date": date.fromisoformat(start),
                        "end_date": date.fromisoformat(end) if end else None, "is_current": end is None,
                        "description": description, "technologies": technologies,
                        "created_by": profil.user_id, "updated_by": profil.user_id,
                    },
                )

    def _prestations(self):
        for dev in demo.DEVS:
            if "prestation" not in dev:
                continue
            title, category, price, days, revisions, description = dev["prestation"]
            profil = self.profils[dev["key"]]
            Prestation.objects.update_or_create(
                slug=f"{dev['key']}-{slugify(title)}"[:160],
                defaults={
                    "profil": profil, "title": title, "description": description, "category": category, "price": price,
                    "currency": "XOF", "delivery_days": days, "revisions": revisions, "is_active": True,
                    "created_by": profil.user_id, "updated_by": profil.user_id,
                },
            )

    def _histories(self):
        for key, field, old, new, source in demo.HISTORIES:
            profil = self.profils[key]
            ProfilHistory.objects.get_or_create(
                profil=profil, field=field, new_value=new,
                defaults={
                    "old_value": old, "source": source, "changed_by": None if source != "manual" else profil.user,
                    "created_by": profil.user_id, "updated_by": profil.user_id,
                },
            )

    # ── Offres et candidatures ───────────────────────────────────────────────

    def _offers(self) -> dict:
        offers = {}
        for item in demo.OFFERS:
            recruiter = self.profils[item["recruiter"]]
            offer, _ = Offer.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "company": self.companies[item["company"]], "recruiter": recruiter, "title": item["title"],
                    "description": item["description"], "type": item["type"], "contract_duration": item["duration"],
                    "experience_level": item["level"], "budget_min": item["min"], "budget_max": item["max"],
                    "currency": "XOF", "budget_period": item["period"], "country": item["country"], "city": item["city"],
                    "work_mode": item["mode"], "start_date": self.today + timedelta(days=item["start"]),
                    "deadline": self.today + timedelta(days=item["deadline"]) if item["deadline"] is not None else None,
                    "status": item["status"],
                    "published_at": self.now + timedelta(days=item["published"]) if item["published"] is not None else None,
                    "views_count": 20 + 7 * len(item["skills"]) if item["status"] != "draft" else 0,
                    "created_by": recruiter.user_id, "updated_by": recruiter.user_id,
                },
            )
            offer.required_skills.set([self.skills[name] for name in item["skills"]])
            offers[item["key"]] = offer
        return offers

    def _candidatures(self):
        for offer_key, dev_key, status, days_ago, message in demo.CANDIDATURES:
            offer, profil = self.offers[offer_key], self.profils[dev_key]
            sent_at = self.now - timedelta(days=days_ago)
            decided = status != "sent"
            candidature, _ = Candidature.objects.update_or_create(
                offer=offer, profil=profil,
                defaults={
                    "message": message, "status": status,
                    "decided_at": sent_at + timedelta(days=min(2, days_ago)) if decided else None,
                    "created_by": profil.user_id, "updated_by": profil.user_id,
                },
            )
            # created_at est automatique : on le recale pour que le suivi montre des dates échelonnées
            Candidature.objects.filter(pk=candidature.pk).update(created_at=sent_at)
            if status == "accepted":
                self._book_mission(offer, profil)

    def _book_mission(self, offer: Offer, profil: Profil):
        """Période « occupé » d'une candidature acceptée, comme le fait l'acceptation dans l'application."""
        start, end = mission_period(offer.start_date, offer.contract_duration, offer.type)
        Availability.objects.update_or_create(
            profil=profil, source="mission", note=f"Mission : {offer.title}"[:255],
            defaults={"start_date": start, "end_date": end, "status": "busy", "created_by": SYSTEM_ID, "updated_by": SYSTEM_ID},
        )

    def _availabilities(self):
        """Périodes manuelles : recréées à chaque exécution (les dates suivent « aujourd'hui »)."""
        keys = {dev_key for dev_key, *_ in demo.AVAILABILITIES}
        Availability.objects.filter(profil__in=[self.profils[key] for key in keys], source="manual").delete()
        for dev_key, start, end, status, hours, note in demo.AVAILABILITIES:
            profil = self.profils[dev_key]
            Availability.objects.create(
                profil=profil, start_date=self.today + timedelta(days=start), end_date=self.today + timedelta(days=end),
                status=status, hours_per_week=hours, source="manual", note=note,
                created_by=profil.user_id, updated_by=profil.user_id,
            )

    # ── Avis, swipes, connexions ─────────────────────────────────────────────

    def _reviews(self):
        for author_key, target_key, rating, comment, link, public in demo.REVIEWS:
            author, target = self.profils[author_key], self.profils[target_key]
            candidature = (
                Candidature.objects.filter(offer=self.offers[link[0]], profil=self.profils[link[1]]).first() if link else None
            )
            Review.objects.update_or_create(
                author=author, target=target, comment=comment,
                defaults={"rating": rating, "is_public": public, "candidature": candidature,
                          "created_by": author.user_id, "updated_by": author.user_id},
            )

    def _swipes_and_connections(self):
        for author_key, target_key, direction in demo.RECRUIT_SWIPES:
            self._swipe(author_key, target_key, direction, "recruit")
        for author_key, target_key, direction in demo.NETWORK_SWIPES:
            self._swipe(author_key, target_key, direction, "network")
        likes = {
            (author_key, target_key) for author_key, target_key, direction in demo.NETWORK_SWIPES if direction == "like"
        }
        for author_key, target_key in sorted(likes):
            if (target_key, author_key) in likes and author_key < target_key:
                self._connection(author_key, target_key, "matched")
        for first, second in demo.BLOCKED_CONNECTIONS:
            self._connection(first, second, "blocked")

    def _swipe(self, author_key: str, target_key: str, direction: str, context: str):
        author = self.profils[author_key]
        Swipe.objects.update_or_create(
            author=author, target=self.profils[target_key], context=context,
            defaults={"direction": direction, "created_by": author.user_id, "updated_by": author.user_id},
        )

    def _connection(self, first_key: str, second_key: str, status: str):
        low, high = sorted((self.profils[first_key], self.profils[second_key]), key=lambda profil: profil.id)
        Connection.objects.update_or_create(
            profil_a=low, profil_b=high,
            defaults={"status": status, "matched_at": self.now - timedelta(days=3), "created_by": SYSTEM_ID, "updated_by": SYSTEM_ID},
        )

    # ── Résumé ───────────────────────────────────────────────────────────────

    def _report(self):
        counts = {
            "Entreprises": Company.objects.filter(slug__endswith="-demo").count(),
            "Profils": len(self.profils),
            "Compétences de profil": ProfilSkill.objects.filter(profil__in=self.profils.values()).count(),
            "Expériences": Experience.objects.filter(profil__in=self.profils.values()).count(),
            "Prestations": Prestation.objects.filter(profil__in=self.profils.values()).count(),
            "Historique": ProfilHistory.objects.filter(profil__in=self.profils.values()).count(),
            "Disponibilités": Availability.objects.filter(profil__in=self.profils.values()).count(),
            "Offres": len(self.offers),
            "Candidatures": Candidature.objects.filter(offer__in=self.offers.values()).count(),
            "Avis": Review.objects.filter(author__in=self.profils.values()).count(),
            "Swipes": Swipe.objects.filter(author__in=self.profils.values()).count(),
            "Connexions": Connection.objects.filter(profil_a__in=self.profils.values()).count(),
        }
        self.stdout.write(self.style.SUCCESS("Données de démonstration de la marketplace prêtes :"))
        for label, count in counts.items():
            self.stdout.write(f"  {label} : {count}")
        self.stdout.write(f"Comptes (@{demo.DOMAIN}) — mot de passe : {SHOWCASE_PASSWORD}")
