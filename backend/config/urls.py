"""
URL configuration for the devstreet project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema
schema_view = get_schema_view(
    openapi.Info(
        title="OnePourcent devstreet API",
        default_version='v1',
        description="A comprehensive API for OnePourcent",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/', include('app.core.urls')),
        path('api/', include('app.metier.urls')),
        path('api/', include('app.devstreet_hub.urls')),
    ],
)

urlpatterns = [
    # API Core (inclut JWT auth et CRUD)
    path('api/', include('app.core.urls')),
    
    # API Metier (application pour les modèles métier)
    path('api/', include('app.metier.urls')),
    path('api/', include('app.devstreet_hub.urls')),
    
]

# Administration Django : exposée seulement si ENABLE_ADMIN est actif
if settings.ENABLE_ADMIN:
    urlpatterns += [path('admin/', admin.site.urls)]

# Documentation de l'API : exposée seulement si ENABLE_API_DOCS est actif (par défaut : DEBUG)
if settings.ENABLE_API_DOCS:
    urlpatterns += [
        path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
