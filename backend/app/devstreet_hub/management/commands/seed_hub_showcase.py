"""Peuple le Hub : technos, projets, repos, tâches, contributions, stars.

Réutilise les comptes forum showcase (@showcase.devstreet.local).
Lancez d'abord seed_forum_showcase (ou seed_showcase).

Usage :
  python manage.py seed_hub_showcase
  python manage.py seed_hub_showcase --allow-non-debug
"""
from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from app.core.models import Role
from app.devstreet_hub.models import (
    Contribution,
    ContributionTask,
    Project,
    ProjectMember,
    Repository,
    Star,
    Technology,
)

from app.communaute.management.commands import _forum_showcase_data as forum_data
from . import _hub_showcase_data as data

User = get_user_model()
FORUM_DOMAIN = forum_data.DOMAIN


class Command(BaseCommand):
    help = "Seed Hub showcase : projets, repos, tâches, contributions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--allow-non-debug",
            action="store_true",
            help="Autorise l'exécution quand DEBUG=False (prod/staging vide).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG and not options["allow_non_debug"]:
            raise CommandError(
                "DEBUG=False : passe --allow-non-debug pour peupler une instance vide."
            )

        call_command("init_devstreet_hub")
        users = self._users()
        if len(users) < 5:
            raise CommandError(
                f"Comptes showcase introuvables (@{FORUM_DOMAIN}). "
                "Lance d'abord : python manage.py seed_forum_showcase"
            )

        developer = Role.objects.get(name="DevStreet Hub Developer")
        for user in users.values():
            user.roles.add(developer)

        with transaction.atomic():
            techs = self._technologies(users)
            n_projects = self._projects(users, techs)

        self.stdout.write(
            self.style.SUCCESS(
                f"Hub showcase OK — {len(techs)} technos, {n_projects} projets "
                f"(repos, tâches, contributions, stars)"
            )
        )

    def _users(self) -> dict[str, User]:
        users = {}
        for person in forum_data.USERS:
            email = f"{person['key']}@{FORUM_DOMAIN}"
            user = User.objects.filter(email=email).first()
            if user is not None:
                users[person["key"]] = user
        return users

    def _technologies(self, users: dict[str, User]) -> dict[str, Technology]:
        creator = users.get("mariam") or next(iter(users.values()))
        techs = {}
        for label, slug in data.TECHNOLOGIES:
            tech, _ = Technology.objects.get_or_create(
                slug=slug,
                defaults={
                    "label": label,
                    "created_by": creator.id,
                    "updated_by": creator.id,
                },
            )
            techs[slug] = tech
        return techs

    def _projects(self, users: dict[str, User], techs: dict[str, Technology]) -> int:
        count = 0
        now = timezone.now()
        for spec in data.PROJECTS:
            owner = users.get(spec["owner"])
            if not owner:
                continue
            project, _ = Project.objects.update_or_create(
                slug=spec["slug"],
                defaults={
                    "owner": owner,
                    "title": spec["title"],
                    "problem": spec["problem"],
                    "description": spec["description"],
                    "declared_license": spec["license"],
                    "status": spec["status"],
                    "created_by": owner.id,
                    "updated_by": owner.id,
                },
            )
            project.technologies.set([techs[s] for s in spec["tech"] if s in techs])

            ProjectMember.objects.get_or_create(
                project=project,
                user=owner,
                defaults={"role": "maintainer"},
            )
            for member_key in spec.get("members", []):
                member = users.get(member_key)
                if not member or member.id == owner.id:
                    continue
                ProjectMember.objects.get_or_create(
                    project=project,
                    user=member,
                    defaults={"role": "contributor"},
                )

            repo, _ = Repository.objects.get_or_create(
                project=project,
                defaults={"name": spec["repo_name"]},
            )
            repo.name = spec["repo_name"]
            repo.namespace = owner.username
            repo.default_branch = "main"
            if spec["status"] == "published":
                repo.status = "ready"
                repo.current_sha = spec.get("sha") or repo.current_sha
            else:
                repo.status = "pending"
            repo.save()

            for star_key in spec.get("stars", []):
                star_user = users.get(star_key)
                if not star_user:
                    continue
                Star.objects.get_or_create(project=project, user=star_user)

            tasks_by_title: dict[str, ContributionTask] = {}
            for task_spec in spec.get("tasks", []):
                task, _ = ContributionTask.objects.update_or_create(
                    project=project,
                    title=task_spec["title"],
                    defaults={
                        "description": task_spec["description"],
                        "status": task_spec["status"],
                        "acceptance_criteria": task_spec.get("criteria", []),
                        "created_by": owner.id,
                        "updated_by": owner.id,
                    },
                )
                tasks_by_title[task.title] = task

            for contrib_spec in spec.get("contributions", []):
                task = tasks_by_title.get(contrib_spec["task_title"])
                author = users.get(contrib_spec["author"])
                if not task or not author:
                    continue
                status = contrib_spec["status"]
                reviewer = (
                    users.get(contrib_spec["reviewer"])
                    if contrib_spec.get("reviewer")
                    else None
                )
                defaults = {
                    "summary": contrib_spec["summary"],
                    "pull_request_number": contrib_spec.get("pr"),
                    "artifact_sha": contrib_spec.get("sha", ""),
                    "status": status,
                    "review_note": contrib_spec.get("note", ""),
                }
                if status in ("accepted", "rejected") and reviewer:
                    defaults["reviewed_by"] = reviewer
                    defaults["reviewed_at"] = now
                else:
                    defaults["reviewed_by"] = None
                    defaults["reviewed_at"] = None
                    defaults["review_note"] = ""
                    defaults["status"] = "submitted"

                existing = Contribution.objects.filter(
                    task=task, author=author, summary=contrib_spec["summary"]
                ).first()
                if existing:
                    for field, value in defaults.items():
                        setattr(existing, field, value)
                    existing.save()
                else:
                    Contribution.objects.create(task=task, author=author, **defaults)

            count += 1
            self.stdout.write(f"  Projet {project.slug} ({project.status})")
        return count
