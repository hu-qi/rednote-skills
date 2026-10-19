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
