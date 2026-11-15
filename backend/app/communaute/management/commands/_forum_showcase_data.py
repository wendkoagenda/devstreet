"""Jeu de données showcase forum — personas ouest-africains, communautés et chaînes évocatrices.

Destiné à peupler une instance vide (staging / prod vide) avec un contenu crédible.
Les e-mails utilisent le domaine DEMO_DOMAIN ; les mots de passe sont générés hors dépôt.
"""

DOMAIN = "showcase.devstreet.local"

# ── Membres (au moins 12) ───────────────────────────────────────────────────
USERS = [
    {
        "key": "awa",
        "username": "awa.kone",
        "first": "Awa",
        "last": "Koné",
        "city": "Abidjan",
        "headline": "Full stack React · Node",
    },
    {
        "key": "yao",
        "username": "yao.mensah",
        "first": "Yao",
        "last": "Mensah",
        "city": "Lomé",
        "headline": "Mobile Flutter",
    },
    {
        "key": "mariam",
        "username": "mariam.diop",
        "first": "Mariam",
        "last": "Diop",
        "city": "Dakar",
        "headline": "Django · API paiement",
    },
    {
        "key": "kossi",
        "username": "kossi.adjovi",
        "first": "Kossi",
        "last": "Adjovi",
        "city": "Cotonou",
        "headline": "DevOps · GCP",
    },
    {
        "key": "aicha",
        "username": "aicha.traore",
        "first": "Aïcha",
        "last": "Traoré",
        "city": "Abidjan",
        "headline": "Data · Python",
    },
    {
        "key": "moussa",
        "username": "moussa.boureima",
        "first": "Moussa",
        "last": "Boureima",
        "city": "Niamey",
        "headline": "Front React · TypeScript",
    },
    {
        "key": "ibrahim",
        "username": "ibrahim.ouedraogo",
        "first": "Ibrahim",
        "last": "Ouédraogo",
        "city": "Ouagadougou",
        "headline": "Junior Django · React",
    },
    {
        "key": "binta",
        "username": "binta.ndiaye",
        "first": "Binta",
        "last": "Ndiaye",
        "city": "Dakar",
        "headline": "Product · AgriConnect",
    },
    {
        "key": "fatou",
        "username": "fatou.sow",
        "first": "Fatou",
        "last": "Sow",
        "city": "Ouagadougou",
        "headline": "Recrutement tech · Faso Pay",
    },
    {
        "key": "koffi",
        "username": "koffi.agbodjan",
        "first": "Koffi",
        "last": "Agbodjan",
        "city": "Lomé",
        "headline": "Ops produit · Resto Express",
    },
    {
        "key": "nadia",
        "username": "nadia.kabore",
        "first": "Nadia",
        "last": "Kaboré",
        "city": "Ouagadougou",
        "headline": "Mobile Flutter · mentorship",
    },
    {
        "key": "salif",
        "username": "salif.tapsoba",
        "first": "Salif",
        "last": "Tapsoba",
        "city": "Bobo-Dioulasso",
        "headline": "Back-end Django · open source",
    },
]

# ── Communautés ─────────────────────────────────────────────────────────────
# key unique, creator = key user, members = keys (creator inclus auto)
COMMUNITIES = [
    {
        "key": "teranga-dev",
        "nom": "Teranga Dev",
        "description": (
            "Communauté bienveillante des développeurs francophones d'Afrique de l'Ouest. "
            "Questions, retours d'expérience, entraide sans ego."
        ),
        "creator": "mariam",
        "members": [
            "awa", "yao", "mariam", "kossi", "aicha", "moussa",
            "ibrahim", "binta", "nadia", "salif",
        ],
    },
    {
        "key": "baobab-js",
        "nom": "Baobab.js",
        "description": (
            "React, TypeScript, Node et l'écosystème front. "
            "On parle perf, design system et bundlers — en français."
        ),
        "creator": "awa",
        "members": ["awa", "moussa", "nadia", "ibrahim", "yao", "koffi"],
    },
    {
        "key": "django-sahel",
        "nom": "Django Sahel",
        "description": (
            "DRF, ORM, Celery, déploiements Django en conditions réelles "
            "(latence, Mobile Money, multi-pays)."
        ),
        "creator": "mariam",
        "members": ["mariam", "salif", "ibrahim", "kossi", "aicha", "fatou"],
    },
    {
        "key": "mobile-golfe",
        "nom": "Mobile Golfe",
        "description": (
            "Flutter & React Native autour du golfe de Guinée : "
            "hors-ligne, géoloc livreurs, wallets Wave / MoMo / Orange Money."
        ),
        "creator": "yao",
        "members": ["yao", "awa", "nadia", "kossi", "koffi"],
    },
    {
        "key": "data-savane",
        "nom": "Data Savane",
        "description": (
            "Analyse de données, dashboards et ML léger pour PME, "
            "coopératives et administrations locales."
        ),
        "creator": "aicha",
        "members": ["aicha", "moussa", "ibrahim", "binta", "salif"],
    },
    {
        "key": "devops-harmattan",
        "nom": "DevOps Harmattan",
        "description": (
            "CI/CD, conteneurs, observabilité et coûts cloud — "
            "adaptés aux équipes petites et aux contraintes réseau."
        ),
        "creator": "kossi",
        "members": ["kossi", "mariam", "awa", "fatou", "salif"],
    },
    {
        "key": "product-wakanda",
        "nom": "Product & Growth AF",
        "description": (
            "Product managers, founders et tech leads : discovery, pricing, "
            "go-to-market en Afrique francophone."
        ),
        "creator": "binta",
        "members": ["binta", "fatou", "koffi", "mariam", "awa"],
    },
    {
        "key": "open-source-afrique",
        "nom": "Open Source Afrique",
        "description": (
            "Contributions, licences, mantainership et projets "
            "open source ancrés dans nos contextes locaux."
        ),
        "creator": "salif",
        "members": ["salif", "ibrahim", "kossi", "moussa", "nadia", "aicha"],
    },
    {
        "key": "freelance-uoa",
        "nom": "Freelance UEMOA",
        "description": (
            "Missions, TJM, contrats et relation client pour freelances "
            "basés dans l'espace UEMOA (et remote vers l'Europe)."
        ),
        "creator": "awa",
        "members": ["awa", "yao", "nadia", "kossi", "moussa", "fatou"],
    },
    {
        "key": "women-in-tech-af",
        "nom": "Women in Tech AF",
        "description": (
            "Espace safe pour les femmes en tech : mentorat, "
            "offres, conférences et partage de parcours."
        ),
        "creator": "nadia",
        "members": ["nadia", "awa", "mariam", "aicha", "binta", "fatou"],
    },
]

# ── Chaînes (annonces / éditorial) ──────────────────────────────────────────
CHANNELS = [
    {
        "key": "annonces-devstreet",
        "nom": "Annonces DevStreet",
        "description": "Nouveautés produit, maintenance et messages officiels de l'équipe DevStreet.",
        "creator": "fatou",
        "members": [u["key"] for u in USERS],
        "commentaires_ouverts": True,
    },
    {
        "key": "jobs-afrique-ouest",
        "nom": "Jobs Afrique de l'Ouest",
        "description": "Missions, CDI, stages et appels à freelances — stack tech, remote ou hybride.",
        "creator": "fatou",
        "members": ["fatou", "koffi", "binta", "awa", "mariam", "yao", "ibrahim", "nadia"],
        "commentaires_ouverts": True,
    },
    {
        "key": "tips-quotidien",
        "nom": "Tip du jour",
        "description": "Une astuce courte chaque jour : Git, SQL, accessibilité, perf, soft skills.",
        "creator": "moussa",
        "members": [u["key"] for u in USERS],
        "commentaires_ouverts": True,
    },
    {
        "key": "meetups-calendrier",
        "nom": "Meetups & calendrier",
        "description": "Événements en présentiel (Dakar, Abidjan, Lomé, Ouaga, Cotonou) et lives en ligne.",
        "creator": "binta",
        "members": ["binta", "awa", "yao", "mariam", "kossi", "nadia", "ibrahim"],
        "commentaires_ouverts": True,
    },
    {
        "key": "release-notes",
        "nom": "Release notes",
        "description": "Changelog DevStreet : forum, marketplace et Hub — ce qui change vraiment pour vous.",
        "creator": "kossi",
        "members": [u["key"] for u in USERS],
        # Ouverts : les membres peuvent laisser des retours sur les notes de version.
        "commentaires_ouverts": True,
    },
]

# ── Publications curated (fil général + quelques chaînes) ───────────────────
# auteur = key, espace = key communauté/chaîne ou None (fil général)
PUBLICATIONS = [
    {
        "auteur": "mariam",
        "espace": None,
        "type": "DISCUSSION",
        "titre": "Comment structurer une API Django multi-pays (XOF, TVA, fuseaux) ?",
        "description": (
            "On gère SN / BF / CI avec des règles fiscales différentes. "
            "Aujourd'hui on a un service « billing » monolithe. Vous préférez "
            "des strategy par pays, ou un moteur de règles versionné en base ? "
            "Je cherche des retours concrets (pas de théorie pure)."
        ),
    },
    {
        "auteur": "awa",
        "espace": None,
        "type": "DISCUSSION",
        "titre": "RTK Query vs TanStack Query en 2026 — votre choix en prod ?",
        "description": (
            "Sur DevStreet on est sur RTK Query. Pour un nouveau module marketplace, "
            "est-ce que vous resteriez dans Redux ou vous passeriez à TanStack Query "
            "pour le server-state ? Critères : cache, invalidation, DX TypeScript."
        ),
    },
    {
        "auteur": "kossi",
        "espace": None,
        "type": "DISCUSSION",
        "titre": "CI trop lente sur runners partagés : vos leviers qui marchent vraiment",
        "description": (
            "Pipeline Django + Vite qui passe de 4 à 18 minutes dès qu'on a du traffic "
            "sur le runner. On a déjà le cache npm/pip. Docker layer caching ? "
            "Matrix plus fine ? Self-hosted à Abidjan ?"
        ),
    },
    {
        "auteur": "yao",
        "espace": None,
        "type": "ENTRAIDE",
        "titre": "Flutter : sync hors-ligne + file d'attente Mobile Money",
        "description": (
            "App terrain agri : saisie sans réseau, puis flush quand le signal revient. "
            "Le paiement Wave parfois échoue après un retry. Vous stockez l'idempotency key "
            "côté device ou côté API ?"
        ),
    },
    {
        "auteur": "ibrahim",
        "espace": None,
        "type": "ENTRAIDE",
        "titre": "CORS Vite → Django en local : préflight OPTIONS 403",
        "description": (
            "Vite sur :5173, Django sur :8000. Les GET passent, les POST avec JWT non. "
            "J'ai déjà `CORS_ALLOW_CREDENTIALS` et l'origine. Un détail SimpleJWT "
            "ou CSRF que je rate ?"
        ),
    },
    {
        "auteur": "aicha",
        "espace": None,
        "type": "DISCUSSION",
        "titre": "Dashboard prix céréales : Pandas en batch ou SQL matérialisé ?",
        "description": (
            "Volume ~2M lignes / an. Les coopératives veulent des courbes journalières "
            "et des alertes. On hésite entre un job Pandas nocturne et des vues "
            "matérialisées Postgres. Retours bienvenus."
        ),
    },
    {
        "auteur": "salif",
        "espace": None,
        "type": "APPLICATION",
        "titre": "GestionScolaire — open source pour écoles privées",
        "description": (
            "Django + React : inscriptions, notes, frais de scolarité, SMS parents. "
            "On cherche des contributeurs (docs FR, tests, i18n mooré/dioula). "
            "Repo et roadmap dans le premier commentaire."
        ),
        "lien_app": "https://github.com/example/gestion-scolaire",
        "plateforme_app": "WEB",
    },
    {
        "auteur": "moussa",
        "espace": None,
        "type": "APPLICATION",
        "titre": "Sahel UI — composants React accessibles en français",
        "description": (
            "Bibliothèque de composants (inputs, tables, toasts) avec labels FR par défaut, "
            "contrastes WCAG AA et tokens adaptés au dark mode. Feedback design system bienvenu."
        ),
        "lien_app": "https://github.com/example/sahel-ui",
        "plateforme_app": "WEB",
    },
    {
        "auteur": "nadia",
        "espace": "women-in-tech-af",
        "type": "DISCUSSION",
        "titre": "Session mentorat samedi : préparer un portfolio remote",
        "description": (
            "Samedi 10h GMT : on revoit 4 portfolios (anonymisés) et on travaille "
            "accroche + preuves projets. Places limitées — commentez avec votre stack."
        ),
    },
    {
        "auteur": "fatou",
        "espace": "jobs-afrique-ouest",
        "type": "DISCUSSION",
        "titre": "Faso Pay recrute — Front React CDI (remote UEMOA)",
        "description": (
            "Tableau de bord marchands, TypeScript strict, tests et accessibilité. "
            "Postulez via la marketplace DevStreet (offre « Front-end React, CDI ») "
            "ou écrivez-moi en MP avec votre GitHub."
        ),
    },
    {
        "auteur": "koffi",
        "espace": "jobs-afrique-ouest",
        "type": "DISCUSSION",
        "titre": "Resto Express — mission React Native livraison (Lomé / hybride)",
        "description": (
            "3 mois : commande, suivi livreur, Wave / MoMo. "
            "Idéal si vous avez déjà touché à la géoloc temps réel. "
            "Offre ouverte sur la marketplace."
        ),
    },
    {
        "auteur": "binta",
        "espace": "meetups-calendrier",
        "type": "DISCUSSION",
        "titre": "Meetup Dakar — AgriTech & data (jeudi 18h30, Plateau)",
        "description": (
            "Deux talks courts : saisie terrain hors-ligne, et dashboards pour coopératives. "
            "Puis networking. RSVP en commentaire (places ~40)."
        ),
    },
    {
        "auteur": "moussa",
        "espace": "tips-quotidien",
        "type": "DISCUSSION",
        "titre": "Tip : `git switch -` pour revenir à la branche précédente",
        "description": (
            "Équivalent de `cd -`. Utile quand vous alternez feature / review PR. "
            "Fonctionne aussi avec `git merge -` dans certains workflows."
        ),
    },
    {
        "auteur": "kossi",
        "espace": "release-notes",
        "type": "DISCUSSION",
        "titre": "DevStreet — notes de version (forum · marketplace · Hub)",
        "description": (
            "• Fil forum : onglets Pour vous / Abonnements\n"
            "• Marketplace : annuaire talents + vivier recruteur\n"
            "• Hub : lien « Demander de l'aide » → discussion forum\n"
            "Détails et captures dans la doc interne."
        ),
    },
    {
        "auteur": "awa",
        "espace": "baobab-js",
        "type": "DISCUSSION",
        "titre": "Design tokens : HSL sémantiques vs palette figée",
        "description": (
            "On migre vers des variables `bg-muted` / `text-destructive` plutôt que "
            "des hex en dur. Qui a déjà industrialisé ça avec Tailwind 4 ?"
        ),
    },
    {
        "auteur": "salif",
        "espace": "django-sahel",
        "type": "ENTRAIDE",
        "titre": "Select_related vs prefetch sur ParticipationEspace + Publication",
        "description": (
            "Liste des pubs d'une communauté : N+1 sur auteur et sur tags. "
            "Vous prefetch_related('tags') systématiquement, ou dénormalisez un cache ?"
        ),
    },
]

# ── Messages de groupe (par communauté) ─────────────────────────────────────
GROUP_MESSAGES = {
    "teranga-dev": [
        ("mariam", "Bienvenue dans Teranga Dev 👋 Présentez-vous en une ligne : ville + stack."),
        ("awa", "Awa · Abidjan · React/Node. Contente d'être là."),
        ("yao", "Yao · Lomé · Flutter. Je passe souvent sur les threads mobile."),
        ("ibrahim", "Ibrahim · Ouaga · junior Django/React. Je lis beaucoup, j'ose peu — ça va changer."),
        ("kossi", "Si vous déployez sur un VPS, partagez votre stack monitoring (même légère)."),
    ],
    "baobab-js": [
        ("awa", "Thread du jour : comment vous organisez vos features slices ?"),
        ("moussa", "Un dossier par domaine + api RTK + schema Zod. Sinon ça part en spaghetti."),
        ("nadia", "Pareil côté mobile : modules feature, pas de god-component."),
    ],
    "django-sahel": [
        ("mariam", "On mutualise les retours d'expérience multi-devises ici."),
        ("salif", "J'ai un snippet d'idempotency key pour les webhooks Wave si ça intéresse."),
        ("ibrahim", "Intéressé — je galère justement sur les retries."),
    ],
    "women-in-tech-af": [
        ("nadia", "Rappel mentorat samedi. Ambiance bienveillante, caméra optionnelle."),
        ("aicha", "Je peux co-animer la partie « raconter son projet data »."),
        ("binta", "Et moi un retour product : comment pitcher une agri-tech à un investisseur local."),
    ],
}

# ── Engagement : likes pubs (titre → auteurs qui like) ───────────────────────
PUBLICATION_LIKES = {
    "Comment structurer une API Django multi-pays (XOF, TVA, fuseaux) ?": [
        "awa", "salif", "ibrahim", "kossi", "fatou",
    ],
    "RTK Query vs TanStack Query en 2026 — votre choix en prod ?": [
        "moussa", "nadia", "kossi", "ibrahim",
    ],
    "CI trop lente sur runners partagés : vos leviers qui marchent vraiment": [
        "mariam", "awa", "salif",
    ],
    "Flutter : sync hors-ligne + file d'attente Mobile Money": [
        "awa", "nadia", "kossi", "koffi", "binta",
    ],
    "GestionScolaire — open source pour écoles privées": [
        "ibrahim", "moussa", "aicha", "nadia", "mariam",
    ],
    "Faso Pay recrute — Front React CDI (remote UEMOA)": [
        "moussa", "awa", "ibrahim",
    ],
}

# ── Commentaires + réponses (titre pub, auteur, texte, nature, replies[]) ───
# replies : (auteur_key, texte)
COMMENTS = [
    {
        "publication": "Comment structurer une API Django multi-pays (XOF, TVA, fuseaux) ?",
        "auteur": "salif",
        "nature": "REPONSE_TECHNIQUE",
        "texte": (
            "Chez nous : un `TaxRule` versionné (pays, date d'effet, taux) + "
            "un service qui résout la règle au moment de la facture. "
            "Évite les if/elif qui explosent."
        ),
        "likes": ["mariam", "awa", "ibrahim"],
        "replies": [
            (
                "mariam",
                "Exactement le genre de modèle que je visais. Tu versionnes en table ou en JSON ?",
            ),
            (
                "salif",
                "Table dédiée + migration de données. Le JSON c'est trop opaque en audit.",
            ),
        ],
    },
    {
        "publication": "Comment structurer une API Django multi-pays (XOF, TVA, fuseaux) ?",
        "auteur": "kossi",
        "nature": "COMMENTAIRE",
        "texte": "Pense aussi aux fuseaux pour les cut-off de paiement Mobile Money (souvent minuit local).",
        "likes": ["mariam", "fatou"],
        "replies": [],
    },
    {
        "publication": "RTK Query vs TanStack Query en 2026 — votre choix en prod ?",
        "auteur": "moussa",
        "nature": "COMMENTAIRE",
        "texte": (
            "TanStack Query pour le server-state pur, Redux seulement pour l'UI locale. "
            "Moins de boilerplate, invalidation plus lisible."
        ),
        "likes": ["awa", "nadia"],
        "replies": [
            ("awa", "On est déjà très couplés à RTK — le coût de migration me fait hésiter."),
            ("moussa", "Tu peux migrer module par module : c'est ce qu'on a fait sur Sahel UI."),
        ],
    },
    {
        "publication": "Flutter : sync hors-ligne + file d'attente Mobile Money",
        "auteur": "kossi",
        "nature": "REPONSE_TECHNIQUE",
        "texte": (
            "Idempotency key générée côté device (UUID v4), stockée en Drift, "
            "renvoyée à chaque retry. L'API refuse les doublons 24h."
        ),
        "likes": ["yao", "awa", "nadia"],
        "replies": [
            ("yao", "Merci — je bascule là-dessus cette semaine."),
        ],
    },
    {
        "publication": "CORS Vite → Django en local : préflight OPTIONS 403",
        "auteur": "awa",
        "nature": "REPONSE_TECHNIQUE",
        "texte": (
            "Vérifie que `OPTIONS` n'est pas bloqué par une permission DRF globale. "
            "Et que l'origine exacte `http://localhost:5173` est dans CORS_ALLOWED_ORIGINS."
        ),
        "likes": ["ibrahim", "moussa"],
        "replies": [
            ("ibrahim", "C'était ça — j'avais mis 127.0.0.1 au lieu de localhost. Merci !"),
        ],
    },
    {
        "publication": "GestionScolaire — open source pour écoles privées",
        "auteur": "ibrahim",
        "nature": "COMMENTAIRE",
        "texte": "Je prends la doc d'install Windows + un premier test smoke sur l'auth.",
        "likes": ["salif", "nadia"],
        "replies": [
            ("salif", "Parfait — issue #12 créée, je t'assigne."),
        ],
    },
    {
        "publication": "Sahel UI — composants React accessibles en français",
        "auteur": "nadia",
        "nature": "RETOUR_APP",
        "texte": "Les contrastes du badge « Dispo » en dark mode passent juste — je peux envoyer une PR tokens.",
        "likes": ["moussa", "awa"],
        "replies": [
            ("moussa", "PR bienvenue, branche `tokens/a11y-badge`."),
        ],
    },
    {
        "publication": "Faso Pay recrute — Front React CDI (remote UEMOA)",
        "auteur": "moussa",
        "nature": "COMMENTAIRE",
        "texte": "Candidature envoyée via la marketplace — portfolio Sahel UI en pièce jointe.",
        "likes": ["fatou"],
        "replies": [
            ("fatou", "Reçu, on shortlist jeudi."),
        ],
    },
    {
        "publication": "Session mentorat samedi : préparer un portfolio remote",
        "auteur": "aicha",
        "nature": "COMMENTAIRE",
        "texte": "Je m'inscris — stack data Python / Power BI.",
        "likes": ["nadia", "binta"],
        "replies": [],
    },
    {
        "publication": "Meetup Dakar — AgriTech & data (jeudi 18h30, Plateau)",
        "auteur": "mariam",
        "nature": "COMMENTAIRE",
        "texte": "RSVP +1 — je peux aider pour le wifi / projecteur.",
        "likes": ["binta"],
        "replies": [
            ("binta", "Top, on se parle en MP pour la logistique."),
        ],
    },
]

# ── Suivis (suiveur → suivi) ────────────────────────────────────────────────
FOLLOWS = [
    ("ibrahim", "salif"),
    ("ibrahim", "mariam"),
    ("ibrahim", "awa"),
    ("awa", "mariam"),
    ("awa", "kossi"),
    ("moussa", "awa"),
    ("moussa", "fatou"),
    ("nadia", "awa"),
    ("nadia", "mariam"),
    ("yao", "kossi"),
    ("yao", "awa"),
    ("aicha", "binta"),
    ("aicha", "mariam"),
    ("salif", "kossi"),
    ("koffi", "fatou"),
    ("binta", "mariam"),
    ("fatou", "moussa"),
]

# ── Favoris (user → titre publication) ──────────────────────────────────────
FAVORITES = [
    ("ibrahim", "Comment structurer une API Django multi-pays (XOF, TVA, fuseaux) ?"),
    ("ibrahim", "GestionScolaire — open source pour écoles privées"),
    ("awa", "CI trop lente sur runners partagés : vos leviers qui marchent vraiment"),
    ("yao", "Flutter : sync hors-ligne + file d'attente Mobile Money"),
    ("moussa", "RTK Query vs TanStack Query en 2026 — votre choix en prod ?"),
    ("nadia", "Session mentorat samedi : préparer un portfolio remote"),
    ("fatou", "Sahel UI — composants React accessibles en français"),
]

# ── DM (paires de keys + messages) ──────────────────────────────────────────
DIRECT_MESSAGES = [
    (
        "awa",
        "mariam",
        [
            ("awa", "Salut Mariam ! Ton post multi-pays est top."),
            ("mariam", "Merci Awa. Tu as déjà géré de la TVA CI/SN ?"),
            ("awa", "Oui sur un checkout Node — je t'envoie mon schéma demain."),
        ],
    ),
    (
        "fatou",
        "moussa",
        [
            ("fatou", "Moussa, ton profil React matche bien notre CDI."),
            ("moussa", "Merci Fatou — j'ai candidaté via la marketplace."),
            ("fatou", "Parfait, on shortlist cette semaine."),
        ],
    ),
    (
        "yao",
        "kossi",
        [
            ("yao", "Tu aurais un exemple de healthcheck Flutter → API ?"),
            ("kossi", "Oui — endpoint /health + timeout court côté client. Je te partage un gist."),
        ],
    ),
    (
        "ibrahim",
        "salif",
        [
            ("ibrahim", "Salut Salif, je veux contribuer à GestionScolaire."),
            ("salif", "Bienvenue ! Commence par les issues label « good first issue »."),
            ("ibrahim", "Je prends la doc d'install Windows."),
        ],
    ),
]
