import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


import sys
sys.path.insert(0, str(ROOT / "tools"))
import codearts_package as codearts
import skill_dist as dist


class CodeArtsPackageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        skill = self.root / "skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            "---\nname: repodoctor\ndescription: Safe and read-only repository review\n---\n# RepoDoctor\n",
            encoding="utf-8",
        )
        (skill / "README.md").write_text("test")
        binary = self.root / "repodoctor"
        binary.write_bytes(b"fake binary used only for packaging test")
        self.original = self.root / "repodoctor-linux.zip"
        dist.build(skill, binary, self.original, "linux-x86_64")
        self.codearts_archive = self.root / "repodoctor-codearts.zip"

    def test_contains_required_top_level_directory(self):
        codearts.build(self.original, self.codearts_archive)
        codearts.validate(self.codearts_archive)
        with zipfile.ZipFile(self.codearts_archive) as archive:
            self.assertIn("repodoctor/SKILL.md", archive.namelist())
            self.assertIn("repodoctor/manifest.json", archive.namelist())
            self.assertIn("repodoctor/bin/repodoctor", archive.namelist())
            self.assertNotIn("SKILL.md", archive.namelist())

    def test_reject_flat_archive_on_import(self):
        with self.assertRaisesRegex(ValueError, "repodoctor/"):
            codearts.validate(self.original)

    def test_invalid_source_is_not_repackaged(self):
        with zipfile.ZipFile(self.original, "w") as archive:
            archive.writestr("../escape", "bad")
        with self.assertRaises(ValueError):
            codearts.build(self.original, self.codearts_archive)


if __name__ == "__main__":
    unittest.main()
