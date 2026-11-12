from rest_framework import serializers
from app.projects.models import ContributionTask, Project, Technology


class ContributionTaskSerializer(serializers.ModelSerializer):
    """
    Serializer pour les contribution-tasks.
    """

    class Meta:
        model = ContributionTask
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = [
            "id",
            "title",
            "description",
            "status",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def get_fields(self):
        """
        Marque les champs système en lecture seule s'ils existent.
        """
        fields = super().get_fields()
        for sys_field in ["id", "created_by", "updated_by", "created_at", "updated_at"]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def to_representation(self, instance):
        """
        Personnalise la représentation des données.
        """
        data = super().to_representation(instance)

        data["created_at"] = (
            instance.created_at.isoformat() if hasattr(instance, "created_at") else None
        )
        data["updated_at"] = (
            instance.updated_at.isoformat() if hasattr(instance, "updated_at") else None
        )

        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer pour les projects.
    """

    class Meta:
        model = Project
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = [
            "id",
            "title",
            "slug",
            "problem",
            "description",
            "demo_url",
            "declared_license",
            "status",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def get_fields(self):
        """
        Marque les champs système en lecture seule s'ils existent.
        """
        fields = super().get_fields()
        for sys_field in ["id", "created_by", "updated_by", "created_at", "updated_at"]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def to_representation(self, instance):
        """
        Personnalise la représentation des données.
        """
        data = super().to_representation(instance)

        data["created_at"] = (
            instance.created_at.isoformat() if hasattr(instance, "created_at") else None
        )
        data["updated_at"] = (
            instance.updated_at.isoformat() if hasattr(instance, "updated_at") else None
        )

        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data


class TechnologySerializer(serializers.ModelSerializer):
    """
    Serializer pour les technologies.
    """

    class Meta:
        model = Technology
        # Champs listés explicitement : un champ ajouté plus tard au modèle n'est jamais exposé automatiquement
        fields = [
            "id",
            "label",
            "slug",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def get_fields(self):
        """
        Marque les champs système en lecture seule s'ils existent.
        """
        fields = super().get_fields()
        for sys_field in ["id", "created_by", "updated_by", "created_at", "updated_at"]:
            if sys_field in fields:
                fields[sys_field].read_only = True
        return fields

    def to_representation(self, instance):
        """
        Personnalise la représentation des données.
        """
        data = super().to_representation(instance)

        data["created_at"] = (
            instance.created_at.isoformat() if hasattr(instance, "created_at") else None
        )
        data["updated_at"] = (
            instance.updated_at.isoformat() if hasattr(instance, "updated_at") else None
        )

        return data

    def validate(self, data):
        """
        Validation personnalisée des données.
        """
        return data
