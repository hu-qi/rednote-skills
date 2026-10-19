# RepoDoctor reproducible distributions

RepoDoctor is a Rust CLI bundled alongside its portable SKILL.md. Source remains the authoritative artifact.

## Build and verify

```bash
cargo build --release
python3 tools/skill_dist.py validate
python3 tools/skill_dist.py package --binary target/release/repodoctor --platform macos-aarch64 --output dist/repodoctor-v0.1.0-macos-aarch64.zip
python3 tools/skill_dist.py verify dist/repodoctor-v0.1.0-macos-aarch64.zip
```

The zip contains `SKILL.md`, `README.md`, `bin/repodoctor` (or `.exe`) and `manifest.json`. Manifest hashes protect payload integrity; signed provenance is future work. The archive is limited to <= 30 entries and <= 40 MiB uncompressed. The binary is limited to 30 MiB.

Builds are published by the `repodoctor-distribution` workflow on `repodoctor/v*` tags; manual dispatch produces downloadable Actions artifacts but does not publish a Release. Current release version is 0.1.0. Do not tag a different version without updating VERSION in the packager.

## Install

Download the archive appropriate for your platform and verify the published SHA256SUMS before extracting. Run `python3 tools/skill_dist.py verify <archive>` if the source checkout is available. Extract into a **user-selected** skills directory and configure CodeArts or another compatible Skill runner to load the extracted `SKILL.md`; the environment must be able to execute the platform binary in `bin/`.

The specific CodeArts deployment/import flow is not yet independently verified. Do not claim official marketplace publication or compatibility based on GitHub CI alone.

## Upgrade policy

Users pin versions. Installation/upgrade is explicit only; no self-update or remote script execution. Rollback is achieved by reinstalling an earlier verified archive. Automatic updater is planned, not shipped.
