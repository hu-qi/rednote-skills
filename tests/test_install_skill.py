import importlib.util
from pathlib import Path
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
spec = importlib.util.spec_from_file_location("install_skill", TOOLS / "install_skill.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skill = self.root / "source"
        self.skill.mkdir()
        (self.skill / "SKILL.md").write_text("---\nname: repodoctor\ndescription: Safe code scan\n---\n# RepoDoctor\n")
        self.binary = self.root / "bin"
        self.binary.write_bytes(b"version 1")
        self.archive = self.root / "skill.zip"
        module.dist.build(self.skill, self.binary, self.archive, "linux-x86_64")
        self.destination = self.root / "skills" / "repodoctor"

    def test_install_requires_opt_in_to_replace(self):
        module.install(self.archive, self.destination)
        self.assertTrue((self.destination / "SKILL.md").exists())
        with self.assertRaisesRegex(ValueError, "already installed"):
            module.install(self.archive, self.destination)

    def test_upgrade_then_rollback(self):
        module.install(self.archive, self.destination)
        self.binary.write_bytes(b"version 2")
        module.dist.build(self.skill, self.binary, self.archive, "linux-x86_64")
        module.install(self.archive, self.destination, replace=True)
        self.assertEqual((self.destination / "bin" / "repodoctor").read_bytes(), b"version 2")
        module.rollback(self.destination)
        self.assertEqual((self.destination / "bin" / "repodoctor").read_bytes(), b"version 1")

    def test_bad_archive_does_not_replace_existing(self):
        module.install(self.archive, self.destination)
        self.archive.write_bytes(b"invalid")
        with self.assertRaises(Exception):
            module.install(self.archive, self.destination, replace=True)
        self.assertTrue((self.destination / "SKILL.md").is_file())

    def test_reject_symlink_destination(self):
        parent = self.root / "skills"
        parent.mkdir()
        (parent / "repodoctor").symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            module.install(self.archive, self.destination)

if __name__ == "__main__":
    unittest.main()
