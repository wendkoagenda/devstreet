# Accès, journal d'audit et protections de l'API

Ce document décrit les protections ajoutées au backend au-delà de l'authentification : hiérarchie des droits, verrouillage de la connexion, journal d'audit, limites de téléversement et admin Django. Les tests sont dans `backend/app/tests/` (`test_access_policy.py`, `test_audit_log.py`, `test_upload_limits.py`).

## Hiérarchie des droits (`AccessPolicy`)

Avoir `users.update` ou `roles.update` ne suffit pas pour se promouvoir. Les vues utilisateurs et rôles appellent `app/core/services/access_policy.py`, qui refuse (403, message en clair, entrée `access.denied` au journal) :

- d'attribuer un rôle ou une permission que l'on ne possède pas soi-même (aucune montée en puissance) ;
- de gérer un compte ou un rôle plus puissant que le sien ;
- de gérer un superutilisateur, ou de modifier `is_staff`, sans être superutilisateur ;
- de modifier ses propres rôles et droits, de se désactiver ou de supprimer son propre compte (le profil reste modifiable) ;
- de supprimer ou désactiver le dernier superutilisateur actif.

Un superutilisateur actif n'est pas soumis à la hiérarchie, mais reste soumis aux règles sur soi-même. Les services (`UserService`, `RoleService`) restent utilisables sans acteur par les seeds et les commandes : la politique s'applique aux requêtes HTTP.

## Verrouillage de la connexion par compte

La limite par adresse IP (`LoginThrottle`) ne suffit pas contre une attaque répartie sur plusieurs adresses. En plus, après `LOGIN_LOCKOUT_MAX_FAILURES` échecs (10) en `LOGIN_LOCKOUT_MINUTES` minutes (15), l'e-mail saisi refuse toute tentative (429 + `Retry-After`), même avec le bon mot de passe. La fenêtre est glissante ; une connexion réussie remet le compteur à zéro. Un e-mail inconnu est verrouillé comme un e-mail connu : la réponse ne révèle pas quels comptes existent. Le compteur est lu dans le journal d'audit (base de données), donc partagé entre les processus.

`NUM_PROXIES` vaut 1 derrière un reverse proxy de confiance (un seul) et **0** sinon (jamais `None`) : avec `None`, un client pourrait forger `X-Forwarded-For` pour contourner la limite par IP et fausser les adresses du journal.

## Journal d'audit

Table `core_audit_log` (modèle `AuditLog`) : auteur, action, objet concerné, adresse, métadonnées, date. Une entrée n'est jamais modifiée. Elle est consultable en lecture seule dans l'admin Django (si `ENABLE_ADMIN`). Actions enregistrées :

| Action | Quand |
|---|---|
| `auth.login_success`, `auth.login_failed` | Connexion (l'e-mail saisi n'est jamais stocké : seulement son empreinte SHA-256) |
| `auth.password_changed`, `auth.password_reset` | Changement ou réinitialisation du mot de passe |
| `user.created`, `user.updated`, `user.deleted` | Gestion des comptes (champs modifiés, rôles ; jamais de mot de passe) |
| `user.role_assigned`, `user.role_removed` | Attribution ou retrait de rôles |
| `role.created`, `role.updated`, `role.deleted` | Gestion des rôles |
| `role.permission_assigned`, `role.permission_removed`, `role.permissions_bulk_assigned` | Permissions d'un rôle |
| `access.denied` | Action refusée par la politique d'accès |

Les métadonnées ne contiennent jamais de secret : noms de rôles, codes de permission, noms de champs.

### Purge planifiée

La commande `python manage.py purge_expired_data` supprime les jetons de rafraîchissement expirés de la liste noire (sinon elle grossit sans fin), les challenges de réinitialisation de plus de 7 jours et les entrées du journal plus anciennes que `AUDIT_RETENTION_DAYS` (365). À planifier **une fois par jour** (cron ou timer systemd sur la VM). Sans elle, ni la liste noire ni le journal ne se vident.

## Téléversements

- `UPLOAD_MAX_SIZE_MB` (25) est le plafond absolu. `RequestSizeLimitMiddleware` refuse (413) toute requête dont le `Content-Length` dépasse ce plafond + 1 Mo de multipart, avant de la lire.
- Chaque champ fichier déclare `allowed_extensions` (obligatoire dans le JSON du générateur) et `max_size_mb` (10 par défaut, 25 au plus). Sans extension configurée, **aucun fichier n'est accepté**.
- Le contrôle porte sur l'extension et la taille, pas sur le contenu : ne jamais servir un fichier téléversé depuis le même domaine que l'application avec un type exécutable.

## Admin Django

`ENABLE_ADMIN` est une variable **obligatoire** (`false` sauf besoin précis). L'admin contourne la politique d'accès et le journal de l'API. La règle de scanner `DJ-010` signale une route `/admin/` déclarée sans condition.

## Migrations destructives

La règle `DJ-011` du scanner signale `RemoveField`, `DeleteModel` et `RunSQL` avec `DROP`, `DELETE` ou `TRUNCATE`. Une telle migration se déclare dans `security-exceptions.json` (relue, datée, attribuée) après sauvegarde de la base et déploiement d'une version qui n'utilise plus l'élément supprimé.
