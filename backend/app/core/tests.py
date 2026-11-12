"""
Tests pour l'application core.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from app.core.models import Role, Permission
from app.core.services.user_service import UserService
from app.core.services.role_service import RoleService
from app.core.services.permission_service import PermissionService

User = get_user_model()


class ModelTests(TestCase):
    """
    Tests pour les modèles de données.
    """

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.permission = Permission.objects.create(
            code='test.permission',
            description='Permission de test'
        )
        self.role = Role.objects.create(
            name='Test Role',
            description='Rôle de test'
        )
        self.role.permissions.add(self.permission)

    def test_permission_creation(self):
        """Test de création d'une permission."""
        self.assertEqual(self.permission.code, 'test.permission')
        self.assertEqual(str(self.permission), 'test.permission')

    def test_role_creation(self):
        """Test de création d'un rôle."""
        self.assertEqual(self.role.name, 'Test Role')
        self.assertEqual(str(self.role), 'Test Role')
        self.assertIn(self.permission, self.role.permissions.all())

    def test_user_creation(self):
        """Test de création d'un utilisateur."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        user.roles.add(self.role)
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.full_name, 'Test User')
        self.assertTrue(user.has_permission('test.permission'))
        self.assertIn('Test Role', user.get_roles())


class ServiceTests(TestCase):
    """
    Tests pour les services métier.
    """

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.user_service = UserService()
        self.role_service = RoleService()
        self.permission_service = PermissionService()

    def test_permission_service(self):
        """Test du service de permissions."""
        # Créer une permission
        permission_data = {
            'code': 'service.test',
            'description': 'Test du service'
        }
        permission = self.permission_service.create_permission(permission_data)
        
        self.assertEqual(permission.code, 'service.test')
        
        # Récupérer la permission
        retrieved = self.permission_service.get_permission_by_code('service.test')
        self.assertEqual(retrieved.id, permission.id)

    def test_role_service(self):
        """Test du service de rôles."""
        # Créer une permission d'abord
        permission = Permission.objects.create(
            code='role.test',
            description='Test pour rôle'
        )
        
        # Créer un rôle avec permission
        role_data = {
            'name': 'Service Test Role',
            'description': 'Rôle de test du service',
            'permission_codes': ['role.test']
        }
        role = self.role_service.create_role(role_data)
        
        self.assertEqual(role.name, 'Service Test Role')
        self.assertIn('role.test', role.get_permissions())

    def test_user_service(self):
        """Test du service d'utilisateurs."""
        # Créer un rôle d'abord
        role = Role.objects.create(name='User Test Role')
        
        # Créer un utilisateur
        user_data = {
            'username': 'serviceuser',
            'email': 'service@example.com',
            'first_name': 'Service',
            'last_name': 'User',
            'password': 'servicepass123',
            'role_names': ['User Test Role']
        }
        user = self.user_service.create_user(user_data)
        
        self.assertEqual(user.email, 'service@example.com')
        self.assertIn('User Test Role', user.get_roles())


class AuthenticationAPITests(APITestCase):
    """
    Tests pour l'API d'authentification.
    """

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            first_name='API',
            last_name='User',
            password='apipass123'
        )

    def test_token_obtain(self):
        """Test d'obtention de token JWT."""
        url = reverse('core:token_obtain_pair')
        data = {
            'email': 'api@example.com',
            'password': 'apipass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Les jetons sont dans des cookies HttpOnly, jamais dans le corps
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertTrue(response.cookies['access_token']['httponly'])
        self.assertTrue(response.cookies['refresh_token']['httponly'])

    def test_token_refresh(self):
        """Test de rafraîchissement de token."""
        # Obtenir un token d'abord
        refresh = RefreshToken.for_user(self.user)
        
        url = reverse('core:token_refresh')
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_profile_access(self):
        """Test d'accès au profil utilisateur."""
        # Authentifier l'utilisateur
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('core:profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'api@example.com')


class UserAPITests(APITestCase):
    """
    Tests pour l'API des utilisateurs.
    """

    def setUp(self):
        """Configuration initiale pour les tests."""
        # Créer les permissions nécessaires
        Permission.objects.create(code='users.view', description='Voir les utilisateurs')
        Permission.objects.create(code='users.create', description='Créer des utilisateurs')
        
        # Créer un rôle admin
        self.admin_role = Role.objects.create(name='Admin', description='Administrateur')
        self.admin_role.permissions.set(Permission.objects.all())
        
        # Créer un utilisateur admin
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.admin_user.roles.add(self.admin_role)
        
        # Authentifier l'admin
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_user_list(self):
        """Test de listage des utilisateurs."""
        url = reverse('core:user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_user_create(self):
        """Test de création d'utilisateur."""
        url = reverse('core:user-list')
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'new@example.com')

    def test_user_detail(self):
        """Test de récupération des détails d'un utilisateur."""
        url = reverse('core:user-detail', kwargs={'pk': self.admin_user.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'admin@example.com')


class PermissionTests(TestCase):
    """
    Tests pour le système de permissions.
    """

    def setUp(self):
        """Configuration initiale pour les tests."""
        self.permission = Permission.objects.create(
            code='test.action',
            description='Action de test'
        )
        self.role = Role.objects.create(name='Test Role')
        self.role.permissions.add(self.permission)
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.roles.add(self.role)

    def test_user_has_permission(self):
        """Test de vérification de permission utilisateur."""
        self.assertTrue(self.user.has_permission('test.action'))
        self.assertFalse(self.user.has_permission('nonexistent.permission'))

    def test_user_get_all_permissions(self):
        """Test de récupération de toutes les permissions utilisateur."""
        permissions = self.user.get_all_permissions()
        self.assertIn('test.action', permissions)

    def test_superuser_permissions(self):
        """Test que les superutilisateurs ont toutes les permissions."""
        superuser = User.objects.create_user(
            username='super',
            email='super@example.com',
            password='superpass123',
            is_superuser=True
        )
        
        # Un superutilisateur devrait avoir n'importe quelle permission
        self.assertTrue(superuser.has_permission('any.permission'))


class IntegrationTests(APITestCase):
    """
    Tests d'intégration pour vérifier le fonctionnement global.
    """

    def setUp(self):
        """Configuration complète pour les tests d'intégration."""
        # Créer les permissions de base
        permissions_data = [
            {'code': 'users.view', 'description': 'Voir les utilisateurs'},
            {'code': 'users.create', 'description': 'Créer des utilisateurs'},
            {'code': 'roles.view', 'description': 'Voir les rôles'},
        ]
        
        for perm_data in permissions_data:
            Permission.objects.create(**perm_data)
        
        # Créer un rôle avec permissions
        self.role = Role.objects.create(name='Manager', description='Gestionnaire')
        self.role.permissions.set(Permission.objects.all())
        
        # Créer un utilisateur avec le rôle
        self.user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='managerpass123'
        )
        self.user.roles.add(self.role)

    def test_complete_workflow(self):
        """Test d'un workflow complet d'authentification et d'utilisation de l'API."""
        # 1. Obtenir un token
        token_url = reverse('core:token_obtain_pair')
        token_data = {
            'email': 'manager@example.com',
            'password': 'managerpass123'
        }
        token_response = self.client.post(token_url, token_data, format='json')
        
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        access_token = token_response.cookies['access_token'].value
        
        # 2. Utiliser le token pour accéder au profil
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_url = reverse('core:profile')
        profile_response = self.client.get(profile_url)
        
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['email'], 'manager@example.com')
        
        # 3. Vérifier les permissions
        check_perm_url = reverse('core:check_permission')
        check_data = {'permission_code': 'users.view'}
        perm_response = self.client.post(check_perm_url, check_data, format='json')
        
        self.assertEqual(perm_response.status_code, status.HTTP_200_OK)
        self.assertTrue(perm_response.data['has_permission'])
        
        # 4. Accéder à la liste des utilisateurs
        users_url = reverse('core:user-list')
        users_response = self.client.get(users_url)
        
        self.assertEqual(users_response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(users_response.data, list)


class CommandTests(TestCase):
    """
    Tests pour les commandes de gestion Django.
    """

    def test_init_data_command(self):
        """Test de la commande d'initialisation des données."""
        from django.core.management import call_command
        from io import StringIO
        
        # Capturer la sortie de la commande
        out = StringIO()
        call_command('init_data', '--skip-admin', stdout=out)
        
        # Vérifier que les permissions ont été créées
        self.assertTrue(Permission.objects.filter(code='users.view').exists())
        self.assertTrue(Permission.objects.filter(code='roles.create').exists())
        
        # Vérifier que les rôles ont été créés
        self.assertTrue(Role.objects.filter(name='Super Admin').exists())
        self.assertTrue(Role.objects.filter(name='Viewer').exists())
        
        # Vérifier la sortie
        output = out.getvalue()
        self.assertIn('Initialisation terminée avec succès', output)