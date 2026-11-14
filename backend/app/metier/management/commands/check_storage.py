"""Vérifie que le stockage de fichiers actif fonctionne (disque local ou S3/MinIO).

    python manage.py check_storage

Écrit un petit fichier de test, vérifie qu'il existe, le relit, affiche son URL, puis le supprime.
Code de sortie non nul au premier échec.
"""
import uuid

from django.core.management.base import BaseCommand, CommandError

from app.metier.services.storage_service import get_storage_service

_CONTENU = b"check_storage"


class Command(BaseCommand):
    help = "Écrit, relit et supprime un fichier de test sur le stockage actif (USE_S3)."

    def handle(self, *args, **options):
        try:
            storage = get_storage_service()
        except Exception as exc:
            raise CommandError(f"Initialisation du stockage impossible : {exc}") from exc

        info = storage.get_storage_info()
        self.stdout.write("Stockage actif :")
        for key, value in info.items():
            self.stdout.write(f"  {key} : {value}")

        name = f"check_storage/{uuid.uuid4().hex}.txt"
        saved = None
        try:
            saved = self._step("écriture", lambda: storage.save(name, _CONTENU))
            self._step("présence", lambda: self._require(storage.exists(saved), "le fichier n'existe pas après l'écriture"))
            self._step("lecture", lambda: self._require(self._read(storage, saved) == _CONTENU, "contenu relu différent du contenu écrit"))
            self.stdout.write(f"  URL renvoyée à l'API : {storage.url(saved)}")
        finally:
            if saved:
                self._step("suppression", lambda: self._require(storage.delete(saved), "le fichier n'a pas été supprimé"))

        self.stdout.write(self.style.SUCCESS("Stockage opérationnel (écriture, lecture, suppression)."))

    def _step(self, label, action):
        try:
            result = action()
        except Exception as exc:
            raise CommandError(f"Échec de l'étape « {label} » : {type(exc).__name__}: {exc}") from exc
        self.stdout.write(self.style.SUCCESS(f"  OK  {label}"))
        return result

    @staticmethod
    def _require(condition, message):
        if not condition:
            raise RuntimeError(message)

    @staticmethod
    def _read(storage, name):
        handle = storage.open(name, 'rb')
        try:
            return handle.read()
        finally:
            handle.close()
