import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

async function load(name) {
  const uri = new URL('../skills/vibecoding-pet/adapters/' + name, import.meta.url);
  const code = await readFile(uri, 'utf8');
  return import('data:text/javascript;base64,' + Buffer.from(code).toString('base64'));
}
async function withMock(callback) {
  const original = globalThis.fetch;
  const calls = [];
  globalThis.fetch = async (url, options) => {
    calls.push({ url, options });
    return { ok: true };
  };
  try { await callback(calls); }
  finally { globalThis.fetch = original; }
}
function assertPrivate(calls, source) {
  for (const call of calls) {
    assert.equal(call.url, 'http://127.0.0.1:7878/api/event');
    assert.equal(call.options.method, 'POST');
    assert.deepEqual(Array.from(call.options.body.keys()).sort(), ['kind', 'source']);
    assert.equal(call.options.body.get('source'), source);
    assert(!call.options.body.toString().includes('PRIVATE_CONTENT'));
  }
}
test('CodeArts hooks send only event names, not prompts, code or tool output', async () => {
  await withMock(async (calls) => {
    const { VibeCodingPetPlugin } = await load('codearts-plugin.js');
    const hooks = await VibeCodingPetPlugin({});
    await hooks['chat.message']({ text: 'PRIVATE_CONTENT' });
    await hooks['tool.execute.before']({ args: { code: 'PRIVATE_CONTENT' } });
    await hooks['tool.execute.after']({ output: 'PRIVATE_CONTENT' });
    await hooks['user.approval']({ message: 'PRIVATE_CONTENT' });
    await hooks['chat.error']({ error: 'PRIVATE_CONTENT' });
    await hooks['chat.finished']({ transcript: 'PRIVATE_CONTENT' });
    assert.deepEqual(calls.map(c => c.options.body.get('kind')),
      ['session_start','tool_start','tool_done','approval_wait','task_failure','session_idle']);
    assertPrivate(calls, 'codearts');
    assert(!calls.some(c => c.options.body.get('kind') === 'task_success'));
  });
});
test('OpenCode maps session idle to rest, never success', async () => {
  await withMock(async (calls) => {
    const { VibeCodingPetPlugin } = await load('opencode-plugin.js');
    const hooks = await VibeCodingPetPlugin({});
    await hooks.event({ event: { type:'session.created', properties:{text:'PRIVATE_CONTENT'} } });
    await hooks.event({ event: { type:'session.status', properties:{status:{type:'busy'}} } });
    await hooks['tool.execute.before']({ args:{ command:'PRIVATE_CONTENT' } });
    await hooks['tool.execute.after']({ output:'PRIVATE_CONTENT' });
    await hooks.event({ event: { type:'session.status', properties:{status:{type:'idle'}} } });
    await hooks.event({ event: { type:'session.error', properties:{error:'PRIVATE_CONTENT'} } });
    assert.deepEqual(calls.map(c => c.options.body.get('kind')),
      ['session_start','thinking','tool_start','tool_done','session_idle','task_failure']);
    assertPrivate(calls, 'opencode');
  });
});
test('no local service does not block CodeArts or OpenCode', async () => {
  const old = globalThis.fetch;
  globalThis.fetch = async () => { throw new Error('ECONNREFUSED'); };
  try {
    const ca = await load('codearts-plugin.js');
    const oc = await load('opencode-plugin.js');
    await assert.doesNotReject((await ca.VibeCodingPetPlugin({}))['chat.message']({}));
    await assert.doesNotReject((await oc.VibeCodingPetPlugin({})).event({event:{type:'session.created'}}));
  } finally { globalThis.fetch = old; }
});
