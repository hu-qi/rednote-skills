# Huawei CodeArts / Rednote competition acceptance checklist

- [x] Local Rust Skill with name and description frontmatter and read-only CLI
- [x] JSON and Markdown outputs with file/line positions
- [x] Three-platform CI test/build matrix and tag-gated zip distribution pipeline
- [ ] Actually publish a release tag and verify downloaded archives
- [ ] Import Skill into CodeArts and execute from the host runtime
- [x] Build a dedicated CodeArts ZIP layout with repodoctor/ root and 5 MiB compressed limit in CI
- [ ] Test CodeArts import, filesystem, OS, permissions and actual command execution on the platform
- [ ] Establish labeled evaluation dataset; report false positives and false negatives
- [ ] Produce authorized before/after reproducibility demo
- [ ] Test at least two external repositories with representative language/CI patterns
- [ ] Collect genuine, consented user feedback and publication evidence

Important: current static findings are review leads, not proven vulnerabilities. Do not submit score claims without benchmark evidence.
