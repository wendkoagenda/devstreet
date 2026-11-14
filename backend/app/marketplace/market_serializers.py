"""Validation des corps de requête des écrans utilisateur (offres, candidatures, compétences)."""
from rest_framework import serializers

from app.marketplace.models import Availability, Experience, Offer, Prestation

_choice = lambda field: [value for value, _label in Offer._meta.get_field(field).choices]  # noqa: E731


class OfferWriteSerializer(serializers.Serializer):
    """Offre saisie par un recruteur : l'entreprise, le recruteur, le slug et le statut initial sont gérés côté serveur."""

    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    type = serializers.ChoiceField(choices=_choice("type"))
    contract_duration = serializers.IntegerField(min_value=1, max_value=10000, required=False, allow_null=True)
    contract_duration_unit = serializers.ChoiceField(choices=_choice("contract_duration_unit"), required=False)
    experience_level = serializers.ChoiceField(choices=_choice("experience_level"))
    budget_min = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0, required=False, allow_null=True)
    budget_max = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0, required=False, allow_null=True)
    currency = serializers.RegexField(r"^[A-Za-z]{3}$", required=False)
    budget_period = serializers.ChoiceField(choices=_choice("budget_period"), required=False)
    country = serializers.RegexField(r"^[A-Za-z]{2}$", error_messages={"invalid": "Code pays ISO à 2 lettres attendu."})
    city = serializers.CharField(max_length=100, required=False, allow_blank=True)
    work_mode = serializers.ChoiceField(choices=_choice("work_mode"), required=False)
    start_date = serializers.DateField(required=False, allow_null=True)
    deadline = serializers.DateField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=_choice("status"), required=False)
    required_skill_ids = serializers.ListField(child=serializers.IntegerField(), required=False, max_length=30)
    publish = serializers.BooleanField(required=False, default=False)

    def validate_country(self, value):
        return value.upper()

    def validate_currency(self, value):
        return value.upper()

    # Durée maximale raisonnable selon l'unité choisie
    MAX_DURATION = {"hour": 10000, "day": 3650, "month": 120, "year": 20}

    def validate(self, attrs):
        duration, unit = attrs.get("contract_duration"), attrs.get("contract_duration_unit")
        if duration and unit and duration > self.MAX_DURATION[unit]:
            raise serializers.ValidationError(
                {"contract_duration": f"La durée ne peut pas dépasser {self.MAX_DURATION[unit]} dans cette unité."}
            )
        low, high = attrs.get("budget_min"), attrs.get("budget_max")
        if low is not None and high is not None and low > high:
            raise serializers.ValidationError({"budget_max": "Le budget maximum doit dépasser le minimum."})
        start, deadline = attrs.get("start_date"), attrs.get("deadline")
        if start and deadline and deadline > start:
            raise serializers.ValidationError({"deadline": "La date limite doit précéder le début de la mission."})
        ids = attrs.get("required_skill_ids")
        if ids is not None:
            from app.marketplace.models import Skill

            attrs["required_skill_ids"] = list(dict.fromkeys(ids))
            missing = set(attrs["required_skill_ids"]) - set(Skill.objects.filter(id__in=ids).values_list("id", flat=True))
            if missing:
                raise serializers.ValidationError({"required_skill_ids": f"Compétence(s) inconnue(s) : {sorted(missing)}"})
        return attrs


class OfferGenerateSerializer(serializers.Serializer):
    """Besoin en langage naturel pour préremplir une offre (UC-09)."""

    brief = serializers.CharField(min_length=12, max_length=4000)


class ApplySerializer(serializers.Serializer):
    message = serializers.CharField(max_length=5000, allow_blank=True, required=False, default="")


class DecisionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["shortlisted", "rejected", "accepted"])


class ProfilSkillItemSerializer(serializers.Serializer):
    skill_id = serializers.IntegerField()
    level = serializers.IntegerField(min_value=1, max_value=5)
    years = serializers.IntegerField(min_value=0, max_value=60, required=False, default=0)


class ProfilSkillsSerializer(serializers.Serializer):
    skills = ProfilSkillItemSerializer(many=True, max_length=60)


class AvailabilityWriteSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    status = serializers.ChoiceField(choices=[value for value, _label in Availability._meta.get_field("status").choices])
    hours_per_week = serializers.IntegerField(min_value=0, max_value=80, required=False, allow_null=True)
    note = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, attrs):
        start, end = attrs.get("start_date"), attrs.get("end_date")
        if start and end and end < start:
            raise serializers.ValidationError({"end_date": "La fin doit suivre le début."})
        return attrs


class ExperienceWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=150)
    company_name = serializers.CharField(max_length=150)
    location = serializers.CharField(max_length=150, required=False, allow_blank=True)
    contract_type = serializers.ChoiceField(
        choices=[value for value, _label in Experience._meta.get_field("contract_type").choices], required=False, allow_blank=True
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)
    is_current = serializers.BooleanField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    technologies = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, attrs):
        start, end = attrs.get("start_date"), attrs.get("end_date")
        if start and end and end < start and not attrs.get("is_current"):
            raise serializers.ValidationError({"end_date": "La fin doit suivre le début."})
        return attrs


class PrestationWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=150)
    description = serializers.CharField()
    category = serializers.ChoiceField(
        choices=[value for value, _label in Prestation._meta.get_field("category").choices]
    )
    price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    currency = serializers.RegexField(regex=r"^[A-Za-z]{3}$", required=False)
    delivery_days = serializers.IntegerField(min_value=1, max_value=365)
    revisions = serializers.IntegerField(min_value=0, max_value=50, required=False)
    cover_image = serializers.CharField(max_length=512, required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)

    def validate_currency(self, value):
        return value.upper()


__all__ = [
    "AvailabilityWriteSerializer",
    "ExperienceWriteSerializer",
    "PrestationWriteSerializer",
    "OfferWriteSerializer",
    "OfferGenerateSerializer",
    "ApplySerializer",
    "DecisionSerializer",
    "ProfilSkillsSerializer",
]
