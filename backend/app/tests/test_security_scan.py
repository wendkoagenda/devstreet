"""
Tests du scanner de sécurité (backend/scripts/security_scan) :
règles (exemple qui échoue / exemple qui passe), score, exceptions, baseline, absence de fuite de secret.
"""
import json
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from django.test import SimpleTestCase

from scripts.security_scan import baseline, engine, exceptions, report, scoring
from scripts.security_scan.cli import main as cli_main
from scripts.security_scan.models import Finding, ScanContext, ScanFile, mask
from scripts.security_scan.registry import all_rules


# Règles dont le verdict dépend d'autres fichiers du dépôt : testées avec un dépôt simulé (voir leurs tests dédiés)
CONTEXT_DEPENDENT_RULES = ('DEP-003', 'SUP-001')


class FakeContext:
    """Contexte minimal : seuls les fichiers de `present` existent (utile aux règles de présence)."""

    def __init__(self, present=()):
        self.present = set(present)

    def exists(self, path):
        return path in self.present


def run(rule, path, text, present=()):
    return list(rule.check(ScanFile(path, text, FakeContext(present))))


class RuleCatalogTests(SimpleTestCase):
    def test_ids_are_unique_stable_and_documented(self):
        rules = all_rules()
        ids = [r.id for r in rules]
        self.assertEqual(len(ids), len(set(ids)))
        for r in rules:
            self.assertRegex(r.id, r'^[A-Z]+-\d{3}$')
            for field in ('title', 'description', 'recommendation', 'category', 'sample_path'):
                self.assertTrue(getattr(r, field), f'{r.id} : {field} manquant')
            self.assertTrue(r.fail_example, f'{r.id} : exemple qui échoue manquant')

    def test_each_rule_fails_on_its_bad_example(self):
        for r in all_rules():
            if r.id in CONTEXT_DEPENDENT_RULES:
                continue  # testé séparément (dépend de la présence d'un fichier)
            with self.subTest(rule=r.id):
                self.assertTrue(engine.matches(r.sample_path, r), f'{r.id} : sample_path hors de ses globs')
                self.assertGreaterEqual(len(run(r, r.sample_path, r.fail_example)), 1)

    def test_each_rule_passes_on_its_good_example(self):
        for r in all_rules():
            if r.id in CONTEXT_DEPENDENT_RULES:
                continue
            with self.subTest(rule=r.id):
                path = r.pass_path or r.sample_path
                self.assertEqual(run(r, path, r.pass_example), [])

    def test_missing_lock_rule(self):
        rule = next(r for r in all_rules() if r.id == 'DEP-003')
        self.assertEqual(len(run(rule, 'frontend/package.json', '{}')), 1)
        self.assertEqual(run(rule, 'frontend/package.json', '{}', present=['frontend/package-lock.json']), [])

    def test_blank_target_with_multiline_rel_is_accepted(self):
        rule = next(r for r in all_rules() if r.id == 'FE-003')
        text = '<a\n  href={u}\n  target="_blank"\n  rel="noreferrer"\n>x</a>\n'
        self.assertEqual(run(rule, 'frontend/src/x.tsx', text), [])

    def test_docs_route_inside_condition_is_accepted(self):
        rule = next(r for r in all_rules() if r.id == 'DJ-006')
        text = "urlpatterns = []\nif ENABLE:\n    urlpatterns += [path('redoc/', v)]\n"
        self.assertEqual(run(rule, 'backend/config/urls.py', text), [])

    def test_localstorage_for_theme_is_not_flagged(self):
        rule = next(r for r in all_rules() if r.id == 'FE-001')
        self.assertEqual(run(rule, 'frontend/src/x.ts', 'localStorage.setItem("theme", t);\n'), [])


class FallbackRuleTests(SimpleTestCase):
    def rule(self, rule_id):
        return next(r for r in all_rules() if r.id == rule_id)

    def messages(self, rule_id, path, text):
        return [h.message for h in run(self.rule(rule_id), path, text)]

    def test_python_env_default_forms(self):
        text = (
            "import os\n"
            "a = os.getenv('A', 'x')\n"
            "b = os.environ.get('B', default='y')\n"
            "c = os.getenv('C') or 'z'\n"
            "d = getattr(settings, 'D', 1)\n"
        )
        self.assertEqual(len(self.messages('FB-001', 'backend/config/settings.py', text)), 4)

    def test_python_env_without_fallback_is_fine(self):
        text = "import os\na = os.environ['A']\nb = os.getenv('B')\nc = os.getenv('C', None)\n"
        self.assertEqual(self.messages('FB-001', 'backend/config/settings.py', text), [])

    def test_empty_string_default_is_still_a_fallback(self):
        self.assertEqual(len(self.messages('FB-001', 'a.py', "import os\nx = os.getenv('X', '')\n")), 1)

    def test_js_env_fallback_forms(self):
        text = 'const a = import.meta.env.VITE_A ?? "";\nconst b = process.env.B || "x";\nconst c = process.env["C"] ?? 1;\n'
        self.assertEqual(len(self.messages('FB-002', 'frontend/src/x.ts', text)), 3)

    def test_swallowed_python_exceptions(self):
        for body in ('pass', 'continue', 'return None', 'result = None', 'return []'):
            text = f"for i in x:\n    try:\n        run()\n    except Exception:\n        {body}\n"
            self.assertEqual(len(self.messages('FB-003', 'a.py', text)), 1, body)

    def test_handled_python_exceptions_are_fine(self):
        for body in ('raise', 'logger.exception("x")', 'print(e)', 'raise ValueError("x") from e'):
            text = f"try:\n    run()\nexcept Exception as e:\n    {body}\n"
            self.assertEqual(self.messages('FB-003', 'a.py', text), [], body)

    def test_swallowed_js_errors(self):
        for code in ('try { a(); } catch {}', 'try { a(); } catch (e) { }', 'p.catch(() => null);',
                     'p.catch(() => {});', 'try { a(); } catch (e) { return null; }',
                     'try { a(); } catch {\n  // ignore\n}'):
            self.assertEqual(len(self.messages('FB-004', 'frontend/src/x.ts', code + '\n')), 1, code)

    def test_handled_js_errors_are_fine(self):
        for code in ('try { a(); } catch (e) { console.error(e); }', 'p.catch((e) => report(e));',
                     'try { a(); } catch (e) { throw e; }'):
            self.assertEqual(self.messages('FB-004', 'frontend/src/x.ts', code + '\n'), [], code)

    def test_python_log_then_constant_is_still_a_fallback(self):
        for body in ('logger.error("x")\n    return None', 'logger.warning("x")\n    result = False',
                     'logging.exception("x")\n    return ""'):
            text = f"try:\n    run()\nexcept Exception as e:\n    {body}\n"
            self.assertEqual(len(self.messages('FB-003', 'a.py', text)), 1, body)

    def test_python_log_only_or_log_then_raise_is_fine(self):
        for body in ('logger.error("x")\n    pass', 'logger.error("x")\n    raise',
                     'logger.error("x")\n    raise RuntimeError("y") from e',
                     'logger.error("x")\n    return compute()'):
            text = f"try:\n    run()\nexcept Exception as e:\n    {body}\n"
            self.assertEqual(self.messages('FB-003', 'a.py', text), [], body)

    def test_cli_user_facing_print_counts_as_handling(self):
        text = "try:\n    run()\nexcept RuntimeError as e:\n    print(f'Erreur: {e}')\n    return 1\n"
        self.assertEqual(self.messages('FB-003', 'git-cli/x.py', text), [])

    def test_js_console_then_constant_is_still_a_fallback(self):
        for code in ('try { a(); } catch (e) { console.error("x", e); return null; }',
                     'try { a(); } catch (e) {\n  console.warn("x");\n  return false;\n}',
                     'try { a(); } catch (e) { console.error(e); return []; }'):
            self.assertEqual(len(self.messages('FB-004', 'frontend/src/x.ts', code + '\n')), 1, code)

    def test_js_console_then_real_handling_is_fine(self):
        for code in ('try { a(); } catch (e) { console.error(e); return result; }',
                     'try { a(); } catch (e) { console.error(e); throw e; }',
                     'try { a(); } catch (e) { console.error(e); setError(e); }'):
            self.assertEqual(self.messages('FB-004', 'frontend/src/x.ts', code + '\n'), [], code)

    def test_shell_defaults(self):
        self.assertEqual(len(self.messages('FB-005', 'backend/entrypoint.sh', 'A=${A:-1}\nB=${B:=2}\n')), 2)
        self.assertEqual(self.messages('FB-005', 'backend/entrypoint.sh', 'A=${A:?obligatoire}\n# ${X:-ok}\n'), [])
        self.assertEqual(len(self.messages('FB-005', 'backend/Dockerfile', 'ARG PORT=80\n')), 1)
        self.assertEqual(self.messages('FB-005', 'backend/Dockerfile', 'ARG VITE_API_URL\n'), [])


class ApiRuleTests(SimpleTestCase):
    def messages(self, rule_id, path, text):
        rule = next(r for r in all_rules() if r.id == rule_id)
        return [h.message for h in run(rule, path, text)]

    # ------------------------------------------------------------ RT-001 : versionnement
    def test_versioned_routes_are_accepted(self):
        text = (
            "urlpatterns = [\n"
            "    path('v1/', include(router.urls)),\n"
            "    path('v2/users', users_view),\n"
            "    path('v10/auth/login', login_view),\n"
            "    path('api/', include('app.core.urls')),\n"
            "    path('admin/', admin.site.urls),\n"
            "    path('swagger/', schema_view),\n"
            "    path('redoc/', redoc_view),\n"
            "]\n"
        )
        self.assertEqual(self.messages('RT-001', 'backend/config/urls.py', text), [])

    def test_unversioned_routes_are_reported_once_each(self):
        text = (
            "urlpatterns = [\n"
            "    path('auth/login', login_view),\n"
            "    path('users', users_view),\n"
            "    re_path(r'^legacy/', legacy_view),\n"
            "    path('version/', info_view),\n"
            "]\n"
        )
        self.assertEqual(len(self.messages('RT-001', 'backend/app/core/urls.py', text)), 4)

    def test_a_route_that_only_looks_like_a_version_is_reported(self):
        for route in ('values/x', 'vendor/x', 'v/x', 'version/x'):
            text = f"urlpatterns = [path('{route}', view)]\n"
            self.assertEqual(len(self.messages('RT-001', 'backend/app/x/urls.py', text)), 1, route)

    def test_unparsable_urls_file_is_ignored_without_crash(self):
        self.assertEqual(self.messages('RT-001', 'backend/app/x/urls.py', 'urlpatterns = ['), [])

    # ------------------------------------------------------------ RT-002 : limite par défaut
    def test_missing_default_throttle_is_reported(self):
        text = "INSTALLED_APPS = []\nREST_FRAMEWORK = {'DEFAULT_PAGINATION_CLASS': 'x'}\n"
        self.assertEqual(len(self.messages('RT-002', 'backend/config/settings.py', text)), 1)

    def test_empty_default_throttle_is_reported(self):
        text = "INSTALLED_APPS = []\nREST_FRAMEWORK = {'DEFAULT_THROTTLE_CLASSES': []}\n"
        self.assertEqual(len(self.messages('RT-002', 'backend/config/settings.py', text)), 1)

    def test_classes_without_rates_are_reported(self):
        text = "INSTALLED_APPS = []\nREST_FRAMEWORK = {'DEFAULT_THROTTLE_CLASSES': ['x.AnonRateThrottle']}\n"
        self.assertEqual(len(self.messages('RT-002', 'backend/config/settings.py', text)), 1)

    def test_default_throttle_with_rates_is_accepted(self):
        text = ("INSTALLED_APPS = []\nREST_FRAMEWORK = {\n"
                "    'DEFAULT_THROTTLE_CLASSES': ['x.AnonRateThrottle', 'x.UserRateThrottle'],\n"
                "    'DEFAULT_THROTTLE_RATES': {'anon': '60/minute', 'user': '600/minute'},\n}\n")
        self.assertEqual(self.messages('RT-002', 'backend/config/settings.py', text), [])

    def test_partial_settings_files_are_not_concerned(self):
        self.assertEqual(self.messages('RT-002', 'backend/config/settings.py', "DEBUG = True\n"), [])

    # ------------------------------------------------------------ RT-003 : routes publiques
    def test_public_function_view_needs_its_own_throttle(self):
        text = "@api_view(['GET'])\n@permission_classes([AllowAny])\ndef v(request):\n    pass\n"
        self.assertEqual(len(self.messages('RT-003', 'a.py', text)), 1)

    def test_public_function_view_with_throttle_is_accepted(self):
        text = ("@api_view(['POST'])\n@permission_classes([AllowAny])\n"
                "@throttle_classes([LoginThrottle])\ndef v(request):\n    pass\n")
        self.assertEqual(self.messages('RT-003', 'a.py', text), [])

    def test_private_view_without_own_throttle_is_fine(self):
        text = "@api_view(['GET'])\n@permission_classes([IsAuthenticated])\ndef v(request):\n    pass\n"
        self.assertEqual(self.messages('RT-003', 'a.py', text), [])

    def test_public_class_views_are_detected(self):
        for body in ("class V(APIView):\n    permission_classes = [AllowAny]\n",
                     "class V(TokenVerifyView):\n    pass\n",
                     "class V(jwt_views.TokenObtainPairView):\n    serializer_class = S\n"):
            self.assertEqual(len(self.messages('RT-003', 'a.py', body)), 1, body)

    def test_public_class_view_with_throttle_is_accepted(self):
        text = "class V(TokenVerifyView):\n    throttle_classes = [VerifyThrottle]\n"
        self.assertEqual(self.messages('RT-003', 'a.py', text), [])

    def test_disabling_the_throttle_is_always_reported(self):
        for text in ("class V(APIView):\n    throttle_classes = []\n",
                     "@api_view(['GET'])\n@throttle_classes([])\ndef v(request):\n    pass\n",
                     "class V(APIView):\n    permission_classes = [IsAuthenticated]\n    throttle_classes = ()\n"):
            self.assertEqual(len(self.messages('RT-003', 'a.py', text)), 1, text)


class SwaggerTagRuleTests(SimpleTestCase):
    VIEWSET = 'backend/app/core/views/role_viewset.py'

    def messages(self, rule_id, path, text, present=()):
        rule = next(r for r in all_rules() if r.id == rule_id)
        return [h.message for h in run(rule, path, text, present)]

    @staticmethod
    def viewset(tag, action='list', name='RoleViewSet'):
        return (f"class {name}(viewsets.ModelViewSet):\n"
                f"    @swagger_auto_schema(tags=['{tag}'])\n    def {action}(self, request):\n        pass\n")

    def test_correct_viewset_tag_is_accepted(self):
        self.assertEqual(self.messages('RT-004', self.VIEWSET, self.viewset('V1 - Role')), [])

    def test_tag_copied_from_another_resource_is_reported(self):
        self.assertEqual(len(self.messages('RT-004', self.VIEWSET, self.viewset('V1 - User'))), 1)

    def test_wrong_version_prefix_is_reported_when_the_router_version_is_known(self):
        urls = {'backend/app/core/urls.py'}

        class Ctx:
            def exists(self, path):
                return path in urls

            def read(self, path):
                return "urlpatterns = [path('v2/', include(router.urls))]" if path in urls else ''

        rule = next(r for r in all_rules() if r.id == 'RT-004')
        file = ScanFile(self.VIEWSET, self.viewset('V1 - Role'), Ctx())
        self.assertEqual(len(list(rule.check(file))), 1)
        file = ScanFile(self.VIEWSET, self.viewset('V2 - Role'), Ctx())
        self.assertEqual(list(rule.check(file)), [])

    def test_typo_in_the_tag_is_reported(self):
        for tag in ('V1 - Roles', 'v1 - Role', 'V1-Role', 'Role', 'V1 - role'):
            self.assertEqual(len(self.messages('RT-004', self.VIEWSET, self.viewset(tag))), 1, tag)

    def test_several_tags_on_one_action_are_reported(self):
        text = ("class RoleViewSet(viewsets.ModelViewSet):\n"
                "    @swagger_auto_schema(tags=['V1 - Role', 'Autre'])\n    def list(self, request):\n        pass\n")
        self.assertEqual(len(self.messages('RT-004', self.VIEWSET, text)), 1)

    def test_auth_views_must_use_the_auth_tag(self):
        good = "@swagger_auto_schema(method='get', tags=['Auth'])\n@api_view(['GET'])\ndef me_view(request):\n    pass\n"
        bad = good.replace("'Auth'", "'V1 - Auth'")
        self.assertEqual(self.messages('RT-004', 'backend/app/core/views/auth_views.py', good), [])
        self.assertEqual(len(self.messages('RT-004', 'backend/app/core/views/auth_views.py', bad)), 1)

    def test_class_based_auth_views_are_checked(self):
        text = ("class CustomTokenVerifyView(TokenVerifyView):\n"
                "    @swagger_auto_schema(tags=['Autre'])\n    def post(self, request):\n        pass\n")
        self.assertEqual(len(self.messages('RT-004', 'backend/app/core/views/auth_views.py', text)), 1)

    def test_every_action_needs_a_tag(self):
        for action in ('list', 'create', 'retrieve', 'update', 'partial_update', 'destroy'):
            text = f"class RoleViewSet(viewsets.ModelViewSet):\n    def {action}(self, request):\n        pass\n"
            self.assertEqual(len(self.messages('RT-005', self.VIEWSET, text)), 1, action)

    def test_custom_action_without_tag_is_reported(self):
        text = ("class RoleViewSet(viewsets.ModelViewSet):\n"
                "    @action(detail=True, methods=['get'])\n    def stats(self, request, pk=None):\n        pass\n")
        self.assertEqual(len(self.messages('RT-005', self.VIEWSET, text)), 1)

    def test_swagger_decorator_without_tags_is_reported(self):
        text = ("class RoleViewSet(viewsets.ModelViewSet):\n"
                "    @swagger_auto_schema(operation_description='x')\n    def list(self, request):\n        pass\n")
        self.assertEqual(len(self.messages('RT-005', self.VIEWSET, text)), 1)

    def test_helper_methods_are_not_actions(self):
        text = ("class RoleViewSet(viewsets.ModelViewSet):\n    def get_queryset(self):\n        pass\n"
                "    def _private(self):\n        pass\n")
        self.assertEqual(self.messages('RT-005', self.VIEWSET, text), [])

    def test_function_view_without_tag_is_reported(self):
        text = "@api_view(['GET'])\ndef ping(request):\n    pass\n"
        self.assertEqual(len(self.messages('RT-005', 'backend/app/core/views/auth_views.py', text)), 1)

    def test_unparsable_file_is_ignored(self):
        self.assertEqual(self.messages('RT-004', self.VIEWSET, 'class ('), [])
        self.assertEqual(self.messages('RT-005', self.VIEWSET, 'class ('), [])


class ExposureRuleTests(SimpleTestCase):
    def messages(self, rule_id, path, text, present=()):
        rule = next(r for r in all_rules() if r.id == rule_id)
        return [h.message for h in run(rule, path, text, present)]

    # ------------------------------------------------------------ API-001
    def handler(self, body, caught='Exception'):
        return f"def vue(request):\n    try:\n        run()\n    except {caught} as e:\n        {body}\n"

    def test_exception_text_in_response_is_reported(self):
        for body in ("return Response({'error': str(e)}, status=400)",
                     "return Response({'detail': f'Erreur: {e}'})",
                     "return Response({'error': e.args})",
                     "return JsonResponse({'message': repr(e)})",
                     "return Response({'trace': traceback.format_exc()})"):
            self.assertEqual(len(self.messages('API-001', 'a.py', self.handler(body))), 1, body)

    def test_generic_message_is_accepted(self):
        text = self.handler("logger.exception('x')\n        return Response({'error': 'Operation impossible'})")
        self.assertEqual(self.messages('API-001', 'a.py', text.replace('\n        return', '\n        return')), [])

    def test_validation_errors_are_meant_for_users(self):
        for caught in ('ValidationError', 'serializers.ValidationError', 'django.core.exceptions.ValidationError'):
            text = self.handler("return Response({'error': str(e)}, status=400)", caught)
            self.assertEqual(self.messages('API-001', 'a.py', text), [], caught)

    def test_exception_logged_but_not_returned_is_accepted(self):
        text = self.handler("logger.error(str(e))\n        return Response(status=500)")
        self.assertEqual(self.messages('API-001', 'a.py', text), [])

    # ------------------------------------------------------------ API-002
    def test_serializer_meta_forms(self):
        for line, expected in (("fields = '__all__'", 1), ("exclude = ('password',)", 1),
                               ("fields = ['id', 'name']", 0), ("fields = ('id',)", 0)):
            text = f"class S(serializers.ModelSerializer):\n    class Meta:\n        model = M\n        {line}\n"
            self.assertEqual(len(self.messages('API-002', 'backend/app/x/serializers.py', text)), expected, line)

    # ------------------------------------------------------------ API-003
    def test_settings_without_pagination_are_reported(self):
        text = "INSTALLED_APPS = []\nREST_FRAMEWORK = {'DEFAULT_RENDERER_CLASSES': []}\n"
        self.assertEqual(len(self.messages('API-003', 'backend/config/settings.py', text)), 2)  # classe + taille

    def test_oversized_page_is_reported(self):
        text = ("INSTALLED_APPS = []\nREST_FRAMEWORK = {'DEFAULT_PAGINATION_CLASS': 'x', 'PAGE_SIZE': 5000}\n")
        self.assertEqual(len(self.messages('API-003', 'backend/config/settings.py', text)), 1)

    def test_reasonable_pagination_settings_are_accepted(self):
        text = ("INSTALLED_APPS = []\nREST_FRAMEWORK = {'DEFAULT_PAGINATION_CLASS': 'x', 'PAGE_SIZE': 20}\n")
        self.assertEqual(self.messages('API-003', 'backend/config/settings.py', text), [])

    def test_custom_action_returning_a_list_is_reported(self):
        text = ("class UserViewSet(viewsets.ModelViewSet):\n"
                "    @action(detail=False)\n    def search(self, request):\n"
                "        serializer = self.get_serializer(self.get_queryset(), many=True)\n"
                "        return Response(serializer.data)\n")
        self.assertEqual(len(self.messages('API-003', 'backend/app/core/views/user_viewset.py', text)), 1)

    def test_paginated_action_is_accepted(self):
        text = ("class UserViewSet(viewsets.ModelViewSet):\n"
                "    def list(self, request):\n"
                "        page = self.paginate_queryset(self.get_queryset())\n"
                "        serializer = self.get_serializer(page, many=True)\n"
                "        return self.get_paginated_response(serializer.data)\n")
        self.assertEqual(self.messages('API-003', 'backend/app/core/views/user_viewset.py', text), [])

    def test_swagger_documentation_with_many_true_is_not_a_list_response(self):
        text = ("class UserViewSet(viewsets.ModelViewSet):\n"
                "    @swagger_auto_schema(responses={200: UserSerializer(many=True)})\n"
                "    def retrieve(self, request, pk=None):\n        return Response({})\n")
        self.assertEqual(self.messages('API-003', 'backend/app/core/views/user_viewset.py', text), [])

    def test_single_object_serializer_is_not_a_list(self):
        text = ("class UserViewSet(viewsets.ModelViewSet):\n"
                "    def retrieve(self, request, pk=None):\n"
                "        return Response(self.get_serializer(self.get_object()).data)\n")
        self.assertEqual(self.messages('API-003', 'backend/app/core/views/user_viewset.py', text), [])

    # ------------------------------------------------------------ API-004
    def test_upload_without_checks_reports_what_is_missing(self):
        text = "def up(request):\n    f = request.FILES['a']\n    save(f)\n"
        messages = self.messages('API-004', 'backend/app/x/views.py', text)
        self.assertEqual(len(messages), 1)
        self.assertIn('taille ni de type', messages[0])

    def test_upload_with_size_only_reports_the_type(self):
        text = "def up(request):\n    f = request.FILES['a']\n    if f.size > 10:\n        raise ValueError()\n"
        messages = self.messages('API-004', 'backend/app/x/views.py', text)
        self.assertEqual(len(messages), 1)
        self.assertIn('type', messages[0])
        self.assertNotIn('taille', messages[0])

    def test_upload_with_both_checks_is_accepted(self):
        text = ("def up(request):\n    f = request.FILES['a']\n    if f.size > 10:\n        raise ValueError()\n"
                "    ext = os.path.splitext(f.name)[1]\n")
        self.assertEqual(self.messages('API-004', 'backend/app/x/views.py', text), [])

    def test_files_without_uploads_are_ignored(self):
        self.assertEqual(self.messages('API-004', 'backend/app/x/views.py', 'def f():\n    pass\n'), [])


class PasswordPolicyRuleTests(SimpleTestCase):
    NAMES = ('UserAttributeSimilarityValidator', 'MinimumLengthValidator', 'CommonPasswordValidator',
             'NumericPasswordValidator')

    def settings_text(self, min_length=None, skip=None):
        entries = []
        for name in self.NAMES:
            if name == skip:
                continue
            options = f", 'OPTIONS': {{'min_length': {min_length}}}" if name == 'MinimumLengthValidator' and min_length else ''
            entries.append(f"    {{'NAME': 'django.contrib.auth.password_validation.{name}'{options}}},")
        return "INSTALLED_APPS = []\nAUTH_PASSWORD_VALIDATORS = [\n" + "\n".join(entries) + "\n]\n"

    def messages(self, text):
        rule = next(r for r in all_rules() if r.id == 'DJ-009')
        return [h.message for h in run(rule, 'backend/config/settings.py', text)]

    def test_django_default_length_is_too_short(self):
        self.assertEqual(len(self.messages(self.settings_text())), 1)

    def test_short_length_is_reported(self):
        self.assertEqual(len(self.messages(self.settings_text(min_length=8))), 1)

    def test_long_enough_policy_is_accepted(self):
        for length in (10, 12, 16):
            self.assertEqual(self.messages(self.settings_text(min_length=length)), [], length)

    def test_each_missing_validator_is_reported(self):
        for name in self.NAMES:
            if name == 'MinimumLengthValidator':
                continue
            self.assertEqual(len(self.messages(self.settings_text(min_length=12, skip=name))), 1, name)

    def test_missing_setting_is_reported(self):
        self.assertEqual(len(self.messages("INSTALLED_APPS = []\n")), 1)


class DependencyScanRuleTests(SimpleTestCase):
    class Repo:
        """Dépôt simulé : fichiers et contenus."""

        def __init__(self, files):
            self.files = files
            self.all_files = list(files)

        def exists(self, path):
            return path in self.files

        def read(self, path):
            return self.files.get(path, '')

    def check(self, path, files):
        rule = next(r for r in all_rules() if r.id == 'SUP-001')
        return list(rule.check(ScanFile(path, '', self.Repo(files))))

    def test_no_scan_is_reported_for_both_ecosystems(self):
        self.assertEqual(len(self.check('backend/requirements.txt', {})), 1)
        self.assertEqual(len(self.check('frontend/package.json', {})), 1)

    def test_dependabot_covers_its_ecosystem_only(self):
        files = {'.github/dependabot.yml': 'updates:\n  - package-ecosystem: "pip"\n    directory: "/backend"\n'}
        self.assertEqual(self.check('backend/requirements.txt', files), [])
        self.assertEqual(len(self.check('frontend/package.json', files)), 1)

    def test_audit_step_in_a_workflow_covers_the_ecosystem(self):
        files = {'.github/workflows/ci.yml': 'steps:\n  - run: pip-audit -r backend/requirements.txt\n  - run: npm audit --omit=dev\n'}
        self.assertEqual(self.check('backend/requirements.txt', files), [])
        self.assertEqual(self.check('frontend/package.json', files), [])

    def test_unrelated_workflow_does_not_count(self):
        files = {'.github/workflows/git-cli.yml': 'steps:\n  - run: echo ok\n'}
        self.assertEqual(len(self.check('backend/requirements.txt', files)), 1)


class MaskingTests(SimpleTestCase):
    def test_secret_values_never_appear(self):
        for line in ('PASSWORD = "Sup3rS3cretValue"', "token: 'abcdEFGH1234ijklMNOP5678qrst'",
                     'key = "AKIAABCDEFGHIJKLMNOP"'):
            masked = mask(line)
            self.assertNotIn('Sup3rS3cretValue', masked)
            self.assertNotIn('abcdEFGH1234ijklMNOP5678qrst', masked)
            self.assertNotIn('AKIAABCDEFGHIJKLMNOP', masked)

    def test_snippet_is_short(self):
        self.assertLessEqual(len(mask('x = ' + 'a ' * 200)), 80)


class ScoringTests(SimpleTestCase):
    @staticmethod
    def finding(rule_id, severity, n=0):
        return Finding(rule_id, severity, 'c', 'f.py', n, 'm', '', f'{rule_id}{n}')

    def test_penalties_follow_the_specification(self):
        self.assertEqual(scoring.compute([self.finding('A', 'critical')])['score'], 80)
        self.assertEqual(scoring.compute([self.finding('A', 'error')])['score'], 90)
        self.assertEqual(scoring.compute([self.finding('A', 'warning')])['score'], 97)
        self.assertEqual(scoring.compute([self.finding('A', 'info')])['score'], 100)

    def test_one_rule_cannot_zero_the_score(self):
        many = [self.finding('A', 'error', i) for i in range(50)]
        self.assertEqual(scoring.compute(many)['score'], 100 - 10 * scoring.MAX_OCCURRENCES_PER_RULE)

    def test_states(self):
        self.assertEqual(scoring.state_for(100), 'Sain')
        self.assertEqual(scoring.state_for(90), 'Sain')
        self.assertEqual(scoring.state_for(89), 'À surveiller')
        self.assertEqual(scoring.state_for(74), 'Risque élevé')
        self.assertEqual(scoring.state_for(49), 'Bloquant')


class ExceptionTests(SimpleTestCase):
    def write(self, items):
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory, True)
        path = directory / 'security-exceptions.json'
        path.write_text(json.dumps({'exceptions': items}), encoding='utf-8')
        return path

    @staticmethod
    def entry(**override):
        base = {'rule': 'DJ-005', 'path': 'backend/app/v.py', 'reason': 'Route publique du mot de passe oublié',
                'author': 'elisee', 'expires': (date.today() + timedelta(days=30)).isoformat()}
        base.update(override)
        return base

    def test_valid_entry_is_loaded(self):
        self.assertEqual(len(exceptions.load(self.write([self.entry()]))), 1)

    def test_missing_expiry_is_refused(self):
        item = self.entry()
        del item['expires']
        with self.assertRaisesMessage(exceptions.ConfigError, 'expires'):
            exceptions.load(self.write([item]))

    def test_missing_author_or_reason_is_refused(self):
        for field in ('author', 'reason'):
            item = self.entry()
            del item[field]
            with self.assertRaisesMessage(exceptions.ConfigError, field):
                exceptions.load(self.write([item]))

    def test_short_reason_is_refused(self):
        with self.assertRaisesMessage(exceptions.ConfigError, 'justification'):
            exceptions.load(self.write([self.entry(reason='ok')]))

    def test_wildcard_or_folder_path_is_refused(self):
        for path in ('backend/*', 'backend/app/', '*.py'):
            with self.assertRaisesMessage(exceptions.ConfigError, 'chemin'):
                exceptions.load(self.write([self.entry(path=path)]))

    def test_unknown_rule_is_refused(self):
        with self.assertRaisesMessage(exceptions.ConfigError, 'inconnue'):
            exceptions.load(self.write([self.entry(rule='NOPE-999')]))

    def test_permanent_exception_is_refused(self):
        far = (date.today() + timedelta(days=exceptions.MAX_VALIDITY_DAYS + 5)).isoformat()
        with self.assertRaisesMessage(exceptions.ConfigError, 'trop lointaine'):
            exceptions.load(self.write([self.entry(expires=far)]))

    def test_bad_date_is_refused(self):
        with self.assertRaisesMessage(exceptions.ConfigError, 'date'):
            exceptions.load(self.write([self.entry(expires='demain')]))

    def test_exception_marks_matching_findings_only(self):
        entries = exceptions.load(self.write([self.entry()]))
        hit = Finding('DJ-005', 'warning', 'auth', 'backend/app/v.py', 3, 'm', '', 'a')
        other_file = Finding('DJ-005', 'warning', 'auth', 'backend/app/w.py', 3, 'm', '', 'b')
        other_rule = Finding('PY-001', 'error', 'injection', 'backend/app/v.py', 3, 'm', '', 'c')
        expired, unused = exceptions.apply([hit, other_file, other_rule], entries)
        self.assertEqual((hit.status, other_file.status, other_rule.status), ('excepted', 'new', 'new'))
        self.assertEqual((expired, unused), ([], []))

    def test_expired_exception_reactivates_the_finding(self):
        entries = exceptions.load(self.write([self.entry(expires=(date.today() + timedelta(days=1)).isoformat())]))
        finding = Finding('DJ-005', 'warning', 'auth', 'backend/app/v.py', 3, 'm', '', 'a')
        expired, _ = exceptions.apply([finding], entries, today=date.today() + timedelta(days=2))
        self.assertEqual(finding.status, 'new')
        self.assertEqual(len(expired), 1)

    def test_unused_exception_is_reported(self):
        entries = exceptions.load(self.write([self.entry()]))
        _, unused = exceptions.apply([], entries)
        self.assertEqual(len(unused), 1)


class BaselineTests(SimpleTestCase):
    def test_new_versus_existing(self):
        known = Finding('PY-001', 'error', 'injection', 'a.py', 1, 'm', '', 'known')
        fresh = Finding('PY-001', 'error', 'injection', 'a.py', 9, 'm', '', 'fresh')
        baseline.apply([known, fresh], Counter(['known']))
        self.assertEqual((known.status, fresh.status), ('existing', 'new'))

    def test_extra_identical_occurrence_is_new(self):
        first = Finding('FE-001', 'error', 'frontend', 'a.ts', 1, 'm', 's', 'same')
        second = Finding('FE-001', 'error', 'frontend', 'a.ts', 2, 'm', 's', 'same')
        third = Finding('FE-001', 'error', 'frontend', 'a.ts', 3, 'm', 's', 'same')
        baseline.apply([first, second, third], Counter(['same', 'same']))
        self.assertEqual([f.status for f in (first, second, third)], ['existing', 'existing', 'new'])
    def test_saved_baseline_contains_no_snippet(self):
        directory = Path(tempfile.mkdtemp())
        path = directory / 'security-baseline.json'
        self.addCleanup(shutil.rmtree, directory, True)
        secret = Finding('SEC-001', 'critical', 'secrets', 'a.py', 1, 'm', 'password="****"', 'fp1')
        baseline.save(path, [secret])
        data = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(set(data['findings'][0]), {'fingerprint', 'rule', 'path'})


class EndToEndTests(SimpleTestCase):
    """Scan d'un petit dépôt temporaire (sans git : parcours disque)."""

    SECRET = 'Sup3rS3cretValue99'

    def make_repo(self, files):
        root = Path(tempfile.mkdtemp())
        for rel, text in files.items():
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding='utf-8')
        self.addCleanup(shutil.rmtree, root, True)
        return root

    def scan(self, root, *extra):
        out = root / 'out.json'
        code = cli_main(['--root', str(root), '--format', 'json', '--output', str(out), *extra])
        return code, json.loads(out.read_text(encoding='utf-8')) if out.exists() else None

    def test_secret_is_found_but_never_written_to_the_report(self):
        root = self.make_repo({'backend/config/x.py': f'DB_PASSWORD = "{self.SECRET}"\n'})
        code, result = self.scan(root)
        self.assertEqual(code, 1)
        self.assertTrue(any(f['rule_id'] == 'SEC-001' for f in result['findings']))
        self.assertNotIn(self.SECRET, (root / 'out.json').read_text(encoding='utf-8'))
        for fmt in ('text', 'markdown'):
            rendered = report.RENDERERS[fmt](result)
            self.assertNotIn(self.SECRET, rendered)

    def test_clean_repository_exits_zero(self):
        root = self.make_repo({'README.md': 'rien\n', '.gitignore': '.env\n'})
        code, result = self.scan(root)
        self.assertEqual((code, result['score']), (0, 100))

    def test_baseline_turns_existing_debt_into_non_blocking(self):
        root = self.make_repo({'backend/config/x.py': f'DB_PASSWORD = "{self.SECRET}"\n'})
        self.assertEqual(cli_main(['--root', str(root), '--update-baseline']), 0)
        code, result = self.scan(root)
        self.assertEqual(code, 0)
        self.assertEqual((result['new_count'], result['existing_count']), (0, 1))
        self.assertNotIn(self.SECRET, (root / 'security-baseline.json').read_text(encoding='utf-8'))

    def test_new_problem_after_baseline_blocks(self):
        root = self.make_repo({'backend/config/x.py': f'DB_PASSWORD = "{self.SECRET}"\n'})
        cli_main(['--root', str(root), '--update-baseline'])
        (root / 'backend/config/y.py').write_text('eval(texte)\n', encoding='utf-8')
        code, result = self.scan(root)
        self.assertEqual((code, result['new_count']), (1, 1))

    def test_invalid_exception_file_is_a_config_error(self):
        root = self.make_repo({'security-exceptions.json': json.dumps(
            {'exceptions': [{'rule': 'PY-001', 'path': 'a.py', 'reason': 'x' * 20, 'author': 'a'}]})})
        self.assertEqual(cli_main(['--root', str(root)]), 2)

    def test_exception_removes_blocking_until_it_expires(self):
        root = self.make_repo({'backend/config/y.py': 'eval(texte)\n'})
        item = {'rule': 'PY-001', 'path': 'backend/config/y.py', 'reason': 'Cas isolé et contrôlé en interne',
                'author': 'elisee', 'expires': (date.today() + timedelta(days=10)).isoformat()}
        (root / 'security-exceptions.json').write_text(json.dumps({'exceptions': [item]}), encoding='utf-8')
        code, result = self.scan(root)
        self.assertEqual((code, result['excepted_count']), (0, 1))
        item['expires'] = (date.today() - timedelta(days=1)).isoformat()
        (root / 'security-exceptions.json').write_text(json.dumps({'exceptions': [item]}), encoding='utf-8')
        code, result = self.scan(root)
        self.assertEqual(code, 1)
        self.assertEqual(len(result['expired_exceptions']), 1)

    def test_fail_on_never_never_blocks(self):
        root = self.make_repo({'backend/config/y.py': 'eval(texte)\n'})
        self.assertEqual(self.scan(root, '--fail-on', 'never')[0], 0)

    def test_changed_since_scans_only_modified_files(self):
        root = self.make_repo({'backend/config/old.py': 'eval(a)\n'})
        git = lambda *a: subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=root,
                                        check=True, capture_output=True)
        git('init', '-q')
        git('add', '.')
        git('commit', '-q', '-m', 'init')
        (root / 'backend/config/new.py').write_text('eval(b)\n', encoding='utf-8')
        code, result = self.scan(root, '--changed-since', 'HEAD')
        paths = {f['path'] for f in result['findings']}
        self.assertEqual(paths, {'backend/config/new.py'})
        self.assertEqual(code, 1)


class RepositoryScanTests(SimpleTestCase):
    def test_the_scanner_does_not_scan_itself_or_tests(self):
        root = Path(__file__).resolve().parents[3]
        context = ScanContext(root)
        self.assertFalse([p for p in context.files if p.startswith('backend/scripts/security_scan/')])
        self.assertFalse([p for p in context.files if re.search(r'/tests/|/tests\.py$|/test_', p)])


class MigrationAndAdminRuleTests(SimpleTestCase):
    """DJ-011 (migration destructive) et DJ-010 (admin Django toujours exposé)."""

    def rule(self, rule_id):
        return next(r for r in all_rules() if r.id == rule_id)

    def check_migration(self, operations):
        text = 'from django.db import migrations\n\n\nclass Migration(migrations.Migration):\n    operations = [\n' + operations + '\n    ]\n'
        return run(self.rule('DJ-011'), 'backend/app/core/migrations/0009_x.py', text)

    def test_removing_a_field_or_a_model_is_reported(self):
        self.assertEqual(len(self.check_migration("        migrations.RemoveField(model_name='user', name='phone'),")), 1)
        self.assertEqual(len(self.check_migration("        migrations.DeleteModel(name='Old'),")), 1)

    def test_creating_and_altering_are_not_destructive(self):
        operations = ("        migrations.CreateModel(name='New', fields=[]),\n"
                      "        migrations.AddField(model_name='user', name='a', field=None),\n"
                      "        migrations.AlterField(model_name='user', name='a', field=None),\n"
                      "        migrations.RenameField(model_name='user', old_name='a', new_name='b'),")
        self.assertEqual(self.check_migration(operations), [])

    def test_raw_sql_that_drops_or_deletes_is_reported(self):
        for sql in ('DROP TABLE core_old', 'delete from core_user', 'TRUNCATE core_log'):
            with self.subTest(sql=sql):
                self.assertEqual(len(self.check_migration(f"        migrations.RunSQL('{sql}'),")), 1)

    def test_harmless_raw_sql_is_not_reported(self):
        self.assertEqual(self.check_migration("        migrations.RunSQL('CREATE INDEX i ON core_user (email)'),"), [])

    def test_two_destructive_operations_in_one_file_are_two_findings(self):
        operations = "        migrations.RemoveField(model_name='a', name='x'),\n        migrations.RemoveField(model_name='a', name='y'),"
        self.assertEqual(len(self.check_migration(operations)), 2)

    def test_admin_route_is_reported_only_when_unconditional(self):
        rule = self.rule('DJ-010')
        bare = "from django.urls import path\nurlpatterns = [path('admin/', admin.site.urls)]\n"
        guarded = "urlpatterns = []\nif settings.ENABLE_ADMIN:\n    urlpatterns += [path('admin/', admin.site.urls)]\n"
        self.assertEqual(len(run(rule, 'backend/config/urls.py', bare)), 1)
        self.assertEqual(run(rule, 'backend/config/urls.py', guarded), [])
