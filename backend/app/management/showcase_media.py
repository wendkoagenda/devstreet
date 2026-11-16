"""URLs médias externes pour seeds showcase — plateforme tech Afrique de l'Ouest.

Portraits : Unsplash, personnes noires / afro-descendantes (IDs fixes).
Visuels : écrans de code, dashboards, mobile, meetups tech.
Vidéos : clips Pexels (typing / écrans) en MP4 public.
"""
from __future__ import annotations

from typing import Any


def _unsplash(photo_id: str, width: int, height: int) -> str:
    """URL Unsplash croppée, stable (pas de redirect picsum)."""
    return (
        f"https://images.unsplash.com/{photo_id}"
        f"?auto=format&fit=crop&w={width}&h={height}&q=80"
    )


# Portraits afro / black (Unsplash) — volontairement monochromes de peau cohérents.
# Pas de randomuser / picsum : trop d'Européens par défaut.
_AVATARS: dict[str, str] = {
    "awa": "photo-1531123897727-8f129e1688ce",
    "yao": "photo-1522529599102-193c0d76b5b6",
    "mariam": "photo-1573496359142-b8d87734a5a2",
    "kossi": "photo-1463453091185-61582044d556",
    "aicha": "photo-1589156280159-276398a6660a",
    "moussa": "photo-1556157382-97eda2d62296",
    "ibrahim": "photo-1506277886164-e25aa3f4ef7f",
    "binta": "photo-1573497019940-1cfe4cfcdeba",
    "fatou": "photo-1594744803322-ea8136144473",
    "koffi": "photo-1539701938214-0d9736e1c16b",
    "nadia": "photo-1573164713714-d95e436ab8d6",
    "salif": "photo-1615109398623-907385bdd835",
    "seydou": "photo-1629425733761-caae3b5f2e50",
    "boubacar": "photo-1506277886164-e25aa3f4ef7f",
    "ousmane": "photo-1539701938214-0d9736e1c16b",
    "grace": "photo-1607990281513-2c110a25bd8c",
}

# Bannière profil : ambiance tech / workspace (pas photo random).
_BANNERS: dict[str, str] = {
    "default": "photo-1518770660439-4636190af475",
    "code": "photo-1555066931-4365d14bab8c",
    "office": "photo-1497366216548-37526070297c",
    "city-night": "photo-1519389950473-47ba0277781c",
}

# Visuels publications / covers — thèmes tech explicites.
_TECH_IMAGES: dict[str, str] = {
    "code-editor": "photo-1555066931-4365d14bab8c",
    "laptop-code": "photo-1498050108023-c5249f4df085",
    "dashboard": "photo-1551288049-bebda4e38f71",
    "analytics": "photo-1460925895917-afdab827c52f",
    "mobile-app": "photo-1512941937450-a43bc72e88fc",
    "mobile-ui": "photo-1551650975-87deedd944c3",
    "ui-kit": "photo-1561070791-2526d30994b5",
    "design-system": "photo-1586717791821-3f44a563fa4c",
    "server": "photo-1558494949-ef526b0040ad",
    "devops": "photo-1667372393119-3d4c48d07fc9",
    "team-dev": "photo-1522071820081-009f0129c71c",
    "meetup": "photo-1540575467063-178a50c2df87",
    "workshop": "photo-1531482615713-2afd69097998",
    "african-dev": "photo-1573164713714-d95e436ab8d6",
    "pairing": "photo-1531482615713-2afd69097998",
    "fintech": "photo-1563986768609-322da13575f3",
    "agritech": "photo-1625246333195-78d9c38ad449",
    "education": "photo-1503676260728-1c00da094a0b",
    "api-docs": "photo-1516321318423-f06f85e504b3",
    "git-flow": "photo-1618401471353-b98afee0b2eb",
    "flutter-offline-queue": "photo-1551650975-87deedd944c3",
    "mobile-money-retry": "photo-1563986768609-322da13575f3",
    "cereales-dashboard": "photo-1551288049-bebda4e38f71",
    "gestion-scolaire-dashboard": "photo-1460925895917-afdab827c52f",
    "gestion-scolaire-mobile": "photo-1512941937450-a43bc72e88fc",
    "sahel-ui-kit": "photo-1561070791-2526d30994b5",
    "sahel-ui-dark": "photo-1555066931-4365d14bab8c",
    "meetup-dakar-agritech": "photo-1540575467063-178a50c2df87",
    "devstreet-release-forum": "photo-1516321318423-f06f85e504b3",
    "comment-idempotency-flow": "photo-1558494949-ef526b0040ad",
}

# Clips tech publics (Pexels CDN) — typing / écrans, pas fleurs.
SAMPLE_VIDEOS = (
    # Développeur qui tape au clavier
    "https://videos.pexels.com/video-files/3129671/3129671-uhd_2560_1440_30fps.mp4",
    # Écran / travail digital
    "https://videos.pexels.com/video-files/2278095/2278095-hd_1920_1080_30fps.mp4",
)

# Logos entreprises : monogrammes UI Avatars (lisible, pas photo stock).
_COMPANY_COLORS: dict[str, str] = {
    "resto": "E85D04",
    "faso": "0077B6",
    "agri": "2D6A4F",
    "edu": "7B2CBF",
}


def avatar_url(key: str) -> str:
    """Portrait afro / black déterministe pour une clé persona."""
    photo_id = _AVATARS.get(key) or _AVATARS["moussa"]
    return _unsplash(photo_id, 400, 400)


def banner_url(key: str) -> str:
    """Bannière tech (circuit / code / workspace)."""
    # Alterne 4 bannières selon la clé pour varier sans sortir du thème.
    keys = list(_BANNERS.keys())
    chosen = keys[abs(hash(key)) % len(keys)]
    return _unsplash(_BANNERS[chosen], 1200, 320)


def image_url(seed: str, width: int = 960, height: int = 640) -> str:
    """Image tech : mappe le seed vers un Unsplash connu, sinon code-editor."""
    photo_id = _TECH_IMAGES.get(seed) or _TECH_IMAGES["code-editor"]
    return _unsplash(photo_id, width, height)


def logo_url(key: str) -> str:
    """Logo entreprise (monogramme coloré, thème fintech/agritech…)."""
    color = _COMPANY_COLORS.get(key, "1B4332")
    name = key.replace("-", "+").title()
    return (
        f"https://ui-avatars.com/api/?name={name}&background={color}"
        f"&color=fff&size=256&bold=true&format=png"
    )


def cover_url(key: str) -> str:
    """Visuel de couverture projet / prestation — toujours tech."""
    # Prefixe prestation- / slug projet → thème dérivé
    if "prestation" in key or "mobile" in key:
        theme = "mobile-app"
    elif "pay" in key or "fintech" in key or "teranga" in key:
        theme = "fintech"
    elif "agri" in key:
        theme = "agritech"
    elif "scolaire" in key or "edu" in key or "gestion" in key:
        theme = "education"
    elif "ui" in key or "sahel" in key:
        theme = "ui-kit"
    elif "devops" in key or "sdk" in key:
        theme = "devops"
    else:
        theme = "laptop-code"
    return image_url(theme, 1200, 630)


def video_url(index: int = 0) -> str:
    return SAMPLE_VIDEOS[index % len(SAMPLE_VIDEOS)]


def media_image(seed: str, alt: str = "") -> dict[str, Any]:
    return {
        "kind": "IMAGE",
        "url": image_url(seed),
        "texte_alternatif": alt or seed.replace("-", " "),
    }


def media_video(index: int = 0, alt: str = "Démo technique") -> dict[str, Any]:
    return {
        "kind": "VIDEO",
        "url": video_url(index),
        "texte_alternatif": alt,
    }
