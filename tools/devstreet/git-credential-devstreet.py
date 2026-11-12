#!/usr/bin/env python
"""Credential helper Git : fournit le PAT DevStreet pour l'hôte Gitea concerné."""

from __future__ import annotations

import sys
from pathlib import Path

# Permet l'exécution directe hors package installé.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from devstreet.secure_store import find_token_for_gitea_host  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        return 0
    action = sys.argv[1]
    lines = sys.stdin.read().splitlines()
    fields: dict[str, str] = {}
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key] = value
    if action != "get":
        return 0
    host = fields.get("host", "")
    protocol = fields.get("protocol", "https")
    if protocol != "https" or not host:
        return 0
    found = find_token_for_gitea_host(host)
    if not found:
        return 0
    login, token = found
    sys.stdout.write(f"username={login}\n")
    sys.stdout.write(f"password={token}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
