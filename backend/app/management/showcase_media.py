"""URLs médias externes stables pour les seeds showcase / démo.

Photos profil : randomuser.me (portraits fixes).
Images : picsum.photos (seed déterministe).
Vidéos : exemples MDN CC0.
"""
from __future__ import annotations

from typing import Any

# Portraits stables randomuser (0–99). genre + index par persona.
_AVATARS: dict[str, tuple[str, int]] = {
    "awa": ("women", 21),
    "yao": ("men", 32),
    "mariam": ("women", 44),
    "kossi": ("men", 15),
    "aicha": ("women", 68),
    "moussa": ("men", 41),
    "ibrahim": ("men", 52),
    "binta": ("women", 33),
    "fatou": ("women", 12),
    "koffi": ("men", 22),
    "nadia": ("women", 55),
    "salif": ("men", 36),
    "seydou": ("men", 47),
    "boubacar": ("men", 58),
    "ousmane": ("men", 63),
    "grace": ("women", 71),
}

SAMPLE_VIDEOS = (
    "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
    "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.webm",
)


def avatar_url(key: str) -> str:
    """Photo de profil déterministe pour une clé persona."""
    gender, index = _AVATARS.get(key, ("men", abs(hash(key)) % 99))
    return f"https://randomuser.me/api/portraits/{gender}/{index}.jpg"


def banner_url(key: str) -> str:
    """Bannière de profil (picsum seed)."""
    return f"https://picsum.photos/seed/{key}-banner/1200/320"


def image_url(seed: str, width: int = 960, height: int = 640) -> str:
    """Image générique déterministe."""
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in seed)[:80]
    return f"https://picsum.photos/seed/{safe}/{width}/{height}"


def logo_url(key: str) -> str:
    """Logo entreprise / projet."""
    return image_url(f"logo-{key}", 400, 400)


def cover_url(key: str) -> str:
    """Visuel de couverture (offre / prestation / projet)."""
    return image_url(f"cover-{key}", 1200, 630)


def video_url(index: int = 0) -> str:
    return SAMPLE_VIDEOS[index % len(SAMPLE_VIDEOS)]


def media_image(seed: str, alt: str = "") -> dict[str, Any]:
    return {
        "kind": "IMAGE",
        "url": image_url(seed),
        "texte_alternatif": alt or seed.replace("-", " "),
    }


def media_video(index: int = 0, alt: str = "Démo vidéo") -> dict[str, Any]:
    return {
        "kind": "VIDEO",
        "url": video_url(index),
        "texte_alternatif": alt,
    }
