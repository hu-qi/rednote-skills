"""Reproducible labelled-fixture benchmark for RepoDoctor's static rule engine.

Do not confuse fixture accuracy with real-world precision or vulnerability confirmation.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "target" / "release" / ("repodoctor.exe" if os.name == "nt" else "repodoctor")

CASES = [
    # name, relative path, file contents, expected (rule_id,line) or None
    ("workflow-write-all", ".github/workflows/unsafe.yml", "name: test\npermissions: write-all\n", ("RD001", 2)),
    ("workflow-target", ".github/workflows/target.yml", "on:\n  pull_request_target:\n", ("RD002", 2)),
    ("python-shell", "bad.py", "import subprocess\nsubprocess.run(user_input, shell=True)\n", ("RD003", 2)),
    ("javascript-eval", "bad.js", "const output = eval(input);\n", ("RD004", 1)),
    ("private-key-header", "test.pem", "-----BEGIN RSA PRIVATE KEY-----\n", ("RD005", 1)),
    ("python-comment", "good.py", "# subprocess.run(input, shell=True)\n", None),
    ("js-comment", "good.js", "// eval(input)\n", None),
    ("workflow-readonly", ".github/workflows/safe.yml", "permissions: read-all\n", None),
    ("python-safe-subprocess", "safe.py", "import subprocess\nsubprocess.run(['ls'], shell=False)\n", None),
    ("js-safe-code", "safe.js", "const result = JSON.parse(input);\n", None),
]

class RuleBenchmark(unittest.TestCase):
    def test_labelled_fixtures(self):
        if not BIN.is_file():
            self.skipTest("Release binary not built")
        true_positive = false_positive = false_negative = 0
        for name, path, content, expected in CASES:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as temp:
                sample = Path(temp) / path
                sample.parent.mkdir(parents=True, exist_ok=True)
                sample.write_text(content, encoding="utf-8")
                run = subprocess.run([str(BIN), "scan", temp],capture_output=True,text=True,check=True)
                doc = json.loads(run.stdout)
                found = [(f["rule_id"], f["line"]) for f in doc["findings"]]
                if expected:
                    if expected in found:
                        true_positive += 1
                    else:
                        false_negative += 1
                    false_positive += len(found) - int(expected in found)
                else:
                    false_positive += len(found)
                self.assertEqual(found, [expected] if expected else [])
                self.assertFalse(doc["scan"]["truncated"])
        self.assertEqual((true_positive, false_positive, false_negative),(5,0,0))

if __name__ == "__main__":
    unittest.main()
