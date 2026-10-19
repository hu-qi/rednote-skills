"""Unit tests for the CodeArts CLI orchestration contract (no real credentials)."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("codearts_ci", ROOT / "tools/codearts_ci.py")
ci = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ci)


class CodeArtsCiUnitTests(unittest.TestCase):
    def test_resolves_model_ids_not_display_guesses(self):
        table = (
            "model_id model_name\n"
            "huaweicloud-maas/glm-5.3-flash GLM-5.3-Flash\n"
            "custom/Gemini-3.8-Flash-Medium Gemini-3.8-Flash-Medium\n"
        )
        self.assertEqual(ci.resolve_model(table, "glm-5.3-flash"), "huaweicloud-maas/glm-5.3-flash")
        self.assertEqual(ci.resolve_model(table, "Gemini-3.8-Flash-Medium"),
                         "custom/Gemini-3.8-Flash-Medium")
        self.assertIsNone(ci.resolve_model(table, "unconfigured-model"))

    def test_primary_qualified_model_id_matches_exact_provider(self):
        table = (
            "model_id model_name\\n"
            "other/glm-5.3 GLM-5.3\\n"
            "huaweicloud-maas/glm-5.3 GLM-5.3\\n"
        )
        self.assertEqual(
            ci.resolve_model(table, "huaweicloud-maas/glm-5.3"),
            "huaweicloud-maas/glm-5.3",
        )
        self.assertIsNone(ci.resolve_model(table, "custom/glm-5.3"))
        self.assertEqual(
            ci.resolve_model(table, "glm-5.3"),
            "other/glm-5.3",
        )

    def test_builtin_models_do_not_include_private_custom_provider_names(self):
        table = ("model_id model_name\n"
                 "huaweicloud-maas/GLM-5.2 GLM-5.2\n"
                 "custom/internal-private-model ACME\n"
                 "huaweicloud-maas/openpangu-2.0-flash OpenPangu\n")
        self.assertEqual(
            ci.available_builtin_models(table),
            ["huaweicloud-maas/GLM-5.2", "huaweicloud-maas/openpangu-2.0-flash"],
        )

    def test_only_quota_failure_activates_fallback(self):
        table = "model_id model_name\nhuaweicloud-maas/glm-5.3-flash GLM-5.3-Flash\ncustom/Gemini-3.8-Flash-Medium Gemini-3.8-Flash-Medium\n"
        outputs = [
            subprocess.CompletedProcess([], 0, table, ""),
            subprocess.CompletedProcess([], 1, "", "HTTP 429 quota exceeded"),
            subprocess.CompletedProcess([], 0, '{"result":"ok"}', ""),
        ]
        with patch.object(ci, "invoke", side_effect=outputs) as mocked:
            result = ci.choose_and_run("test prompt", ROOT)
        self.assertEqual(result["status"], "cli_completed")
        self.assertEqual(result["model"], "custom/Gemini-3.8-Flash-Medium")
        self.assertEqual(mocked.call_count, 3)
        self.assertIn("--sandbox", mocked.call_args.args[0])
        self.assertNotIn("--auto", mocked.call_args.args[0])

    def test_authentication_or_generic_failure_must_not_fallback(self):
        table = "model_id model_name\nhuaweicloud-maas/glm-5.3-flash GLM\ncustom/Gemini-3.8-Flash-Medium Gemini\n"
        outputs = [
            subprocess.CompletedProcess([], 0, table, ""),
            subprocess.CompletedProcess([], 1, "", "permission denied"),
        ]
        with patch.object(ci, "invoke", side_effect=outputs) as mocked:
            result = ci.choose_and_run("test", ROOT)
        self.assertEqual(result["status"], "cli_failed")
        self.assertEqual(mocked.call_count, 2)

    def test_model_failure_diagnostic_never_echoes_credentials(self):
        raw = "Access Key SECRET_AK could not authorize model registry: 403; url https://example.com?token=SECRET_SK"
        failure = subprocess.CompletedProcess([], 1, "", raw)
        detail = ci.diagnose_model_listing(failure)
        serialized = str(detail)
        self.assertEqual(detail["exit_code"], 1)
        self.assertIn("credential_or_signature", detail["safe_signals"])
        self.assertIn("http_4xx", detail["safe_signals"])
        self.assertNotIn("SECRET_AK", serialized)
        self.assertNotIn("SECRET_SK", serialized)
        self.assertNotIn("https://", serialized)

    def test_model_failure_tracks_output_shape(self):
        result = subprocess.CompletedProcess([], 2, "<html>gateway unavailable</html>", "")
        detail = ci.diagnose_model_listing(result)
        self.assertEqual(detail["output_shape"], "html")
        self.assertEqual(detail["exit_code"], 2)
        self.assertEqual(detail["stdout_chars"], len(result.stdout))

    def test_http_service_failure_is_retried_but_not_auth_failure(self):
        listing = ("model_id model_name\n"
                   "huaweicloud-maas/glm-5.3-flash GLM-5.3-Flash\n")
        outputs = [
            subprocess.CompletedProcess([], 1, "", "HTTP 503 Service Unavailable"),
            subprocess.CompletedProcess([], 0, listing, ""),
            subprocess.CompletedProcess([], 0, '{"ok":true}', ""),
        ]
        with patch.object(ci, "invoke", side_effect=outputs) as mocked, \
             patch.object(ci.time, "sleep") as wait:
            result = ci.choose_and_run("safe prompt", ROOT)
        self.assertEqual(result["status"], "cli_completed")
        self.assertEqual(mocked.call_count, 3)
        wait.assert_called_once()

    def test_http_status_diagnostic_uses_allowlisted_categories(self):
        failure = subprocess.CompletedProcess([], 1, "", "HTTP 503 Service Unavailable. Secret=VERY_PRIVATE")
        detail = ci.diagnose_model_listing(failure)
        self.assertEqual(detail["http_status_codes"], ["503"])
        self.assertIn("service", detail["safe_error_keywords"])
        self.assertNotIn("VERY_PRIVATE", repr(detail))
        self.assertEqual(ci.classify_cli_error(failure.stderr), "service_or_gateway")

    def test_chinese_error_is_classified_without_exposing_original_text(self):
        message = "Error: 请求失败。当前账号没有使用权限，请联系管理员。trace_id=SECRET_TRACE"
        result = subprocess.CompletedProcess([], 1, "", message)
        details = ci.diagnose_model_listing(result)
        self.assertTrue(details["contains_chinese"])
        self.assertIn("account_permissions", details["localized_error_categories"])
        self.assertIn("generic_failure", details["localized_error_categories"])
        self.assertNotIn("SECRET_TRACE", repr(details))
        self.assertIn("diagnostic", details["line_kinds"])

    def test_urls_are_deidentified_and_not_treated_as_publication_proof(self):
        candidates = ci.allowed_receipts(
            "https://example.com/private?token=SECRET "
            "https://example.huaweicloud.com/skill/123?access_token=SECRET "
            "https://www.xiaohongshu.com/skill/456?key=SECRET"
        )
        self.assertEqual(len(candidates), 2)
        self.assertTrue(all("SECRET" not in u for u in candidates))
        self.assertTrue(all("?" not in u for u in candidates))

    def test_smoke_fixture_contains_expected_rule(self):
        with tempfile.TemporaryDirectory() as folder:
            prompt, report = ci.build_smoke(ROOT, Path(folder))
            self.assertIn("repodoctor scan", prompt)
            self.assertIn("RD001", prompt)
            self.assertIn("permissions: write-all",
                          (Path(folder) / "fixture/.github/workflows/ci.yml").read_text())
            self.assertFalse(report.exists())

    def test_submission_prompt_matches_official_two_market_sequence(self):
        prompt = ci.submission_prompt(ROOT)
        self.assertLess(prompt.index("华为云Skill市场"), prompt.index("redskillhub-upload"))
        self.assertIn("小红书Skill市场", prompt)


if __name__ == "__main__":
    unittest.main()
