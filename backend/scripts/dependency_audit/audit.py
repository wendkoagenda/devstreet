"""Lecture des rapports d'audit, exceptions datées et décision de blocage."""
import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

EXCEPTIONS_FILE = 'dependency-audit-exceptions.json'
MAX_VALIDITY_DAYS = 180
MIN_REASON_LENGTH = 15
REQUIRED_FIELDS = ('id', 'package', 'reason', 'author', 'expires')
# pip-audit ne donne aucune gravité : toute faille Python connue bloque. npm en donne une.
NPM_BLOCKING_SEVERITIES = ('high', 'critical')


class ConfigError(Exception):
    """Rapport ou fichier d'exceptions invalide : l'audit s'arrête plutôt que de conclure à tort."""


@dataclass
class Vulnerability:
    ecosystem: str  # 'python' ou 'npm'
    package: str
    version: str
    ids: Tuple[str, ...]
    severity: str  # 'inconnue' pour Python
    fix: str
    blocking: bool
    excepted_by: Optional['ExceptionEntry'] = None


@dataclass
class ExceptionEntry:
    id: str
    package: str
    reason: str
    author: str
    expires: date
    used: bool = False

    def matches(self, vuln: Vulnerability) -> bool:
        return self.package.lower() == vuln.package.lower() and self.id in vuln.ids


@dataclass
class Result:
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    expired: List[ExceptionEntry] = field(default_factory=list)
    unused: List[ExceptionEntry] = field(default_factory=list)

    @property
    def blocking(self) -> List[Vulnerability]:
        return [v for v in self.vulnerabilities if v.blocking and v.excepted_by is None]

    @property
    def failed(self) -> bool:
        return bool(self.blocking or self.expired)


def _load_json(path: Path, what: str):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except OSError as error:
        raise ConfigError(f'{what} : lecture impossible ({error})')
    except ValueError as error:
        raise ConfigError(f'{what} : JSON invalide ({error})')


def parse_pip_audit(path: Path) -> List[Vulnerability]:
    data = _load_json(path, 'rapport pip-audit')
    dependencies = data.get('dependencies') if isinstance(data, dict) else None
    if not isinstance(dependencies, list):
        raise ConfigError('rapport pip-audit : clé « dependencies » absente (format inattendu)')
    found = []
    for dependency in dependencies:
        for vuln in dependency.get('vulns', []):
            ids = tuple(dict.fromkeys([vuln['id'], *vuln.get('aliases', [])]))
            found.append(Vulnerability('python', dependency['name'], str(dependency.get('version', '')), ids,
                                       'inconnue', ', '.join(vuln.get('fix_versions', [])) or 'aucun correctif', True))
    return found


def _advisory_id(via: dict) -> str:
    url = str(via.get('url', ''))
    return url.rstrip('/').rsplit('/', 1)[-1] if url else str(via.get('source', ''))


def parse_npm_audit(path: Path) -> List[Vulnerability]:
    data = _load_json(path, 'rapport npm audit')
    packages = data.get('vulnerabilities') if isinstance(data, dict) else None
    if not isinstance(packages, dict):
        raise ConfigError('rapport npm audit : clé « vulnerabilities » absente (format inattendu)')
    found = []
    for name, entry in packages.items():
        advisories = [via for via in entry.get('via', []) if isinstance(via, dict)]
        if not advisories:  # entrée dérivée d'une autre dépendance : la cause racine a sa propre entrée
            continue
        fix = entry.get('fixAvailable')
        fix_text = (f'{fix["name"]}@{fix["version"]}' if isinstance(fix, dict) else 'mise à jour disponible' if fix else 'aucun correctif')
        ids = tuple(dict.fromkeys(_advisory_id(via) for via in advisories))
        found.append(Vulnerability('npm', name, '', ids, entry['severity'], fix_text, entry['severity'] in NPM_BLOCKING_SEVERITIES))
    return found


def load_exceptions(path: Path, today: Optional[date] = None) -> List[ExceptionEntry]:
    today = today or date.today()
    if not path.exists():
        return []
    data = _load_json(path, path.name)
    items = data.get('exceptions') if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise ConfigError(f'{path.name} : attendu {{"exceptions": [...]}}')
    entries = []
    for index, item in enumerate(items, 1):
        where = f'{path.name} entrée {index}'
        if not isinstance(item, dict):
            raise ConfigError(f'{where} : objet attendu')
        missing = [f for f in REQUIRED_FIELDS if not str(item.get(f, '')).strip()]
        if missing:
            raise ConfigError(f'{where} : champ(s) obligatoire(s) manquant(s) : {", ".join(missing)}')
        if len(str(item['reason']).strip()) < MIN_REASON_LENGTH:
            raise ConfigError(f'{where} : la raison doit faire {MIN_REASON_LENGTH} caractères minimum')
        try:
            expires = date.fromisoformat(str(item['expires']))
        except ValueError:
            raise ConfigError(f'{where} : date d\'expiration invalide (AAAA-MM-JJ attendu)')
        if expires > today + timedelta(days=MAX_VALIDITY_DAYS):
            raise ConfigError(f'{where} : expiration trop lointaine ({MAX_VALIDITY_DAYS} jours maximum)')
        entries.append(ExceptionEntry(item['id'].strip(), item['package'].strip(), item['reason'].strip(), item['author'].strip(), expires))
    return entries


def evaluate(vulnerabilities: List[Vulnerability], entries: List[ExceptionEntry], today: Optional[date] = None) -> Result:
    """Applique les exceptions. Une exception expirée ne couvre plus rien et fait échouer l'audit."""
    today = today or date.today()
    result = Result(vulnerabilities=vulnerabilities)
    result.expired = [e for e in entries if today > e.expires]
    for vuln in vulnerabilities:
        for entry in entries:
            if today <= entry.expires and entry.matches(vuln):
                vuln.excepted_by, entry.used = entry, True
                break
    result.unused = [e for e in entries if not e.used and today <= e.expires]
    return result


def render(result: Result, markdown: bool = False) -> str:
    bullet = '- ' if markdown else '  - '
    title = '## Audit des dépendances' if markdown else 'Audit des dépendances'
    lines = [title, '']
    blocking, excepted = result.blocking, [v for v in result.vulnerabilities if v.excepted_by]
    others = [v for v in result.vulnerabilities if not v.blocking and not v.excepted_by]
    lines.append(f'{len(result.vulnerabilities)} faille(s) connue(s) : {len(blocking)} bloquante(s), '
                 f'{len(excepted)} sous exception, {len(others)} sans blocage.')
    for label, group in (('Bloquantes', blocking), ('Sous exception', excepted), ('Sans blocage (gravité moyenne ou basse)', others)):
        if group:
            lines += ['', f'{label} :']
            for v in group:
                suffix = f' — exception de {v.excepted_by.author} jusqu\'au {v.excepted_by.expires}' if v.excepted_by else ''
                lines.append(f'{bullet}[{v.ecosystem}] {v.package} {v.version}'.rstrip() +
                             f' ({v.severity}) {", ".join(v.ids[:3])} — correctif : {v.fix}{suffix}')
    if result.expired:
        lines += ['', 'Exceptions expirées (elles ne couvrent plus rien) :']
        lines += [f'{bullet}{e.id} ({e.package}), expirée le {e.expires}' for e in result.expired]
    if result.unused:
        lines += ['', 'Exceptions inutilisées (à retirer) :']
        lines += [f'{bullet}{e.id} ({e.package})' for e in result.unused]
    lines += ['', 'Résultat : ' + ('ÉCHEC' if result.failed else 'OK')]
    return '\n'.join(lines)
