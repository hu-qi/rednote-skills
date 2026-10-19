"""Regression guards for RepoDoctor's Chinese-first market presentation.

Do not translate executable commands, rule IDs or machine-readable names.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "repodoctor" / "SKILL.md"
INTRO = ROOT / "docs" / "MARKETPLACE.zh-CN.md"


class ChineseMarketplaceContentTests(unittest.TestCase):
    def test_skill_frontmatter_preserves_machine_identity_with_chinese_description(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^name:\s*repodoctor\s*$")
        description = re.search(r"(?m)^description:\s*(.+)$", frontmatter)
        self.assertIsNotNone(description)
        self.assertRegex(description.group(1), r"[\u4e00-\u9fff]")
        self.assertGreaterEqual(len(description.group(1)), 20)

    def test_instructions_keep_original_executable_commands_and_limitations(self):
        text = SKILL.read_text(encoding="utf-8")
        for token in ("RD001", "RD002", "RD003", "RD004", "RD005",
                      "repodoctor scan", "--format json", "--format sarif",
                      "static-lead", "scan.truncated", "JSON"):
            self.assertIn(token, text)
        self.assertIn("简体中文", text)
        self.assertIn("静态风险线索", text)
        self.assertIn("不执行", text)

    def test_market_copy_distinguishes_platform_and_release_versions(self):
        text = INTRO.read_text(encoding="utf-8")
        self.assertIn("101678", text)
        self.assertIn("108108", text)
        self.assertIn("0.2.0", text)
        self.assertIn("1.0.0", text)
        self.assertIn("已证实的安全漏洞", text)


if __name__ == "__main__":
    unittest.main()
