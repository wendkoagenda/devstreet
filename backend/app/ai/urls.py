from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.ai.views.chat_viewsets import AiConversationViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"ai/conversations", AiConversationViewSet, basename="ai-conversations")

urlpatterns = [
    path("v1/", include(router.urls)),
]

app_name = "ai"
