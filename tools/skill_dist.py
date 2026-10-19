#!/usr/bin/env python3
"""Deterministic, dependency-free RepoDoctor Skill package builder and verifier."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import sys
import zipfile

SLUG = "repodoctor"
VERSION = "0.1.0"
MAX_FILES = 30
MAX_BYTES = 40 * 1024 * 1024
BINARY_LIMIT = 30 * 1024 * 1024

def digest(data):
    return hashlib.sha256(data).hexdigest()

def validate_skill(skill):
    skill = Path(skill)
    doc = skill / "SKILL.md"
    if not doc.is_file() or doc.is_symlink():
        raise ValueError("SKILL.md missing or is a symlink")
    data = doc.read_text(encoding="utf-8")
    if not data.startswith("---\n") or "\n---\n" not in data[4:]:
        raise ValueError("SKILL.md missing YAML frontmatter")
    header = data.split("---", 2)[1]
    fields = {}
    for line in header.splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    if fields.get("name") != SLUG or not fields.get("description"):
        raise ValueError("SKILL.md must contain name: repodoctor and description")
    return True

def build(skill, binary, destination, platform):
    skill = Path(skill)
    binary = Path(binary)
    validate_skill(skill)
    if not binary.is_file() or binary.is_symlink():
        raise ValueError("binary missing or is a symlink")
    if binary.stat().st_size > BINARY_LIMIT:
        raise ValueError("binary exceeds 30 MiB limit")
    entries = {}
    for path in sorted(skill.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlinks not allowed: {path}")
        if path.is_file():
            rel = path.relative_to(skill).as_posix()
            if rel.startswith(".") or "/." in rel:
                continue
            entries[rel] = path.read_bytes()
    binary_name = "repodoctor.exe" if platform.startswith("windows-") else "repodoctor"
    entries["bin/" + binary_name] = binary.read_bytes()
    # Manifest contains hashes for every payload entry, excluding itself.
    manifest = {
        "schema_version": 1,
        "name": SLUG,
        "version": VERSION,
        "platform": platform,
        "entrypoint": "bin/" + binary_name,
        "files": {name: digest(data) for name, data in sorted(entries.items())},
        "installer_policy": "explicit-user-consent",
    }
    entries["manifest.json"] = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    if len(entries) > MAX_FILES or sum(map(len, entries.values())) > MAX_BYTES:
        raise ValueError("package exceeds competition limits (30 files / 40 MiB)")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w") as z:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if name.startswith("bin/") else 0o644) << 16
            z.writestr(info, data, compresslevel=9)
    verify(destination)
    return manifest

def verify(package):
    with zipfile.ZipFile(package) as z:
        members = z.infolist()
        names = [m.filename for m in members]
        if len(names) != len(set(names)) or len(names) > MAX_FILES:
            raise ValueError("duplicate entries or file-count limit exceeded")
        for member in members:
            name = member.filename
            p = PurePosixPath(name)
            mode = member.external_attr >> 16
            if (p.is_absolute() or ".." in p.parts or "\\" in name or
                    name.startswith(".") or name.endswith("/") or
                    stat.S_ISLNK(mode)):
                raise ValueError(f"unsafe archive entry: {name}")
        if sum(m.file_size for m in members) > MAX_BYTES:
            raise ValueError("uncompressed package exceeds 40 MiB")
        if "manifest.json" not in names:
            raise ValueError("manifest missing")
        manifest = json.loads(z.read("manifest.json"))
        if manifest.get("schema_version") != 1 or manifest.get("name") != SLUG:
            raise ValueError("invalid manifest")
        payload = set(names) - {"manifest.json"}
        expected = manifest.get("files")
        if not isinstance(expected, dict) or set(expected) != payload:
            raise ValueError("manifest inventory mismatch")
        if manifest.get("entrypoint") not in payload or "SKILL.md" not in payload:
            raise ValueError("Skill entrypoint or SKILL.md missing")
        for name in payload:
            if digest(z.read(name)) != expected[name]:
                raise ValueError(f"integrity check failed: {name}")
        return manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    v = commands.add_parser("validate")
    v.add_argument("--skill", default="skills/repodoctor")
    p = commands.add_parser("package")
    p.add_argument("--skill", default="skills/repodoctor")
    p.add_argument("--binary", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--platform", required=True)
    c = commands.add_parser("verify")
    c.add_argument("archive")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            validate_skill(args.skill)
            print("Skill frontmatter valid")
        elif args.command == "package":
            manifest = build(args.skill, args.binary, args.output, args.platform)
            print(json.dumps({"name": manifest["name"], "version": manifest["version"],
                              "files": len(manifest["files"]) + 1, "output": args.output}))
        else:
            manifest = verify(args.archive)
            print(json.dumps({"verified": True, "name": manifest["name"],
                              "version": manifest["version"], "platform": manifest["platform"]}))
    except (ValueError, OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
