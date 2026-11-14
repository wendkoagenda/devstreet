"""Tests des règles sur le nom d'utilisateur (adresse /profil/<nom>)."""
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from app.core.serializers import ProfileUpdateSerializer, PublicRegisterSerializer, UserUpdateSerializer
from app.core.username_rules import (
    MESSAGE_RESERVED,
    MESSAGE_TAKEN,
    check_username,
    is_reserved_username,
)

User = get_user_model()


class UsernameRulesTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='motdepasse-solide',
            first_name='Alice',
            last_name='Martin',
        )

    def test_nom_reserve_refuse_quelle_que_soit_la_casse(self):
        self.assertTrue(is_reserved_username('ME'))
        self.assertEqual(check_username('Moi'), MESSAGE_RESERVED)

    def test_doublon_a_la_casse_pres_refuse(self):
        self.assertEqual(check_username('ALICE'), MESSAGE_TAKEN)

    def test_son_propre_nom_reste_valide_a_la_modification(self):
        self.assertIsNone(check_username('Alice', exclude_pk=self.alice.pk))

    def test_base_interdit_les_doublons_a_la_casse_pres(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(
                username='Alice',
                email='autre@example.com',
                password='motdepasse-solide',
                first_name='A',
                last_name='B',
            )

    def test_inscription_refuse_nom_reserve_et_doublon(self):
        base = {
            'email': 'new@example.com',
            'first_name': 'N',
            'last_name': 'M',
            'password': 'motdepasse-solide',
            'password_confirm': 'motdepasse-solide',
        }
        reserve = PublicRegisterSerializer(data={**base, 'username': 'moi'})
        self.assertFalse(reserve.is_valid())
        self.assertIn('username', reserve.errors)

        doublon = PublicRegisterSerializer(data={**base, 'username': 'ALICE'})
        self.assertFalse(doublon.is_valid())
        self.assertIn('username', doublon.errors)

    def test_modification_refuse_nom_reserve(self):
        serializer = UserUpdateSerializer(
            self.alice, data={'username': 'me'}, partial=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_profil_modifiable_par_le_membre(self):
        serializer = ProfileUpdateSerializer(
            self.alice, data={'first_name': 'Alicia', 'username': 'Alice'}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)  # son propre nom reste valide
        serializer.save()
        self.alice.refresh_from_db()
        self.assertEqual(self.alice.first_name, 'Alicia')

    def test_profil_refuse_nom_reserve_doublon_et_nom_vide(self):
        bob = User.objects.create_user(
            username='bob', email='bob@example.com', password='motdepasse-solide', first_name='Bob', last_name='L'
        )
        for data in ({'username': 'moi'}, {'username': 'ALICE'}, {'first_name': '  '}):
            serializer = ProfileUpdateSerializer(bob, data=data, partial=True)
            self.assertFalse(serializer.is_valid(), data)
