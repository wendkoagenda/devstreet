"""Tests de la liste de référence du déploiement (scripts/deploy_env)."""
import json
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from scripts.deploy_env import render, spec, verifier

BACKEND_EXAMPLE = """\
# Prose avec NOM=valeur au milieu d'une ligne : ignorée
DEBUG=True
SECRET_KEY=            # @secret
DB_PASSWORD=postgres   # @secret
# EMAIL_HOST=smtp.exemple.com
# EMAIL_HOST_PASSWORD=   # @secret
"""
FRONTEND_EXAMPLE = """\
VITE_API_URL=/api
# VITE_GCS_BUCKET_NAME=
"""


def faire_depot(backend=BACKEND_EXAMPLE, frontend=FRONTEND_EXAMPLE):
    racine = Path(tempfile.mkdtemp())
    for dossier, contenu in (('backend', backend), ('frontend', frontend)):
        (racine / dossier).mkdir()
        (racine / dossier / '.env.example').write_text(contenu, encoding='utf-8')
    return racine


class ParseExampleTests(SimpleTestCase):
    def test_distingue_obligatoire_facultative_et_secret(self):
        variables = {v.name: v for v in spec.parse_example(BACKEND_EXAMPLE, 'backend')}
        self.assertEqual(set(variables), {'DEBUG', 'SECRET_KEY', 'DB_PASSWORD', 'EMAIL_HOST', 'EMAIL_HOST_PASSWORD'})
        self.assertTrue(variables['DEBUG'].required and not variables['DEBUG'].secret)
        self.assertTrue(variables['SECRET_KEY'].required and variables['SECRET_KEY'].secret)
        self.assertFalse(variables['EMAIL_HOST'].required)
        self.assertTrue(not variables['EMAIL_HOST_PASSWORD'].required and variables['EMAIL_HOST_PASSWORD'].secret)

    def test_refuse_un_secret_dans_le_frontend(self):
        with self.assertRaises(spec.SpecError):
            spec.parse_example('VITE_TOKEN=   # @secret\n', 'frontend')

    def test_refuse_un_nom_declare_deux_fois(self):
        with self.assertRaises(spec.SpecError):
            spec.parse_example('A=1\n# A=2\n', 'backend')

    def test_les_exemples_reels_sont_lisibles(self):
        racine = Path(__file__).resolve().parents[3]
        noms = {v.name for v in spec.load_spec(racine)}
        # Garde-fou : ces noms sont exigés par backend/entrypoint.sh
        for requis in ('SECRET_KEY', 'JWT_SIGNING_KEY', 'DB_PASSWORD', 'ALLOWED_HOSTS', 'VITE_API_URL'):
            self.assertIn(requis, noms)
        secrets = {v.name for v in spec.load_spec(racine) if v.secret}
        self.assertTrue({'SECRET_KEY', 'JWT_SIGNING_KEY', 'DB_PASSWORD', 'ADMIN_PASSWORD'} <= secrets)


class NommageTests(SimpleTestCase):
    def test_nom_simple_dans_l_environnement_de_la_branche(self):
        self.assertEqual(spec.gh_name('SECRET_KEY', 'prod'), 'SECRET_KEY')

    def test_refuse_une_branche_inconnue(self):
        with self.assertRaises(spec.SpecError):
            spec.gh_name('SECRET_KEY', 'feature-x')


class FichiersLocauxTests(SimpleTestCase):
    def test_parse_dotenv_garde_les_diese_dans_les_valeurs(self):
        valeurs = spec.parse_dotenv('# commentaire\n\nexport A="x#y"\nB=\'z\'\nC=a=b\n')
        self.assertEqual(valeurs, {'A': 'x#y', 'B': 'z', 'C': 'a=b'})

    def test_parse_dotenv_refuse_une_ligne_invalide(self):
        with self.assertRaises(spec.SpecError):
            spec.parse_dotenv('pas une affectation\n')

    def test_check_values_signale_inconnu_vide_et_manquant(self):
        definitions = spec.load_spec(faire_depot())
        erreurs = spec.check_values(definitions, 'backend', {'DEBUG': 'False', 'SECRET_KEY': '', 'INCONNU': '1'})
        texte = '\n'.join(erreurs)
        self.assertIn('INCONNU', texte)
        self.assertIn('SECRET_KEY : valeur obligatoire vide', texte)
        self.assertIn('DB_PASSWORD : variable obligatoire manquante', texte)
        self.assertNotIn('EMAIL_HOST', texte)

    def test_check_values_refuse_les_valeurs_de_deploiement_invalides(self):
        definitions = spec.load_spec(faire_depot())
        valeurs = {
            'DEPLOY_NAMESPACE': 'Mauvais Nom', 'DEPLOY_DOMAIN': 'https://exemple.fr/', 'DEPLOY_LETSENCRYPT_EMAIL': 'x',
            'DEPLOY_ACCES': 'telnet', 'DEPLOY_DB_MODE': 'interne',
        }
        erreurs = '\n'.join(spec.check_values(definitions, 'deploy', valeurs))
        for nom in ('DEPLOY_NAMESPACE', 'DEPLOY_DOMAIN', 'DEPLOY_LETSENCRYPT_EMAIL', 'DEPLOY_ACCES'):
            self.assertIn(nom, erreurs)
        self.assertNotIn('DEPLOY_DB_MODE', erreurs)

    def test_les_acces_ssh_ne_se_definissent_pas_a_la_main(self):
        definitions = spec.load_spec(faire_depot())
        erreurs = spec.check_values(definitions, 'deploy', {'VM_SSH_PRIVATE_KEY': 'x'})
        self.assertTrue(any('preparer-vm' in e for e in erreurs))


class EnvironnementTests(SimpleTestCase):
    def setUp(self):
        self.definitions = spec.load_spec(faire_depot())

    def complet(self):
        secrets = {'SECRET_KEY', 'DB_PASSWORD', 'VM_SSH_HOST', 'VM_SSH_USER', 'VM_SSH_PRIVATE_KEY'}
        variables = {
            'DEBUG', 'VITE_API_URL', 'VM_SSH_KNOWN_HOSTS', 'DEPLOY_NAMESPACE',
            'DEPLOY_DOMAIN', 'DEPLOY_LETSENCRYPT_EMAIL', 'DEPLOY_ACCES', 'DEPLOY_DB_MODE',
        }
        return secrets, variables

    def test_environnement_complet(self):
        secrets, variables = self.complet()
        self.assertEqual(spec.check_environment(self.definitions, 'prod', secrets, variables, 'ssh'), [])

    def test_signale_un_secret_enregistre_comme_variable(self):
        secrets, variables = self.complet()
        secrets.remove('DB_PASSWORD')
        variables.add('DB_PASSWORD')
        erreurs = spec.check_environment(self.definitions, 'prod', secrets, variables, 'ssh')
        self.assertEqual(len(erreurs), 1)
        self.assertIn('lisible par tous', erreurs[0])

    def test_noms_insensibles_a_la_casse(self):
        secrets, variables = self.complet()
        secrets = {nom.lower() for nom in secrets}
        self.assertEqual(spec.check_environment(self.definitions, 'prod', secrets, variables, 'ssh'), [])

    def test_names_from_json_ignore_les_valeurs_vides_et_ne_garde_pas_les_valeurs(self):
        noms = spec.names_from_json(json.dumps({'A': 'secret-a', 'B': '', 'github_token': 'ghs_x'}))
        self.assertEqual(noms, {'A', 'github_token'})


class VerifierTests(SimpleTestCase):
    def test_code_de_sortie_et_aucune_valeur_dans_la_sortie(self):
        racine = faire_depot()
        environ = {'BRANCHE': 'prod', 'SECRETS_JSON': json.dumps({'SECRET_KEY': 'valeur-tres-secrete'}), 'VARS_JSON': '{}'}
        from io import StringIO
        from contextlib import redirect_stdout
        sortie = StringIO()
        with redirect_stdout(sortie):
            code = verifier.main(environ=environ, repo_root=racine)
        self.assertEqual(code, 1)
        self.assertIn('DB_PASSWORD : manquant', sortie.getvalue())
        self.assertNotIn('valeur-tres-secrete', sortie.getvalue())

    def test_entree_invalide(self):
        self.assertEqual(verifier.main(environ={'BRANCHE': 'inconnue'}, repo_root=faire_depot()), 2)


class RenduTests(SimpleTestCase):
    SHA = 'a' * 40
    IMAGES = {
        'BACKEND_IMAGE': 'ghcr.io/wendkoagenda/depot-backend:' + 'a' * 40,
        'FRONTEND_IMAGE': 'ghcr.io/wendkoagenda/depot-frontend:prod-' + 'a' * 40 + '-1234abcd',
    }

    def setUp(self):
        backend = BACKEND_EXAMPLE + 'DB_NAME=x\nDB_USER=x\nDB_HOST=x\nALLOWED_HOSTS=x\n'
        self.definitions = spec.load_spec(faire_depot(backend=backend))
        self.secrets = {'SECRET_KEY': 's3cr3t', 'DB_PASSWORD': 'p$ss#1'}
        self.variables = {
            'DEBUG': 'False', 'DB_NAME': 'bd', 'DB_USER': 'u', 'DB_HOST': 'db',
            'ALLOWED_HOSTS': 'app.exemple.fr,localhost', 'DEPLOY_NAMESPACE': 'devstreet-prod',
            'DEPLOY_DOMAIN': 'app.exemple.fr', 'DEPLOY_LETSENCRYPT_EMAIL': 'ops@exemple.fr',
            'DEPLOY_ACCES': 'ssh', 'DEPLOY_DB_MODE': 'interne',
        }

    def rendre(self, **changements):
        variables = {**self.variables, **changements.pop('variables', {})}
        secrets = {**self.secrets, **changements.pop('secrets', {})}
        return render.render(self.definitions, 'prod', secrets, variables, self.IMAGES, self.SHA)

    def test_ecrit_les_valeurs_entre_apostrophes(self):
        fichiers, erreurs = self.rendre()
        self.assertEqual(erreurs, [])
        self.assertIn("SECRET_KEY='s3cr3t'\n", fichiers['backend.env'])
        self.assertIn("DB_PASSWORD='p$ss#1'\n", fichiers['backend.env'])
        self.assertNotIn('DEPLOY_', fichiers['backend.env'])
        self.assertIn("DEPLOY_NAMESPACE='devstreet-prod'\n", fichiers['compose.env'])
        self.assertIn("DB_PASSWORD='p$ss#1'\n", fichiers['compose.env'])
        self.assertIn(f"DEPLOY_SHA='{self.SHA}'\n", fichiers['compose.env'])

    def test_les_valeurs_facultatives_absentes_sont_omises(self):
        fichiers, _ = self.rendre()
        self.assertNotIn('EMAIL_HOST', fichiers['backend.env'])

    def test_refuse_une_valeur_manquante(self):
        _, erreurs = self.rendre(secrets={'SECRET_KEY': ''})
        self.assertEqual(erreurs, ['SECRET_KEY : manquant.'])

    def test_refuse_une_apostrophe_ou_un_retour_a_la_ligne(self):
        for valeur in ("a'b", 'a\nb'):
            _, erreurs = self.rendre(secrets={'SECRET_KEY': valeur})
            self.assertEqual(len(erreurs), 1, valeur)
            self.assertIn('SECRET_KEY', erreurs[0])

    def test_base_interne_impose_db_host_db(self):
        _, erreurs = self.rendre(variables={'DB_HOST': 'base.exemple.fr'})
        self.assertTrue(any('DB_HOST' in e for e in erreurs))
        _, erreurs = self.rendre(variables={'DB_HOST': 'base.exemple.fr', 'DEPLOY_DB_MODE': 'externe'})
        self.assertEqual(erreurs, [])

    def test_le_domaine_doit_etre_dans_allowed_hosts(self):
        _, erreurs = self.rendre(variables={'ALLOWED_HOSTS': 'autre.exemple.fr'})
        self.assertTrue(any('ALLOWED_HOSTS' in e for e in erreurs))

    def test_host_allowed_suit_les_regles_de_django(self):
        self.assertTrue(render.host_allowed('app.exemple.fr', '.exemple.fr'))
        self.assertTrue(render.host_allowed('exemple.fr', '.exemple.fr'))
        self.assertTrue(render.host_allowed('app.exemple.fr', 'x, *'))
        self.assertFalse(render.host_allowed('app.exemple.fr', 'exemple.fr'))
        self.assertFalse(render.host_allowed('evilexemple.fr', '.exemple.fr'))

    def test_refuse_une_image_ou_un_commit_invalide(self):
        images = {**self.IMAGES, 'BACKEND_IMAGE': 'docker.io/x/y:1'}
        _, erreurs = render.render(self.definitions, 'prod', self.secrets, self.variables, images, self.SHA)
        self.assertTrue(any('images' in e for e in erreurs))
        _, erreurs = render.render(self.definitions, 'prod', self.secrets, self.variables, self.IMAGES, 'abc')
        self.assertTrue(any('DEPLOY_SHA' in e for e in erreurs))

    def test_mode_gcp_exige_les_valeurs_gcp_qui_ne_vont_pas_sur_la_vm(self):
        _, erreurs = self.rendre(variables={'DEPLOY_ACCES': 'gcp'})
        self.assertEqual(len(erreurs), 5)
        gcp = {
            'GCP_PROJECT_ID': 'mon-projet-123', 'GCP_ZONE': 'europe-west1-b', 'GCP_INSTANCE': 'vm-prod',
            'GCP_WIF_PROVIDER': 'projects/1/locations/global/workloadIdentityPools/p/providers/q',
            'GCP_SERVICE_ACCOUNT': 'deploy@mon-projet-123.iam.gserviceaccount.com',
        }
        fichiers, erreurs = self.rendre(variables={'DEPLOY_ACCES': 'gcp', **gcp})
        self.assertEqual(erreurs, [])
        self.assertNotIn('GCP_', fichiers['compose.env'] + fichiers['backend.env'])

    def test_ecriture_via_la_ligne_de_commande_sans_afficher_de_valeur(self):
        import os
        from io import StringIO
        from contextlib import redirect_stdout
        racine = faire_depot(backend=BACKEND_EXAMPLE + 'DB_NAME=x\nDB_USER=x\nDB_HOST=x\nALLOWED_HOSTS=x\n')
        sortie_dossier = Path(tempfile.mkdtemp()) / 'rendu'
        environ = {
            'BRANCHE': 'prod', 'SECRETS_JSON': json.dumps(self.secrets), 'VARS_JSON': json.dumps(self.variables),
            'DEPLOY_SHA': self.SHA, **self.IMAGES,
        }
        affichage = StringIO()
        with redirect_stdout(affichage):
            code = render.main(['--sortie', str(sortie_dossier)], environ=environ, repo_root=racine)
        self.assertEqual(code, 0)
        self.assertNotIn('s3cr3t', affichage.getvalue())
        self.assertIn("SECRET_KEY='s3cr3t'", (sortie_dossier / 'backend.env').read_text(encoding='utf-8'))
        if os.name != 'nt':
            self.assertEqual((sortie_dossier / 'backend.env').stat().st_mode & 0o777, 0o600)


class ModeGcpTests(SimpleTestCase):
    GCP = {
        'GCP_PROJECT_ID': 'mon-projet-123', 'GCP_ZONE': 'europe-west1-b', 'GCP_INSTANCE': 'vm-prod',
        'GCP_WIF_PROVIDER': 'projects/123456789/locations/global/workloadIdentityPools/github/providers/depot',
        'GCP_SERVICE_ACCOUNT': 'deploy@mon-projet-123.iam.gserviceaccount.com',
    }
    DEPLOY = {
        'DEPLOY_NAMESPACE': 'devstreet-prod', 'DEPLOY_DOMAIN': 'app.exemple.fr',
        'DEPLOY_LETSENCRYPT_EMAIL': 'ops@exemple.fr', 'DEPLOY_DB_MODE': 'interne',
    }

    def setUp(self):
        self.definitions = spec.load_spec(faire_depot())

    def test_les_valeurs_gcp_ne_sont_exigees_qu_en_mode_gcp(self):
        ssh = spec.check_values(self.definitions, 'deploy', {**self.DEPLOY, 'DEPLOY_ACCES': 'ssh'})
        self.assertEqual(ssh, [])
        gcp = '\n'.join(spec.check_values(self.definitions, 'deploy', {**self.DEPLOY, 'DEPLOY_ACCES': 'gcp'}))
        for nom in self.GCP:
            self.assertIn(f'{nom} : variable obligatoire manquante', gcp)
        complet = spec.check_values(self.definitions, 'deploy', {**self.DEPLOY, **self.GCP, 'DEPLOY_ACCES': 'gcp'})
        self.assertEqual(complet, [])

    def test_refuse_des_valeurs_gcp_mal_formees(self):
        for nom, valeur in (
            ('GCP_PROJECT_ID', 'X; rm -rf /'), ('GCP_ZONE', 'europe'), ('GCP_INSTANCE', 'vm prod'),
            ('GCP_WIF_PROVIDER', 'projects/abc/locations/global'), ('GCP_SERVICE_ACCOUNT', 'moi@gmail.com'),
        ):
            self.assertIsNotNone(spec.validate_value(nom, valeur), nom)

    def test_environnement_gcp_n_exige_pas_les_acces_ssh(self):
        variables = {f'{nom}' for nom in self.GCP} | {f'{nom}' for nom in self.DEPLOY} | {
            'DEPLOY_ACCES', 'DEBUG', 'VITE_API_URL',
        }
        secrets = {'SECRET_KEY', 'DB_PASSWORD'}
        self.assertEqual(spec.check_environment(self.definitions, 'prod', secrets, variables, 'gcp'), [])
        erreurs = spec.check_environment(self.definitions, 'prod', secrets, variables, 'ssh')
        self.assertTrue(any('VM_SSH_PRIVATE_KEY' in e for e in erreurs))

    def test_json_value_est_insensible_a_la_casse(self):
        self.assertEqual(spec.json_value('{"deploy_acces": "gcp"}', 'DEPLOY_ACCES'), 'gcp')
        self.assertEqual(spec.json_value('{}', 'DEPLOY_ACCES'), '')

    def test_le_verifier_controle_la_forme_des_variables_de_deploiement(self):
        racine = faire_depot()
        variables = {
            **self.DEPLOY, **self.GCP, 'DEPLOY_ACCES': 'gcp', 'DEBUG': 'x', 'VITE_API_URL': '/api',
            'GCP_ZONE': 'mauvaise zone',
        }
        environ = {
            'BRANCHE': 'prod',
            'SECRETS_JSON': json.dumps({'SECRET_KEY': 'a', 'DB_PASSWORD': 'b'}),
            'VARS_JSON': json.dumps({f'{nom}': valeur for nom, valeur in variables.items()}),
        }
        from io import StringIO
        from contextlib import redirect_stdout
        sortie = StringIO()
        with redirect_stdout(sortie):
            code = verifier.main(environ=environ, repo_root=racine)
        self.assertEqual(code, 1)
        self.assertIn('GCP_ZONE', sortie.getvalue())
        self.assertNotIn('DEPLOY_NAMESPACE', sortie.getvalue())



def _charger_deploy_env():
    """git-cli/deploy_env.py n'est pas un paquet : chargé depuis son chemin, avec git-cli dans sys.path (git_utils)."""
    import importlib.util
    import sys
    dossier = Path(__file__).resolve().parents[3] / 'git-cli'
    if str(dossier) not in sys.path:
        sys.path.insert(0, str(dossier))
    module_spec = importlib.util.spec_from_file_location('deploy_env_cli', dossier / 'deploy_env.py')
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


class UpsertTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cli = _charger_deploy_env()

    def test_cree_ce_qui_manque(self):
        ecritures, suppressions, inchangees = self.cli.plan_changes([('DEBUG', 'False', False), ('SECRET_KEY', 's', True)], set(), {})
        self.assertEqual([(n, a) for n, _, _, a in ecritures], [('DEBUG', 'cree'), ('SECRET_KEY', 'cree')])
        self.assertEqual((suppressions, inchangees), ([], 0))

    def test_relance_identique_ne_reecrit_aucune_variable(self):
        ecritures, suppressions, inchangees = self.cli.plan_changes([('DEBUG', 'False', False)], set(), {'DEBUG': 'False'})
        self.assertEqual((ecritures, suppressions, inchangees), ([], [], 1))

    def test_met_a_jour_une_variable_differente(self):
        ecritures, _, _ = self.cli.plan_changes([('DEBUG', 'False', False)], set(), {'DEBUG': 'True'})
        self.assertEqual([(n, a) for n, _, _, a in ecritures], [('DEBUG', 'mis a jour')])

    def test_un_secret_existant_est_remplace(self):
        ecritures, _, _ = self.cli.plan_changes([('SECRET_KEY', 's', True)], {'SECRET_KEY'}, {})
        self.assertEqual([(n, a) for n, _, _, a in ecritures], [('SECRET_KEY', 'remplace')])

    def test_un_nom_du_mauvais_type_est_supprime(self):
        _, suppressions, _ = self.cli.plan_changes([('SECRET_KEY', 's', True)], set(), {'SECRET_KEY': 'lisible'})
        self.assertEqual(suppressions, [('SECRET_KEY', False)])

    def test_ne_supprime_jamais_un_nom_absent_des_fichiers(self):
        _, suppressions, _ = self.cli.plan_changes([('DEBUG', 'False', False)], {'AUTRE_SECRET'}, {'AUTRE': 'x'})
        self.assertEqual(suppressions, [])


class VmOptionsTests(SimpleTestCase):
    """preparer-vm : infos de la VM lues dans .env.vm.<branche>, la ligne de commande prime."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.cli = _charger_deploy_env()

    def setUp(self):
        from unittest import mock
        self.dossier = Path(tempfile.mkdtemp())
        for cible, valeur in (('REPO_ROOT', self.dossier), ('ensure_ignored', lambda path: None)):
            patcher = mock.patch.object(self.cli, cible, valeur)
            patcher.start()
            self.addCleanup(patcher.stop)

    def _args(self, **options):
        from argparse import Namespace
        valeurs = {'branche': 'develop', 'hote': None, 'admin_user': None, 'cle_admin': None}
        valeurs.update(options)
        return Namespace(**valeurs)

    def _fichier(self, contenu):
        (self.dossier / '.env.vm.develop').write_text(contenu, encoding='utf-8')

    def test_lit_le_fichier(self):
        self._fichier('VM_HOTE=203.0.113.10\nVM_ADMIN_USER=ubuntu\nVM_CLE_ADMIN=~/.ssh/admin\n')
        args = self._args()
        self.cli.resolve_vm_options(args)
        self.assertEqual((args.hote, args.admin_user, args.cle_admin), ('203.0.113.10', 'ubuntu', '~/.ssh/admin'))

    def test_la_ligne_de_commande_prime(self):
        self._fichier('VM_HOTE=203.0.113.10\nVM_ADMIN_USER=ubuntu\n')
        args = self._args(hote='198.51.100.7')
        self.cli.resolve_vm_options(args)
        self.assertEqual((args.hote, args.admin_user), ('198.51.100.7', 'ubuntu'))

    def test_sans_fichier_les_options_suffisent(self):
        args = self._args(hote='203.0.113.10', admin_user='ubuntu')
        self.cli.resolve_vm_options(args)
        self.assertIsNone(args.cle_admin)

    def test_info_manquante_refusee(self):
        self._fichier('VM_HOTE=203.0.113.10\n')
        with self.assertRaisesMessage(self.cli.Failure, '--admin-user (ou VM_ADMIN_USER'):
            self.cli.resolve_vm_options(self._args())

    def test_nom_inconnu_refuse(self):
        self._fichier('VM_HOTE=203.0.113.10\nVM_ADMIN_USER=ubuntu\nSECRET_KEY=x\n')
        with self.assertRaisesMessage(self.cli.Failure, 'noms inconnus SECRET_KEY'):
            self.cli.resolve_vm_options(self._args())
