"""Audit des zones protégées : motifs orphelins et fichiers hors zone."""
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence, Tuple

from .config import Zone
from .matcher import matches, matches_any


@dataclass(frozen=True)
class OrphanPattern:
    zone: str
    kind: str  # paths | tests
    pattern: str


@dataclass
class AuditReport:
    orphan_zones: List[OrphanPattern] = field(default_factory=list)
    orphan_protected: List[str] = field(default_factory=list)
    outside_by_prefix: Dict[str, int] = field(default_factory=dict)
    outside_total: int = 0
    tracked_total: int = 0

    @property
    def has_orphans(self) -> bool:
        return bool(self.orphan_zones or self.orphan_protected)

    @property
    def has_outside(self) -> bool:
        return self.outside_total > 0


def orphan_zone_patterns(zones: Iterable[Zone], tracked_files: Iterable[str]) -> List[OrphanPattern]:
    tracked = list(tracked_files)
    found = []
    for zone in zones:
        for kind, patterns in (('paths', zone.paths), ('tests', zone.tests)):
            for pattern in patterns:
                if not any(matches(pattern, path) for path in tracked):
                    found.append(OrphanPattern(zone=zone.name, kind=kind, pattern=pattern))
    return found


def matches_protected(prefix: str, path: str) -> bool:
    """Règle PROTECTED_PATHS : `/` final = préfixe dossier, sinon fichier exact."""
    if prefix.endswith('/'):
        return path == prefix.rstrip('/') or path.startswith(prefix)
    return path == prefix


def orphan_protected_paths(protected_prefixes: Sequence[str], tracked_files: Iterable[str]) -> List[str]:
    tracked = list(tracked_files)
    return [
        prefix for prefix in protected_prefixes
        if not any(matches_protected(prefix, path) for path in tracked)
    ]


def outside_zones_summary(zones: Iterable[Zone], tracked_files: Iterable[str]) -> Tuple[Dict[str, int], int]:
    """Compteurs par premier segment pour les chemins non couverts par aucun motif paths."""
    zone_list = list(zones)
    all_paths = [pattern for zone in zone_list for pattern in zone.paths]
    counts: Counter = Counter()
    outside = 0
    for path in tracked_files:
        if matches_any(all_paths, path):
            continue
        outside += 1
        prefix = path.split('/', 1)[0] + ('/' if '/' in path else '')
        counts[prefix] += 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0]))), outside


def run_audit(zones: Sequence[Zone], protected_prefixes: Sequence[str], tracked_files: Sequence[str]) -> AuditReport:
    outside_by_prefix, outside_total = outside_zones_summary(zones, tracked_files)
    return AuditReport(
        orphan_zones=orphan_zone_patterns(zones, tracked_files),
        orphan_protected=orphan_protected_paths(protected_prefixes, tracked_files),
        outside_by_prefix=outside_by_prefix,
        outside_total=outside_total,
        tracked_total=len(tracked_files),
    )


def render_text(report: AuditReport) -> str:
    lines = [
        f'Audit des zones protégées — {report.tracked_total} fichier(s) suivi(s)',
        '',
        '## Motifs / chemins orphelins',
    ]
    if not report.has_orphans:
        lines.append('Aucun.')
    else:
        for item in report.orphan_zones:
            lines.append(
                f'  - zone « {item.zone} » : motif « {item.pattern} » ({item.kind}) '
                f'ne correspond à aucun fichier'
            )
        for prefix in report.orphan_protected:
            lines.append(
                f'  - PROTECTED_PATHS : « {prefix} » ne correspond à aucun fichier'
            )
    lines += ['', '## Fichiers hors zone (informatif)']
    if not report.has_outside:
        lines.append('Tous les fichiers suivis sont couverts par au moins une zone.')
    else:
        lines.append(
            f'{report.outside_total} fichier(s) hors zone '
            f'({report.tracked_total - report.outside_total} couvert(s)).'
        )
        for prefix, count in report.outside_by_prefix.items():
            lines.append(f'  - {prefix or "(racine)"} : {count}')
    return '\n'.join(lines)


def render_summary_line(report: AuditReport) -> str:
    """Ligne courte pour GITHUB_STEP_SUMMARY (hors zone, non bloquant)."""
    if not report.has_outside:
        return 'Fichiers hors zone : aucun (tous couverts).'
    detail = ', '.join(f'{prefix}:{count}' for prefix, count in list(report.outside_by_prefix.items())[:8])
    return f'Fichiers hors zone : {report.outside_total} ({detail}).'
