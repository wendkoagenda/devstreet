"""Chargement et validation de regression-guard.json et des responsables par défaut."""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

from .matcher import matches

GUARD_FILE = 'regression-guard.json'
ACCESS_CONTROL_FILE = 'git-cli/access_control.conf'
MIN_TEXT_LENGTH = 15
ZONE_NAME = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


class ConfigError(Exception):
    """Configuration invalide : le contrôle s'arrête plutôt que de protéger moins sans le dire."""


@dataclass
class Zone:
    name: str
    reason: str
    paths: List[str]
    tests: List[str]
    verify: str
    owners: List[str] = field(default_factory=list)


def _text_list(item: dict, key: str, where: str, required: bool) -> List[str]:
    values = item.get(key, [])
    if not isinstance(values, list) or not all(isinstance(v, str) and v.strip() for v in values):
        raise ConfigError(f'{where} : « {key} » doit être une liste de textes non vides')
    if required and not values:
        raise ConfigError(f'{where} : « {key} » ne peut pas être vide')
    for value in values:
        if value.startswith('/') or '\\' in value:
            raise ConfigError(f'{where} : « {value} » doit être un chemin relatif à la racine, avec des « / »')
    return values


def load(path: Path) -> List[Zone]:
    if not path.exists():
        raise ConfigError(f'{path.name} introuvable')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except ValueError as error:
        raise ConfigError(f'{path.name} : JSON invalide ({error})')
    items = data.get('zones') if isinstance(data, dict) else None
    if not isinstance(items, list) or not items:
        raise ConfigError(f'{path.name} : attendu {{"zones": [...]}} avec au moins une zone')

    zones, seen = [], set()
    for index, item in enumerate(items, 1):
        if not isinstance(item, dict):
            raise ConfigError(f'{path.name} zone {index} : objet attendu')
        name = str(item.get('name', '')).strip()
        where = f'{path.name} zone « {name or index} »'
        if not ZONE_NAME.match(name):
            raise ConfigError(f'{where} : nom en minuscules et tirets attendu (ex. auth-cookies)')
        if name in seen:
            raise ConfigError(f'{where} : nom déjà utilisé')
        seen.add(name)
        for key in ('reason', 'verify'):
            if len(str(item.get(key, '')).strip()) < MIN_TEXT_LENGTH:
                raise ConfigError(f'{where} : « {key} » obligatoire ({MIN_TEXT_LENGTH} caractères minimum)')
        zones.append(Zone(
            name=name,
            reason=item['reason'].strip(),
            paths=_text_list(item, 'paths', where, required=True),
            tests=_text_list(item, 'tests', where, required=False),
            verify=item['verify'].strip(),
            owners=_text_list(item, 'owners', where, required=False),
        ))
    return zones


def check_patterns_exist(zones: Iterable[Zone], tracked_files: Iterable[str]) -> None:
    """Un motif qui ne correspond plus à aucun fichier protège le vide : on le refuse."""
    tracked = list(tracked_files)
    for zone in zones:
        for kind, patterns in (('paths', zone.paths), ('tests', zone.tests)):
            for pattern in patterns:
                if not any(matches(pattern, path) for path in tracked):
                    raise ConfigError(f'zone « {zone.name} » : le motif « {pattern} » ({kind}) ne correspond à aucun fichier')


def protected_paths(path: Path) -> List[str]:
    """Lit PROTECTED_PATHS dans git-cli/access_control.conf (chemins protégés au commit)."""
    if not path.exists():
        raise ConfigError(f'{ACCESS_CONTROL_FILE} introuvable : impossible de lire PROTECTED_PATHS')
    match = re.search(r'^\s*PROTECTED_PATHS\s*=\s*"([^"]*)"', path.read_text(encoding='utf-8'), re.MULTILINE)
    if not match:
        raise ConfigError(f'{ACCESS_CONTROL_FILE} : PROTECTED_PATHS est absent')
    values = [item.strip() for item in match.group(1).split(',') if item.strip()]
    if not values:
        raise ConfigError(f'{ACCESS_CONTROL_FILE} : PROTECTED_PATHS est vide')
    return values


def check_protected_paths_exist(prefixes: Iterable[str], tracked_files: Iterable[str]) -> None:
    """Un chemin PROTECTED_PATHS sans fichier protège le vide : on le refuse."""
    from .audit import orphan_protected_paths
    for prefix in orphan_protected_paths(list(prefixes), tracked_files):
        raise ConfigError(f'PROTECTED_PATHS : « {prefix} » ne correspond à aucun fichier')


def master_users(path: Path) -> List[str]:
    """Responsables des zones protégées par défaut : ZONE_PROTEGEE_USERS de git-cli/access_control.conf."""
    if not path.exists():
        raise ConfigError(f'{ACCESS_CONTROL_FILE} introuvable : impossible de connaître les responsables')
    match = re.search(r'^\s*ZONE_PROTEGEE_USERS\s*=\s*"([^"]*)"', path.read_text(encoding='utf-8'), re.MULTILINE)
    users = [user.strip() for user in match.group(1).split(',') if user.strip()] if match else []
    if not users:
        raise ConfigError(f'{ACCESS_CONTROL_FILE} : ZONE_PROTEGEE_USERS est vide ou absent')
    return users
