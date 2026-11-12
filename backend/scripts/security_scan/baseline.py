"""Baseline : distingue la dette existante des nouveaux problèmes."""
import json
from datetime import date
from pathlib import Path
from collections import Counter
from typing import List

from .exceptions import ConfigError
from .models import Finding

BASELINE_FILE = 'security-baseline.json'


def load(path: Path) -> Counter:
    """Empreintes connues avec leur nombre d'occurrences (deux lignes identiques ont la même empreinte)."""
    if not path.exists():
        return Counter()
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return Counter(item['fingerprint'] for item in data['findings'])
    except (ValueError, KeyError, TypeError):
        raise ConfigError(f'{path.name} : fichier de baseline invalide (le regénérer avec --update-baseline)')


def apply(findings: List[Finding], known: Counter) -> None:
    """Chaque occurrence connue n'est consommée qu'une fois : une occurrence en plus est « nouvelle »."""
    remaining = Counter(known)
    for finding in findings:
        if finding.status == 'excepted':
            continue
        if remaining[finding.fingerprint] > 0:
            remaining[finding.fingerprint] -= 1
            finding.status = 'existing'
        else:
            finding.status = 'new'


def save(path: Path, findings: List[Finding]) -> int:
    """Écrit la baseline : empreintes, règle et fichier seulement (aucun extrait, aucun secret)."""
    active = [f for f in findings if f.status != 'excepted']
    entries = sorted(({'fingerprint': f.fingerprint, 'rule': f.rule_id, 'path': f.path} for f in active),
                     key=lambda e: (e['path'], e['rule'], e['fingerprint']))
    payload = {'version': 1, 'generated': date.today().isoformat(), 'findings': entries}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return len(entries)
