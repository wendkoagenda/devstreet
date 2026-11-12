"""Exécution des règles sur les fichiers du dépôt."""
from fnmatch import fnmatch
from typing import Iterable, List, Optional

from .models import Finding, ScanContext, ScanFile, fingerprint, mask
from .registry import all_rules
from .models import Rule

MAX_FILE_BYTES = 1_000_000


def matches(path: str, rule: Rule) -> bool:
    return any(fnmatch(path, glob) for glob in rule.globs)


def run_rule_on(rule: Rule, file: ScanFile) -> List[Finding]:
    findings, seen = [], set()
    for hit in rule.check(file):
        snippet = mask(hit.snippet) if hit.snippet else ''
        key = hit.key if hit.key is not None else (snippet or hit.message)
        fp = fingerprint(rule.id, file.path, key)
        if (fp, hit.line) in seen:
            continue
        seen.add((fp, hit.line))
        findings.append(Finding(rule.id, rule.severity, rule.category, file.path, hit.line, hit.message, snippet, fp))
    return findings


def scan(context: ScanContext, rules: Optional[Iterable[Rule]] = None) -> List[Finding]:
    """Applique toutes les règles ; un fichier illisible ou une règle en erreur ne bloque jamais le scan."""
    rules = list(rules) if rules is not None else all_rules()
    findings: List[Finding] = []
    for path in context.files:
        applicable = [r for r in rules if matches(path, r)]
        if not applicable:
            continue
        text = context.read(path)
        if len(text) > MAX_FILE_BYTES:
            continue
        file = ScanFile(path, text, context)
        for rule in applicable:
            findings.extend(run_rule_on(rule, file))
    findings.sort(key=lambda f: (f.path, f.line, f.rule_id))
    return findings
