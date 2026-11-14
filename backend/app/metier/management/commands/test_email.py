"""Envoie un e-mail de test pour vérifier la configuration SMTP.

    python manage.py test_email destinataire@exemple.com
"""
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = "Envoie un e-mail de test au destinataire donné (vérifie EMAIL_BACKEND, EMAIL_HOST*, DEFAULT_FROM_EMAIL)."

    def add_arguments(self, parser):
        parser.add_argument('destinataire', help="Adresse e-mail qui reçoit le message de test")

    def handle(self, *args, **options):
        destinataire = options['destinataire']
        try:
            validate_email(destinataire)
        except ValidationError as exc:
            raise CommandError(f"Adresse e-mail invalide : {destinataire}") from exc

        self.stdout.write(f"Moteur d'envoi : {settings.EMAIL_BACKEND}")
        if settings.EMAIL_HOST:
            self.stdout.write(f"Serveur SMTP : {settings.EMAIL_HOST}:{settings.EMAIL_PORT} (STARTTLS), "
                              f"compte {settings.EMAIL_HOST_USER}")
        else:
            self.stdout.write(self.style.WARNING(
                "Aucun serveur SMTP configuré : l'e-mail s'affiche dans la console, il n'est pas envoyé."
            ))
        self.stdout.write(f"Expéditeur : {settings.DEFAULT_FROM_EMAIL}")

        try:
            send_mail(
                subject="Test d'envoi d'e-mail",
                message="Ce message confirme que la configuration SMTP du backend fonctionne.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[destinataire],
                fail_silently=False,
            )
        except Exception as exc:
            raise CommandError(
                f"Échec de l'envoi ({type(exc).__name__}) : {exc}. "
                "Vérifier EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD et que le serveur accepte le port 587 (STARTTLS)."
            ) from exc

        self.stdout.write(self.style.SUCCESS(f"E-mail de test remis au serveur d'envoi pour {destinataire}."))
