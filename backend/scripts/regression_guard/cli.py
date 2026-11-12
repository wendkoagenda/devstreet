"""Ligne de commande : python -m scripts.regression_guard --base develop (depuis backend/).

Codes de sortie : 0 aucune zone touchée, 1 au moins une zone touchée, 2 configuration ou git invalide.
"""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import config, engine, report

REPO_ROOT = Path(__file__).resolve().parents[3]
FORMATS = ('text', 'markdown', 'json')


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='regression_guard', description='Signale les zones protégées touchées par un changement')
    p.add_argument('--root', type=Path, default=REPO_ROOT, help='racine du dépôt (défaut : racine de devstreet)')
    p.add_argument('--config-root', type=Path, metavar='DIR',
                   help='dossier de confiance contenant regression-guard.json et git-cli/access_control.conf '
                        "(CI : copie de la branche cible, pour qu'une PR ne puisse pas réécrire ses propres règles)")
    p.add_argument('--base', required=True, metavar='REF', help='branche ou commit de départ (ex. origin/develop)')
    p.add_argument('--head', default='HEAD', metavar='REF', help='branche ou commit à contrôler (défaut : HEAD)')
    p.add_argument('--two-dot', action='store_true', help='comparer base et head directement (push) au lieu de l\'ancêtre commun (PR)')
    p.add_argument('--format', choices=FORMATS, default='text')
    p.add_argument('--approved', action='store_true', help='markdown : indiquer que la validation d\'un responsable est donnée')
    p.add_argument('--output', type=Path, help='écrire le rapport dans ce fichier')
    p.add_argument('--github-output', type=Path, help='fichier $GITHUB_OUTPUT : écrit touched=true|false et zones=a,b')
    return p


def render(fmt: str, hits, owners: List[str], approved: bool) -> str:
    if fmt == 'markdown':
        return report.render_markdown(hits, owners, approved)
    return report.RENDERERS[fmt](hits, owners)


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    root = args.root.resolve()
    config_root = args.config_root.resolve() if args.config_root else root
    try:
        zones = config.load(config_root / config.GUARD_FILE)
        changes = engine.git_changes(root, args.base, args.head, args.two_dot)
        # Les fichiers du diff comptent aussi : un fichier protégé supprimé doit être signalé, pas rejeté comme « motif vide »
        known_files = engine.tracked_files(root) + [path for change in changes for path in change.paths]
        config.check_patterns_exist(zones, known_files)
        owners = config.master_users(config_root / config.ACCESS_CONTROL_FILE)
    except config.ConfigError as error:
        print(f'Erreur : {error}', file=sys.stderr)
        return 2

    hits = engine.analyze(zones, changes)
    rendered = render(args.format, hits, owners, args.approved)
    if args.output:
        args.output.write_text(rendered + '\n', encoding='utf-8')
        print(f'Rapport écrit dans {args.output} ({len(hits)} zone(s) touchée(s)).')
    else:
        print(rendered)
    if args.github_output:
        with args.github_output.open('a', encoding='utf-8') as handle:
            handle.write(f'touched={"true" if hits else "false"}\n')
            handle.write(f'zones={",".join(hit.zone.name for hit in hits)}\n')
    return 1 if hits else 0


if __name__ == '__main__':
    sys.exit(main())
