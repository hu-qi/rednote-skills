import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class SarifSmoke(unittest.TestCase):
    def test_report_and_evidence_contract(self):
        binary = ROOT / "target" / "release" / ("repodoctor.exe" if __import__("os").name == "nt" else "repodoctor")
        if not binary.is_file():
            self.skipTest("release CLI not built")
        with tempfile.TemporaryDirectory() as temp:
            repository = Path(temp)
            (repository / ".github" / "workflows").mkdir(parents=True)
            (repository / ".github" / "workflows" / "ci.yml").write_text("permissions: write-all\n", encoding="utf-8")
            (repository / "ignored.py").write_text("# subprocess.run(user, shell=True)\n", encoding="utf-8")
            proc = subprocess.run([str(binary), "scan", temp, "--format", "sarif"],check=True,capture_output=True,text=True)
            result = json.loads(proc.stdout)
            self.assertEqual(result["version"], "2.1.0")
            run = result["runs"][0]
            self.assertEqual(len(run["results"]),1)
            lead = run["results"][0]
            self.assertEqual(lead["ruleId"],"RD001")
            self.assertFalse(lead["properties"]["verified"])
            self.assertEqual(lead["properties"]["evidenceLevel"], "static-lead")
            self.assertEqual(lead["locations"][0]["physicalLocation"]["region"]["startLine"],1)
            self.assertEqual(run["properties"]["filesScanned"],2)

if __name__=="__main__":
    unittest.main()
