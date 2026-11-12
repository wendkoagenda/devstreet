from rest_framework import serializers

from app.devstreet_hub.models import GitConnectedComputer


class GitDeviceStartSerializer(serializers.Serializer):
    computer_name = serializers.CharField(max_length=120)
    hub_base_url = serializers.URLField(max_length=400)
    code_challenge = serializers.CharField(min_length=43, max_length=128)


class GitDevicePollSerializer(serializers.Serializer):
    code_verifier = serializers.CharField(min_length=43, max_length=128)


class GitDeviceRequestSerializer(serializers.Serializer):
    id = serializers.CharField()
    computer_name = serializers.CharField()
    hub_base_url = serializers.CharField()
    status = serializers.CharField()
    expires_at = serializers.CharField()
    created_at = serializers.CharField()
    decided_at = serializers.CharField(allow_null=True)
    scopes = serializers.ListField(child=serializers.CharField())
    scope_labels = serializers.ListField(child=serializers.CharField())
    gitea_host = serializers.CharField()


class GitConnectedComputerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GitConnectedComputer
        fields = (
            "id",
            "name",
            "forge_login",
            "token_last_eight",
            "status",
            "created_at",
            "revoked_at",
            "last_used_at",
        )
