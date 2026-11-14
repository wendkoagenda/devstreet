"""Profil utilisateur : calendrier de disponibilité, expériences et CV automatique (PDF)."""
from datetime import date

from django.test import TestCase
from rest_framework.test import APITestCase

from app.marketplace.factories import (
    make_availability,
    make_company,
    make_experience,
    make_prestation,
    make_profil,
    make_profil_skill,
    make_review,
    make_skill,
    make_user,
)
from app.marketplace.models import Availability, Experience, Prestation
from app.marketplace.services.cv_service import (
    PhotoUnavailable,
    _square_photo,
    can_download_cv,
    cv_data,
    cv_filename,
    render_cv_pdf,
)
from app.tests.test_marketplace_market import login


class ProfileBase(APITestCase):
    def setUp(self):
        self.by = make_user()
        self.user = make_user(first_name="Ibrahim", last_name="Ouédraogo", email="ibrahim@example.com")
        self.profil = make_profil(self.by, user=self.user, headline="Dev web junior", bio="Premier stage.")
        login(self.client, self.user)


class AvailabilityApiTests(ProfileBase):
    URL = "/api/v1/marketplace/me/availabilities"
    BODY = {"start_date": "2026-12-01", "end_date": "2026-12-11", "status": "available", "hours_per_week": 40}

    def test_create_and_list(self):
        response = self.client.post(self.URL, self.BODY, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["source"], "manual")
        self.assertEqual([row["start_date"] for row in self.client.get(self.URL).data], ["2026-12-01"])

    def test_overlap_is_refused(self):
        self.client.post(self.URL, self.BODY, format="json")
        response = self.client.post(self.URL, {**self.BODY, "start_date": "2026-12-05", "end_date": "2026-12-20"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Availability.objects.count(), 1)

    def test_end_before_start_is_refused(self):
        self.assertEqual(self.client.post(self.URL, {**self.BODY, "end_date": "2026-11-01"}, format="json").status_code, 400)

    def test_update_and_delete_manual_period(self):
        created = self.client.post(self.URL, self.BODY, format="json").data
        updated = self.client.patch(f"{self.URL}/{created['id']}", {"status": "partial", "hours_per_week": 20}, format="json")
        self.assertEqual((updated.status_code, updated.data["status"]), (200, "partial"))
        self.assertEqual(self.client.delete(f"{self.URL}/{created['id']}").status_code, 204)
        self.assertFalse(Availability.objects.exists())

    def test_mission_period_is_read_only(self):
        mission = make_availability(self.by, profil=self.profil, source="mission", status="busy")
        self.assertEqual(self.client.patch(f"{self.URL}/{mission.id}", {"note": "x"}, format="json").status_code, 400)
        self.assertEqual(self.client.delete(f"{self.URL}/{mission.id}").status_code, 400)
        self.assertTrue(Availability.objects.filter(id=mission.id).exists())

    def test_cannot_touch_someone_elses_period(self):
        other = make_availability(self.by, profil=make_profil(self.by))
        self.assertEqual(self.client.delete(f"{self.URL}/{other.id}").status_code, 404)
        self.assertEqual(self.client.get(self.URL).data, [])

    def test_requires_profil(self):
        login(self.client, make_user())
        self.assertEqual(self.client.get(self.URL).status_code, 403)


class ExperienceApiTests(ProfileBase):
    URL = "/api/v1/marketplace/me/experiences"
    BODY = {"title": "Développeur junior", "company_name": "Agence web", "start_date": "2022-01-01", "end_date": "2024-01-01"}

    def test_crud(self):
        created = self.client.post(self.URL, self.BODY, format="json")
        self.assertEqual(created.status_code, 201, created.data)
        pk = created.data["id"]
        self.assertEqual(self.client.patch(f"{self.URL}/{pk}", {"location": "Lomé"}, format="json").data["location"], "Lomé")
        self.assertEqual(len(self.client.get(self.URL).data), 1)
        self.assertEqual(self.client.delete(f"{self.URL}/{pk}").status_code, 204)
        self.assertFalse(Experience.objects.exists())

    def test_current_experience_has_no_end_date(self):
        response = self.client.post(self.URL, {**self.BODY, "is_current": True}, format="json")
        self.assertIsNone(response.data["end_date"])

    def test_end_before_start_is_refused(self):
        self.assertEqual(self.client.post(self.URL, {**self.BODY, "end_date": "2021-01-01"}, format="json").status_code, 400)

    def test_cannot_edit_someone_elses_experience(self):
        other = make_experience(self.by, profil=make_profil(self.by))
        self.assertEqual(self.client.patch(f"{self.URL}/{other.id}", {"title": "x"}, format="json").status_code, 404)


class PrestationApiTests(ProfileBase):
    URL = "/api/v1/marketplace/me/prestations"
    BODY = {
        "title": "Landing page en 5 jours",
        "description": "Création d'une landing responsive avec formulaire de contact.",
        "category": "web",
        "price": "150000.00",
        "delivery_days": 5,
        "revisions": 2,
    }

    def test_crud(self):
        created = self.client.post(self.URL, self.BODY, format="json")
        self.assertEqual(created.status_code, 201, created.data)
        self.assertTrue(created.data["slug"])
        self.assertTrue(created.data["is_active"])
        pk = created.data["id"]
        updated = self.client.patch(f"{self.URL}/{pk}", {"price": "175000.00", "is_active": False}, format="json")
        self.assertEqual(updated.status_code, 200, updated.data)
        self.assertEqual(updated.data["price"], "175000.00")
        self.assertFalse(updated.data["is_active"])
        self.assertEqual(len(self.client.get(self.URL).data), 1)
        self.assertEqual(self.client.delete(f"{self.URL}/{pk}").status_code, 204)
        self.assertFalse(Prestation.objects.exists())

    def test_invalid_category_refused(self):
        response = self.client.post(self.URL, {**self.BODY, "category": "blockchain"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_cannot_edit_someone_elses_prestation(self):
        other = make_prestation(self.by, profil=make_profil(self.by))
        self.assertEqual(self.client.patch(f"{self.URL}/{other.id}", {"title": "x"}, format="json").status_code, 404)

    def test_public_profile_lists_active_prestations_only(self):
        make_prestation(self.by, profil=self.profil, title="Active", is_active=True)
        make_prestation(self.by, profil=self.profil, title="Inactive", is_active=False)
        response = self.client.get(f"/api/v1/marketplace/profils/{self.profil.id}")
        self.assertEqual(response.status_code, 200)
        titles = [row["title"] for row in response.data["prestations"]]
        self.assertEqual(titles, ["Active"])


class CvVisibilityTests(TestCase):
    def setUp(self):
        self.by = make_user()
        self.company = make_company(self.by)
        self.recruiter = make_profil(self.by, company=self.company)
        self.dev = make_profil(self.by)

    def test_rules(self):
        for visibility, recruiter_ok, dev_ok in (("public", True, True), ("companies", True, False), ("private", False, False)):
            target = make_profil(self.by, cv_visibility=visibility)
            self.assertEqual(can_download_cv(self.recruiter, target), recruiter_ok, visibility)
            self.assertEqual(can_download_cv(self.dev, target), dev_ok, visibility)
            self.assertTrue(can_download_cv(target, target))


class CvApiTests(ProfileBase):
    def test_my_cv_is_a_pdf_built_from_the_profile(self):
        skill = make_skill(self.by, name="Django Y", slug="django-y")
        make_profil_skill(self.by, profil=self.profil, skill=skill, level=4)
        make_experience(self.by, profil=self.profil, title="Stagiaire", company_name="Resto Éxpress")
        make_prestation(self.by, profil=self.profil)
        make_review(self.by, target=self.profil, rating=5)
        response = self.client.get("/api/v1/marketplace/me/cv")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertIn("CV_Ibrahim_Ouedraogo", response["Content-Disposition"])
        self.assertTrue(response["Content-Disposition"].isascii())
        data = cv_data(self.profil)
        self.assertEqual(data["skills"], [("Django Y", 4)])
        self.assertEqual(data["experiences"][0]["company"], "Resto Éxpress")
        self.assertEqual((data["rating_avg"], data["reviews_count"]), (5.0, 1))

    def test_other_cv_respects_visibility(self):
        target = make_profil(self.by, cv_visibility="private")
        self.assertEqual(self.client.get(f"/api/v1/marketplace/profils/{target.id}/cv").status_code, 403)
        target.cv_visibility = "public"
        target.save()
        self.assertEqual(self.client.get(f"/api/v1/marketplace/profils/{target.id}/cv").status_code, 200)
        self.assertEqual(self.client.get("/api/v1/marketplace/profils/999999/cv").status_code, 404)

    def test_companies_cv_is_for_recruiters_only(self):
        target = make_profil(self.by, cv_visibility="companies")
        self.assertEqual(self.client.get(f"/api/v1/marketplace/profils/{target.id}/cv").status_code, 403)
        recruiter_user = make_user()
        make_profil(self.by, user=recruiter_user, company=make_company(self.by))
        login(self.client, recruiter_user)
        self.assertEqual(self.client.get(f"/api/v1/marketplace/profils/{target.id}/cv").status_code, 200)

    def test_requires_profil_and_auth(self):
        login(self.client, make_user())
        self.assertEqual(self.client.get("/api/v1/marketplace/me/cv").status_code, 403)
        self.client.credentials()
        self.assertEqual(self.client.get("/api/v1/marketplace/me/cv").status_code, 401)

    def test_pdf_handles_markup_characters_and_long_text(self):
        self.profil.bio = "Ligne <b>1</b> & « accents éàü »\n" + "texte long " * 400
        self.profil.save()
        make_experience(self.by, profil=self.profil, title="Dev <script>", company_name="A&B", description="x" * 3000)
        pdf = render_cv_pdf(cv_data(self.profil))
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 1000)

    def test_filename_is_ascii(self):
        self.assertEqual(cv_filename({"name": "Aïcha Traoré"}), "CV_Aicha_Traore.pdf")
        self.assertEqual(cv_filename({"name": ""}), "CV_profil.pdf")

    def test_public_profile_exposes_cv_access(self):
        target = make_profil(self.by, cv_visibility="public")
        self.assertTrue(self.client.get(f"/api/v1/marketplace/profils/{target.id}").data["can_download_cv"])
        hidden = make_profil(self.by, cv_visibility="private")
        self.assertFalse(self.client.get(f"/api/v1/marketplace/profils/{hidden.id}").data["can_download_cv"])

    # ── Photo de profil sur le CV ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def _jpeg(width=300, height=200) -> bytes:
        from io import BytesIO

        from PIL import Image

        buffer = BytesIO()
        Image.new("RGB", (width, height), (200, 120, 80)).save(buffer, format="JPEG")
        return buffer.getvalue()

    def test_square_photo_is_a_centered_square_png(self):
        from io import BytesIO

        from PIL import Image

        image = Image.open(BytesIO(_square_photo(self._jpeg(300, 200))))
        self.assertEqual(image.format, "PNG")
        self.assertEqual(image.size[0], image.size[1])

    def test_unreadable_photo_gives_no_image(self):
        with self.assertRaises(PhotoUnavailable):
            _square_photo(b"pas une image")

    def test_cv_embeds_the_profile_photo(self):
        from io import BytesIO
        from unittest import mock

        self.profil.user.photo = "profile_photos/moi.jpg"
        self.profil.user.save()
        storage = mock.Mock()
        storage.open.return_value = BytesIO(self._jpeg())
        with mock.patch("app.marketplace.services.cv_service.get_storage_service", return_value=storage):
            data = cv_data(self.profil)
        self.assertTrue(data["photo"].startswith(b"\x89PNG"))
        self.assertIn(b"/Subtype /Image", render_cv_pdf(data))
        storage.open.assert_called_once_with("profile_photos/moi.jpg")

    def test_cv_without_photo_or_with_missing_file_still_works(self):
        from unittest import mock

        self.assertIsNone(cv_data(self.profil)["photo"])
        self.assertTrue(render_cv_pdf(cv_data(self.profil)).startswith(b"%PDF"))
        self.profil.user.photo = "profile_photos/absente.jpg"
        self.profil.user.save()
        storage = mock.Mock()
        storage.open.side_effect = FileNotFoundError("absente")
        with mock.patch("app.marketplace.services.cv_service.get_storage_service", return_value=storage):
            data = cv_data(self.profil)
        self.assertIsNone(data["photo"])
        self.assertTrue(render_cv_pdf(data).startswith(b"%PDF"))


class CvSettingsTests(ProfileBase):
    URL = "/api/v1/marketplace/me/cv-settings"

    def test_defaults_until_the_member_changes_something(self):
        data = self.client.get(self.URL).data
        self.assertEqual(data["settings"]["color"], "violet")
        self.assertEqual(data["settings"]["font"], "sans")
        self.assertEqual(data["settings"]["hidden_sections"], [])
        self.assertIn("bleu", data["presets"])

    def test_patch_saves_and_keeps_the_other_settings(self):
        self.assertEqual(self.client.patch(self.URL, {"color": "bleu", "font": "serif"}, format="json").status_code, 200)
        self.client.patch(self.URL, {"density": "compact"}, format="json")
        settings = self.client.get(self.URL).data["settings"]
        self.assertEqual((settings["color"], settings["font"], settings["density"]), ("bleu", "serif", "compact"))
        self.profil.refresh_from_db()
        self.assertEqual(self.profil.cv_settings["color"], "bleu")

    def test_custom_hex_color_is_accepted_and_normalized(self):
        self.client.patch(self.URL, {"color": "#1a2b3c"}, format="json")
        self.assertEqual(self.client.get(self.URL).data["settings"]["color"], "#1A2B3C")

    def test_invalid_values_are_refused(self):
        for payload in ({"color": "bleu clair"}, {"color": "#12345"}, {"font": "comic"}, {"hidden_sections": ["nope"]},
                        {"sidebar": "top"}):
            self.assertEqual(self.client.patch(self.URL, payload, format="json").status_code, 400, payload)

    def test_delete_resets_to_defaults(self):
        self.client.patch(self.URL, {"color": "rouge"}, format="json")
        self.assertEqual(self.client.delete(self.URL).data["settings"]["color"], "violet")

    def test_requires_a_dev_profile(self):
        login(self.client, make_user())
        self.assertEqual(self.client.get(self.URL).status_code, 403)

    def test_every_style_combination_renders_a_pdf(self):
        from app.marketplace.cv_settings import (
            DENSITIES, FONTS, PHOTOS, SIDEBAR_STYLES, SIDEBARS, SKILL_STYLES,
        )

        skill = make_skill(self.by, name="Django Z", slug="django-z")
        make_profil_skill(self.by, profil=self.profil, skill=skill, level=3)
        make_experience(self.by, profil=self.profil, title="Dev", company_name="Acme")
        for font in FONTS:
            for sidebar in SIDEBARS:
                for style in SIDEBAR_STYLES:
                    for photo in PHOTOS:
                        for skills in SKILL_STYLES:
                            for density in DENSITIES:
                                settings = {"color": "#FFE066", "font": font, "sidebar": sidebar, "sidebar_style": style,
                                            "photo": photo, "skills": skills, "density": density}
                                data = cv_data(self.profil)
                                data["settings"] = {**data["settings"], **settings}
                                self.assertTrue(render_cv_pdf(data).startswith(b"%PDF"), settings)

    def test_hidden_sections_are_left_out(self):
        from app.marketplace.cv_settings import SECTIONS

        make_experience(self.by, profil=self.profil, title="Dev", company_name="Acme")
        full = render_cv_pdf(cv_data(self.profil))
        data = cv_data(self.profil)
        data["settings"] = {**data["settings"], "hidden_sections": list(SECTIONS)}
        self.assertLess(len(render_cv_pdf(data)), len(full))

    def test_preview_uses_query_settings_without_saving_them(self):
        saved = self.client.get("/api/v1/marketplace/me/cv").content
        preview = self.client.get("/api/v1/marketplace/me/cv?color=rouge&font=mono&hidden_sections=bio,skills")
        self.assertEqual(preview.status_code, 200)
        self.assertNotEqual(preview.content, saved)
        self.profil.refresh_from_db()
        self.assertEqual(self.profil.cv_settings, {})
        self.assertEqual(self.client.get("/api/v1/marketplace/me/cv?color=pas-une-couleur").status_code, 400)

    def test_someone_else_cv_follows_the_owner_settings_not_the_query(self):
        target = make_profil(self.by, cv_visibility="public")
        url = f"/api/v1/marketplace/profils/{target.id}/cv"
        plain = self.client.get(url).content
        self.assertEqual(self.client.get(url + "?color=rouge&font=mono").content, plain)
