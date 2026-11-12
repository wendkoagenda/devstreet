"""Rapports : texte (terminal), Markdown (commentaire de pull request) et JSON."""
import json
from typing import Dict, List

from .engine import STATUS_LABELS, ZoneHit

COMMENT_MARKER = '<!-- regression-guard -->'
MAX_FILES_SHOWN = 15


def owners_of(hit: ZoneHit, default_owners: List[str]) -> List[str]:
    return list(dict.fromkeys(hit.zone.owners + default_owners))


def tests_warning(hit: ZoneHit) -> bool:
    """Code de la zone modifié alors qu'elle déclare des tests et qu'aucun n'a bougé."""
    return bool(hit.zone.tests) and not hit.tests_touched


def _describe(change) -> str:
    label = STATUS_LABELS[change.status]
    return f'{change.old_path} → {change.path} ({label})' if change.old_path else f'{change.path} ({label})'


def to_dict(hits: List[ZoneHit], default_owners: List[str]) -> Dict:
    return {
        'touched': bool(hits),
        'masters': default_owners,
        'zones': [{
            'name': hit.zone.name,
            'reason': hit.zone.reason,
            'verify': hit.zone.verify,
            'owners': owners_of(hit, default_owners),
            'files': [{'path': c.path, 'old_path': c.old_path, 'status': c.status} for c in hit.changes],
            'tests_touched': hit.tests_touched,
            'tests_missing': tests_warning(hit),
        } for hit in hits],
    }


def render_json(hits: List[ZoneHit], default_owners: List[str]) -> str:
    return json.dumps(to_dict(hits, default_owners), ensure_ascii=False, indent=2)


def render_text(hits: List[ZoneHit], default_owners: List[str]) -> str:
    if not hits:
        return 'Aucune zone protégée touchée.'
    lines = [f'{len(hits)} zone(s) protégée(s) touchée(s) :']
    for hit in hits:
        lines.append(f'\n[{hit.zone.name}] {hit.zone.reason}')
        lines.extend(f'  - {_describe(c)}' for c in hit.changes)
        if tests_warning(hit):
            lines.append('  ! code modifié, aucun test de la zone modifié')
        lines.append(f'  À vérifier : {hit.zone.verify}')
        lines.append(f'  Responsables : {", ".join(owners_of(hit, default_owners))}')
    return '\n'.join(lines)


def render_markdown(hits: List[ZoneHit], default_owners: List[str], approved: bool = False) -> str:
    lines = [COMMENT_MARKER, '## Contrôle de non-régression', '']
    if not hits:
        lines.append('Aucune zone protégée touchée par ce changement.')
        return '\n'.join(lines)
    if approved:
        lines += ['**Validé par un responsable ? :** Oui', '']
    else:
        lines += ['**Validé par un responsable ? :** Non. Approuver la pull request (« Approve ») sur son dernier commit '
                  'fait passer ce contrôle.', '']
    for hit in hits:
        mentions = ' '.join(f'@{owner}' for owner in owners_of(hit, default_owners))
        lines += [f'### `{hit.zone.name}`', '', hit.zone.reason, '']
        shown = hit.changes[:MAX_FILES_SHOWN]
        lines += [f'- `{_describe(c)}`' for c in shown]
        if len(hit.changes) > len(shown):
            lines.append(f'- … et {len(hit.changes) - len(shown)} autre(s) fichier(s)')
        lines.append('')
        if tests_warning(hit):
            lines += ['> Code modifié, aucun test de la zone modifié.', '']
        lines += [f'**À vérifier :** {hit.zone.verify}', '', f'**Responsables :** {mentions}', '']
    return '\n'.join(lines).rstrip()


RENDERERS = {'text': render_text, 'json': render_json}
