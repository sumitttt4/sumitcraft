#!/usr/bin/env node
// SumitCraft doctor: what is installed, what is missing, which skills are ready, and the exact next setup step.
//
//   node tools/doctor.mjs [--json] [--no-browser] [--out DIR]
//   (Windows: powershell -ExecutionPolicy Bypass -File tools\doctor.ps1)
//
// Read-only. It runs version commands and, unless --no-browser, launches Playwright's Chromium once to read the WebGL
// renderer. It writes and deletes one temporary file in the output folder to prove it is writable. It never installs
// anything, never changes PATH or settings, and never prints environment values: API keys are reported as set/not set.
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import { skills } from "../catalog/skills.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2), JSON_OUT = args.includes("--json");
const outDir = path.resolve(args.includes("--out") ? args[args.indexOf("--out") + 1] : process.cwd());
const WIN = process.platform === "win32", MAC = process.platform === "darwin";

function run(cmd, a = [], opts = {}) {
  const r = spawnSync(cmd, a, { encoding: "utf8", timeout: 20000, windowsHide: true, shell: false, ...opts });
  return r.error ? null : { code: r.status, out: `${r.stdout || ""}${r.stderr || ""}`.trim() };
}
const firstLine = (s) => (s || "").split(/\r?\n/)[0].trim();
const ver = (s) => (s || "").match(/(\d+)\.(\d+)(?:\.(\d+))?/);
const atLeast = (m, a, b, c = 0) => !!m && (+m[1] > a || (+m[1] === a && (+m[2] > b || (+m[2] === b && +(m[3] || 0) >= c))));

// ---------- OS ----------
function osInfo() {
  const info = { platform: process.platform, arch: process.arch, release: os.release(), name: WIN || MAC ? os.version() : `${os.type()} ${os.release()}` };
  if (WIN) {
    const build = +(os.release().split(".")[2] || 0);
    info.windows = { build, family: build >= 22000 ? "Windows 11" : build >= 10240 ? "Windows 10" : "older than Windows 10 (unsupported)",
      supported: build >= 17763, note: "SumitCraft documents Windows 10 1809 (build 17763) and later as the target; native Windows runs have not been recorded yet (see docs/VALIDATION_MATRIX.md)." };
  }
  return info;
}

// ---------- tools ----------
const checks = {};
const add = (id, ok, detail, extra = {}) => { checks[id] = { ok, detail, ...extra }; };

add("node", atLeast(ver(process.version), 18, 19), process.version, { needs: ">= 18.19" });

const pyCandidates = WIN ? [["py", ["-3"]], ["python", []]] : [["python3", []], ["python", []]];
let PY = null;
for (const [c, pre] of pyCandidates) {
  const r = run(c, [...pre, "--version"]);
  if (r && r.code === 0 && /Python 3/.test(r.out)) { PY = [c, pre]; add("python", atLeast(ver(r.out), 3, 9), `${firstLine(r.out)} (${[c, ...pre].join(" ")})`, { needs: ">= 3.9", command: [c, ...pre].join(" ") }); break; }
}
if (!PY) add("python", false, "not found", { needs: ">= 3.9" });

const pyMod = (mod, label = mod, py = PY) => {
  if (!py) return add(label, false, "python missing");
  const r = run(py[0], [...py[1], "-c", `import ${mod} as m; print(getattr(m, "__version__", "ok"))`]);
  add(label, !!r && r.code === 0, r && r.code === 0 ? firstLine(r.out) : "not importable");
};
pyMod("numpy"); pyMod("matplotlib"); pyMod("pypdf"); pyMod("yaml", "pyyaml"); pyMod("cv2", "opencv");
// Whisper lives in rough-cut's own venv by design; check there first, then the main Python.
const venvPy = path.join(ROOT, "skills", "rough-cut", ".venv", WIN ? "Scripts/python.exe" : "bin/python");
const hasVenv = fs.existsSync(venvPy);
{
  const py = hasVenv ? [venvPy, []] : PY;
  const r = py && run(py[0], [...py[1], "-c", "import importlib.util as u; print('faster-whisper' if u.find_spec('faster_whisper') else 'mlx-whisper' if u.find_spec('mlx_whisper') else '')"]);
  const found = r && r.code === 0 && r.out.trim();
  add("whisper", !!found, found ? `${r.out.trim()} in ${hasVenv ? "rough-cut/.venv" : "main python"} (weights download on first use)` : `not installed (${hasVenv ? "rough-cut/.venv exists without it" : "no rough-cut/.venv yet"})`);
}

const g = run("git", ["--version"]); add("git", !!g && g.code === 0, g ? firstLine(g.out) : "not found");
const FF = process.env.FFMPEG || "ffmpeg";
const ff = run(FF, ["-version"]); add("ffmpeg", !!ff && ff.code === 0, ff ? firstLine(ff.out) : `not found (${process.env.FFMPEG ? "FFMPEG is set but does not run" : "not on PATH; set FFMPEG to its full path"})`);
const fpPath = process.env.FFMPEG ? path.join(path.dirname(process.env.FFMPEG), WIN ? "ffprobe.exe" : "ffprobe") : "ffprobe";
const fp = run(fpPath, ["-version"]); add("ffprobe", !!fp && fp.code === 0, fp ? firstLine(fp.out) : "not found (usually installed with ffmpeg)");
const ts = run("tesseract", ["--version"]); add("tesseract", !!ts && ts.code === 0, ts ? firstLine(ts.out) : "not found (optional: on-screen text in reverse-engineer-video)");

// ---------- Playwright and the browser binary (separate things) ----------
const req = createRequire(path.join(ROOT, "package.json"));
let pw = null;
try { pw = req("playwright/package.json").version; add("playwright", true, `playwright ${pw} (package)`); } catch { add("playwright", false, "package not installed: run `npm install` in the SumitCraft folder"); }
let gl = null;
if (pw) {
  try {
    const mod = await import(pathToFileURL(req.resolve("playwright")).href);
    const chromium = mod.chromium || mod.default?.chromium;
    const exe = chromium.executablePath();
    const present = fs.existsSync(exe);
    add("chromium", present, present ? `browser binary present (${path.basename(path.dirname(exe))})` : "browser binary missing: the npm package does not include it (see next step)", { bytesNote: "Chromium download is roughly 150-200 MB" });
    if (present && !args.includes("--no-browser")) {
      const { requestedBackend } = await import(pathToFileURL(path.join(ROOT, "skills/code-loop/scripts/gpu_backend.mjs")).href);
      const backend = requestedBackend([]);
      const flags = backend === "default" ? [] : [`--use-angle=${backend}`, ...(backend === "swiftshader" ? [] : ["--enable-gpu", "--ignore-gpu-blocklist"])];
      const b = await chromium.launch({ args: flags });
      const p = await b.newPage();
      const info = await p.evaluate(() => { const c = document.createElement("canvas"), x = c.getContext("webgl2") || c.getContext("webgl"); if (!x) return null; const e = x.getExtension("WEBGL_debug_renderer_info"); return { renderer: e ? x.getParameter(e.UNMASKED_RENDERER_WEBGL) : x.getParameter(x.RENDERER) }; });
      gl = { requested: backend, chromium: b.version(), webgl: info, software: info ? /swiftshader|llvmpipe|software/i.test(info.renderer) : null };
      await b.close();
      add("webgl", !!info, info ? `${info.renderer}${gl.software ? " (software rendering: works, slowly; no GPU acceleration)" : ""}; backend requested: ${backend}` : `WebGL unavailable with backend ${backend}`);
    }
  } catch (e) { add("chromium", false, `could not check: ${e.message.split("\n")[0]}`); }
}
let three = false; try { createRequire(path.join(process.cwd(), "x.js")).resolve("three"); three = true; } catch {}
add("three", three, three ? "three resolves in the current folder" : "not in the current folder (installed per work folder by code-loop and perspective-illusion)");

// ---------- keys (presence only) ----------
const cfgDir = process.env.SUMITCRAFT_CONFIG || (WIN ? path.join(process.env.APPDATA || os.homedir(), "SumitCraft") : path.join(process.env.XDG_CONFIG_HOME || path.join(os.homedir(), ".config"), "sumitcraft"));
const keyFile = path.join(cfgDir, "keys.env");
const keyIn = (names) => names.some((n) => !!process.env[n]) || (fs.existsSync(keyFile) && names.some((n) => new RegExp(`^\\s*${n}\\s*=\\s*\\S`, "m").test(fs.readFileSync(keyFile, "utf8"))));
add("gemini-key", keyIn(["GEMINI_API_KEY", "SIMCRAFT_GEMINI_KEY", "GOOGLE_API_KEY"]), "presence only, value never read into output");
add("openai-key", keyIn(["OPENAI_API_KEY", "SIMCRAFT_OPENAI_KEY"]), "presence only, value never read into output");

// ---------- writable output ----------
let writable = false;
try { fs.mkdirSync(outDir, { recursive: true }); const f = path.join(outDir, `.sumitcraft-doctor-${process.pid}.tmp`); fs.writeFileSync(f, "ok"); fs.rmSync(f); writable = true; } catch {}
add("output-writable", writable, writable ? "can write to the output folder" : "cannot write to the output folder", { folder: path.basename(outDir) || outDir });

// ---------- per-skill readiness ----------
const readiness = skills.map((s) => {
  const missing = s.needs.required.filter((r) => !checks[r]?.ok);
  const optMissing = s.needs.optional.filter((r) => !checks[r]?.ok);
  return { name: s.name, category: s.category, origin: s.origin, ready: missing.length === 0, missing, optionalMissing: optMissing };
});

// ---------- next steps (printed, never run) ----------
const HOW = {
  node: WIN ? "winget install OpenJS.NodeJS.LTS" : MAC ? "brew install node" : "install Node 20+ LTS from your distribution or nodejs.org",
  python: WIN ? "winget install Python.Python.3.12" : MAC ? "brew install python@3.12" : "sudo apt install python3 python3-venv  (or your distribution's equivalent)",
  git: WIN ? "winget install Git.Git" : MAC ? "xcode-select --install  (or brew install git)" : "sudo apt install git",
  ffmpeg: WIN ? "winget install Gyan.FFmpeg   (then open a new terminal, or set FFMPEG to ffmpeg.exe's full path)" : MAC ? "brew install ffmpeg" : "sudo apt install ffmpeg",
  playwright: "npm install   (in the SumitCraft folder; installs the playwright package only)",
  chromium: "npx playwright install chromium   (downloads the browser binary, roughly 150-200 MB)",
  numpy: `${checks.python?.command || "python"} -m pip install --user numpy   (or use a skill's setup.py, which installs into that skill's own .venv)`,
  whisper: `${checks.python?.command || "python"} skills/rough-cut/setup.py   (shows the plan; add --yes to create the venv; weights download later, about 0.5-1.5 GB)`,
};
const order = ["node", "python", "git", "ffmpeg", "playwright", "chromium", "numpy", "whisper"];
const blocking = order.filter((id) => checks[id] && !checks[id].ok && readiness.some((r) => r.missing.includes(id)));
const report = { tool: "sumitcraft doctor", when: new Date().toISOString(), os: osInfo(), checks, gl, readiness,
  summary: { ready: readiness.filter((r) => r.ready).length, total: readiness.length },
  next: blocking.length ? { missing: blocking[0], command: HOW[blocking[0]], unlocks: readiness.filter((r) => r.missing.includes(blocking[0])).map((r) => r.name) } : null };

if (JSON_OUT) { console.log(JSON.stringify(report, null, 2)); process.exit(0); }
const o = report.os;
console.log(`SumitCraft doctor  (${o.name}, ${o.platform} ${o.arch}, release ${o.release}${o.windows ? `, ${o.windows.family} build ${o.windows.build}` : ""})`);
if (o.windows && !o.windows.supported) console.log("  ! this Windows build is older than the documented minimum (10 1809)");
console.log("\nPrerequisites");
for (const [id, c] of Object.entries(checks)) console.log(`  ${c.ok ? "ok     " : "missing"}  ${id.padEnd(15)} ${c.detail}`);
console.log(`\nSkills ready: ${report.summary.ready}/${report.summary.total}`);
for (const r of readiness) console.log(`  ${r.ready ? "ready  " : "blocked"}  ${r.name.padEnd(28)} ${r.ready ? (r.optionalMissing.length ? `optional missing: ${r.optionalMissing.join(", ")}` : "") : `needs: ${r.missing.join(", ")}`}`);
console.log("\nNext step" + (report.next ? `: ${report.next.missing} (unlocks ${report.next.unlocks.length} skills)\n  ${report.next.command}` : ": nothing required is missing."));
console.log("\nThe doctor changed nothing. Commands above are suggestions for you to run.");
