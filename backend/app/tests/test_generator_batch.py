"""
Génération de plusieurs modèles à la fois (saisie « 1,2,3 ») et génération de l'API et de l'interface en une fois.
Les générateurs sont simulés : aucun fichier du dépôt n'est écrit.
"""
import contextlib
import io
from unittest import mock

from django.test import SimpleTestCase

from scripts import generate_api as cli
from scripts.generate_api import (
    EXIT_GENERATION_FAILED,
    EXIT_INVALID_SCHEMA,
    EXIT_NOT_FOUND,
    EXIT_OK,
    exit_code_for,
    parse_model_names,
    parse_selection,
    run_generation,
    select_models,
)


class FakeState:
    """État minimal : modèles disponibles, API et interfaces déjà générées."""

    def __init__(self, models=None, generated=(), frontends=()):
        self.models = {'zone_1': {'Alpha': {}, 'Beta': {}, 'Gamma': {}, 'Delta': {}}} if models is None else models
        self.generated = set(generated)
        self.frontends = set(frontends)

    def list_available_models(self):
        return self.models

    def is_api_generated(self, name):
        return name in self.generated

    def is_frontend_generated(self, name):
        return name in self.frontends

    def get_api_app_name(self, name):
        return 'metier'

    def find_model_file(self, zone, name):
        return None  # l'application déclarée s'affiche alors « ? »

    def add_generated_frontend(self, model_name, zone, file, auto_detected=False):
        self.frontends.add(model_name)


def run_quiet(function, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        result = function(*args, **kwargs)
    return result, out.getvalue()


class ParseSelectionTests(SimpleTestCase):
    def test_comma_separated_numbers(self):
        self.assertEqual(parse_selection('1,2,3', 5), [0, 1, 2])

    def test_order_typed_is_kept_and_duplicates_dropped(self):
        self.assertEqual(parse_selection('3,1,3,2', 5), [2, 0, 1])

    def test_ranges_and_mixed(self):
        self.assertEqual(parse_selection('1-3', 5), [0, 1, 2])
        self.assertEqual(parse_selection('1, 3-5', 5), [0, 2, 3, 4])
        self.assertEqual(parse_selection('2 - 4', 5), [1, 2, 3])

    def test_spaces_and_semicolons_separate_too(self):
        self.assertEqual(parse_selection('1 2;3', 5), [0, 1, 2])

    def test_all_keywords(self):
        for word in ('tous', 'TOUS', 'toutes', 'all', '*'):
            self.assertEqual(parse_selection(word, 3), [0, 1, 2], word)

    def test_single_number(self):
        self.assertEqual(parse_selection('2', 3), [1])

    def test_invalid_input_is_rejected_with_a_clear_message(self):
        cases = {
            '': 'Aucune sélection',
            '   ': 'Aucune sélection',
            'a': 'Sélection invalide',
            '1,x': 'Sélection invalide',
            '0': 'hors liste',
            '6': 'hors liste',
            '1-9': 'hors liste',
            '3-1': 'Plage invalide',
            ',,,': 'Aucune sélection',
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                with self.assertRaisesMessage(ValueError, expected):
                    parse_selection(raw, 5)

    def test_model_names_from_the_command_line(self):
        self.assertEqual(parse_model_names('Elitest, Dragon ,Elitest,,Fusion'), ['Elitest', 'Dragon', 'Fusion'])
        self.assertEqual(parse_model_names(' , '), [])


class SelectModelsTests(SimpleTestCase):
    def select(self, typed, state=None):
        with mock.patch('builtins.input', return_value=typed):
            return run_quiet(select_models, state or FakeState(), 'Modèles :', True)

    def test_returns_zone_and_model_in_the_typed_order(self):
        targets, output = self.select('3,1')
        self.assertEqual(targets, [('zone_1', 'Gamma'), ('zone_1', 'Alpha')])
        self.assertIn('1. Alpha (Zone: zone_1, app: ?)', output)  # pas de JSON dans ce faux état

    def test_shows_which_apis_are_already_generated(self):
        _, output = self.select('1', FakeState(generated=['Beta']))
        self.assertIn('2. Beta', output)
        self.assertIn('✅ Généré', output)
        self.assertIn('❌ Non généré', output)

    def test_shows_which_frontends_are_already_generated(self):
        with mock.patch('builtins.input', return_value='1'):
            _, output = run_quiet(
                select_models,
                FakeState(frontends=['Beta']),
                'Frontend :',
                show_frontend_status=True,
            )
        self.assertIn('2. Beta', output)
        self.assertIn('✅ Interface générée', output)
        self.assertIn('❌ Interface non générée', output)

    def test_shows_api_and_frontend_status_together(self):
        with mock.patch('builtins.input', return_value='1'):
            _, output = run_quiet(
                select_models,
                FakeState(generated=['Alpha'], frontends=['Beta']),
                'Les deux :',
                True,
                show_frontend_status=True,
            )
        self.assertIn('API ✅  Interface ❌', output)
        self.assertIn('API ❌  Interface ✅', output)

    def test_invalid_selection_returns_none_with_an_error(self):
        targets, output = self.select('9')
        self.assertIsNone(targets)
        self.assertIn('❌', output)

    def test_no_model_available(self):
        targets, output = self.select('1', FakeState(models={}))
        self.assertIsNone(targets)
        self.assertIn('Aucun modèle disponible', output)


class RunGenerationTests(SimpleTestCase):
    TARGETS = [('zone_1', 'Alpha'), ('zone_1', 'Beta'), ('zone_1', 'Gamma')]

    def run_with(self, backend_codes=None, frontend_codes=None, state=None, **kwargs):
        """Lance run_generation avec des générateurs simulés renvoyant les codes donnés par modèle."""
        backend_codes = backend_codes or {}
        frontend_codes = frontend_codes or {}
        calls = []

        def fake_backend(_state, zone, name):
            calls.append(('api', name))
            return backend_codes.get(name, EXIT_OK)

        def fake_frontend(_state, zone, name):
            calls.append(('ui', name))
            return frontend_codes.get(name, EXIT_OK)

        with mock.patch.object(cli, 'generate_backend_for_model', side_effect=fake_backend), \
                mock.patch.object(cli, 'generate_frontend_for_model', side_effect=fake_frontend), \
                mock.patch.object(cli, 'sync_and_validate') as sync:
            results, output = run_quiet(run_generation, state or FakeState(), self.TARGETS, **kwargs)
        return results, output, calls, sync

    def test_api_and_interface_for_each_model_in_order(self):
        results, output, calls, sync = self.run_with(backend=True, frontend=True)
        self.assertEqual(calls, [
            ('api', 'Alpha'), ('ui', 'Alpha'),
            ('api', 'Beta'), ('ui', 'Beta'),
            ('api', 'Gamma'), ('ui', 'Gamma'),
        ])
        self.assertEqual(exit_code_for(results), EXIT_OK)
        self.assertIn('[1/3] Alpha', output)
        self.assertIn('Tout a été généré avec succès', output)
        sync.assert_called_once()  # un seul contrôle d'état pour tout le lot

    def test_a_failure_does_not_stop_the_other_models(self):
        results, output, calls, _ = self.run_with(
            backend_codes={'Beta': EXIT_GENERATION_FAILED}, backend=True, frontend=True
        )
        self.assertIn(('api', 'Gamma'), calls)
        self.assertIn(('ui', 'Gamma'), calls)
        self.assertEqual(exit_code_for(results), EXIT_GENERATION_FAILED)
        self.assertIn('❌ Beta', output)
        self.assertIn('✅ Alpha', output)
        self.assertIn('1 modèle(s) en échec', output)

    def test_interface_is_skipped_when_its_api_failed(self):
        results, output, calls, _ = self.run_with(
            backend_codes={'Beta': EXIT_INVALID_SCHEMA}, backend=True, frontend=True
        )
        self.assertNotIn(('ui', 'Beta'), calls)
        self.assertIn('Interface de Beta ignorée', output)
        beta = next(entry for entry in results if entry['model'] == 'Beta')
        self.assertIsNone(beta['frontend'])
        self.assertEqual(exit_code_for(results), EXIT_INVALID_SCHEMA)

    def test_interface_failure_is_reported_even_if_the_api_succeeded(self):
        results, output, _, _ = self.run_with(
            frontend_codes={'Gamma': EXIT_GENERATION_FAILED}, backend=True, frontend=True
        )
        self.assertEqual(exit_code_for(results), EXIT_GENERATION_FAILED)
        self.assertIn('❌ Gamma : API ✅  Interface ❌', output)

    def test_frontend_only_never_calls_the_backend(self):
        results, _, calls, sync = self.run_with(backend=False, frontend=True)
        self.assertEqual([call for call in calls if call[0] == 'api'], [])
        self.assertEqual(len([call for call in calls if call[0] == 'ui']), 3)
        sync.assert_not_called()  # pas de synchronisation d'état sans génération backend

    def test_backend_only_never_calls_the_frontend(self):
        _, _, calls, _ = self.run_with(backend=True, frontend=False)
        self.assertEqual([call for call in calls if call[0] == 'ui'], [])

    def test_no_state_check_when_every_api_failed(self):
        codes = {name: EXIT_NOT_FOUND for _, name in self.TARGETS}
        results, _, _, sync = self.run_with(backend_codes=codes, backend=True, frontend=False)
        sync.assert_not_called()
        self.assertEqual(exit_code_for(results), EXIT_NOT_FOUND)

    def test_regeneration_is_asked_once_for_all_existing_apis(self):
        confirm = mock.Mock(return_value=True)
        _, _, calls, _ = self.run_with(
            state=FakeState(generated=['Alpha', 'Gamma']), backend=True, confirm_regenerate=confirm
        )
        confirm.assert_called_once_with(['Alpha', 'Gamma'])
        self.assertEqual([name for kind, name in calls if kind == 'api'], ['Alpha', 'Beta', 'Gamma'])

    def test_refused_regeneration_skips_only_the_existing_apis(self):
        confirm = mock.Mock(return_value=False)
        results, output, calls, _ = self.run_with(
            state=FakeState(generated=['Alpha']), backend=True, frontend=True, confirm_regenerate=confirm
        )
        self.assertEqual([name for kind, name in calls if kind == 'api'], ['Beta', 'Gamma'])
        self.assertIn('⏭️  Alpha : ignoré', output)
        self.assertEqual(exit_code_for(results), EXIT_OK)  # un modèle ignoré n'est pas un échec

    def test_refused_frontend_regeneration_skips_only_existing_interfaces(self):
        confirm_ui = mock.Mock(return_value=False)
        results, output, calls, _ = self.run_with(
            state=FakeState(frontends=['Alpha']),
            backend=False,
            frontend=True,
            confirm_regenerate_frontend=confirm_ui,
        )
        confirm_ui.assert_called_once_with(['Alpha'])
        self.assertEqual([name for kind, name in calls if kind == 'ui'], ['Beta', 'Gamma'])
        self.assertIn('Ignorés (interface', output)
        self.assertEqual(exit_code_for(results), EXIT_OK)

    def test_refused_frontend_regeneration_keeps_api_but_skips_ui(self):
        confirm_ui = mock.Mock(return_value=False)
        _, output, calls, _ = self.run_with(
            state=FakeState(frontends=['Beta']),
            backend=True,
            frontend=True,
            confirm_regenerate_frontend=confirm_ui,
        )
        self.assertIn(('api', 'Beta'), calls)
        self.assertNotIn(('ui', 'Beta'), calls)
        self.assertIn('Interface de Beta ignorée', output)

    def test_no_question_without_a_confirmation_callback(self):
        _, _, calls, _ = self.run_with(state=FakeState(generated=['Alpha']), backend=True)
        self.assertIn(('api', 'Alpha'), calls)  # mode non interactif : régénère sans demander

    def test_single_backend_model_prints_no_summary(self):
        with mock.patch.object(cli, 'generate_backend_for_model', return_value=EXIT_OK), \
                mock.patch.object(cli, 'sync_and_validate'):
            _, output = run_quiet(run_generation, FakeState(), [('zone_1', 'Alpha')], backend=True, frontend=False)
        self.assertNotIn('RÉSUMÉ', output)


class ExitCodeTests(SimpleTestCase):
    def test_highest_failure_code_wins(self):
        results = [
            {'backend': EXIT_OK, 'frontend': EXIT_OK},
            {'backend': EXIT_INVALID_SCHEMA, 'frontend': None},
            {'backend': EXIT_OK, 'frontend': EXIT_GENERATION_FAILED},
        ]
        self.assertEqual(exit_code_for(results), EXIT_GENERATION_FAILED)

    def test_ok_when_nothing_failed(self):
        self.assertEqual(exit_code_for([{'backend': EXIT_OK, 'frontend': None}]), EXIT_OK)
        self.assertEqual(exit_code_for([]), EXIT_OK)


class CommandLineTests(SimpleTestCase):
    def main_exit(self, *argv):
        with mock.patch('sys.argv', ['generate_api.py', *argv]), mock.patch.object(cli, 'run_generation') as run:
            with self.assertRaises(SystemExit) as raised:
                run_quiet(cli.main)
        return raised.exception.code, run

    def test_with_frontend_requires_generate(self):
        code, run = self.main_exit('--with-frontend')
        self.assertEqual(code, 2)
        run.assert_not_called()

    def test_empty_model_list_is_refused(self):
        code, run = self.main_exit('--generate', ' , ')
        self.assertEqual(code, 2)
        run.assert_not_called()
        code, run = self.main_exit('--frontend', ',')
        self.assertEqual(code, 2)

    def test_generate_accepts_several_models_and_the_interface_flag(self):
        results = [{'backend': EXIT_OK, 'frontend': EXIT_OK}]
        with mock.patch('sys.argv', ['generate_api.py', '--generate', 'Alpha,Beta', '--zone', 'zone_2', '--with-frontend']), \
                mock.patch.object(cli, 'scan_models_in_zones'), \
                mock.patch.object(cli.ImprovedStateManager, 'sync_with_filesystem'), \
                mock.patch.object(cli, 'run_generation', return_value=results) as run:
            with self.assertRaises(SystemExit) as raised:
                run_quiet(cli.main)
        self.assertEqual(raised.exception.code, EXIT_OK)
        _, targets = run.call_args.args[:2]
        self.assertEqual(targets, [('zone_2', 'Alpha'), ('zone_2', 'Beta')])
        self.assertEqual((run.call_args.kwargs['backend'], run.call_args.kwargs['frontend']), (True, True))

    def test_exit_code_reflects_a_failed_model(self):
        results = [{'backend': EXIT_GENERATION_FAILED, 'frontend': None}]
        with mock.patch('sys.argv', ['generate_api.py', '--frontend', 'Alpha']), \
                mock.patch.object(cli, 'run_generation', return_value=results) as run:
            with self.assertRaises(SystemExit) as raised:
                run_quiet(cli.main)
        self.assertEqual(raised.exception.code, EXIT_GENERATION_FAILED)
        self.assertEqual((run.call_args.kwargs['backend'], run.call_args.kwargs['frontend']), (False, True))
