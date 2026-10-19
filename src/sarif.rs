//! SARIF 2.1.0 serialization. The scanner produces heuristic review leads, not verified flaws.
use crate::Report;

fn quote(s: &str) -> String {
    let mut out = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c.is_control() => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}
fn level(severity: &str) -> &'static str {
    match severity {
        "critical" | "high" => "error",
        "medium" => "warning",
        _ => "note",
    }
}
pub fn sarif_report(report: &Report) -> String {
    let rules = [
        ("RD001", "Broad workflow write permission"),
        ("RD002", "Fork pull request trust boundary"),
        ("RD003", "Python subprocess shell execution"),
        ("RD004", "JavaScript dynamic evaluation"),
        ("RD005", "Potential private key in repository"),
    ];
    let descriptors: Vec<String> = rules.iter().map(|(id, description)| {
        format!("{{\"id\":{},\"shortDescription\":{{\"text\":{}}},\"help\":{{\"text\":\"Heuristic review lead; manually validate source and execution context before changing code.\"}}}}",quote(id),quote(description))
    }).collect();
    let results: Vec<String> = report.findings.iter().map(|f| {
        format!(
            "{{\"ruleId\":{},\"level\":{},\"message\":{{\"text\":{}}},\"locations\":[{{\"physicalLocation\":{{\"artifactLocation\":{{\"uri\":{}}},\"region\":{{\"startLine\":{}}}}}}}],\"properties\":{{\"evidenceLevel\":\"static-lead\",\"verified\":false}}}}",
            quote(f.rule), quote(level(f.severity)), quote(f.evidence),quote(&f.path),f.line
        )
    }).collect();
    format!(
        "{{\"$schema\":\"https://json.schemastore.org/sarif-2.1.0.json\",\"version\":\"2.1.0\",\"runs\":[{{\"tool\":{{\"driver\":{{\"name\":\"RepoDoctor\",\"version\":{},\"informationUri\":\"https://github.com/hu-qi/rednote-skills\",\"rules\":[{}]}}}},\"results\":[{}],\"properties\":{{\"truncated\":{},\"filesScanned\":{},\"filesSkipped\":{},\"note\":\"These are review leads, not verified vulnerabilities.\"}}}}]}}",
        quote(env!("CARGO_PKG_VERSION")),descriptors.join(","),results.join(","), report.truncated,report.scanned,report.skipped
    )
}
#[cfg(test)]
mod tests {
    use super::*;
    use crate::Finding;
    #[test]
    fn creates_sarif_with_safe_escaping() {
        let report=Report{scanned:1, skipped:0,truncated:false,findings:vec![
            Finding{rule:"RD001",severity:"high",path:"a\"test.yml".into(),line:1,evidence:"Broad workflow write permission"}
        ]};
        let data=sarif_report(&report);
        assert!(data.contains("\"version\":\"2.1.0\""));
        assert!(data.contains("a\\\"test.yml"));
        assert!(data.contains("\"verified\":false"));
    }
}
