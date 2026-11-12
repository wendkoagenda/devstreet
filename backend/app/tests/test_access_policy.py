"""
Politique d'accès aux comptes et aux rôles : pas de montée en puissance, pas d'action sur soi-même, superutilisateurs
protégés, dernier superutilisateur conservé, et traçabilité de chaque modification dans le journal d'audit.
"""
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from app.core.models import AuditLog, Permission, Role
from app.core.services.access_policy import AccessDenied, AccessPolicy
from app.core.services.audit_service import Actions

User = get_user_model()

PASSWORD = 'MotDePasse-Solide-42'
MANAGER_CODES = ['users.view', 'users.create', 'users.update', 'users.delete', 'roles.view', 'roles.update']
SUPER_CODES = MANAGER_CODES + ['roles.create', 'roles.delete']


def make_role(name, codes):
    role = Role.objects.create(name=name)
    for code in codes:
        permission, _ = Permission.objects.get_or_create(code=code)
        role.permissions.add(permission)
    return role


def make_user(email, roles=(), **flags):
    user = User.objects.create_user(username=email.split('@')[0], email=email, password=PASSWORD,
                                    first_name='Prénom', last_name='Nom', **flags)
    user.roles.set(roles)
    return user


def api(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


class PolicyTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        self.viewer_role = make_role('Viewer', ['users.view'])
        self.manager_role = make_role('Manager', MANAGER_CODES)
        self.super_role = make_role('Super', SUPER_CODES)

        self.root = make_user('root@example.com', is_superuser=True, is_staff=True)
        self.manager = make_user('manager@example.com', [self.manager_role])
        self.plain = make_user('plain@example.com')
        self.powerful = make_user('powerful@example.com', [self.super_role])

    def denied_entries(self):
        return AuditLog.objects.filter(action=Actions.ACCESS_DENIED)

    def entries(self, action):
        return AuditLog.objects.filter(action=action)


class RoleGrantingTests(PolicyTestCase):
    def test_manager_cannot_assign_a_more_powerful_role(self):
        response = api(self.manager).post(f'/api/v1/users/{self.plain.pk}/assign_role', {'role_names': ['Super']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('plus puissant', response.data['error'])
        self.assertEqual(self.plain.get_roles(), [])
        self.assertEqual(self.denied_entries().get().actor, self.manager)

    def test_manager_can_assign_a_role_within_their_own_rights(self):
        response = api(self.manager).post(f'/api/v1/users/{self.plain.pk}/assign_role', {'role_names': ['Viewer']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([role['name'] for role in response.data['roles']], ['Viewer'])
        entry = self.entries(Actions.USER_ROLE_ASSIGNED).get()
        self.assertEqual((entry.actor, entry.target_id, entry.metadata['roles']), (self.manager, str(self.plain.pk), ['Viewer']))

    def test_superuser_can_assign_any_role(self):
        response = api(self.root).post(f'/api/v1/users/{self.plain.pk}/assign_role', {'role_names': ['Super']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unknown_role_is_a_validation_error(self):
        response = api(self.manager).post(f'/api/v1/users/{self.plain.pk}/assign_role', {'role_names': ['Fantome']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_cannot_create_a_user_with_a_more_powerful_role(self):
        payload = {'username': 'nouveau', 'email': 'nouveau@example.com', 'first_name': 'N', 'last_name': 'N',
                   'password': PASSWORD, 'password_confirm': PASSWORD, 'role_names': ['Super']}
        response = api(self.manager).post('/api/v1/users', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(email='nouveau@example.com').exists())

    def test_creating_a_user_is_journalized(self):
        payload = {'username': 'nouveau', 'email': 'nouveau@example.com', 'first_name': 'N', 'last_name': 'N',
                   'password': PASSWORD, 'password_confirm': PASSWORD, 'role_names': ['Viewer']}
        response = api(self.manager).post('/api/v1/users', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        entry = self.entries(Actions.USER_CREATED).get()
        self.assertEqual(entry.metadata, {'label': 'nouveau@example.com', 'roles': ['Viewer']})
        self.assertNotIn(PASSWORD, str(entry.metadata))


class HierarchyTests(PolicyTestCase):
    def test_only_a_superuser_can_change_is_staff(self):
        denied = api(self.manager).patch(f'/api/v1/users/{self.plain.pk}', {'is_staff': True}, format='json')
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)
        allowed = api(self.root).patch(f'/api/v1/users/{self.plain.pk}', {'is_staff': True}, format='json')
        self.assertEqual(allowed.status_code, status.HTTP_200_OK)

    def test_manager_cannot_touch_a_superuser(self):
        client = api(self.manager)
        self.assertEqual(client.patch(f'/api/v1/users/{self.root.pk}', {'first_name': 'X'}, format='json').status_code, 403)
        self.assertEqual(client.delete(f'/api/v1/users/{self.root.pk}').status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.root.pk).exists())

    def test_manager_cannot_touch_a_user_with_higher_rights(self):
        client = api(self.manager)
        self.assertEqual(client.patch(f'/api/v1/users/{self.powerful.pk}', {'first_name': 'X'}, format='json').status_code, 403)
        self.assertEqual(client.delete(f'/api/v1/users/{self.powerful.pk}').status_code, 403)
        self.assertEqual(client.post(f'/api/v1/users/{self.powerful.pk}/remove_role', {'role_names': ['Super']}, format='json').status_code, 403)

    def test_manager_can_manage_a_user_below_them(self):
        response = api(self.manager).patch(f'/api/v1/users/{self.plain.pk}', {'first_name': 'Modifié'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Modifié')

    def test_removing_a_role_is_journalized(self):
        self.plain.roles.add(self.viewer_role)
        response = api(self.manager).post(f'/api/v1/users/{self.plain.pk}/remove_role', {'role_names': ['Viewer']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['roles'], [])
        self.assertEqual(self.entries(Actions.USER_ROLE_REMOVED).get().metadata['roles'], ['Viewer'])


class SelfProtectionTests(PolicyTestCase):
    def test_nobody_deletes_their_own_account(self):
        other_super = make_user('autre-root@example.com', is_superuser=True)
        for user in (self.manager, other_super):
            response = api(user).delete(f'/api/v1/users/{user.pk}')
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, user.email)
            self.assertTrue(User.objects.filter(pk=user.pk).exists())

    def test_a_user_cannot_change_their_own_roles(self):
        response = api(self.manager).patch(f'/api/v1/users/{self.manager.pk}', {'role_names': ['Super']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.manager.get_roles(), ['Manager'])

    def test_a_user_cannot_assign_a_role_to_themselves(self):
        response = api(self.manager).post(f'/api/v1/users/{self.manager.pk}/assign_role', {'role_names': ['Viewer']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_a_user_cannot_deactivate_themselves(self):
        response = api(self.manager).patch(f'/api/v1/users/{self.manager.pk}', {'is_active': False}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_a_user_can_still_edit_their_own_profile(self):
        response = api(self.manager).patch(f'/api/v1/users/{self.manager.pk}', {'first_name': 'Moi'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unchanged_roles_and_flags_in_a_self_update_are_accepted(self):
        payload = {'first_name': 'Moi', 'role_names': ['Manager'], 'is_active': True, 'is_staff': False}
        response = api(self.manager).patch(f'/api/v1/users/{self.manager.pk}', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LastSuperuserTests(PolicyTestCase):
    def test_the_only_active_superuser_is_protected(self):
        with self.assertRaises(AccessDenied):
            AccessPolicy(self.manager).ensure_not_last_superuser(self.root)

    def test_a_second_active_superuser_lifts_the_protection(self):
        make_user('deuxieme@example.com', is_superuser=True)
        AccessPolicy(self.manager).ensure_not_last_superuser(self.root)

    def test_an_inactive_second_superuser_does_not_count(self):
        make_user('inactif@example.com', is_superuser=True, is_active=False)
        with self.assertRaises(AccessDenied):
            AccessPolicy(self.manager).ensure_not_last_superuser(self.root)

    def test_a_regular_user_is_never_concerned(self):
        AccessPolicy(self.manager).ensure_not_last_superuser(self.plain)

    def test_a_superuser_can_delete_another_superuser_when_one_remains(self):
        second = make_user('second@example.com', is_superuser=True)
        response = api(self.root).delete(f'/api/v1/users/{second.pk}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class RolePolicyTests(PolicyTestCase):
    def test_manager_cannot_add_a_permission_they_lack(self):
        response = api(self.manager).post(f'/api/v1/roles/{self.viewer_role.pk}/assign_permission',
                                          {'permission_code': 'roles.delete'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn('roles.delete', self.viewer_role.get_permissions())

    def test_manager_can_add_a_permission_they_hold(self):
        response = api(self.manager).post(f'/api/v1/roles/{self.viewer_role.pk}/assign_permission',
                                          {'permission_code': 'users.create'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.entries(Actions.ROLE_PERMISSION_ASSIGNED).get().metadata['permissions'], ['users.create'])

    def test_manager_cannot_bulk_assign_beyond_their_rights(self):
        response = api(self.manager).post(f'/api/v1/roles/{self.viewer_role.pk}/bulk_assign_permissions',
                                          {'permission_codes': ['users.view', 'roles.delete']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_cannot_modify_or_delete_a_more_powerful_role(self):
        client = api(self.manager)
        self.assertEqual(client.patch(f'/api/v1/roles/{self.super_role.pk}', {'description': 'x'}, format='json').status_code, 403)
        self.assertEqual(client.delete(f'/api/v1/roles/{self.super_role.pk}').status_code, 403)
        self.assertEqual(client.post(f'/api/v1/roles/{self.super_role.pk}/remove_permission',
                                     {'permission_code': 'users.view'}, format='json').status_code, 403)
        self.assertTrue(Role.objects.filter(pk=self.super_role.pk).exists())

    def test_manager_cannot_create_a_role_beyond_their_rights(self):
        response = api(self.manager).post('/api/v1/roles', {'name': 'Trop', 'permission_codes': ['roles.delete']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Role.objects.filter(name='Trop').exists())

    def test_a_role_within_the_creators_rights_is_created_and_journalized(self):
        response = api(self.powerful).post('/api/v1/roles', {'name': 'Lecteur+', 'permission_codes': ['users.view']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        entry = self.entries(Actions.ROLE_CREATED).get()
        self.assertEqual((entry.metadata['label'], entry.metadata['permissions']), ('Lecteur+', ['users.view']))

    def test_a_role_update_cannot_smuggle_permissions_through_permission_codes(self):
        response = api(self.manager).patch(f'/api/v1/roles/{self.viewer_role.pk}', {'permission_codes': ['roles.delete']}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_modify_the_most_powerful_role(self):
        response = api(self.root).patch(f'/api/v1/roles/{self.super_role.pk}', {'description': 'ok'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.entries(Actions.ROLE_UPDATED).get().metadata['fields'], ['description'])

    def test_deleting_a_role_is_journalized(self):
        unused = make_role('Inutilisé', ['users.view'])
        response = api(self.powerful).delete(f'/api/v1/roles/{unused.pk}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        entry = self.entries(Actions.ROLE_DELETED).get()
        self.assertEqual((entry.target_id, entry.metadata['label']), (str(unused.pk), 'Inutilisé'))


class JournalOfUserChangesTests(PolicyTestCase):
    def test_update_records_the_changed_fields_and_never_a_password(self):
        api(self.manager).patch(f'/api/v1/users/{self.plain.pk}', {'first_name': 'A', 'last_name': 'B'}, format='json')
        entry = self.entries(Actions.USER_UPDATED).get()
        self.assertEqual(entry.metadata['fields'], ['first_name', 'last_name'])
        self.assertEqual(entry.actor, self.manager)

    def test_deleting_a_user_is_journalized_with_its_identifier(self):
        victim = make_user('victime@example.com')
        response = api(self.manager).delete(f'/api/v1/users/{victim.pk}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        entry = self.entries(Actions.USER_DELETED).get()
        self.assertEqual((entry.target_type, entry.target_id, entry.metadata['label']), ('user', str(victim.pk), 'victime@example.com'))

    def test_a_refused_action_changes_nothing_and_is_journalized(self):
        before = self.plain.updated_at
        api(self.manager).post(f'/api/v1/users/{self.plain.pk}/assign_role', {'role_names': ['Super']}, format='json')
        self.plain.refresh_from_db()
        self.assertEqual(self.plain.updated_at, before)
        self.assertEqual(self.entries(Actions.USER_ROLE_ASSIGNED).count(), 0)
        entry = self.denied_entries().get()
        self.assertEqual(entry.metadata['action'], 'assign_role')


class EndpointRobustnessTests(PolicyTestCase):
    def test_unknown_user_gives_404_with_a_message(self):
        client = api(self.root)
        for call in (client.get('/api/v1/users/99999'), client.delete('/api/v1/users/99999'),
                     client.patch('/api/v1/users/99999', {'first_name': 'x'}, format='json'),
                     client.post('/api/v1/users/99999/assign_role', {'role_names': ['Viewer']}, format='json')):
            self.assertEqual(call.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(call.data, {'error': 'Utilisateur non trouvé'})

    def test_a_non_numeric_identifier_is_an_unknown_route_not_a_server_error(self):
        client = api(self.root)
        self.assertEqual(client.get('/api/v1/users/abc').status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(client.get('/api/v1/roles/abc').status_code, status.HTTP_404_NOT_FOUND)

    def test_user_search_works(self):
        response = api(self.manager).get('/api/v1/users/search', {'q': 'plain'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([user['email'] for user in response.data], ['plain@example.com'])

    def test_user_search_without_a_term_is_refused(self):
        self.assertEqual(api(self.manager).get('/api/v1/users/search').status_code, status.HTTP_400_BAD_REQUEST)

    def test_role_can_be_updated_with_its_own_name(self):
        response = api(self.root).put(f'/api/v1/roles/{self.viewer_role.pk}', {'name': 'Viewer', 'description': 'Lecture'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Lecture')

    def test_role_partial_update_works(self):
        response = api(self.root).patch(f'/api/v1/roles/{self.viewer_role.pk}', {'description': 'Lecture seule'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unknown_role_gives_404(self):
        client = api(self.root)
        self.assertEqual(client.patch('/api/v1/roles/99999', {'description': 'x'}, format='json').status_code, 404)
        self.assertEqual(client.delete('/api/v1/roles/99999').status_code, 404)
        self.assertEqual(client.post('/api/v1/roles/99999/assign_permission', {'permission_code': 'users.view'}, format='json').status_code, 404)
