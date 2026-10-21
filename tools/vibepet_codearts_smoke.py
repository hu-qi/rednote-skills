#!/usr/bin/env python3
"""Real CodeArts CLI plugin-to-Rust-pet acceptance on a credentialed CI runner.

No prompts, model transcripts, AK/SK or Session IDs are uploaded or printed.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

PORT = 7878
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(os.environ.get("RUNNER_TEMP", ".")) / "vibepet-codearts-result.json"


def state():
    with urlopen("http://127.0.0.1:7878/api/state", timeout=3) as reply:
        return json.load(reply)


def main():
    result = {
        "phase": "codearts-hook-real-integration",
        "status": "started",
        "rust_server_healthy": False,
        "codearts_cli_completed": False,
        "codearts_hook_events_found": False,
        "observed_kinds": [],
        "contains_private_payload": False,
    }
    binary = ROOT / "target/release/vibepet"
    process = None
    try:
        if not binary.is_file():
            result["status"] = "missing_binary"
            return 1
        if not (os.environ.get("CODEARTS_CLI_AK") and os.environ.get("CODEARTS_CLI_SK")):
            result["status"] = "missing_codearts_credentials"
            return 2
        # The Rust server has no need for any cloud credentials.
        environment = {
            key: value for key, value in os.environ.items()
            if key not in ("CODEARTS_CLI_AK", "CODEARTS_CLI_SK")
        }
        process = subprocess.Popen(
            [str(binary), "serve", "--port", str(PORT)],
            cwd=ROOT, env=environment,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        for _ in range(50):
            if process.poll() is not None:
                result["status"] = "rust_server_exited"
                return 1
            try:
                state()
                result["rust_server_healthy"] = True
                break
            except (OSError, ValueError):
                time.sleep(0.12)
        if not result["rust_server_healthy"]:
            result["status"] = "server_unreachable"
            return 1

        models = subprocess.run(
            ["codearts", "models"], cwd=ROOT,
            check=False, capture_output=True, text=True, timeout=60,
        )
        if models.returncode:
            result["status"] = "models_unavailable"
            return 1
        from codearts_ci import resolve_model
        model = resolve_model(models.stdout, os.environ.get(
            "CODEARTS_PRIMARY_MODEL", "huaweicloud-maas/glm-5.3"))
        if not model:
            result["status"] = "requested_model_not_listed"
            return 1
        # Deliberately benign text-only interaction. No tools, reads or writes.
        prompt = (
            "请只用简体中文回复“宠物连通性验证”，不要调用任何工具，"
            "不要修改或访问文件、网络或环境变量。"
        )
        try:
            execution = subprocess.run(
                ["codearts", "run", prompt, "--model", model,
                 "--format", "json", "--sandbox"],
                cwd=ROOT, check=False, capture_output=True, text=True, timeout=220,
            )
        except subprocess.TimeoutExpired:
            result["status"] = "codearts_timeout"
            return 1
        result["codearts_cli_completed"] = execution.returncode == 0
        # Only event source and fixed event kinds are published as telemetry.
        pet = state()
        codearts = [event["kind"] for event in pet["history"]
                   if event.get("source") == "codearts"]
        result["observed_kinds"] = codearts[:12]
        result["codearts_hook_events_found"] = bool(codearts)
        # The endpoint accepts only enumerated fields. No payload can be stored.
        result["contains_private_payload"] = any(
            set(e) != {"number", "source", "kind"} for e in pet["history"]
        )
        if result["codearts_cli_completed"] and result["codearts_hook_events_found"] and not result["contains_private_payload"]:
            result["status"] = "real_codearts_hook_verified"
            return 0
        result["status"] = (
            "codearts_invocation_failed" if not result["codearts_cli_completed"]
            else "codearts_hook_not_observed"
        )
        return 1
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print("VibeCoding Pet CodeArts Hook status: " + result["status"])
        print("Hook events observed: " + str(result["codearts_hook_events_found"]))


if __name__ == "__main__":
    sys.exit(main())
