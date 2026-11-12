"""Exceptions versionnées : un risque accepté doit être justifié, attribué et daté."""
import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import Finding
from .registry import all_rules

EXCEPTIONS_FILE = 'security-exceptions.json'
MAX_VALIDITY_DAYS = 180
REQUIRED_FIELDS = ('rule', 'path', 'reason', 'author', 'expires')
MIN_REASON_LENGTH = 15


class ConfigError(Exception):
    """Fichier d'exceptions ou de baseline invalide."""


@dataclass
class ExceptionEntry:
    rule: str
    path: str
    reason: str
    author: str
    expires: date
    line: Optional[int] = None

    def matches(self, finding: Finding) -> bool:
        return (finding.rule_id == self.rule and finding.path == self.path
                and (self.line is None or finding.line == self.line))

    def is_expired(self, today: date) -> bool:
        return today > self.expires


def load(path: Path, today: Optional[date] = None) -> List[ExceptionEntry]:
    """Charge et valide le fichier. Toute entrée invalide arrête le scan (jamais d'exception « molle »)."""
    today = today or date.today()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except ValueError as error:
        raise ConfigError(f'{path.name} : JSON invalide ({error})')
    items = data.get('exceptions') if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise ConfigError(f'{path.name} : attendu {{"exceptions": [...]}}')

    known_rules = {r.id for r in all_rules()}
    entries = []
    for index, item in enumerate(items, 1):
        where = f'{path.name} entrée {index}'
        if not isinstance(item, dict):
            raise ConfigError(f'{where} : objet attendu')
        missing = [f for f in REQUIRED_FIELDS if not str(item.get(f, '')).strip()]
        if missing:
            raise ConfigError(f'{where} : champ(s) obligatoire(s) manquant(s) : {", ".join(missing)}')
        if item['rule'] not in known_rules:
            raise ConfigError(f'{where} : règle inconnue « {item["rule"]} »')
        if any(ch in item['path'] for ch in '*?[]') or item['path'].endswith('/'):
            raise ConfigError(f'{where} : le chemin doit désigner un fichier précis (pas de joker ni de dossier)')
        if len(item['reason'].strip()) < MIN_REASON_LENGTH:
            raise ConfigError(f'{where} : justification trop courte (minimum {MIN_REASON_LENGTH} caractères)')
        try:
            expires = date.fromisoformat(item['expires'])
        except ValueError:
            raise ConfigError(f'{where} : date d\'expiration invalide (format AAAA-MM-JJ)')
        if expires > today + timedelta(days=MAX_VALIDITY_DAYS):
            raise ConfigError(
                f'{where} : expiration trop lointaine (maximum {MAX_VALIDITY_DAYS} jours, soit {today + timedelta(days=MAX_VALIDITY_DAYS)})')
        line = item.get('line')
        if line is not None and not (isinstance(line, int) and line > 0):
            raise ConfigError(f'{where} : line doit être un entier positif')
        entries.append(ExceptionEntry(item['rule'], item['path'], item['reason'].strip(),
                                      item['author'].strip(), expires, line))
    return entries


def apply(findings: List[Finding], entries: List[ExceptionEntry], today: Optional[date] = None
          ) -> Tuple[List[ExceptionEntry], List[ExceptionEntry]]:
    """Marque les findings couverts par une exception valide. Retourne (expirées, inutilisées)."""
    today = today or date.today()
    expired, used = [], set()
    for entry in entries:
        matched = [f for f in findings if entry.matches(f)]
        if matched:
            used.add(id(entry))
        if entry.is_expired(today):
            expired.append(entry)  # l'exception ne protège plus : le finding reste actif
            continue
        for finding in matched:
            finding.status = 'excepted'
            finding.exception_reason = f'{entry.reason} ({entry.author}, jusqu\'au {entry.expires})'
    unused = [e for e in entries if id(e) not in used]
    return expired, unused


def describe(entry: ExceptionEntry) -> Dict:
    return {'rule': entry.rule, 'path': entry.path, 'author': entry.author,
            'expires': entry.expires.isoformat(), 'reason': entry.reason}
