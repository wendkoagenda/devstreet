"""CV automatique : données construites à la demande depuis le profil, règle de visibilité et rendu PDF (reportlab).

Le CV n'est jamais stocké : il est reconstruit à chaque téléchargement depuis Profil, ProfilSkill, Experience,
Prestation et les avis publics, donc toujours à jour.
"""
import unicodedata
from io import BytesIO
from typing import Optional
from xml.sax.saxutils import escape

from django.db.models import Avg, Count
from rest_framework.exceptions import NotFound, PermissionDenied
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from app.marketplace.models import Profil, Review

LEVEL_LABELS = {1: "Notions", 2: "Débutant", 3: "Intermédiaire", 4: "Avancé", 5: "Expert"}
MONTHS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def can_download_cv(viewer: Profil, target: Profil) -> bool:
    """Visibilité du CV : soi-même toujours ; « public » pour tout profil ; « entreprises » pour les recruteurs ; « privé » jamais."""
    if viewer.id == target.id:
        return True
    if target.cv_visibility == "public":
        return True
    if target.cv_visibility == "companies":
        return viewer.company_id is not None
    return False


def _month(value) -> str:
    return f"{MONTHS[value.month - 1]} {value.year}"


def _period(exp) -> str:
    end = "aujourd'hui" if exp.is_current or not exp.end_date else _month(exp.end_date)
    return f"{_month(exp.start_date)} – {end}"


def cv_data(profil: Profil) -> dict:
    """Contenu du CV d'un profil."""
    user = profil.user
    reviews = Review.objects.filter(target=profil, is_public=True)
    stats = reviews.aggregate(avg=Avg("rating"), total=Count("id"))
    return {
        "name": user.full_name or user.email.split("@")[0],
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


def _styles() -> dict:
    base = getSampleStyleSheet()["Normal"]
    ink, muted = colors.HexColor("#0f172a"), colors.HexColor("#475569")
    return {
        "name": ParagraphStyle("name", parent=base, fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=ink),
        "headline": ParagraphStyle("headline", parent=base, fontSize=12, leading=16, textColor=muted),
        "contact": ParagraphStyle("contact", parent=base, fontSize=9, leading=13, textColor=muted),
        "h": ParagraphStyle("h", parent=base, fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=ink, spaceBefore=12, spaceAfter=4),
        "body": ParagraphStyle("body", parent=base, fontSize=10, leading=14, textColor=colors.HexColor("#1e293b")),
        "role": ParagraphStyle("role", parent=base, fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=ink, spaceBefore=6),
        "meta": ParagraphStyle("meta", parent=base, fontSize=9, leading=12, textColor=muted),
    }


def render_cv_pdf(data: dict) -> bytes:
    """PDF A4 du CV (une colonne, polices standard : les caractères latins accentués sont pris en charge)."""
    style = _styles()
    story = [Paragraph(escape(data["name"]), style["name"])]
    if data["headline"]:
        story.append(Paragraph(escape(data["headline"]), style["headline"]))
    contact = [data["email"], data["phone"], data["location"], *data["links"]]
    story.append(Paragraph(escape(" · ".join(part for part in contact if part)), style["contact"]))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#cbd5e1")))

    def section(title: str):
        story.append(Paragraph(title.upper(), style["h"]))

    if data["bio"]:
        section("Profil")
        story.append(Paragraph(escape(data["bio"]).replace("\n", "<br/>"), style["body"]))
    if data["experiences"]:
        section("Expériences")
        for exp in data["experiences"]:
            story.append(Paragraph(escape(f"{exp['title']}, {exp['company']}"), style["role"]))
            place = f" · {exp['location']}" if exp["location"] else ""
            story.append(Paragraph(escape(exp["period"] + place), style["meta"]))
            if exp["description"]:
                story.append(Paragraph(escape(exp["description"]).replace("\n", "<br/>"), style["body"]))
            if exp["technologies"]:
                story.append(Paragraph(escape("Technologies : " + exp["technologies"]), style["meta"]))
    if data["skills"]:
        section("Compétences")
        story.append(
            Paragraph(escape(", ".join(f"{name} ({LEVEL_LABELS.get(level, level)})" for name, level in data["skills"])), style["body"])
        )
    if data["prestations"]:
        section("Prestations")
        for item in data["prestations"]:
            story.append(Paragraph(escape(item["title"]), style["role"]))
            if item["description"]:
                story.append(Paragraph(escape(item["description"]).replace("\n", "<br/>"), style["body"]))
    if data["languages"]:
        section("Langues")
        story.append(Paragraph(escape(", ".join(data["languages"])), style["body"]))
    if data["rating_avg"] is not None:
        section("Réputation")
        story.append(
            Paragraph(escape(f"Note moyenne {data['rating_avg']} / 5 sur {data['reviews_count']} avis publics"), style["body"])
        )

    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"CV {data['name']}",
        author=data["name"],
    )
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
    target = Profil.objects.select_related("user").filter(id=profil_id).first()
    if target is None:
        raise NotFound("Profil introuvable.")
    if not can_download_cv(viewer, target):
        raise PermissionDenied("Ce CV n'est pas accessible avec votre profil.")
    return target
