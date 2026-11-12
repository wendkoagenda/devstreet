"""Fichier de seeds pour Dragon."""
from django.core.management.base import BaseCommand
from app.core.models import Permission
from app.metier.models import Dragon
from app.core.models import User, Role
from django.conf import settings
import uuid
from datetime import datetime, timedelta
import random
import string
from decimal import Decimal


class Command(BaseCommand):
    help = 'Créer des données de test pour Dragon'

    def handle(self, *args, **options):
        """Créer des données de test pour Dragon."""
        self.stdout.write(self.style.SUCCESS('Création des seeds pour Dragon...'))
        
        # Créer les permissions pour le modèle Dragon
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
        
        existing_count = Dragon.objects.count()
        if existing_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    'La table dragon contient deja '
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
        dragon_data = []
        
        for i in range(1, 4):  # Créer 3 enregistrements de test
            data = {                'uuid': str(uuid.uuid4()),                'titre': generate_unique_string('titre', i, 8),                'statut': ['draft', 'published', 'archived'][(i - 1) % 3],                'description': f'Contenu de test unique pour description #{i} - {generate_unique_string("content", i, 12)}',                'prix': generate_unique_decimal(99.99, i),                'document': None,                'created_by': user.id,
                'updated_by': user.id,
            }
            dragon_data.append(data)
        
        created_dragons = []
        for data in dragon_data:
            dragon = Dragon.objects.create(**data)
            created_dragons.append(dragon)
            # Afficher le premier champ disponible ou l'UUID            self.stdout.write('Dragon créé: ' + str(dragon.id))        
        self.stdout.write(
            self.style.SUCCESS(
                str(len(created_dragons)) + ' dragons créé(s) avec succès!'
            )
        )
        
        # Afficher un résumé
        total_count = Dragon.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                'Total de dragon(s) dans la base: ' + str(total_count)
            )
        )
        
        # Afficher les URLs disponibles pour tester
        self.stdout.write('\nURLs disponibles pour tester:')
        self.stdout.write('   GET    /api/v1/dragons           - Liste tous les dragons')
        self.stdout.write('   POST   /api/v1/dragons           - Créer un nouveau dragon')
        self.stdout.write('   GET    /api/v1/dragons/{id}      - Récupérer un dragon spécifique')
        self.stdout.write('   PUT    /api/v1/dragons/{id}      - Mettre à jour un dragon')
        self.stdout.write('   DELETE /api/v1/dragons/{id}      - Supprimer un dragon')
        
        self.stdout.write('\nPour tester avec curl:')
        self.stdout.write('   curl -X GET http://localhost:8000/api/v1/dragons')
        
        self.stdout.write('\nSeeds créés avec succès! Vous pouvez maintenant tester votre API.')
    
    def create_permissions(self):
        """Créer les permissions personnalisées pour le modèle Dragon."""
        
        permissions = [
            ('dragons.view', 'Can view dragons'),
            ('dragons.create', 'Can create dragons'),
            ('dragons.update', 'Can update dragons'),
            ('dragons.delete', 'Can delete dragons'),
        ]
        
        for code, description in permissions:
            permission, created = Permission.objects.get_or_create(
                code=code,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(f'Permission créée: {description}')
    
    
    
    def assign_permissions_to_admin_role(self):
        """Assigner toutes les permissions Dragon aux rôles Admin et SuperAdmin."""
        # Récupérer les permissions pour ce modèle
        permissions = Permission.objects.filter(code__startswith='dragons.')
        
        # Assigner aux rôles Admin et Super Admin
        roles_to_assign = ['Admin', 'Super Admin']
        
        for role_name in roles_to_assign:
            try:
                role = Role.objects.get(name=role_name)
                
                for permission in permissions:
                    if permission not in role.permissions.all():
                        role.permissions.add(permission)
                        self.stdout.write(f'Permission assignée au rôle {role_name}: {permission.code}')
                
                self.stdout.write(f'Toutes les permissions Dragon assignées au rôle {role_name}')
                
            except Role.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Rôle {role_name} non trouvé'))
                continue