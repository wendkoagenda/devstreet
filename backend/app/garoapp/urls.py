from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.garoapp.views.gado_viewset import GadoViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'gados', GadoViewSet, basename='gados')

urlpatterns = [
    path('v1/', include(router.urls)),
]

app_name = 'garoapp'
