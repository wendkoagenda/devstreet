"""Validation des corps de requête des écrans utilisateur (offres, candidatures, compétences)."""
from rest_framework import serializers

from app.marketplace.models import Offer

_choice = lambda field: [value for value, _label in Offer._meta.get_field(field).choices]  # noqa: E731


class OfferWriteSerializer(serializers.Serializer):
    """Offre saisie par un recruteur : l'entreprise, le recruteur, le slug et le statut initial sont gérés côté serveur."""

    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    type = serializers.ChoiceField(choices=_choice("type"))
    contract_duration = serializers.IntegerField(min_value=1, max_value=120, required=False, allow_null=True)
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

    def validate(self, attrs):
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


__all__ = [
    "OfferWriteSerializer",
    "ApplySerializer",
    "DecisionSerializer",
    "ProfilSkillsSerializer",
]
