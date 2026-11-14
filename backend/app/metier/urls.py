"""Routes des futurs CRUD generes dans metier + lecture authentifiée des fichiers stockés."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.metier.views.file_views import StoredFileView

router = DefaultRouter(trailing_slash=False)

urlpatterns = [
    path("v1/files/<path:file_path>", StoredFileView.as_view(), name="stored-file"),
    path("v1/", include(router.urls)),
]
