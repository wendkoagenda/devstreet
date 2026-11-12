"""Modèles du scanner : sévérités, résultats (findings), contexte de scan."""
import hashlib
import re
import subprocess
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

CRITICAL, ERROR, WARNING, INFO = 'critical', 'error', 'warning', 'info'
SEVERITIES = (CRITICAL, ERROR, WARNING, INFO)
BLOCKING_SEVERITIES = (CRITICAL, ERROR)

MAX_SNIPPET = 80

_SECRET_ASSIGN = re.compile(
    r"""(?ix)((?:password|passwd|pwd|secret|token|api_?key|private_?key|signing_?key|secret_?key)\w*["']?\s*[:=]\s*)(["'])[^"']{4,}\2"""
)
_KNOWN_TOKEN = re.compile(
    r'AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_\-]{35}|gh[pousr]_[A-Za-z0-9]{36,}|sk_live_[0-9a-zA-Z]{20,}|xox[baprs]-[0-9A-Za-z\-]{20,}'
)
# Longue suite de caractères : masquée si elle contient un chiffre (jeton) ou dépasse 32 caractères
_LONG_TOKEN = re.compile(r'[A-Za-z0-9+/_\-]{20,}')


def mask(text: str) -> str:
    """Masque les valeurs sensibles d'une ligne et la tronque : aucun secret ne doit sortir d'un rapport."""
    text = ' '.join(text.strip().split())
    text = _SECRET_ASSIGN.sub(lambda m: f'{m.group(1)}{m.group(2)}****{m.group(2)}', text)
    text = _KNOWN_TOKEN.sub(lambda m: m.group(0)[:4] + '****', text)
    text = _LONG_TOKEN.sub(
        lambda m: m.group(0)[:4] + '****' if (len(m.group(0)) > 32 or re.search(r'\d', m.group(0))) else m.group(0), text)
    return text if len(text) <= MAX_SNIPPET else text[: MAX_SNIPPET - 1] + '…'


@dataclass
class Hit:
    """Résultat brut d'une règle sur un fichier."""
    line: int
    message: str
    snippet: str = ''
    key: Optional[str] = None  # valeur stable pour l'empreinte (par défaut : l'extrait masqué)


@dataclass
class Rule:
    id: str
    title: str
    severity: str
    category: str
    description: str
    recommendation: str
    globs: Tuple[str, ...]
    check: Callable[['ScanFile'], Iterable[Hit]]
    sample_path: str = ''
    fail_example: str = ''
    pass_example: str = ''
    pass_path: str = ''  # chemin de l'exemple conforme (par défaut : sample_path)


@dataclass
class Finding:
    rule_id: str
    severity: str
    category: str
    path: str
    line: int
    message: str
    snippet: str
    fingerprint: str
    status: str = 'new'  # new | existing | excepted
    exception_reason: str = ''

    def to_dict(self) -> Dict:
        return self.__dict__.copy()


def fingerprint(rule_id: str, path: str, key: str) -> str:
    """Empreinte stable (indépendante du numéro de ligne) pour la baseline."""
    raw = f'{rule_id}|{path}|{" ".join(key.split())}'
    return hashlib.sha1(raw.encode('utf-8')).hexdigest()[:16]


@dataclass
class ScanFile:
    """Fichier à analyser, avec accès aux autres fichiers du dépôt (contrôles de présence)."""
    path: str
    text: str
    context: Optional['ScanContext'] = field(repr=False, default=None)

    @property
    def lines(self) -> List[str]:
        return self.text.splitlines()


class ScanContext:
    """Dépôt analysé : liste des fichiers suivis par git (ou parcours disque en secours)."""

    SKIPPED_DIRS = {'.git', 'node_modules', 'venv', '.venv', '__pycache__', 'dist', 'staticfiles', 'media', 'backups'}
    # Le scanner ne s'analyse pas lui-même (ses motifs ressemblent à des secrets), ni les tests.
    EXCLUDED_PREFIXES = ('backend/scripts/security_scan/',)
    EXCLUDED_GLOBS = ('*/tests/*', '*/tests.py', '*/test_*.py', 'test_*.py', 'conftest.py',
                      '*.test.ts', '*.test.tsx', '*.spec.ts', '*.spec.tsx')

    def __init__(self, root: Path, only_paths: Optional[Iterable[str]] = None):
        self.root = Path(root)
        self.all_files = self._list_files()
        self._all_set = set(self.all_files)
        self.files = [p for p in self.all_files if self._scannable(p)]
        if only_paths is not None:
            wanted = set(only_paths)
            self.files = [p for p in self.files if p in wanted]
        self._cache: Dict[str, str] = {}

    def _list_files(self) -> List[str]:
        try:
            out = subprocess.run(
                ['git', 'ls-files', '-co', '--exclude-standard'], cwd=self.root,
                capture_output=True, text=True, check=True, encoding='utf-8',
            ).stdout
            files = [line for line in out.splitlines() if line]
        except (OSError, subprocess.CalledProcessError):
            files = []
            for p in self.root.rglob('*'):
                if p.is_file() and not (set(p.relative_to(self.root).parts) & self.SKIPPED_DIRS):
                    files.append(p.relative_to(self.root).as_posix())
        return sorted(f for f in files if (self.root / f).is_file())

    def _scannable(self, path: str) -> bool:
        if path.startswith(self.EXCLUDED_PREFIXES):
            return False
        if set(path.split('/')) & self.SKIPPED_DIRS:
            return False
        return not any(fnmatch(path, g) for g in self.EXCLUDED_GLOBS)

    def read(self, path: str) -> str:
        if path not in self._cache:
            try:
                self._cache[path] = (self.root / path).read_text(encoding='utf-8', errors='replace')
            except OSError:
                self._cache[path] = ''
        return self._cache[path]

    def exists(self, path: str) -> bool:
        return path in self._all_set
