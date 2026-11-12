"""Worker borné ; le contexte est toujours prélevé au SHA enregistré lors de la demande."""

import hashlib
import json
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import APIException
from pydantic import ValidationError
from app.devstreet_hub.repositories.workflow_repository import WorkflowRepository
from app.devstreet_hub.services.gitea_client import GiteaClient
from app.devstreet_hub.services.openai_client import OpenAIClient, validate_brief


def process_next(*, repository=None, forge=None, ai=None):
    repo = repository or WorkflowRepository()
    with transaction.atomic():
        repo.expire_jobs()
        job = repo.claim_job()
    if job is None:
        return None
    try:
        if not job.project.ai_consent_at or job.project.status == "archived":
            raise ValueError("consent_revoked")
        forge = forge or GiteaClient()
        sources = forge.collect_sources(job.project.repository, job.commit_sha)
        digest = hashlib.sha256(
            json.dumps(sources, sort_keys=True).encode()
        ).hexdigest()
        snapshot = repo.snapshot(
            job.project.repository, job.commit_sha, sources, digest
        )
        result, input_tokens, output_tokens = (ai or OpenAIClient()).generate(
            job.objective, job.language, snapshot.sources, job.model
        )
        result = validate_brief(result, snapshot.sources)
        with transaction.atomic():
            # Un consentement révoqué pendant l'appel empêche aussi la conservation du résultat.
            current = repo.locked_project(job.project_id)
            if not current.ai_consent_at or current.status == "archived":
                raise ValueError("consent_revoked")
            repo.save(
                job,
                snapshot=snapshot,
                result=result,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                status="succeeded",
                finished_at=timezone.now(),
            )
    except (APIException, ValidationError, ValueError, KeyError, TypeError) as error:
        code = (
            "consent_revoked" if str(error) == "consent_revoked" else "analysis_failed"
        )
        repo.save(
            job, result={}, error_code=code, status="failed", finished_at=timezone.now()
        )
    return job
