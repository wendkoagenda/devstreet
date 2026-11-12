"""Commande pour exécuter automatiquement tous les tests du projet."""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from pathlib import Path
import os
import sys


class Command(BaseCommand):
    help = 'Exécute automatiquement tous les tests du projet'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pattern',
            type=str,
            default='test*.py',
            help='Pattern pour les fichiers de test'
        )
        parser.add_argument(
            '--discover-only',
            action='store_true',
            help='Découvrir les tests sans les exécuter'
        )

    def handle(self, *args, **options):
        """Exécute tous les tests du projet."""
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('🧪 DÉCOUVERTE ET EXÉCUTION DES TESTS'))
        self.stdout.write('='*60)
        
        # Découvrir tous les modules de test
        test_modules = self._discover_test_modules()
        
        if not test_modules:
            self.stdout.write(self.style.WARNING('❌ Aucun module de test trouvé'))
            return
            
        self.stdout.write(f'📋 {len(test_modules)} module(s) de test découvert(s):')
        for module in test_modules:
            self.stdout.write(f'   • {module}')
        self.stdout.write('')
        
        # Si l'option discover-only est activée, ne pas exécuter les tests
        if options['discover_only']:
            self.stdout.write(self.style.SUCCESS('✅ Découverte terminée (--discover-only activé)'))
            return
        
        # Préparer les arguments pour la commande test
        test_kwargs = {
            'verbosity': options.get('verbosity', 2),
            'interactive': False,
        }
        
        # Utiliser les options Django natives si elles sont disponibles
        django_options = ['keepdb', 'parallel', 'failfast', 'debug_mode', 'timing']
        for opt in django_options:
            if opt in options and options[opt] is not None:
                test_kwargs[opt] = options[opt]
        
        # Exécuter tous les tests
        try:
            self.stdout.write('🚀 Démarrage des tests...')
            self.stdout.write('-'*60)
            
            # Exécuter la commande test de Django avec tous les modules découverts
            call_command('test', *test_modules, **test_kwargs)
            
            self.stdout.write('-'*60)
            self.stdout.write(self.style.SUCCESS('✅ Tous les tests ont été exécutés'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de l\'exécution des tests: {e}'))
            sys.exit(1)
        
        self._display_summary()
    
    def _discover_test_modules(self):
        """Découvre automatiquement tous les modules de test dans le projet."""
        test_modules = []
        
        # Chemin racine du projet Django (app/)
        project_root = Path(__file__).parent.parent.parent
        
        # Rechercher dans toutes les apps
        for app_dir in project_root.iterdir():
            if app_dir.is_dir() and not app_dir.name.startswith('.') and app_dir.name != '__pycache__':
                # Vérifier s'il y a un fichier tests.py
                tests_file = app_dir / 'tests.py'
                if tests_file.exists():
                    module_name = f'app.{app_dir.name}.tests'
                    test_modules.append(module_name)
                    self.stdout.write(f'   📄 Trouvé: {tests_file}')
                
                # Vérifier s'il y a un dossier tests/
                tests_dir = app_dir / 'tests'
                if tests_dir.exists() and tests_dir.is_dir():
                    # Rechercher tous les fichiers test_*.py dans le dossier tests
                    for test_file in tests_dir.glob('test_*.py'):
                        if test_file.name != '__init__.py':
                            module_name = f'app.{app_dir.name}.tests.{test_file.stem}'
                            test_modules.append(module_name)
                            self.stdout.write(f'   📄 Trouvé: {test_file}')
        
        # Rechercher dans le dossier tests global s'il existe
        global_tests_dir = project_root / 'tests'
        if global_tests_dir.exists() and global_tests_dir.is_dir():
            for test_file in global_tests_dir.glob('test_*.py'):
                if test_file.name != '__init__.py':
                    module_name = f'app.tests.{test_file.stem}'
                    test_modules.append(module_name)
                    self.stdout.write(f'   📄 Trouvé: {test_file}')
        
        return sorted(list(set(test_modules)))
    
    def _display_summary(self):
        """Affiche un résumé de l'exécution des tests."""
        self.stdout.write('')
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('📊 RÉSUMÉ DE L\'EXÉCUTION DES TESTS'))
        self.stdout.write('='*60)
        self.stdout.write('✅ Exécution terminée')
        self.stdout.write('')
        self.stdout.write('💡 Conseils:')
        self.stdout.write('   • Utilisez --failfast pour arrêter au premier échec')
        self.stdout.write('   • Utilisez --keepdb pour accélérer les tests répétés')
        self.stdout.write('   • Utilisez --parallel N pour exécuter en parallèle')
        self.stdout.write('   • Utilisez --verbosity 3 pour plus de détails')
        self.stdout.write('   • Utilisez --discover-only pour voir les tests sans les exécuter')
        self.stdout.write('')
        self.stdout.write('📖 Exemples d\'utilisation:')
        self.stdout.write('   python manage.py run_tests')
        self.stdout.write('   python manage.py run_tests --discover-only')
        self.stdout.write('   python manage.py run_tests --failfast --keepdb')
        self.stdout.write('   python manage.py run_tests --parallel 4 --verbosity 3')
        self.stdout.write('='*60)