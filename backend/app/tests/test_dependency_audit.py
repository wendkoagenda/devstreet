"""
Audit des dépendances : lecture des rapports pip-audit et npm audit, gravité qui bloque,
exceptions datées (validation, expiration, usage) et codes de sortie de la ligne de commande.
"""
import json
import tempfile
from datetime import date, timedelta
from pathlib import Path

from django.test import SimpleTestCase

from scripts.dependency_audit import audit, cli

TODAY = date(2026, 10, 18)

PIP_REPORT = {'dependencies': [
    {'name': 'django', 'version': '6.0.6', 'vulns': [
        {'id': 'PYSEC-2026-1', 'aliases': ['CVE-2026-1', 'GHSA-aaaa'], 'fix_versions': ['6.0.8']},
        {'id': 'PYSEC-2026-2', 'aliases': [], 'fix_versions': []},
    ]},
    {'name': 'requests', 'version': '2.0', 'vulns': []},
]}

NPM_REPORT = {'vulnerabilities': {
    'tar': {'name': 'tar', 'severity': 'critical', 'fixAvailable': True,
            'via': [{'source': 1, 'name': 'tar', 'url': 'https://github.com/advisories/GHSA-tar1', 'severity': 'critical'}]},
    'postcss': {'name': 'postcss', 'severity': 'moderate', 'fixAvailable': {'name': 'postcss', 'version': '8.5.30'},
                'via': [{'source': 2, 'name': 'postcss', 'url': 'https://github.com/advisories/GHSA-post', 'severity': 'moderate'}]},
    'micromatch': {'name': 'micromatch', 'severity': 'high', 'fixAvailable': False, 'via': ['braces']},
    'react-router': {'name': 'react-router', 'severity': 'high', 'fixAvailable': False,
                     'via': [{'source': 3, 'name': 'react-router', 'severity': 'high'}]},
}}


def write(directory, name, content):
    path = Path(directory) / name
    path.write_text(json.dumps(content), encoding='utf-8')
    return path


def exception(**overrides):
    values = {'id': 'GHSA-aaaa', 'package': 'django', 'reason': 'Correctif prévu dans la prochaine version',
              'author': 'wendkoagenda', 'expires': (TODAY + timedelta(days=30)).isoformat()}
    values.update(overrides)
    return values


class ParsingTests(SimpleTestCase):
    def test_pip_report_lists_each_vulnerability_with_its_aliases_and_fix(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = audit.parse_pip_audit(write(tmp, 'pip.json', PIP_REPORT))
        self.assertEqual(len(found), 2)
        self.assertEqual(found[0].ids, ('PYSEC-2026-1', 'CVE-2026-1', 'GHSA-aaaa'))
        self.assertEqual(found[0].fix, '6.0.8')
        self.assertEqual(found[1].fix, 'aucun correctif')
        self.assertTrue(all(v.blocking for v in found))  # pip-audit sans gravité : tout bloque

    def test_npm_blocks_only_high_and_critical(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = {v.package: v for v in audit.parse_npm_audit(write(tmp, 'npm.json', NPM_REPORT))}
        self.assertTrue(found['tar'].blocking)
        self.assertFalse(found['postcss'].blocking)
        self.assertEqual(found['postcss'].fix, 'postcss@8.5.30')
        self.assertEqual(found['tar'].ids, ('GHSA-tar1',))

    def test_npm_entries_derived_from_another_package_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = audit.parse_npm_audit(write(tmp, 'npm.json', NPM_REPORT))
        self.assertNotIn('micromatch', [v.package for v in found])

    def test_npm_advisory_without_url_falls_back_to_its_source_number(self):
        with tempfile.TemporaryDirectory() as tmp:
            found = {v.package: v for v in audit.parse_npm_audit(write(tmp, 'npm.json', NPM_REPORT))}
        self.assertEqual(found['react-router'].ids, ('3',))

    def test_unexpected_report_format_is_an_error_not_a_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            for parser, content in ((audit.parse_pip_audit, {'autre': 1}), (audit.parse_npm_audit, [])):
                with self.subTest(parser=parser.__name__), self.assertRaises(audit.ConfigError):
                    parser(write(tmp, 'r.json', content))

    def test_missing_or_invalid_report_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(audit.ConfigError):
                audit.parse_pip_audit(Path(tmp) / 'absent.json')
            bad = Path(tmp) / 'bad.json'
            bad.write_text('pas du json', encoding='utf-8')
            with self.assertRaises(audit.ConfigError):
                audit.parse_npm_audit(bad)


class ExceptionTests(SimpleTestCase):
    def load(self, *items):
        with tempfile.TemporaryDirectory() as tmp:
            return audit.load_exceptions(write(tmp, 'e.json', {'exceptions': list(items)}), TODAY)

    def test_missing_file_means_no_exception(self):
        self.assertEqual(audit.load_exceptions(Path('inexistant.json'), TODAY), [])

    def test_valid_exception_loads(self):
        self.assertEqual(self.load(exception())[0].id, 'GHSA-aaaa')

    def test_invalid_exceptions_are_refused(self):
        invalid = {
            'missing author': exception(author=''),
            'short reason': exception(reason='court'),
            'bad date': exception(expires='demain'),
            'too far': exception(expires=(TODAY + timedelta(days=181)).isoformat()),
        }
        for label, item in invalid.items():
            with self.subTest(label), self.assertRaises(audit.ConfigError):
                self.load(item)

    def test_exception_matches_by_alias_and_package(self):
        pip = self.parse_pip()
        result = audit.evaluate(pip, self.load(exception()), TODAY)
        self.assertIsNotNone(pip[0].excepted_by)
        self.assertIsNone(pip[1].excepted_by)
        self.assertEqual(len(result.blocking), 1)

    def test_exception_for_another_package_does_not_apply(self):
        pip = self.parse_pip()
        audit.evaluate(pip, self.load(exception(package='flask')), TODAY)
        self.assertIsNone(pip[0].excepted_by)

    def test_expired_exception_covers_nothing_and_fails_the_audit(self):
        pip = self.parse_pip()
        result = audit.evaluate(pip, self.load(exception(expires=(TODAY - timedelta(days=1)).isoformat())), TODAY)
        self.assertIsNone(pip[0].excepted_by)
        self.assertEqual(len(result.expired), 1)
        self.assertTrue(result.failed)

    def test_unused_exception_is_reported_but_does_not_fail(self):
        result = audit.evaluate([], self.load(exception()), TODAY)
        self.assertEqual(len(result.unused), 1)
        self.assertFalse(result.failed)

    def test_everything_excepted_passes(self):
        pip = self.parse_pip()
        result = audit.evaluate(pip, self.load(exception(), exception(id='PYSEC-2026-2')), TODAY)
        self.assertFalse(result.failed)

    def parse_pip(self):
        with tempfile.TemporaryDirectory() as tmp:
            return audit.parse_pip_audit(write(tmp, 'pip.json', PIP_REPORT))


class ReportAndCliTests(SimpleTestCase):
    def run_cli(self, *args, pip=PIP_REPORT, npm=None, exceptions=None):
        with tempfile.TemporaryDirectory() as tmp:
            argv = ['--exceptions', str(write(tmp, 'e.json', {'exceptions': exceptions or []}))]
            if pip is not None:
                argv += ['--pip', str(write(tmp, 'pip.json', pip))]
            if npm is not None:
                argv += ['--npm', str(write(tmp, 'npm.json', npm))]
            return cli.main([*argv, *args])

    def test_blocking_vulnerability_gives_exit_1(self):
        self.assertEqual(self.run_cli(), 1)

    def test_clean_reports_give_exit_0(self):
        self.assertEqual(self.run_cli(pip={'dependencies': []}, npm={'vulnerabilities': {}}), 0)

    def test_non_blocking_npm_severity_gives_exit_0(self):
        npm = {'vulnerabilities': {'postcss': NPM_REPORT['vulnerabilities']['postcss']}}
        self.assertEqual(self.run_cli(pip=None, npm=npm), 0)

    def test_no_report_given_is_a_usage_error(self):
        self.assertEqual(self.run_cli(pip=None), 2)

    def test_invalid_exceptions_file_gives_exit_2(self):
        self.assertEqual(self.run_cli(exceptions=[{'id': 'x'}]), 2)

    def test_markdown_report_lists_blocking_items_and_the_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            pip = write(tmp, 'pip.json', PIP_REPORT)
            vulns = audit.parse_pip_audit(pip)
        text = audit.render(audit.evaluate(vulns, [], TODAY), markdown=True)
        for expected in ('## Audit des dépendances', 'Bloquantes', 'django 6.0.6', 'PYSEC-2026-1', '6.0.8', 'ÉCHEC'):
            self.assertIn(expected, text)

    def test_committed_exceptions_file_is_valid(self):
        repo_root = Path(__file__).resolve().parents[3]
        audit.load_exceptions(repo_root / audit.EXCEPTIONS_FILE)
