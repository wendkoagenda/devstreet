"""Edition atomique de la presentation et suggestion explicitement non publiee."""
import json

from django.db import transaction
from rest_framework.exceptions import ValidationError

from app.core.services.audit_service import record
from app.devstreet_hub.permissions.policy import require_owner, require_permission
from app.devstreet_hub.services.errors import Conflict
from app.devstreet_hub.services.workflow_service import WorkflowService


class PresentationService:
    def __init__(self, workflow=None):
        self.workflow = workflow or WorkflowService()
        self.repo = self.workflow.repo

    def save(self, actor, project, data):
        require_permission(actor, 'projects.update')
        require_owner(actor, project)
        created = []
        try:
            with transaction.atomic():
                project = self.repo.locked_project(project.pk)
                if project.updated_at != data['base_updated_at']:
                    raise Conflict('La presentation a change. Rechargez le projet avant de reessayer.')
                existing = self.repo.project_images(project)
                removed = set(data['remove_image_ids'])
                if not removed <= {image.pk for image in existing}:
                    raise ValidationError('Image absente de ce projet.')
                if len(existing) - len(removed) + len(data['images']) > 4:
                    raise ValidationError('Quatre images maximum par projet.')
                for file in data['images']:
                    created.append(self.repo.create_project_image(project, file, file.display_name))
                self.repo.save(project, description=data['description'], problem=data['problem'], updated_by=actor.pk)
                for image in existing:
                    if image.pk in removed:
                        storage, name = image.file.storage, image.file.name
                        self.repo.delete_project_image(image)
                        transaction.on_commit(lambda s=storage, n=name: s.delete(n), robust=True)
                record('project.presentation_updated', actor=actor, target=project)
            return project
        except Exception:
            for image in created:
                image.file.storage.delete(image.file.name)
            raise

    def suggest(self, actor, project, description, language):
        require_permission(actor, 'projects.update')
        require_owner(actor, project)
        objective = json.dumps({
            'title': project.title,
            'problem': project.problem,
            'draft_description': description,
        }, ensure_ascii=False)
        return self.workflow.request_analysis(
            actor, project, objective, language, prompt_version='presentation-v1',
        )
