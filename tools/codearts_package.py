#!/usr/bin/env python3
"""Build a CodeArts-importable Skill ZIP from a verified RepoDoctor release archive."""
import argparse
from pathlib import Path
import sys
import zipfile

from skill_dist import MAX_FILES, SLUG, verify

CODEARTS_MAX_ZIP_BYTES = 5 * 1024 * 1024


def build(source: Path, destination: Path) -> None:
    manifest = verify(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(destination, "w") as output:
        members = original.infolist()
        if len(members) > MAX_FILES:
            raise ValueError("too many Skill files")
        for member in members:
            # CodeArts requires the top-level directory name to match Skill name.
            info = zipfile.ZipInfo(f"{SLUG}/{member.filename}", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = member.external_attr
            output.writestr(info, original.read(member.filename), compresslevel=9)
    validate(destination)
    print(
        f"CodeArts ZIP: {destination}, {manifest['platform']}, "
        f"{destination.stat().st_size} bytes"
    )


def validate(package: Path) -> None:
    if package.stat().st_size > CODEARTS_MAX_ZIP_BYTES:
        raise ValueError("CodeArts import ZIP exceeds 5 MiB")
    with zipfile.ZipFile(package) as archive:
        files = archive.infolist()
        if len(files) > MAX_FILES:
            raise ValueError("Skill package exceeds 30 files")
        if not files or not all(
            file.filename.startswith(f"{SLUG}/")
            and file.filename != f"{SLUG}/"
            for file in files
        ):
            raise ValueError("CodeArts ZIP must contain repodoctor/ root directory")
        if f"{SLUG}/SKILL.md" not in archive.namelist():
            raise ValueError("SKILL.md missing inside repodoctor/")
        if f"{SLUG}/manifest.json" not in archive.namelist():
            raise ValueError("release manifest missing")
        total = sum(file.file_size for file in files)
        if total > 40 * 1024 * 1024:
            raise ValueError("competition uncompressed limit exceeded")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    try:
        if args.verify:
            validate(args.archive)
        else:
            if args.output is None:
                parser.error("--output is required for packaging")
            build(args.archive, args.output)
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
