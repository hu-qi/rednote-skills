# RepoDoctor distribution and verification

RepoDoctor uses a Rust CLI bundled with its portable `SKILL.md`. Build and integrity validation use Python 3's standard library.

## Build

```bash
cargo build --release
python3 tools/skill_dist.py validate
python3 tools/skill_dist.py package --binary target/release/repodoctor --platform macos-aarch64 --output dist/repodoctor-v0.2.0-macos-aarch64.zip
python3 tools/skill_dist.py verify dist/repodoctor-v0.2.0-macos-aarch64.zip
```

Each zip includes a native executable, `SKILL.md`, `README.md`, and `manifest.json` with hashes. The archive limit is 30 entries and 40 MiB uncompressed. Manifest integrity is not a signature: always obtain artifacts and SHA256SUMS from the trusted project release.

## Explicit local installation

Only install archives from a source you trust. Verify their published SHA256SUMS first.

```bash
python3 tools/install_skill.py install dist/repodoctor-v0.2.0-macos-aarch64.zip --destination "$HOME/.agents/skills/repodoctor"
# For an opt-in upgrade:
python3 tools/install_skill.py install dist/repodoctor-v0.2.0-macos-aarch64.zip --destination "$HOME/.agents/skills/repodoctor" --replace
# Restore the backup:
python3 tools/install_skill.py rollback --destination "$HOME/.agents/skills/repodoctor"
```

The installer checks manifest hashes before extraction, rejects traversal and symlink archive entries, never silently overwrites the active Skill, and retains one previous installation at `repodoctor.previous`. Rolled-back versions are saved under `repodoctor.replaced` for inspection. Remove these backup directories explicitly before subsequent upgrades.

The CLI does not automatically configure CodeArts, update skills, authenticate to GitHub, or execute repository code. Users must configure their target Skill runner to load the installed `SKILL.md` and make its packaged native binary available. Official CodeArts import is still unverified.

## Releases

The `repodoctor-distribution` workflow creates per-platform archives on tag `repodoctor/v*`. Manual workflow dispatch produces Actions artifacts, not a public GitHub Release. Do not cut a new version tag without updating the packager's version constant and testing all supported target platforms.

Automatic remote upgrades and signed provenance are not implemented.
