/**
 * OpenCode plugin adapter. Install only with user's explicit permission:
 * https://docs.opencode.ai/docs/plugins/
 * No prompts, code, paths, tool output, tokens or session IDs transmitted.
 */
const endpoint = "http://127.0.0.1:7878/api/event";
async function signal(kind) {
  try {
    await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ source: "opencode", kind }),
      signal: AbortSignal.timeout(300)
    });
  } catch {
    // Fail open: coding assistant continues normally if pet bridge is unavailable.
  }
}
export const VibeCodingPetPlugin = async () => ({
  event: async ({ event }) => {
    switch (event?.type) {
      case "session.created":
        await signal("session_start");
        break;
      case "session.status": {
        const status = event?.properties?.status?.type;
        if (status === "busy" || status === "retry") await signal("thinking");
        if (status === "idle") await signal("session_idle");
        break;
      }
      case "session.idle":
        await signal("session_idle");
        break;
      case "session.error":
        await signal("task_failure");
        break;
      case "permission.asked":
        await signal("approval_wait");
        break;
      default:
        break;
    }
  },
  "tool.execute.before": async () => signal("tool_start"),
  "tool.execute.after": async () => signal("tool_done")
});
