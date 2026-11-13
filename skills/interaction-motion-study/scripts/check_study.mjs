// Check a disclosure-style interaction (a trigger that opens and closes a panel) in a real browser.
//
//   node check_study.mjs <page.html|url> [--trigger "#trigger"] [--panel "#panel"] [--out DIR] [--no-fail]
//
// Observable checks, each with what was measured:
//   semantics      trigger is a <button> (or role=button) and exposes aria-expanded
//   keyboard-open  Tab reaches the trigger; Enter opens; the panel becomes visible; aria-expanded="true"
//   focus-visible the keyboard-focused trigger shows a visible focus indicator (outline or box-shadow)
//   escape         Escape closes the panel and focus returns to the trigger
//   outside-close  a pointer press outside closes it
//   interruption   a second click 40 ms into opening ends closed, with state and attribute agreeing (no stuck half state)
//   timing         transition durations on the panel, as measured (reported, not judged: the spec decides)
//   reduced-motion with prefers-reduced-motion: reduce, the panel has no running animation 30 ms after opening
// Writes DIR/check.json and DIR/check.md, plus open/closed screenshots. Exit 1 on any failed check (unless --no-fail).
import { chromium } from "playwright";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const args = process.argv.slice(2), VALUED = new Set(["--trigger", "--panel", "--out"]), pos = [];
for (let i = 0; i < args.length; i++) { if (VALUED.has(args[i])) { i++; continue; } if (!args[i].startsWith("--")) pos.push(args[i]); }
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
if (!pos[0]) { console.error("usage: node check_study.mjs <page> [--trigger SEL] [--panel SEL] [--out DIR]"); process.exit(2); }
const url = /^[a-z][a-z0-9+.-]+:\/\//i.test(pos[0]) ? pos[0] : pathToFileURL(path.resolve(pos[0])).href;
const T = opt("--trigger", "#trigger"), P = opt("--panel", "#panel"), out = path.resolve(opt("--out", "study-check"));
fs.mkdirSync(out, { recursive: true });
const rows = [], add = (id, ok, measured, needs) => rows.push({ id, ok, measured, needs });

const visible = (page) => page.$eval(P, (el) => { const cs = getComputedStyle(el); return cs.visibility !== "hidden" && cs.display !== "none" && +cs.opacity > 0.5; });
const expanded = (page) => page.$eval(T, (el) => el.getAttribute("aria-expanded"));
const settle = (page) => page.waitForTimeout(600);

const browser = await chromium.launch();
let page = await browser.newPage({ viewport: { width: 800, height: 600 } });
await page.goto(url);
const sem = await page.$eval(T, (el) => ({ tag: el.tagName.toLowerCase(), role: el.getAttribute("role"), exp: el.getAttribute("aria-expanded") }));
add("semantics", (sem.tag === "button" || sem.role === "button") && sem.exp !== null, `<${sem.tag}> role=${sem.role} aria-expanded=${sem.exp}`, "<button> with aria-expanded");

let reached = false;
for (let i = 0; i < 10 && !reached; i++) { await page.keyboard.press("Tab"); reached = await page.$eval(T, (el) => el === document.activeElement); }
const ring = reached ? await page.$eval(T, (el) => { const cs = getComputedStyle(el); return { ow: parseFloat(cs.outlineWidth) || 0, os: cs.outlineStyle, sh: cs.boxShadow }; }) : null;
add("focus-visible", !!ring && ((ring.ow > 0 && ring.os !== "none") || (ring.sh && ring.sh !== "none")), ring ? `outline ${ring.ow}px ${ring.os}, shadow ${ring.sh}` : "trigger never received keyboard focus", "a visible focus indicator");
if (reached) {
  await page.keyboard.press("Enter"); await settle(page);
  const v = await visible(page), e = await expanded(page);
  add("keyboard-open", v && e === "true", `Tab reached trigger; after Enter visible=${v}, aria-expanded=${e}`, "visible and aria-expanded=true");
  await page.screenshot({ path: path.join(out, "open.png") });
  await page.keyboard.press("Escape"); await settle(page);
  const v2 = await visible(page), back = await page.$eval(T, (el) => el === document.activeElement);
  add("escape", !v2 && back, `after Escape visible=${v2}, focus on trigger=${back}`, "closed, focus back on trigger");
} else {
  add("keyboard-open", false, "Tab never reached the trigger in 10 presses", "trigger reachable by keyboard");
  add("escape", false, "not testable without keyboard access", "closed, focus back on trigger");
}
await page.click(T); await settle(page);
const openedByClick = await visible(page);
await page.mouse.click(780, 580); await settle(page);
add("outside-close", openedByClick && !(await visible(page)), `opened by click=${openedByClick}, after outside press visible=${await visible(page)}`, "closes on outside press");
await page.screenshot({ path: path.join(out, "closed.png") });

await page.click(T); await page.waitForTimeout(40); await page.click(T); await settle(page);
const iv = await visible(page), ie = await expanded(page);
add("interruption", !iv && (ie === "false" || ie === null), `after open then close 40 ms apart: visible=${iv}, aria-expanded=${ie}`, "closed, and state agrees with the attribute");

const durs = await page.$eval(P, (el) => getComputedStyle(el).transitionDuration);
add("timing", true, `panel transition-duration: ${durs}`, "reported for the spec to judge");
await page.close();

page = await browser.newPage({ viewport: { width: 800, height: 600 }, reducedMotion: "reduce" });
await page.goto(url);
await page.click(T); await page.waitForTimeout(30);
const running = await page.$eval(P, (el) => el.getAnimations().filter((a) => a.playState === "running").length);
const rv = await visible(page);
add("reduced-motion", running === 0 && rv, `30 ms after opening: running animations=${running}, visible=${rv}`, "no running animation, already visible");
await browser.close();

const failed = rows.filter((r) => !r.ok);
const rep = { tool: "sumitcraft interaction-motion-study check_study.mjs", page: path.basename(pos[0]), when: new Date().toISOString(), trigger: T, panel: P, failed: failed.length, rows };
fs.writeFileSync(path.join(out, "check.json"), JSON.stringify(rep, null, 2));
fs.writeFileSync(path.join(out, "check.md"), [`# Interaction check: ${rep.page}`, "", `${rows.length} checks, **${failed.length} failed**.`, "", "| Check | Measured | Needs | |", "|---|---|---|---|",
  ...rows.map((r) => `| ${r.id} | ${r.measured} | ${r.needs} | ${r.ok ? "ok" : "**FAIL**"} |`), "", "Automated checks cover behaviour, not feel. Watch it at normal speed and with reduced motion before calling it done."].join("\n") + "\n");
for (const r of rows) console.log(`${r.ok ? "ok  " : "FAIL"} ${r.id}: ${r.measured}`);
if (failed.length && !args.includes("--no-fail")) process.exit(1);
