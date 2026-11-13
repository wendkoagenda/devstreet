# Validation parcours Git HTTPS navigateur

Date : 2026-11-13 — branche `feat/hub-git-https-browser`.

## Automatisé

| # | Cas | Résultat |
|---|---|---|
| — | `test_git_oauth` (client-config, redirect, approve+token, PKCE, deny) | OK |
| — | `test_git_auth` (device legacy) | OK |
| — | `test_project` / `test_forge_identity` | OK |
| 1 | Clone public sans credential (POC isolé) | OK |
| 2–4 | OAuth approve+token → push `git:PAT` → 2ᵉ push | OK (navigateur GCM simulé via service) |
| — | Config/coffre isolés sans helper LOCALAPPDATA | OK |

Commande POC : `python scripts/smoke_git_oauth_gcm.py` (DEBUG, dépôt jetable).

## Manuel restant (environnement neuf)

| # | Cas | Statut |
|---|---|---|
| 2 | Premier push réel ouvrant GCM → page Hub | Proposé (non exécuté ici) |
| 5 | 2ᵉ dépôt même propriétaire | Proposé |
| 6 | Refus écriture non collaborateur | Proposé |
| 7 | Révocation effective | Couvert API `git-computers` + tests unitaires |
| 8 | 2ᵉ ordinateur n’invalidé pas le 1ᵉʳ | Proposé |
| 9 | Annulation / panne réseau | Couvert partiellement (deny OAuth) |
| 10 | Absence dépendance ancien helper | POC isolé OK |

## Implémenté vs proposé

- **Implémenté** : AS OAuth PKCE Hub, dépôts publics + visibility user public, UI config Git + parcours A/B, reconcile dry-run, docs migration, dépréciation CLI.
- **Testé auto** : OAuth unitaires + POC transport (clone/push).
- **Testé manuel GCM UI** : pas encore (nécessite interaction navigateur sur machine sans helper DevStreet).
