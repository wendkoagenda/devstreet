# Espace utilisateur de la marketplace

L'interface de la marketplace est orientée utilisateur : chacun gère son profil, ses candidatures ou ses offres. Les 13 pages CRUD générées restent accessibles aux rôles qui ont les permissions, sous `/admin/marketplace/*`.

## Principe d'accès

Les endpoints `/api/v1/marketplace/...` sont ouverts à tout utilisateur connecté, sans permission RBAC (`profils.view`, etc., réservées à l'administration). Chaque règle d'accès est portée par les services (`app/marketplace/services/`) :

- un utilisateur ne lit et ne modifie que son propre profil, ses périodes et ses expériences ;
- un **recruteur** est un profil rattaché à une entreprise : il gère les offres de son entreprise, ses candidatures et son vivier ;
- le compte, le slug, l'entreprise, le statut de vérification et les champs système ne se choisissent jamais depuis le corps d'une requête.

## Endpoints

| Domaine | Endpoint | Rôle |
| --- | --- | --- |
| Profil | `GET marketplace/me` | Profil et entreprise de l'utilisateur |
| | `POST` / `PATCH marketplace/me/profil` | Créer / modifier son profil |
| | `POST` / `PATCH marketplace/me/company` | Créer son entreprise (il en devient propriétaire) / la modifier |
| Compétences | `GET marketplace/skills` | Référentiel (graine de base : migration `0003`) |
| | `GET` / `PUT marketplace/me/skills` | Compétences du profil (le `PUT` remplace la liste) |
| Offres | `GET marketplace/offers` | Offres ouvertes, triées par score |
| | `GET marketplace/offers/<id>` | Fiche et détail du score |
| | `POST marketplace/offers/<id>/apply` | Postuler |
| | `GET marketplace/me/candidatures` | Mes candidatures |
| Recruteur | `GET` / `POST marketplace/me/offers` | Offres de mon entreprise |
| | `GET` / `PATCH marketplace/me/offers/<id>` | Lire / modifier (dont le statut) |
| | `GET marketplace/me/offers/<id>/candidatures` | Candidatures reçues, triées par score |
| | `GET marketplace/me/offers/<id>/recommended-profils` | Talents classés pour l'offre |
| | `POST marketplace/candidatures/<id>/decision` | `shortlisted`, `rejected` ou `accepted` |
| Découverte | `GET marketplace/me/deck?context=recruit\|network` | Paquet de cartes |
| | `POST marketplace/me/swipes` | Like ou passe (un like réseau réciproque crée la connexion) |
| | `DELETE marketplace/me/swipes/last?context=` | Annuler le dernier choix |
| | `GET marketplace/me/pool` | Vivier de l'entreprise |
| | `GET marketplace/me/connections` | Mes connexions |
| | `GET marketplace/profils/<id>` | Fiche d'un profil |
| Calendrier | `GET` / `POST marketplace/me/availabilities` | Périodes de disponibilité |
| | `PATCH` / `DELETE marketplace/me/availabilities/<id>` | Seules les périodes saisies à la main |
| Expériences | `GET` / `POST marketplace/me/experiences` | Parcours professionnel |
| | `PATCH` / `DELETE marketplace/me/experiences/<id>` | |
| CV | `GET marketplace/me/cv` | Mon CV en PDF |
| | `GET marketplace/profils/<id>/cv` | CV d'un profil, selon `cv_visibility` |

## Règles métier

- **Score de recommandation (sur 100, par règles)** : compétences 40, expérience 15, localisation 15, budget 10, disponibilité 10, réputation 10. Code : `services/scoring.py`. La part IA est prévue plus tard et annoncée « Bientôt disponible » dans l'interface.
- **Candidature acceptée** : crée une période « occupé » (origine `mission`) dans le calendrier du candidat, de la date de début de l'offre pour la durée du contrat (12 mois sans durée pour un CDI ou CDD, 1 mois sinon), et envoie un e-mail. Une candidature acceptée est définitive.
- **Swipe** : deux contextes. `recruit` (recruteur vers talent) alimente le vivier de l'entreprise. `network` (dev vers dev) crée une `Connection` quand le like est réciproque ; annuler ce like la supprime.
- **Coordonnées** : l'e-mail d'un profil n'est visible que pour soi-même, une connexion, un candidat à une offre de mon entreprise ou un membre de mon vivier.
- **CV** : reconstruit à chaque téléchargement (reportlab) depuis le profil, les compétences, les expériences, les prestations actives et les avis publics. Visibilité : `public` (tout profil), `companies` (profils rattachés à une entreprise), `private` (soi-même).
- **Calendrier** : les périodes d'un même profil ne se chevauchent pas ; une période créée par une mission n'est ni modifiable ni supprimable.

## Hors périmètre pour l'instant

Génération d'offre par IA, part IA du score, messagerie intégrée (« Contacter » ouvre un `mailto:`), photo de profil, gestion des prestations et dépôt d'avis, historique des modifications du profil (`ProfilHistory`), `Skill.forum_tag`.
