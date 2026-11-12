"""
Contrôle de non-régression : motifs de chemins, lecture du diff, rapprochement avec les zones,
configuration refusée si elle protège le vide, et fonctionnement de bout en bout sur un vrai dépôt Git.
"""
import json
import subprocess
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from scripts.regression_guard import cli, config, engine, report
from scripts.regression_guard.engine import Change
from scripts.regression_guard.matcher import matches

REPO_ROOT = Path(__file__).resolve().parents[3]


def make_zone(**overrides):
    values = dict(name='auth', reason='Connexion et jetons de session', paths=['backend/app/core/auth.py', 'frontend/src/auth/**'],
                  tests=['backend/app/tests/test_auth.py'], verify='Relancer test_auth et tester la connexion', owners=[])
    values.update(overrides)
    return config.Zone(**values)


class PatternTests(SimpleTestCase):
    def test_exact_path(self):
        self.assertTrue(matches('backend/config/settings.py', 'backend/config/settings.py'))
        self.assertFalse(matches('backend/config/settings.py', 'backend/config/settings.pyc'))

    def test_single_star_stays_in_one_folder(self):
        self.assertTrue(matches('backend/app/*/migrations/**', 'backend/app/core/migrations/0001_initial.py'))
        self.assertFalse(matches('backend/app/*/migrations/**', 'backend/app/core/sub/migrations/0001.py'))

    def test_double_star_crosses_folders(self):
        self.assertTrue(matches('frontend/src/models/auth/**', 'frontend/src/models/auth/a/b/c.ts'))
        self.assertFalse(matches('frontend/src/models/auth/**', 'frontend/src/models/user/a.ts'))

    def test_double_star_slash_accepts_zero_folder(self):
        self.assertTrue(matches('frontend/src/models/auth/**/*.test.ts', 'frontend/src/models/auth/x.test.ts'))
        self.assertTrue(matches('frontend/src/models/auth/**/*.test.ts', 'frontend/src/models/auth/pages/x.test.ts'))

    def test_trailing_slash_means_whole_folder(self):
        self.assertTrue(matches('git-cli/', 'git-cli/commit.py'))
        self.assertTrue(matches('git-cli/', 'git-cli/sub/x.py'))
        self.assertFalse(matches('git-cli/', 'git-cli-other/x.py'))

    def test_special_regex_characters_are_literal(self):
        self.assertTrue(matches('a+b(1).py', 'a+b(1).py'))
        self.assertFalse(matches('a.py', 'abpy'))


class DiffParsingTests(SimpleTestCase):
    def test_parses_each_kind_of_change(self):
        output = 'M\ta.py\nA\tb.py\nD\tc.py\nR087\told.py\tnew.py\nT\td.py\nC100\tsrc.py\tcopy.py\n'
        changes = engine.parse_name_status(output)
        self.assertEqual(changes, [
            Change('a.py', 'M'), Change('b.py', 'A'), Change('c.py', 'D'),
            Change('new.py', 'R', 'old.py'), Change('d.py', 'M'), Change('copy.py', 'A'),
        ])

    def test_unreadable_line_is_an_error_not_silence(self):
        with self.assertRaises(config.ConfigError):
            engine.parse_name_status('n importe quoi')


class AnalysisTests(SimpleTestCase):
    def test_untouched_zone_is_not_reported(self):
        self.assertEqual(engine.analyze([make_zone()], [Change('README.md', 'M')]), [])

    def test_modified_file_touches_its_zone(self):
        hits = engine.analyze([make_zone()], [Change('backend/app/core/auth.py', 'M')])
        self.assertEqual([h.zone.name for h in hits], ['auth'])
        self.assertFalse(hits[0].tests_touched)

    def test_deletion_and_addition_count(self):
        hits = engine.analyze([make_zone()], [Change('frontend/src/auth/new.ts', 'A'), Change('frontend/src/auth/old.ts', 'D')])
        self.assertEqual(len(hits[0].changes), 2)

    def test_rename_out_of_a_zone_is_still_reported(self):
        hits = engine.analyze([make_zone()], [Change('elsewhere/auth.py', 'R', 'backend/app/core/auth.py')])
        self.assertEqual(len(hits), 1)

    def test_rename_into_a_zone_is_reported(self):
        hits = engine.analyze([make_zone()], [Change('backend/app/core/auth.py', 'R', 'tmp/auth.py')])
        self.assertEqual(len(hits), 1)

    def test_one_file_can_touch_several_zones(self):
        zones = [make_zone(), make_zone(name='autre', paths=['backend/app/core/**'], tests=[])]
        hits = engine.analyze(zones, [Change('backend/app/core/auth.py', 'M')])
        self.assertEqual({h.zone.name for h in hits}, {'auth', 'autre'})

    def test_modified_test_alone_does_not_touch_the_zone(self):
        self.assertEqual(engine.analyze([make_zone()], [Change('backend/app/tests/test_auth.py', 'M')]), [])

    def test_deleted_test_touches_the_zone(self):
        hits = engine.analyze([make_zone()], [Change('backend/app/tests/test_auth.py', 'D')])
        self.assertEqual(len(hits), 1)

    def test_code_with_its_test_marks_tests_as_touched(self):
        hits = engine.analyze([make_zone()], [Change('backend/app/core/auth.py', 'M'), Change('backend/app/tests/test_auth.py', 'M')])
        self.assertTrue(hits[0].tests_touched)
        self.assertFalse(report.tests_warning(hits[0]))

    def test_warning_when_code_changes_without_its_tests(self):
        hits = engine.analyze([make_zone()], [Change('backend/app/core/auth.py', 'M')])
        self.assertTrue(report.tests_warning(hits[0]))

    def test_no_warning_for_a_zone_without_declared_tests(self):
        hits = engine.analyze([make_zone(tests=[])], [Change('backend/app/core/auth.py', 'M')])
        self.assertFalse(report.tests_warning(hits[0]))


class ReportTests(SimpleTestCase):
    def hits(self, count=1):
        changes = [Change(f'frontend/src/auth/f{i}.ts', 'M') for i in range(count)]
        return engine.analyze([make_zone(owners=['alice'])], changes)

    def test_default_and_zone_owners_are_merged_without_duplicates(self):
        owners = report.owners_of(self.hits()[0], ['wendkoagenda', 'alice'])
        self.assertEqual(owners, ['alice', 'wendkoagenda'])

    def test_markdown_has_marker_zone_reason_check_and_mentions(self):
        text = report.render_markdown(self.hits(), ['wendkoagenda'])
        for expected in (report.COMMENT_MARKER, '`auth`', 'Connexion et jetons de session', 'Relancer test_auth', '@alice', '@wendkoagenda',
                         'aucun test de la zone modifié', 'Validé par un responsable ? :** Non'):
            self.assertIn(expected, text)

    def test_markdown_when_approved_says_so(self):
        text = report.render_markdown(self.hits(), ['wendkoagenda'], approved=True)
        self.assertIn('Validé par un responsable ? :** Oui', text)
        self.assertNotIn('** Non', text)

    def test_markdown_without_hit_keeps_the_marker_to_update_the_comment(self):
        text = report.render_markdown([], ['wendkoagenda'])
        self.assertIn(report.COMMENT_MARKER, text)
        self.assertIn('Aucune zone protégée touchée', text)

    def test_markdown_truncates_long_file_lists(self):
        text = report.render_markdown(self.hits(report.MAX_FILES_SHOWN + 5), ['wendkoagenda'])
        self.assertIn('… et 5 autre(s) fichier(s)', text)

    def test_json_is_machine_readable(self):
        data = json.loads(report.render_json(self.hits(), ['wendkoagenda']))
        self.assertTrue(data['touched'])
        self.assertEqual(data['zones'][0]['name'], 'auth')
        self.assertTrue(data['zones'][0]['tests_missing'])


class ConfigTests(SimpleTestCase):
    def write(self, directory, content):
        path = Path(directory) / 'regression-guard.json'
        path.write_text(json.dumps(content), encoding='utf-8')
        return path

    def zone(self, **overrides):
        values = {'name': 'auth', 'reason': 'Connexion et jetons de session', 'paths': ['a/**'], 'verify': 'Relancer les tests de la zone'}
        values.update(overrides)
        return values

    def test_valid_file_loads(self):
        with tempfile.TemporaryDirectory() as tmp:
            zones = config.load(self.write(tmp, {'zones': [self.zone(owners=['alice'])]}))
        self.assertEqual(zones[0].owners, ['alice'])
        self.assertEqual(zones[0].tests, [])

    def test_missing_file_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(config.ConfigError):
            config.load(Path(tmp) / 'regression-guard.json')

    def test_invalid_zones_are_refused(self):
        invalid = {
            'no zone': {'zones': []},
            'bad name': {'zones': [self.zone(name='Mauvais Nom')]},
            'short reason': {'zones': [self.zone(reason='court')]},
            'no verify': {'zones': [self.zone(verify='')]},
            'no path': {'zones': [self.zone(paths=[])]},
            'absolute path': {'zones': [self.zone(paths=['/etc/passwd'])]},
            'windows path': {'zones': [self.zone(paths=['a\\b'])]},
            'duplicate': {'zones': [self.zone(), self.zone()]},
        }
        for label, content in invalid.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as tmp, self.assertRaises(config.ConfigError):
                config.load(self.write(tmp, content))

    def test_pattern_matching_nothing_is_refused(self):
        zone = make_zone(paths=['dossier/disparu/**'])
        with self.assertRaises(config.ConfigError) as caught:
            config.check_patterns_exist([zone], ['autre/fichier.py'])
        self.assertIn('dossier/disparu/**', str(caught.exception))

    def test_test_pattern_matching_nothing_is_refused(self):
        zone = make_zone(paths=['a.py'], tests=['tests/disparu.py'])
        with self.assertRaises(config.ConfigError):
            config.check_patterns_exist([zone], ['a.py'])

    def test_master_users_come_from_access_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'access_control.conf'
            path.write_text('# ZONE_PROTEGEE_USERS="commentaire"\nGIT_MASTER_USERS="carol"\nZONE_PROTEGEE_USERS="alice, bob"\n', encoding='utf-8')
            self.assertEqual(config.master_users(path), ['alice', 'bob'])

    def test_missing_or_empty_masters_are_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'access_control.conf'
            with self.assertRaises(config.ConfigError):
                config.master_users(path)
            path.write_text('GIT_MASTER_USERS="carol"\nZONE_PROTEGEE_USERS=""\n', encoding='utf-8')
            with self.assertRaises(config.ConfigError):
                config.master_users(path)


class RepositoryConfigurationTests(SimpleTestCase):
    """Le vrai regression-guard.json du dépôt est valide et ne protège pas le vide."""

    def test_repository_zones_are_valid_and_match_real_files(self):
        zones = config.load(REPO_ROOT / config.GUARD_FILE)
        config.check_patterns_exist(zones, engine.tracked_files(REPO_ROOT))
        self.assertTrue(config.master_users(REPO_ROOT / config.ACCESS_CONTROL_FILE))

    def test_the_guard_protects_itself(self):
        zones = config.load(REPO_ROOT / config.GUARD_FILE)
        hits = engine.analyze(zones, [Change('regression-guard.json', 'M')])
        self.assertEqual([h.zone.name for h in hits], ['regression-guard'])


class GitIntegrationTests(SimpleTestCase):
    """Bout en bout sur un vrai dépôt Git temporaire."""

    def git(self, *args):
        subprocess.run(['git', '-c', 'user.name=test', '-c', 'user.email=test@example.com', '-c', 'commit.gpgsign=false', *args],
                       cwd=self.root, check=True, capture_output=True, text=True)

    def commit(self, message):
        self.git('add', '-A')
        self.git('commit', '-m', message)

    def put(self, relative, content='x\n'):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.git('init', '-b', 'develop')
        self.put('regression-guard.json', json.dumps({'zones': [{
            'name': 'auth', 'reason': 'Connexion et jetons de session', 'paths': ['backend/auth.py'],
            'tests': ['backend/test_auth.py'], 'verify': 'Relancer test_auth et tester la connexion'}]}))
        self.put('git-cli/access_control.conf', 'ZONE_PROTEGEE_USERS="wendkoagenda"\n')
        self.put('backend/auth.py')
        self.put('backend/test_auth.py')
        self.put('backend/autre.py')
        self.commit('base')
        self.git('checkout', '-b', 'feature')

    def run_cli(self, *extra):
        return cli.main(['--root', str(self.root), '--base', 'develop', *extra])

    def test_no_change_means_exit_0(self):
        self.assertEqual(self.run_cli(), 0)

    def test_change_outside_a_zone_means_exit_0(self):
        self.put('backend/autre.py', 'y\n')
        self.commit('autre')
        self.assertEqual(self.run_cli(), 0)

    def test_change_inside_a_zone_means_exit_1_and_writes_github_output(self):
        self.put('backend/auth.py', 'y\n')
        self.commit('auth')
        output = self.root / 'github_output.txt'
        self.assertEqual(self.run_cli('--github-output', str(output)), 1)
        self.assertEqual(output.read_text(encoding='utf-8'), 'touched=true\nzones=auth\n')

    def test_output_file_receives_the_markdown_report(self):
        self.put('backend/auth.py', 'y\n')
        self.commit('auth')
        target = self.root / 'rapport.md'
        self.run_cli('--format', 'markdown', '--output', str(target))
        text = target.read_text(encoding='utf-8')
        self.assertIn(report.COMMENT_MARKER, text)
        self.assertIn('@wendkoagenda', text)

    def test_changes_already_on_the_base_are_not_attributed_to_the_branch(self):
        self.git('checkout', 'develop')
        self.put('backend/auth.py', 'arrive sur develop\n')
        self.commit('develop avance')
        self.git('checkout', 'feature')
        self.put('backend/autre.py', 'y\n')
        self.commit('feature')
        self.assertEqual(self.run_cli(), 0)  # trois points : seulement le travail de la branche
        self.assertEqual(self.run_cli('--two-dot'), 1)  # deux points : comparaison directe des commits

    def test_deleted_protected_file_is_reported(self):
        (self.root / 'backend' / 'auth.py').unlink()
        self.commit('suppression')
        self.assertEqual(self.run_cli(), 1)

    def test_first_push_of_a_branch_compares_with_the_empty_tree(self):
        changes = engine.git_changes(self.root, '0' * 40, 'HEAD')
        self.assertIn(Change('backend/auth.py', 'A'), changes)

    def test_unknown_reference_is_a_configuration_error(self):
        self.assertEqual(cli.main(['--root', str(self.root), '--base', 'branche-inconnue']), 2)

    def test_rules_come_from_the_trusted_config_root(self):
        """Une PR qui réécrit regression-guard.json ne peut pas masquer ses propres changements."""
        trusted = Path(self._tmp.name) / 'trusted'
        (trusted / 'git-cli').mkdir(parents=True)
        (trusted / 'regression-guard.json').write_text((self.root / 'regression-guard.json').read_text(encoding='utf-8'), encoding='utf-8')
        (trusted / 'git-cli' / 'access_control.conf').write_text('ZONE_PROTEGEE_USERS="wendkoagenda"\n', encoding='utf-8')
        self.put('regression-guard.json', json.dumps({'zones': [{
            'name': 'autre', 'reason': 'Zone qui ne couvre plus le fichier', 'paths': ['backend/autre.py'],
            'verify': 'Relancer les tests de la zone'}]}))
        self.put('backend/auth.py', 'y\n')
        self.commit('la PR réécrit les règles')
        self.assertEqual(self.run_cli(), 0)  # avec ses propres règles, la PR passe inaperçue
        self.assertEqual(self.run_cli('--config-root', str(trusted)), 1)  # avec les règles de confiance, elle est vue

    def test_json_report_lists_the_masters_for_the_approval_check(self):
        self.put('backend/auth.py', 'y\n')
        self.commit('auth')
        target = self.root / 'rapport.json'
        self.run_cli('--format', 'json', '--output', str(target))
        data = json.loads(target.read_text(encoding='utf-8'))
        self.assertEqual(data['masters'], ['wendkoagenda'])
        self.assertEqual(data['zones'][0]['name'], 'auth')

    def test_stale_pattern_in_the_file_is_a_configuration_error(self):
        self.put('regression-guard.json', json.dumps({'zones': [{
            'name': 'auth', 'reason': 'Connexion et jetons de session', 'paths': ['backend/disparu.py'],
            'verify': 'Relancer test_auth et tester la connexion'}]}))
        self.commit('motif obsolète')
        self.assertEqual(self.run_cli(), 2)
