// Measure an implemented page against a written spec at several viewport widths, and report mismatches as numbers.
//
//   node inspect_layout.mjs <spec.json> [--out DIR] [--page FILE_OR_URL] [--reference-dir DIR] [--no-fail]
//
// spec.json:
//   { "page": "index.html" | "http://localhost:3000/",   (relative paths are resolved from the spec's folder)
//     "widths": [375, 768, 1280], "height": 900, "tolerance_px": 2,
//     "checks": [
//       { "id": "card-width", "selector": ".card", "at": [1280],             (at: widths this check applies to; default all)
//         "box": { "width": 360, "x": 460 },                               (any of x, y, width, height; px, page coords)
//         "style": { "font-size": "16px", "color": "#1d1d1b", "border-radius": "12px" },
//         "visible": true, "count": 3, "text": "Pro",                         (optional)
//         "min_target_px": 44 } ] }                                          (optional: tap target at least this big)
//   --reference-dir DIR  compares a full-page screenshot per width with DIR/<width>.png if present, inside the
//                        browser (canvas), and reports the share of pixels that differ by more than 24/255.
//
// Writes DIR/report.json, DIR/report.md and DIR/shot-<width>.png. Exits 1 if any check fails (unless --no-fail).
// It reports measured values next to expected ones. It does not score taste: a person still looks at the shots.
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const VALUED = new Set(["--out", "--page", "--reference-dir"]), pos = [];
for (let i = 0; i < args.length; i++) { if (VALUED.has(args[i])) { i++; continue; } if (!args[i].startsWith("--")) pos.push(args[i]); }
const specPath = pos[0];
if (!specPath) { console.error("usage: node inspect_layout.mjs <spec.json> [--out DIR] [--page FILE_OR_URL] [--reference-dir DIR] [--no-fail]"); process.exit(2); }
const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
const base = path.dirname(path.resolve(specPath));
const out = path.resolve(opt("--out", path.join(base, "inspection")));
fs.mkdirSync(out, { recursive: true });
const pageArg = opt("--page", spec.page);
const isUrl = /^[a-z][a-z0-9+.-]+:\/\//i.test(pageArg);
const url = isUrl ? pageArg : pathToFileURL(path.resolve(base, pageArg)).href;
const widths = spec.widths || [375, 768, 1280], tol = spec.tolerance_px ?? 2, refDir = opt("--reference-dir");

function normColor(v) {  // "#1d1d1b" or "rgb(29, 29, 27)" -> "rgb(29, 29, 27)"
  if (typeof v !== "string") return v;
  const h = v.trim().match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i);
  if (!h) return v.replace(/\s+/g, " ").trim();
  let s = h[1]; if (s.length === 3) s = s.split("").map((c) => c + c).join("");
  const n = parseInt(s, 16); return `rgb(${n >> 16 & 255}, ${n >> 8 & 255}, ${n & 255})`;
}

const browser = await chromium.launch();
const results = [];
for (const w of widths) {
  const page = await browser.newPage({ viewport: { width: w, height: spec.height || 900 }, deviceScaleFactor: 1 });
  await page.goto(url, { waitUntil: "load" });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  const shot = path.join(out, `shot-${w}.png`);
  await page.screenshot({ path: shot, fullPage: true });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  results.push({ width: w, id: "no-horizontal-scroll", ok: overflow <= 0, expected: "scrollWidth <= viewport", measured: `${overflow}px overflow` });
  for (const c of spec.checks || []) {
    if (c.at && !c.at.includes(w)) continue;
    const m = await page.evaluate(({ sel, props }) => {
      const els = [...document.querySelectorAll(sel)];
      const e = els[0];
      if (!e) return { count: 0 };
      const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
      const visible = r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && cs.display !== "none" && +cs.opacity > 0;
      return { count: els.length, box: { x: r.left + scrollX, y: r.top + scrollY, width: r.width, height: r.height }, visible,
               style: Object.fromEntries(props.map((p) => [p, cs.getPropertyValue(p)])), text: e.textContent.trim().replace(/\s+/g, " ") };
    }, { sel: c.selector, props: Object.keys(c.style || {}) });
    const add = (what, ok, expected, measured) => results.push({ width: w, id: `${c.id || c.selector}:${what}`, selector: c.selector, ok, expected, measured });
    if (!m.count) { add("exists", false, "present", "not found"); continue; }
    if (c.count != null) add("count", m.count === c.count, c.count, m.count);
    if (c.visible != null) add("visible", m.visible === c.visible, c.visible, m.visible);
    for (const [k, v] of Object.entries(c.box || {})) add(`box.${k}`, Math.abs(m.box[k] - v) <= tol, `${v}px ±${tol}`, `${Math.round(m.box[k] * 10) / 10}px`);
    for (const [k, v] of Object.entries(c.style || {})) add(`style.${k}`, normColor(m.style[k]) === normColor(v), v, m.style[k]);
    if (c.text != null) add("text", m.text.includes(c.text), `contains "${c.text}"`, m.text.slice(0, 60));
    if (c.min_target_px) add("target-size", m.box.width >= c.min_target_px && m.box.height >= c.min_target_px, `>= ${c.min_target_px}px`, `${Math.round(m.box.width)}x${Math.round(m.box.height)}`);
  }
  const ref = refDir && path.join(path.resolve(refDir), `${w}.png`);
  if (ref && fs.existsSync(ref)) {
    const toData = (f) => "data:image/png;base64," + fs.readFileSync(f).toString("base64");
    const diff = await page.evaluate(async ([a, b]) => {
      const load = (s) => new Promise((ok) => { const i = new Image(); i.onload = () => ok(i); i.src = s; });
      const [ia, ib] = await Promise.all([load(a), load(b)]);
      const W = Math.max(ia.width, ib.width), H = Math.max(ia.height, ib.height);
      const px = (img) => { const c = new OffscreenCanvas(W, H), g = c.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, W, H); g.drawImage(img, 0, 0); return g.getImageData(0, 0, W, H).data; };
      const A = px(ia), B = px(ib); let n = 0;
      for (let i = 0; i < A.length; i += 4) if (Math.max(Math.abs(A[i] - B[i]), Math.abs(A[i + 1] - B[i + 1]), Math.abs(A[i + 2] - B[i + 2])) > 24) n++;
      return { share: n / (W * H), sizeA: [ia.width, ia.height], sizeB: [ib.width, ib.height] };
    }, [toData(shot), toData(ref)]);
    results.push({ width: w, id: "reference-pixels", ok: diff.share <= (spec.max_pixel_diff ?? 0.01), expected: `<= ${((spec.max_pixel_diff ?? 0.01) * 100).toFixed(1)}% pixels differ`, measured: `${(diff.share * 100).toFixed(2)}% (impl ${diff.sizeA.join("x")}, ref ${diff.sizeB.join("x")})` });
  }
  await page.close();
}
await browser.close();

const failed = results.filter((r) => !r.ok);
const report = { tool: "sumitcraft design-to-code-inspection", spec: path.basename(specPath), page: isUrl ? pageArg : path.basename(pageArg),
  when: new Date().toISOString(), widths, tolerance_px: tol, checks: results.length, failed: failed.length, results };
fs.writeFileSync(path.join(out, "report.json"), JSON.stringify(report, null, 2));
const md = [`# Design-to-code inspection: ${report.page}`, "", `${results.length} measurements at ${widths.join(", ")} px; **${failed.length} mismatches**. Tolerance ±${tol}px.`, "",
  "| Width | Check | Expected | Measured | |", "|---:|---|---|---|---|",
  ...results.map((r) => `| ${r.width} | ${r.id} | ${r.expected} | ${r.measured} | ${r.ok ? "ok" : "**MISMATCH**"} |`), "",
  "Screenshots: " + widths.map((w) => `[${w}](shot-${w}.png)`).join(", "), "",
  "Measured values only. Look at the screenshots before deciding which mismatches matter."].join("\n");
fs.writeFileSync(path.join(out, "report.md"), md + "\n");
console.log(`${results.length} checks, ${failed.length} mismatches -> ${path.join(out, "report.md")}`);
for (const f of failed) console.log(`  [${f.width}] ${f.id}: expected ${f.expected}, measured ${f.measured}`);
if (failed.length && !args.includes("--no-fail")) process.exit(1);
