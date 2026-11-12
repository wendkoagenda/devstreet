"""Construit une collection de parcours, sans secret et sans dépendance frontend."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
requests = []


def request(
    name,
    method,
    path,
    expected=200,
    body=None,
    token="owner_access",
    capture=None,
    script=(),
    pre=(),
):
    item = {
        "name": name,
        "request": {
            "method": method,
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "url": "{{base_url}}" + path,
        },
    }
    if token:
        item["request"]["auth"] = {
            "type": "bearer",
            "bearer": [
                {"key": "token", "value": "{{" + token + "}}", "type": "string"}
            ],
        }
    else:
        item["request"]["auth"] = {"type": "noauth"}
    if body is not None:
        item["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(body, ensure_ascii=False),
        }
    tests = [
        f"pm.test('HTTP {expected}', () => pm.response.to.have.status({expected}));"
    ]
    if capture:
        for key, field in capture.items():
            tests.append(
                f"pm.collectionVariables.set('{key}', pm.response.json().{field});"
            )
    tests.extend(script)
    item["event"] = [
        {"listen": "test", "script": {"type": "text/javascript", "exec": tests}}
    ]
    if pre:
        item["event"].append(
            {
                "listen": "prerequest",
                "script": {"type": "text/javascript", "exec": list(pre)},
            }
        )
    requests.append(item)
    return item


request(
    "01 - Santé",
    "GET",
    "/api/health",
    token=None,
    pre=[
        "pm.collectionVariables.set('run', Date.now().toString());",
        "pm.collectionVariables.set('request_key', pm.variables.replaceIn('{{$guid}}'));",
        "pm.collectionVariables.set('delivery_id', pm.variables.replaceIn('{{$guid}}'));",
    ],
)
request("02 - Schéma Swagger réel", "GET", "/swagger.json/", token=None)
request(
    "03 - Création anonyme interdite",
    "POST",
    "/api/v1/projects",
    401,
    {"title": "Refus", "slug": "refus-{{run}}"},
    token=None,
)
request(
    "04 - Créer une technologie",
    "POST",
    "/api/v1/technologies",
    201,
    {"label": "Python {{run}}", "slug": "python-{{run}}"},
    capture={"technology_id": "id"},
)
request("05 - Catalogue technologies", "GET", "/api/v1/technologies")
request("06 - Détail technologie", "GET", "/api/v1/technologies/{{technology_id}}")
request(
    "07 - Modifier technologie PATCH",
    "PATCH",
    "/api/v1/technologies/{{technology_id}}",
    body={"label": "Python"},
)
request(
    "08 - Modifier technologie PUT",
    "PUT",
    "/api/v1/technologies/{{technology_id}}",
    body={"label": "Python", "slug": "python-{{run}}"},
)
request(
    "09 - Créer le projet Aïcha",
    "POST",
    "/api/v1/projects",
    201,
    {
        "title": "Stock {{run}}",
        "slug": "stock-{{run}}",
        "declared_license": "MIT",
        "technologies": ["{{technology_id}}"],
    },
    capture={"project_id": "id"},
)
request(
    "10 - Recherche de projets",
    "GET",
    "/api/v1/projects?search=Stock&technology=python-{{run}}",
)
request("11 - Fiche projet", "GET", "/api/v1/projects/{{project_id}}")
request(
    "12 - Modifier présentation",
    "PATCH",
    "/api/v1/projects/{{project_id}}",
    body={"problem": "Suivre le stock et faciliter son export CSV"},
)
request("13 - Dépôt en attente", "GET", "/api/v1/projects/{{project_id}}/repository")
request(
    "14 - Publication trop tôt refusée",
    "POST",
    "/api/v1/projects/{{project_id}}/publish",
    409,
)
request("15 - Préparer accès Git technique", "POST", "/api/v1/forge-access")
request(
    "16 - Provisionner le vrai dépôt Gitea",
    "POST",
    "/api/v1/projects/{{project_id}}/provision",
    capture={"git_namespace": "namespace", "git_repository": "name"},
)
request("17 - Publier", "POST", "/api/v1/projects/{{project_id}}/publish")
request(
    "18 - Moussa étoile",
    "PUT",
    "/api/v1/projects/{{project_id}}/star",
    token="contributor_access",
)
request(
    "19 - Étoile idempotente",
    "PUT",
    "/api/v1/projects/{{project_id}}/star",
    token="contributor_access",
    script=[
        "pm.test('Une étoile', () => pm.expect(pm.response.json().star_count).to.eql(1));"
    ],
)
request(
    "20 - Retirer étoile",
    "DELETE",
    "/api/v1/projects/{{project_id}}/star",
    token="contributor_access",
)
request(
    "21 - Ajouter Moussa mainteneur",
    "POST",
    "/api/v1/projects/{{project_id}}/members",
    body={"user_id": "{{contributor_id}}", "role": "maintainer"},
)
request("22 - Lister membres", "GET", "/api/v1/projects/{{project_id}}/members")
request(
    "23 - Retirer droit métier",
    "DELETE",
    "/api/v1/projects/{{project_id}}/members/{{contributor_id}}",
    204,
)
request(
    "24 - Consentement aux extraits IA",
    "POST",
    "/api/v1/projects/{{project_id}}/ai-consent",
    body={"enabled": True},
)
request(
    "25 - IA non configurée : erreur explicite",
    "POST",
    "/api/v1/projects/{{project_id}}/analyses",
    503,
    {"objective": "Faciliter un export CSV", "language": "fr"},
)
request(
    "26 - Tâche manuelle",
    "POST",
    "/api/v1/projects/{{project_id}}/tasks",
    201,
    {
        "title": "Export CSV",
        "description": "Ajouter un export lisible",
        "acceptance_criteria": ["Un CSV lisible est produit"],
    },
    capture={"task_id": "id"},
)
request("27 - Tâches du projet", "GET", "/api/v1/projects/{{project_id}}/tasks")
request("28 - Catalogue tâches", "GET", "/api/v1/contribution-tasks")
request("29 - Détail tâche", "GET", "/api/v1/contribution-tasks/{{task_id}}")
request(
    "30 - Ouvrir tâche",
    "PATCH",
    "/api/v1/contribution-tasks/{{task_id}}",
    body={"status": "open"},
)
request(
    "31 - Soumettre réalisation Moussa",
    "POST",
    "/api/v1/contribution-tasks/{{task_id}}/contributions",
    201,
    {"summary": "Export CSV proposé pour revue humaine"},
    token="contributor_access",
    capture={"contribution_id": "id"},
)
request("32 - Lister contributions", "GET", "/api/v1/contributions")
request("33 - Détail contribution", "GET", "/api/v1/contributions/{{contribution_id}}")
request(
    "34 - Auto-revue refusée",
    "POST",
    "/api/v1/contributions/{{contribution_id}}/review",
    403,
    {"status": "accepted", "note": "Moi-même"},
    token="contributor_access",
)
request(
    "35 - Aïcha accepte avec motif",
    "POST",
    "/api/v1/contributions/{{contribution_id}}/review",
    body={"status": "accepted", "note": "Réalisation revue par le mainteneur"},
)
request(
    "36 - Réalisations du profil", "GET", "/api/v1/project-profiles/{{contributor_id}}"
)
request(
    "37 - Preuve sélectionnable Moussa",
    "GET",
    "/api/v1/project-evidence/{{contribution_id}}",
    token="contributor_access",
)
request(
    "38 - Preuve non sélectionnable Aïcha",
    "GET",
    "/api/v1/project-evidence/{{contribution_id}}",
    404,
)
request(
    "39 - Forum non raccordé explicite",
    "POST",
    "/api/v1/projects/{{project_id}}/discussions",
    503,
    {
        "title": "Comment exporter ?",
        "body": "Besoin de contexte",
        "task_id": "{{task_id}}",
        "request_key": "{{request_key}}",
    },
)
request("40 - Analyse absente", "GET", "/api/v1/analyses/999999", 404)
request(
    "41 - Adoption analyse absente",
    "POST",
    "/api/v1/projects/{{project_id}}/tasks/from-analysis",
    404,
    {"analysis_id": 999999, "suggestion_index": 0},
)
hook = {"repository": {"id": 999999}, "ref": "refs/heads/main", "after": "a" * 40}
for index in (42, 43):
    item = request(
        f"{index} - Webhook signé et dédoublonné",
        "POST",
        "/api/v1/integrations/gitea/webhook",
        body=hook,
        token=None,
        pre=[
            "var hookCrypto = require('crypto-js');",
            "const signature = hookCrypto.HmacSHA256(pm.request.body.raw, pm.environment.get('webhook_secret')).toString();",
            "pm.variables.set('webhook_signature', signature);",
        ],
    )
    item["request"]["header"].extend(
        [
            {"key": "X-Gitea-Signature", "value": "{{webhook_signature}}"},
            {"key": "X-Gitea-Delivery", "value": "{{delivery_id}}"},
            {"key": "X-Gitea-Event", "value": "push"},
        ]
    )
request(
    "44 - Révoquer consentement",
    "POST",
    "/api/v1/projects/{{project_id}}/ai-consent",
    body={"enabled": False},
)
request("45 - Archiver", "POST", "/api/v1/projects/{{project_id}}/archive")
request(
    "46 - Preuve archivée non sélectionnable",
    "GET",
    "/api/v1/project-evidence/{{contribution_id}}",
    404,
    token="contributor_access",
)
request(
    "47 - Technologie utilisée protégée",
    "DELETE",
    "/api/v1/technologies/{{technology_id}}",
    409,
)
request(
    "48 - Technologie libre à supprimer",
    "POST",
    "/api/v1/technologies",
    201,
    {"label": "Temporaire", "slug": "temp-{{run}}"},
    capture={"unused_technology_id": "id"},
)
request(
    "49 - Supprimer technologie libre",
    "DELETE",
    "/api/v1/technologies/{{unused_technology_id}}",
    204,
)
request(
    "50 - Connexion native boilerplate",
    "POST",
    "/api/auth/login",
    body={"email": "{{owner_email}}", "password": "{{password}}"},
    token=None,
)

directory = ROOT / "docs/chantier/testing"
directory.mkdir(parents=True, exist_ok=True)
collection = {
    "info": {
        "name": "Chantier - Backend P0",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        "description": "Parcours réel Django + Gitea ; IA et forum absents sont signalés explicitement. Le cas 25 suppose OpenAI non configuré.",
    },
    "item": requests,
}
(directory / "chantier.postman_collection.json").write_text(
    json.dumps(collection, ensure_ascii=False, indent=2), encoding="utf-8"
)
keys = (
    "base_url",
    "owner_access",
    "contributor_access",
    "owner_email",
    "password",
    "contributor_id",
    "webhook_secret",
)
environment = {
    "name": "Chantier local - modèle sans secrets",
    "values": [
        {
            "key": k,
            "value": "http://127.0.0.1:18000" if k == "base_url" else "",
            "enabled": True,
            "type": (
                "secret"
                if k
                in ("password", "owner_access", "contributor_access", "webhook_secret")
                else "default"
            ),
        }
        for k in keys
    ],
    "_postman_variable_scope": "environment",
}
(directory / "chantier.postman_environment.example.json").write_text(
    json.dumps(environment, indent=2), encoding="utf-8"
)
print(f"{len(requests)} requêtes Postman écrites dans docs/chantier/testing")
