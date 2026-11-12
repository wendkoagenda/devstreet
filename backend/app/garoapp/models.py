from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Gado(models.Model):
    """
    Gado model.
    """
    
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    titre = models.CharField(max_length=200, blank=False, null=False)
    statut = models.CharField(max_length=20, blank=False, null=False, choices=[('draft', 'Brouillon'), ('published', 'Publie'), ('archived', 'Archive')])
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(blank=False, null=False, max_digits=10, decimal_places=2)
    document = models.CharField(max_length=512, blank=True, null=True)
    created_by = models.IntegerField(
        verbose_name="Créé par",
        help_text="ID de l'utilisateur créateur"
    )
    updated_by = models.IntegerField(
        verbose_name="Modifié par",
        help_text="ID de l'utilisateur ayant modifié"
    )
    created_at = models.DateTimeField(
        verbose_name="Date de création",
        auto_now_add=True,
        auto_now=False
    )
    updated_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=False,
        auto_now=True
    )

    class Meta:
        db_table = 'garoapp_gado'
        verbose_name = 'Gado'
        verbose_name_plural = 'Gados'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titre}"

    def get_absolute_url(self):
        return f"/garoapp/gados/{self.id}/" 
