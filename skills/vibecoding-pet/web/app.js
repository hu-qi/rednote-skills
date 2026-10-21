/* Browser dashboard: only accepts safe enum values from local Rust HTTP service. */
const moodCopy = {
  idle: ["好奇地观察着屏幕", "准备好一起创造了吗？", "正在待命的小宠物粒粒"],
  focus: ["思考的火花正在闪烁", "让我认真想想！", "正在专注思考的粒粒"],
  busy: ["代码魔法正在施展", "工具启动！冲呀！", "正在忙碌的粒粒"],
  waiting: ["耐心等待你的决定", "这里需要你的确认哦～", "正在等待确认的粒粒"],
  happy: ["开心到要飞起来了！", "耶！我们又前进了一步！", "正在庆祝的粒粒"],
  worried: ["遇到难题也不要放弃", "没关系，再试一次！", "正在发愁的粒粒"],
  resting: ["休息一下，为下一次出发充能", "呼噜……好舒服呀。", "正在休息的粒粒"]
};
const eventCopy = {
  session_start: ["新的编码旅程", "▶"],
  thinking: ["Agent 正在思考", "✧"],
  tool_start: ["正在调用工具", "⚙"],
  tool_done: ["工具执行结束", "◈"],
  approval_wait: ["等待人工确认", "◷"],
  task_success: ["任务完成，收获经验", "✦"],
  task_failure: ["任务遇到了问题", "↺"],
  session_idle: ["Agent 正在休息", "☾"],
  feed: ["投喂了一份能量", "🍓"],
  cheer: ["收到了温暖的鼓励", "♡"]
};
const sourceCopy = {
  codearts: "CodeArts 真实事件", opencode: "OpenCode 真实事件",
  demo: "演示模拟事件", manual: "手动互动"
};
const get = (id) => document.getElementById(id);
let lastSequence = -1;
let online = false;
let waitingForPost = false;

function metric(id, n, unit) {
  const element = get(id);
  element.replaceChildren(document.createTextNode(String(n) + " "));
  const small = document.createElement("small");
  small.textContent = unit;
  element.append(small);
}

function render(state) {
  if (!state || !moodCopy[state.mood]) return;
  get("pet-scene").dataset.mood = state.mood;
  const [caption, bubble, accessible] = moodCopy[state.mood];
  get("status-text").textContent = caption;
  get("pet-message").textContent = bubble;
  get("pet").setAttribute("aria-label", accessible);
  const level = get("level");
  level.replaceChildren(document.createTextNode("LV. " + String(state.level).padStart(2, "0") + " "));
  const title = document.createElement("span");
  title.textContent = state.level >= 5 ? "星际魔法师" : state.level >= 3 ? "代码探索家" : "新手冒险家";
  level.append(title);
  get("energy-value").textContent = state.energy + " / 100";
  get("joy-value").textContent = state.joy + " / 100";
  get("energy-bar").style.width = state.energy + "%";
  get("joy-bar").style.width = state.joy + "%";
  metric("xp", state.xp, "XP");
  metric("tasks", state.tasks_done, "次");
  metric("streak", state.streak, "次");
  const currentXP = state.xp % 60;
  get("xp-next").textContent = currentXP + " / 60 XP";
  get("xp-bar").style.width = String(currentXP / 60 * 100) + "%";
  const real = state.last_source === "codearts" || state.last_source === "opencode";
  get("source-label").dataset.real = String(real);
  get("source-label").textContent = state.events ?
    (sourceCopy[state.last_source] || "未知来源") : "尚无 Agent 事件";
  get("live-tag").textContent = !state.events ? "等待信号" :
    real ? "● 已收到真实事件" : "● 演示 / 手动互动";
  if (lastSequence === state.events) return;
  lastSequence = state.events;
  const container = get("timeline");
  container.replaceChildren();
  if (!state.history || !state.history.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    const glyph = document.createElement("span");
    glyph.textContent = "☁";
    const headline = document.createElement("strong");
    headline.textContent = "一切就绪，等待第一个事件";
    const detail = document.createElement("small");
    detail.textContent = "接入 CodeArts / OpenCode，或者先试玩演示";
    empty.append(glyph, headline, detail);
    container.append(empty);
    return;
  }
  for (const e of state.history.slice(0, 6)) {
    const [label, glyph] = eventCopy[e.kind] || ["未知事件", "?"];
    const row = document.createElement("div");
    row.className = "event";
    const icon = document.createElement("div");
    icon.className = "event-glyph";
    icon.textContent = glyph;
    const body = document.createElement("div");
    body.className = "event-main";
    const name = document.createElement("strong");
    name.textContent = label;
    const from = document.createElement("small");
    from.textContent = sourceCopy[e.source] || "未知来源";
    body.append(name, from);
    const number = document.createElement("span");
    number.className = "event-num";
    number.textContent = "#" + e.number;
    row.append(icon, body, number);
    container.append(row);
  }
}
function connection(connected) {
  if (online === connected) return;
  online = connected;
  get("connection").className = "connection " + (connected ? "online" : "offline");
  get("connection").lastChild.textContent = connected ? "本地服务在线" : "连接已断开";
}
async function refresh() {
  try {
    const reply = await fetch("/api/state", { cache: "no-store" });
    if (!reply.ok) throw new Error("no state");
    render(await reply.json());
    connection(true);
  } catch {
    connection(false);
  }
}
async function event(source, kind) {
  if (waitingForPost) return;
  waitingForPost = true;
  try {
    const reply = await fetch("/api/event", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ source, kind })
    });
    if (!reply.ok) throw new Error("event rejected");
    render(await reply.json());
    connection(true);
  } catch {
    connection(false);
  } finally {
    waitingForPost = false;
  }
}
get("feed-btn").addEventListener("click", () => event("manual", "feed"));
get("cheer-btn").addEventListener("click", () => event("manual", "cheer"));
for (const button of document.querySelectorAll("[data-kind]")) {
  button.addEventListener("click", () => event("demo", button.dataset.kind));
}
void refresh();
setInterval(refresh, 1300);
