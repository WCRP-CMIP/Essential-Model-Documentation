// Verify the hint connector reaches the picker and the ring surrounds it.
import { spawn } from "node:child_process";
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9347;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const chrome = spawn(CHROME, ["--headless=new","--disable-gpu","--no-first-run","--window-size=1400,900",
  `--remote-debugging-port=${PORT}`,"--user-data-dir=/tmp/emd-hint-check3","about:blank"],{stdio:"ignore"});
async function wsUrl(){for(let i=0;i<40;i++){try{const r=await fetch(`http://localhost:${PORT}/json/version`);const j=await r.json();if(j.webSocketDebuggerUrl)return j.webSocketDebuggerUrl;}catch{}await sleep(250);}throw new Error("no devtools");}
const ws=new WebSocket(await wsUrl());await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
let id=0;const pend=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){pend.get(m.id)(m);pend.delete(m.id);}};
const send=(method,params={},sid)=>{const i=++id;const p={id:i,method,params};if(sid)p.sessionId=sid;return new Promise((res,rej)=>{pend.set(i,m=>m.error?rej(new Error(m.error.message)):res(m.result));ws.send(JSON.stringify(p));});};
const {targetId}=await send("Target.createTarget",{url:"about:blank"});
const {sessionId:S}=await send("Target.attachToTarget",{targetId,flatten:true});
await send("Runtime.enable",{},S);
await send("Emulation.setDeviceMetricsOverride",{width:1400,height:900,deviceScaleFactor:1,mobile:false},S);
const ev=async x=>{const r=await send("Runtime.evaluate",{expression:x,returnByValue:true,awaitPromise:true},S);if(r.exceptionDetails)throw new Error(r.exceptionDetails.text);return r.result.value;};
await send("Page.enable",{},S);await send("Page.navigate",{url:"http://localhost:8765/index.html"},S);
for(let i=0;i<40;i++){await sleep(300);if(await ev(`!!document.querySelector('.model-header')`))break;}
await sleep(700);
const out = await ev(`(()=>{
  const svg=document.querySelector('.hint-canvas');
  const ell=document.querySelector('.hint-ring');
  const lines=document.querySelectorAll('.hint-line');
  const pk=document.querySelector('.model-picker');
  if(!svg||!ell||!pk||lines.length<2) return JSON.stringify({ok:false, hasSvg:!!svg, hasEll:!!ell, lines:lines.length, hasPk:!!pk});
  const p=pk.getBoundingClientRect();
  const pcx=p.left+p.width/2, pcy=p.top+p.height/2;
  const ecx=+ell.getAttribute('cx'), ecy=+ell.getAttribute('cy'), rx=+ell.getAttribute('rx'), ry=+ell.getAttribute('ry');
  // arrow tip = 2nd point of the arrowhead path (the L x y)
  const d=lines[1].getAttribute('d'); const m=d.match(/L\\s+([\\d.]+)\\s+([\\d.]+)/); const tipx=+m[1], tipy=+m[2];
  // tip distance to ellipse centre, and how close to boundary
  const distTip=Math.hypot(tipx-pcx,tipy-pcy);
  return JSON.stringify({
    ok:true,
    ringCentredOnPicker: Math.abs(ecx-pcx)<1 && Math.abs(ecy-pcy)<1,
    ringSurroundsPicker: rx> p.width/2 && ry> p.height/2,
    tipNearPicker: distTip < Math.max(rx,ry)+18,
    picker:{pcx:Math.round(pcx),pcy:Math.round(pcy),w:Math.round(p.width),h:Math.round(p.height)},
    ring:{rx:Math.round(rx),ry:Math.round(ry)},
    tip:{x:Math.round(tipx),y:Math.round(tipy)}
  });
})()`);
console.log(out);
ws.close();chrome.kill();await sleep(200);process.exit(0);
