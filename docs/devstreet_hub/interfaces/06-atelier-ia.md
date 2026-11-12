# 06 — Préparer une contribution avec l’IA

**Statut : à réaliser.** Un atelier guidé, centré sur une tâche à publier après relecture.

## À regrouper

Objectif du mainteneur, choix FR/EN, autorisation d’envoi des extraits par le propriétaire, demande de génération, progression, résultat sourcé, inconnues et adoption d’une suggestion. Le rendu est une fiche de travail, pas un chat vide.

| Route | Intégration |
| --- | --- |
| GET /api/v1/projects/{id} | Consentement, état du projet et dépôt |
| POST /api/v1/projects/{id}/ai-consent | Propriétaire : enabled true/false, avec explication de l’envoi externe |
| POST /api/v1/projects/{id}/analyses | Objectif et langue ; 202 en attente, 200 si résultat exact déjà disponible |
| GET /api/v1/analyses/{id} | Lecture périodique avec délai croissant et arrêt sur succeeded/failed ; aucune boucle infinie |
| POST /api/v1/projects/{id}/tasks/from-analysis | analysis_id + suggestion_index ; crée un brouillon, jamais une tâche ouverte automatiquement |
| PATCH /api/v1/contribution-tasks/{id} | Relire/modifier le brouillon puis ouvrir explicitement |
| POST /api/v1/projects/{id}/tasks | Solution manuelle toujours proposée si la génération est impossible |

## UX proposée

Prendre l’exemple concret « Ajouter un export CSV » comme aide de saisie, sans préremplir de données prétendument détectées. Afficher une progression honnête : « En attente », « Analyse des extraits », puis résultat ; aucune animation ne prétend que des tests sont exécutés.

Résultat : résumé, points d’entrée avec références, une à trois suggestions, étapes, critères et inconnues. Afficher la version analysée et le nom du modèle dans un panneau secondaire. Une action « En faire une tâche à relire » conduit au brouillon éditable. Si le projet a évolué, signaler la différence de version ; ne pas présenter les sources historiques comme le code courant.

503 : service non configuré/indisponible, créer manuellement. 429 : quota atteint, pas de retry automatique. Échec : ne pas afficher une réponse partielle comme un succès. La clé API n’est jamais demandée dans cet écran produit.

## Terminé lorsque

Le propriétaire comprend ce qui est envoyé ; une génération ne publie rien ; références et limites sont visibles ; le parcours manuel reste utilisable ; aucun texte ne promet une compétence, un audit ou un résultat de test non effectué.
