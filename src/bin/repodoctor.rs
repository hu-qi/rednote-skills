use std::env;
use std::path::Path;
fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 || args[1] != "scan" {
        eprintln!("Usage: repodoctor scan <local-directory> [--markdown]");
        std::process::exit(2);
    }
    let root = Path::new(&args[2]);
    match rednote_skills::scan(root) {
        Ok(report) => {
            if args.iter().any(|v| v == "--markdown") {
                print!("{}", rednote_skills::markdown_report(&report));
            } else {
                println!("{}", rednote_skills::json_report(root, &report));
            }
        },
        Err(err) => { eprintln!("scan failed: {err}"); std::process::exit(1); }
    }
}
