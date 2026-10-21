//! Deterministic, dependency-free Agent lifecycle -> virtual pet state.
//! Only safe enumerated event names are accepted; no prompts, code, IDs or outputs.
use std::collections::VecDeque;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    SessionStart, Thinking, ToolStart, ToolDone, ApprovalWait,
    TaskSuccess, TaskFailure, SessionIdle, Feed, Cheer,
}
impl Kind {
    pub fn parse(s: &str) -> Option<Self> {
        Some(match s {
            "session_start" => Self::SessionStart,
            "thinking" => Self::Thinking,
            "tool_start" => Self::ToolStart,
            "tool_done" => Self::ToolDone,
            "approval_wait" => Self::ApprovalWait,
            "task_success" => Self::TaskSuccess,
            "task_failure" => Self::TaskFailure,
            "session_idle" => Self::SessionIdle,
            "feed" => Self::Feed,
            "cheer" => Self::Cheer,
            _ => return None,
        })
    }
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::SessionStart => "session_start",
            Self::Thinking => "thinking",
            Self::ToolStart => "tool_start",
            Self::ToolDone => "tool_done",
            Self::ApprovalWait => "approval_wait",
            Self::TaskSuccess => "task_success",
            Self::TaskFailure => "task_failure",
            Self::SessionIdle => "session_idle",
            Self::Feed => "feed",
            Self::Cheer => "cheer",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Source { CodeArts, OpenCode, Manual, Demo }
impl Source {
    pub fn parse(s: &str) -> Option<Self> {
        Some(match s {
            "codearts" => Self::CodeArts,
            "opencode" => Self::OpenCode,
            "manual" => Self::Manual,
            "demo" => Self::Demo,
            _ => return None,
        })
    }
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::CodeArts => "codearts", Self::OpenCode => "opencode",
            Self::Manual => "manual", Self::Demo => "demo",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Mood { Idle, Focus, Busy, Waiting, Happy, Worried, Resting }
impl Mood {
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::Idle => "idle", Self::Focus => "focus", Self::Busy => "busy",
            Self::Waiting => "waiting", Self::Happy => "happy",
            Self::Worried => "worried", Self::Resting => "resting",
        }
    }
}

#[derive(Clone, Debug)]
pub struct EventRecord {
    pub sequence: u64,
    pub kind: Kind,
    pub source: Source,
}

#[derive(Clone, Debug)]
pub struct PetState {
    pub energy: u8,
    pub joy: u8,
    pub xp: u32,
    pub tasks_done: u32,
    pub streak: u32,
    pub mood: Mood,
    pub last_source: Source,
    pub last_kind: Kind,
    pub events: u64,
    pub history: VecDeque<EventRecord>,
}
impl Default for PetState {
    fn default() -> Self {
        Self {
            energy: 75, joy: 76, xp: 0, tasks_done: 0, streak: 0,
            mood: Mood::Idle, last_source: Source::Manual,
            last_kind: Kind::SessionIdle, events: 0, history: VecDeque::new(),
        }
    }
}
impl PetState {
    /// Changes are deterministic and recreational, not measurements of code quality.
    pub fn apply(&mut self, source: Source, kind: Kind) {
        self.last_source = source;
        self.last_kind = kind;
        self.events = self.events.saturating_add(1);
        match kind {
            Kind::SessionStart => {
                self.mood = Mood::Focus;
                self.energy = self.energy.saturating_sub(2);
            }
            Kind::Thinking => self.mood = Mood::Focus,
            Kind::ToolStart => {
                self.mood = Mood::Busy;
                self.energy = self.energy.saturating_sub(4);
            }
            Kind::ToolDone => {
                self.mood = Mood::Focus;
                self.xp = self.xp.saturating_add(3);
            }
            Kind::ApprovalWait => self.mood = Mood::Waiting,
            Kind::TaskSuccess => {
                self.mood = Mood::Happy;
                self.tasks_done = self.tasks_done.saturating_add(1);
                self.streak = self.streak.saturating_add(1);
                self.xp = self.xp.saturating_add(25);
                self.joy = self.joy.saturating_add(9).min(100);
            }
            Kind::TaskFailure => {
                self.mood = Mood::Worried;
                self.streak = 0;
                self.joy = self.joy.saturating_sub(12);
            }
            Kind::SessionIdle => {
                self.mood = Mood::Resting;
                self.energy = self.energy.saturating_add(4).min(100);
            }
            Kind::Feed => {
                self.mood = Mood::Happy;
                self.energy = self.energy.saturating_add(16).min(100);
                self.joy = self.joy.saturating_add(4).min(100);
            }
            Kind::Cheer => {
                self.mood = Mood::Happy;
                self.joy = self.joy.saturating_add(13).min(100);
            }
        }
        self.history.push_front(EventRecord { sequence: self.events, source, kind });
        while self.history.len() > 16 { self.history.pop_back(); }
    }

    pub fn level(&self) -> u32 { (1 + self.xp / 60).min(1000) }

    /// JSON fields are enumerated or numeric, so source input cannot leak into outputs.
    pub fn to_json(&self) -> String {
        let records = self.history.iter()
            .map(|e| format!(
                r#"{{"number":{},"source":"{}","kind":"{}"}}"#,
                e.sequence, e.source.as_str(), e.kind.as_str()))
            .collect::<Vec<_>>().join(",");
        format!(
            r#"{{"schema_version":1,"energy":{},"joy":{},"xp":{},"level":{},"tasks_done":{},"streak":{},"mood":"{}","last_source":"{}","last_kind":"{}","events":{},"history":[{}]}}"#,
            self.energy, self.joy, self.xp, self.level(), self.tasks_done, self.streak,
            self.mood.as_str(), self.last_source.as_str(), self.last_kind.as_str(),
            self.events, records
        )
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn defaults_are_independent_from_cloud() {
        let state = PetState::default();
        assert_eq!((state.energy, state.joy, state.level()), (75, 76, 1));
        assert_eq!(state.mood, Mood::Idle);
        assert!(state.to_json().contains(r#""schema_version":1"#));
    }
    #[test]
    fn lifecycle_and_growth_are_deterministic() {
        let mut p = PetState::default();
        p.apply(Source::CodeArts, Kind::SessionStart);
        p.apply(Source::CodeArts, Kind::ToolStart);
        assert_eq!(p.mood, Mood::Busy);
        p.apply(Source::CodeArts, Kind::ToolDone);
        for _ in 0..3 { p.apply(Source::OpenCode, Kind::TaskSuccess); }
        assert_eq!((p.tasks_done, p.streak, p.level()), (3, 3, 2));
        p.apply(Source::OpenCode, Kind::TaskFailure);
        assert_eq!(p.streak, 0);
        assert_eq!(p.mood, Mood::Worried);
    }
    #[test]
    fn numeric_bounds_and_event_history_limit() {
        let mut p = PetState::default();
        for _ in 0..250 {
            p.apply(Source::Demo, Kind::Feed);
            p.apply(Source::Demo, Kind::Cheer);
        }
        assert_eq!((p.energy, p.joy, p.events, p.history.len()), (100, 100, 500, 16));
        for _ in 0..300 { p.apply(Source::Manual, Kind::ToolStart); }
        assert_eq!(p.energy, 0);
    }
    #[test]
    fn unknown_event_names_do_not_parse() {
        assert_eq!(Kind::parse("task_success"), Some(Kind::TaskSuccess));
        assert_eq!(Kind::parse("task_success; rm -rf /"), None);
        assert_eq!(Source::parse("codearts&prompt=secret"), None);
    }
}
