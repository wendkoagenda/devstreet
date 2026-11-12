from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.marketplace.views.company_viewset import CompanyViewSet
from app.marketplace.views.skill_viewset import SkillViewSet
from app.marketplace.views.profil_viewset import ProfilViewSet
from app.marketplace.views.offer_viewset import OfferViewSet
from app.marketplace.views.candidature_viewset import CandidatureViewSet
from app.marketplace.views.profilskill_viewset import ProfilSkillViewSet
from app.marketplace.views.experience_viewset import ExperienceViewSet
from app.marketplace.views.prestation_viewset import PrestationViewSet
from app.marketplace.views.profilhistory_viewset import ProfilHistoryViewSet
from app.marketplace.views.availability_viewset import AvailabilityViewSet
from app.marketplace.views.review_viewset import ReviewViewSet
from app.marketplace.views.swipe_viewset import SwipeViewSet
from app.marketplace.views.connection_viewset import ConnectionViewSet
from app.marketplace.views import market_views, network_views
from app.marketplace.views.me_views import MeCompanyView, MeProfilView, MeView

router = DefaultRouter(trailing_slash=False)
router.register(r'companies', CompanyViewSet, basename='companies')
router.register(r'skills', SkillViewSet, basename='skills')
router.register(r'profils', ProfilViewSet, basename='profils')
router.register(r'offers', OfferViewSet, basename='offers')
router.register(r'candidatures', CandidatureViewSet, basename='candidatures')
router.register(r'profil-skills', ProfilSkillViewSet, basename='profil-skills')
router.register(r'experiences', ExperienceViewSet, basename='experiences')
router.register(r'prestations', PrestationViewSet, basename='prestations')
router.register(r'profil-histories', ProfilHistoryViewSet, basename='profil-histories')
router.register(r'availabilities', AvailabilityViewSet, basename='availabilities')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'swipes', SwipeViewSet, basename='swipes')
router.register(r'connections', ConnectionViewSet, basename='connections')

urlpatterns = [
    path('v1/marketplace/me', MeView.as_view(), name='marketplace-me'),
    path('v1/marketplace/me/profil', MeProfilView.as_view(), name='marketplace-me-profil'),
    path('v1/marketplace/me/company', MeCompanyView.as_view(), name='marketplace-me-company'),
    path('v1/marketplace/skills', market_views.skills_list, name='marketplace-skills'),
    path('v1/marketplace/me/skills', market_views.my_skills, name='marketplace-me-skills'),
    path('v1/marketplace/offers', market_views.offers_list, name='marketplace-offers'),
    path('v1/marketplace/offers/<int:offer_id>', market_views.offer_detail, name='marketplace-offer'),
    path('v1/marketplace/offers/<int:offer_id>/apply', market_views.offer_apply, name='marketplace-offer-apply'),
    path('v1/marketplace/me/candidatures', market_views.my_candidatures, name='marketplace-me-candidatures'),
    path('v1/marketplace/me/offers', market_views.my_offers, name='marketplace-me-offers'),
    path('v1/marketplace/me/offers/<int:offer_id>', market_views.my_offer_detail, name='marketplace-me-offer'),
    path('v1/marketplace/me/offers/<int:offer_id>/candidatures', market_views.offer_candidatures, name='marketplace-me-offer-candidatures'),
    path('v1/marketplace/me/offers/<int:offer_id>/recommended-profils', market_views.offer_recommended_profils, name='marketplace-me-offer-profils'),
    path('v1/marketplace/candidatures/<int:candidature_id>/decision', market_views.candidature_decision, name='marketplace-candidature-decision'),
    path('v1/marketplace/me/deck', network_views.deck, name='marketplace-me-deck'),
    path('v1/marketplace/me/swipes', network_views.swipe, name='marketplace-me-swipes'),
    path('v1/marketplace/me/swipes/last', network_views.undo_swipe, name='marketplace-me-swipes-last'),
    path('v1/marketplace/me/pool', network_views.pool, name='marketplace-me-pool'),
    path('v1/marketplace/me/connections', network_views.connections, name='marketplace-me-connections'),
    path('v1/marketplace/profils/<int:profil_id>', network_views.public_profile, name='marketplace-profil'),
    path('v1/', include(router.urls)),
]

app_name = 'marketplace'
