"""Exploration du dépôt via Django (pas d'iframe / pas de jeton admin côté client)."""

from app.devstreet_hub.services.errors import ExternalUnavailable
from app.tests.devstreet_hub_base import DevStreetHubAPITestCase


class ProjectCodeBrowseTests(DevStreetHubAPITestCase):
    def setUp(self):
        super().setUp()
        self.proj = self.project(status="published")
        self.forge.get_repository_meta.return_value = {
            "empty": False,
            "default_branch": "main",
            "description": "Dépôt de test",
            "size": 25,
        }
        self.forge.repo_is_empty.return_value = False
        self.forge.list_branches.return_value = [
            {
                "name": "main",
                "commit": {
                    "id": "a" * 40,
                    "message": "feat: initial",
                    "author": {"name": "Forge User", "date": "2026-11-12T10:00:00Z"},
                },
            }
        ]
        self.forge.list_tags.return_value = []
        self.forge.get_languages.return_value = {"HTML": 1000}
        self.forge.count_commits.return_value = 1
        self.forge.latest_commit.return_value = {
            "sha": "a" * 40,
            "commit": {
                "message": "feat: initial commit - test\n",
                "author": {"name": "Forge User", "date": "2026-11-12T10:00:00Z"},
            },
        }
        self.forge.get_contents.return_value = [
            {
                "name": "index.html",
                "path": "index.html",
                "type": "file",
                "size": 42,
                "sha": "b" * 40,
            },
            {
                "name": "README.md",
                "path": "README.md",
                "type": "file",
                "size": 20,
                "sha": "c" * 40,
            },
        ]
        self.forge.get_raw_blob.side_effect = lambda repository, *, path, ref: (
            b"# Hello\n<script>alert(1)</script>\n"
            if path == "README.md"
            else b"<html><body>Hi</body></html>"
        )

    def test_summary_and_tree_for_visible_project(self):
        summary = self.client.get(f"/api/v1/projects/{self.proj.pk}/code/summary")
        self.assertEqual(summary.status_code, 200, summary.data)
        self.assertEqual(summary.data["default_branch"], "main")
        self.assertFalse(summary.data["is_empty"])
        self.assertEqual(summary.data["stats"]["branches"], 1)
        self.assertEqual(summary.data["languages"][0]["name"], "HTML")
        self.assertNotIn("stars_count", summary.data)
        self.assertNotIn("stars", summary.data)

        tree = self.client.get(
            f"/api/v1/projects/{self.proj.pk}/code/tree",
            {"ref": "main", "path": ""},
        )
        self.assertEqual(tree.status_code, 200, tree.data)
        names = [e["name"] for e in tree.data["entries"]]
        self.assertIn("index.html", names)
        self.assertEqual(tree.data["readme"]["name"], "README.md")
        self.assertIn("# Hello", tree.data["readme"]["content"])
        self.assertEqual(tree.data["latest_commit"]["author_name"], "Forge User")

    def test_blob_returns_html_as_text_not_executed(self):
        self.forge.get_contents.return_value = {
            "name": "index.html",
            "path": "index.html",
            "type": "file",
            "size": 28,
            "sha": "b" * 40,
        }
        blob = self.client.get(
            f"/api/v1/projects/{self.proj.pk}/code/blob",
            {"ref": "main", "path": "index.html"},
        )
        self.assertEqual(blob.status_code, 200, blob.data)
        self.assertEqual(blob.data["encoding"], "utf-8")
        self.assertFalse(blob.data["is_binary"])
        self.assertIn("<html>", blob.data["content"])
        self.assertEqual(blob.data["language"], "html")

    def test_blob_rejects_directory_and_missing_file(self):
        self.forge.get_contents.return_value = [
            {"name": "src", "path": "src", "type": "dir"}
        ]
        self.assertEqual(
            self.client.get(
                f"/api/v1/projects/{self.proj.pk}/code/blob",
                {"ref": "main", "path": "src"},
            ).status_code,
            404,
        )
        self.forge.get_contents.return_value = None
        self.assertEqual(
            self.client.get(
                f"/api/v1/projects/{self.proj.pk}/code/blob",
                {"ref": "main", "path": "missing.txt"},
            ).status_code,
            404,
        )

    def test_private_draft_hidden_from_outsider(self):
        draft = self.project(status="draft", owner=self.aicha)
        self.login(self.outsider)
        self.assertEqual(
            self.client.get(f"/api/v1/projects/{draft.pk}/code/summary").status_code,
            404,
        )

    def test_branch_with_slash_accepted_via_query(self):
        self.forge.get_contents.return_value = []
        response = self.client.get(
            f"/api/v1/projects/{self.proj.pk}/code/tree",
            {"ref": "feature/login", "path": "src/app"},
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["ref"], "feature/login")
        self.assertEqual(response.data["path"], "src/app")

    def test_invalid_ref_rejected(self):
        self.assertEqual(
            self.client.get(
                f"/api/v1/projects/{self.proj.pk}/code/tree",
                {"ref": "../etc"},
            ).status_code,
            400,
        )

    def test_forge_unavailable_returns_503(self):
        self.forge.get_repository_meta.side_effect = ExternalUnavailable()
        self.assertEqual(
            self.client.get(f"/api/v1/projects/{self.proj.pk}/code/summary").status_code,
            503,
        )

    def test_empty_repository_summary(self):
        self.forge.get_repository_meta.return_value = {
            "empty": True,
            "default_branch": "main",
            "size": 0,
        }
        self.forge.repo_is_empty.return_value = True
        response = self.client.get(f"/api/v1/projects/{self.proj.pk}/code/summary")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_empty"])
        self.assertEqual(response.data["stats"]["branches"], 0)
