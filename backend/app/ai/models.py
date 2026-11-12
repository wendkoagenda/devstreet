from django.conf import settings
from django.db import models


class AiConversation(models.Model):
    CONSUMER_HUB = "hub"
    CONSUMER_GENERIC = "generic"
    CONSUMER_CHOICES = (
        (CONSUMER_HUB, "DevStreet Hub"),
        (CONSUMER_GENERIC, "Générique"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_conversations",
    )
    consumer = models.CharField(max_length=32, choices=CONSUMER_CHOICES, default=CONSUMER_GENERIC)
    title = models.CharField(max_length=180, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at", "-id")

    def __str__(self):
        return f"AiConversation#{self.pk} ({self.consumer})"


class AiMessage(models.Model):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_SYSTEM = "system"
    ROLE_CHOICES = (
        (ROLE_USER, "Utilisateur"),
        (ROLE_ASSISTANT, "Assistant"),
        (ROLE_SYSTEM, "Système"),
    )

    conversation = models.ForeignKey(
        AiConversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    provider = models.CharField(max_length=32, blank=True, default="")
    failover_reason = models.CharField(max_length=120, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"AiMessage#{self.pk} ({self.role})"
