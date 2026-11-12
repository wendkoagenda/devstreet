"""Calcul des fichiers modifiés et rapprochement avec les zones protégées."""
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .config import ConfigError, Zone
from .matcher import matches_any

EMPTY_TREE = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
NULL_SHA = re.compile(r'^0+$')
STATUS_LABELS = {'A': 'ajouté', 'M': 'modifié', 'D': 'supprimé', 'R': 'renommé'}


@dataclass(frozen=True)
class Change:
    path: str
    status: str  # A, M, D ou R
    old_path: Optional[str] = None

    @property
    def paths(self) -> List[str]:
        return [self.path] + ([self.old_path] if self.old_path else [])


@dataclass
class ZoneHit:
    zone: Zone
    changes: List[Change] = field(default_factory=list)
    tests_touched: bool = False


def parse_name_status(output: str) -> List[Change]:
    """Lit la sortie de `git diff --name-status -M` (A/M/D/T, Rxx et Cxx avec ancien et nouveau chemin)."""
    changes = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split('\t')
        code = parts[0][0]
        if code in 'RC' and len(parts) == 3:
            changes.append(Change(path=parts[2], status='R' if code == 'R' else 'A', old_path=parts[1] if code == 'R' else None))
        elif len(parts) == 2:
            changes.append(Change(path=parts[1], status='M' if code == 'T' else code))
        else:
            raise ConfigError(f'ligne de diff illisible : « {line} »')
    return changes


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(['git', *args], cwd=root, capture_output=True, text=True, encoding='utf-8')
    if result.returncode != 0:
        raise ConfigError(f'git {" ".join(args)} a échoué : {result.stderr.strip()}')
    return result.stdout


def tracked_files(root: Path) -> List[str]:
    """Fichiers suivis par Git, plus les nouveaux fichiers pas encore ajoutés (hors fichiers ignorés)."""
    return [line for line in _git(root, 'ls-files', '--cached', '--others', '--exclude-standard').splitlines() if line]


def git_changes(root: Path, base: str, head: str, two_dot: bool = False) -> List[Change]:
    """Fichiers modifiés entre `base` et `head`.

    Trois points (défaut, pull request) : depuis l'ancêtre commun, sans les changements arrivés sur la base.
    Deux points : comparaison directe de deux commits (push, ou deux branches à comparer).
    """
    if NULL_SHA.match(base):  # première publication d'une branche : tout son contenu est nouveau
        base, two_dot = EMPTY_TREE, True
    separator = '..' if two_dot else '...'
    output = _git(root, 'diff', '--name-status', '-M', f'{base}{separator}{head}')
    return parse_name_status(output)


def analyze(zones: List[Zone], changes: List[Change]) -> List[ZoneHit]:
    """Une zone est touchée par un fichier du code protégé. Un test ajouté ou modifié ne la déclenche pas,
    un test supprimé oui (affaiblir la couverture est un risque)."""
    hits = []
    for zone in zones:
        hit = ZoneHit(zone)
        for change in changes:
            is_test = matches_any(zone.tests, change.path) or (change.old_path and matches_any(zone.tests, change.old_path))
            if is_test:
                hit.tests_touched = True
                if change.status in ('D', 'R'):
                    hit.changes.append(change)
            elif matches_any(zone.paths, change.path) or (change.old_path and matches_any(zone.paths, change.old_path)):
                hit.changes.append(change)
        if hit.changes:
            hits.append(hit)
    return hits
