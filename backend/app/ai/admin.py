from django.contrib import admin

from app.ai.models import AiConversation, AiMessage


class AiMessageInline(admin.TabularInline):
    model = AiMessage
    extra = 0
    readonly_fields = ("role", "content", "provider", "failover_reason", "created_at")


@admin.register(AiConversation)
class AiConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "consumer", "title", "updated_at")
    list_filter = ("consumer",)
    search_fields = ("title", "user__email")
    inlines = [AiMessageInline]


@admin.register(AiMessage)
class AiMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "provider", "created_at")
    list_filter = ("role", "provider")
