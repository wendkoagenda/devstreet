# 02 — Créer le projet et préparer son dépôt

**Statut : livré (étape 1 headless).** Parcours du propriétaire dans DevStreet, sans ouvrir l’interface Gitea et sans créer de compte Django / rôle IAM.

## À regrouper

Un parcours **à un bouton principal** : **Créer mon projet**. Le serveur orchestre brouillon Django + identité Git + dépôt privé. Ensuite, l’utilisateur initialise dans DevStreet (**README** ou **envoyer un projet existant**). La publication publique reste une action explicite séparée.

| Route | Intégration |
| --- | --- |
| GET /api/v1/technologies | Sélection des technologies existantes |
| POST /api/v1/projects | Titre + licence (+ techno, options avancées). **Slug optionnel** (généré côté serveur avec collision). Réponse 201 : projet + `setup` + `forge_access` éventuel |
| PATCH /api/v1/projects/{id} | Corriger la fiche (slug toujours unique) |
| POST /api/v1/projects/{id}/setup | Reprise après échec partiel : identité + dépôt, **idempotent**, sans doublon |
| POST /api/v1/forge-access | Toujours disponible pour reprise identité seule (preuves de corrélation inchangées) |
| POST /api/v1/projects/{id}/provision | Reprise dépôt seule (idempotent si `ready`) |
| GET /api/v1/projects/{id}/repository | État, `clone_url`, `is_empty`, `current_sha` ; pas d’URL fictive |
| POST /api/v1/projects/{id}/initialize | `{ "mode": "readme" \| "push_existing" }` — README/LICENSE/.gitignore via API Gitea, ou consignes de push |
| POST /api/v1/projects/{id}/publish | Rendre le dépôt public puis publier la fiche (jamais implicite) |

## UX proposée

Formulaire minimal : **nom**, **licence**, **technologies**. Slug / problème / description / démo dans **options avancées**. Un CTA **Créer mon projet** ; progression lisible (brouillon → accès Git → dépôt → initialisation). En cas d’échec : garder le brouillon, bouton **Reprendre**, aucun second compte / dépôt.

Après dépôt prêt et vide : **Initialiser avec un README** (écriture réelle Gitea) ou **Envoyer un projet existant** (commandes clone/push dans le Hub). Afficher le secret forge **une seule fois** ; aucun jeton admin dans le navigateur ; **aucun bouton** qui impose d’ouvrir l’UI Gitea.

La création reste **privée**. Publier exige confirmation d’intégrité. La licence reste déclarative.

## Terminé lorsque

Slug auto + collision gérés serveur ; création orchestrée avec reprise sans doublons ; init README réelle via Gitea ; publication explicite ; parcours 100 % DevStreet pour cette étape ; secret initial non persisté côté frontend.
