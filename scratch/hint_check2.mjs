// Verify the centered handwritten model-hint behaviour.
import { spawn } from "node:child_process";
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9346;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const chrome = spawn(CHROME, ["--headless=new","--disable-gpu","--no-first-run",
  `--remote-debugging-port=${PORT}`,"--user-data-dir=/tmp/emd-hint-check2","about:blank"],{stdio:"ignore"});
async function wsUrl(){for(let i=0;i<40;i++){try{const r=await fetch(`http://localhost:${PORT}/json/version`);const j=await r.json();if(j.webSocketDebuggerUrl)return j.webSocketDebuggerUrl;}catch{}await sleep(250);}throw new Error("no devtools");}
const ws=new WebSocket(await wsUrl());await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
let id=0;const pend=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){pend.get(m.id)(m);pend.delete(m.id);}};
const send=(method,params={},sid)=>{const i=++id;const p={id:i,method,params};if(sid)p.sessionId=sid;return new Promise((res,rej)=>{pend.set(i,m=>m.error?rej(new Error(m.error.message)):res(m.result));ws.send(JSON.stringify(p));});};
const {targetId}=await send("Target.createTarget",{url:"about:blank"});
const {sessionId:S}=await send("Target.attachToTarget",{targetId,flatten:true});
await send("Runtime.enable",{},S);
const ev=async x=>{const r=await send("Runtime.evaluate",{expression:x,returnByValue:true,awaitPromise:true},S);if(r.exceptionDetails)throw new Error(r.exceptionDetails.text);return r.result.value;};
async function waitHeader(){for(let i=0;i<40;i++){await sleep(300);if(await ev(`!!document.querySelector('.model-header')`))return true;}return false;}
async function nav(u){await send("Page.enable",{},S);await send("Page.navigate",{url:u},S);await waitHeader();}

await nav("http://localhost:8765/index.html");
await sleep(500);
console.log("no-param present =", await ev(`!!document.querySelector('.picker-hint#model-hint-note')`));
console.log("centered (fixed, flex) =", await ev(`(()=>{const n=document.querySelector('.picker-hint');if(!n)return false;const s=getComputedStyle(n);return s.position==='fixed'&&s.justifyContent==='center'&&s.alignItems==='center'&&s.pointerEvents==='none';})()`));
console.log("text =", JSON.stringify(await ev(`(document.querySelector('.hint-note-text')||{}).textContent||''`)));
console.log("font =", JSON.stringify(await ev(`(()=>{const t=document.querySelector('.hint-note-text');return t?getComputedStyle(t).fontFamily:'';})()`)));
console.log("arrow present =", await ev(`!!document.querySelector('.hint-note-arrow')`));
console.log("count (dupe check) =", await ev(`document.querySelectorAll('.picker-hint').length`));
await sleep(3000);
console.log("present after ~3.5s =", await ev(`!!document.querySelector('.picker-hint')`));

await nav("http://localhost:8765/index.html?model=access-esm1-6");
await sleep(700);
console.log("with-param present =", await ev(`!!document.querySelector('.picker-hint')`));
ws.close();chrome.kill();await sleep(200);process.exit(0);
