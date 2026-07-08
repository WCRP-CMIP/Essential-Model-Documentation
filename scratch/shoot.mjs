// Headless-Chrome screenshotter via the DevTools Protocol (no npm deps).
// Node 26 has global fetch + WebSocket. Launches Chrome, navigates to the
// model page, waits for it to render, and captures element-level screenshots.
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";

const URL_BASE = "http://localhost:8765/index.html";
const MODEL = "ec-earth3-esm-1-1";
const OUT = "/Users/daniel.ellis/WIPwork/Essential-Model-Documentation/docs/Model/assets/guide-assets";
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9333;

const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---- launch Chrome ----
const chrome = spawn(CHROME, [
  "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
  "--hide-scrollbars", `--remote-debugging-port=${PORT}`,
  "--user-data-dir=/tmp/emd-shoot-profile", "about:blank",
], { stdio: "ignore" });

async function browserWS() {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://localhost:${PORT}/json/version`);
      const j = await r.json();
      if (j.webSocketDebuggerUrl) return j.webSocketDebuggerUrl;
    } catch (_) {}
    await sleep(250);
  }
  throw new Error("Chrome DevTools endpoint never came up");
}

const wsUrl = await browserWS();
const ws = new WebSocket(wsUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

let msgId = 0;
const pending = new Map();
ws.onmessage = ev => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
};
function send(method, params = {}, sessionId) {
  const id = ++msgId;
  const payload = { id, method, params };
  if (sessionId) payload.sessionId = sessionId;
  return new Promise((resolve, reject) => {
    pending.set(id, m => m.error ? reject(new Error(m.error.message)) : resolve(m.result));
    ws.send(JSON.stringify(payload));
  });
}

// ---- attach to a fresh page target ----
const { targetId } = await send("Target.createTarget", { url: "about:blank" });
const { sessionId } = await send("Target.attachToTarget", { targetId, flatten: true });
const S = sessionId;

await send("Page.enable", {}, S);
await send("Runtime.enable", {}, S);
await send("Emulation.setDeviceMetricsOverride",
  { width: 1240, height: 1400, deviceScaleFactor: 2, mobile: false }, S);

async function evaluate(expression) {
  const r = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true }, S);
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + " :: " + expression.slice(0, 80));
  return r.result.value;
}

// ---- navigate + wait for render ----
await send("Page.navigate", { url: `${URL_BASE}?model=${MODEL}` }, S);

let ready = false;
for (let i = 0; i < 60; i++) {
  await sleep(500);
  const state = await evaluate(`(() => {
    const rj = document.querySelector('.raw-json');
    const nodes = document.querySelectorAll('.hierarchy-canvas svg g.h-node').length;
    const crs = !!document.querySelector('.crs-svg');
    const grids = !!document.querySelector('.grids');
    return JSON.stringify({ rj: !!rj, nodes, crs, grids });
  })()`);
  const st = JSON.parse(state);
  if (st.rj && st.crs && st.grids && st.nodes > 0) { ready = true; break; }
}
if (!ready) console.error("WARN: page may not be fully rendered");
await sleep(2000); // let the force layout settle + fit transition finish

// expand collapsed sub-sections so their features are visible
await evaluate(`(() => {
  document.querySelectorAll('.grids .subgrid-block').forEach(d => d.open = true);
  const rj = document.querySelector('.raw-json'); if (rj) rj.open = true;
  return true;
})()`);
await sleep(400);

// ---- capture helper ----
async function shot(selector, file, pad = 10) {
  const rectJson = await evaluate(`(() => {
    const el = document.querySelector(${JSON.stringify(selector)});
    if (!el) return null;
    el.scrollIntoView();
    const r = el.getBoundingClientRect();
    return JSON.stringify({ x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height });
  })()`);
  if (!rectJson) { console.error("MISSING", selector); return false; }
  const r = JSON.parse(rectJson);
  const clip = { x: Math.max(0, r.x - pad), y: Math.max(0, r.y - pad), width: r.w + pad * 2, height: r.h + pad * 2, scale: 1 };
  const { data } = await send("Page.captureScreenshot", { format: "png", clip, captureBeyondViewport: true }, S);
  writeFileSync(`${OUT}/${file}`, Buffer.from(data, "base64"));
  console.log("OK", file, `${Math.round(clip.width)}x${Math.round(clip.height)}`);
  return true;
}

const shots = [
  [".model-header", "01-header.png"],
  [".overview", "02-overview.png"],
  [".crs-diagram", "03-crs.png"],
  [".references", "04-references.png"],
  [".family-card", "05-family.png"],
  [".hierarchy", "06-schema.png"],
  [".components-detail", "07-components.png"],
  [".grids", "08-grids.png"],
  [".raw-json", "09-json.png"],
];
for (const [sel, file] of shots) { try { await shot(sel, file); } catch (e) { console.error("ERR", file, e.message); } }

// full-page hero (whole emd-page)
try { await shot(".emd-page", "00-fullpage.png", 0); } catch (e) { console.error("ERR full", e.message); }

ws.close();
chrome.kill();
await sleep(300);
console.log("DONE");
process.exit(0);
