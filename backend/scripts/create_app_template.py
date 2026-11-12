#!/usr/bin/env python
"""
Template pour créer une nouvelle application Django.
"""
import os
import sys
from pathlib import Path

def create_app_template(app_name, verbose_name=None):
    """
    Crée une nouvelle application Django avec la structure complète.
    
    Args:
        app_name (str): Nom de l'application (ex: 'products')
        verbose_name (str): Nom d'affichage (ex: 'Products')
    """
    if verbose_name is None:
        verbose_name = app_name.title()
    
    # Structure de l'application
    app_structure = {
        '__init__.py': f'"""Application {app_name} - {verbose_name}."""',
        
        'apps.py': f'''"""
Configuration de l'application {app_name}.
"""
from django.apps import AppConfig


class {app_name.title()}Config(AppConfig):
    """
    Configuration de l'application {app_name}.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.{app_name}'
    verbose_name = '{verbose_name}'
    
    def ready(self):
        """
        Méthode appelée quand l'application est prête.
        """
        pass
''',
        
        'urls.py': f'''"""
Configuration des URLs pour l'application {app_name}.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.{app_name}.views.{app_name}_viewset import {app_name.title()}ViewSet

# Configuration du routeur pour les ViewSets
router = DefaultRouter(trailing_slash=False)
router.register(r'{app_name}', {app_name.title()}ViewSet, basename='{app_name}')

# URLs de l'application
urlpatterns = [
    # === API CRUD ===
    # Inclure toutes les routes des ViewSets
    path('v1/', include(router.urls)),
]

# URLs nommées pour faciliter les références
app_name = '{app_name}'
''',
        
        'models.py': f'''"""
Modèles de données pour l'application {app_name}.
"""
from django.db import models
from django.utils import timezone


class {app_name.title()}(models.Model):
    """
    Modèle {verbose_name}.
    """
    name = models.CharField(max_length=255, verbose_name="Nom")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "{verbose_name}"
        verbose_name_plural = "{verbose_name}"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
''',
        
        'serializers.py': f'''"""
Sérialiseurs pour l'application {app_name}.
"""
from rest_framework import serializers
from app.{app_name}.models import {app_name.title()}


class {app_name.title()}Serializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le modèle {app_name.title()}.
    """
    
    class Meta:
        model = {app_name.title()}
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
''',
        
        'views/__init__.py': '',
        'views/{app_name}_viewset.py': f'''"""
ViewSet pour la gestion des {app_name}.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from app.{app_name}.models import {app_name.title()}
from app.{app_name}.serializers import {app_name.title()}Serializer
from app.{app_name}.services.{app_name}_service import {app_name.title()}Service
from app.{app_name}.permissions.{app_name}_permissions import (
    CanView{app_name.title()},
    CanCreate{app_name.title()},
    CanUpdate{app_name.title()},
    CanDelete{app_name.title()}
)


class {app_name.title()}ViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les opérations CRUD sur les {app_name}.
    """
    swagger_tags = ['V1 - {app_name.title()}']
    queryset = {app_name.title()}.objects.all()
    serializer_class = {app_name.title()}Serializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.{app_name}_service = {app_name.title()}Service()

    def get_permissions(self):
        """
        Retourne les permissions requises selon l'action.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [CanView{app_name.title()}]
        elif self.action == 'create':
            permission_classes = [CanCreate{app_name.title()}]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanUpdate{app_name.title()}]
        elif self.action == 'destroy':
            permission_classes = [CanDelete{app_name.title()}]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Lister tous les {app_name}",
        responses={{200: {app_name.title()}Serializer(many=True)}},
        security=[{{'Bearer': []}}],
        tags=['V1 - {app_name.title()}']
    )
    def list(self, request):
        """
        Retourne la liste de tous les {app_name}.
        """
        {app_name} = self.{app_name}_service.get_all()
        serializer = self.get_serializer({app_name}, many=True)
        return Response(serializer.data)
''',
        
        'services/__init__.py': '',
        'services/{app_name}_service.py': f'''"""
Service pour la gestion des {app_name}.
"""
from app.{app_name}.models import {app_name.title()}
from app.{app_name}.repositories.{app_name}_repository import {app_name.title()}Repository


class {app_name.title()}Service:
    """
    Service pour les opérations métier sur les {app_name}.
    """
    
    def __init__(self):
        self.{app_name}_repository = {app_name.title()}Repository()
    
    def get_all(self):
        """
        Récupère tous les {app_name}.
        """
        return self.{app_name}_repository.get_all()
    
    def get_by_id(self, {app_name}_id):
        """
        Récupère un {app_name} par son ID.
        """
        return self.{app_name}_repository.get_by_id({app_name}_id)
    
    def create(self, data):
        """
        Crée un nouveau {app_name}.
        """
        return self.{app_name}_repository.create(data)
    
    def update(self, {app_name}_id, data, partial=False):
        """
        Met à jour un {app_name}.
        """
        return self.{app_name}_repository.update({app_name}_id, data, partial)
    
    def delete(self, {app_name}_id):
        """
        Supprime un {app_name}.
        """
        return self.{app_name}_repository.delete({app_name}_id)
''',
        
        'repositories/__init__.py': '',
        'repositories/{app_name}_repository.py': f'''"""
Repository pour l'accès aux données des {app_name}.
"""
from app.{app_name}.models import {app_name.title()}
from app.{app_name}.interfaces.{app_name}_repository_interface import {app_name.title()}RepositoryInterface


class {app_name.title()}Repository({app_name.title()}RepositoryInterface):
    """
    Repository pour les opérations de base de données sur les {app_name}.
    """
    
    def get_all(self):
        """
        Récupère tous les {app_name}.
        """
        return {app_name.title()}.objects.all()
    
    def get_by_id(self, {app_name}_id):
        """
        Récupère un {app_name} par son ID.
        """
        return {app_name.title()}.objects.get(id={app_name}_id)
    
    def create(self, data):
        """
        Crée un nouveau {app_name}.
        """
        return {app_name.title()}.objects.create(**data)
    
    def update(self, {app_name}_id, data, partial=False):
        """
        Met à jour un {app_name}.
        """
        {app_name} = self.get_by_id({app_name}_id)
        for field, value in data.items():
            setattr({app_name}, field, value)
        {app_name}.save()
        return {app_name}
    
    def delete(self, {app_name}_id):
        """
        Supprime un {app_name}.
        """
        {app_name} = self.get_by_id({app_name}_id)
        {app_name}.delete()
        return True
''',
        
        'interfaces/__init__.py': '',
        'interfaces/{app_name}_repository_interface.py': f'''"""
Interface pour le repository des {app_name}.
"""
from abc import ABC, abstractmethod


class {app_name.title()}RepositoryInterface(ABC):
    """
    Interface pour les opérations de base de données sur les {app_name}.
    """
    
    @abstractmethod
    def get_all(self):
        """
        Récupère tous les {app_name}.
        """
        pass
    
    @abstractmethod
    def get_by_id(self, {app_name}_id):
        """
        Récupère un {app_name} par son ID.
        """
        pass
    
    @abstractmethod
    def create(self, data):
        """
        Crée un nouveau {app_name}.
        """
        pass
    
    @abstractmethod
    def update(self, {app_name}_id, data, partial=False):
        """
        Met à jour un {app_name}.
        """
        pass
    
    @abstractmethod
    def delete(self, {app_name}_id):
        """
        Supprime un {app_name}.
        """
        pass
''',
        
        'permissions/__init__.py': '',
        'permissions/{app_name}_permissions.py': f'''"""
Permissions pour l'application {app_name}.
"""
from rest_framework import permissions


class CanView{app_name.title()}(permissions.BasePermission):
    """
    Permission pour voir les {app_name}.
    """
    
    def has_permission(self, request, view):
        return request.user.has_perm('{app_name}.view_{app_name}')


class CanCreate{app_name.title()}(permissions.BasePermission):
    """
    Permission pour créer des {app_name}.
    """
    
    def has_permission(self, request, view):
        return request.user.has_perm('{app_name}.add_{app_name}')


class CanUpdate{app_name.title()}(permissions.BasePermission):
    """
    Permission pour modifier des {app_name}.
    """
    
    def has_permission(self, request, view):
        return request.user.has_perm('{app_name}.change_{app_name}')


class CanDelete{app_name.title()}(permissions.BasePermission):
    """
    Permission pour supprimer des {app_name}.
    """
    
    def has_permission(self, request, view):
        return request.user.has_perm('{app_name}.delete_{app_name}')
''',
        
        'tests.py': f'''"""
Tests pour l'application {app_name}.
"""
from django.test import TestCase
from app.{app_name}.models import {app_name.title()}


class {app_name.title()}ModelTest(TestCase):
    """
    Tests pour le modèle {app_name.title()}.
    """
    
    def test_create_{app_name}(self):
        """
        Test de création d'un {app_name}.
        """
        {app_name} = {app_name.title()}.objects.create(
            name="Test {app_name.title()}",
            description="Description de test"
        )
        self.assertEqual({app_name}.name, "Test {app_name.title()}")
        self.assertEqual({app_name}.description, "Description de test")
''',
    }
    
    # Créer le dossier de l'application
    app_dir = Path(f'app/{app_name}')
    app_dir.mkdir(parents=True, exist_ok=True)
    
    # Créer tous les fichiers
    for file_path, content in app_structure.items():
        full_path = app_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✅ Application '{app_name}' créée avec succès !")
    print(f"📁 Dossier : {app_dir}")
    print("\n📝 Prochaines étapes :")
    print(f"1. Ajouter 'app.{app_name}' dans INSTALLED_APPS (config/settings.py)")
    print(f"2. Ajouter path('api/', include('app.{app_name}.urls')) dans config/urls.py")
    print(f"3. Créer et appliquer les migrations : python manage.py makemigrations {app_name}")
    print(f"4. Tester l'application : python manage.py test app.{app_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_app_template.py <app_name> [verbose_name]")
        sys.exit(1)
    
    app_name = sys.argv[1]
    verbose_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    create_app_template(app_name, verbose_name) 