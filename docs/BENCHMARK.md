# RepoDoctor v0.2 fixture benchmark

Run with:

```bash
cargo build --release --locked
python3 -m unittest discover -s tests -p 'test_rule_benchmark.py' -v
```

The labelled corpus has **10 synthetic single-file repositories**: five positive and five negative examples spanning RD001–RD005. CI asserts all five known matches and no findings on five negative controls. These are developer-authored fixtures, not independently verified vulnerabilities, not sampled real-world repositories, and not a generalizable statistical estimate of precision or recall.

The benchmark's value is regression detection: a rule change must not silently break these known examples. Expand with real-world, permission-safe repositories, reviewed labels and independent ground truth before claiming detection performance or competition-grade accuracy. Measure per-rule precision, recall, false-positive rate, skipped/truncated coverage, runtime and reproducibility. Keep fixtures free of working keys or credentials.

Known limitations: lexical matching may flag strings and comments in some languages, miss multiline calls, and does not determine exploitability. A zero-finding scan is not a security certification.
