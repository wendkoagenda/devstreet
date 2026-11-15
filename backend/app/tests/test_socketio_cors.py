"""
Origines CORS Socket.IO : dérivées de CORS_ALLOWED_ORIGINS et FRONTEND_URL.
"""
from django.test import SimpleTestCase, override_settings

from app.communaute.socketio_app import socketio_cors_origins


class SocketioCorsOriginsTests(SimpleTestCase):
    @override_settings(
        CORS_ALLOWED_ORIGINS=[
            'https://devstreet.ewo-soft.com',
            'http://localhost:5173',
        ],
        FRONTEND_URL='https://devstreet.ewo-soft.com',
    )
    def test_includes_prod_and_local_without_duplicate(self):
        self.assertEqual(
            socketio_cors_origins(),
            [
                'https://devstreet.ewo-soft.com',
                'http://localhost:5173',
            ],
        )

    @override_settings(
        CORS_ALLOWED_ORIGINS=['http://localhost:5173'],
        FRONTEND_URL='https://app.exemple.fr/',
    )
    def test_appends_frontend_url_when_absent(self):
        self.assertEqual(
            socketio_cors_origins(),
            [
                'http://localhost:5173',
                'https://app.exemple.fr',
            ],
        )

    @override_settings(
        CORS_ALLOWED_ORIGINS=['*', 'http://127.0.0.1:5173'],
        FRONTEND_URL='http://127.0.0.1:5173',
    )
    def test_skips_star_and_deduplicates(self):
        self.assertEqual(
            socketio_cors_origins(),
            ['http://127.0.0.1:5173'],
        )
