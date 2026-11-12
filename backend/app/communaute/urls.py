from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.communaute.views.avischoix_viewset import AvisChoixViewSet
from app.communaute.views.commentaire_viewset import CommentaireViewSet
from app.communaute.views.confirmationaide_viewset import ConfirmationAideViewSet
from app.communaute.views.conversation_viewset import ConversationViewSet
from app.communaute.views.espace_viewset import EspaceViewSet
from app.communaute.views.imagepublication_viewset import ImagePublicationViewSet
from app.communaute.views.lieninvitation_viewset import LienInvitationViewSet
from app.communaute.views.likecommentaire_viewset import LikeCommentaireViewSet
from app.communaute.views.likepublication_viewset import LikePublicationViewSet
from app.communaute.views.message_viewset import MessageViewSet
from app.communaute.views.notificationresume_viewset import NotificationResumeViewSet
from app.communaute.views.optionpublication_viewset import OptionPublicationViewSet
from app.communaute.views.participationespace_viewset import ParticipationEspaceViewSet
from app.communaute.views.publication_viewset import PublicationViewSet
from app.communaute.views.suiviutilisateur_viewset import SuiviUtilisateurViewSet
from app.communaute.views.votesondage_viewset import VoteSondageViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'avis-choix', AvisChoixViewSet, basename='avis-choix')
router.register(r'commentaires', CommentaireViewSet, basename='commentaires')
router.register(r'confirmations-aide', ConfirmationAideViewSet, basename='confirmations-aide')
router.register(r'conversations', ConversationViewSet, basename='conversations')
router.register(r'espaces', EspaceViewSet, basename='espaces')
router.register(r'images-publication', ImagePublicationViewSet, basename='images-publication')
router.register(r'liens-invitation', LienInvitationViewSet, basename='liens-invitation')
router.register(r'likes-commentaire', LikeCommentaireViewSet, basename='likes-commentaire')
router.register(r'likes-publication', LikePublicationViewSet, basename='likes-publication')
router.register(r'messages', MessageViewSet, basename='messages')
router.register(r'notifications-resume', NotificationResumeViewSet, basename='notifications-resume')
router.register(r'options-publication', OptionPublicationViewSet, basename='options-publication')
router.register(r'participations-espace', ParticipationEspaceViewSet, basename='participations-espace')
router.register(r'publications', PublicationViewSet, basename='publications')
router.register(r'suivis-utilisateur', SuiviUtilisateurViewSet, basename='suivis-utilisateur')
router.register(r'votes-sondage', VoteSondageViewSet, basename='votes-sondage')

urlpatterns = [
    path('v1/', include(router.urls)),
]

app_name = 'communaute'
