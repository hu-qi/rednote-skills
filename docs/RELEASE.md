# RepoDoctor distribution

RepoDoctor uses independent versioned Skill archives for Linux, macOS and Windows. A GitHub Release is built on a pushed vX.Y.Z tag matching Cargo.toml. No tag has been published yet.

Each archive contains repodoctor/SKILL.md, README.md, VERSION and bin/repodoctor(.exe). The release job validates three artifacts, 30-file and 40-MiB limits, and publishes SHA256SUMS. Executable permissions are preserved inside zip archives.

Consumers should verify SHA-256 before unpacking. Version upgrades and rollbacks are **manual** (pin a tag and retain an earlier zip). No auto-update, remote scripts or LLM API are necessary.

Official Huawei CodeArts import and invocation remain unverified and are a separate release gate.
