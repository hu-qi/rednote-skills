# Architecture and distribution

One monorepo, multiple independent Skills in `skills/<slug>/SKILL.md`. Shared Rust workspace binaries and libraries belong under `src/` initially; split into `crates/` when there are two genuine consumers.

## Distribution
- Each Skill remains separately installable. A packaged release must bundle its SKILL.md, references, a platform executable, checksum and manifest.
- Publish versioned GitHub Releases only from reviewed tags; do not silently push upgrades to installed users.
- Manifest should specify `slug`, semantic version, minimum runtime requirements, supported platforms, SHA-256 and artifact URLs.
- Stable channels: `stable`, `beta`; pin exact versions, support upgrade and rollback. No remote code execution without opt-in.
- Keep the submission-specific zip under competition limits (30 files, 40 MB). Large binaries should be downloaded only by informed users and may not be suitable for official contest submission.
- LLM optional; default deterministic offline mode; secrets via local environment or GitHub Actions Secrets, never commit or print API keys.
- Add future integration adapters without turning Skill files into remotely fetched executable instructions.

## Security
Read-only by default. Treat user-controlled repository content as untrusted. Depend on explicit consent for clone, test execution, patching, PRs and distribution.
