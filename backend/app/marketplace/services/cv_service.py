"""CV automatique : données construites à la demande depuis le profil, règle de visibilité et rendu PDF (reportlab).

Le CV n'est jamais stocké : il est reconstruit à chaque téléchargement depuis Profil, ProfilSkill, Experience,
Prestation et les avis publics, donc toujours à jour.
"""
import logging
import unicodedata
from io import BytesIO
from typing import List, Optional
from xml.sax.saxutils import escape

from django.db.models import Avg, Count
from rest_framework.exceptions import NotFound, PermissionDenied
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    FrameBreak,
    HRFlowable,
    KeepInFrame,
    NextPageTemplate,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from app.marketplace.cv_settings import color_hex, merged_settings
from app.metier.services.storage_service import get_storage_service
from app.marketplace.models import Profil, Review

logger = logging.getLogger(__name__)

LEVEL_LABELS = {1: "Notions", 2: "Débutant", 3: "Intermédiaire", 4: "Avancé", 5: "Expert"}
MONTHS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def can_download_cv(viewer: Profil, target: Profil) -> bool:
    """Visibilité du CV : soi-même toujours ; « public » pour tout profil ; « entreprises » pour les recruteurs ; « privé » jamais."""
    if viewer.id == target.id:
        return True
    if target.cv_visibility == "public":
        return True
    if target.cv_visibility == "companies":
        # « entreprises » : réservé aux membres ayant un profil entreprise
        return Profil.objects.filter(user_id=viewer.user_id, type=Profil.TYPE_ENTREPRISE).exists()
    return False


def _month(value) -> str:
    return f"{MONTHS[value.month - 1]} {value.year}"


def _period(exp) -> str:
    end = "aujourd'hui" if exp.is_current or not exp.end_date else _month(exp.end_date)
    return f"{_month(exp.start_date)} – {end}"


PHOTO_MAX_BYTES = 8 * 1024 * 1024
PHOTO_PIXELS = 480


class PhotoUnavailable(Exception):
    """La photo de profil ne peut pas figurer sur le CV (fichier absent, trop gros ou illisible)."""


def _no_photo(error: PhotoUnavailable) -> None:
    """
    Un CV sans photo vaut mieux qu'un CV qui échoue : le motif est journalisé pour qu'on puisse le corriger,
    et le CV est produit avec les initiales à la place de la photo.
    """
    logger.warning("CV sans photo : %s", error, exc_info=error.__cause__ is not None)
    return None


def _square_photo(raw: bytes) -> bytes:
    """Photo recadrée au carré (centrée), en PNG. La forme est donnée au dessin. Lève PhotoUnavailable si ce n'est pas une image."""
    from PIL import Image, ImageOps

    try:
        with Image.open(BytesIO(raw)) as image:
            square = ImageOps.fit(ImageOps.exif_transpose(image).convert("RGB"), (PHOTO_PIXELS, PHOTO_PIXELS))
    except Exception as exc:  # noqa: BLE001 - tout format illisible est ramené à une erreur nommée
        raise PhotoUnavailable("fichier illisible") from exc
    buffer = BytesIO()
    square.save(buffer, format="PNG")
    return buffer.getvalue()


def _profile_photo(profil: Profil) -> Optional[bytes]:
    """Photo de profil du membre, prête pour le CV (carrée, PNG). None sans photo ou si elle est introuvable."""
    path = profil.user.photo or profil.photo
    if not path:
        return None
    try:
        return _square_photo(_read_photo(path))
    except PhotoUnavailable as error:
        return _no_photo(error)


def _read_photo(path: str) -> bytes:
    """Octets de la photo dans le stockage. Lève PhotoUnavailable si le fichier manque, est injoignable ou trop gros."""
    try:
        with get_storage_service().open(path) as handle:
            raw = handle.read(PHOTO_MAX_BYTES + 1)
    except Exception as exc:  # noqa: BLE001 - absent, droits, stockage objet injoignable : même traitement
        raise PhotoUnavailable("fichier introuvable") from exc
    if len(raw) > PHOTO_MAX_BYTES:
        raise PhotoUnavailable("fichier trop gros")
    return raw


def cv_data(profil: Profil) -> dict:
    """Contenu du CV d'un profil."""
    user = profil.user
    reviews = Review.objects.filter(target=profil, is_public=True)
    stats = reviews.aggregate(avg=Avg("rating"), total=Count("id"))
    return {
        "name": user.full_name or user.email.split("@")[0],
        "photo": _profile_photo(profil),
        "settings": merged_settings(profil.cv_settings),
        "headline": profil.headline,
        "email": user.email,
        "phone": profil.phone,
        "location": ", ".join(part for part in (profil.city, profil.country) if part),
        "links": [url for url in (profil.github_url, profil.linkedin_url, profil.portfolio_url) if url],
        "bio": profil.bio,
        "years_of_experience": profil.years_of_experience,
        "languages": [item.get("language") for item in profil.languages if isinstance(item, dict) and item.get("language")],
        "skills": [
            (item.skill.name, item.level)
            for item in profil.profil_skills.select_related("skill").order_by("-level", "skill__name")
        ],
        "experiences": [
            {
                "title": exp.title,
                "company": exp.company_name,
                "location": exp.location,
                "period": f"{_month(exp.start_date)} – {'aujourd\'hui' if exp.is_current or not exp.end_date else _month(exp.end_date)}",
                "description": exp.description,
                "technologies": exp.technologies,
            }
            for exp in profil.experiences.order_by("-start_date")
        ],
        "prestations": [
            {"title": item.title, "description": item.description}
            for item in profil.prestations.filter(is_active=True).order_by("-id")
        ],
        "rating_avg": round(float(stats["avg"]), 1) if stats["avg"] is not None else None,
        "reviews_count": stats["total"],
    }


PAGE_W, PAGE_H = A4
SIDEBAR_W = 6.6 * cm
SIDE_PAD = 0.75 * cm
MAIN_GAP = 0.9 * cm
MAIN_MARGIN = 1.5 * cm
MAIN_W = PAGE_W - SIDEBAR_W - MAIN_GAP - MAIN_MARGIN
SIDE_W = SIDEBAR_W - 2 * SIDE_PAD
PHOTO_DIAMETER = 3.7 * cm
MAX_SKILLS = 14
INK = colors.HexColor("#1E1B2E")
MUTED = colors.HexColor("#5B5670")

# Polices de base de la norme PDF (toujours disponibles) : (normale, gras, échelle de taille)
FONT_FAMILIES = {
    "sans": ("Helvetica", "Helvetica-Bold", 1.0),
    "serif": ("Times-Roman", "Times-Bold", 1.06),
    "mono": ("Courier", "Courier-Bold", 0.92),
}
# Densité : échelle des interlignes et des espaces
DENSITY_SCALE = {"compact": 0.9, "standard": 1.0, "airy": 1.14}


def _mix(first, second, weight: float):
    """Mélange de deux couleurs : 0 = `first`, 1 = `second`."""
    return colors.Color(
        first.red * (1 - weight) + second.red * weight,
        first.green * (1 - weight) + second.green * weight,
        first.blue * (1 - weight) + second.blue * weight,
    )


def _hex(color) -> str:
    return "#" + color.hexval()[2:]


def _palette(settings: dict) -> dict:
    """
    Couleurs du CV dérivées de la couleur principale choisie : titres, fond clair, bordures, et couleurs de la bande
    latérale (pleine : texte clair ou foncé selon la luminosité de la couleur ; claire : texte foncé).
    """
    main = colors.HexColor(color_hex(settings))
    luminance = 0.2126 * main.red + 0.7152 * main.green + 0.0722 * main.blue
    soft = _mix(main, colors.white, 0.94)
    if settings["sidebar_style"] == "filled":
        dark_text = luminance > 0.55
        on = INK if dark_text else _mix(main, colors.white, 0.95)
        side = {
            "bg": main,
            "text": on,
            "muted": _mix(on, main, 0.35),
            "track": _mix(main, colors.black if dark_text else colors.white, 0.25),
            "fill": on,
            "ring": on,
            "initials_bg": _mix(main, colors.black if dark_text else colors.white, 0.2),
        }
    else:
        side = {
            "bg": soft,
            "text": INK,
            "muted": MUTED,
            "track": _mix(main, colors.white, 0.8),
            "fill": main,
            "ring": main,
            "initials_bg": main,
        }
    side["heading"] = side["text"] if settings["sidebar_style"] == "filled" else main
    return {
        "main": main,
        "soft": soft,
        "border": _mix(main, colors.white, 0.82),
        "accent_bar": _mix(main, colors.white, 0.18),
        "side": side,
    }


def _styles(settings: dict, palette: dict) -> dict:
    regular, bold, font_scale = FONT_FAMILIES[settings["font"]]
    density = DENSITY_SCALE[settings["density"]]
    side = palette["side"]
    base = getSampleStyleSheet()["Normal"]

    def style(name, size, lead, **kwargs):
        return ParagraphStyle(
            name,
            parent=base,
            fontName=kwargs.pop("fontName", regular),
            fontSize=size * font_scale,
            leading=lead * font_scale * density,
            **{k: (v * density if k in ("spaceBefore", "spaceAfter") else v) for k, v in kwargs.items()},
        )

    return {
        "name": style("name", 26, 29, fontName=bold, textColor=INK),
        "headline": style("headline", 12.5, 17, textColor=palette["main"], spaceBefore=3),
        "h": style("h", 10.5, 13, fontName=bold, textColor=palette["main"], spaceBefore=15, spaceAfter=3),
        "body": style("body", 9.8, 14, textColor=INK),
        "role": style("role", 10.5, 13.5, fontName=bold, textColor=INK),
        "company": style("company", 9.8, 13, textColor=palette["main"]),
        "period": style("period", 8.8, 12, textColor=MUTED, alignment=TA_RIGHT),
        "meta": style("meta", 8.8, 12, textColor=MUTED),
        # Bande latérale
        "side_h": style("side_h", 9.5, 12, fontName=bold, textColor=side["heading"], spaceBefore=14, spaceAfter=4),
        "side": style("side", 8.8, 12.5, textColor=side["text"]),
        "side_muted": style("side_muted", 8.2, 11.5, textColor=side["muted"]),
    }


class ProfilePhoto(Flowable):
    """Photo de profil (ronde ou carrée à coins arrondis) avec un anneau, ou, sans photo, un bloc avec les initiales."""

    def __init__(self, png: Optional[bytes], name: str, diameter: float, shape: str, side: dict, bold_font: str):
        super().__init__()
        self.png, self.name, self.diameter, self.shape = png, name, diameter, shape
        self.side, self.bold_font = side, bold_font
        self.width = self.height = diameter + 8

    def wrap(self, avail_width, avail_height):
        return self.width, self.height

    def _outline(self, canvas, x, y, size, fill=0, stroke=0):
        if self.shape == "round":
            canvas.circle(x + size / 2, y + size / 2, size / 2, stroke=stroke, fill=fill)
        else:
            canvas.roundRect(x, y, size, size, size * 0.1, stroke=stroke, fill=fill)

    def draw(self):
        canvas, d = self.canv, self.diameter
        x = y = (self.width - d) / 2
        canvas.saveState()
        # Anneau
        canvas.setFillColor(self.side["ring"])
        self._outline(canvas, x - 3, y - 3, d + 6, fill=1)
        if self.png:
            canvas.saveState()
            path = canvas.beginPath()
            if self.shape == "round":
                path.circle(x + d / 2, y + d / 2, d / 2)
            else:
                path.roundRect(x, y, d, d, d * 0.1)
            canvas.clipPath(path, stroke=0, fill=0)
            canvas.drawImage(ImageReader(BytesIO(self.png)), x, y, d, d)
            canvas.restoreState()
        else:
            canvas.setFillColor(self.side["initials_bg"])
            self._outline(canvas, x, y, d, fill=1)
            initials = "".join(part[0] for part in self.name.split()[:2]).upper() or "?"
            canvas.setFillColor(self.side["text"] if self.side["text"] != self.side["ring"] else colors.white)
            canvas.setFont(self.bold_font, d * 0.34)
            canvas.drawCentredString(x + d / 2, y + d / 2 - d * 0.12, initials)
        canvas.restoreState()


class SkillBar(Flowable):
    """Compétence avec une barre de niveau (sur 5)."""

    def __init__(self, name: str, level: int, width: float, side: dict, font: str):
        super().__init__()
        self.name, self.level, self.side, self.font = name, max(0, min(5, level)), side, font
        self.width, self.height = width, 0.78 * cm

    def wrap(self, avail_width, avail_height):
        return self.width, self.height

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        canvas.setFillColor(self.side["text"])
        canvas.setFont(self.font, 8.6)
        label = _fit(canvas, self.name, self.font, 8.6, self.width)
        canvas.drawString(0, self.height - 8.5, label)
        track_y, track_h = 2, 3.2
        canvas.setFillColor(self.side["track"])
        canvas.roundRect(0, track_y, self.width, track_h, track_h / 2, stroke=0, fill=1)
        canvas.setFillColor(self.side["fill"])
        canvas.roundRect(0, track_y, self.width * self.level / 5, track_h, track_h / 2, stroke=0, fill=1)
        canvas.restoreState()


class SkillDots(Flowable):
    """Compétence avec cinq points (niveau sur 5), alignés à droite du nom."""

    def __init__(self, name: str, level: int, width: float, side: dict, font: str):
        super().__init__()
        self.name, self.level, self.side, self.font = name, max(0, min(5, level)), side, font
        self.width, self.height = width, 0.52 * cm

    def wrap(self, avail_width, avail_height):
        return self.width, self.height

    def draw(self):
        canvas, radius, gap = self.canv, 2.3, 3.4
        dots_width = 5 * 2 * radius + 4 * gap
        canvas.saveState()
        canvas.setFillColor(self.side["text"])
        canvas.setFont(self.font, 8.6)
        canvas.drawString(0, 3, _fit(canvas, self.name, self.font, 8.6, self.width - dots_width - 6))
        for index in range(5):
            cx = self.width - dots_width + radius + index * (2 * radius + gap)
            canvas.setFillColor(self.side["fill"] if index < self.level else self.side["track"])
            canvas.circle(cx, 5, radius, stroke=0, fill=1)
        canvas.restoreState()


def _fit(canvas, text: str, font: str, size: float, width: float) -> str:
    """Texte raccourci avec « … » pour tenir dans la largeur donnée."""
    if canvas.stringWidth(text, font, size) <= width:
        return text
    while len(text) > 1 and canvas.stringWidth(text + "…", font, size) > width:
        text = text[:-1]
    return text.rstrip() + "…"


def _short_link(url: str) -> str:
    return url.replace("https://", "").replace("http://", "").rstrip("/")


def _paragraph(text: str, style) -> Paragraph:
    return Paragraph(escape(text).replace("\n", "<br/>"), style)


def render_cv_pdf(data: dict) -> bytes:
    """
    PDF A4 du CV en deux colonnes : une bande latérale (photo, contact, compétences, langues…) et la colonne principale
    (nom, profil, expériences, prestations). Le style suit les réglages du profil (`data["settings"]`) : couleur,
    police, côté et style de la bande, forme de la photo, présentation des compétences, densité, sections masquées.
    Polices de base de la norme PDF : les caractères latins accentués passent.
    """
    settings = merged_settings(None, data.get("settings"))
    palette = _palette(settings)
    side_colors = palette["side"]
    style = _styles(settings, palette)
    regular, bold, _scale = FONT_FAMILIES[settings["font"]]
    hidden = set(settings["hidden_sections"])
    show = lambda section: section not in hidden  # noqa: E731

    # ── Bande latérale ──
    side: List = [Spacer(1, 0.2 * cm)]
    if settings["photo"] != "none":
        side.append(ProfilePhoto(data.get("photo"), data["name"], PHOTO_DIAMETER, settings["photo"], side_colors, bold))
    if show("contact"):
        contact_lines = [escape(part) for part in (data["email"], data["phone"], data["location"]) if part] + [
            f'<a href="{escape(url)}" color="{_hex(side_colors["text"])}">{escape(_short_link(url))}</a>'
            for url in data["links"]
        ]
        if contact_lines:
            side.append(Paragraph("CONTACT", style["side_h"]))
            for line in contact_lines:
                side.append(Paragraph(line, style["side"]))
                side.append(Spacer(1, 2))
    if show("skills") and data["skills"]:
        side.append(Paragraph("COMPÉTENCES", style["side_h"]))
        skills = data["skills"][:MAX_SKILLS]
        if settings["skills"] == "text":
            for name, level in skills:
                side.append(Paragraph(f"{escape(name)} <font color=\"{_hex(side_colors['muted'])}\">· {LEVEL_LABELS.get(level, level)}</font>", style["side"]))
        else:
            widget = SkillBar if settings["skills"] == "bars" else SkillDots
            for name, level in skills:
                side.append(widget(name, level, SIDE_W, side_colors, regular))
    if show("languages") and data["languages"]:
        side.append(Paragraph("LANGUES", style["side_h"]))
        for language in data["languages"]:
            side.append(Paragraph(escape(language), style["side"]))
    if data["years_of_experience"]:
        side.append(Paragraph("EXPÉRIENCE", style["side_h"]))
        side.append(Paragraph(f"{data['years_of_experience']} an(s)", style["side"]))
    if show("reputation") and data["rating_avg"] is not None:
        side.append(Paragraph("RÉPUTATION", style["side_h"]))
        side.append(Paragraph(f"{data['rating_avg']} / 5", style["side"]))
        side.append(Paragraph(f"{data['reviews_count']} avis publics", style["side_muted"]))

    # ── Colonne principale ──
    main: List = [Paragraph(escape(data["name"]), style["name"])]
    if data["headline"]:
        main.append(Paragraph(escape(data["headline"]), style["headline"]))
    main.append(Spacer(1, 5))
    main.append(HRFlowable(width="100%", thickness=1.2, color=palette["border"], spaceAfter=2))

    def section(title: str):
        main.append(Paragraph(title.upper(), style["h"]))

    if show("bio") and data["bio"]:
        section("Profil")
        main.append(_paragraph(data["bio"], style["body"]))
    if show("experiences") and data["experiences"]:
        section("Expériences")
        for exp in data["experiences"]:
            head = Table(
                [[
                    [Paragraph(escape(exp["title"]), style["role"]), Paragraph(escape(exp["company"]), style["company"])],
                    Paragraph(escape(exp["period"]), style["period"]),
                ]],
                colWidths=[MAIN_W - 3.3 * cm, 3.3 * cm],
            )
            head.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            main.append(Spacer(1, 5))
            main.append(head)
            if exp["location"]:
                main.append(Paragraph(escape(exp["location"]), style["meta"]))
            if exp["description"]:
                main.append(_paragraph(exp["description"], style["body"]))
            if exp["technologies"]:
                main.append(Paragraph(escape("Technologies : " + exp["technologies"]), style["meta"]))
    if show("prestations") and data["prestations"]:
        section("Prestations")
        for item in data["prestations"]:
            main.append(Spacer(1, 3))
            main.append(Paragraph(escape(item["title"]), style["role"]))
            if item["description"]:
                main.append(_paragraph(item["description"], style["body"]))

    # ── Document : la 1re page a bande + colonne ; les suivantes n'ont que la colonne principale ──
    side_left = settings["sidebar"] == "left"
    sidebar_x = 0 if side_left else PAGE_W - SIDEBAR_W
    main_x = SIDEBAR_W + MAIN_GAP if side_left else MAIN_MARGIN
    side_top = PAGE_H - 1.2 * cm

    def draw_page(canvas, _document):
        """Fond de chaque page : bande latérale et liseré d'accent en haut de la colonne principale."""
        canvas.saveState()
        canvas.setFillColor(side_colors["bg"])
        canvas.rect(sidebar_x, 0, SIDEBAR_W, PAGE_H, stroke=0, fill=1)
        if settings["sidebar_style"] == "light":
            canvas.setStrokeColor(palette["border"])
            canvas.setLineWidth(0.8)
            edge = sidebar_x + SIDEBAR_W if side_left else sidebar_x
            canvas.line(edge, 0, edge, PAGE_H)
        canvas.setFillColor(palette["accent_bar"])
        bar_x = SIDEBAR_W if side_left else 0
        canvas.rect(bar_x, PAGE_H - 0.28 * cm, PAGE_W - SIDEBAR_W, 0.28 * cm, stroke=0, fill=1)
        canvas.restoreState()

    flat = dict(leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    side_frame = Frame(sidebar_x + SIDE_PAD, 1.2 * cm, SIDE_W, side_top - 1.2 * cm, id="side", **flat)
    main_frame = Frame(main_x, 1.5 * cm, MAIN_W, PAGE_H - 3.0 * cm, id="main", **flat)
    later_frame = Frame(main_x, 1.5 * cm, MAIN_W, PAGE_H - 3.0 * cm, id="later_main", **flat)

    buffer = BytesIO()
    document = BaseDocTemplate(
        buffer,
        pagesize=A4,
        title=f"CV {data['name']}",
        author=data["name"],
        pageTemplates=[
            PageTemplate(id="first", frames=[side_frame, main_frame], onPage=draw_page),
            PageTemplate(id="later", frames=[later_frame], onPage=draw_page),
        ],
    )
    story = [
        NextPageTemplate("later"),
        # La bande latérale est réduite pour tenir dans son cadre : elle ne déborde jamais sur la colonne principale
        KeepInFrame(SIDE_W, side_top - 1.2 * cm, side, mode="shrink"),
        FrameBreak(),
        *main,
    ]
    document.build(story)
    return buffer.getvalue()


def cv_filename(data: dict) -> str:
    """Nom de fichier sûr (ASCII, accents retirés) : CV_Prenom_Nom.pdf."""
    ascii_name = unicodedata.normalize("NFKD", data["name"]).encode("ascii", "ignore").decode()
    cleaned = "".join(char if char.isalnum() or char in "-_" else "_" for char in ascii_name.replace(" ", "_"))
    return f"CV_{cleaned.strip('_') or 'profil'}.pdf"


def get_cv_profil(profil_id: Optional[int], viewer: Profil) -> Profil:
    """Profil dont le CV est demandé (None : le mien) ; 404 si inconnu, 403 si sa visibilité l'interdit."""
    if profil_id is None or profil_id == viewer.id:
        return viewer
    target = Profil.objects.select_related("user").filter(id=profil_id, type=Profil.TYPE_DEV).first()
    if target is None:
        raise NotFound("Profil introuvable.")
    if not can_download_cv(viewer, target):
        raise PermissionDenied("Ce CV n'est pas accessible avec votre profil.")
    return target
