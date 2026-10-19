import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

MODULE = Path(__file__).resolve().parents[1] / "tools" / "skill_dist.py"
spec = importlib.util.spec_from_file_location("skill_dist", MODULE)
dist = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dist)

class SkillDistTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skill = self.root / "skill"
        self.skill.mkdir()
        (self.skill / "SKILL.md").write_text("---\nname: repodoctor\ndescription: Read-only repository diagnostics\n---\n# RepoDoctor\n")
        self.binary = self.root / "repodoctor"
        self.binary.write_bytes(b"fake executable for packaging test")
        self.archive = self.root / "skill.zip"

    def test_deterministic_roundtrip(self):
        dist.build(self.skill, self.binary, self.archive, "linux-x86_64")
        first = self.archive.read_bytes()
        self.assertEqual(dist.verify(self.archive)["name"], "repodoctor")
        dist.build(self.skill, self.binary, self.archive, "linux-x86_64")
        self.assertEqual(first, self.archive.read_bytes())

    def test_reject_corrupt_archive(self):
        dist.build(self.skill, self.binary, self.archive, "linux-x86_64")
        with zipfile.ZipFile(self.archive) as z:
            contents = {name: z.read(name) for name in z.namelist()}
        contents["SKILL.md"] = b"tampered"
        with zipfile.ZipFile(self.archive, "w") as z:
            for name, body in contents.items():
                z.writestr(name, body)
        with self.assertRaisesRegex(ValueError, "integrity"):
            dist.verify(self.archive)

    def test_reject_traversal(self):
        with zipfile.ZipFile(self.archive, "w") as z:
            z.writestr("../escape", "bad")
            z.writestr("manifest.json", json.dumps({"schema_version": 1, "name": "repodoctor"}))
        with self.assertRaisesRegex(ValueError, "unsafe"):
            dist.verify(self.archive)

    def test_reject_untrusted_symlink(self):
        (self.skill / "link").symlink_to(self.binary)
        with self.assertRaisesRegex(ValueError, "symlink"):
            dist.build(self.skill, self.binary, self.archive, "linux-x86_64")

    def test_requires_frontmatter(self):
        (self.skill / "SKILL.md").write_text("# invalid\n")
        with self.assertRaisesRegex(ValueError, "frontmatter"):
            dist.validate_skill(self.skill)

if __name__ == "__main__":
    unittest.main()
