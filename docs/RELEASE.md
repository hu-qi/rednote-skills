# RepoDoctor release and installation

The implemented distribution system is documented in [DISTRIBUTION.md](DISTRIBUTION.md).

## Current verification

- GitHub Actions CI produced Linux x86_64, macOS ARM64 and Windows x86_64 ZIP artifacts for RepoDoctor v0.2.0 on PR #4.
- Each archive contains independent SKILL.md, README.md, a native binary and manifest.json with SHA-256 file hashes.
- Python packager verifies all file hashes, validates paths, and enforces at most 30 files and 40 MiB uncompressed.
- Local installation is **explicit**; verified archives can be installed or upgraded with tools/install_skill.py, and the previous version can be restored.
- Package-level hashes are not digital signatures. Obtain archives from a trusted GitHub Actions run or release.

## Official release workflow

The existing .github/workflows/release.yml triggers when a tag matching **repodoctor/v*** is pushed. Its four-platform matrix targets:

- linux-x86_64
- macos-x86_64
- macos-aarch64
- windows-x86_64

The publish job creates release assets and SHA256SUMS. The version encoded in the tag must align with Cargo.toml and tools/skill_dist.py. **No v0.2.0 tagged release has been published or verified yet**.

CI package artifacts and tagged GitHub Releases are separate distribution mechanisms. Do not claim the release workflow has passed until a tagged run succeeds.

## Competition compatibility

Huawei CodeArts installation, recognition of SKILL.md, executable invocation permissions and end-to-end host compatibility still require a manual platform acceptance test. Passing GitHub CI alone does not establish CodeArts compatibility. See [COMPETITION.md](COMPETITION.md).
