# Rednote Skills

Rust-first, portable AI Skills for Huawei CodeArts and compatible agent environments.

## Current priority: RepoDoctor

**RepoDoctor** is a read-only, evidence-first repository inspection Skill. Its Rust scanner detects selected CI permission risks and static code patterns, reports file/line locations, and never executes untrusted repository code. Rule matches are **review leads**, not confirmed vulnerabilities.

```bash
cargo test
cargo run --bin repodoctor -- scan /path/to/repo --markdown
python3 tools/skill_dist.py validate
```

See [RepoDoctor Skill](skills/repodoctor/SKILL.md), [distribution and verification](docs/DISTRIBUTION.md), and [roadmap](docs/TODO.md).

## Multi-Skill roadmap

- RepoDoctor: actively developed for the Huawei × Xiaohongshu Skill competition.
- VibeCoding Pet: planned, no runtime implementation yet.
- Rednote Creator Lab: planned, no runtime implementation yet.

The release workflow bundles independent platform binaries with the Skill, a manifest and per-file SHA-256 hashes. CodeArts platform import remains unverified and must be tested before competition submission.
