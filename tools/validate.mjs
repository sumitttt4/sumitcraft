#!/usr/bin/env node
// Static checks for the whole collection. Offline, read-only except for the report it writes.
//
//   node tools/validate.mjs [--json evidence/static/validate.json]
//
// 1 discover   every catalog skill has skills/<name>/SKILL.md and vice versa; all 24 upstream names present
// 2 metadata   frontmatter name matches the folder; description present and <= 1024 chars; SKILL.md links contract.md
// 3 contract   contract.md has every required section
// 4 links      relative links in every Markdown file resolve
// 5 parse      every .py compiles (python -m py_compile); every .mjs/.js/.cjs passes node --check
// 6 license    LICENSE keeps the upstream MIT notice; THIRD_PARTY_NOTICES.md names the upstream commit
// 7 secrets    no credential-looking strings outside the documented fake fixtures
// 8 platform   no unguarded POSIX/macOS assumptions in scripts (allowlist below, each with a reason)
// Passing these does not mean a skill works. Functional status lives in docs/VALIDATION_MATRIX.md.
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { skills, UPSTREAM } from "../catalog/skills.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const rel = (p) => path.relative(ROOT, p).split(path.sep).join("/");
const results = [], add = (group, ok, what) => results.push({ group, ok, what });
const SKIP_DIRS = new Set([".git", "node_modules", ".venv", "__pycache__", "evidence"]);
function walk(d, out = []) { for (const e of fs.readdirSync(d, { withFileTypes: true })) { if (SKIP_DIRS.has(e.name)) continue; const p = path.join(d, e.name); e.isDirectory() ? walk(p, out) : out.push(p); } return out; }
const files = walk(ROOT);

const UPSTREAM_24 = ["perspective-illusion", "code-loop", "reverse-engineer-video", "scripted-screencast", "repo-timelapse", "rough-cut", "clean-audio", "vox-explainer",
  "codebase-map", "bisect-anything", "flaky-test-killer", "benchmark-honestly", "api-design-review", "security-threat-model", "dx-audit",
  "paper-to-runnable", "system-design-from-scratch", "from-scratch", "teach-back", "image-gen", "brand-kit", "skill-router", "next-step", "video-script"];
const CONTRACT_SECTIONS = ["Purpose", "Use it for", "Not for", "Accepted inputs", "Deliverables", "Prerequisites", "Local and network behaviour", "Cost-sensitive operations",
  "Workflow", "Human decisions", "Quality checks", "Common failures", "Limitations", "Reproducible example", "Validation status"];

// 1 + 2 + 3
const dirs = fs.readdirSync(path.join(ROOT, "skills")).filter((d) => fs.statSync(path.join(ROOT, "skills", d)).isDirectory());
for (const n of UPSTREAM_24) add("discover", dirs.includes(n) && skills.some((s) => s.name === n && s.origin === "upstream"), `upstream skill ${n} present`);
for (const s of skills) add("discover", dirs.includes(s.name), `catalog skill ${s.name} has a folder`);
for (const d of dirs) add("discover", skills.some((s) => s.name === d), `folder skills/${d} is in the catalog`);
for (const d of dirs) {
  const f = path.join(ROOT, "skills", d, "SKILL.md");
  if (!fs.existsSync(f)) { add("metadata", false, `skills/${d}/SKILL.md missing`); continue; }
  const t = fs.readFileSync(f, "utf8"), fm = t.match(/^---\n([\s\S]*?)\n---/);
  const name = fm && fm[1].match(/^name:\s*(.+)$/m)?.[1].trim(), desc = fm && fm[1].match(/^description:\s*(.+)$/m)?.[1].trim();
  add("metadata", name === d, `skills/${d}: frontmatter name "${name}"`);
  add("metadata", !!desc && desc.length <= 1024, `skills/${d}: description ${desc ? desc.length : 0} chars (<= 1024)`);
  add("metadata", t.includes("contract.md"), `skills/${d}: SKILL.md links contract.md`);
  const c = path.join(ROOT, "skills", d, "contract.md");
  if (!fs.existsSync(c)) { add("contract", false, `skills/${d}/contract.md missing`); continue; }
  const ct = fs.readFileSync(c, "utf8"), miss = CONTRACT_SECTIONS.filter((h) => !new RegExp(`^## ${h}\\b`, "m").test(ct));
  add("contract", !miss.length, `skills/${d}/contract.md sections${miss.length ? ": missing " + miss.join(", ") : " complete"}`);
}

// 4 links
for (const f of files.filter((x) => x.endsWith(".md"))) {
  const t = fs.readFileSync(f, "utf8").replace(/```[\s\S]*?```/g, "").replace(/`[^`\n]*`/g, "");
  for (const m of t.matchAll(/\]\(([^)\s]+)\)/g)) {
    const link = m[1].split("#")[0];
    if (!link || /^[a-z][a-z0-9+.-]*:/i.test(m[1]) || m[1].startsWith("#")) continue;
    add("links", fs.existsSync(path.resolve(path.dirname(f), decodeURIComponent(link))), `${rel(f)} -> ${m[1]}`);
  }
}

// 5 parse
const py = process.platform === "win32" ? ["py", ["-3"]] : ["python3", []];
const pyFiles = files.filter((f) => f.endsWith(".py"));
const pyc = spawnSync(py[0], [...py[1], "-c", "import sys,py_compile\nbad=[]\nfor f in sys.argv[1:]:\n  try: py_compile.compile(f, doraise=True, cfile=None if False else f + '.validate-pyc')\n  except Exception as e: bad.append(f + ': ' + str(e).splitlines()[-1])\n  else:\n    import os; os.remove(f + '.validate-pyc')\nprint('\\n'.join(bad))", ...pyFiles], { encoding: "utf8" });
const badPy = new Set((pyc.stdout || "").split("\n").filter(Boolean).map((l) => l.split(": ")[0]));
for (const f of pyFiles) add("parse", pyc.status === 0 && !badPy.has(f), `${rel(f)} compiles`);
for (const f of files.filter((x) => /\.(mjs|cjs|js)$/.test(x))) {
  const r = spawnSync(process.execPath, ["--check", f], { encoding: "utf8" });
  add("parse", r.status === 0, `${rel(f)} parses${r.status ? ": " + (r.stderr || "").split("\n").find((l) => /Error/.test(l)) : ""}`);
}

// 6 license
const lic = fs.readFileSync(path.join(ROOT, "LICENSE"), "utf8");
add("license", lic.includes("Copyright (c) 2026 Simran Sachdeva") && lic.includes("Permission is hereby granted"), "LICENSE keeps the upstream MIT notice");
const tpn = path.join(ROOT, "THIRD_PARTY_NOTICES.md");
add("license", fs.existsSync(tpn) && fs.readFileSync(tpn, "utf8").includes(UPSTREAM.commit), "THIRD_PARTY_NOTICES.md names the upstream commit");
add("license", fs.existsSync(path.join(ROOT, "skills/repo-timelapse/engine/fonts/OFL.txt")) && fs.existsSync(path.join(ROOT, "skills/vox-explainer/engine/fonts/OFL.txt")), "OFL text ships next to the bundled Geist fonts");

// 7 secrets (documented fake fixtures are allowed and listed)
const SECRET = [/AKIA[0-9A-Z]{16}/, /gh[pousr]_[A-Za-z0-9]{30,}/, /\bsk-(?:live|proj|ant)?[-_]?[A-Za-z0-9]{24,}/, /xox[baprs]-[A-Za-z0-9-]{10,}/, /-----BEGIN [A-Z ]*PRIVATE KEY-----/, /AIza[0-9A-Za-z_-]{35}/];
const FAKE_OK = ["skills/security-threat-model/", "skills/work-to-explanation/scripts/preflight.py", "tools/validate.mjs", "skills/dx-audit/scripts/friction.py", "tests/"];
for (const f of files.filter((x) => /\.(py|mjs|js|cjs|json|md|html|txt|yaml|yml|sh|ps1|env)$/.test(x))) {
  const r = rel(f), t = fs.readFileSync(f, "utf8");
  const hit = SECRET.find((re) => re.test(t));
  if (hit && !FAKE_OK.some((a) => r.startsWith(a))) add("secrets", false, `${r} matches ${hit}`);
}
add("secrets", true, `scanned ${files.length} files (documented fake fixtures: ${FAKE_OK.join(", ")})`);

// 8 platform assumptions in scripts
const LINT = [
  [/--use-angle=metal/, "hard-coded Metal backend", ["skills/code-loop/scripts/gpu_backend.mjs", "skills/perspective-illusion/templates/gpu_backend.mjs"]],
  [/["']file:\/\/["']\s*\+/, "string-built file:// URL (use pathToFileURL)", []],
  [/\.venv\/bin\/python/, ".venv/bin/python without a Windows branch", ["skills/vox-explainer/scripts/build.py", "tools/doctor.mjs", "skills/rough-cut/setup.py", "skills/reverse-engineer-video/setup.py", "skills/paper-to-runnable/setup.py", "skills/codebase-map/scripts/trace_py.py"]],
  [/os\.killpg\(/, "os.killpg without a Windows path", ["skills/bisect-anything/scripts/_common.py", "skills/bisect-anything/scripts/oracles/serve_oracle.py"]],
  [/preexec_fn=(?!limits if os\.name)/, "preexec_fn (POSIX only)", []],
  [/^import resource\b/m, "top-level import of the POSIX resource module", []],
  [/\bopen -e\b|subprocess\.\w+\(\[?["']open["']/, "macOS `open`", []],
  [/~\/Movies|Path\.home\(\) \/ "\.config\/simcraft|\.local\/share\/simcraft/, "macOS or upstream-specific home path", []],
];
for (const f of files.filter((x) => /\.(py|mjs|js|cjs|sh)$/.test(x) && rel(x).startsWith("skills/"))) {
  const r = rel(f), t = fs.readFileSync(f, "utf8");
  for (const [re, why, allow] of LINT) if (re.test(t) && !allow.includes(r)) add("platform", false, `${r}: ${why}`);
}
for (const f of files.filter((x) => x.endsWith("SKILL.md"))) {
  const t = fs.readFileSync(f, "utf8");
  if (/~\/simcraft|~\/Movies|open -e|\bsh setup\.sh\b/.test(t)) add("platform", false, `${rel(f)}: Unix-only or upstream-specific instruction`);
}
add("platform", true, "platform lint ran over skills/*/scripts, templates and SKILL.md files");

// report
const failed = results.filter((r) => !r.ok);
const groups = [...new Set(results.map((r) => r.group))];
for (const g of groups) { const rs = results.filter((r) => r.group === g); console.log(`${rs.every((r) => r.ok) ? "PASS" : "FAIL"}  ${g.padEnd(9)} ${rs.filter((r) => r.ok).length}/${rs.length}`); }
for (const f of failed) console.log(`  - [${f.group}] ${f.what}`);
const jsonOut = process.argv.includes("--json") ? process.argv[process.argv.indexOf("--json") + 1] : null;
if (jsonOut) { fs.mkdirSync(path.dirname(path.resolve(jsonOut)), { recursive: true }); fs.writeFileSync(jsonOut, JSON.stringify({ tool: "sumitcraft validate", when: new Date().toISOString(), platform: process.platform, total: results.length, failed: failed.length, groups: Object.fromEntries(groups.map((g) => [g, { ok: results.filter((r) => r.group === g && r.ok).length, total: results.filter((r) => r.group === g).length }])), failures: failed }, null, 2)); }
console.log(`${results.length} checks, ${failed.length} failed. Static checks say nothing about whether a skill works; see docs/VALIDATION_MATRIX.md.`);
process.exit(failed.length ? 1 : 0);
