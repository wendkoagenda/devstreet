from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.metier.views.elitest_viewset import ElitestViewSet
from app.metier.views.elitesty_viewset import ElitestyViewSet
from app.metier.views.dragon_viewset import DragonViewSet
from app.metier.views.fusion_viewset import FusionViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'elitests', ElitestViewSet, basename='elitests')
router.register(r'elitesties', ElitestyViewSet, basename='elitesties')
router.register(r'dragons', DragonViewSet, basename='dragons')
router.register(r'fusions', FusionViewSet, basename='fusions')

urlpatterns = [
    path('v1/', include(router.urls)),
]

app_name = 'metier'
