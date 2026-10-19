use std::env;
use std::fs;
use std::path::Path;

fn execute(args: &[String]) -> Result<(), String> {
    if args.len() == 2 && args[1] == "--version" {
        println!("{}", env!("CARGO_PKG_VERSION"));
        return Ok(());
    }
    if args.len() == 3 && args[1] == "validate-skill" {
        let text = fs::read_to_string(Path::new(&args[2]).join("SKILL.md"))
            .map_err(|err| err.to_string())?;
        let mut lines = text.lines();
        if lines.next() != Some("---") {
            return Err("SKILL.md needs YAML frontmatter".into());
        }
        let mut name = false;
        let mut description = false;
        let mut closed = false;
        for line in lines {
            if line.trim() == "---" {
                closed = true;
                break;
            }
            if line.starts_with("name:") && !line[5..].trim().is_empty() {
                name = true;
            }
            if line.starts_with("description:") && line[12..].trim().len() >= 20 {
                description = true;
            }
        }
        if !closed || !name || !description {
            return Err("Skill requires name and description in closed frontmatter".into());
        }
        println!("Skill metadata is valid");
        return Ok(());
    }
    if args.len() < 3 || args[1] != "scan" {
        return Err("Usage: repodoctor scan <path> [--format json|markdown] [--output file]; repodoctor validate-skill <skill-dir>".into());
    }
    let mut format = "json";
    let mut output = None;
    let mut index = 3;
    while index < args.len() {
        match args[index].as_str() {
            "--markdown" => format = "markdown",
            "--format" => {
                index += 1;
                format = args.get(index).ok_or("missing format")?.as_str();
                if format != "json" && format != "markdown" && format != "sarif" {
                    return Err("format must be json, markdown or sarif".into());
                }
            }
            "--output" => {
                index += 1;
                output = Some(args.get(index).ok_or("missing output path")?);
            }
            other => return Err(format!("unknown option: {other}")),
        }
        index += 1;
    }
    let root = Path::new(&args[2]);
    let report = rednote_skills::scan(root).map_err(|err| err.to_string())?;
    let body = if format == "sarif" {
        rednote_skills::sarif::sarif_report(&report)
    } else if format == "markdown" {
        rednote_skills::markdown_report(&report)
    } else {
        rednote_skills::json_report(root, &report)
    };
    if let Some(path) = output {
        fs::write(path, body).map_err(|err| err.to_string())?;
    } else {
        println!("{body}");
    }
    Ok(())
}

fn main() {
    if let Err(error) = execute(&env::args().collect::<Vec<_>>()) {
        eprintln!("repodoctor: {error}");
        std::process::exit(1);
    }
}
