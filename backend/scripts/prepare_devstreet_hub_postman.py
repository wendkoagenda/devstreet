"""Prépare un environnement Postman local ignoré par Git ; ne jamais afficher les jetons."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from app.devstreet_hub.conf import config

data = json.loads(
    (Path(settings.BASE_DIR) / ".local/demo.credentials.json").read_text(
        encoding="utf-8"
    )
)
owner = get_user_model().objects.get(pk=data["aicha-chantier"]["id"])
contributor = get_user_model().objects.get(pk=data["moussa-chantier"]["id"])
values = {
    "base_url": "http://127.0.0.1:18000",
    "owner_access": str(RefreshToken.for_user(owner).access_token),
    "contributor_access": str(RefreshToken.for_user(contributor).access_token),
    "owner_email": owner.email,
    "password": data["password"],
    "contributor_id": str(contributor.pk),
    "webhook_secret": config("GITEA_WEBHOOK_SECRET"),
}
env = {
    "name": "DevStreet Hub local - privé",
    "values": [{"key": k, "value": v, "enabled": True} for k, v in values.items()],
    "_postman_variable_scope": "environment",
}
path = Path(settings.BASE_DIR) / ".local/devstreet_hub.postman_environment.json"
path.write_text(json.dumps(env), encoding="utf-8")
print(
    "Environnement privé écrit dans backend/.local/devstreet_hub.postman_environment.json"
)
