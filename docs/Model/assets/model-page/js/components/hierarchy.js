// components/hierarchy.js — model → realm → grids → subgrids → cells force graph.
//
// Refactored from Model-CRS/emd_model_graph.html into a mountable component.
// Requires d3 v7 on the page (window.d3). Fetches + resolves nested JSON-LD in
// the browser, then renders a tiered force layout (model at top, grid cells at
// the bottom) with embedded-parent nests, coupling arcs, hover spotlight, zoom.

import { Resolver, short } from "../resolver.js";
import { realmColor } from "../crs.js";

const FIELD_TYPE = {
  "model_components": "component_config",
  "component_configs": "component_config",
  "horizontal_computational_grid": "horizontal_computational_grid",
  "vertical_computational_grid": "vertical_computational_grid",
  "horizontal_subgrids": "horizontal_subgrid",
  "horizontal_grid_cell": "horizontal_grid_cell",
  "horizontal_grid_cells": "horizontal_grid_cell",
  "family": "model_family",
};
const TYPES = {
  "model":                         { tier: 0,  fill: "#1f4e79", stroke: "#1f4e79", text: "#fff" },
  "model_family":                  { tier: -1, fill: "#efe3ff", stroke: "#6a3aa8", text: "#3a1b5e" },
  "component_config":              { tier: 1,  fill: "#ffffff", stroke: "#2b3a55", text: "#14223a" },
  "model_component":               { tier: 2,  fill: "#fff3e0", stroke: "#c77d24", text: "#5a3d10" },
  "component_family":              { tier: 3,  fill: "#efe3ff", stroke: "#6a3aa8", text: "#3a1b5e" },
  "vertical_computational_grid":   { tier: 4,  fill: "#e3f0fb", stroke: "#4a90d9", text: "#14223a" },
  "horizontal_computational_grid": { tier: 5,  fill: "#d3e6fb", stroke: "#1565c0", text: "#14223a" },
  "horizontal_subgrid":            { tier: 6,  fill: "#ffffff", stroke: "#6b7280", text: "#14223a" },
  "horizontal_grid_cell":          { tier: 7,  fill: "#e3f3e9", stroke: "#2d6a4f", text: "#14223a" },
};
const ROW_NAME = { "-1": "family", "0": "model", "1": "realm · config",
  "2": "component", "3": "component family",
  "4": "vertical grid", "5": "horizontal grid", "6": "subgrid", "7": "grid cell" };
const LEFT_RAIL = 120;

// Map each node type to its repo folder (component families are stored as
// model_family records) and build a GitHub source link for that record.
const TYPE_FOLDER = {
  "model": "model",
  "model_family": "model_family",
  "component_config": "component_config",
  "model_component": "model_component",
  "component_family": "model_family",
  "vertical_computational_grid": "vertical_computational_grid",
  "horizontal_computational_grid": "horizontal_computational_grid",
  "horizontal_subgrid": "horizontal_subgrid",
  "horizontal_grid_cell": "horizontal_grid_cell",
};
const GH_BASE = "https://github.com/WCRP-CMIP/Essential-Model-Documentation/blob/src-data";
const ghUrl = node => {
  const folder = TYPE_FOLDER[node.type];
  const fileId = short(node.id);
  return folder && fileId ? `${GH_BASE}/${folder}/${fileId}.json` : null;
};
// Reliably open a new tab. window.open(url, "_blank", "noopener") is treated as
// a popup by Chrome and silently blocked even on a user gesture; a synthesized
// anchor click is not.
function openInNewTab(url) {
  const a = document.createElement("a");
  a.href = url; a.target = "_blank"; a.rel = "noopener noreferrer";
  document.body.appendChild(a);
  a.click();
  a.remove();
}

const vocab = v =>
  typeof v === "string" ? short(v)
  : Array.isArray(v) ? v.map(vocab).filter(Boolean).join(", ")
  : (v && typeof v === "object") ? short(v["@id"] || v.validation_key || "") : "";
const nameOf = it =>
  typeof it === "string" ? short(it)
  : (it && typeof it === "object") ? short(it["@id"] || it.validation_key || "") : null;

function metaFor(type, n) {
  const out = [];
  if (type === "horizontal_grid_cell") {
    const gt = vocab(n.grid_type); if (gt) out.push(gt);
    if (Number.isInteger(n.n_cells)) out.push(`${n.n_cells.toLocaleString()} cells`);
  } else if (type === "horizontal_computational_grid") {
    const a = vocab(n.arrangement); if (a) out.push(a);
  } else if (type === "vertical_computational_grid") {
    if (n.n_z) out.push(`${n.n_z} levels`);
    const vc = vocab(n.vertical_coordinate); if (vc) out.push(vc);
  } else if (type === "horizontal_subgrid") {
    const c = vocab(n.cell_variable_type); if (c) out.push(c);
  }
  return out;
}

async function buildGraph(resolver, modelId, depth) {
  const model = await resolver.model(modelId);
  const rootId = model["@id"] || modelId;

  const dyn = new Set((model.dynamic_components || []).map(nameOf).filter(Boolean));
  const embChild = new Map();
  (model.embedded_components || []).forEach(p => {
    if (Array.isArray(p) && p.length === 2) embChild.set(nameOf(p[0]), nameOf(p[1])); // [child,parent]
  });
  const couplingPairs = [];
  const seen = new Set();
  const addPair = (a, b) => {
    if (!a || !b || a === b) return;
    const k = [a, b].sort().join("\u0000");
    if (!seen.has(k)) { seen.add(k); couplingPairs.push([a, b]); }
  };
  (model.coupled_components || []).forEach(p => { if (Array.isArray(p) && p.length === 2) addPair(nameOf(p[0]), nameOf(p[1])); });

  const nodes = new Map();
  const links = [];
  const add = (id, type, meta, extra = {}) => {
    if (!nodes.has(id)) nodes.set(id, { id, type, label: short(id), meta: meta || [] });
    Object.assign(nodes.get(id), extra);
    return nodes.get(id);
  };
  const link = (a, b) => links.push({ source: a, target: b });

  add(rootId, "model");
  const fam = model.family;
  if (fam) { const f = nameOf(fam); add(f, "model_family"); links.push({ source: rootId, target: f, kind: "family" }); }

  const REALM_OF = id => String(id).split("_")[0];

  async function walk(node, parentId, key, d) {
    if (Array.isArray(node)) { for (const v of node) await walk(v, parentId, key, d); return; }
    if (typeof node === "string") {
      const type = FIELD_TYPE[key];
      if (!parentId || !type) return;
      if (d > 0 && Resolver.folderFor(key)) {
        try { await emit(await resolver.fetchDoc(Resolver.folderFor(key), node), parentId, key, d); return; }
        catch (e) { /* stub below */ }
      }
      add(node, type, []); if (parentId !== node) link(parentId, node);
      return;
    }
    if (node && typeof node === "object" && node["@id"]) {
      const ref = node["@id"];
      if (d > 0 && Resolver.folderFor(key) && Object.keys(node).length <= 3) {
        try { await emit(await resolver.fetchDoc(Resolver.folderFor(key), ref), parentId, key, d); return; }
        catch (e) { /* fall through */ }
      }
      await emit(node, parentId, key, d);
    }
  }

  async function emit(node, parentId, key, d) {
    const type = FIELD_TYPE[key];
    if (!TYPES[type]) return;
    const id = node["@id"];
    if (type === "component_config") {
      const realm = REALM_OF(id);
      const compId = nameOf(node.model_component);
      add(id, type, [], { label: realm, realm, embedded: embChild.has(realm) });
      if (parentId && parentId !== id) link(parentId, id);

      // model_component as its own node, and its component family beyond that.
      if (compId) {
        let compDoc = null;
        if (d > 0) { try { compDoc = await resolver.fetchDoc("model_component", compId); } catch (_) {} }
        add(compId, "model_component",
            compDoc ? [compDoc.component ? vocab(compDoc.component) : ""].filter(Boolean) : [],
            { label: (compDoc && (compDoc.name || compDoc.ui_label)) ? (compDoc.name || compDoc.ui_label) : compId });
        link(id, compId);
        const cfam = compDoc && nameOf(compDoc.family);
        if (cfam) {
          let famDoc = null;
          if (d > 1) { try { famDoc = await resolver.fetchDoc("model_family", cfam); } catch (_) {} }
          add(cfam, "component_family",
              famDoc && famDoc.primary_institution ? [vocab(famDoc.primary_institution)] : [],
              { label: (famDoc && (famDoc.ui_label || famDoc.validation_key)) ? (famDoc.ui_label || famDoc.validation_key) : cfam });
          link(compId, cfam);
        }
      }

      for (const k of ["horizontal_computational_grid", "vertical_computational_grid"])
        if (node[k] !== undefined) await walk(node[k], id, k, d - 1);
      return;
    }
    add(id, type, metaFor(type, node));
    if (parentId && parentId !== id) link(parentId, id);
    for (const k of Object.keys(node)) {
      if (Resolver.isMeta(k) || Resolver.isModelMeta(k) || Resolver.isInline(k) || Resolver.isScalar(k)) continue;
      await walk(node[k], id, k, d - 1);
    }
  }

  for (const k of Object.keys(model)) {
    if (Resolver.isMeta(k) || Resolver.isModelMeta(k) || Resolver.isInline(k) || Resolver.isScalar(k)) continue;
    await walk(model[k], rootId, k, depth);
  }

  // nests + embed links
  const byRealm = new Map();
  for (const nn of nodes.values()) if (nn.type === "component_config" && nn.realm) byRealm.set(nn.realm, nn);
  const grouped = new Map();
  for (const [child, parent] of embChild) {
    const cn = byRealm.get(child); if (!cn) continue;
    if (!grouped.has(parent)) grouped.set(parent, []);
    grouped.get(parent).push(cn);
  }
  const nests = [], embedLinks = [];
  for (const [parent, kids] of grouped) {
    const pn = byRealm.get(parent); if (!pn) continue;
    nests.push({ id: `nest:${parent}`, parent, members: [pn, ...kids] });
    for (const c of kids) embedLinks.push({ source: pn.id, target: c.id });
  }
  const couplings = [];
  for (const [ra, rb] of couplingPairs) {
    const a = byRealm.get(ra), b = byRealm.get(rb);
    if (a && b) couplings.push({ source: a.id, target: b.id });
  }

  return { rootId, nodes: [...nodes.values()], links, nests, embedLinks, couplings };
}

function sizeNode(d) {
  const lines = [d.label, ...(d.inside ? [d.inside] : []), ...(d.meta || [])];
  d.w = Math.max(92, Math.max(...lines.map(s => (s ? s.length : 0) * 6.6)) + 18);
  d.h = 24 + (lines.length - 1) * 12;
}

export async function mountHierarchy(root, { modelId, base, depth = 8 }) {
  const d3 = window.d3;
  const resolver = new Resolver(base);

  const wrap = document.createElement("section");
  wrap.className = "card hierarchy";
  wrap.innerHTML = `<h2 class="card-title">EMD schema</h2>
    <dl class="h-key">
      <dt>structure</dt><dd>Model → realm · component → vertical &amp; horizontal grids → subgrids → grid cells</dd>
      <dt>hover</dt><dd>highlights a node's parents and children</dd>
      <dt>double-click</dt><dd>opens that record's source JSON on GitHub ↗</dd>
      <dt>dashed nest</dt><dd>embedded realms wrapped inside their host</dd>
      <dt>dashed arc</dt><dd>couplings between realms</dd>
    </dl>`;
  const holder = document.createElement("div");
  holder.className = "hierarchy-canvas";
  const svgEl = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  holder.appendChild(svgEl);
  const zoombar = document.createElement("div");
  zoombar.className = "hierarchy-zoom";
  zoombar.innerHTML = `<button data-z="in" title="Zoom in" aria-label="Zoom in">+</button>` +
    `<button data-z="out" title="Zoom out" aria-label="Zoom out">−</button>` +
    `<button data-z="fit" title="Fit to view" aria-label="Fit to view">` +
      `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">` +
      `<path d="M4 9V5a1 1 0 0 1 1-1h4M15 4h4a1 1 0 0 1 1 1v4M20 15v4a1 1 0 0 1-1 1h-4M9 20H5a1 1 0 0 1-1-1v-4"/></svg></button>`;
  holder.appendChild(zoombar);
  wrap.appendChild(holder);
  root.appendChild(wrap);

  if (!d3) {
    holder.innerHTML = `<p class="card-sub" style="padding:1rem">d3 is not loaded — the hierarchy diagram needs D3 v7.</p>`;
    return;
  }

  let graph;
  try { graph = await buildGraph(resolver, modelId, depth); }
  catch (e) { holder.innerHTML = `<p class="card-sub" style="padding:1rem;color:#b3261e">Could not load hierarchy: ${e.message}</p>`; return; }

  const svg = d3.select(svgEl);
  let zoom, rootG, sim;

  function render() {
    svg.selectAll("*").remove();
    const W = holder.clientWidth || 900, H = 560;
    svgEl.setAttribute("viewBox", `0 0 ${W} ${H}`);
    rootG = svg.append("g");

    const byId = new Map(graph.nodes.map(n => [n.id, n]));
    graph.nodes.forEach(n => { n.tier = TYPES[n.type]?.tier ?? 3; sizeNode(n); });
    const tiers = [...new Set(graph.nodes.map(n => n.tier))].sort((a, b) => a - b);
    const rowGap = Math.max(90, (H - 70) / Math.max(tiers.length, 1));
    const marginTop = 44;
    const rowY = new Map(tiers.map((t, i) => [t, marginTop + i * rowGap]));

    const SPREAD = Math.max(W * 2.2, 1600);
    d3.groups(graph.nodes, n => n.tier).forEach(([tier, members]) => {
      const y = rowY.get(tier);
      members.sort((a, b) => a.id.localeCompare(b.id));
      const step = SPREAD / Math.max(members.length, 1);
      members.forEach((n, i) => { n.targetY = y; n.fy = y; n.y = y; n.x = W / 2 - SPREAD / 2 + step * (i + 0.5); });
    });

    const parents = new Map(), children = new Map(), coupled = new Map();
    graph.nodes.forEach(n => { parents.set(n.id, new Set()); children.set(n.id, new Set()); coupled.set(n.id, new Set()); });
    graph.links.forEach(l => { const s = l.source.id ?? l.source, t = l.target.id ?? l.target; children.get(s)?.add(t); parents.get(t)?.add(s); });
    (graph.couplings || []).forEach(c => { coupled.get(c.source)?.add(c.target); coupled.get(c.target)?.add(c.source); });

    const nestG = rootG.append("g");
    const nestSel = nestG.selectAll("g.h-nest").data(graph.nests).join("g").attr("class", "h-nest");
    nestSel.append("rect"); nestSel.append("text").text(d => d.parent);

    const linkSel = rootG.append("g").selectAll("path").data(graph.links).join("path")
      .attr("class", d => "h-link" + (d.kind === "family" ? " family" : ""));

    const coupleG = rootG.append("g");
    const coupleSel = coupleG.selectAll("path").data(graph.couplings || []).join("path").attr("class", "h-couple");

    const nodeSel = rootG.append("g").selectAll("g.h-node").data(graph.nodes).join("g").attr("class", "h-node");
    nodeSel.each(function (d) {
      const g = d3.select(this), cfg = TYPES[d.type] || {};
      const url = ghUrl(d);
      g.append("title").text(url ? `Double-click to open ${short(d.id)}.json on GitHub ↗` : short(d.id));
      const realmFill = d.type === "component_config" && d.realm ? realmColor(d.realm) : null;
      g.append("rect").attr("x", -d.w / 2).attr("y", -d.h / 2).attr("width", d.w).attr("height", d.h)
        .attr("rx", 5)
        .attr("fill", d.embedded ? "#fff7d6" : (realmFill ? tint(realmFill) : cfg.fill))
        .attr("stroke", realmFill || cfg.stroke);
      const tx = g.append("text").attr("text-anchor", "middle").attr("y", -d.h / 2 + 14);
      tx.append("tspan").attr("class", "h-nid").attr("x", 0).attr("fill", cfg.text).text(d.label);
      if (d.inside) tx.append("tspan").attr("class", "h-inside").attr("x", 0).attr("dy", 12).text(d.inside);
      (d.meta || []).forEach(m => tx.append("tspan").attr("class", "h-meta").attr("x", 0).attr("dy", 12).text(m));
    });

    nodeSel
      .on("dblclick", (e, d) => {
        const url = ghUrl(d);
        if (!url) return;
        e.preventDefault(); e.stopPropagation();   // don't let the zoom behavior treat this as dblclick-to-zoom
        openInNewTab(url);
      })
      .on("mouseenter", (e, d) => {
        const hot = new Set([d.id, ...parents.get(d.id), ...children.get(d.id), ...coupled.get(d.id)]);
        svg.classed("focus", true);
        nodeSel.classed("hot", n => hot.has(n.id));
        linkSel.classed("hot", l => { const s = l.source.id ?? l.source, t = l.target.id ?? l.target; return (s === d.id && hot.has(t)) || (t === d.id && hot.has(s)); });
        coupleSel.classed("hot", c => c.source === d.id || c.target === d.id);
      })
      .on("mouseleave", () => { svg.classed("focus", false); nodeSel.classed("hot", false); linkSel.classed("hot", false); coupleSel.classed("hot", false); });

    function nestRepel(alpha) {
      const ns = graph.nests; if (ns.length < 2) return;
      const m = ns.map(nest => { let lo = Infinity, hi = -Infinity, sum = 0; nest.members.forEach(n => { lo = Math.min(lo, n.x - n.w / 2); hi = Math.max(hi, n.x + n.w / 2); sum += n.x; }); return { lo, hi, cx: sum / nest.members.length, w: hi - lo }; });
      for (let i = 0; i < ns.length; i++) for (let j = i + 1; j < ns.length; j++) {
        const a = m[i], b = m[j], dx = b.cx - a.cx, min = (a.w + b.w) / 2 + 90;
        if (Math.abs(dx) >= min) continue;
        const push = (min - Math.abs(dx)) * alpha * 0.5, sign = dx === 0 ? 1 : Math.sign(dx);
        ns[i].members.forEach(n => n.vx = (n.vx || 0) - sign * push);
        ns[j].members.forEach(n => n.vx = (n.vx || 0) + sign * push);
      }
    }

    sim = d3.forceSimulation(graph.nodes)
      .force("x", d3.forceX(W / 2).strength(0.015))
      .force("charge", d3.forceManyBody().strength(-380).distanceMax(460))
      .force("link", d3.forceLink(graph.links).id(d => d.id).distance(0).strength(0.08))
      .force("embed", d3.forceLink(graph.embedLinks).id(d => d.id).distance(d => (d.source.w + d.target.w) / 2 + 16).strength(0.5))
      .force("collide", d3.forceCollide(d => Math.hypot(d.w / 2, d.h / 2) + 12).strength(1).iterations(3))
      .force("nest", nestRepel)
      .alphaDecay(0.02)
      .on("tick", tick);

    function tick() {
      linkSel.attr("d", d => { const s = d.source, t = d.target; const sy = s.y + s.h / 2, ty = t.y - t.h / 2, my = (sy + ty) / 2; return `M${s.x},${sy} C${s.x},${my} ${t.x},${my} ${t.x},${ty}`; });
      nodeSel.attr("transform", d => `translate(${d.x},${d.y})`);
      coupleSel.attr("d", c => { const s = byId.get(c.source), t = byId.get(c.target); if (!s || !t) return null; const x1 = s.x, y1 = s.y - s.h / 2, x2 = t.x, y2 = t.y - t.h / 2, mx = (x1 + x2) / 2, lift = Math.min(80, 24 + Math.abs(x2 - x1) * 0.16); return `M${x1},${y1} Q${mx},${Math.min(y1, y2) - lift} ${x2},${y2}`; });
      const PAD = 12;
      nestSel.each(function (nest) {
        let lx = Infinity, rx = -Infinity, ty = Infinity, by = -Infinity;
        nest.members.forEach(n => { lx = Math.min(lx, n.x - n.w / 2); rx = Math.max(rx, n.x + n.w / 2); ty = Math.min(ty, n.y - n.h / 2); by = Math.max(by, n.y + n.h / 2); });
        const g = d3.select(this);
        g.select("rect").attr("x", lx - PAD).attr("y", ty - PAD - 4).attr("width", rx - lx + 2 * PAD).attr("height", by - ty + 2 * PAD + 4);
        g.select("text").attr("x", lx - PAD + 8).attr("y", ty - PAD + 8);
      });
    }

    nodeSel.call(d3.drag()
      .on("start", (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; })
      .on("drag", (e, d) => { d.fx = e.x; })
      .on("end", (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; }));

    zoom = d3.zoom().scaleExtent([0.05, 4]).on("zoom", e => { rootG.attr("transform", e.transform); rail(e.transform); });
    svg.call(zoom);
    svg.on("dblclick.zoom", null);   // dblclick is reserved for opening a node's GitHub source

    // left rail
    const railG = svg.append("g").attr("class", "h-rail").style("pointer-events", "none");
    railG.append("rect").attr("x", 0).attr("y", 0).attr("width", LEFT_RAIL).attr("height", "100%").attr("fill", "var(--paper,#f7f5ef)");
    railG.append("line").attr("x1", LEFT_RAIL).attr("y1", 0).attr("x2", LEFT_RAIL).attr("y2", "100%").attr("stroke", "var(--line,#c9d2e0)");
    const railSel = railG.selectAll("text.h-row").data(tiers).join("text").attr("class", "h-row").attr("x", LEFT_RAIL - 8).text(t => ROW_NAME[String(t)] || "");
    function rail(tf) { railSel.attr("y", t => tf.y + tf.k * rowY.get(t)); }

    sim.alpha(1).restart();
    for (let i = 0; i < 500; i++) sim.tick();
    tick();
    fit();
    sim.on("end.fit", fit);
    rail(d3.zoomIdentity);

    function fit() {
      const w = holder.clientWidth || W, hgt = H, pad = 50;
      let m = { x0: Infinity, x1: -Infinity, y0: Infinity, y1: -Infinity };
      graph.nodes.forEach(n => { m.x0 = Math.min(m.x0, n.x - n.w / 2); m.x1 = Math.max(m.x1, n.x + n.w / 2); m.y0 = Math.min(m.y0, n.y - n.h / 2); m.y1 = Math.max(m.y1, n.y + n.h / 2); });
      const spanX = Math.max(m.x1 - m.x0, 10), spanY = Math.max(m.y1 - m.y0, 10);
      const availW = Math.max(w - LEFT_RAIL - pad, 100), availH = Math.max(hgt - 2 * pad, 100);
      const scale = Math.min(availW / spanX, availH / spanY);
      const tx = LEFT_RAIL + (availW - scale * spanX) / 2 - scale * m.x0;
      const ty = pad + (availH - scale * spanY) / 2 - scale * m.y0;
      svg.transition().duration(400).call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
    }
    holder._fit = fit;
  }

  zoombar.addEventListener("click", e => {
    const btn = e.target.closest("button"); if (!btn) return;
    const z = btn.dataset.z; if (!z) return;
    if (z === "in") svg.transition().duration(200).call(zoom.scaleBy, 1.4);
    else if (z === "out") svg.transition().duration(200).call(zoom.scaleBy, 1 / 1.4);
    else if (z === "fit" && holder._fit) holder._fit();
  });

  render();
  let rT;
  window.addEventListener("resize", () => { clearTimeout(rT); rT = setTimeout(render, 250); });
}

// lighten a hex colour toward white for node fills
function tint(hex) {
  const m = hex.replace("#", "");
  const r = parseInt(m.slice(0, 2), 16), g = parseInt(m.slice(2, 4), 16), b = parseInt(m.slice(4, 6), 16);
  const mix = c => Math.round(c + (255 - c) * 0.82);
  return `rgb(${mix(r)},${mix(g)},${mix(b)})`;
}
