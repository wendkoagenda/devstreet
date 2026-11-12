# 02 — Créer le projet et préparer son dépôt

**Statut : à réaliser.** Parcours du propriétaire, sans créer de compte Django ni de rôle IAM.

## À regrouper

Un parcours en trois étapes : **Présenter → Préparer le dépôt → Publier**. Le projet est sauvegardé en brouillon dès la première étape. Une interruption doit permettre de revenir sur sa fiche sans ressaisir les informations.

| Route | Intégration |
| --- | --- |
| GET /api/v1/technologies | Sélection des technologies existantes |
| POST /api/v1/projects | Envoyer titre, slug, problème, description, démo optionnelle, licence et IDs de technologies ; conserver l’ID retourné |
| PATCH /api/v1/projects/{id} | Reprendre et corriger le brouillon |
| POST /api/v1/forge-access | Préparer l’identité Git liée au compte existant ; secret initial retourné une seule fois à sa création |
| POST /api/v1/projects/{id}/provision | Créer/retrouver le dépôt, privé tant que le projet est brouillon |
| GET /api/v1/projects/{id}/repository | Afficher état et URL Git ; aucune fausse URL tant que le dépôt n’est pas prêt |
| POST /api/v1/projects/{id}/publish | Rendre le dépôt public puis confirmer la publication de la fiche |

## UX proposée

Chaque étape explique le résultat : « Les autres comprendront ton projet », puis « Voici où envoyer ton code ». Les commandes Git affichées utilisent seulement l’URL publique fournie, jamais le jeton administratif. Pour la première connexion Git, proposer la transition explicite vers Gitea pour changer le mot de passe initial et créer un token personnel. Un panneau à usage unique permet de copier le secret initial ; aucune persistance locale automatique.

Erreur de provisionnement : garder le brouillon et proposer « Réessayer ». Avant publication, indiquer clairement que le code deviendra public. La licence reste déclarative : ce choix ne constitue pas un audit de ses dépendances.

## Terminé lorsque

L’utilisateur peut reprendre son brouillon ; un retry ne crée pas de second dépôt ; l’absence de forge donne un message explicite ; publier est impossible avant confirmation du dépôt ; le secret initial n’est pas conservé dans l’état persistant du frontend.
