"""
SuiviUtilisateur service layer pour les opérations de logique métier.
"""
from typing import List, Optional, Dict, Any, Set
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Q, QuerySet
from django.core.exceptions import ValidationError
from app.communaute.models import SuiviUtilisateur
from app.communaute.repositories.suiviutilisateur_repository import SuiviUtilisateurRepository

User = get_user_model()


class SuiviUtilisateurService:
    """
    Classe de service pour la logique métier liée aux suivi_utilisateurs.
    """

    def __init__(self):
        self.suiviutilisateur_repository = SuiviUtilisateurRepository()

    def ids_suivis_par(self, suiveur: User) -> Set[int]:
        """IDs des membres suivis par cet utilisateur."""
        if suiveur is None or not getattr(suiveur, 'id', None):
            return set()
        return set(
            SuiviUtilisateur.objects.filter(suiveur_id=suiveur.id).values_list(
                'suivi_id', flat=True
            )
        )

    def list_membres_suivis(
        self,
        suiveur: User,
        *,
        search: Optional[str] = None,
        limit: int = 50,
    ) -> List[User]:
        """Membres actifs suivis par l'utilisateur (pour Messages / DM)."""
        if suiveur is None or not getattr(suiveur, 'id', None):
            return []
        qs = User.objects.filter(
            is_active=True,
            id__in=SuiviUtilisateur.objects.filter(
                suiveur_id=suiveur.id
            ).values('suivi_id'),
        ).order_by('username')
        cleaned = (search or '').strip()
        if cleaned:
            qs = qs.filter(
                Q(username__icontains=cleaned)
                | Q(first_name__icontains=cleaned)
                | Q(last_name__icontains=cleaned)
            )
        safe_limit = max(1, min(int(limit or 50), 100))
        return list(qs[:safe_limit])

    def est_suivi(self, *, suiveur: User, suivi_id: int) -> bool:
        return SuiviUtilisateur.objects.filter(
            suiveur_id=suiveur.id, suivi_id=suivi_id
        ).exists()

    def toggle_suivi(self, *, suiveur: User, suivi_id: int) -> Dict[str, Any]:
        """Ajoute ou retire un suivi. Retourne {following, suivi_id}."""
        if suivi_id == suiveur.id:
            raise ValidationError('Tu ne peux pas te suivre toi-même.')
        cible = User.objects.filter(pk=suivi_id, is_active=True).first()
        if cible is None:
            raise ValidationError('Profil introuvable.')

        existing = SuiviUtilisateur.objects.filter(
            suiveur=suiveur, suivi=cible
        ).first()
        if existing is not None:
            existing.delete()
            return {'following': False, 'suivi_id': cible.id}

        try:
            with transaction.atomic():
                SuiviUtilisateur.objects.create(
                    suiveur=suiveur,
                    suivi=cible,
                    created_by=suiveur.id,
                    updated_by=suiveur.id,
                )
        except IntegrityError:
            # Course double-clic : considéré comme déjà suivi.
            pass
        return {'following': True, 'suivi_id': cible.id}

    def get_all(self, search: Optional[str] = None, ordering: Optional[str] = None) -> QuerySet:
        """
        Obtenir les suivi_utilisateurs, avec recherche textuelle et tri facultatifs.

        Returns:
            QuerySet: Les suivi_utilisateurs filtrés et triés

        Raises:
            ValueError: Si le champ de tri n'est pas autorisé
        """
        return self.suiviutilisateur_repository.get_all(search=search, ordering=ordering)

    def get_by_id(self, suivi_utilisateur_id: int) -> Optional[SuiviUtilisateur]:
        """
        Obtenir un suivi_utilisateur par ID.
        
        Args:
            suivi_utilisateur_id (int): L'ID du suivi_utilisateur
            
        Returns:
            Optional[SuiviUtilisateur]: Le suivi_utilisateur si trouvé, None sinon
        """
        return self.suiviutilisateur_repository.get_by_id(suivi_utilisateur_id)

    def create(self, suivi_utilisateur_data: Dict[str, Any]) -> SuiviUtilisateur:
        """
        Créer un nouveau suivi_utilisateur avec validation.
        
        Args:
            suivi_utilisateur_data (Dict[str, Any]): Données du suivi_utilisateur
            
        Returns:
            SuiviUtilisateur: Le suivi_utilisateur créé
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des données
        self.validate_data(suivi_utilisateur_data)
        
        return self.suiviutilisateur_repository.create(**suivi_utilisateur_data)

    def update(self, suivi_utilisateur_id: int, suivi_utilisateur_data: Dict[str, Any], partial: bool = False) -> Optional[SuiviUtilisateur]:
        """
        Mettre à jour un suivi_utilisateur existant.
        
        Args:
            suivi_utilisateur_id (int): L'ID du suivi_utilisateur
            suivi_utilisateur_data (Dict[str, Any]): Données mises à jour
            partial (bool): Si c'est une mise à jour partielle
            
        Returns:
            Optional[SuiviUtilisateur]: Le suivi_utilisateur mis à jour si trouvé, None sinon
            
        Raises:
            ValidationError: Si la validation échoue
        """
        suivi_utilisateur = self.suiviutilisateur_repository.get_by_id(suivi_utilisateur_id)
        if not suivi_utilisateur:
            return None

        # Validation des données
        if not partial:
            self.validate_data(suivi_utilisateur_data)

        return self.suiviutilisateur_repository.update(suivi_utilisateur, **suivi_utilisateur_data)

    def delete(self, suivi_utilisateur_id: int) -> bool:
        """
        Supprimer un suivi_utilisateur.
        
        Args:
            suivi_utilisateur_id (int): L'ID du suivi_utilisateur
            
        Returns:
            bool: True si supprimé avec succès, False si suivi_utilisateur non trouvé
        """
        suivi_utilisateur = self.suiviutilisateur_repository.get_by_id(suivi_utilisateur_id)
        if not suivi_utilisateur:
            return False

        return self.suiviutilisateur_repository.delete(suivi_utilisateur)

    def validate_data(self, suivi_utilisateur_data: Dict[str, Any]):
        """
        Valider les données du suivi_utilisateur.
        
        Args:
            suivi_utilisateur_data (Dict[str, Any]): Données du suivi_utilisateur à valider
            
        Raises:
            ValidationError: Si la validation échoue
        """
        # Validation des champs CharField obligatoires
        # Ajoutez d'autres validations selon vos besoins