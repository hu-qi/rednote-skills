# Roadmap

## P0 — RepoDoctor competition entry
- [x] Initialize multi-Skill Rust-first monorepo
- [x] Implement offline local-file preflight rules and JSON/Markdown output
- [ ] Verify GitHub Actions CI on PR and fix compiler/test issues
- [ ] Prove Huawei CodeArts imports and invokes SKILL.md
- [ ] Reduce false positives using AST/tree-sitter or precise parsing
- [ ] Define benchmark corpus with true positives/false positives
- [ ] Add GitHub repository read-only ingestion with authorization
- [ ] Capture before/after proof using isolated, explicitly approved tests

## P1 — Distribution
- [ ] Skill manifest schema and integrity validation
- [ ] Semantic-versioned release packaging for Linux/macOS/Windows
- [ ] Installer/updater with checksum and rollback
- [ ] Compatibility tests across CodeArts and supported Skill runtimes

## P2 — Future Skills
- [ ] VibeCoding Pet: event schema, hook integration, privacy-safe display
- [ ] Rednote Creator Lab: drafts, factual provenance, feedback loop
- [ ] Optional LLM provider abstraction, redaction, cost/time limits
