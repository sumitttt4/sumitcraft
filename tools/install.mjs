#!/usr/bin/env node
// Copy SumitCraft skills into a Claude Code skills folder, selectively, without ever overwriting someone else's skill.
//
//   node tools/install.mjs list
//   node tools/install.mjs status   [--scope user|project | --target DIR]
//   node tools/install.mjs install  <name ...> | --all | --category <video|engineering|learning|design|planning|docs>  [--scope user|project | --target DIR] [--dry-run] [--yes] [--update]
//   node tools/install.mjs uninstall <name ...> | --all                   [--scope user|project | --target DIR] [--dry-run] [--yes]
//   (Windows: powershell -ExecutionPolicy Bypass -File tools\install.ps1 <same arguments>)
//
// Scopes: project = ./.claude/skills in the current folder (default); user = <home>/.claude/skills (the global folder:
// requires --yes, because it affects every project). --target writes anywhere else (e.g. a test folder).
// Copies, never symlinks (works on Windows without developer mode). Skips .venv, node_modules, __pycache__.
// Every installed folder gets .sumitcraft-install.json. A folder without that marker is someone else's skill: it is
// never overwritten or removed. --update replaces only folders that carry the marker.
// Tip: installing SumitCraft as a Claude Code plugin (see README) namespaces skills as sumitcraft:<name> instead.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { skills } from "../catalog/skills.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SRC = path.join(ROOT, "skills");
const MARK = ".sumitcraft-install.json";
const SKIP = new Set([".venv", "node_modules", "__pycache__", ".DS_Store", MARK]);
// Skills that call a sibling skill's scripts at run time.
const SIBLINGS = { "clean-audio": ["rough-cut"], "vox-explainer": ["rough-cut"], "perspective-illusion": ["vox-explainer"], "brand-kit": ["vox-explainer"], "design-critique": ["design-system-build"], "design-system-build": ["design-critique"] };

const [cmd, ...rest] = process.argv.slice(2);
const flag = (f) => rest.includes(f);
const val = (f) => (rest.includes(f) ? rest[rest.indexOf(f) + 1] : undefined);
const names = rest.filter((a, i) => !a.startsWith("--") && !["--scope", "--target", "--category"].includes(rest[i - 1]));
const scope = val("--scope") || "project";
const target = path.resolve(val("--target") || (scope === "user" ? path.join(os.homedir(), ".claude", "skills") : path.join(process.cwd(), ".claude", "skills")));
const isGlobal = !val("--target") && scope === "user";
const known = new Map(skills.map((s) => [s.name, s]));
const commit = (() => { const r = spawnSync("git", ["-C", ROOT, "rev-parse", "--short", "HEAD"], { encoding: "utf8" }); return r.status === 0 ? r.stdout.trim() : "unknown"; })();
const version = JSON.parse(fs.readFileSync(path.join(ROOT, "package.json"), "utf8")).version;

function select() {
  let list = flag("--all") ? [...known.keys()] : val("--category") ? skills.filter((s) => s.category === val("--category")).map((s) => s.name) : names;
  const bad = list.filter((n) => !known.has(n));
  if (bad.length) { console.error(`unknown skill(s): ${bad.join(", ")}. Run: node tools/install.mjs list`); process.exit(2); }
  if (!list.length) { console.error("name at least one skill, or --all, or --category <video|engineering|learning|design|planning|docs>"); process.exit(2); }
  return list;
}
const marker = (dir) => { try { return JSON.parse(fs.readFileSync(path.join(dir, MARK), "utf8")); } catch { return null; } };
function copyDir(a, b) {
  fs.mkdirSync(b, { recursive: true });
  for (const e of fs.readdirSync(a, { withFileTypes: true })) {
    if (SKIP.has(e.name)) continue;
    const s = path.join(a, e.name), d = path.join(b, e.name);
    if (e.isDirectory()) copyDir(s, d); else if (e.isFile()) fs.copyFileSync(s, d);
  }
}
function guardGlobal(action) {
  if (isGlobal && !flag("--yes") && !flag("--dry-run")) {
    console.error(`This would ${action} in your global Claude skills folder:\n  ${target}\nwhich affects every project. Re-run with --yes to confirm, or --dry-run to preview, or use --scope project.`);
    process.exit(3);
  }
}

if (cmd === "list") {
  for (const cat of ["video", "engineering", "learning", "design", "planning", "docs"]) {
    console.log(`\n${cat}`);
    for (const s of skills.filter((x) => x.category === cat)) console.log(`  ${s.name.padEnd(32)} ${s.origin === "upstream" ? "foundation" : s.origin === "vendor" ? "vendor    " : "addition  "}  ${s.kind}`);
  }
  console.log(`\n${skills.length} skills. Install some with: node tools/install.mjs install <name ...> --scope project`);
} else if (cmd === "status") {
  console.log(`target: ${target}${isGlobal ? " (global)" : ""}`);
  for (const s of skills) {
    const d = path.join(target, s.name), m = fs.existsSync(d) ? marker(d) : undefined;
    console.log(`  ${s.name.padEnd(28)} ${m === undefined ? "not installed" : m ? `installed (sumitcraft ${m.version} @ ${m.commit}, ${m.installed_at.slice(0, 10)})` : "a different skill with this name is there (left alone)"}`);
  }
} else if (cmd === "install") {
  const list = select(); guardGlobal("copy skills");
  const plan = [];
  for (const n of list) {
    const d = path.join(target, n);
    if (!fs.existsSync(d)) plan.push([n, "install"]);
    else if (!marker(d)) plan.push([n, "conflict: an existing skill with this name has no SumitCraft marker; left untouched"]);
    else plan.push([n, flag("--update") ? "update" : "already installed (use --update to replace it)"]);
  }
  const missingSib = [...new Set(list.flatMap((n) => (SIBLINGS[n] || []).filter((s) => !list.includes(s) && !fs.existsSync(path.join(target, s)))))];
  console.log(`target: ${target}${isGlobal ? " (global)" : ""}${flag("--dry-run") ? "  [dry run: nothing will be written]" : ""}`);
  for (const [n, what] of plan) console.log(`  ${n.padEnd(28)} ${what}`);
  if (missingSib.length) console.log(`note: some selected skills call scripts in ${missingSib.join(", ")}; install those too for full function.`);
  if (flag("--dry-run")) process.exit(0);
  let done = 0;
  for (const [n, what] of plan) {
    if (what !== "install" && what !== "update") continue;
    const d = path.join(target, n);
    if (what === "update") fs.rmSync(d, { recursive: true, force: true });
    copyDir(path.join(SRC, n), d);
    fs.writeFileSync(path.join(d, MARK), JSON.stringify({ name: n, version, commit, installed_at: new Date().toISOString(), source: "sumitcraft" }, null, 2));
    done++;
  }
  console.log(`${done} installed or updated; ${plan.filter(([, w]) => w.startsWith("conflict")).length} conflicts left alone.`);
  if (plan.some(([, w]) => w.startsWith("conflict"))) process.exitCode = 4;
} else if (cmd === "uninstall") {
  const list = select(); guardGlobal("remove skills");
  for (const n of list) {
    const d = path.join(target, n);
    if (!fs.existsSync(d)) { console.log(`  ${n.padEnd(28)} not installed`); continue; }
    if (!marker(d)) { console.log(`  ${n.padEnd(28)} not a SumitCraft install (no marker): left untouched`); continue; }
    if (flag("--dry-run")) { console.log(`  ${n.padEnd(28)} would remove`); continue; }
    fs.rmSync(d, { recursive: true, force: true }); console.log(`  ${n.padEnd(28)} removed`);
  }
} else {
  console.log(fs.readFileSync(fileURLToPath(import.meta.url), "utf8").split("\n").filter((l) => l.startsWith("//")).map((l) => l.slice(3)).join("\n"));
  process.exit(cmd ? 2 : 0);
}
