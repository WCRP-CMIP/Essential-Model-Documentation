// svg-export.js — download an inline SVG as a self-contained, attributed .svg file.
//
// Adapted from ESGF-view (src/lib/svg-export.js) so the EMD schema downloads the same way as
// the ESGF charts: styles inlined, a CMIP watermark, an RDF / Dublin Core metadata block, and a
// SHA-256 hash of the content so later edits can be detected. The on-screen SVG is never
// touched: everything below happens on a clone.
//
// Differences from the ESGF-view version:
//  - the CMIP logo is fetched from the site (assets/cmip-logo.svg) instead of being bundled,
//    and the export simply goes without it if it cannot be read (e.g. a file:// copy);
//  - an optional footer band is added under the diagram, so the watermark never overlaps it;
//  - a `prepare(clone)` hook lets the caller adjust the clone (for example to reset pan / zoom)
//    before styles are inlined.

const AUTHOR       = "Daniel Ellis";
const AUTHOR_NOTE  = "commissioned for CMIP IPO";
const AUTHOR_ORCID = "https://orcid.org/0000-0001-6733-7028";
const AUTHOR_GITHUB_USER = "wolfiex";
const AUTHOR_GITHUB = "https://github.com/" + AUTHOR_GITHUB_USER;
const PUBLISHER    = "CMIP IPO";
const WEBSITE      = "https://wcrp-cmip.org";
const CONTACT      = "ipo@wcrp-cmip.org";
const LICENSE      = "https://creativecommons.org/licenses/by/4.0/";
const BRAND_FONT   = "Lexend, 'Helvetica Neue', Arial, sans-serif";
const TOOLTIP      = "Original hosted by the CMIP IPO";

const SVG_NS = "http://www.w3.org/2000/svg";

// The download icon for the diagrams' buttons. A line icon: it is drawn in the button's text colour.
export const DOWNLOAD_ICON =
  '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" ' +
  'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<path d="M12 4v11"/><path d="m7 11 5 5 5-5"/><path d="M5 20h14"/></svg>';

async function sha256Hex(str) {
  const buf = new TextEncoder().encode(str);
  const digest = await crypto.subtle.digest("SHA-256", buf);
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, "0")).join("");
}

let logoText;   // undefined = not tried yet, null = unavailable
async function loadLogo() {
  if (logoText !== undefined) return logoText;
  try {
    // NAV_PREFIX is set by the build (the path from this page back to the site root).
    const prefix = (typeof window !== "undefined" && window.NAV_PREFIX) ? window.NAV_PREFIX : "../../";
    const r = await fetch(prefix + "assets/cmip-logo.svg");
    logoText = r.ok ? await r.text() : null;
  } catch (e) { logoText = null; }
  return logoText;
}

/** Serialize an inline SVG element into a downloadable, attributed SVG file.
 *  opts: { title, fileName, subtitle, heading, subheading, sourceUrl, header, footer, prepare, decorate }
 *    title     — used in <title>/<desc>/metadata and, if no fileName, the file name
 *    fileName  — file name without the .svg extension
 *    subtitle  — optional extra line in the watermark (e.g. "model UKESM1-3-LL")
 *    heading   — optional visible heading, top-left, so the file says what it shows on its own
 *    subheading— optional second line under the heading, in monospace (e.g. a CRS string)
 *    header    — extra height added ABOVE the diagram (the content is moved down) for the heading
 *    footer    — extra height (in the SVG's own units) added under the diagram for the watermark
 *    prepare   — function(clone) called on the clone before anything else; may change attributes
 *    decorate  — function(clone, { vbW, vbH, footerTop }) called last, to draw extras (a legend) into the footer */
export async function exportSvg(svgEl, opts = {}) {
  const {
    title = "diagram",
    fileName = "",
    subtitle = "",
    heading = "",
    subheading = "",
    sourceUrl = (typeof location !== "undefined") ? location.href.split("#")[0] : "",
    header = 0,
    footer = 0,
    prepare = null,
    decorate = null,
  } = opts;

  // Clone so the live diagram is never touched.
  const clone = svgEl.cloneNode(true);
  clone.setAttribute("xmlns", SVG_NS);
  clone.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");
  clone.setAttribute("xmlns:dc",  "http://purl.org/dc/elements/1.1/");
  clone.setAttribute("xmlns:cc",  "http://creativecommons.org/ns#");
  clone.setAttribute("xmlns:rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#");

  if (prepare) prepare(clone);

  // Copy the computed style of every element into an inline style, so the file renders on its
  // own (no page stylesheet or CSS variables to resolve against). Done BEFORE anything is added.
  inlineStyles(svgEl, clone);

  // Room above the diagram for a heading: move everything down by `header`.
  if (header) {
    const shifted = document.createElementNS(SVG_NS, "g");
    shifted.setAttribute("transform", `translate(0 ${header})`);
    while (clone.firstChild) shifted.appendChild(clone.firstChild);
    clone.appendChild(shifted);
  }

  // Size: explicit width / height so viewers and editors open it at a sensible size.
  const vb = (clone.getAttribute("viewBox") || `0 0 ${svgEl.clientWidth || 900} ${svgEl.clientHeight || 560}`)
    .split(/\s+/).map(Number);
  const vbW = vb[2], vbH = vb[3] + header + footer;
  clone.setAttribute("viewBox", `0 0 ${vbW} ${vbH}`);
  clone.setAttribute("width", String(Math.round(vbW)));
  clone.setAttribute("height", String(Math.round(vbH)));

  // Background: the page's own paper colour, as a real rectangle (a CSS background is ignored by
  // many viewers and converters).
  const holderBg = svgEl.parentElement ? getComputedStyle(svgEl.parentElement).backgroundColor : "";
  const bg = (holderBg && holderBg !== "rgba(0, 0, 0, 0)" && holderBg !== "transparent") ? holderBg : "#ffffff";
  const bgRect = document.createElementNS(SVG_NS, "rect");
  bgRect.setAttribute("x", "0"); bgRect.setAttribute("y", "0");
  bgRect.setAttribute("width", String(vbW)); bgRect.setAttribute("height", String(vbH));
  bgRect.setAttribute("fill", bg);
  clone.insertBefore(bgRect, clone.firstChild);

  // <title> = hover tooltip; <desc> = long-form attribution.
  const titleEl = document.createElementNS(SVG_NS, "title"); titleEl.textContent = TOOLTIP;
  const descEl = document.createElementNS(SVG_NS, "desc");
  descEl.textContent = `${title} — ${PUBLISHER}. Created by ${AUTHOR} (${AUTHOR_NOTE}), ORCID ${AUTHOR_ORCID}, GitHub @${AUTHOR_GITHUB_USER}. `
    + `Website ${WEBSITE}. Contact ${CONTACT}. Original hosted at ${sourceUrl}.`;
  clone.insertBefore(descEl, clone.firstChild);
  clone.insertBefore(titleEl, clone.firstChild);

  // Watermark, bottom-right: CMIP logo, then right-aligned text lines above it.
  const wm = document.createElementNS(SVG_NS, "g");
  wm.setAttribute("opacity", "0.7");
  const PAD = 10, LOGO_H = 28;
  const logoY = vbH - PAD - LOGO_H;

  const logoRaw = await loadLogo();
  if (logoRaw) {
    const logoSvg = new DOMParser().parseFromString(logoRaw, "image/svg+xml").documentElement;
    const [, , logoW, logoH] = (logoSvg.getAttribute("viewBox") || "0 0 228 210").split(/\s+/).map(Number);
    const scale = LOGO_H / logoH;
    const logoG = document.createElementNS(SVG_NS, "g");
    logoG.setAttribute("transform", `translate(${vbW - PAD - logoW * scale} ${logoY}) scale(${scale})`);
    while (logoSvg.firstChild) logoG.appendChild(logoSvg.firstChild);
    wm.appendChild(logoG);
  }

  const line = (y, text, weight) => {
    const t = document.createElementNS(SVG_NS, "text");
    t.setAttribute("x", String(vbW - PAD)); t.setAttribute("y", String(y)); t.setAttribute("text-anchor", "end");
    t.setAttribute("font-family", BRAND_FONT); t.setAttribute("font-size", "10"); t.setAttribute("fill", "#0f1720");
    if (weight) t.setAttribute("font-weight", weight);
    t.textContent = text; wm.appendChild(t);
  };
  const base = logoY - 6;
  line(base - 24, "© CC-BY 4.0 · CMIP-IPO", "bold");
  line(base - 12, WEBSITE);
  if (subtitle) line(base, subtitle);
  clone.appendChild(wm);

  if (heading) {
    const h = document.createElementNS(SVG_NS, "text");
    h.setAttribute("x", "14"); h.setAttribute("y", "26");
    h.setAttribute("font-family", BRAND_FONT); h.setAttribute("font-size", "14"); h.setAttribute("font-weight", "bold");
    h.setAttribute("fill", "#0f1720"); h.textContent = heading;
    clone.appendChild(h);
  }
  if (subheading) {
    const h2 = document.createElementNS(SVG_NS, "text");
    h2.setAttribute("x", "14"); h2.setAttribute("y", "46");
    h2.setAttribute("font-family", "ui-monospace, Menlo, Consolas, monospace"); h2.setAttribute("font-size", "11");
    h2.setAttribute("fill", "#5d6b82"); h2.textContent = subheading;
    clone.appendChild(h2);
  }
  if (decorate) decorate(clone, { vbW, vbH, footerTop: vbH - footer });

  // RDF / Dublin Core metadata. Invisible in a viewer; found by XML tools and metadata readers.
  // Parsed as XML (not set with innerHTML): the HTML parser lower-cases tag names, which would
  // turn <rdf:RDF> into <rdf:rdf> and make the block unreadable to RDF tools.
  const nowIso = new Date().toISOString();
  const metadataXml = `<metadata xmlns="${SVG_NS}" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
      xmlns:cc="http://creativecommons.org/ns#" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <rdf:RDF>
      <cc:Work rdf:about="">
        <dc:title>${escapeXml(title)}</dc:title>
        <dc:creator>
          <cc:Agent rdf:about="${AUTHOR_ORCID}">
            <dc:title>${AUTHOR} (${AUTHOR_NOTE})</dc:title>
            <dc:identifier>${AUTHOR_ORCID}</dc:identifier>
            <dc:identifier>${AUTHOR_GITHUB}</dc:identifier>
          </cc:Agent>
        </dc:creator>
        <dc:publisher>
          <cc:Agent rdf:about="${WEBSITE}">
            <dc:title>${PUBLISHER}</dc:title>
            <dc:identifier>${WEBSITE}</dc:identifier>
          </cc:Agent>
        </dc:publisher>
        <dc:contributor><cc:Agent><dc:title>${CONTACT}</dc:title></cc:Agent></dc:contributor>
        <dc:date>${escapeXml(nowIso)}</dc:date>
        <dc:source>${escapeXml(sourceUrl)}</dc:source>
        <dc:rights>© ${new Date().getFullYear()} CMIP-IPO. Licensed under CC-BY 4.0. Contact ${CONTACT}.</dc:rights>
        <cc:license rdf:resource="${LICENSE}"/>
        <dc:relation>Commission: CMIP - IPO</dc:relation>
        <dc:relation>${WEBSITE}</dc:relation>
      </cc:Work>
    </rdf:RDF>
  </metadata>`;
  const metadataDoc = new DOMParser().parseFromString(metadataXml, "image/svg+xml");
  if (!metadataDoc.querySelector("parsererror")) clone.appendChild(document.importNode(metadataDoc.documentElement, true));

  // SHA-256 of the SVG BEFORE the identifier is added: strip the identifier, re-serialise and
  // re-hash to check whether the file was changed after export. Needs a secure context
  // (https or localhost); where crypto.subtle is unavailable the hash is left out.
  if (typeof crypto !== "undefined" && crypto.subtle) {
    const pre = new XMLSerializer().serializeToString(clone);
    const idEl = document.createElementNS(SVG_NS, "metadata");
    idEl.setAttribute("id", "content-hash");
    idEl.textContent = `sha256:${await sha256Hex(pre)}`;
    clone.appendChild(idEl);
  }

  const out = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n` + new XMLSerializer().serializeToString(clone);
  const blob = new Blob([out], { type: "image/svg+xml;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = safeFilename(fileName || title) + ".svg";
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// Copy the *computed* style of the properties that matter for an SVG into an inline `style`
// attribute on each element of the clone.
function inlineStyles(source, target) {
  const srcAll = source.querySelectorAll("*"), tgtAll = target.querySelectorAll("*");
  const props = ["fill", "fill-opacity", "stroke", "stroke-opacity", "stroke-width", "stroke-dasharray",
    "stroke-linecap", "stroke-linejoin", "opacity", "font-family", "font-size", "font-weight", "letter-spacing",
    "text-anchor", "text-transform", "dominant-baseline"];
  for (let i = 0; i < srcAll.length; i++) {
    const cs = getComputedStyle(srcAll[i]); let inline = "";
    for (const p of props) {
      const v = cs.getPropertyValue(p);
      if (v && v !== "auto" && v !== "normal") inline += `${p}:${v};`;
    }
    if (inline) tgtAll[i].setAttribute("style", inline);
  }
  const rcs = getComputedStyle(source);
  target.setAttribute("style", `font-family:${rcs.fontFamily || BRAND_FONT};`);
}

const escapeXml = s => String(s).replace(/[<>&"']/g, c => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;", "'": "&apos;" }[c]));
const safeFilename = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 80) || "diagram";
