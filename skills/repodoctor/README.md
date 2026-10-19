# RepoDoctor Skill v0.1.0

Runs locally, without network connectivity or LLM credentials.

Example from the source checkout:

```bash
cargo run --release --bin repodoctor -- scan . --markdown
```

From a release zip, replace the command with `bin/repodoctor scan /path/to/repo --markdown` or `bin/repodoctor.exe` on Windows.

The scan reads the repository without executing it and emits static review leads. It is not a vulnerability certification, and no auto-fix engine is included yet.

## Install and verify

See [distribution documentation](../../docs/DISTRIBUTION.md). Each platform archive contains its own SKILL.md and executable.
