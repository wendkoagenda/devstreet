"""Ligne de commande : python -m scripts.security_scan (depuis backend/)."""
import argparse
from collections import Counter
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import List, Optional

from . import baseline, engine, exceptions, report
from .models import ScanContext
from .registry import all_rules

REPO_ROOT = Path(__file__).resolve().parents[3]


def changed_files(root: Path, ref: str) -> List[str]:
    """Fichiers modifiés depuis `ref` (commits + modifications locales + nouveaux fichiers)."""
    def git(*args):
        return subprocess.run(['git', *args], cwd=root, capture_output=True, text=True, encoding='utf-8')

    diff = git('diff', '--name-only', ref)
    if diff.returncode != 0:
        raise exceptions.ConfigError(f'git diff impossible avec « {ref} » : {diff.stderr.strip()}')
    untracked = git('ls-files', '-o', '--exclude-standard')
    return sorted({line for line in (diff.stdout + untracked.stdout).splitlines() if line})


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='security_scan', description='Scanner de sécurité déterministe du dépôt')
    p.add_argument('--root', type=Path, default=REPO_ROOT, help='racine du dépôt (défaut : racine de devstreet)')
    p.add_argument('--format', choices=sorted(report.RENDERERS), default='text')
    p.add_argument('--output', type=Path, help='écrire le rapport dans ce fichier')
    p.add_argument('--changed-since', metavar='REF', help='analyser seulement les fichiers modifiés depuis REF (mode PR)')
    p.add_argument('--fail-on', choices=['critical', 'error', 'warning', 'never'], default='error',
                   help='gravité minimale d\'un NOUVEAU problème qui rend le scan bloquant (défaut : error)')
    p.add_argument('--update-baseline', action='store_true', help='enregistrer l\'état actuel comme dette connue')
    p.add_argument('--no-baseline', action='store_true', help='ignorer la baseline (tout est « nouveau »)')
    p.add_argument('--list-rules', action='store_true', help='afficher le catalogue des règles')
    return p


def list_rules() -> str:
    lines = []
    for r in all_rules():
        lines.append(f'{r.id:11} [{r.severity:8}] {r.category:13} {r.title}')
    return '\n'.join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if args.list_rules:
        print(list_rules())
        return 0

    root = args.root.resolve()
    try:
        entries = exceptions.load(root / exceptions.EXCEPTIONS_FILE)
        known = Counter() if args.no_baseline else baseline.load(root / baseline.BASELINE_FILE)
        only = changed_files(root, args.changed_since) if args.changed_since else None
    except exceptions.ConfigError as error:
        print(f'Erreur de configuration : {error}', file=sys.stderr)
        return 2

    context = ScanContext(root, only_paths=only)
    findings = engine.scan(context)
    expired, unused = exceptions.apply(findings, entries, date.today())
    if only is not None:
        unused = []  # un scan partiel ne peut pas juger les exceptions inutilisées
    baseline.apply(findings, known)

    if args.update_baseline:
        if args.changed_since:
            print('--update-baseline exige un scan complet (sans --changed-since).', file=sys.stderr)
            return 2
        count = baseline.save(root / baseline.BASELINE_FILE, findings)
        print(f'Baseline enregistrée : {count} problème(s) connu(s) dans {baseline.BASELINE_FILE}.')
        return 0

    result = report.build(findings, len(context.files), len(all_rules()), expired, unused, args.fail_on)
    rendered = report.RENDERERS[args.format](result)
    if args.output:
        args.output.write_text(rendered + '\n', encoding='utf-8')
        print(f'Rapport écrit dans {args.output} (score {result["score"]}/100, {result["state"]}).')
    else:
        print(rendered)
    return 1 if result['blocking'] else 0


if __name__ == '__main__':
    sys.exit(main())
