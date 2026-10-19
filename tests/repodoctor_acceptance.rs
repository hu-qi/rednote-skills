use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

fn fixture() -> PathBuf {
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let root = std::env::temp_dir().join(format!("repodoctor-acceptance-{}-{nonce}", std::process::id()));
    fs::create_dir_all(root.join(".github/workflows")).unwrap();
    root
}

fn run(root: &Path, format: &str) -> String {
    let result = Command::new(env!("CARGO_BIN_EXE_repodoctor"))
        .args(["scan", root.to_str().unwrap(), "--format", format])
        .output()
        .unwrap();
    assert!(
        result.status.success(),
        "stderr: {}",
        String::from_utf8_lossy(&result.stderr)
    );
    String::from_utf8(result.stdout).unwrap()
}

#[test]
fn reports_rule_ids_without_leaking_source() {
    let root = fixture();
    fs::write(
        root.join(".github/workflows/unsafe.yml"),
        "permissions: write-all\non: [pull_request_target]\n",
    ).unwrap();
    fs::write(
        root.join("process.py"),
        "import subprocess\nsubprocess.run('SECRET_DEMO_NEVER_PRINT', shell=True)\n",
    ).unwrap();
    fs::write(root.join("web.ts"), "const value = eval(input);\n").unwrap();
    fs::write(root.join("identity.pem"), "-----BEGIN RSA PRIVATE KEY-----\nSECRET_DEMO_NEVER_PRINT\n-----END RSA PRIVATE KEY-----\n").unwrap();

    let report = run(&root, "json");
    assert!(report.contains("RD001"));
    assert!(report.contains("RD002"));
    assert!(report.contains("RD003"));
    assert!(report.contains("RD004"));
    assert!(report.contains("RD005"));
    assert!(report.contains("static-lead"));
    assert!(!report.contains("SECRET_DEMO_NEVER_PRINT"));
    assert!(report.contains("schema_version"));
    let md = run(&root, "markdown");
    assert!(md.contains("RD001"));
    fs::remove_dir_all(root).unwrap();
}

#[test]
fn ignores_irrelevant_files_and_comments() {
    let root = fixture();
    fs::write(root.join("README.yaml"), "permissions: write-all\n").unwrap();
    fs::write(root.join("safe.py"), "# subprocess.run(user, shell=True)\nprint('shell=True')\n").unwrap();
    fs::write(root.join("safe.js"), "// eval(user);\n").unwrap();
    fs::write(root.join(".github/workflows/safe.yml"), "permissions: read-all\n").unwrap();
    let result = run(&root, "json");
    assert!(result.contains("\"total_findings\":0"));
    fs::remove_dir_all(root).unwrap();
}

#[test]
fn refuses_invalid_output_format() {
    let root = fixture();
    let result = Command::new(env!("CARGO_BIN_EXE_repodoctor"))
        .args(["scan", root.to_str().unwrap(), "--format", "xml"])
        .output()
        .unwrap();
    assert!(!result.status.success());
    fs::remove_dir_all(root).unwrap();
}

#[test]
fn validates_embedded_skill_definition() {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("skills/repodoctor");
    let result = Command::new(env!("CARGO_BIN_EXE_repodoctor"))
        .args(["validate-skill", root.to_str().unwrap()])
        .output()
        .unwrap();
    assert!(result.status.success());
}
