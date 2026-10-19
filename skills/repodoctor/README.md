# RepoDoctor v0.2

Rust-only, dependency-free offline repository risk triage. Designed to be packaged as a portable Agent Skill, with no API key required.

Run from this repository:

```bash
cargo run --bin repodoctor -- validate-skill skills/repodoctor
cargo run --bin repodoctor -- scan . --format json
cargo run --bin repodoctor -- scan . --format markdown
cargo test --all-targets
```

Tagged GitHub Releases package SKILL.md together with native Linux/macOS/Windows executables and SHA256SUMS. Install the platform archive and point your Skill runtime to the extracted repodoctor folder. Official Huawei CodeArts compatibility has not yet been tested.

Current rules are limited static *leads*, not reproduced vulnerabilities. RepoDoctor does not clone GitHub URLs, call LLMs, run target code, apply patches, or create PRs. Scans at most 10,000 eligible UTF-8 files up to 1 MiB each; symlinks are skipped.
