#!/usr/bin/env python3
"""Verify and explicitly install or roll back a RepoDoctor Skill package."""
import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile

spec = importlib.util.spec_from_file_location("skill_dist", Path(__file__).with_name("skill_dist.py"))
dist = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dist)

def validate_destination(dest):
    dest = Path(dest).expanduser().absolute()
    if dest.name != "repodoctor":
        raise ValueError("installation destination must end in 'repodoctor'")
    if dest.is_symlink() or dest.parent.is_symlink():
        raise ValueError("symlink installation destinations are forbidden")
    dest.parent.mkdir(parents=True, exist_ok=True)
    return dest

def install(archive, destination, replace=False):
    dest = validate_destination(destination)
    # Verify first: never extract unverified payloads.
    manifest = dist.verify(archive)
    backup = dest.with_name(dest.name + ".previous")
    if dest.exists() and not replace:
        raise ValueError("Skill already installed; pass --replace to upgrade")
    if backup.exists():
        raise ValueError("previous-version backup exists; roll back or remove it before upgrading")
    staged = Path(tempfile.mkdtemp(prefix=".repodoctor-staged-", dir=dest.parent))
    moved_old = False
    try:
        with zipfile.ZipFile(archive) as archive_file:
            for member in archive_file.infolist():
                target = staged / member.filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive_file.read(member))
                if member.filename.startswith("bin/") and os.name != "nt":
                    target.chmod(0o755)
        if dest.exists():
            if not dest.is_dir() or dest.is_symlink():
                raise ValueError("existing destination must be a real directory")
            os.replace(dest, backup)
            moved_old = True
        try:
            os.replace(staged, dest)
        except Exception:
            if moved_old and not dest.exists():
                os.replace(backup, dest)
            raise
    finally:
        if staged.exists():
            shutil.rmtree(staged)
    return manifest

def rollback(destination):
    dest = validate_destination(destination)
    backup = dest.with_name(dest.name + ".previous")
    if not backup.is_dir() or backup.is_symlink():
        raise ValueError("no previous version available")
    if not dest.is_dir() or dest.is_symlink():
        raise ValueError("active version is missing or invalid")
    # Preserve displaced version, so rollback can itself be reversed manually.
    displaced = dest.with_name(dest.name + ".replaced")
    if displaced.exists():
        raise ValueError("replaced-version backup already exists")
    os.replace(dest, displaced)
    try:
        os.replace(backup, dest)
    except Exception:
        os.replace(displaced, dest)
        raise

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    installer = commands.add_parser("install")
    installer.add_argument("archive")
    installer.add_argument("--destination", required=True)
    installer.add_argument("--replace", action="store_true")
    rb = commands.add_parser("rollback")
    rb.add_argument("--destination", required=True)
    args = parser.parse_args()
    try:
        if args.command == "install":
            manifest = install(args.archive, args.destination, args.replace)
            print(f"Installed {manifest['name']} {manifest['version']} for {manifest['platform']}")
        else:
            rollback(args.destination)
            print("Restored previous RepoDoctor installation")
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
