"""Ligne de commande : python -m scripts.dependency_audit --pip pip.json --npm npm.json (depuis backend/).

Codes de sortie : 0 aucune faille bloquante, 1 faille bloquante ou exception expirée, 2 rapport ou configuration invalide.
"""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import audit

REPO_ROOT = Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='dependency_audit', description='Audit des dépendances Python et npm avec exceptions datées')
    p.add_argument('--pip', type=Path, help='rapport JSON de pip-audit')
    p.add_argument('--npm', type=Path, help='rapport JSON de npm audit')
    p.add_argument('--exceptions', type=Path, default=REPO_ROOT / audit.EXCEPTIONS_FILE, help='fichier d\'exceptions datées')
    p.add_argument('--format', choices=('text', 'markdown'), default='text')
    p.add_argument('--output', type=Path, help='écrire le rapport dans ce fichier')
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if not args.pip and not args.npm:
        print('Erreur : indiquer au moins un rapport (--pip et/ou --npm).', file=sys.stderr)
        return 2
    try:
        vulnerabilities = []
        if args.pip:
            vulnerabilities += audit.parse_pip_audit(args.pip)
        if args.npm:
            vulnerabilities += audit.parse_npm_audit(args.npm)
        entries = audit.load_exceptions(args.exceptions)
    except audit.ConfigError as error:
        print(f'Erreur : {error}', file=sys.stderr)
        return 2

    result = audit.evaluate(vulnerabilities, entries)
    rendered = audit.render(result, markdown=args.format == 'markdown')
    if args.output:
        args.output.write_text(rendered + '\n', encoding='utf-8')
        print(f'Rapport écrit dans {args.output}.')
    print(rendered)
    return 1 if result.failed else 0


if __name__ == '__main__':
    sys.exit(main())
