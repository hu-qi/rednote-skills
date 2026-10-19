# Evidence contract and SARIF

RepoDoctor produces read-only **static-lead** findings. These are heuristic review leads and are **not** reproduced vulnerabilities, test-confirmed defects, or verified fixes.

## Report formats

```bash
cargo run --release --bin repodoctor -- scan . --format json
cargo run --release --bin repodoctor -- scan . --format markdown
cargo run --release --bin repodoctor -- scan . --format sarif --output repodoctor.sarif
```

SARIF 2.1.0 results include `ruleId`, `level`, `message`, location with line number, and `properties.evidenceLevel=static-lead`, `verified=false`. Rule descriptors are fixed and no source line or secret contents are emitted.

## Limitations and privacy

Files larger than 1 MiB are skipped, symlinks are not followed, and the scanner limits total eligible files to 10,000. A truncated scan must not be interpreted as comprehensive. Simple lexical matching can produce false positives or false negatives; do not automatically create security advisories or PRs based solely on these reports.

Future evidence levels may include validated-static, reproduced, and fixed-and-verified, **only** after collecting explicit test artifacts. No LLM key is required for current functionality.
