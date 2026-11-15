"""
Commande Django pour initialiser les données de base du système.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from app.core.models import Permission, Role
from django.conf import settings
from app.core.services.permission_service import PermissionService
from app.core.services.role_service import RoleService
from app.core.services.user_service import UserService
from django.core.management import call_command
import os
from pathlib import Path

User = get_user_model()


class Command(BaseCommand):
    """
    Commande pour initialiser les permissions, rôles et utilisateur admin par défaut.
    
    Usage: python manage.py init_data
    """
    help = 'Initialise les données de base du système (permissions, rôles, admin)'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permission_service = PermissionService()
        self.role_service = RoleService()
        self.user_service = UserService()

    def add_arguments(self, parser):
        """
        Ajoute des arguments à la commande.
        """
        parser.add_argument(
            '--skip-admin',
            action='store_true',
            help='Ne pas créer l\'utilisateur admin par défaut',
        )
        parser.add_argument(
            '--only-admin',
            action='store_true',
            help="Ne créer que l'utilisateur admin par défaut (les rôles doivent déjà exister)",
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default=None,
            help='Email de l\'utilisateur admin (défaut: variable ADMIN_EMAIL)',
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default=None,
            help='Mot de passe de l\'utilisateur admin (défaut: variable ADMIN_PASSWORD)',
        )

    def handle(self, *args, **options):
        """
        Exécute la commande d'initialisation.
        """
        if options['only_admin']:
            # Utilisé par la migration finale : le compte admin utilise le vrai modèle User,
            # il doit donc être créé quand toutes les colonnes de la table existent.
            with transaction.atomic():
                self._create_admin_user(
                    options['admin_email'] or settings.ADMIN_EMAIL,
                    options['admin_password'] or settings.ADMIN_PASSWORD,
                )
            return

        self.stdout.write(
            self.style.SUCCESS('🚀 Initialisation des données de base...')
        )

        try:
            with transaction.atomic():
                # Créer les permissions de base
                self._create_permissions()
                
                # Créer les rôles de base
                self._create_roles()

                # Permissions de la marketplace (créées par la migration marketplace.0002) pour les rôles de base
                self._assign_marketplace_permissions()

                # Rôle membre (« DevStreet Hub Developer ») et permissions DevStreet Hub
                call_command('init_devstreet_hub', stdout=self.stdout)

                # Permissions communauté / forum (créées ici si absentes, puis attribuées aux membres et admins)
                self._ensure_and_assign_communaute_permissions()

                # Permission assistant IA
                self._ensure_and_assign_ai_permissions()

                # Créer l'admin avant les seeds (les seeds peuvent créer l'admin sans rôle)
                if not options['skip_admin']:
                    self._create_admin_user(
                        options['admin_email'] or settings.ADMIN_EMAIL,
                        options['admin_password'] or settings.ADMIN_PASSWORD
                    )
                    # Compte Selina après schéma User complet (évite core.0006 précoce)
                    self._ensure_selina_user()

                # Exécuter les seeds pour les autres modèles
                self._run_model_seeds()

            self.stdout.write(
                self.style.SUCCESS('✅ Initialisation terminée avec succès!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de l\'initialisation: {str(e)}')
            )
            raise

    def _create_permissions(self):
        """
        Crée les permissions de base du système.
        """
        self.stdout.write('📋 Création des permissions de base...')

        # Définir les permissions de base
        base_permissions = [
            # Permissions utilisateurs
            {
                'code': 'users.view',
                'description': 'Voir les utilisateurs'
            },
            {
                'code': 'users.create',
                'description': 'Créer des utilisateurs'
            },
            {
                'code': 'users.update',
                'description': 'Modifier des utilisateurs'
            },
            {
                'code': 'users.delete',
                'description': 'Supprimer des utilisateurs'
            },
            
            # Permissions rôles
            {
                'code': 'roles.view',
                'description': 'Voir les rôles'
            },
            {
                'code': 'roles.create',
                'description': 'Créer des rôles'
            },
            {
                'code': 'roles.update',
                'description': 'Modifier des rôles'
            },
            {
                'code': 'roles.delete',
                'description': 'Supprimer des rôles'
            },
            
            # Permissions permissions
            {
                'code': 'permissions.view',
                'description': 'Voir les permissions'
            },
            {
                'code': 'permissions.create',
                'description': 'Créer des permissions'
            },
            {
                'code': 'permissions.update',
                'description': 'Modifier des permissions'
            },
            {
                'code': 'permissions.delete',
                'description': 'Supprimer des permissions'
            },
            
            # Permissions système
            {
                'code': 'system.admin',
                'description': 'Administration système complète'
            },
            {
                'code': 'system.view_logs',
                'description': 'Voir les logs système'
            },
            {
                'code': 'system.manage_settings',
                'description': 'Gérer les paramètres système'
            },
        ]

        created_count = 0
        for perm_data in base_permissions:
            if not Permission.objects.filter(code=perm_data['code']).exists():
                try:
                    self.permission_service.create_permission(perm_data)
                    created_count += 1
                    self.stdout.write(f'  ✓ Permission créée: {perm_data["code"]}')
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ Erreur création permission {perm_data["code"]}: {str(e)}')
                    )
            else:
                self.stdout.write(f'  - Permission existe déjà: {perm_data["code"]}')

        self.stdout.write(f'📋 {created_count} permissions créées.')

    def _create_roles(self):
        """
        Crée les rôles de base du système.
        """
        self.stdout.write('👥 Création des rôles de base...')

        # Définir les rôles de base avec leurs permissions
        base_roles = [
            {
                'name': 'Super Admin',
                'description': 'Administrateur avec tous les droits',
                'permission_codes': [
                    'users.view', 'users.create', 'users.update', 'users.delete',
                    'roles.view', 'roles.create', 'roles.update', 'roles.delete',
                    'permissions.view', 'permissions.create', 'permissions.update', 'permissions.delete',
                    'system.admin', 'system.view_logs', 'system.manage_settings'
                ]
            },
            {
                'name': 'Admin',
                'description': 'Administrateur avec droits de gestion des utilisateurs et rôles',
                'permission_codes': [
                    'users.view', 'users.create', 'users.update', 'users.delete',
                    'roles.view', 'roles.create', 'roles.update',
                    'permissions.view'
                ]
            },
            {
                'name': 'Manager',
                'description': 'Gestionnaire avec droits de lecture et modification limitée',
                'permission_codes': [
                    'users.view', 'users.update',
                    'roles.view',
                    'permissions.view'
                ]
            },
            {
                'name': 'Editor',
                'description': 'Éditeur avec droits de modification des utilisateurs',
                'permission_codes': [
                    'users.view', 'users.update'
                ]
            },
            {
                'name': 'Viewer',
                'description': 'Utilisateur avec droits de lecture uniquement',
                'permission_codes': [
                    'users.view'
                ]
            }
        ]

        created_count = 0
        for role_data in base_roles:
            if not Role.objects.filter(name=role_data['name']).exists():
                try:
                    self.role_service.create_role(role_data)
                    created_count += 1
                    self.stdout.write(f'  ✓ Rôle créé: {role_data["name"]}')
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ Erreur création rôle {role_data["name"]}: {str(e)}')
                    )
            else:
                self.stdout.write(f'  - Rôle existe déjà: {role_data["name"]}')

        self.stdout.write(f'👥 {created_count} rôles créés.')

    def _assign_marketplace_permissions(self):
        """Attribue les permissions marketplace aux membres et administrateurs."""
        from app.marketplace.permission_codes import MARKETPLACE_PERMISSION_CODES

        permissions = Permission.objects.filter(code__in=MARKETPLACE_PERMISSION_CODES)
        for role in Role.objects.filter(
            name__in=['DevStreet Hub Developer', 'Admin', 'Super Admin']
        ):
            role.permissions.add(*permissions)
        self.stdout.write(
            f'  ✓ {permissions.count()} permissions marketplace attribuées '
            f'à DevStreet Hub Developer / Admin / Super Admin'
        )

    def _ensure_and_assign_communaute_permissions(self):
        """Crée si besoin les permissions communauté/forum et les attribue aux membres et administrateurs."""
        from app.communaute.permission_codes import COMMUNAUTE_PERMISSION_CODES

        created = 0
        permissions = []
        for code in COMMUNAUTE_PERMISSION_CODES:
            permission, was_created = Permission.objects.get_or_create(
                code=code,
                defaults={'description': f'Can {code.split(".", 1)[1]} {code.split(".", 1)[0]}'},
            )
            if was_created:
                created += 1
            permissions.append(permission)

        target_roles = [
            'DevStreet Hub Developer',
            'Viewer',
            'Editor',
            'Manager',
            'Admin',
            'Super Admin',
        ]
        for role in Role.objects.filter(name__in=target_roles):
            role.permissions.add(*permissions)

        self.stdout.write(
            f'  ✓ {len(permissions)} permissions communauté '
            f'({created} créées) attribuées aux rôles membres et admins'
        )

    def _ensure_and_assign_ai_permissions(self):
        """Crée si besoin ai.chat et l'attribue aux rôles membre et administrateurs."""
        permission, was_created = Permission.objects.get_or_create(
            code='ai.chat',
            defaults={'description': 'Assistant IA : ai.chat'},
        )
        for role in Role.objects.filter(name__in=['DevStreet Hub Developer', 'Admin', 'Super Admin']):
            role.permissions.add(permission)
        status = 'créée' if was_created else 'existante'
        self.stdout.write(f'  ✓ Permission ai.chat ({status}) attribuée à DevStreet Hub Developer / Admin / Super Admin')

    def _ensure_selina_user(self):
        """Assure le compte système Selina pour les réponses forum @selina."""
        from django.db.utils import ProgrammingError

        self.stdout.write('🤖 Compte système Selina...')
        try:
            from app.ai.selina_user import ensure_selina_user

            user = ensure_selina_user()
            self.stdout.write(f'  ✓ Compte Selina prêt: {user.username} ({user.email})')
        except ProgrammingError as error:
            # Pendant les migrations précoces (ex. core.0006), le schéma User peut être incomplet.
            self.stdout.write(
                self.style.WARNING(
                    f'  ⚠ Compte Selina reporté (schéma incomplet): {error}'
                )
            )

    def _create_admin_user(self, admin_email, admin_password):
        """
        Crée l'utilisateur administrateur par défaut ou lui assigne le rôle Super Admin.
        """
        self.stdout.write('👤 Création de l\'utilisateur admin...')

        if User.objects.filter(email=admin_email).exists():
            user = User.objects.get(email=admin_email)
            if 'Super Admin' not in user.get_roles():
                self.user_service.assign_role_to_user(user.id, 'Super Admin')
                self.stdout.write(f'  ✓ Rôle Super Admin assigné à: {admin_email}')
            else:
                self.stdout.write(f'  - Utilisateur admin existe déjà: {admin_email}')
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                user.save(update_fields=['is_staff', 'is_superuser'])
            return

        try:
            # Créer l'utilisateur admin
            admin_data = {
                'username': 'admin',
                'email': admin_email,
                'first_name': 'Super',
                'last_name': 'Admin',
                'password': admin_password,
                'is_staff': True,
                'is_superuser': True,
                'role_names': ['Super Admin']
            }

            admin_user = self.user_service.create_user(admin_data)
            self.stdout.write(f'  ✓ Utilisateur admin créé: {admin_email}')
            self.stdout.write(f'  📧 Email: {admin_email}')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Erreur création admin: {str(e)}')
            )
            raise

    def _run_model_seeds(self):
        """
        Exécute automatiquement toutes les commandes de seed pour les modèles metier.
        """
        self.stdout.write('🌱 Exécution des seeds pour les modèles metier...')
        
        # Chemin vers le répertoire des commandes management
        management_dir = Path(__file__).parent.parent.parent / 'metier' / 'management' / 'commands'
        if not management_dir.exists():
            self.stdout.write(self.style.WARNING('  ⚠ Répertoire metier/management/commands non trouvé'))
            return
        
        seed_commands = []
        for file in management_dir.iterdir():
            if file.name.startswith('seed_') and file.name.endswith('.py'):
                command_name = file.stem
                seed_commands.append(command_name)
        
        for command in seed_commands:
            try:
                call_command(command)
                self.stdout.write(f'  ✓ Seed exécuté: {command}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Erreur exécution {command}: {str(e)}'))
        
        self.stdout.write(f'🌱 {len(seed_commands)} seeds exécutés.')

    def _display_summary(self):
        """
        Affiche un résumé des données créées.
        """
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 RÉSUMÉ DE L\'INITIALISATION')
        self.stdout.write('='*50)
        
        permissions_count = Permission.objects.count()
        roles_count = Role.objects.count()
        users_count = User.objects.count()
        
        self.stdout.write(f'📋 Permissions: {permissions_count}')
        self.stdout.write(f'👥 Rôles: {roles_count}')
        self.stdout.write(f'👤 Utilisateurs: {users_count}')
        
        self.stdout.write('\n🎯 PROCHAINES ÉTAPES:')
        self.stdout.write('1. Exécuter les migrations: python manage.py migrate')
        self.stdout.write('2. Démarrer le serveur: python manage.py runserver')
        self.stdout.write('3. Accéder à l\'API: http://localhost:8000/api/v1/')
        self.stdout.write('4. Documentation: http://localhost:8000/swagger/')
        self.stdout.write('='*50)