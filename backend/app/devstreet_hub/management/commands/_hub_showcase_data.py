"""Projets Hub showcase — Afrique de l'Ouest, repos + tâches + contributions."""

# Owners / membres = keys des users forum showcase (@showcase.devstreet.local)
TECHNOLOGIES = (
    ("Python", "python"),
    ("Django", "django"),
    ("PostgreSQL", "postgresql"),
    ("React", "react"),
    ("TypeScript", "typescript"),
    ("Flutter", "flutter"),
    ("Go", "go"),
    ("Firebase", "firebase"),
)

PROJECTS = [
    {
        "slug": "teranga-pay-sdk",
        "title": "TerangaPay SDK",
        "owner": "mariam",
        "members": ["kossi", "awa", "ibrahim"],
        "problem": (
            "Unifier Wave, Orange Money et MTN MoMo derrière une API Python/Node "
            "avec idempotence et webhooks testables."
        ),
        "description": (
            "SDK open source pour agrégateurs de paiement en Afrique de l'Ouest. "
            "Focus DX : sandbox locale, retries et documentation FR."
        ),
        "license": "Apache-2.0",
        "status": "published",
        "tech": ("python", "django", "go"),
        "repo_name": "teranga-pay-sdk",
        "sha": "a1b2c3d4e5f6789012345678901234567890abcd",
        "stars": ["awa", "kossi", "ibrahim", "fatou", "moussa"],
        "tasks": [
            {
                "title": "Adapter Wave : signatures webhook",
                "description": "Valider la signature HMAC et documenter les cas d'erreur 4xx.",
                "status": "open",
                "criteria": ["Tests unitaires signature", "Doc FR dans /docs/wave.md"],
            },
            {
                "title": "Sandbox Docker Compose",
                "description": "Stack locale mock des 3 PSP pour les tutoriels.",
                "status": "open",
                "criteria": ["docker compose up démarre en < 60s", "README quickstart"],
            },
        ],
        "contributions": [
            {
                "task_title": "Adapter Wave : signatures webhook",
                "author": "kossi",
                "summary": "Ajout du validateur HMAC + 6 tests pytest.",
                "pr": 12,
                "sha": "b2c3d4e5f6789012345678901234567890abcde1",
                "status": "accepted",
                "reviewer": "mariam",
                "note": "Nickel, merge après squash.",
            },
        ],
    },
    {
        "slug": "agritrack-sahel",
        "title": "AgriTrack Sahel",
        "owner": "binta",
        "members": ["aicha", "yao", "moussa"],
        "problem": (
            "Les coopératives n'ont pas de vue fiable des cours céréaliers "
            "ni de saisie terrain hors-ligne."
        ),
        "description": (
            "Dashboard data + app Flutter hors-ligne pour agents de terrain. "
            "Sync différée et alertes prix."
        ),
        "license": "MIT",
        "status": "published",
        "tech": ("django", "react", "postgresql", "flutter", "firebase"),
        "repo_name": "agritrack-sahel",
        "sha": "c3d4e5f6789012345678901234567890abcdef12",
        "stars": ["aicha", "mariam", "yao", "nadia"],
        "tasks": [
            {
                "title": "Sync Drift → API (file d'attente)",
                "description": "Flush des saisies avec idempotency key UUID.",
                "status": "open",
                "criteria": ["Retry sans doublon", "Indicateur sync UI"],
            },
            {
                "title": "Vue matérialisée prix journaliers",
                "description": "Postgres : agrégats par marché / céréale.",
                "status": "open",
                "criteria": ["Migration + refresh job", "Endpoint read-only"],
            },
        ],
        "contributions": [
            {
                "task_title": "Vue matérialisée prix journaliers",
                "author": "aicha",
                "summary": "Migration matview + commande refresh_prices.",
                "pr": 7,
                "sha": "d4e5f6789012345678901234567890abcdef1234",
                "status": "submitted",
                "reviewer": None,
                "note": "",
            },
        ],
    },
    {
        "slug": "sahel-ui",
        "title": "Sahel UI",
        "owner": "moussa",
        "members": ["awa", "nadia", "ibrahim"],
        "problem": (
            "Les design systems importés ignorent le français, "
            "l'accessibilité et les contraintes mobile 3G."
        ),
        "description": (
            "Bibliothèque React/TypeScript : tokens HSL, composants WCAG AA, "
            "labels FR par défaut."
        ),
        "license": "MIT",
        "status": "published",
        "tech": ("react", "typescript"),
        "repo_name": "sahel-ui",
        "sha": "e5f6789012345678901234567890abcdef123456",
        "stars": ["awa", "nadia", "fatou", "mariam"],
        "tasks": [
            {
                "title": "Badge a11y dark mode",
                "description": "Corriger le contraste du badge Disponibilité.",
                "status": "open",
                "criteria": ["Contrast ratio ≥ 4.5", "Storybook story"],
            },
        ],
        "contributions": [],
    },
    {
        "slug": "gestion-scolaire",
        "title": "GestionScolaire",
        "owner": "salif",
        "members": ["ibrahim", "moussa", "kossi"],
        "problem": (
            "Les écoles privées du Burkina gèrent encore notes et frais "
            "sur Excel et WhatsApp."
        ),
        "description": (
            "Django + React : inscriptions, notes, frais, SMS parents. "
            "i18n FR / mooré / dioula en roadmap."
        ),
        "license": "MIT",
        "status": "published",
        "tech": ("python", "django", "react", "postgresql"),
        "repo_name": "gestion-scolaire",
        "sha": "f6789012345678901234567890abcdef12345678",
        "stars": ["ibrahim", "nadia", "aicha"],
        "tasks": [
            {
                "title": "Doc install Windows",
                "description": "Guide pas à pas venv + Postgres + frontend.",
                "status": "open",
                "criteria": ["docs/install-windows.md", "Captures écran"],
            },
            {
                "title": "Smoke test auth",
                "description": "Pytest login / refresh JWT.",
                "status": "draft",
                "criteria": ["2 tests verts en CI"],
            },
        ],
        "contributions": [
            {
                "task_title": "Doc install Windows",
                "author": "ibrahim",
                "summary": "Premier jet de la doc + scripts PowerShell.",
                "pr": 3,
                "sha": "789012345678901234567890abcdef1234567890",
                "status": "submitted",
                "reviewer": None,
                "note": "",
            },
        ],
    },
    {
        "slug": "resto-livraison",
        "title": "Resto Livraison",
        "owner": "koffi",
        "members": ["yao", "awa"],
        "problem": (
            "Resto Express a besoin d'une app livreur avec suivi temps réel "
            "et paiement Mobile Money à Lomé."
        ),
        "description": "Prototype Flutter + API Node (démo Hub, pas encore public).",
        "license": "MIT",
        "status": "draft",
        "tech": ("flutter", "firebase"),
        "repo_name": "resto-livraison",
        "sha": "",
        "stars": [],
        "tasks": [
            {
                "title": "Carte livreur (géoloc)",
                "description": "Afficher la position live sur la commande.",
                "status": "draft",
                "criteria": ["Màj < 5s", "Mode économie batterie"],
            },
        ],
        "contributions": [],
    },
]
