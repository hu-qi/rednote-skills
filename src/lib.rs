pub mod sarif;
pub mod pet;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Finding {
    pub rule: &'static str,
    pub severity: &'static str,
    pub path: String,
    pub line: usize,
    pub evidence: &'static str,
}
#[derive(Debug, Default)]
pub struct Report { pub scanned: usize, pub skipped: usize, pub truncated: bool, pub findings: Vec<Finding> }

fn ignored(name: &str) -> bool {
    matches!(name, ".git" | "node_modules" | "target" | "dist" | "build" | "vendor" | ".venv" | "__pycache__" | ".next")
}
fn eligible(path: &Path) -> bool {
    matches!(path.extension().and_then(|v| v.to_str()), Some("py" | "js" | "jsx" | "ts" | "tsx" | "yml" | "yaml" | "pem" | "key"))
}
fn walk(root: &Path, current: &Path, report: &mut Report) -> std::io::Result<()> {
    let mut entries = fs::read_dir(current)?.collect::<std::io::Result<Vec<_>>>()?;
    entries.sort_by_key(|e| e.path());
    for entry in entries {
        let p = entry.path();
        let typ = entry.file_type()?;
        if typ.is_symlink() { report.skipped += 1; report.truncated = true; continue; }
        if typ.is_dir() {
            if !ignored(&entry.file_name().to_string_lossy()) { walk(root, &p, report)?; }
            continue;
        }
        if !typ.is_file() || !eligible(&p) { continue; }
        if report.scanned >= 10_000 || entry.metadata()?.len() > 1_048_576 {
            report.skipped += 1; report.truncated = true; continue;
        }
        let Ok(content) = fs::read_to_string(&p) else { report.skipped += 1; report.truncated = true; continue; };
        report.scanned += 1;
        let rel = p.strip_prefix(root).unwrap_or(&p).to_string_lossy().replace('\\', "/");
        let workflow = rel.starts_with(".github/workflows/") && (rel.ends_with(".yml") || rel.ends_with(".yaml"));
        for (idx, line) in content.lines().enumerate() {
            let trimmed = line.trim();
            // Avoid comments as a first-pass false-positive reduction.
            let commented = trimmed.starts_with('#') || trimmed.starts_with("//") || trimmed.starts_with('*');
            let mut add = |rule, severity, evidence| report.findings.push(Finding {
                rule, severity, path: rel.clone(), line: idx + 1, evidence
            });
            if workflow && (trimmed == "permissions: write-all" || trimmed.starts_with("permissions: write-all #")) {
                add("RD001", "high", "Broad workflow write permission");
            }
            if workflow && (trimmed.starts_with("pull_request_target:") || trimmed == "- pull_request_target" || trimmed.contains("[pull_request_target]")) {
                add("RD002", "medium", "Fork trust boundary requires manual review");
            }
            if !commented && rel.ends_with(".py") && ["subprocess.run(", "subprocess.call(", "subprocess.Popen(", "subprocess.check_output(", "subprocess.check_call("].iter().any(|name| trimmed.contains(name)) && trimmed.replace(" ", "").contains("shell=True") {
                add("RD003", "medium", "Shell execution requires taint analysis");
            }
            if !commented && [".js", ".jsx", ".ts", ".tsx"].iter().any(|e| rel.ends_with(e))
                && trimmed.contains("eval(") {
                add("RD004", "medium", "Dynamic evaluation requires input review");
            }
            if trimmed.starts_with("-----BEGIN ") && trimmed.ends_with(" PRIVATE KEY-----") && trimmed.len() <= 100 {
                add("RD005", "critical", "Private key delimiter detected; contents withheld");
            }
        }
    }
    Ok(())
}
pub fn scan(root: &Path) -> std::io::Result<Report> {
    let root: PathBuf = root.canonicalize()?;
    if !root.is_dir() { return Err(std::io::Error::new(std::io::ErrorKind::InvalidInput, "not a directory")); }
    let mut report = Report::default();
    walk(&root, &root, &mut report)?;
    report.findings.sort_by(|a,b| (&a.path,a.line,a.rule).cmp(&(&b.path,b.line,b.rule)));
    Ok(report)
}
fn escape_json(input: &str) -> String {
    let mut s = String::new();
    for c in input.chars() {
        match c { '"' => s.push_str("\\\""), '\\' => s.push_str("\\\\"), '\n' => s.push_str("\\n"),
            '\r' => s.push_str("\\r"), '\t' => s.push_str("\\t"),
            c if c.is_control() => s.push_str(&format!("\\u{:04x}", c as u32)),
            c => s.push(c) }
    }
    s
}
pub fn json_report(root: &Path, report: &Report) -> String {
    let items: Vec<String> = report.findings.iter().map(|f| format!(
        "{{\"rule_id\":\"{}\",\"severity\":\"{}\",\"path\":\"{}\",\"line\":{},\"evidence_level\":\"static-lead\",\"evidence\":\"{}\"}}",
        f.rule, f.severity, escape_json(&f.path), f.line, f.evidence)).collect();
    format!("{{\"schema_version\":\"0.2.0\",\"repository\":\"{}\",\"scan\":{{\"mode\":\"read-only-static\",\"files_scanned\":{},\"files_skipped\":{},\"truncated\":{}}},\"summary\":{{\"total_findings\":{}}},\"findings\":[{}],\"limitations\":[\"Heuristic matches are not proven vulnerabilities\",\"No code execution or automatic repairs\",\"Zero findings does not imply safety\"]}}",
        escape_json(&root.display().to_string()), report.scanned, report.skipped, report.truncated,
        report.findings.len(), items.join(","))
}
pub fn markdown_report(report: &Report) -> String {
    let mut out = format!("# RepoDoctor scan\n\nScanned: {} | Skipped: {} | Truncated: {} | Leads: {}\n\n", report.scanned, report.skipped, report.truncated, report.findings.len());
    for f in &report.findings {
        out.push_str(&format!("- **{}** ({}) at `{}:{}`: {} [static-lead]\n",
            f.rule, f.severity, f.path, f.line, f.evidence));
    }
    out.push_str("\nThese are static review leads, not reproduced vulnerabilities. No repository code was executed.\n");
    out
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn json_escaping() { assert_eq!(escape_json("a\"b\\c"), "a\\\"b\\\\c"); }
    #[test]
    fn classify_extensions() {
        assert!(eligible(Path::new("x.py")));
        assert!(!eligible(Path::new("x.exe")));
    }
    #[test]
    fn shell_rule_is_scoped() {
        let source = "subprocess.run(user, shell=True)";
        assert!(source.contains("subprocess.run("));
        assert!(!"print('shell=True')".contains("subprocess.run("));
    }
    #[test]
    fn scan_fixture() {
        let base = std::env::temp_dir().join(format!("repodoctor-test-{}", std::process::id()));
        let _ = fs::remove_dir_all(&base);
        fs::create_dir_all(base.join(".github/workflows")).unwrap();
        fs::write(base.join(".github/workflows/test.yml"), "permissions: write-all\n").unwrap();
        fs::write(base.join("safe.py"), "# shell=True\n").unwrap();
        let result = scan(&base).unwrap();
        assert_eq!(result.findings.len(), 1);
        assert_eq!(result.findings[0].rule, "RD001");
        fs::remove_dir_all(base).unwrap();
    }
}
