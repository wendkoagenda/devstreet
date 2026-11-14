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
| Tableau de bord | `GET marketplace/me/dashboard` | Indicateurs du profil, des candidatures et, pour un recruteur, de son entreprise |
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
| | `POST marketplace/me/offers/generate` | Brouillon d'offre + suggestions (IA, UC-09) |
| | `GET` / `PATCH marketplace/me/offers/<id>` | Lire / modifier (dont le statut) |
| | `GET marketplace/me/offers/<id>/candidatures` | Candidatures reçues, triées par score |
| | `GET marketplace/me/offers/<id>/recommended-profils` | Talents classés pour l'offre |
| | `POST marketplace/candidatures/<id>/decision` | `shortlisted`, `rejected` ou `accepted` |
| | `GET marketplace/talents` | Annuaire filtrable (compétence, pays, dispo, remote) |
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
| Prestations | `GET` / `POST marketplace/me/prestations` | Services packagés du profil |
| | `PATCH` / `DELETE marketplace/me/prestations/<id>` | |
| Avis | `GET marketplace/me/reviews/pending` | Missions acceptées à noter |
| | `GET` / `POST marketplace/me/reviews` | Avis déposés / noter l'autre partie |
| Réputation | `GET marketplace/me/reputation` | Score /100 (avis, forum, hub, apps) |
| CV | `GET marketplace/me/cv` | Mon CV en PDF |
| | `GET marketplace/profils/<id>/cv` | CV d'un profil, selon `cv_visibility` |

## Tableau de bord

La page `/marketplace` s'adapte au profil. Toutes les valeurs sont celles de l'utilisateur connecté (code : `services/dashboard_service.py`).

- **Recruteur** (profil rattaché à une entreprise) : offres ouvertes, brouillons et clôturées, candidatures reçues et à traiter, vues des offres, taille du vivier, candidatures par semaine sur 8 semaines, répartition par statut, offres les plus actives et dernières candidatures avec leur score.
- **Candidat** (tout profil, recruteur compris) : répartition de ses candidatures par statut, missions à venir, trois offres recommandées.
- **Profil** : complétude sur 8 critères avec les éléments manquants, statut du jour du calendrier (le plus contraignant des périodes en cours) et prochaine disponibilité, score de réputation DevStreet (breakdown), nombre de connexions.

## Règles métier

- **Score de recommandation (sur 100, par règles)** : compétences 40, expérience 15, localisation 15, budget 10, disponibilité 10, réputation 10. Code : `services/scoring.py`. La part IA est prévue plus tard et annoncée « Bientôt disponible » dans l'interface.
- **Candidature acceptée** : crée une période « occupé » (origine `mission`) dans le calendrier du candidat, de la date de début de l'offre pour la durée du contrat (12 mois sans durée pour un CDI ou CDD, 1 mois sinon), et envoie un e-mail. Une candidature acceptée est définitive.
- **Swipe** : deux contextes. `recruit` (recruteur vers talent) alimente le vivier de l'entreprise. `network` (dev vers dev) crée une `Connection` quand le like est réciproque ; annuler ce like la supprime.
- **Coordonnées** : l'e-mail d'un profil n'est visible que pour soi-même, une connexion, un candidat à une offre de mon entreprise ou un membre de mon vivier.
- **CV** : reconstruit à chaque téléchargement (reportlab) depuis le profil, les compétences, les expériences, les prestations actives et les avis publics. Visibilité : `public` (tout profil), `companies` (profils rattachés à une entreprise), `private` (soi-même).
- **Calendrier** : les périodes d'un même profil ne se chevauchent pas ; une période créée par une mission n'est ni modifiable ni supprimable.

## Hors périmètre pour l'instant

Part IA du score (embeddings), messagerie intégrée (« Contacter » ouvre un `mailto:`), photo de profil, historique des modifications du profil (`ProfilHistory`), `Skill.forum_tag`, paiement Mobile Money (UC-15).

## Données de démonstration

```powershell
# depuis backend/, venv active, DEBUG=True
python manage.py seed_marketplace_demo            # crée ou met à jour (idempotent)
python manage.py seed_marketplace_demo --reset    # supprime d'abord les données de démonstration
```

La commande remplit les 13 tables : 4 entreprises, 16 profils (5 recruteurs, 11 développeurs), compétences de profil, expériences, prestations, historique, calendriers, 8 offres (ouvertes, brouillon, clôturée), 15 candidatures dans tous les statuts, avis publics et privé, swipes et connexions (réciproques et bloquée). Les dates suivent « aujourd'hui » : les offres démarrent bientôt, les calendriers sont en cours. Une candidature acceptée ajoute sa période « occupé », comme dans l'application.

Les comptes ont une adresse `@marketplace.example.test` et un mot de passe commun généré, lu dans `backend/.local/demo.credentials.json` (hors dépôt, partagé avec le seed du Hub). Pour parcourir les écrans :

| Compte | Rôle | À regarder |
| --- | --- | --- |
| `awa@…` | Dev React et Node | Offres classées, candidature acceptée, CV PDF |
| `ibrahim@…` | Dev junior | Profil à compléter, 2 connexions, rencontres entre devs |
| `fatou@…` | Recruteuse Faso Pay (propriétaire) | Offres, candidatures reçues, vivier de 4 talents |
| `seydou@…` | Recruteur Faso Pay (non propriétaire) | Ne peut pas modifier l'entreprise |
| `koffi@…` | Directeur Resto Express | Offre clôturée avec avis |
| `binta@…` | Cofondatrice AgriConnect (non vérifiée) | Offre en brouillon |
| `grace@…` | Dev front, non disponible | Profil masqué des recommandations |

Les seeds générés `seed_<modèle>` (3 lignes aléatoires par table) restent disponibles ; `seed_marketplace_demo` les remplace pour une démonstration cohérente.
