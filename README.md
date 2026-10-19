# Rednote Skills

Rust-first, independently distributable agent Skills. The competition priority is **RepoDoctor**. VibeCoding Pet and Rednote Creator Lab remain separately planned.

## RepoDoctor v0.2 (development)

```bash
cargo run --bin repodoctor -- validate-skill skills/repodoctor
cargo run --bin repodoctor -- scan . --format json
cargo run --bin repodoctor -- scan . --format markdown
cargo test --all-targets
```

[Skill instructions](skills/repodoctor/SKILL.md) · [Release process](docs/RELEASE.md) · [Competition checklist](docs/COMPETITION.md) · [Roadmap](docs/TODO.md)

Results are **static leads**, not confirmed vulnerabilities. The scanner does not execute target code, upload files or modify the scanned repository. Read-only by default; explicitly authorize any future patching or network integration.

CodeArts compatibility, benchmark accuracy and a published tagged Release still require verification.
