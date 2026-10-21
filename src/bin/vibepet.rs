//! Local-only VibeCoding Pet HTTP/CLI bridge. Zero third-party Rust dependencies.
use rednote_skills::pet::{Kind, PetState, Source};
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::Mutex;
use std::time::Duration;

const HTML: &str = include_str!("../../skills/vibecoding-pet/web/index.html");
const CSS: &str = include_str!("../../skills/vibecoding-pet/web/style.css");
const JS: &str = include_str!("../../skills/vibecoding-pet/web/app.js");
const MAX_REQUEST: usize = 8 * 1024;
const MAX_BODY: usize = 1024;

#[derive(Debug)]
struct Request {
    method: String,
    path: String,
    host: String,
    origin: Option<String>,
    site: Option<String>,
    content_type: Option<String>,
    body: String,
}

fn parse_http_request(bytes: &[u8]) -> Result<Request, &'static str> {
    let end = bytes.windows(4).position(|w| w == b"\r\n\r\n")
        .ok_or("headers incomplete")?;
    let header = std::str::from_utf8(&bytes[..end]).map_err(|_| "invalid header encoding")?;
    let mut lines = header.split("\r\n");
    let first = lines.next().ok_or("empty request")?;
    let bits: Vec<&str> = first.split_whitespace().collect();
    if bits.len() != 3 || bits[2] != "HTTP/1.1" {
        return Err("invalid request line");
    }
    let mut request = Request {
        method: bits[0].into(), path: bits[1].into(), host: String::new(),
        origin: None, site: None, content_type: None, body: String::new(),
    };
    let mut content_length = None;
    for line in lines {
        let (name, value) = line.split_once(':').ok_or("malformed header")?;
        let value = value.trim();
        match name.trim().to_ascii_lowercase().as_str() {
            "host" => request.host = value.to_ascii_lowercase(),
            "origin" => request.origin = Some(value.to_ascii_lowercase()),
            "sec-fetch-site" => request.site = Some(value.to_ascii_lowercase()),
            "content-type" => request.content_type = Some(value.to_ascii_lowercase()),
            "content-length" => {
                content_length = Some(value.parse::<usize>().map_err(|_| "invalid length")?);
            }
            "transfer-encoding" => return Err("chunked requests unsupported"),
            _ => {}
        }
    }
    let length = content_length.unwrap_or(0);
    if length > MAX_BODY || bytes.len() > MAX_REQUEST { return Err("request too large"); }
    let body = bytes.get(end + 4..).ok_or("missing body")?;
    if body.len() != length { return Err("request body length mismatch"); }
    request.body = String::from_utf8(body.to_vec()).map_err(|_| "non-utf8 body")?;
    Ok(request)
}

fn url_decode(raw: &str) -> Option<String> {
    let input = raw.as_bytes();
    let mut out = Vec::with_capacity(input.len());
    let mut index = 0;
    while index < input.len() {
        match input[index] {
            b'+' => out.push(b' '),
            b'%' => {
                if index + 2 >= input.len() { return None; }
                let a = (input[index + 1] as char).to_digit(16)?;
                let b = (input[index + 2] as char).to_digit(16)?;
                out.push((a * 16 + b) as u8);
                index += 2;
            }
            c => out.push(c),
        }
        index += 1;
    }
    String::from_utf8(out).ok()
}

fn parse_event(body: &str) -> Option<(Source, Kind)> {
    let mut source = None;
    let mut kind = None;
    for pair in body.split('&') {
        let (key, value) = pair.split_once('=')?;
        match key {
            "source" if source.is_none() => source = Source::parse(&url_decode(value)?),
            "kind" if kind.is_none() => kind = Kind::parse(&url_decode(value)?),
            _ => return None, // free text or duplicate key is forbidden
        }
    }
    Some((source?, kind?))
}

fn response(status: &str, mime: &str, body: &str) -> Vec<u8> {
    let head = format!(
        "HTTP/1.1 {status}\r\nContent-Type: {mime}\r\nContent-Length: {}\r\nCache-Control: no-store\r\nConnection: close\r\nX-Content-Type-Options: nosniff\r\nReferrer-Policy: no-referrer\r\nCross-Origin-Resource-Policy: same-origin\r\nContent-Security-Policy: default-src 'none'; img-src 'self' data:; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'\r\n\r\n",
        body.len()
    );
    [head.as_bytes(), body.as_bytes()].concat()
}

fn safe_host(host: &str, port: u16) -> bool {
    host == format!("127.0.0.1:{port}") || host == format!("localhost:{port}")
}
fn safe_origin(origin: &str, port: u16) -> bool {
    origin == format!("http://127.0.0.1:{port}") ||
        origin == format!("http://localhost:{port}")
}
fn route(request: &Request, state: &Mutex<PetState>, port: u16) -> Vec<u8> {
    if !safe_host(&request.host, port) {
        return response("403 Forbidden", "text/plain; charset=utf-8", "invalid host");
    }
    if request.method == "POST" &&
        (request.origin.as_deref().is_some_and(|o| !safe_origin(o, port))
            || request.site.as_deref() == Some("cross-site")) {
        return response("403 Forbidden", "text/plain; charset=utf-8", "cross-site write denied");
    }
    match (request.method.as_str(), request.path.as_str()) {
        ("GET", "/") => response("200 OK", "text/html; charset=utf-8", HTML),
        ("GET", "/style.css") => response("200 OK", "text/css; charset=utf-8", CSS),
        ("GET", "/app.js") => response("200 OK", "application/javascript; charset=utf-8", JS),
        ("GET", "/healthz") => response("200 OK", "application/json", r#"{"ok":true}"#),
        ("GET", "/api/state") => {
            let pet = state.lock().unwrap_or_else(|e| e.into_inner());
            response("200 OK", "application/json; charset=utf-8", &pet.to_json())
        }
        ("POST", "/api/event") => {
            if request.content_type.as_deref() != Some("application/x-www-form-urlencoded") {
                return response("415 Unsupported Media Type", "text/plain", "form encoding required");
            }
            if let Some((source, kind)) = parse_event(&request.body) {
                if request.origin.is_some() && !matches!(source, Source::Demo | Source::Manual) {
                    return response("403 Forbidden", "text/plain", "browser cannot impersonate agents");
                }
                if matches!(kind, Kind::Feed | Kind::Cheer)
                    && !matches!(source, Source::Manual | Source::Demo) {
                    return response("403 Forbidden", "text/plain", "agent cannot award manual care");
                }
                let mut pet = state.lock().unwrap_or_else(|e| e.into_inner());
                pet.apply(source, kind);
                response("200 OK", "application/json; charset=utf-8", &pet.to_json())
            } else {
                response("400 Bad Request", "text/plain", "unknown event")
            }
        }
        ("GET", _) | ("POST", _) => response("404 Not Found", "text/plain", "not found"),
        _ => response("405 Method Not Allowed", "text/plain", "method denied"),
    }
}

fn read_request(stream: &mut TcpStream) -> Result<Vec<u8>, &'static str> {
    let mut bytes = Vec::new();
    let mut chunk = [0u8; 1024];
    loop {
        if bytes.len() >= MAX_REQUEST { return Err("request too large"); }
        let received = stream.read(&mut chunk).map_err(|_| "request read failed")?;
        if received == 0 { return Err("unexpected eof"); }
        bytes.extend_from_slice(&chunk[..received]);
        if let Some(split) = bytes.windows(4).position(|w| w == b"\r\n\r\n") {
            if split > 6000 { return Err("headers too large"); }
            let head = std::str::from_utf8(&bytes[..split]).map_err(|_| "invalid headers")?;
            let mut len = 0;
            for line in head.split("\r\n") {
                if let Some((name, value)) = line.split_once(':') {
                    if name.eq_ignore_ascii_case("content-length") {
                        len = value.trim().parse::<usize>().map_err(|_| "invalid length")?;
                    }
                }
            }
            if len > MAX_BODY || split + 4 + len > MAX_REQUEST { return Err("body too large"); }
            if bytes.len() >= split + 4 + len {
                if bytes.len() != split + 4 + len { return Err("unexpected trailing bytes"); }
                return Ok(bytes);
            }
        }
    }
}

fn serve(port: u16) -> Result<(), String> {
    let listener = TcpListener::bind(("127.0.0.1", port)).map_err(|e| e.to_string())?;
    let state = Mutex::new(PetState::default());
    println!("VibeCoding Pet http://127.0.0.1:{port}");
    println!("仅本机运行；成长进度保存在内存，退出服务即清除；不读取代码或提示词。");
    for connection in listener.incoming() {
        let Ok(mut stream) = connection else { continue; };
        let _ = stream.set_read_timeout(Some(Duration::from_secs(2)));
        let _ = stream.set_write_timeout(Some(Duration::from_secs(2)));
        let output = match read_request(&mut stream) {
            Ok(bytes) => match parse_http_request(&bytes) {
                Ok(req) => route(&req, &state, port),
                Err(_) => response("400 Bad Request", "text/plain", "invalid request"),
            },
            Err(_) => response("400 Bad Request", "text/plain", "invalid request"),
        };
        let _ = stream.write_all(&output);
    }
    Ok(())
}

fn request(port: u16, bytes: &[u8]) -> Result<String, String> {
    let mut connection = TcpStream::connect(("127.0.0.1", port)).map_err(|e| e.to_string())?;
    connection.set_read_timeout(Some(Duration::from_secs(3))).map_err(|e| e.to_string())?;
    connection.write_all(bytes).map_err(|e| e.to_string())?;
    let mut buffer = Vec::new();
    connection.read_to_end(&mut buffer).map_err(|e| e.to_string())?;
    let raw = String::from_utf8(buffer).map_err(|e| e.to_string())?;
    if !raw.starts_with("HTTP/1.1 200 ") { return Err("pet rejected the event".into()); }
    Ok(raw.split_once("\r\n\r\n").map_or("", |(_, body)| body).to_string())
}

fn parse_port(args: &[String]) -> Result<u16, String> {
    let mut port = 7878;
    let mut i = 0;
    while i < args.len() {
        if args[i] != "--port" { return Err(format!("unknown argument: {}", args[i])); }
        i += 1;
        port = args.get(i).ok_or("missing port")?
            .parse::<u16>().map_err(|_| "invalid port")?;
        if port == 0 { return Err("port zero unsupported".into()); }
        i += 1;
    }
    Ok(port)
}

fn run(args: &[String]) -> Result<(), String> {
    match args.get(1).map(String::as_str) {
        Some("--version") if args.len() == 2 => {
            println!("0.1.0");
            Ok(())
        }
        Some("serve") => serve(parse_port(&args[2..])?),
        Some("status") => {
            let port = parse_port(&args[2..])?;
            let text = format!("GET /api/state HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nConnection: close\r\n\r\n");
            println!("{}", request(port, text.as_bytes())?);
            Ok(())
        }
        Some("emit") => {
            let kind = args.get(2).and_then(|s| Kind::parse(s)).ok_or("unknown kind")?;
            let mut source = Source::Manual;
            let mut options = Vec::new();
            let mut index = 3;
            while index < args.len() {
                if args[index] == "--source" {
                    index += 1;
                    source = Source::parse(args.get(index).ok_or("missing source")?)
                        .ok_or("unknown source")?;
                } else {
                    options.push(args[index].clone());
                    if args[index] == "--port" {
                        index += 1;
                        options.push(args.get(index).ok_or("missing port")?.clone());
                    }
                }
                index += 1;
            }
            let port = parse_port(&options)?;
            let body = format!("source={}&kind={}", source.as_str(), kind.as_str());
            let text = format!(
                "POST /api/event HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",
                body.len()
            );
            println!("{}", request(port, text.as_bytes())?);
            Ok(())
        }
        _ => Err("用法: vibepet serve [--port 7878] | status [--port 7878] | emit <session_start|thinking|tool_start|tool_done|approval_wait|task_success|task_failure|session_idle|feed|cheer> [--source codearts|opencode|manual|demo] [--port 7878] | --version".into()),
    }
}
fn main() {
    if let Err(err) = run(&std::env::args().collect::<Vec<_>>()) {
        eprintln!("vibepet: {err}");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn incoming(body: &str, origin: Option<&str>) -> Request {
        Request {
            method: "POST".into(), path: "/api/event".into(), host: "127.0.0.1:7878".into(),
            origin: origin.map(str::to_string), site: None,
            content_type: Some("application/x-www-form-urlencoded".into()), body: body.into(),
        }
    }
    #[test]
    fn agent_event_triggers_state() {
        let state = Mutex::new(PetState::default());
        let out = route(&incoming("source=codearts&kind=tool_start", None), &state, 7878);
        let data = String::from_utf8(out).unwrap();
        assert!(data.starts_with("HTTP/1.1 200"));
        assert!(data.contains(r#""mood":"busy""#));
    }
    #[test]
    fn cross_site_and_browser_impersonation_rejected() {
        let state = Mutex::new(PetState::default());
        let cross = incoming("source=demo&kind=feed", Some("https://attacker.example"));
        assert!(String::from_utf8(route(&cross, &state, 7878)).unwrap().contains("403 Forbidden"));
        let forged = incoming("source=codearts&kind=task_success", Some("http://localhost:7878"));
        assert!(String::from_utf8(route(&forged, &state, 7878)).unwrap().contains("403 Forbidden"));
        assert_eq!(state.lock().unwrap().events, 0);
    }
    #[test]
    fn free_text_and_bad_event_rejected() {
        assert!(parse_event("source=demo&kind=task_success").is_some());
        assert!(parse_event("source=demo&kind=task_success&prompt=private").is_none());
        assert!(parse_event("source=codearts&kind=task_succ%65ss").is_some());
        assert!(parse_event("source=codearts&kind=%ZZ").is_none());
    }
    #[test]
    fn hostile_host_and_large_payload_denied() {
        assert!(!safe_host("127.0.0.1.attacker:7878", 7878));
        let bad = format!(
            "POST /api/event HTTP/1.1\r\nHost: localhost:7878\r\nContent-Length: 1025\r\n\r\n{}",
            "x".repeat(1025));
        assert!(parse_http_request(bad.as_bytes()).is_err());
        let mut req = incoming("source=demo&kind=feed", None);
        req.host = "evil.example".into();
        assert!(String::from_utf8(route(&req, &Mutex::new(PetState::default()), 7878))
            .unwrap().contains("403 Forbidden"));
    }
    #[test]
    fn web_home_has_csp() {
        let mut req = incoming("", None);
        req.method = "GET".into();
        req.path = "/".into();
        let body = String::from_utf8(route(&req, &Mutex::new(PetState::default()), 7878)).unwrap();
        assert!(body.contains("Content-Security-Policy"));
        assert!(body.contains("VibeCoding Pet"));
    }
}
