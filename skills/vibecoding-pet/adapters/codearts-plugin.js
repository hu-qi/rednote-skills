/**
 * CodeArts CLI hook adapter — install only with user's explicit permission.
 * https://support.huaweicloud.com/usermanual-cli/codeartsagent_cli_0018.html
 * Privacy: only source + fixed event kind go to local loopback.
 */
const endpoint = "http://127.0.0.1:7878/api/event";
async function signal(kind) {
  try {
    await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ source: "codearts", kind }),
      signal: AbortSignal.timeout(300)
    });
  } catch {
    // Agent execution must not fail when the optional pet is offline.
  }
}
export const VibeCodingPetPlugin = async () => ({
  "chat.message": async () => signal("session_start"),
  "tool.execute.before": async () => signal("tool_start"),
  "tool.execute.after": async () => signal("tool_done"),
  "user.approval": async () => signal("approval_wait"),
  "chat.error": async () => signal("task_failure"),
  "chat.finished": async () => signal("session_idle")
});
