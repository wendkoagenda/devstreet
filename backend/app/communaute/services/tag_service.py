"""
Service tags forum : thèmes optionnels + suivi (« Mes favoris »).

Les suivis sont persistés en base par utilisateur (SuiviTag), pas en session.
Les libellés libres sont normalisés et rattachés à un tag canonique existant
quand c'est possible (# ia / #AI / #ai → même slug).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Count, QuerySet
from django.utils.text import slugify

from app.communaute.models import Publication, SuiviTag, Tag

User = get_user_model()

MAX_TAGS_PER_PUBLICATION = 3
LABEL_MAX = 48
SLUG_MAX = 64
# Alias courants → slug canonique (évite la dispersion ia/ai/ml…).
TAG_ALIASES = {
    'ia': 'ai',
    'a-i': 'ai',
    'artificial-intelligence': 'ai',
    'intelligence-artificielle': 'ai',
    'ml': 'machine-learning',
    'machinelearning': 'machine-learning',
    'llm': 'llm',
    'llms': 'llm',
    'gpt': 'llm',
    'embedding': 'embeddings',
    'embeddings': 'embeddings',
    'vector': 'embeddings',
    'vectors': 'embeddings',
    'model': 'models',
    'models': 'models',
    'modele': 'models',
    'modeles': 'models',
    'ts': 'typescript',
    'js': 'javascript',
    'py': 'python',
    'golang': 'go',
    'k8s': 'kubernetes',
    'kube': 'kubernetes',
}


class TagService:
    """Logique métier des tags de publication."""

    def normalize_label(self, raw: str) -> str:
        """Nettoie un libellé saisi (# ia, AI, etc.)."""
        cleaned = re.sub(r'[\s_]+', ' ', (raw or '').strip())
        cleaned = cleaned.lstrip('#').strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)
        if not cleaned:
            raise ValidationError('Tag vide.')
        if len(cleaned) > LABEL_MAX:
            raise ValidationError(f'Tag trop long (max {LABEL_MAX}).')
        # Lettres, chiffres, espaces, tirets, + . seulement.
        if not re.fullmatch(r'[\w.+ -]+', cleaned, flags=re.UNICODE):
            raise ValidationError(
                'Tag invalide : utilise des lettres, chiffres ou tirets.'
            )
        return cleaned

    def slug_for(self, label: str) -> str:
        slug = slugify(label)
        if not slug or len(slug) < 2:
            raise ValidationError(f'Tag invalide : {label}')
        return slug[:SLUG_MAX]

    def compact_key(self, value: str) -> str:
        """Clé de rapprochement : sans tirets ni espaces (aiinfra == ai-infra)."""
        return re.sub(r'[^a-z0-9]', '', (value or '').lower())

    def canonical_slug(self, label: str) -> str:
        slug = self.slug_for(label)
        alias = TAG_ALIASES.get(slug) or TAG_ALIASES.get(self.compact_key(slug))
        return alias or slug

    def _find_existing(self, slug: str) -> Optional[Tag]:
        """Retrouve un tag existant par slug, alias ou forme compacte."""
        candidates = [slug]
        compact = self.compact_key(slug)
        aliased = TAG_ALIASES.get(slug) or TAG_ALIASES.get(compact)
        if aliased:
            candidates.append(aliased)
        if compact and compact != slug:
            candidates.append(compact)

        for candidate in candidates:
            hit = Tag.objects.filter(slug=candidate).first()
            if hit is not None:
                return hit

        # aiinfra ↔ ai-infra : compare la forme compacte en Python sur un sous-ensemble.
        if compact:
            for tag in Tag.objects.filter(slug__icontains=compact[:12]).only(
                'id', 'label', 'slug'
            )[:80]:
                if self.compact_key(tag.slug) == compact:
                    return tag

        # Pluriel naïf : models ↔ model
        if slug.endswith('s') and len(slug) > 3:
            singular = Tag.objects.filter(slug=slug[:-1]).first()
            if singular is not None:
                return singular
        else:
            plural = Tag.objects.filter(slug=f'{slug}s').first()
            if plural is not None:
                return plural

        return None

    def get_or_create(self, label: str, *, acteur_id: int = 0) -> Tag:
        cleaned = self.normalize_label(label)
        slug = self.canonical_slug(cleaned)
        existing = self._find_existing(slug)
        if existing is not None:
            return existing

        tag, _created = Tag.objects.get_or_create(
            slug=slug,
            defaults={
                'label': cleaned,
                'created_by': acteur_id,
                'updated_by': acteur_id,
            },
        )
        return tag

    def resolve_labels(
        self,
        labels: Optional[List[str]],
        *,
        acteur_id: int = 0,
        max_tags: int = MAX_TAGS_PER_PUBLICATION,
    ) -> List[Tag]:
        if not labels:
            return []
        if len(labels) > max_tags:
            raise ValidationError(f'Maximum {max_tags} tags par publication.')
        seen: Set[str] = set()
        tags: List[Tag] = []
        for raw in labels:
            tag = self.get_or_create(raw, acteur_id=acteur_id)
            if tag.slug in seen:
                continue
            seen.add(tag.slug)
            tags.append(tag)
        return tags

    def ensure_suivi(self, *, membre: User, tag: Tag) -> None:
        """Persiste le suivi pour ce membre (idempotent)."""
        if membre is None or not getattr(membre, 'id', None):
            return
        SuiviTag.objects.get_or_create(
            membre_id=membre.id,
            tag_id=tag.id,
            defaults={
                'created_by': membre.id,
                'updated_by': membre.id,
            },
        )

    def set_publication_tags(
        self,
        publication: Publication,
        labels: Optional[List[str]],
        *,
        acteur_id: int,
        auto_follow: bool = True,
        membre: Optional[User] = None,
    ) -> None:
        tags = self.resolve_labels(labels, acteur_id=acteur_id)
        publication.tags.set(tags)
        if auto_follow and tags:
            user = membre
            if user is None and acteur_id:
                user = User.objects.filter(id=acteur_id).first()
            if user is not None:
                for tag in tags:
                    self.ensure_suivi(membre=user, tag=tag)

    def list_tags(
        self,
        *,
        search: Optional[str] = None,
        limit: int = 30,
    ) -> QuerySet:
        qs = Tag.objects.annotate(
            publications_count=Count('publications', distinct=True),
            suivis_count=Count('suivis', distinct=True),
        ).order_by('-suivis_count', '-publications_count', 'label')
        cleaned = (search or '').strip().lstrip('#')
        if cleaned:
            slug_q = slugify(cleaned)
            from django.db.models import Q

            query = Q(label__icontains=cleaned)
            if slug_q:
                query |= Q(slug__icontains=slug_q)
            compact = self.compact_key(cleaned)
            if compact:
                query |= Q(slug__icontains=compact[:24])
            qs = qs.filter(query).distinct()
        return qs[: max(1, min(int(limit or 30), 100))]

    def list_suivis(self, membre: User) -> List[Tag]:
        if membre is None or not getattr(membre, 'id', None):
            return []
        return list(
            Tag.objects.filter(suivis__membre_id=membre.id)
            .annotate(publications_count=Count('publications', distinct=True))
            .order_by('label')
        )

    def ids_suivis(self, membre: Optional[User]) -> List[int]:
        if membre is None or not getattr(membre, 'id', None):
            return []
        return list(
            SuiviTag.objects.filter(membre_id=membre.id).values_list(
                'tag_id', flat=True
            )
        )

    def toggle_suivi(self, *, membre: User, slug: str) -> Dict[str, Any]:
        cleaned = (slug or '').strip().lower().lstrip('#')
        slug_n = slugify(cleaned) or cleaned
        tag = self._find_existing(slug_n) or Tag.objects.filter(slug=slug_n).first()
        if tag is None:
            raise ValidationError('Tag introuvable.')
        existing = SuiviTag.objects.filter(membre=membre, tag=tag).first()
        if existing is not None:
            existing.delete()
            return {
                'following': False,
                'tag': {'id': tag.id, 'label': tag.label, 'slug': tag.slug},
            }
        with transaction.atomic():
            SuiviTag.objects.create(
                membre=membre,
                tag=tag,
                created_by=membre.id,
                updated_by=membre.id,
            )
        return {
            'following': True,
            'tag': {'id': tag.id, 'label': tag.label, 'slug': tag.slug},
        }
