from app.tests.projects_base import ProjectsAPITestCase


class ContributionRoutesTests(ProjectsAPITestCase):
    def test_manual_task_workflow_and_public_visibility(self):
        project = self.project()
        path = f"/api/v1/projects/{project.pk}/tasks"
        response = self.client.post(
            path,
            {"title": "Export CSV", "acceptance_criteria": ["CSV lisible"]},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        task_id = response.data["id"]
        self.assertEqual(response.data["status"], "draft")
        self.login(self.moussa)
        self.assertEqual(
            self.client.get(f"/api/v1/contribution-tasks/{task_id}").status_code, 404
        )
        self.login(self.aicha)
        self.assertEqual(
            self.client.patch(
                f"/api/v1/contribution-tasks/{task_id}",
                {"status": "open"},
                format="json",
            ).status_code,
            200,
        )
        self.login(self.moussa)
        self.assertEqual(
            self.client.get(f"/api/v1/contribution-tasks/{task_id}").status_code, 200
        )
        self.assertEqual(self.client.get(path).data["count"], 1)

    def test_task_requires_maintainer_and_acceptance_criteria(self):
        project = self.project()
        self.login(self.moussa)
        self.assertEqual(
            self.client.post(
                f"/api/v1/projects/{project.pk}/tasks", {"title": "Vol"}, format="json"
            ).status_code,
            403,
        )
        self.login(self.aicha)
        task = self.task(project, status="draft")
        task.acceptance_criteria = []
        task.save()
        self.assertEqual(
            self.client.patch(
                f"/api/v1/contribution-tasks/{task.pk}",
                {"status": "open"},
                format="json",
            ).status_code,
            400,
        )

    def submit(self):
        self.task_obj = self.task()
        self.login(self.moussa)
        response = self.client.post(
            f"/api/v1/contribution-tasks/{self.task_obj.pk}/contributions",
            {"summary": "Export CSV ajouté", "pull_request_number": 1},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        return response.data["id"]

    def test_submission_and_review_appear_on_profile_and_evidence(self):
        pk = self.submit()
        self.assertEqual(
            self.client.get(f"/api/v1/project-evidence/{pk}").status_code, 404
        )
        self.login(self.aicha)
        response = self.client.post(
            f"/api/v1/contributions/{pk}/review",
            {"status": "accepted", "note": "Export relu"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["validation_kind"], "maintainer_review")
        profile = self.client.get(f"/api/v1/project-profiles/{self.moussa.pk}")
        self.assertEqual(profile.data["contributions"][0]["id"], pk)
        self.assertEqual(
            self.client.get(f"/api/v1/project-evidence/{pk}").status_code, 404
        )
        self.login(self.moussa)
        self.assertEqual(
            self.client.get(f"/api/v1/project-evidence/{pk}").status_code, 200
        )

    def test_review_requires_another_maintainer_and_is_final(self):
        pk = self.submit()
        self.assertEqual(
            self.client.post(
                f"/api/v1/contributions/{pk}/review",
                {"status": "accepted", "note": "Oui"},
                format="json",
            ).status_code,
            403,
        )
        self.login(self.aicha)
        path = f"/api/v1/contributions/{pk}/review"
        self.assertEqual(
            self.client.post(
                path, {"status": "accepted", "note": " "}, format="json"
            ).status_code,
            400,
        )
        self.assertEqual(
            self.client.post(
                path, {"status": "rejected", "note": "À revoir"}, format="json"
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(
                path, {"status": "accepted", "note": "Final"}, format="json"
            ).status_code,
            409,
        )

    def test_self_review_denied_even_to_project_owner(self):
        task = self.task()
        pk = self.client.post(
            f"/api/v1/contribution-tasks/{task.pk}/contributions",
            {"summary": "Mon travail"},
            format="json",
        ).data["id"]
        self.assertEqual(
            self.client.post(
                f"/api/v1/contributions/{pk}/review",
                {"status": "accepted", "note": "Moi"},
                format="json",
            ).status_code,
            403,
        )

    def test_draft_or_closed_task_rejects_contribution(self):
        task = self.task(status="closed")
        self.login(self.moussa)
        self.assertEqual(
            self.client.post(
                f"/api/v1/contribution-tasks/{task.pk}/contributions",
                {"summary": "Travail"},
                format="json",
            ).status_code,
            409,
        )

    def test_private_submission_hidden_from_unrelated_users(self):
        pk = self.submit()
        self.login(self.outsider)
        self.assertEqual(
            self.client.get(f"/api/v1/contributions/{pk}").status_code, 404
        )
        self.assertEqual(self.client.get("/api/v1/contributions").data["count"], 0)

    def test_archived_project_no_longer_provides_selectable_evidence(self):
        pk = self.submit()
        self.login(self.aicha)
        self.client.post(
            f"/api/v1/contributions/{pk}/review",
            {"status": "accepted", "note": "Relu"},
            format="json",
        )
        self.client.post(f"/api/v1/projects/{self.task_obj.project_id}/archive")
        self.login(self.moussa)
        self.assertEqual(
            self.client.get(f"/api/v1/project-evidence/{pk}").status_code, 404
        )

    def test_contribution_status_cannot_be_set_by_author(self):
        task = self.task()
        self.login(self.moussa)
        response = self.client.post(
            f"/api/v1/contribution-tasks/{task.pk}/contributions",
            {"summary": "Travail", "status": "accepted", "reviewed_by": self.aicha.pk},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "submitted")
