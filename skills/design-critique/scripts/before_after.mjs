// Screenshot two versions of a page at the same widths and measure what changed.
//
//   node before_after.mjs <before.html|url> <after.html|url> [--widths 375,1280] [--out DIR] [--height 900]
//
// For each width writes DIR/<width>-before.png, <width>-after.png, <width>-diff.png (changed pixels in magenta over a
// faded "after") and DIR/before_after.json + .md with: share of pixels changed, the bounding box of the change, and a
// 4x4 grid of where the changes are. Use it to confirm a refinement changed what it meant to change, and nothing else.
// The comparison runs inside Chromium (canvas), so no image library is needed.
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2), VALUED = new Set(["--widths", "--out", "--height"]), pos = [];
for (let i = 0; i < args.length; i++) { if (VALUED.has(args[i])) { i++; continue; } if (!args[i].startsWith("--")) pos.push(args[i]); }
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
if (pos.length < 2) { console.error("usage: node before_after.mjs <before> <after> [--widths 375,1280] [--out DIR]"); process.exit(2); }
const toUrl = (p) => (/^[a-z][a-z0-9+.-]+:\/\//i.test(p) ? p : pathToFileURL(path.resolve(p)).href);
const widths = opt("--widths", "375,1280").split(",").map(Number), H = +opt("--height", 900);
const out = path.resolve(opt("--out", "before_after")); fs.mkdirSync(out, { recursive: true });

const browser = await chromium.launch();
const rows = [];
for (const w of widths) {
  const shots = {};
  for (const [tag, src] of [["before", pos[0]], ["after", pos[1]]]) {
    const p = await browser.newPage({ viewport: { width: w, height: H }, deviceScaleFactor: 1 });
    await p.goto(toUrl(src), { waitUntil: "load" }); await p.evaluate(() => document.fonts && document.fonts.ready);
    shots[tag] = path.join(out, `${w}-${tag}.png`); await p.screenshot({ path: shots[tag], fullPage: true }); await p.close();
  }
  const p = await browser.newPage();
  const data = (f) => "data:image/png;base64," + fs.readFileSync(f).toString("base64");
  const r = await p.evaluate(async ([a, b]) => {
    const load = (s) => new Promise((ok) => { const i = new Image(); i.onload = () => ok(i); i.src = s; });
    const [ia, ib] = await Promise.all([load(a), load(b)]);
    const W = Math.max(ia.width, ib.width), Hh = Math.max(ia.height, ib.height);
    const get = (img) => { const c = new OffscreenCanvas(W, Hh), g = c.getContext("2d"); g.fillStyle = "#fff"; g.fillRect(0, 0, W, Hh); g.drawImage(img, 0, 0); return g.getImageData(0, 0, W, Hh); };
    const A = get(ia).data, Bimg = get(ib), B = Bimg.data, grid = Array(16).fill(0);
    let n = 0, x0 = W, y0 = Hh, x1 = -1, y1 = -1;
    const outImg = new ImageData(W, Hh);
    for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++) {
      const i = (y * W + x) * 4, d = Math.max(Math.abs(A[i] - B[i]), Math.abs(A[i + 1] - B[i + 1]), Math.abs(A[i + 2] - B[i + 2]));
      if (d > 24) { n++; grid[Math.min(3, (y * 4 / Hh) | 0) * 4 + Math.min(3, (x * 4 / W) | 0)]++; x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y);
        outImg.data.set([255, 0, 200, 255], i); }
      else outImg.data.set([255 - (255 - B[i]) * 0.35, 255 - (255 - B[i + 1]) * 0.35, 255 - (255 - B[i + 2]) * 0.35, 255], i);
    }
    const c = new OffscreenCanvas(W, Hh); c.getContext("2d").putImageData(outImg, 0, 0);
    const blob = await c.convertToBlob({ type: "image/png" });
    const buf = new Uint8Array(await blob.arrayBuffer()); let s = ""; for (let i = 0; i < buf.length; i += 32768) s += String.fromCharCode(...buf.subarray(i, i + 32768));
    const cell = (W * Hh) / 16;
    return { size: [W, Hh], beforeSize: [ia.width, ia.height], afterSize: [ib.width, ib.height], changed: n / (W * Hh),
             bbox: x1 < 0 ? null : [x0, y0, x1 - x0 + 1, y1 - y0 + 1], grid: grid.map((g) => +(g / cell).toFixed(3)), png: btoa(s) };
  }, [data(shots.before), data(shots.after)]);
  fs.writeFileSync(path.join(out, `${w}-diff.png`), Buffer.from(r.png, "base64")); delete r.png;
  rows.push({ width: w, ...r }); await p.close();
}
await browser.close();
const rep = { tool: "sumitcraft design-critique before_after.mjs", before: path.basename(pos[0]), after: path.basename(pos[1]), when: new Date().toISOString(), threshold: "channel difference > 24/255", widths: rows };
fs.writeFileSync(path.join(out, "before_after.json"), JSON.stringify(rep, null, 2));
const md = [`# Before / after: ${rep.before} -> ${rep.after}`, "", "| Width | Pixels changed | Change box (x, y, w, h) | Page height before -> after |", "|---:|---:|---|---|",
  ...rows.map((r) => `| ${r.width} | ${(r.changed * 100).toFixed(2)}% | ${r.bbox ? r.bbox.join(", ") : "none"} | ${r.beforeSize[1]} -> ${r.afterSize[1]} |`), "",
  "Where the change is (share of each quarter-by-quarter cell that changed, top row first):", "",
  ...rows.map((r) => `- ${r.width}px: ` + [0, 1, 2, 3].map((y) => r.grid.slice(y * 4, y * 4 + 4).map((v) => (v * 100).toFixed(0).padStart(3)).join(" ")).join(" | ")), "",
  "Diff images: " + rows.map((r) => `[${r.width}](${r.width}-diff.png)`).join(", "), "", "A changed-pixel share is not a quality score. Look at the images."].join("\n");
fs.writeFileSync(path.join(out, "before_after.md"), md + "\n");
for (const r of rows) console.log(`${r.width}px: ${(r.changed * 100).toFixed(2)}% pixels changed, box ${r.bbox ? r.bbox.join(",") : "none"}`);
console.log("report:", path.join(out, "before_after.md"));
