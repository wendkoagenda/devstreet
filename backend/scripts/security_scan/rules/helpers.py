"""Aides communes aux règles."""
import ast
from typing import Iterator, Optional

from ..models import ScanFile


def parse(file: ScanFile) -> Optional[ast.AST]:
    """Arbre syntaxique Python, ou None si le fichier ne se parse pas (jamais d'exception)."""
    try:
        return ast.parse(file.text)
    except (SyntaxError, ValueError):
        return None


def line_text(file: ScanFile, number: int) -> str:
    lines = file.lines
    return lines[number - 1] if 0 < number <= len(lines) else ''


def assigned(tree: ast.AST, name: str) -> Iterator[ast.Assign]:
    """Affectations `name = ...` (au niveau module ou imbriquées)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            yield node


def call_name(node: ast.Call) -> str:
    """Nom pointé d'un appel : `os.getenv`, `eval`, `subprocess.run`…"""
    func = node.func
    parts = []
    while isinstance(func, ast.Attribute):
        parts.append(func.attr)
        func = func.value
    if isinstance(func, ast.Name):
        parts.append(func.id)
    return '.'.join(reversed(parts))


def is_env_getter(node: ast.AST) -> bool:
    return isinstance(node, ast.Call) and call_name(node) in ('os.getenv', 'os.environ.get', 'getenv', 'env')
