import base64
import hashlib
import hmac
import json
import uuid
from unittest.mock import Mock, patch
import httpx
from django.test import SimpleTestCase, override_settings
from django.utils import timezone
from app.projects.models import AIAnalysis, ProjectDiscussionLink
from app.projects.services.analysis_worker import process_next
from app.projects.services.errors import Conflict, ExternalUnavailable
from app.projects.services.gitea_client import GiteaClient
from app.projects.services.openai_client import validate_brief
from app.tests.projects_base import ProjectsAPITestCase

SOURCES = [
    {
        "source_id": "src_01",
        "path": "stock/export.py",
        "content": "def export():\n    return []\n",
    }
]
BRIEF = {
    "summary": "Un export de stock.",
    "entry_points": [
        {
            "source_id": "src_01",
            "line_start": 1,
            "line_end": 2,
            "reason": "Point d’entrée",
        }
    ],
    "suggested_tasks": [
        {
            "title": "Exporter en CSV",
            "description": "Proposition à relire",
            "source_ids": ["src_01"],
            "steps": ["Lire export", "Ajouter CSV"],
            "acceptance_criteria": ["CSV valide"],
        }
    ],
    "unknowns": ["Tests non exécutés"],
}


@override_settings(
    PROJECTS_OPENAI_API_KEY="test-only-key", PROJECTS_OPENAI_MODEL="model-test"
)
class AnalysisRoutesTests(ProjectsAPITestCase):
    def prepared_project(self):
        project = self.project()
        project.ai_consent_at = timezone.now()
        project.save()
        return project

    def request_analysis(self, project, objective="Exporter en CSV"):
        return self.client.post(
            f"/api/v1/projects/{project.pk}/analyses",
            {"objective": objective, "language": "fr"},
            format="json",
        )

    def test_analysis_requires_consent_and_maintainer(self):
        project = self.project()
        self.assertEqual(self.request_analysis(project).status_code, 409)
        self.login(self.moussa)
        self.assertEqual(self.request_analysis(project).status_code, 403)

    @override_settings(PROJECTS_OPENAI_API_KEY="")
    def test_unconfigured_ai_returns_503_without_job(self):
        project = self.prepared_project()
        self.assertEqual(self.request_analysis(project).status_code, 503)
        self.assertEqual(AIAnalysis.objects.count(), 0)

    def test_analysis_cached_and_quotas_enforced(self):
        project = self.prepared_project()
        first = self.request_analysis(project)
        self.assertEqual(first.status_code, 202, first.data)
        self.assertEqual(self.request_analysis(project).data["id"], first.data["id"])
        self.assertEqual(
            self.request_analysis(project, "Autre objectif").status_code, 202
        )
        self.assertEqual(
            self.request_analysis(project, "Troisième objectif").status_code, 429
        )
        self.assertEqual(AIAnalysis.objects.count(), 2)

    @override_settings(PROJECTS_AI_DAILY_LIMIT=1)
    def test_requester_quota_is_shared_between_projects(self):
        self.assertEqual(
            self.request_analysis(self.prepared_project()).status_code, 202
        )
        self.assertEqual(
            self.request_analysis(self.prepared_project()).status_code, 429
        )

    def test_queued_job_is_private(self):
        project = self.prepared_project()
        pk = self.request_analysis(project).data["id"]
        self.assertEqual(self.client.get(f"/api/v1/analyses/{pk}").status_code, 200)
        self.login(self.moussa)
        self.assertEqual(self.client.get(f"/api/v1/analyses/{pk}").status_code, 404)

    def test_worker_uses_original_sha_and_leaves_task_as_draft(self):
        project = self.prepared_project()
        pk = self.request_analysis(project).data["id"]
        forge = Mock()
        forge.collect_sources.return_value = SOURCES
        ai = Mock()
        ai.generate.return_value = (BRIEF, 100, 60)
        job = process_next(forge=forge, ai=ai)
        self.assertEqual(job.pk, pk)
        self.assertEqual(job.status, "succeeded")
        forge.collect_sources.assert_called_once_with(project.repository, "a" * 40)
        result = self.client.get(f"/api/v1/analyses/{pk}").data
        self.assertEqual(
            result["sources"], [{"source_id": "src_01", "path": "stock/export.py"}]
        )
        response = self.client.post(
            f"/api/v1/projects/{project.pk}/tasks/from-analysis",
            {"analysis_id": pk, "suggestion_index": 0},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["status"], "draft")
        self.assertEqual(self.request_analysis(project).status_code, 200)

    def test_worker_rejects_hallucinated_references(self):
        project = self.prepared_project()
        self.request_analysis(project)
        forge = Mock()
        forge.collect_sources.return_value = SOURCES
        ai = Mock()
        broken = json.loads(json.dumps(BRIEF))
        broken["entry_points"][0]["source_id"] = "unknown"
        ai.generate.return_value = (broken, 100, 60)
        job = process_next(forge=forge, ai=ai)
        self.assertEqual(job.status, "failed")
        self.assertEqual(job.result, {})

    def test_empty_depot_failure_and_revoked_consent_preserve_manual_creation(self):
        project = self.prepared_project()
        self.request_analysis(project)
        forge = Mock()
        forge.collect_sources.side_effect = Conflict("Vide")
        self.assertEqual(process_next(forge=forge).status, "failed")
        self.assertEqual(
            self.client.post(
                f"/api/v1/projects/{project.pk}/tasks",
                {"title": "Tâche manuelle"},
                format="json",
            ).status_code,
            201,
        )
        self.request_analysis(project)
        project.ai_consent_at = None
        project.save()
        job = process_next(forge=forge)
        self.assertEqual(job.error_code, "consent_revoked")

    def test_suggestion_from_another_project_rejected(self):
        project = self.prepared_project()
        analysis = AIAnalysis.objects.create(
            project=self.prepared_project(),
            requested_by=self.aicha,
            objective="Export",
            status="succeeded",
            commit_sha="a" * 40,
            cache_key="b" * 64,
            model="test",
            result=BRIEF,
        )
        result = self.client.post(
            f"/api/v1/projects/{project.pk}/tasks/from-analysis",
            {"analysis_id": analysis.pk, "suggestion_index": 0},
            format="json",
        )
        self.assertEqual(result.status_code, 400)


def fake_forum(**kwargs):
    return "forum-topic-" + kwargs["request_key"]


class CrossModuleTests(ProjectsAPITestCase):
    def payload(self):
        return {
            "request_key": str(uuid.uuid4()),
            "title": "Comment exporter ?",
            "body": "Question contextualisée",
        }

    def test_missing_forum_is_explicit_not_a_fake_success(self):
        project = self.project()
        response = self.client.post(
            f"/api/v1/projects/{project.pk}/discussions", self.payload(), format="json"
        )
        self.assertEqual(response.status_code, 503)
        self.assertFalse(ProjectDiscussionLink.objects.exists())

    @override_settings(
        PROJECTS_FORUM_ADAPTER="app.tests.test_projects_integrations.fake_forum"
    )
    def test_discussion_link_is_idempotent_and_scoped(self):
        project = self.project()
        path = f"/api/v1/projects/{project.pk}/discussions"
        payload = self.payload()
        first = self.client.post(path, payload, format="json")
        self.assertEqual(first.status_code, 201, first.data)
        self.assertEqual(
            self.client.post(path, payload, format="json").data["id"], first.data["id"]
        )
        self.assertEqual(
            self.client.post(
                path, {**payload, "title": "Autre"}, format="json"
            ).status_code,
            409,
        )
        self.assertEqual(ProjectDiscussionLink.objects.count(), 1)

    @override_settings(
        PROJECTS_FORUM_ADAPTER="app.tests.test_projects_integrations.fake_forum"
    )
    def test_discussion_cannot_link_task_from_other_project(self):
        project = self.project()
        task = self.task(self.project())
        response = self.client.post(
            f"/api/v1/projects/{project.pk}/discussions",
            {**self.payload(), "task_id": task.pk},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    @override_settings(PROJECTS_GITEA_WEBHOOK_SECRET="hook-test-secret")
    def test_webhook_signature_delivery_deduplication_and_push(self):
        project = self.project()
        body = json.dumps(
            {
                "repository": {"id": project.repository.gitea_repo_id},
                "ref": "refs/heads/main",
                "after": "b" * 40,
            }
        ).encode()
        signature = hmac.new(b"hook-test-secret", body, hashlib.sha256).hexdigest()
        self.client.force_authenticate(None)
        headers = {
            "HTTP_X_GITEA_SIGNATURE": signature,
            "HTTP_X_GITEA_DELIVERY": str(uuid.uuid4()),
            "HTTP_X_GITEA_EVENT": "push",
        }
        path = "/api/v1/integrations/gitea/webhook"
        self.assertEqual(
            self.client.post(
                path, body, content_type="application/json", **headers
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                path, body, content_type="application/json", **headers
            ).data,
            {"duplicate": True},
        )
        project.repository.refresh_from_db()
        self.assertEqual(project.repository.current_sha, "b" * 40)
        self.assertEqual(
            self.client.post(path, body, content_type="application/json").status_code,
            403,
        )

    def test_swagger_includes_workflow_request_bodies(self):
        self.client.force_authenticate(None)
        response = self.client.get("/swagger.json/")
        self.assertEqual(response.status_code, 200)
        schema = json.loads(response.content)
        paths = schema["paths"]
        self.assertIn("/v1/projects", paths)
        self.assertIn("/v1/projects/{id}/analyses", paths)
        self.assertIn("/v1/contributions/{id}/review", paths)
        self.assertTrue(
            any(p["in"] == "body" for p in paths["/v1/projects"]["post"]["parameters"])
        )


@override_settings(
    DEBUG=True,
    PROJECTS_GITEA_URL="http://127.0.0.1:13000",
    PROJECTS_GITEA_TOKEN="test-token",
)
class GiteaAdapterTests(SimpleTestCase):
    def client_mock(self, handler):
        original = httpx.Client
        return patch(
            "app.projects.services.gitea_client.httpx.Client",
            side_effect=lambda **kwargs: original(
                transport=httpx.MockTransport(handler), **kwargs
            ),
        )

    def test_gitea_token_stays_in_header_and_redirect_is_not_followed(self):
        calls = []

        def handler(request):
            calls.append(request)
            return httpx.Response(
                302, headers={"location": "https://unexpected.example/"}
            )

        with self.client_mock(handler), self.assertRaises(ExternalUnavailable):
            GiteaClient().request("GET", "/version")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].headers["authorization"], "token test-token")
        self.assertNotIn("test-token", str(calls[0].url))

    @override_settings(DEBUG=False)
    def test_production_rejects_unencrypted_forge_url(self):
        with self.assertRaises(ExternalUnavailable):
            GiteaClient()

    def test_source_collector_excludes_sensitive_files_and_preserves_lines(self):
        entries = [
            {"path": ".env", "type": "blob", "sha": "1", "size": 10},
            {"path": "README.md", "type": "blob", "sha": "2", "size": 8},
            {"path": "settings.py", "type": "blob", "sha": "3", "size": 30},
        ]

        def handler(request):
            if "/trees/" in request.url.path:
                return httpx.Response(200, json={"tree": entries, "truncated": False})
            text = (
                "Intro\nCode\n"
                if request.url.path.endswith("/2")
                else "PASSWORD=private\n"
            )
            return httpx.Response(
                200, json={"content": base64.b64encode(text.encode()).decode()}
            )

        repository = Mock(namespace="owner")
        repository.name = "project-1"
        with self.client_mock(handler):
            sources = GiteaClient().collect_sources(repository, "a" * 40)
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["path"], "README.md")
        self.assertEqual(len(sources[0]["content"].splitlines()), 2)

    def test_schema_valid_json_still_needs_citation_validation(self):
        self.assertEqual(validate_brief(BRIEF, SOURCES)["summary"], BRIEF["summary"])
        broken = json.loads(json.dumps(BRIEF))
        broken["entry_points"][0]["line_end"] = 999
        with self.assertRaises(Conflict):
            validate_brief(broken, SOURCES)
