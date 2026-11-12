"""Construction et rendu du rapport (texte, markdown, JSON). Aucun secret : extraits masqués et courts."""
import json
from datetime import datetime, timezone
from typing import Dict, List

from . import scoring
from .exceptions import ExceptionEntry, describe
from .models import BLOCKING_SEVERITIES, SEVERITIES, Finding

RANK = {'info': 0, 'warning': 1, 'error': 2, 'critical': 3}
LABELS = {'critical': 'critique', 'error': 'erreur', 'warning': 'avertissement', 'info': 'info'}


def build(findings: List[Finding], scanned_files: int, rules_run: int, expired: List[ExceptionEntry],
          unused: List[ExceptionEntry], fail_on: str) -> Dict:
    active = [f for f in findings if f.status != 'excepted']
    score = scoring.compute(active)
    counts = {s: sum(1 for f in active if f.severity == s) for s in SEVERITIES}
    new = [f for f in active if f.status == 'new']
    if fail_on == 'never':
        blocking_new = []
    else:
        blocking_new = [f for f in new if RANK[f.severity] >= RANK[fail_on]]
    return {
        'version': 1,
        'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'scanned_files': scanned_files,
        'rules_run': rules_run,
        'score': score['score'],
        'state': score['state'],
        'penalties': score['penalties'],
        'counts': counts,
        'new_count': len(new),
        'existing_count': sum(1 for f in active if f.status == 'existing'),
        'excepted_count': sum(1 for f in findings if f.status == 'excepted'),
        'blocking': bool(blocking_new or expired),
        'blocking_findings': [f.fingerprint for f in blocking_new],
        'expired_exceptions': [describe(e) for e in expired],
        'unused_exceptions': [describe(e) for e in unused],
        'findings': [f.to_dict() for f in findings],
    }


def to_json(report: Dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False)


def _penalty_lines(report: Dict) -> List[str]:
    return [f'  {rid}: {p["count"]} × {LABELS[p["severity"]]} -> -{p["penalty"]}'
            for rid, p in report['penalties'].items() if p['penalty']]


def to_text(report: Dict) -> str:
    out = [f'Score de sécurité : {report["score"]}/100 ({report["state"]})',
           f'{report["scanned_files"]} fichiers, {report["rules_run"]} règles — '
           f'{report["new_count"]} nouveau(x), {report["existing_count"]} existant(s), '
           f'{report["excepted_count"]} sous exception']
    penalties = _penalty_lines(report)
    if penalties:
        out += ['', 'Pourquoi le score baisse :'] + penalties
    for status, title in (('new', 'NOUVEAUX'), ('existing', 'EXISTANTS (baseline)')):
        group = [f for f in report['findings'] if f['status'] == status]
        if not group:
            continue
        out += ['', f'{title} :']
        for f in sorted(group, key=lambda f: (-RANK[f['severity']], f['path'], f['line'])):
            out.append(f'  [{LABELS[f["severity"]]}] {f["rule_id"]} {f["path"]}:{f["line"]} — {f["message"]}')
            if f['snippet']:
                out.append(f'      {f["snippet"]}')
    for entry in report['expired_exceptions']:
        out.append(f'\nEXCEPTION EXPIRÉE : {entry["rule"]} {entry["path"]} (le {entry["expires"]}, {entry["author"]})')
    for entry in report['unused_exceptions']:
        out.append(f'\nException inutilisée (à retirer) : {entry["rule"]} {entry["path"]}')
    out += ['', 'Résultat : ' + ('BLOQUANT' if report['blocking'] else 'OK')]
    return '\n'.join(out)


def to_markdown(report: Dict) -> str:
    out = [f'# Rapport de sécurité', '',
           f'**Score : {report["score"]}/100 — {report["state"]}**  ',
           f'{report["scanned_files"]} fichiers analysés, {report["rules_run"]} règles. '
           f'Nouveaux : {report["new_count"]} · existants : {report["existing_count"]} · '
           f'sous exception : {report["excepted_count"]}.', '']
    penalties = _penalty_lines(report)
    if penalties:
        out += ['## Pourquoi le score baisse', ''] + [f'- {p.strip()}' for p in penalties] + ['']
    for status, title in (('new', 'Nouveaux problèmes'), ('existing', 'Dette existante (baseline)')):
        group = [f for f in report['findings'] if f['status'] == status]
        if not group:
            continue
        out += [f'## {title}', '', '| Sévérité | Règle | Fichier | Message |', '| --- | --- | --- | --- |']
        for f in sorted(group, key=lambda f: (-RANK[f['severity']], f['path'], f['line'])):
            message = f['message'].replace('|', '\\|')
            out.append(f'| {LABELS[f["severity"]]} | {f["rule_id"]} | `{f["path"]}:{f["line"]}` | {message} |')
        out.append('')
    if report['expired_exceptions']:
        out += ['## Exceptions expirées', ''] + [
            f'- {e["rule"]} `{e["path"]}` (expirée le {e["expires"]}, {e["author"]})' for e in report['expired_exceptions']] + ['']
    out.append('**Résultat : ' + ('BLOQUANT' if report['blocking'] else 'OK') + '**')
    return '\n'.join(out)


RENDERERS = {'text': to_text, 'markdown': to_markdown, 'json': to_json}
BLOCKING_NAMES = BLOCKING_SEVERITIES
