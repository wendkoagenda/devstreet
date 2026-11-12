"""Jeu de données de démonstration de la marketplace (données pures, sans accès à la base).

Les dates sont des décalages en jours par rapport à aujourd'hui (positif : futur) pour que la démonstration
reste d'actualité : offres à démarrer bientôt, calendriers en cours, candidatures récentes.
Les noms de compétences viennent du référentiel de base (migration 0003_seed_base_skills).
"""

DOMAIN = "marketplace.example.test"

# ── Entreprises ──────────────────────────────────────────────────────────────
COMPANIES = [
    {
        "key": "resto", "name": "Resto Express", "sector": "ecommerce", "size": "11-50", "country": "TG", "city": "Lomé",
        "address": "Boulevard du 13 Janvier", "website": "https://resto-express.example.test",
        "contact_email": "contact@resto-express.example.test", "phone": "+22890000001", "verified": True,
        "description": "Chaîne de restauration rapide qui digitalise ses commandes et sa livraison à Lomé.",
    },
    {
        "key": "faso", "name": "Faso Pay", "sector": "fintech", "size": "51-200", "country": "BF", "city": "Ouagadougou",
        "address": "Avenue Kwame Nkrumah", "website": "https://faso-pay.example.test",
        "contact_email": "talents@faso-pay.example.test", "phone": "+22670000002", "verified": True,
        "description": "Solution de paiement Mobile Money pour les commerçants et les PME d'Afrique de l'Ouest.",
    },
    {
        "key": "agri", "name": "AgriConnect", "sector": "agritech", "size": "11-50", "country": "SN", "city": "Dakar",
        "address": "Sicap Liberté 6", "website": "https://agriconnect.example.test",
        "contact_email": "equipe@agriconnect.example.test", "phone": "+22170000003", "verified": False,
        "description": "Plateforme de suivi des cultures et des cours pour les coopératives agricoles.",
    },
    {
        "key": "edu", "name": "EduTech Sahel", "sector": "edtech", "size": "1-10", "country": "NE", "city": "Niamey",
        "address": "Quartier Plateau", "website": "https://edutech-sahel.example.test",
        "contact_email": "bonjour@edutech-sahel.example.test", "phone": "+22790000004", "verified": False,
        "description": "Start-up de cours en ligne pour les élèves du Sahel, accessible hors connexion.",
    },
]

# ── Recruteurs (profil rattaché à une entreprise) ────────────────────────────
RECRUITERS = [
    {"key": "koffi", "first": "Koffi", "last": "Agbodjan", "company": "resto", "owner": True,
     "headline": "Directeur, Resto Express", "city": "Lomé", "country": "TG", "tz": "Africa/Lome"},
    {"key": "fatou", "first": "Fatou", "last": "Sow", "company": "faso", "owner": True,
     "headline": "Responsable recrutement, Faso Pay", "city": "Ouagadougou", "country": "BF", "tz": "Africa/Ouagadougou"},
    {"key": "seydou", "first": "Seydou", "last": "Compaoré", "company": "faso", "owner": False,
     "headline": "Tech lead, Faso Pay", "city": "Ouagadougou", "country": "BF", "tz": "Africa/Ouagadougou"},
    {"key": "binta", "first": "Binta", "last": "Ndiaye", "company": "agri", "owner": True,
     "headline": "Cofondatrice, AgriConnect", "city": "Dakar", "country": "SN", "tz": "Africa/Dakar"},
    {"key": "boubacar", "first": "Boubacar", "last": "Diallo", "company": "edu", "owner": True,
     "headline": "Fondateur, EduTech Sahel", "city": "Niamey", "country": "NE", "tz": "Africa/Niamey"},
]

# ── Développeurs ─────────────────────────────────────────────────────────────
# skills : nom -> (niveau 1-5, années) ; experiences : (poste, entreprise, lieu, contrat, début, fin|None, description, technos)
DEVS = [
    {
        "key": "awa", "first": "Awa", "last": "Koné", "headline": "Dev React et Node, remote", "country": "CI", "city": "Abidjan",
        "tz": "Africa/Abidjan", "years": 5, "rate": 20000, "remote": True, "open": True, "cv": "companies",
        "languages": ["Français", "Anglais"], "github": "https://github.com/awa-kone-demo",
        "bio": "Développeuse full stack JavaScript. J'ai livré une application de livraison avec paiement Mobile Money.",
        "skills": {"React Native": (4, 3), "React": (5, 5), "Node.js": (4, 4), "API Mobile Money": (4, 2), "Géolocalisation": (3, 2), "Git": (5, 5)},
        "experiences": [
            ("Développeuse full stack", "Livraison Rapide", "Abidjan", "freelance", "2023-02-01", None,
             "Application mobile de livraison avec suivi en temps réel et paiement Mobile Money.", "React Native, Node.js, PostgreSQL"),
            ("Développeuse front-end", "Agence Pixel", "Abidjan", "cdi", "2020-09-01", "2023-01-31",
             "Interfaces React pour des clients bancaires.", "React, TypeScript"),
        ],
    },
    {
        "key": "yao", "first": "Yao", "last": "Mensah", "headline": "Dev mobile Flutter", "country": "TG", "city": "Lomé",
        "tz": "Africa/Lome", "years": 4, "rate": 18000, "remote": False, "open": True, "cv": "public",
        "languages": ["Français", "Éwé"], "github": "https://github.com/yao-mensah-demo",
        "bio": "Spécialiste Flutter, expérience du suivi de livreurs en temps réel.",
        "skills": {"Flutter": (5, 4), "Firebase": (4, 3), "Géolocalisation": (4, 3), "Node.js": (2, 1), "Git": (4, 4)},
        "experiences": [
            ("Développeur mobile", "Freelance", "Lomé", "freelance", "2024-01-01", None,
             "Applications de livraison et de réservation.", "Flutter, Firebase"),
            ("Développeur junior", "Agence Web Lomé", "Lomé", "cdi", "2022-02-01", "2023-12-31", "Sites et applications mobiles.", "Flutter, PHP"),
        ],
        "prestation": ("Application mobile Flutter clé en main", "mobile", 450000, 21, 2,
                       "Conception et livraison d'une application mobile Android et iOS, avec deux cycles de retouches."),
    },
    {
        "key": "mariam", "first": "Mariam", "last": "Diop", "headline": "Dev full stack Django", "country": "SN", "city": "Dakar",
        "tz": "Africa/Dakar", "years": 6, "rate": 28000, "remote": True, "open": True, "cv": "companies",
        "languages": ["Français", "Wolof", "Anglais"], "github": "https://github.com/mariam-diop-demo",
        "bio": "Développeuse Django et React, contributrice active de la communauté Python.",
        "skills": {"Django": (5, 6), "Python": (5, 6), "React": (4, 4), "API REST": (5, 5), "PostgreSQL": (4, 5), "Tests": (4, 4), "Communication": (4, 6)},
        "experiences": [
            ("Développeuse back-end senior", "Teranga Pay", "Dakar", "cdi", "2021-03-01", None,
             "API de paiement et tableaux de bord pour marchands.", "Django, PostgreSQL, React"),
            ("Développeuse Python", "Studio Baobab", "Dakar", "cdi", "2018-09-01", "2021-02-28", "Applications web sur mesure.", "Django, Docker"),
        ],
        "prestation": ("API Django REST sécurisée", "web", 350000, 14, 2,
                       "API documentée, authentification JWT, tests automatisés et déploiement."),
    },
    {
        "key": "kossi", "first": "Kossi", "last": "Adjovi", "headline": "DevOps, Docker et GCP", "country": "BJ", "city": "Cotonou",
        "tz": "Africa/Porto-Novo", "years": 6, "rate": 45000, "remote": True, "open": True, "cv": "companies",
        "languages": ["Français", "Fon"], "github": "https://github.com/kossi-adjovi-demo",
        "bio": "Ingénieur DevOps, auteur d'un guide CI/CD très suivi.",
        "skills": {"Docker": (5, 5), "Kubernetes": (4, 3), "GCP": (4, 4), "CI/CD": (5, 5), "Git": (5, 6), "Autonomie": (5, 6)},
        "experiences": [
            ("Ingénieur DevOps", "Cloud Bénin", "Cotonou", "cdi", "2020-01-01", None, "Plateformes Kubernetes et pipelines CI/CD.", "Docker, Kubernetes, GCP"),
        ],
    },
    {
        "key": "aicha", "first": "Aïcha", "last": "Traoré", "headline": "Data analyst Python", "country": "CI", "city": "Abidjan",
        "tz": "Africa/Abidjan", "years": 3, "rate": 15000, "remote": True, "open": True, "cv": "public",
        "languages": ["Français", "Anglais"], "github": "https://github.com/aicha-traore-demo",
        "bio": "Analyse de données et tableaux de bord pour des coopératives et des PME.",
        "skills": {"Python": (4, 3), "Pandas": (4, 3), "SQL": (4, 3), "Power BI": (4, 2), "Charts": (4, 2), "Curiosité": (5, 3)},
        "experiences": [
            ("Data analyst", "AgriData CI", "Abidjan", "cdi", "2023-03-01", None, "Suivi des rendements et des prix agricoles.", "Python, Pandas, Power BI"),
        ],
        "prestation": ("Tableau de bord Power BI", "data", 250000, 10, 1,
                       "Tableau de bord interactif relié à vos fichiers ou à votre base de données."),
    },
    {
        "key": "moussa", "first": "Moussa", "last": "Boureima", "headline": "Dev front React et TypeScript", "country": "NE", "city": "Niamey",
        "tz": "Africa/Niamey", "years": 2, "rate": 15000, "remote": True, "open": True, "cv": "companies",
        "languages": ["Français", "Haoussa"], "github": "https://github.com/moussa-boureima-demo",
        "bio": "Mainteneur d'une bibliothèque de composants UI en français.",
        "skills": {"React": (4, 2), "TypeScript": (4, 2), "CSS": (4, 2), "Figma": (3, 1), "Git": (4, 2)},
        "experiences": [
            ("Développeur front", "Sahel Digital", "Niamey", "cdd", "2024-06-01", None, "Refonte d'interfaces et bibliothèque de composants.", "React, TypeScript"),
        ],
    },
    {
        "key": "ibrahim", "first": "Ibrahim", "last": "Ouédraogo", "headline": "Dev web junior, Django et React", "country": "BF", "city": "Ouagadougou",
        "tz": "Africa/Ouagadougou", "years": 1, "rate": None, "remote": True, "open": True, "cv": "companies",
        "languages": ["Français", "Mooré", "Anglais"], "github": "https://github.com/ibrahim-ouedraogo-demo",
        "bio": "Sorti de formation en 2026, je cherche un premier stage pour progresser sur des projets concrets.",
        "skills": {"Django": (3, 1), "React": (3, 1), "Git": (3, 1), "Curiosité": (5, 1)},
        "experiences": [
            ("Stagiaire développeur", "Atelier Numérique", "Ouagadougou", "stage", "2025-09-01", "2026-02-28", "Petits outils internes en Django.", "Django, HTML, CSS"),
        ],
    },
    {
        "key": "salif", "first": "Salif", "last": "Tapsoba", "headline": "Dev back-end Django", "country": "BF", "city": "Bobo-Dioulasso",
        "tz": "Africa/Ouagadougou", "years": 3, "rate": 17000, "remote": True, "open": True, "cv": "public",
        "languages": ["Français", "Dioula"], "github": "https://github.com/salif-tapsoba-demo",
        "bio": "Cherche des devs juniors pour un projet open source de gestion scolaire.",
        "skills": {"Django": (4, 3), "Python": (4, 3), "PostgreSQL": (3, 2), "Git": (4, 3), "React": (2, 1)},
        "experiences": [
            ("Développeur back-end", "Gestion Plus", "Bobo-Dioulasso", "cdi", "2023-01-01", None, "Logiciels de gestion pour écoles privées.", "Django, PostgreSQL"),
        ],
    },
    {
        "key": "nadia", "first": "Nadia", "last": "Kaboré", "headline": "Dev mobile Flutter", "country": "BF", "city": "Ouagadougou",
        "tz": "Africa/Ouagadougou", "years": 2, "rate": 14000, "remote": True, "open": True, "cv": "companies",
        "languages": ["Français", "Anglais"], "github": "https://github.com/nadia-kabore-demo",
        "bio": "Organise des sessions de code en ligne le samedi.",
        "skills": {"Flutter": (3, 2), "Firebase": (3, 2), "Git": (4, 2), "Esprit d'équipe": (5, 2)},
        "experiences": [
            ("Développeuse mobile", "Ouaga Apps", "Ouagadougou", "cdd", "2024-03-01", None, "Applications Flutter pour des associations.", "Flutter, Firebase"),
        ],
    },
    {
        "key": "ousmane", "first": "Ousmane", "last": "Sawadogo", "headline": "Étudiant data, Python et Pandas", "country": "BF", "city": "Koudougou",
        "tz": "Africa/Ouagadougou", "years": 0, "rate": None, "remote": True, "open": True, "cv": "private",
        "languages": ["Français", "Mooré"], "github": "",
        "bio": "A partagé un notebook d'analyse des prix agricoles.",
        "skills": {"Python": (3, 1), "Pandas": (3, 1), "SQL": (2, 1), "Curiosité": (5, 1)},
        "experiences": [],
    },
    {
        "key": "grace", "first": "Grace", "last": "Amegah", "headline": "Dev front Vue.js", "country": "TG", "city": "Lomé",
        "tz": "Africa/Lome", "years": 3, "rate": 14000, "remote": True, "open": False, "cv": "public",
        "languages": ["Français", "Anglais", "Éwé"], "github": "https://github.com/grace-amegah-demo",
        "bio": "Répond souvent aux questions CSS des débutants. Indisponible pour le moment.",
        "skills": {"Vue.js": (4, 3), "CSS": (5, 3), "JavaScript": (4, 3), "Figma": (3, 2), "Communication": (4, 3)},
        "experiences": [
            ("Développeuse front", "Studio Lomé", "Lomé", "freelance", "2023-01-01", None, "Intégration de maquettes et sites vitrines.", "Vue.js, CSS"),
        ],
        "prestation": ("Intégration de maquette Vue.js", "web", 180000, 7, 1, "Transformation de votre maquette Figma en pages Vue.js responsives."),
    },
]

# ── Disponibilités manuelles : (dev, début, fin, statut, heures/semaine, note) en jours depuis aujourd'hui ─
AVAILABILITIES = [
    ("awa", 0, 24, "available", 40, "Disponible avant la prochaine mission"),
    ("yao", 0, 30, "partial", 20, "Fin d'un projet en cours"),
    ("yao", 31, 120, "available", 40, ""),
    ("mariam", 0, 20, "available", 30, ""),
    ("mariam", 21, 35, "leave", None, "Congés"),
    ("mariam", 36, 150, "available", 40, ""),
    ("aicha", 0, 90, "available", 40, ""),
    ("moussa", 0, 14, "partial", 20, ""),
    ("moussa", 15, 120, "available", 40, ""),
    ("ibrahim", 0, 10, "available", 40, ""),
    ("ibrahim", 13, 17, "partial", 20, "Cours le matin"),
    ("ibrahim", 21, 30, "leave", None, "Examens"),
    ("salif", 0, 60, "partial", 20, ""),
    ("nadia", 0, 90, "available", 40, ""),
    ("ousmane", 0, 120, "available", 20, "Disponible hors cours"),
]

# ── Offres ───────────────────────────────────────────────────────────────────
OFFERS = [
    {
        "key": "resto_mobile", "slug": "resto-mobile-react-native", "company": "resto", "recruiter": "koffi",
        "title": "Développeur mobile React Native, application de livraison",
        "description": "Conception d'une application mobile pour nos restaurants : prise de commande, suivi du livreur en temps réel et paiement Mobile Money.",
        "type": "mission", "duration": 3, "level": "mid", "min": 400000, "max": 500000, "period": "month",
        "country": "TG", "city": "Lomé", "mode": "hybrid", "start": 25, "deadline": 14, "status": "open", "published": -6,
        "skills": ["React Native", "Node.js", "API Mobile Money", "Géolocalisation", "Communication"],
    },
    {
        "key": "resto_site", "slug": "resto-refonte-site-vitrine", "company": "resto", "recruiter": "koffi",
        "title": "Refonte du site vitrine",
        "description": "Refonte du site vitrine avec menu en ligne et page de réservation.",
        "type": "mission", "duration": 1, "level": "mid", "min": 250000, "max": 300000, "period": "fixed",
        "country": "TG", "city": "Lomé", "mode": "remote", "start": -60, "deadline": -75, "status": "closed", "published": -90,
        "skills": ["Vue.js", "CSS", "Figma"],
    },
    {
        "key": "faso_front", "slug": "faso-pay-front-react-cdi", "company": "faso", "recruiter": "fatou",
        "title": "Développeuse ou développeur front-end React, CDI",
        "description": "Rejoignez l'équipe produit de Faso Pay pour construire le tableau de bord marchands. Tests et accessibilité font partie du quotidien.",
        "type": "cdi", "duration": None, "level": "mid", "min": 500000, "max": 700000, "period": "month",
        "country": "BF", "city": "Ouagadougou", "mode": "remote", "start": 45, "deadline": 30, "status": "open", "published": -10,
        "skills": ["React", "TypeScript", "Tests", "Git"],
    },
    {
        "key": "faso_devops", "slug": "faso-pay-devops-ci-cd", "company": "faso", "recruiter": "seydou",
        "title": "Ingénieur DevOps, industrialisation CI/CD",
        "description": "Mise en place des pipelines CI/CD et du déploiement conteneurisé sur GCP.",
        "type": "mission", "duration": 2, "level": "senior", "min": 900000, "max": 1100000, "period": "month",
        "country": "BF", "city": "Ouagadougou", "mode": "remote", "start": 20, "deadline": 10, "status": "open", "published": -12,
        "skills": ["Docker", "Kubernetes", "GCP", "CI/CD"],
    },
    {
        "key": "faso_api", "slug": "faso-pay-api-django", "company": "faso", "recruiter": "fatou",
        "title": "Développeur Django, API de paiement",
        "description": "Évolution de l'API de paiement : webhooks, réconciliation et tests de charge.",
        "type": "cdd", "duration": 6, "level": "mid", "min": 450000, "max": 600000, "period": "month",
        "country": "BF", "city": "Ouagadougou", "mode": "hybrid", "start": 50, "deadline": 35, "status": "open", "published": -3,
        "skills": ["Django", "Python", "API REST", "PostgreSQL", "Tests"],
    },
    {
        "key": "agri_dashboard", "slug": "agriconnect-tableau-de-bord", "company": "agri", "recruiter": "binta",
        "title": "Tableau de bord de suivi des cours agricoles",
        "description": "Refonte d'un tableau de bord de suivi des cours des céréales pour nos coopératives partenaires.",
        "type": "mission", "duration": 1, "level": "mid", "min": 300000, "max": 400000, "period": "fixed",
        "country": "SN", "city": "Dakar", "mode": "on_site", "start": 15, "deadline": 7, "status": "open", "published": -4,
        "skills": ["Python", "SQL", "Charts", "Pandas"],
    },
    {
        "key": "agri_mobile", "slug": "agriconnect-application-terrain", "company": "agri", "recruiter": "binta",
        "title": "Application mobile de saisie terrain (brouillon)",
        "description": "Application hors connexion pour la saisie des relevés par les agents de terrain.",
        "type": "mission", "duration": 3, "level": "mid", "min": None, "max": None, "period": "month",
        "country": "SN", "city": "Dakar", "mode": "hybrid", "start": 60, "deadline": None, "status": "draft", "published": None,
        "skills": ["Flutter", "Firebase"],
    },
    {
        "key": "edu_stage", "slug": "edutech-sahel-stage-web", "company": "edu", "recruiter": "boubacar",
        "title": "Stage développeur web, plateforme de cours",
        "description": "Premier stage encadré : corrections de bugs, petites fonctionnalités et revue de code avec l'équipe.",
        "type": "stage", "duration": 3, "level": "junior", "min": 75000, "max": 100000, "period": "month",
        "country": "NE", "city": "Niamey", "mode": "hybrid", "start": 30, "deadline": 20, "status": "open", "published": -5,
        "skills": ["Django", "React", "Git", "Curiosité"],
    },
]

# ── Candidatures : (offre, dev, statut, jours depuis l'envoi, message) ──────
CANDIDATURES = [
    ("resto_mobile", "awa", "accepted", 5, "Bonjour, j'ai déjà livré une application de livraison avec paiement Mobile Money. Disponible dès le début de la mission."),
    ("resto_mobile", "yao", "shortlisted", 5, "Basé à Lomé, expérience du suivi de livreurs en temps réel."),
    ("resto_mobile", "nadia", "sent", 3, "Développeuse Flutter, je me forme à React Native et je suis très motivée."),
    ("resto_mobile", "salif", "sent", 2, "Je peux assurer l'API Node.js et la partie back-end."),
    ("faso_front", "moussa", "shortlisted", 8, "Passionné par React et TypeScript, je maintiens une bibliothèque de composants."),
    ("faso_front", "awa", "sent", 4, "Développeuse React depuis cinq ans, à l'aise en télétravail."),
    ("faso_front", "grace", "rejected", 9, "Intéressée par le poste, même si mon expérience porte surtout sur Vue.js."),
    ("faso_devops", "kossi", "accepted", 10, "Auteur d'un guide CI/CD, je connais bien vos besoins sur GCP."),
    ("faso_api", "mariam", "sent", 2, "Six ans de Django, dont trois sur des API de paiement."),
    ("agri_dashboard", "aicha", "sent", 3, "Je travaille déjà sur des données agricoles à Abidjan."),
    ("agri_dashboard", "ousmane", "sent", 2, "Étudiant motivé, j'ai analysé les prix agricoles dans un notebook partagé."),
    ("agri_dashboard", "mariam", "shortlisted", 3, "Disponible à partir du mois prochain."),
    ("edu_stage", "ibrahim", "sent", 1, "Sorti de formation en 2026, je cherche un premier stage pour progresser sur des projets concrets."),
    ("edu_stage", "ousmane", "shortlisted", 2, "Je souhaite découvrir le développement web après mes cours de data."),
    ("resto_site", "grace", "accepted", 85, "Je peux livrer le site en un mois, à distance."),
]

# ── Avis : (auteur, cible, note, commentaire, (offre, dev) | None, public) ──
REVIEWS = [
    ("koffi", "grace", 5, "Site livré dans les temps, très bonne communication.", ("resto_site", "grace"), True),
    ("grace", "koffi", 4, "Cahier des charges clair et paiement rapide.", ("resto_site", "grace"), True),
    ("fatou", "mariam", 5, "Mission d'API menée avec rigueur et pédagogie.", None, True),
    ("mariam", "fatou", 5, "Équipe agréable, besoins bien définis.", None, True),
    ("koffi", "yao", 4, "Bonne application de réservation, quelques retards sur la fin.", None, True),
    ("seydou", "kossi", 5, "Pipeline mis en place en deux semaines, documentation claire.", None, True),
    ("binta", "aicha", 4, "Analyses fiables, tableau de bord apprécié des coopératives.", None, True),
    ("fatou", "salif", 3, "Travail correct, à encadrer davantage.", None, False),
]

# ── Swipes de recrutement : (recruteur, dev, direction) ─────────────────────
RECRUIT_SWIPES = [
    ("fatou", "yao", "like"), ("fatou", "mariam", "like"), ("fatou", "kossi", "like"), ("fatou", "salif", "pass"),
    ("seydou", "aicha", "like"), ("seydou", "mariam", "like"),
    ("koffi", "awa", "like"), ("koffi", "yao", "like"), ("koffi", "nadia", "like"), ("koffi", "ousmane", "pass"),
    ("binta", "aicha", "like"), ("binta", "ousmane", "like"),
    ("boubacar", "ibrahim", "like"), ("boubacar", "moussa", "pass"),
]

# ── Swipes réseau : un like réciproque crée une connexion ───────────────────
NETWORK_SWIPES = [
    ("ibrahim", "salif", "like"), ("salif", "ibrahim", "like"),
    ("ibrahim", "nadia", "like"), ("nadia", "ibrahim", "like"),
    ("ibrahim", "ousmane", "pass"), ("ousmane", "ibrahim", "like"),
    ("awa", "mariam", "like"), ("mariam", "awa", "like"),
    ("yao", "kossi", "like"), ("kossi", "yao", "pass"),
    ("moussa", "grace", "like"), ("grace", "moussa", "like"),
]
BLOCKED_CONNECTIONS = [("moussa", "kossi")]

# ── Historique du profil : (dev, champ, ancienne valeur, nouvelle valeur, source) ─
HISTORIES = [
    ("ibrahim", "headline", "Étudiant en informatique", "Développeur web junior, Django et React", "manual"),
    ("ibrahim", "bio", "", "Sorti de formation en 2026, je cherche un premier stage.", "manual"),
    ("ibrahim", "skills", "Django, Git", "Django, React, Git, Curiosité", "system"),
    ("awa", "years_of_experience", "4", "5", "manual"),
    ("awa", "daily_rate", "40000", "45000", "manual"),
    ("yao", "headline", "Développeur Flutter", "Dev mobile Flutter", "ai"),
    ("mariam", "cv_visibility", "public", "companies", "manual"),
    ("kossi", "headline", "DevOps", "DevOps, Docker et GCP", "ai"),
]
