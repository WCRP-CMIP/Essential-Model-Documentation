// Quick headless check for the picker hint behaviour.
import { spawn } from "node:child_process";
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9344;
const sleep = ms => new Promise(r => setTimeout(r, ms));

const chrome = spawn(CHROME, ["--headless=new","--disable-gpu","--no-first-run",
  `--remote-debugging-port=${PORT}`,"--user-data-dir=/tmp/emd-hint-check","about:blank"],{stdio:"ignore"});

async function wsUrl(){for(let i=0;i<40;i++){try{const r=await fetch(`http://localhost:${PORT}/json/version`);const j=await r.json();if(j.webSocketDebuggerUrl)return j.webSocketDebuggerUrl;}catch{}await sleep(250);}throw new Error("no devtools");}
const ws=new WebSocket(await wsUrl());await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
let id=0;const pend=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pend.has(m.id)){pend.get(m.id)(m);pend.delete(m.id);}};
const send=(method,params={},sid)=>{const i=++id;const p={id:i,method,params};if(sid)p.sessionId=sid;return new Promise((res,rej)=>{pend.set(i,m=>m.error?rej(new Error(m.error.message)):res(m.result));ws.send(JSON.stringify(p));});};
const {targetId}=await send("Target.createTarget",{url:"about:blank"});
const {sessionId:S}=await send("Target.attachToTarget",{targetId,flatten:true});
await send("Runtime.enable",{},S);
const ev=async expr=>{const r=await send("Runtime.evaluate",{expression:expr,returnByValue:true,awaitPromise:true},S);if(r.exceptionDetails)throw new Error(r.exceptionDetails.text);return r.result.value;};
async function waitHeader(){for(let i=0;i<40;i++){await sleep(300);if(await ev(`!!document.querySelector('.model-header')`))return true;}return false;}

async function nav(u){await send("Page.enable",{},S);await send("Page.navigate",{url:u},S);await waitHeader();}

// 1) no param → hint present, correct text
await nav("http://localhost:8765/index.html");
await sleep(400);
const present = await ev(`!!document.querySelector('.picker-hint')`);
const text = await ev(`(document.querySelector('.picker-hint-bubble')||{}).textContent||''`);
const arrow = await ev(`!!document.querySelector('.picker-hint-arrow')`);
console.log("no-param: hint present =", present, "| text =", JSON.stringify(text), "| arrow =", arrow);
await sleep(3000);
const after = await ev(`!!document.querySelector('.picker-hint')`);
console.log("no-param: hint present after 3.4s =", after);

// 2) with param → hint absent
await nav("http://localhost:8765/index.html?model=access-esm1-6");
await sleep(600);
const withParam = await ev(`!!document.querySelector('.picker-hint')`);
console.log("with-param: hint present =", withParam);

ws.close();chrome.kill();await sleep(200);process.exit(0);
