"""Integration tests against the actual compiled Rust loopback service."""
import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
import time
import unittest
from urllib.parse import urlencode


class PetHttpIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        value = os.getenv("VIBEPET_BIN")
        if not value:
            raise unittest.SkipTest("VIBEPET_BIN not configured")
        cls.binary = Path(value).resolve()
        if not cls.binary.is_file():
            raise AssertionError("vibepet binary missing: " + str(cls.binary))
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            cls.port = s.getsockname()[1]
        cls.server = subprocess.Popen(
            [str(cls.binary), "serve", "--port", str(cls.port)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        for _ in range(50):
            if cls.server.poll() is not None:
                raise AssertionError("Rust server exited on startup")
            try:
                conn = http.client.HTTPConnection("127.0.0.1", cls.port, timeout=1)
                conn.request("GET", "/healthz")
                reply = conn.getresponse()
                reply.read()
                conn.close()
                if reply.status == 200:
                    return
            except OSError:
                time.sleep(0.1)
        cls.server.terminate()
        cls.server.wait(timeout=4)
        raise AssertionError("local server health endpoint did not start")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "server"):
            cls.server.terminate()
            try:
                cls.server.wait(timeout=4)
            except subprocess.TimeoutExpired:
                cls.server.kill()
                cls.server.wait(timeout=4)

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=4)
        conn.request(method, path, body=body, headers=headers or {})
        reply = conn.getresponse()
        status, head, data = reply.status, reply.headers, reply.read()
        conn.close()
        return status, head, data

    def post(self, data, headers=None):
        base = {"Content-Type": "application/x-www-form-urlencoded"}
        base.update(headers or {})
        return self.request("POST", "/api/event", urlencode(data), base)

    def test_web_assets_api_and_csp(self):
        status, head, html = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("Content-Security-Policy", head)
        self.assertIn("VibeCoding Pet", html.decode())
        for path in ("/style.css", "/app.js"):
            code, _, asset = self.request("GET", path)
            self.assertEqual(code, 200)
            self.assertTrue(asset)
        _, _, body = self.request("GET", "/api/state")
        self.assertEqual(json.loads(body)["schema_version"], 1)

    def test_inbound_agent_and_demonstration_lifecycle(self):
        code, _, result = self.post({"source": "codearts", "kind": "tool_start"})
        self.assertEqual(code, 200)
        result = json.loads(result)
        self.assertEqual(result["mood"], "busy")
        self.assertEqual(result["last_source"], "codearts")
        code, _, result = self.post(
            {"source": "demo", "kind": "feed"},
            {"Origin": "http://localhost:" + str(self.port)},
        )
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(result)["last_source"], "demo")

    def test_same_origin_and_agent_impersonation(self):
        status, _, _ = self.post(
            {"source": "demo", "kind": "cheer"},
            {"Origin": "https://bad.example"},
        )
        self.assertEqual(status, 403)
        status, _, _ = self.post(
            {"source": "codearts", "kind": "task_success"},
            {"Origin": "http://localhost:" + str(self.port)},
        )
        self.assertEqual(status, 403)
        status, _, _ = self.post(
            {"source": "demo", "kind": "task_success"},
            {"Host": "evil.example:" + str(self.port)},
        )
        self.assertEqual(status, 403)

    def test_unknown_event_extra_sensitive_fields(self):
        for data in (
            {"source": "codearts", "kind": "tool_done", "prompt": "secret"},
            {"source": "opencode", "kind": "unknown"},
        ):
            status, _, _ = self.post(data)
            self.assertEqual(status, 400)
        status, _, _ = self.post({"source": "codearts", "kind": "feed"})
        self.assertEqual(status, 403)

    def test_cli_status(self):
        proc = subprocess.run(
            [str(self.binary), "status", "--port", str(self.port)],
            capture_output=True, text=True, check=True, timeout=5,
        )
        self.assertIn("schema_version", proc.stdout)


if __name__ == "__main__":
    unittest.main()
