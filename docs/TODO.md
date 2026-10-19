# RepoDoctor competition delivery plan

## P0 — Source and CI
- [x] Rust-first read-only diagnostic engine and structured reports
- [x] Unit tests and Linux CI smoke checks
- [x] Versioned, independently packaged Skill archives with manifests and SHA-256
- [x] Offline archive verifier, input constraints, traversal and tampering tests
- [ ] Restore strict rustfmt checks (CI currently formats source before lint)
- [ ] Verify release matrix on four OS / architecture runners
- [ ] Add fixture corpus for accuracy and false-positive measurement
- [ ] Manual Huawei CodeArts Skill import / real invocation evidence

## P1 — Evidence-first diagnosis
- [ ] Parse languages / GitHub Action YAML rather than pattern matching
- [ ] Read-only GitHub ingestion with strict authorization and rate limits
- [ ] Evidence classification and reproducer / isolated verified repair
- [ ] SARIF and redacted shareable report
- [ ] Evaluate on real public repos and publish measured precision

## P1 — Skill distribution
- [ ] Release version consistency / tag guard
- [ ] Install / update / rollback CLI with manifest verification and user opt-in
- [ ] Signing / provenance and reproducibility across builders
- [ ] User testing with CodeArts and competition submission checklist

## P2 — Other Skills
- [ ] VibeCoding Pet
- [ ] Rednote Creator Lab
- [ ] Optional LLM provider with redaction and quotas
