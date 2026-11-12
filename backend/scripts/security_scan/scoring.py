"""Score de sécurité de 0 à 100, barème de README_APP_SECURITY.md."""
from collections import defaultdict
from typing import Dict, List

from .models import CRITICAL, ERROR, INFO, WARNING, Finding

PENALTIES = {CRITICAL: 20, ERROR: 10, WARNING: 3, INFO: 0}
# Une même règle ne retire pas plus de N fois son malus unitaire : une seule cause
# (ex. un motif répété dans dix fichiers) ne doit pas écraser le score à elle seule.
MAX_OCCURRENCES_PER_RULE = 3

STATES = ((90, 'Sain'), (75, 'À surveiller'), (50, 'Risque élevé'), (0, 'Bloquant'))


def state_for(score: int) -> str:
    return next(label for threshold, label in STATES if score >= threshold)


def compute(findings: List[Finding]) -> Dict:
    """Score détaillé : la perte de points est expliquée règle par règle."""
    per_rule = defaultdict(lambda: {'count': 0, 'penalty': 0, 'severity': ''})
    for f in findings:
        entry = per_rule[f.rule_id]
        entry['severity'] = f.severity
        entry['count'] += 1
        if entry['count'] <= MAX_OCCURRENCES_PER_RULE:
            entry['penalty'] += PENALTIES[f.severity]
    total = sum(e['penalty'] for e in per_rule.values())
    score = max(0, 100 - total)
    return {
        'score': score,
        'state': state_for(score),
        'penalties': {rid: e for rid, e in sorted(per_rule.items(), key=lambda kv: -kv[1]['penalty'])},
    }
