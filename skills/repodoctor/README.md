# RepoDoctor Skill

Rust-first evidence-driven repository preflight (v0.1).

Run: `cargo run --bin repodoctor -- scan . --markdown`

Rules: RD001 (write-all), RD002 (pull_request_target), RD003 (Python shell=True), RD004 (JS eval), RD005 (private-key PEM delimiter).

Limitations: heuristic-only; never runs target code or makes modifications. Rust source-level rules are future work.
