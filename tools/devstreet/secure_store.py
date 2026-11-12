"""Stockage local des secrets Git DevStreet (keyring OS, jamais dans l'URL)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlsplit

SERVICE = "devstreet-git"
CONFIG_DIR = Path.home() / ".devstreet"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _account_key(hub: str, login: str) -> str:
    host = urlsplit(hub).netloc or hub
    return f"{host}|{login}"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {"accounts": {}}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"accounts": {}}


def save_config(data: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass


def store_account(
    *,
    hub: str,
    login: str,
    token: str,
    gitea_url: str,
    computer_id: int | None,
    computer_name: str,
) -> None:
    import keyring

    key = _account_key(hub, login)
    keyring.set_password(SERVICE, key, token)
    cfg = load_config()
    accounts = cfg.setdefault("accounts", {})
    accounts[key] = {
        "hub": hub.rstrip("/"),
        "login": login,
        "gitea_url": gitea_url.rstrip("/"),
        "computer_id": computer_id,
        "computer_name": computer_name,
    }
    cfg["active"] = key
    save_config(cfg)


def get_token(hub: str, login: str) -> str | None:
    import keyring

    return keyring.get_password(SERVICE, _account_key(hub, login))


def list_accounts() -> list[dict]:
    cfg = load_config()
    active = cfg.get("active")
    result = []
    for key, meta in (cfg.get("accounts") or {}).items():
        item = dict(meta)
        item["key"] = key
        item["active"] = key == active
        item["has_secret"] = bool(get_token(meta["hub"], meta["login"]))
        result.append(item)
    return result


def remove_account(hub: str, login: str) -> bool:
    import keyring

    key = _account_key(hub, login)
    try:
        keyring.delete_password(SERVICE, key)
    except Exception:
        pass
    cfg = load_config()
    accounts = cfg.get("accounts") or {}
    existed = key in accounts
    accounts.pop(key, None)
    if cfg.get("active") == key:
        cfg["active"] = next(iter(accounts), None)
    cfg["accounts"] = accounts
    save_config(cfg)
    return existed


def find_token_for_gitea_host(host: str) -> tuple[str, str] | None:
    """Retourne (login, token) pour un hôte Gitea donné."""
    host = host.lower()
    for account in list_accounts():
        gitea = urlsplit(account.get("gitea_url") or "")
        if (gitea.netloc or "").lower() == host and account.get("has_secret"):
            token = get_token(account["hub"], account["login"])
            if token:
                return account["login"], token
    return None
