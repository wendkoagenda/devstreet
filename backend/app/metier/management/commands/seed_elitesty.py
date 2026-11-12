"""Fichier de seeds pour Elitesty."""
from django.core.management.base import BaseCommand
from app.core.models import Permission
from app.metier.models import Elitesty
from app.core.models import User, Role
from django.conf import settings
import uuid
from datetime import datetime, timedelta
import random
import string
from decimal import Decimal


class Command(BaseCommand):
    help = 'Créer des données de test pour Elitesty'

    def handle(self, *args, **options):
        """Créer des données de test pour Elitesty."""
        self.stdout.write(self.style.SUCCESS('Création des seeds pour Elitesty...'))
        
        # Créer les permissions pour le modèle Elitesty
        self.create_permissions()
        
        # Récupérer ou créer l'administrateur (identifiants : variables ADMIN_EMAIL / ADMIN_PASSWORD)
        try:
            user = User.objects.get(email=settings.ADMIN_EMAIL)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username='admin',
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.WARNING('Utilisateur admin créé'))
            
        # Assigner les permissions à l'utilisateur admin
        self.assign_permissions_to_admin_role()
        
        existing_count = Elitesty.objects.count()
        if existing_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    'La table elitesty contient deja '
                    + str(existing_count)
                    + ' enregistrement(s). Seeds de donnees ignores.'
                )
            )
            return
        
        # Fonction pour générer des valeurs uniques
        def generate_unique_string(base_name, index, length=10):
            """Génère une chaîne unique basée sur un nom de base et un index."""
            timestamp = str(int(datetime.now().timestamp()))
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
            return f"{base_name}_{index}_{timestamp}_{random_suffix}"
        
        def generate_unique_email(index):
            """Génère un email unique."""
            timestamp = str(int(datetime.now().timestamp()))
            return f"test_{index}_{timestamp}@example.com"
        
        def generate_unique_url(index):
            """Génère une URL unique."""
            timestamp = str(int(datetime.now().timestamp()))
            return f"https://example{index}-{timestamp}.com"
        
        def generate_unique_decimal(base_value, index):
            """Génère une valeur décimale unique."""
            return Decimal(str(base_value + (index * 10) + random.uniform(0.01, 9.99)))
        
        # Créer des données de test avec des valeurs uniques
        elitesty_data = []
        
        for i in range(1, 4):  # Créer 3 enregistrements de test
            data = {                'uuid': str(uuid.uuid4()),                'titre': generate_unique_string('titre', i, 8),                'statut': ['draft', 'published', 'archived'][(i - 1) % 3],                'description': f'Contenu de test unique pour description #{i} - {generate_unique_string("content", i, 12)}',                'prix': generate_unique_decimal(99.99, i),                'document': None,                'created_by': user.id,
                'updated_by': user.id,
            }
            elitesty_data.append(data)
        
        created_elitesties = []
        for data in elitesty_data:
            elitesty = Elitesty.objects.create(**data)
            created_elitesties.append(elitesty)
            # Afficher le premier champ disponible ou l'UUID            self.stdout.write('Elitesty créé: ' + str(elitesty.id))        
        self.stdout.write(
            self.style.SUCCESS(
                str(len(created_elitesties)) + ' elitesties créé(s) avec succès!'
            )
        )
        
        # Afficher un résumé
        total_count = Elitesty.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                'Total de elitesty(s) dans la base: ' + str(total_count)
            )
        )
        
        # Afficher les URLs disponibles pour tester
        self.stdout.write('\nURLs disponibles pour tester:')
        self.stdout.write('   GET    /api/v1/elitesties           - Liste tous les elitesties')
        self.stdout.write('   POST   /api/v1/elitesties           - Créer un nouveau elitesty')
        self.stdout.write('   GET    /api/v1/elitesties/{id}      - Récupérer un elitesty spécifique')
        self.stdout.write('   PUT    /api/v1/elitesties/{id}      - Mettre à jour un elitesty')
        self.stdout.write('   DELETE /api/v1/elitesties/{id}      - Supprimer un elitesty')
        
        self.stdout.write('\nPour tester avec curl:')
        self.stdout.write('   curl -X GET http://localhost:8000/api/v1/elitesties')
        
        self.stdout.write('\nSeeds créés avec succès! Vous pouvez maintenant tester votre API.')
    
    def create_permissions(self):
        """Créer les permissions personnalisées pour le modèle Elitesty."""
        
        permissions = [
            ('elitesties.view', 'Can view elitesties'),
            ('elitesties.create', 'Can create elitesties'),
            ('elitesties.update', 'Can update elitesties'),
            ('elitesties.delete', 'Can delete elitesties'),
        ]
        
        for code, description in permissions:
            permission, created = Permission.objects.get_or_create(
                code=code,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(f'Permission créée: {description}')
    
    
    
    def assign_permissions_to_admin_role(self):
        """Assigner toutes les permissions Elitesty aux rôles Admin et SuperAdmin."""
        # Récupérer les permissions pour ce modèle
        permissions = Permission.objects.filter(code__startswith='elitesties.')
        
        # Assigner aux rôles Admin et Super Admin
        roles_to_assign = ['Admin', 'Super Admin']
        
        for role_name in roles_to_assign:
            try:
                role = Role.objects.get(name=role_name)
                
                for permission in permissions:
                    if permission not in role.permissions.all():
                        role.permissions.add(permission)
                        self.stdout.write(f'Permission assignée au rôle {role_name}: {permission.code}')
                
                self.stdout.write(f'Toutes les permissions Elitesty assignées au rôle {role_name}')
                
            except Role.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Rôle {role_name} non trouvé'))
                continue