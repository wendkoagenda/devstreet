"""Registre des règles : chaque règle a un identifiant stable, une sévérité et des exemples."""
from typing import Dict, List

from .models import SEVERITIES, Rule

RULES: Dict[str, Rule] = {}


def rule(*, id, title, severity, category, description, recommendation, globs,
         sample_path='', fail_example='', pass_example='', pass_path=''):
    """Décorateur : enregistre la fonction `check(file) -> Iterable[Hit]` comme règle."""
    assert severity in SEVERITIES, severity

    def register(func):
        if id in RULES:
            raise ValueError(f'Règle en double : {id}')
        RULES[id] = Rule(id, title, severity, category, description, recommendation, tuple(globs),
                         func, sample_path, fail_example, pass_example, pass_path)
        return func

    return register


def all_rules() -> List[Rule]:
    from . import rules  # noqa: F401 (l'import enregistre les règles)
    return [RULES[k] for k in sorted(RULES)]
