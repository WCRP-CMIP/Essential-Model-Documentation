// esgf.js — load a model's ESGF dataset rows from the published Arrow bundle.
//
// Given a model's `validation_key` (== ESGF source_id == Arrow filename stem),
// fetch <ESGF_ROOT>/<validation_key>.arrow and parse it in the browser with
// apache-arrow. This is the shared foundation for the model page's
// arrow-data boxes (e.g. "Dataset submissions", "Output grids"). No build step
// — apache-arrow and the zstd fallback are pulled from esm.sh, the same way the
// ESGF-arrow viewers do.
//
// Results are cached per (root, validation_key) so several boxes on one page
// share a single network request instead of each re-fetching the same file.

import * as Arrow from "https://esm.sh/apache-arrow@21";
import { decompress } from "https://esm.sh/fzstd@0.1";

// Defensive: allow zstd-compressed Arrow bodies. Files written uncompressed
// read natively; this only matters if a compressed file ever appears.
try { Arrow.compressionRegistry.set(Arrow.CompressionType.ZSTD, { decode: b => decompress(b) }); } catch {}

// Published ESGF-arrow bundle (Cloudflare Pages). One Arrow file per model at
// the site root: <ESGF_ROOT>/<validation_key>.arrow  (e.g. /UKESM1-3-LL.arrow).
export const ESGF_ROOT = "https://esgf-arrow.pages.dev";

// Timestamps come back as epoch-ms (number or bigint) → JS number.
const toMs = v => (v == null ? null : Number(v));

// (root, validation_key) -> Promise<rows>. Shared across boxes; a rejected
// fetch is evicted so a later box can retry.
const _cache = new Map();

async function _fetchRows(url) {
  const res = await fetch(url, { mode: "cors", cache: "no-store" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${url}`);
  const table = Arrow.tableFromIPC(new Uint8Array(await res.arrayBuffer()));

  const col = name => table.getChild(name);
  const master_id = col("master_id"), updated = col("updated"),
        experiment_id = col("experiment_id"), variable_id = col("variable_id"),
        frequency = col("frequency"), grid_label = col("grid_label"),
        variant_label = col("variant_label"), activity_id = col("activity_id"),
        institution_id = col("institution_id"),
        start_datetime = col("start_datetime"), retracted = col("retracted");

  const rows = new Array(table.numRows);
  for (let i = 0; i < table.numRows; i++) {
    rows[i] = {
      master_id: master_id?.get(i) ?? "",
      updated: toMs(updated?.get(i)),
      start_datetime: toMs(start_datetime?.get(i)),
      experiment_id: experiment_id?.get(i) ?? "",
      variable_id: variable_id?.get(i) ?? "",
      frequency: frequency?.get(i) ?? "",
      grid_label: grid_label?.get(i) ?? "",
      variant_label: variant_label?.get(i) ?? "",
      activity_id: activity_id?.get(i) ?? "",
      institution_id: institution_id?.get(i) ?? "",
      retracted: !!(retracted && retracted.get(i)),
    };
  }
  return rows;
}

// Fetch + parse one model's datasets. Returns an array of plain row objects.
// Throws if the file is missing or unreadable.
export function loadModelDatasets(validationKey, { root = ESGF_ROOT } = {}) {
  if (!validationKey) return Promise.reject(new Error("no validation_key on model record"));
  const base = String(root).replace(/\/+$/, "");
  const cacheKey = `${base}::${validationKey}`;
  if (_cache.has(cacheKey)) return _cache.get(cacheKey);
  const url = `${base}/${encodeURIComponent(validationKey)}.arrow`;
  const p = _fetchRows(url).catch(err => { _cache.delete(cacheKey); throw err; });
  _cache.set(cacheKey, p);
  return p;
}

// Convenience wrapper for the model-page boxes. Resolves the model's datasets
// and logs to the console the reason a box ends up hidden — so a hidden box is
// diagnosable in DevTools instead of silently disappearing. Returns the rows,
// or null when the box should render nothing.
export async function loadDatasetsForBox(boxName, model, esgfRoot) {
  const key = model && model.validation_key;
  if (!key) {
    console.warn(`[EMD ${boxName}] hidden — model "${(model && model["@id"]) || "?"}" has no validation_key in its record`);
    return null;
  }
  try {
    const rows = await loadModelDatasets(key, esgfRoot ? { root: esgfRoot } : {});
    if (!rows.length) {
      console.info(`[EMD ${boxName}] hidden — no ESGF datasets found for "${key}"`);
      return null;
    }
    return rows;
  } catch (e) {
    console.error(`[EMD ${boxName}] hidden — could not load ${key}.arrow:`, e);
    return null;
  }
}
