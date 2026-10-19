#!/usr/bin/env python3
"""Non-interactive CodeArts smoke / competition submission attempt.

Never prints or uploads model transcripts, repository secrets, or credentials.
Submission receipts require human verification in both marketplaces.
"""
import argparse
import hashlib
import time
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlparse

DEFAULT_PRIMARY = "glm-5.3-flash"
DEFAULT_FALLBACK = "Gemini-3.8-Flash-Medium"
QUOTA_MARKERS = (
    "quota", "insufficient balance", "rate limit", "rate_limit", "too many requests",
    "resource exhausted", "resource_exhausted", "tokens exhausted", "429",
    "额度不足", "额度已用完", "余额不足", "配额不足", "限流", "资源耗尽",
)
ANSI = re.compile(r"\x1b\[[0-9;]*m")
URL = re.compile(r"https?://[^\s\"'<>]+")
SAFE_URL_HOSTS = ("huaweicloud.com", "xiaohongshu.com", "redskillhub.com")


def normalize(text):
    return re.sub(r"[^a-z0-9]", "", text.casefold())


def resolve_model(table, desired):
    """Only use a model actually advertised by codearts models."""
    wanted = normalize(desired)
    for line in ANSI.sub("", table).splitlines():
        columns = line.split()
        if not columns or columns[0].casefold() == "model_id":
            continue
        model_id = columns[0]
        # Match full displayed model ID suffix OR human-readable model name.
        if normalize(model_id.split("/")[-1]) == wanted:
            return model_id
        if any(normalize(column) == wanted for column in columns[1:]):
            return model_id
        if len(columns) > 1 and normalize(" ".join(columns[1:])) == wanted:
            return model_id
    return None


def is_quota_failure(output):
    lower = output.casefold()
    return any(word.casefold() in lower for word in QUOTA_MARKERS)


def allowed_receipts(text):
    """These URLs are only candidate evidence, not confirmed publication."""
    result = []
    for raw in URL.findall(text):
        parsed = urlparse(raw.rstrip(".,);"))
        host = (parsed.hostname or "").casefold()
        if any(host == allowed or host.endswith("." + allowed) for allowed in SAFE_URL_HOSTS):
            clean = parsed._replace(query="", fragment="", params="").geturl()
            if clean not in result:
                result.append(clean)
    return result[:8]


def invoke(command, cwd, timeout):
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(command, 124, "", "CLI_TIMEOUT")


def classify_cli_error(body):
    """Whitelist only error categories; do not expose raw CLI output."""
    lower = body.casefold()
    if is_quota_failure(body):
        return "quota_or_throttling"
    if any(value in lower for value in ("401", "unauthorized", "invalid credential", "invalid ak",
                                        "authentication failed", "鉴权失败", "认证失败", "ak/sk")):
        return "authentication"
    if any(value in lower for value in ("403", "forbidden", "accessdenied", "permission denied",
                                        "not authorized", "无权限", "权限不足")):
        return "authorization"
    if any(value in lower for value in ("timeout", "timed out", "dns", "econnreset", "econnrefused",
                                        "network error", "connection refused", "连接失败")):
        return "network"
    if any(value in lower for value in ("internal server error", "bad gateway",
                                        "service unavailable", "gateway timeout", "503", "502", "500", "504",
                                        "服务异常", "服务器错误", "请求失败")):
        return "service_or_gateway"
    if any(value in lower for value in ("not found", "unknown command", "unsupported",
                                        "unknown option", "not a command")):
        return "cli_incompatible"
    return "unknown"


def diagnose_model_listing(result):
    """Return non-sensitive telemetry only; never copy CLI output to CI artifacts."""
    content = (result.stdout or "") + "\n" + (result.stderr or "")
    low = content.casefold()
    signals = {
        "credential_or_signature": ("ak/sk", "access key", "secret key", "signature", "credential"),
        "account_activation_or_seat": ("seat", "subscription", "activate", "not enabled", "席位", "开通", "订阅"),
        "region_or_endpoint": ("region", "endpoint", "cn-north", "区域"),
        "proxy_or_tls": ("ssl", "tls", "certificate", "proxy", "证书"),
        "model_registry": ("model", "provider", "模型", "供应商"),
        "login_required": ("login", "not logged in", "登录"),
        "noninteractive_or_tty": ("tty", "stdin", "interactive", "terminal", "非交互"),
        "cli_exception": ("typeerror", "exception", "stack trace", "cannot read properties", "panic"),
        "http_5xx": ("500", "502", "503", "504", "internal server error"),
        "http_4xx": ("400", "401", "403", "404", "429"),
    }
    # Lengths, flags, exit code and a short fingerprint cannot reveal AK/SK.
    allowed_error_tokens = {
        "failed", "error", "request", "response", "server", "service", "gateway",
        "timeout", "unavailable", "internal", "authentication", "unauthorized",
        "authorization", "permission", "invalid", "signature", "credentials",
        "model", "models", "provider", "network", "connection", "fetch", "http",
        "https", "axios", "api", "status", "code", "retry", "unknown", "session",
        "region", "endpoint", "proxy", "certificate", "tls", "connect",
        "runtime", "exception", "notfound", "denied", "message", "login",
    }
    safe_keywords = sorted(
        set(re.findall(r"[a-zA-Z]{3,}", low)) & allowed_error_tokens
    )
    # Require HTTP context to avoid mistaking random numeric IDs for HTTP codes.
    status_codes = sorted(set(re.findall(
        r"(?:http(?:/\d(?:\.\d)?)?\s*|status(?:\s+code)?\s*[:=]?\s*)([45]\d\d)\b",
        low,
    )))
    return {
        "exit_code": result.returncode,
        "http_status_codes": status_codes,
        "safe_error_keywords": safe_keywords[:20],
        "stdout_chars": len(result.stdout or ""),
        "stderr_chars": len(result.stderr or ""),
        "output_fingerprint_12": hashlib.sha256(content.encode("utf-8")).hexdigest()[:12],
        "output_shape": (
            "html" if "<html" in low or "<!doctype html" in low else
            "json" if content.lstrip().startswith(("{", "[")) else
            "models_table" if "model_id" in low and "model_name" in low else
            "plain_text" if content.strip() else "empty"
        ),
        "safe_signals": sorted(key for key, patterns in signals.items()
                               if any(pattern in low for pattern in patterns)),
    }


def choose_and_run(prompt, cwd, primary=DEFAULT_PRIMARY, fallback=DEFAULT_FALLBACK, timeout=300):
    models = invoke(["codearts", "models"], cwd, 45)
    list_attempts = 1
    # A CI runner may hit transient CodeArts upstream gateway failures.
    # Retry only service/network/timeout problems, never credential errors.
    while models.returncode and list_attempts < 3:
        category = classify_cli_error(models.stdout + "\n" + models.stderr)
        if category not in ("service_or_gateway", "network"):
            break
        time.sleep(list_attempts * 2)
        models = invoke(["codearts", "models"], cwd, 45)
        list_attempts += 1
    if models.returncode:
        return {"status": "models_failed", "model": None, "text": "",
                "error_kind": classify_cli_error(models.stdout + "\n" + models.stderr),
                "model_list_attempts": list_attempts,
                "model_list_diagnostic": diagnose_model_listing(models),
                "exit": models.returncode}
    primary_id = resolve_model(models.stdout, primary)
    fallback_id = resolve_model(models.stdout, fallback)
    if not primary_id:
        return {
            "status": "primary_model_not_listed",
            "model": None,
            "fallback_listed": bool(fallback_id),
            "text": "",
            "exit": 3,
        }
    attempted = []
    for name in [primary_id, fallback_id]:
        if not name:
            continue
        attempted.append(name)
        # Sandbox is intentional. Never grant unrestricted --auto to a CI agent.
        result = invoke(
            ["codearts", "run", prompt, "--model", name, "--format", "json", "--sandbox"],
            cwd,
            timeout,
        )
        body = result.stdout + "\n" + result.stderr
        if result.returncode == 0 and not is_quota_failure(body):
            return {"status": "cli_completed", "model": name, "attempted": attempted,
                    "text": body, "exit": 0}
        if name == primary_id and is_quota_failure(body) and fallback_id and fallback_id != primary_id:
            continue
        return {
            "status": "quota_exhausted" if is_quota_failure(body) else "cli_failed",
            "model": name, "attempted": attempted, "text": "", "exit": result.returncode or 4,
        }
    return {"status": "no_usable_model", "attempted": attempted, "text": "", "exit": 5}


def build_smoke(root, scratch):
    fixture = scratch / "fixture"
    (fixture / ".github" / "workflows").mkdir(parents=True)
    (fixture / ".github" / "workflows" / "ci.yml").write_text(
        "name: intentionally-unsafe-fixture\non: push\npermissions: write-all\n",
        encoding="utf-8",
    )
    destination = scratch / "codearts-repodoctor-report.json"
    prompt = (
        "这是 CodeArts CLI + RepoDoctor Skill 集成验收。请真正使用已安装的 repodoctor Skill，"
        "调用其 Rust 可执行程序对下面的无敏感信息测试目录做只读扫描，不要仅凭文字猜测结果。"
        "必须调用命令 .codeartsdoer/skills/repodoctor/bin/repodoctor scan "
        + str(fixture) + " --format json --output " + str(destination)
        + " 。不要修改源文件、联网、打印环境变量或读取仓库其他内容。"
        "完成后只回答测试是否找到 RD001，不需要展示任何环境变量。"
    )
    return prompt, destination


def submission_prompt(root):
    # Explicitly from the official Huawei contest submission page.
    return (
        "我正在参加2026华为开发者大赛的小红书Skill创新赛，作品名称 RepoDoctor。"
        "请先将当前目录 skills/repodoctor/SKILL.md 和可复用的 Rust 诊断能力"
        "发布到华为云Skill市场，再使用 redskillhub-upload 发布到小红书Skill市场。"
        "赛题方向：通用赛道/开发工具。作品简介：证据驱动的开源项目风险诊断Skill，"
        "默认只读、离线扫描，输出文件和行号、证据分级与可复用的 JSON/Markdown/SARIF 报告。"
        "开源地址：https://github.com/hu-qi/rednote-skills/tree/main/skills/repodoctor 。"
        "请使用已配置的用户身份进行发布，不得假造上传结果或发布地址。"
        "如果需要用户互动确认、其他凭证或市场功能在CLI不可用，请立即明确报告阻塞，"
        "不要绕过授权，也不要声称已完成发布。"
        "请在完成后返回两个市场各自的公开作品URL或作品ID；仅创建草稿不能算已提交。"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["smoke", "submit"], default="smoke")
    parser.add_argument("--primary", default=DEFAULT_PRIMARY)
    parser.add_argument("--fallback", default=DEFAULT_FALLBACK)
    parser.add_argument("--result", default="codearts-ci-result.json")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    result_file = Path(args.result).resolve()
    result_file.parent.mkdir(parents=True, exist_ok=True)
    summary = {"phase": args.phase, "status": "not_started", "model": None,
               "submission_verified": False, "marketplace_urls_unverified": []}
    try:
        if not os.environ.get("CODEARTS_CLI_AK") or not os.environ.get("CODEARTS_CLI_SK"):
            summary["status"] = "missing_ak_sk_secrets"
            return 2
        root = Path.cwd()
        if args.phase == "smoke":
            with tempfile.TemporaryDirectory(prefix="repodoctor-codearts-ci-") as tmp:
                prompt, output = build_smoke(root, Path(tmp))
                invoked = choose_and_run(prompt, root, args.primary, args.fallback, args.timeout)
                summary["model"] = invoked.get("model")
                summary["status"] = invoked["status"]
                summary["attempted_models"] = invoked.get("attempted", [])
                summary["error_kind"] = invoked.get("error_kind")
                summary["model_list_diagnostic"] = invoked.get("model_list_diagnostic")
                summary["model_list_attempts"] = invoked.get("model_list_attempts")
                if output.is_file():
                    try:
                        report = json.loads(output.read_text(encoding="utf-8"))
                        findings = report.get("findings", [])
                        summary["found_rd001"] = any(f.get("rule_id") == "RD001" for f in findings)
                        summary["report_schema"] = report.get("schema_version")
                    except (ValueError, OSError, TypeError):
                        summary["found_rd001"] = False
                else:
                    summary["found_rd001"] = False
                if invoked["status"] == "cli_completed" and summary["found_rd001"]:
                    summary["status"] = "agent_skill_invocation_verified"
                    return 0
                return 1
        invoked = choose_and_run(submission_prompt(root), root, args.primary, args.fallback,
                                 max(args.timeout, 600))
        summary["model"] = invoked.get("model")
        summary["attempted_models"] = invoked.get("attempted", [])
        summary["marketplace_urls_unverified"] = allowed_receipts(invoked.get("text", ""))
        summary["status"] = ("submission_attempt_needs_marketplace_confirmation"
                             if invoked["status"] == "cli_completed" else invoked["status"])
        # The CLI's answer is not an authoritative confirmation from either marketplace.
        # A manual check of both listings is mandatory.
        return 2
    finally:
        result_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
        print("CodeArts integration status: " + summary["status"])
        print("Model used: " + str(summary.get("model") or "none"))
        print("Results: " + str(result_file))


if __name__ == "__main__":
    sys.exit(main())
