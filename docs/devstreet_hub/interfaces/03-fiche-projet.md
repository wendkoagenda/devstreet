# 03 — Fiche projet

**Statut : livré** pour la fiche et l’onglet **Code** (exploration / lecture). Les PR / diffs / merge restent une étape ultérieure.

## À regrouper

### Présentation en texte libre (interface intégrée)

La présentation utilise une carte de lecture avec les initiales et le nom public du propriétaire,
des paragraphes libres, puis les images facultatives. Aucun titre de section, liste, citation ou
diagramme n'est imposé au rédacteur. Le style vient des composants, de Poppins et des tokens
Graphite (actions anthracite, accent violet), en clair et en sombre.

La colonne « À propos » reprend uniquement les données existantes : propriétaire, licence,
visibilité et technologies. Les raccourcis et l'invitation à contribuer sélectionnent les onglets
internes. Les actions de gestion sont regroupées dans une barre distincte, selon les droits.

« Modifier » ouvre un champ de texte libre. Le résumé court reste facultatif dans une section
repliable. L'auteur peut joindre quatre images JPEG/PNG/WebP de 4 Mo maximum chacune, ou
ne joindre aucune image. Les ajouts/retraits sont appliqués avec le texte au clic « Enregistrer
les modifications ». Annuler abandonne le brouillon. Une édition concurrente est refusée (409).

« Améliorer la description avec l'IA » analyse le texte du brouillon et des extraits du dépôt à
un SHA précis, après consentement du propriétaire. Le résultat apparaît séparément avec les
sources, inconnues et version. « Utiliser cette proposition » modifie le champ du brouillon ;
il faut encore enregistrer. Une génération n'écrit jamais la présentation du projet.

| Route | Contrat |
| --- | --- |
| PUT /api/v1/projects/{id}/presentation | Multipart : description, problem, base_updated_at ; images et remove_image_ids répétables, facultatifs |
| GET /api/v1/projects/{id}/presentation/images/{image_id} | Lecture avec les mêmes droits de visibilité que le projet ; aucune URL de fichier public pour les brouillons |
| POST /api/v1/projects/{id}/presentation/suggestions | description et language (fr/en), retourne une analyse presentation-v1, 202 ou 200 |
| GET /api/v1/analyses/{id} | Lecture bornée jusqu'au résultat ; quotas partagés avec l'atelier IA |

Les images sont vérifiées puis réencodées en JPEG sans métadonnées. Avec `USE_S3=True`, elles
sont stockées dans MinIO sous le préfixe `hub_project_images/` (même bucket privé que le reste,
mais **jamais** via `/api/v1/files/` — uniquement la route présentation ci-dessus). Sans S3,
elles restent sur le disque `DEVSTREET_HUB_PRIVATE_IMAGE_ROOT` (`backend/private_uploads/project_images`),
hors de `MEDIA_ROOT` et non publié par le serveur web.

L'amélioration réutilise le worker d'analyses et la configuration OpenAI existants. En local,
`DEVSTREET_HUB_AI_INLINE_WORKER=true` permet le traitement immédiat ; sinon lancer
`python manage.py process_devstreet_hub_analyses`. Une clé absente, un quota atteint ou un dépôt
sans extraits exploitables donne un état explicite ; la rédaction manuelle reste disponible.

Le schéma de réponse est validé côté serveur : [Structured Outputs OpenAI](https://developers.openai.com/api/docs/guides/structured-outputs).

En-tête : nom, problème résolu, technologies, étoiles et démo. Puis onglets **Présentation · Code · Contribuer · Équipe**. Le visiteur comprend d’abord l’utilité ; le contributeur trouve ensuite une tâche. Le propriétaire dispose d’un menu de gestion discret.

| Route | Intégration |
| --- | --- |
| GET /api/v1/projects/{id} | Source de vérité de la fiche et des états |
| PATCH /api/v1/projects/{id} | Modifier la présentation pour propriétaire/mainteneur avec IAM |
| GET /api/v1/projects/{id}/repository | Métadonnées + URL de clone ; `is_empty` / `current_sha` pour l’état du dépôt |
| GET /api/v1/projects/{id}/code/summary | Résumé dépôt (branche, stats, langues, clone) via Django → Gitea |
| GET /api/v1/projects/{id}/code/branches | Liste des branches |
| GET /api/v1/projects/{id}/code/tree?ref=&path= | Arborescence + bandeau commit + README |
| GET /api/v1/projects/{id}/code/blob?ref=&path= | Contenu fichier (texte, limites taille/binaire) |
| GET /api/v1/projects/{id}/tasks | Onglet Contribuer paginé ; clic → écran 04 |
| GET /api/v1/projects/{id}/members | Équipe, paginée |
| POST /api/v1/projects/{id}/members | Propriétaire : attribuer un rôle métier à un ID utilisateur existant |
| DELETE /api/v1/projects/{id}/members/{user_id} | Propriétaire : retirer une appartenance ; ne pas retirer le propriétaire |
| PUT /api/v1/projects/{id}/star ; DELETE même route | Étoiles DevStreet (seule source de vérité « favoris ») |
| POST /api/v1/projects/{id}/publish ; /archive | Propriétaire : transitions confirmées par le serveur |
| POST /api/v1/projects/{id}/tasks | Créer une tâche manuelle brouillon |

## UX proposée

### Chargement du code

Le skeleton reprend la structure des fichiers au chargement initial et les lignes lors d'un
changement de dossier. Les fichiers sont affichés sans attendre les statistiques ; une panne
de ces dernières ne masque pas le code. RTK Query utilise `currentData` pour ne pas afficher
le contenu d'une ancienne branche ou d'un ancien chemin sous la nouvelle sélection.

L'adaptateur réutilise le contexte TLS et son bundle certifi, sans désactiver la vérification
des certificats ([configuration HTTPX](https://www.python-httpx.org/advanced/ssl/)). Le champ
`empty` des métadonnées évite aussi une requête identique supplémentaire. Aucun contenu ni
permission de dépôt n'est mis en cache par ce mécanisme.

Mesures locales sur le dépôt de test : résumé ~4–5 s avant, ~0,22 s après échauffement ;
arborescence ~2,7 s avant, ~0,25 s après. Premier résumé après redémarrage : ~1,2 s.
Ces durées dépendent de la machine et du réseau et ne constituent pas un SLA.

### Navigation et droits

Le bouton « Préparer une contribution avec l’IA » mène à l’écran 06 ; « Examiner les propositions » à l’écran 05. L’onglet **Code** est **interne à DevStreet** : explorateur de fichiers, sélecteur de branche, fil d’Ariane, lecteur de fichiers (numéros de ligne, HTML affiché comme texte), menu de copie d’URL de clone, README Markdown sécurisé, description et langages. L’en-tête de fiche affiche les **langues détectées** du dépôt (plus les tags manuels type Go/Django choisis à la création). Aucune redirection vers l’UI Gitea, aucun iframe. Les paramètres `tab`, `ref`, `path` et `mode` restent dans l’URL (branches avec slashs via `ref`). Les interfaces PR / diff / merge ne doivent **pas** être annoncées avant leur livraison.

L’ajout d’un membre par nom requiert un sélecteur du compte commun ; `/api/v1/users` est soumis aux permissions IAM et ne doit pas être rendu public par le frontend. Tant qu’un annuaire public n’existe pas, accepter un ID utilisateur communiqué par le membre.

Ne pas confondre rôle de mainteneur métier et droit de push Git. Confirmer l’archivage avec son effet sur la visibilité et les preuves de candidature. Le propriétaire conserve l’accès à son projet archivé. Les blobs et commits restent la vérité Gitea : **pas de copie** dans les tables Django. Les métadonnées d’auteur Git ne créent pas de lien automatique vers un profil DevStreet.

## Terminé lorsque

Les onglets gardent le même projet ; aucun formulaire ne permet de changer owner/status directement ; les listes sont paginées ; les mutations refusées sont expliquées ; les tâches manuelles restent disponibles sans IA ; le parcours Code est consultable sans quitter DevStreet ; aucune redirection forcée vers l’UI Gitea.
