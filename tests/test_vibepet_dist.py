"""Independent VibeCoding Pet ZIP packaging tests."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vibepet_dist", ROOT / "tools/vibepet_dist.py")
dist = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dist)


class VibePetDistTests(unittest.TestCase):
    def test_codearts_package_deterministic_and_valid(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            binary = root / "vibepet"
            binary.write_bytes(b"test-binary")
            a, b = root / "first.zip", root / "second.zip"
            dist.package(binary, "macos-aarch64", a, codearts=True)
            dist.package(binary, "macos-aarch64", b, codearts=True)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            meta = dist.verify(a)
            self.assertEqual(meta["entrypoint"], "bin/vibepet")
            self.assertEqual(meta["layout"], "codearts")
            with zipfile.ZipFile(a) as z:
                self.assertIn("vibecoding-pet/SKILL.md", z.namelist())
                self.assertIn("vibecoding-pet/web/app.js", z.namelist())
                self.assertIn("vibecoding-pet/adapters/codearts-plugin.js", z.namelist())

    def test_flat_windows_binary_and_tampering(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            binary = root / "vibepet.exe"
            binary.write_bytes(b"binary")
            archive = root / "standard.zip"
            dist.package(binary, "windows-x86_64", archive)
            self.assertEqual(dist.verify(archive)["entrypoint"], "bin/vibepet.exe")
            mutated = root / "corrupt.zip"
            with zipfile.ZipFile(archive) as old, zipfile.ZipFile(mutated, "w") as new:
                for info in old.infolist():
                    data = old.read(info)
                    if info.filename == "README.md":
                        data += b"tamper"
                    new.writestr(info, data)
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                dist.verify(mutated)

    def test_reject_path_traversal_and_bad_architecture(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bad = root / "bad.zip"
            with zipfile.ZipFile(bad, "w") as z:
                z.writestr("../SKILL.md", b"wrong")
            with self.assertRaises(ValueError):
                dist.verify(bad)
            binary = root / "test"
            binary.write_bytes(b"test")
            with self.assertRaises(ValueError):
                dist.package(binary, "unsupported-device", root / "none.zip")

    def test_skill_metadata(self):
        self.assertTrue(dist.validate_skill())


if __name__ == "__main__":
    unittest.main()
