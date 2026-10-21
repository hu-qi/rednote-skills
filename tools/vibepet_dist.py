#!/usr/bin/env python3
"""Deterministic, zero-dependency VibeCoding Pet Skill ZIP builder/verifier."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/vibecoding-pet"
NAME = "vibecoding-pet"
VERSION = "0.1.0"
CODEARTS_ZIP_LIMIT = 5 * 1024 * 1024
UNPACKED_LIMIT = 40 * 1024 * 1024
FILES = (
    "SKILL.md", "README.md", "web/index.html", "web/app.js", "web/style.css",
    "adapters/codearts-plugin.js", "adapters/opencode-plugin.js",
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def validate_skill(root=SKILL):
    doc = Path(root) / "SKILL.md"
    if not doc.is_file() or doc.is_symlink():
        raise ValueError("regular SKILL.md required")
    text = doc.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("YAML frontmatter required")
    head = text.split("---", 2)[1]
    metadata = {}
    for line in head.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    if metadata.get("name") != NAME or len(metadata.get("description", "")) < 20:
        raise ValueError("invalid Skill name/description")
    return True


def members(package):
    with zipfile.ZipFile(package) as z:
        infos = z.infolist()
        if not infos or len(infos) > 20:
            raise ValueError("unexpected ZIP file count")
        files = {}
        unpacked = 0
        for info in infos:
            name = info.filename
            path = PurePosixPath(name)
            if (name in files or path.is_absolute() or "\\" in name or
                    name.startswith("/") or
                    any(piece in (".", "..") for piece in name.split("/"))):
                raise ValueError("unsafe or duplicate ZIP path")
            if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("ZIP directory/symlink forbidden")
            unpacked += info.file_size
            if unpacked > UNPACKED_LIMIT:
                raise ValueError("unpacked archive too large")
            files[name] = z.read(info)
        return files


def package(binary, platform, output, codearts=False):
    validate_skill()
    if platform not in (
        "linux-x86_64", "macos-aarch64", "macos-x86_64", "windows-x86_64",
    ):
        raise ValueError("unsupported target platform")
    binary = Path(binary)
    if not binary.is_file() or binary.is_symlink():
        raise ValueError("regular binary required")
    prefix = NAME + "/" if codearts else ""
    executable = "vibepet.exe" if platform.startswith("windows") else "vibepet"
    entries = {}
    for relative in FILES:
        path = SKILL / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError("unsafe/missing Skill file: " + relative)
        entries[prefix + relative] = path.read_bytes()
    entries[prefix + "bin/" + executable] = binary.read_bytes()
    manifest = {
        "schema_version": 1,
        "name": NAME,
        "version": VERSION,
        "platform": platform,
        "layout": "codearts" if codearts else "flat",
        "entrypoint": "bin/" + executable,
        "files": {name[len(prefix):]: sha(data) for name, data in sorted(entries.items())},
    }
    entries[prefix + "manifest.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as z:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (
                0o100755 if "/bin/" in name or name.startswith("bin/") else 0o100644
            ) << 16
            z.writestr(info, data, compresslevel=9)
    if codearts and output.stat().st_size > CODEARTS_ZIP_LIMIT:
        output.unlink(missing_ok=True)
        raise ValueError("CodeArts 5 MiB ZIP limit exceeded")
    verify(output)
    return manifest


def verify(package):
    package = Path(package)
    found = members(package)
    candidates = [prefix for prefix in ("", NAME + "/")
                  if prefix + "manifest.json" in found]
    if len(candidates) != 1:
        raise ValueError("unexpected Skill archive root")
    prefix = candidates[0]
    manifest = json.loads(found[prefix + "manifest.json"].decode("utf-8"))
    if manifest.get("name") != NAME or manifest.get("version") != VERSION:
        raise ValueError("manifest identity mismatch")
    if manifest.get("layout") != ("codearts" if prefix else "flat"):
        raise ValueError("manifest layout mismatch")
    if prefix and package.stat().st_size > CODEARTS_ZIP_LIMIT:
        raise ValueError("oversized CodeArts ZIP")
    payload = {name[len(prefix):]: data for name, data in found.items()
               if name != prefix + "manifest.json" and name.startswith(prefix)}
    if set(payload) != set(manifest.get("files", {})):
        raise ValueError("missing/extra payload")
    for name, data in payload.items():
        if sha(data) != manifest["files"][name]:
            raise ValueError("SHA-256 mismatch for " + name)
    exe = "vibepet.exe" if manifest.get("platform") == "windows-x86_64" else "vibepet"
    expected = set(FILES) | {"bin/" + exe}
    if set(payload) != expected or manifest.get("entrypoint") != "bin/" + exe:
        raise ValueError("wrong payload or executable")
    if not payload["SKILL.md"].startswith(b"---\nname: vibecoding-pet\n"):
        raise ValueError("invalid Skill frontmatter")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    packer = commands.add_parser("package")
    packer.add_argument("--binary", required=True)
    packer.add_argument("--platform", required=True)
    packer.add_argument("--output", required=True)
    packer.add_argument("--codearts", action="store_true")
    checker = commands.add_parser("verify")
    checker.add_argument("path")
    args = parser.parse_args()
    if args.command == "package":
        info = package(args.binary, args.platform, args.output, args.codearts)
        print("Packaged", info["name"], info["version"], info["platform"])
    else:
        info = verify(args.path)
        print("Verified", info["name"], info["version"], info["layout"])


if __name__ == "__main__":
    main()
