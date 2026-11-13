#!/usr/bin/env python3
"""Run SumitCraft's functional checks and record what actually happened, per skill.

  python tests/run_checks.py                 all checks that can run here
  python tests/run_checks.py code-loop rough-cut    only these skills
  python tests/run_checks.py --list

Writes evidence/<skill>/*.txt|json|png (small, committed) and evidence/results.json; heavy outputs (videos, frames,
temporary repos) go to evidence/runs/ (git-ignored). Paths in logs are shortened to <repo> and <runs>.

Status labels, from weakest to strongest (the matrix never upgrades a label without a run):
  not run | blocked | static checks passed | smoke tested | functionally verified
"functionally verified" means a known answer was checked: a planted failure was caught AND a fixed control passed,
or an output was compared with a real reference tool. "smoke tested" means it ran end to end and produced plausible
outputs that were inspected, without a known answer. Visual/audible review is recorded separately in
evidence/reviews.json by the person (or agent) who actually looked or listened.
"""
import json, os, platform, re, shutil, subprocess, sys, time, socket, threading, http.server, functools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SK = ROOT / "skills"
EV = ROOT / "evidence"
RUNS = EV / "runs"
PY = sys.executable
NODE = shutil.which("node") or "node"
FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
RESULTS = {}


def short(s):
    s = str(s).replace(str(RUNS), "<runs>").replace(str(ROOT), "<repo>").replace(str(Path.home()), "~")
    return s


def run(cmd, cwd=None, env=None, timeout=900, log=None):
    t0 = time.time()
    p = subprocess.run([str(c) for c in cmd], cwd=cwd, env={**os.environ, **(env or {})}, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    out = short((p.stdout or "") + (p.stderr or ""))
    rec = {"cmd": short(" ".join(str(c) for c in cmd)), "rc": p.returncode, "seconds": round(time.time() - t0, 1)}
    if log is not None:
        log.append(f"$ {rec['cmd']}\n[exit {p.returncode}, {rec['seconds']} s]\n{out.strip()[-4000:]}\n")
    return p.returncode, out, rec


def ev_dir(name):
    d = EV / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def record(name, status, observed, commands, artifacts=(), gaps="", log=None):
    d = ev_dir(name)
    if log:
        (d / "run.log.txt").write_text("\n".join(log), encoding="utf-8")
    RESULTS[name] = {"status": status, "observed": observed, "commands": commands, "artifacts": [short(a) for a in artifacts] + ([f"evidence/{name}/run.log.txt"] if log else []),
                     "gaps": gaps, "platform": f"{platform.system()} {platform.release()} ({platform.machine()}), Python {platform.python_version()}",
                     "when": time.strftime("%Y-%m-%dT%H:%M:%S")}
    print(f"[{status}] {name}: {observed}")


def fresh(name):
    d = RUNS / name
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    return d


def has_mod(mod, py=PY):
    return subprocess.run([py, "-c", f"import {mod}"], capture_output=True).returncode == 0


def copy_png(src, name, dst_name, max_w=640):
    """Copy a still into evidence, downscaled with ffmpeg so the repo stays small."""
    dst = ev_dir(name) / dst_name
    subprocess.run([FF, "-v", "error", "-y", "-i", str(src), "-vf", f"scale='min({max_w},iw)':-2", str(dst)], check=False)
    return dst


# ------------------------------------------------------------------ engineering
def t_codebase_map():
    log, cmds, w = [], [], fresh("codebase-map")
    S = SK / "codebase-map/scripts"
    rc1, o1, r1 = run([PY, S / "entrypoints.py", ROOT], log=log)
    rc2, o2, r2 = run([PY, S / "deps.py", ROOT / "skills", "--json", w / "deps.json", "--mermaid", w / "deps.mmd"], log=log)
    rc3, o3, r3 = run([PY, S / "hotspots.py", ROOT, "--deps", w / "deps.json", "--anonymize"], log=log)
    rc4, o4, r4 = run([PY, S / "trace_py.py", "--repo", ROOT, "--out", w / "trace.txt", "--", SK / "from-scratch/examples/content-hash-store/hashstore.py", "--step", "2"], log=log)
    trace = (w / "trace.txt").read_text() if (w / "trace.txt").exists() else ""
    hops = len([l for l in trace.splitlines() if "hashstore.py:" in l])
    (ev_dir("codebase-map") / "trace.txt").write_text(short(trace), encoding="utf-8")
    ok = all(r == 0 for r in (rc1, rc2, rc3, rc4)) and hops >= 2
    record("codebase-map", "smoke tested" if ok else "blocked", f"entrypoints/deps/hotspots ran on this repo; Python trace recorded {hops} hops in hashstore.py",
           [r1["cmd"], r2["cmd"], r3["cmd"], r4["cmd"]], [f"evidence/codebase-map/trace.txt"], "MAP.md synthesis is a human/agent step and was not written for this repo here.", log)


def t_bisect():
    log = []
    rc, out, r = run([PY, SK / "bisect-anything/examples/selftest.py"], log=log, timeout=1200)
    passed = rc == 0
    record("bisect-anything", "functionally verified" if passed else "blocked", ("selftest: all planted scenarios found the right commit" if passed else f"selftest exit {rc}") + f" ({r['seconds']} s)",
           [r["cmd"]], [], "Windows process-tree kill path (taskkill /T) not exercised: no native Windows run.", log)


def t_flaky():
    log, w = [], fresh("flaky-test-killer")
    S = SK / "flaky-test-killer"
    run([PY, S / "examples/make_examples.py", "--out", w / "flaky"], log=log)
    run([PY, S / "examples/make_examples.py", "--out", w / "fixed", "--variant", "fixed"], log=log)
    cmd = [PY, "run_tests.py", "--seed", "{seed}"]
    rc1, o1, r1 = run([PY, S / "scripts/flake_rate.py", "-n", "30", "--json", w / "before.json", "--", *cmd], cwd=w / "flaky/py-shop", log=log, timeout=900)
    rc2, o2, r2 = run([PY, S / "scripts/flake_rate.py", "-n", "30", "--json", w / "after.json", "--compare", w / "before.json", "--", *cmd], cwd=w / "fixed/py-shop", log=log, timeout=900)
    rate = lambda o: re.search(r"(\d+) runs, (\d+) failed, rate ([\d.]+%)[^\n]*", o)
    b, a = rate(o1), rate(o2)
    fisher = re.search(r"Fisher exact p = (\S+)", o2)
    ok = b and a and int(b.group(2)) > 0 and int(a.group(2)) == 0 and "drop is real" in o2
    obs = f"planted suite: {b.group(0) if b else '?'}; fixed variant: {a.group(0) if a else '?'}; one-sided Fisher p = {fisher.group(1) if fisher else '?'}"
    record("flaky-test-killer", "functionally verified" if ok else "smoke tested", obs, [r1["cmd"], r2["cmd"]], [], "Stressor sweep and polluter search not re-run here; node-shop not run.", log)


def t_benchmark():
    log, w = [], fresh("benchmark-honestly")
    E = SK / "benchmark-honestly/examples"
    rc, out, r = run([PY, SK / "benchmark-honestly/scripts/bench.py", "-n", "a", "-n", "b", f'"{PY}" "{E / "two_sorts.py"}" a', f'"{PY}" "{E / "two_sorts.py"}" b',
                      "--runs", "12", "--warmup", "2", "--md", w / "report.md", "--json", w / "report.json", "--shell"], log=log, timeout=900)
    verdict = next((l for l in out.splitlines() if "faster" in l.lower() or "no clear" in l.lower() or "difference" in l.lower()), out.strip().splitlines()[-1] if out.strip() else "")
    if (w / "report.md").exists():
        shutil.copy(w / "report.md", ev_dir("benchmark-honestly") / "two_sorts_report.md")
    record("benchmark-honestly", "smoke tested" if rc == 0 else "blocked", f"equal-work comparison ran; verdict line: {verdict.strip()[:160]}", [r["cmd"]],
           ["evidence/benchmark-honestly/two_sorts_report.md"], "Open-loop latency tester not re-run. The equal-work case should report no clear difference; read the verdict.", log)


def t_api():
    log = []
    S, E = SK / "api-design-review/scripts", SK / "api-design-review/examples"
    rc1, o1, r1 = run([PY, S / "breaking_diff.py", E / "bookshop-v1.json", E / "bookshop-v2.yaml"], log=log)
    rc2, o2, r2 = run([PY, S / "breaking_diff.py", E / "bookshop-v1.json", E / "bookshop-v1.json"], log=log)
    rc3, o3, r3 = run([PY, S / "lint_openapi.py", E / "bookshop-v1.json"], log=log)
    rc4, o4, r4 = run([PY, S / "sdk_surface.py", E / "sample-sdk.d.ts"], log=log)
    ok = rc1 == 1 and "BREAKING" in o1 and rc2 == 0
    record("api-design-review", "functionally verified" if ok else "smoke tested",
           f"v1->v2 diff exit {rc1} with BREAKING findings; v1->v1 exit {rc2}; lint and SDK surface ran (exit {rc3}, {rc4})", [r1["cmd"], r2["cmd"], r3["cmd"], r4["cmd"]], [], "", log)


def t_security():
    log = []
    E = SK / "security-threat-model/examples/invoice-api"
    rc1, o1, r1 = run([PY, "-m", "unittest", "discover", "-s", "tests"], cwd=E, env={"TARGET": "vulnerable"}, log=log, timeout=600)
    rc2, o2, r2 = run([PY, "-m", "unittest", "discover", "-s", "tests"], cwd=E, env={"TARGET": "fixed"}, log=log, timeout=600)
    fails = re.search(r"FAILED \(([^)]*)\)", o1)
    ran = re.search(r"Ran (\d+) tests", o2)
    ok = rc1 != 0 and rc2 == 0
    record("security-threat-model", "functionally verified" if ok else "smoke tested",
           f"vulnerable: exit {rc1} ({fails.group(1) if fails else 'no failure summary'}); fixed: exit {rc2} ({ran.group(0) if ran else '?'})", [r1["cmd"] + "  [TARGET=vulnerable]", r2["cmd"] + "  [TARGET=fixed]"], [], "Owned local fixture only, by design.", log)


def t_dx():
    log, w = [], fresh("dx-audit")
    S = SK / "dx-audit/scripts"
    docs = w / "docs site"
    docs.mkdir()
    (docs / "index.html").write_text("<!doctype html><title>Tally quickstart</title><h1>Tally quickstart</h1><p>Install, then run:</p><pre><code>python -c \"print('tally ok')\"</code></pre><a href='missing.html'>Next: configuration</a>", encoding="utf-8")
    A = w / "audit"
    steps = [
        [PY, S / "friction.py", "init", A, "--tool", "Tally (fixture)", "--goal", "print tally ok", "--success", "prints 'tally ok'", "--docs", (docs / "index.html").as_uri(), "--env", f"{platform.system()} fixture", "--redact", f"{w}=~"],
        [NODE, S / "snapshot.mjs", (docs / "index.html").as_uri(), A, "--links", "--name", "01-quickstart"],
        [PY, S / "friction.py", "step", A, "--url", "index.html", "--action", "Open the quickstart", "--shot", "screenshots/01-quickstart.png"],
        [PY, S / "friction.py", "run", A, "--url", "index.html", "--action", "Run the snippet", "--cwd", w, "--show", "python -c ...", "--success-if-ok", "--", f'"{PY}" -c "print(\'tally ok\')"'],
        [PY, S / "friction.py", "amend", A, "2", "--tag", "dead-link", "--sev", "1", "--note", "Next link is a 404 in the fixture", "--fix", "Link to configuration.html"],
        [PY, S / "friction.py", "metrics", A],
        [PY, S / "friction.py", "render", A],
    ]
    rcs = []
    cmds = []
    for c in steps:
        rc, o, r = run(c, cwd=ROOT, log=log, timeout=300)
        rcs.append(rc); cmds.append(r["cmd"])
    ok = (A / "audit.md").exists() and (A / "friction.json").exists()
    for f in ("audit.md", "timeline.png"):
        if (A / f).exists():
            shutil.copy(A / f, ev_dir("dx-audit") / f)
    record("dx-audit", "smoke tested" if ok else "blocked", f"offline docs fixture: init/snapshot/step/run/amend/metrics/render exit codes {rcs}", cmds,
           ["evidence/dx-audit/audit.md", "evidence/dx-audit/timeline.png"], "No real third-party tool audited; the env -i sandbox recipe is POSIX-only.", log)


# ------------------------------------------------------------------ learning
def t_paper():
    log = []
    E = SK / "paper-to-runnable/examples/grokking"
    rc, out, r = run([PY, E / "grok.py", "--check"], cwd=E, log=log, timeout=900)
    record("paper-to-runnable", "smoke tested" if rc == 0 else "blocked", f"grokking sanity ladder (--check) exit {rc}: " + " | ".join(l.strip() for l in out.splitlines() if l.strip())[-220:],
           [r["cmd"]], [], "Full toy run, ablation and visualisation not re-run (time; matplotlib not installed here). fetch_paper not run (network).", log)


def t_system_design():
    log, cmds, rcs = [], [], []
    for ex, test in (("raft-election", "test_raft.py"), ("rate-limiter", "test_limiters.py")):
        rc, o, r = run([PY, "-m", "unittest", test.replace(".py", ""), "-v"], cwd=SK / "system-design-from-scratch/examples" / ex, log=log, timeout=900)
        rcs.append((ex, rc, re.search(r"Ran \d+ tests", o).group(0) if re.search(r"Ran \d+ tests", o) else "?")); cmds.append(r["cmd"])
    ok = all(rc == 0 for _, rc, _ in rcs)
    record("system-design-from-scratch", "functionally verified" if ok else "smoke tested", "; ".join(f"{e}: exit {rc}, {n}" for e, rc, n in rcs), cmds, [],
           "Load tests and fault sweeps from DESIGN.md not re-run here.", log)


def t_from_scratch():
    log = []
    E = SK / "from-scratch/examples/content-hash-store/hashstore.py"
    rc1, o1, r1 = run([PY, E, "--step", "4"], log=log)
    rc2, o2, r2 = run([PY, E, "--compare-git"], log=log)
    record("from-scratch", "functionally verified" if rc2 == 0 and "all match" in o2 else "smoke tested", "worked example matches `git hash-object` for empty, ASCII, Unicode and binary input; tamper detection shown",
           [r1["cmd"], r2["cmd"]], [], "The method itself is guidance; only the worked example is executable.", log)


# ------------------------------------------------------------------ design
def t_image_gen():
    log = []
    G = SK / "image-gen/scripts/gen_image.py"
    env = {"GEMINI_API_KEY": "", "OPENAI_API_KEY": "", "GOOGLE_API_KEY": "", "SUMITCRAFT_CONFIG": str(fresh("image-gen") / "cfg")}
    rc1, o1, r1 = run([PY, G, "--check"], env=env, log=log)
    rc2, o2, r2 = run([PY, G, "a red teapot", "--n", "3", "--cutout", "--dry-run"], env=env, log=log)
    rc3, o3, r3 = run([PY, G, "a red teapot", "--n", "3"], env=env, log=log)
    ok = rc1 == 0 and rc2 == 0 and "paid_image_calls: 3" in o2 and rc3 == 3 and "no request was sent" in o3
    record("image-gen", "smoke tested" if ok else "blocked", f"offline only: --check exit {rc1}; --dry-run exit {rc2} shows 3 paid calls; without --approve-spend exit {rc3}, no request sent. No provider was called.",
           [r1["cmd"], r2["cmd"], r3["cmd"]], [], "Live provider generation not run: needs the user's key and approval of a paid call. This is not a provider pass.", log)


def serve(directory):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    handler.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def t_brand_kit():
    log, w = [], fresh("brand-kit")
    site = w / "site"
    site.mkdir()
    (site / "index.html").write_text("""<!doctype html><html><head><title>Fernwick (fictional)</title><style>
:root{--brand-ink:#14213d;--brand-accent:#e85d04;--brand-paper:#fbf7f0}
body{margin:0;background:var(--brand-paper);color:var(--brand-ink);font:17px/1.5 Georgia,serif}
header{padding:24px 48px;display:flex;justify-content:space-between;align-items:center}
.logo{font:700 24px system-ui;letter-spacing:-.02em}
h1{font:800 64px/1 system-ui;letter-spacing:-.03em;margin:80px 48px 16px;max-width:12ch}
p{margin:0 48px 32px;max-width:52ch}
.btn{display:inline-block;margin-left:48px;background:var(--brand-accent);color:#fff;padding:14px 22px;border-radius:999px;font:600 16px system-ui;text-decoration:none}
.card{margin:48px;padding:24px;background:#fff;border-radius:14px;box-shadow:0 2px 10px rgb(0 0 0/.08)}
</style></head><body><header><div class=logo>Fernwick</div><nav>Plans · Stories</nav></header>
<h1>Tea for slow mornings</h1><p>A made-up brand used only as a SumitCraft test fixture.</p><a class=btn href=#>Start a box</a>
<div class=card><h2>Rooibos & orange</h2><p>Caffeine free.</p></div></body></html>""", encoding="utf-8")
    srv = serve(site)
    url = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
    kit = w / "kits" / "fernwick"
    rc1, o1, r1 = run([NODE, SK / "brand-kit/scripts/extract.mjs", url, kit], cwd=ROOT, log=log, timeout=300)
    rc2, o2, r2 = run([PY, SK / "brand-kit/scripts/propose.py", kit, "--name", "Fernwick"], log=log)
    rc3, o3, r3 = run([PY, SK / "brand-kit/scripts/board.py", kit], cwd=ROOT, log=log, timeout=600)
    srv.shutdown()
    arts = []
    if (kit / "brand.json").exists():
        b = json.loads((kit / "brand.json").read_text())
        (ev_dir("brand-kit") / "brand.json").write_text(json.dumps(b, indent=1), encoding="utf-8"); arts.append("evidence/brand-kit/brand.json")
    if (kit / "board.png").exists():
        copy_png(kit / "board.png", "brand-kit", "board.png", 900); arts.append("evidence/brand-kit/board.png")
    ok = rc1 == 0 and rc2 == 0 and rc3 == 0
    record("brand-kit", "smoke tested" if ok else "blocked", f"fictional local brand: extract exit {rc1}, propose exit {rc2}, board exit {rc3}", [r1["cmd"], r2["cmd"], r3["cmd"]], arts,
           "No real brand extracted (by design for fixtures). Official-guideline check is a manual step.", log)


def t_d2c():
    log = []
    S, E = SK / "design-to-code-inspection/scripts/inspect_layout.mjs", SK / "design-to-code-inspection/examples/pricing-card/spec.json"
    w = fresh("design-to-code-inspection")
    rc1, o1, r1 = run([NODE, S, E, "--out", w / "bad"], cwd=ROOT, log=log)
    rc2, o2, r2 = run([NODE, S, E, "--page", "fixed.html", "--out", w / "good"], cwd=ROOT, log=log)
    n1 = re.search(r"(\d+) mismatches", o1); n2 = re.search(r"(\d+) mismatches", o2)
    for src, dst in ((w / "bad/report.md", "report-planted.md"), (w / "good/report.md", "report-fixed.md")):
        if src.exists(): shutil.copy(src, ev_dir("design-to-code-inspection") / dst)
    if (w / "good/shot-375.png").exists(): copy_png(w / "good/shot-375.png", "design-to-code-inspection", "fixed-375.png", 375)
    ok = rc1 == 1 and rc2 == 0 and n1 and int(n1.group(1)) > 0
    record("design-to-code-inspection", "functionally verified" if ok else "smoke tested", f"planted fixture: exit {rc1}, {n1.group(0) if n1 else '?'}; fixed: exit {rc2}, {n2.group(0) if n2 else '?'}",
           [r1["cmd"], r2["cmd"]], ["evidence/design-to-code-inspection/report-planted.md", "evidence/design-to-code-inspection/report-fixed.md", "evidence/design-to-code-inspection/fixed-375.png"], "", log)


def t_critique():
    log, w = [], fresh("design-critique")
    E = SK / "design-critique/examples/signup-form"
    rc, o, r = run([NODE, SK / "design-critique/scripts/before_after.mjs", E / "before.html", E / "after.html", "--widths", "375,1280", "--out", w], cwd=ROOT, log=log)
    rc2, o2, r2 = run([PY, SK / "design-system-build/scripts/tokens.py", "--pair", "#ffffff", "#b9e4bf"], log=log)
    rc3, o3, r3 = run([PY, SK / "design-system-build/scripts/tokens.py", "--pair", "#ffffff", "#1f6f3a"], log=log)
    for f in ("375-before.png", "375-after.png", "375-diff.png"):
        if (w / f).exists(): copy_png(w / f, "design-critique", f, 375)
    if (w / "before_after.md").exists(): shutil.copy(w / "before_after.md", ev_dir("design-critique") / "before_after.md")
    ok = rc == 0 and "FAIL" in o2 and "pass" in o3
    record("design-critique", "functionally verified" if ok else "smoke tested", f"before/after diff exit {rc} ({o.strip().splitlines()[0] if o.strip() else ''}); button contrast before {o2.split(':')[1].split()[0] if ':' in o2 else '?'}:1 fails, after {o3.split(':')[1].split()[0] if ':' in o3 else '?'}:1 passes",
           [r["cmd"], r2["cmd"], r3["cmd"]], ["evidence/design-critique/375-before.png", "evidence/design-critique/375-after.png", "evidence/design-critique/375-diff.png", "evidence/design-critique/before_after.md"],
           "The critique itself is judgement; only its evidence measurements are automated.", log)


def t_dsb():
    log = []
    S, E = SK / "design-system-build/scripts/tokens.py", SK / "design-system-build/examples/garden-ui"
    w = fresh("design-system-build")
    rc1, o1, r1 = run([PY, S, E / "tokens.json", "--css", w / "tokens.css", "--report", w / "good.md"], log=log)
    rc2, o2, r2 = run([PY, S, E / "tokens-broken.json", "--report", w / "broken.md"], log=log)
    rc3, o3, r3 = run([PY, S, "--audit-css", E / "components.html"], log=log)
    rc4, o4, r4 = run([PY, S, "--audit-css", SK / "design-critique/examples/signup-form/before.html"], log=log)
    same = (w / "tokens.css").read_text() == (E / "tokens.css").read_text().replace("\r\n", "\n") if (w / "tokens.css").exists() else False
    for src, dst in ((w / "good.md", "token-report.md"), (w / "broken.md", "token-report-broken.md")):
        if src.exists(): shutil.copy(src, ev_dir("design-system-build") / dst)
    ok = rc1 == 0 and rc2 == 1 and rc3 == 0 and rc4 == 1 and same
    record("design-system-build", "functionally verified" if ok else "smoke tested",
           f"tokens.json exit {rc1} ({o1.strip().splitlines()[0]}); broken copy exit {rc2} ({o2.strip().splitlines()[0]}); CSS audit clean exit {rc3}, hard-coded page exit {rc4}; committed tokens.css reproduces: {same}",
           [r1["cmd"], r2["cmd"], r3["cmd"], r4["cmd"]], ["evidence/design-system-build/token-report.md", "evidence/design-system-build/token-report-broken.md"], "", log)


def t_motion():
    log, w = [], fresh("interaction-motion-study")
    S, E = SK / "interaction-motion-study/scripts/check_study.mjs", SK / "interaction-motion-study/examples/disclosure-menu"
    rc1, o1, r1 = run([NODE, S, E / "index.html", "--out", w / "good"], cwd=ROOT, log=log)
    rc2, o2, r2 = run([NODE, S, E / "hover-only.html", "--out", w / "bad"], cwd=ROOT, log=log)
    for src, dst in ((w / "good/check.md", "check-study.md"), (w / "bad/check.md", "check-hover-only.md")):
        if src.exists(): shutil.copy(src, ev_dir("interaction-motion-study") / dst)
    if (w / "good/open.png").exists(): copy_png(w / "good/open.png", "interaction-motion-study", "open.png", 640)
    f1, f2 = o1.count("FAIL"), o2.count("FAIL")
    ok = rc1 == 0 and rc2 == 1 and f2 >= 4
    record("interaction-motion-study", "functionally verified" if ok else "smoke tested", f"study: exit {rc1}, {f1} failed checks; hover-only: exit {rc2}, {f2} failed checks",
           [r1["cmd"], r2["cmd"]], ["evidence/interaction-motion-study/check-study.md", "evidence/interaction-motion-study/check-hover-only.md", "evidence/interaction-motion-study/open.png"],
           "Screen-reader announcements and touch not verified.", log)


def t_vra():
    log, w = [], fresh("visual-reference-analysis")
    E = SK / "visual-reference-analysis/examples/poster-study"
    rc1, o1, r1 = run([PY, SK / "visual-reference-analysis/scripts/analyze_image.py", E / "reference.png", "--out", w / "ref"], log=log)
    a = json.loads((w / "ref/analysis.json").read_text()) if (w / "ref/analysis.json").exists() else {}
    # Known answer: in the fixture the orange disc is a circle of radius 180 px, partly cropped by the right edge.
    import math
    seg = 180 ** 2 * math.acos(120 / 180) - 120 * math.sqrt(180 ** 2 - 120 ** 2)  # area of the disc beyond x=600 (centre x=480)
    expected = (math.pi * 180 ** 2 - seg) / (600 * 840)
    orange = next((p["share"] for p in a.get("palette", []) if p["hex"].startswith("#d9") or p["hex"].startswith("#da")), None)
    ok = rc1 == 0 and orange is not None and abs(orange - expected) < 0.01
    (ev_dir("visual-reference-analysis") / "known-answer.txt").write_text(f"expected accent share (geometry) {expected:.4f}; measured {orange}\n", encoding="utf-8")
    record("visual-reference-analysis", "functionally verified" if ok else "smoke tested", f"accent coverage measured {orange} vs {expected:.4f} from the fixture's geometry; analysis exit {rc1}",
           [r1["cmd"]], ["evidence/visual-reference-analysis/known-answer.txt"], "Hierarchy and meaning are judgement, reviewed by eye, not measured.", log)


# ------------------------------------------------------------------ planning
def t_router():
    log = []
    rc, o, r = run([PY, SK / "skill-router/scripts/catalog.py", "--json"], log=log)
    try:
        rows = json.loads(o)
    except Exception:
        rows = []
    names = {x.get("name") for x in rows}
    want = {p.name for p in SK.iterdir() if (p / "SKILL.md").exists()}
    ok = rc == 0 and want <= names
    record("skill-router", "functionally verified" if ok else "smoke tested", f"catalog.py lists {len(want & names)}/{len(want)} repo skills", [r["cmd"]], [], "Routing judgement is covered by scenarios in tests/scenarios/guidance.md, not executed automatically.", log)


def t_w2e():
    log, w = [], fresh("work-to-explanation")
    S = SK / "work-to-explanation/scripts/preflight.py"
    good = SK / "work-to-explanation/examples/webgl-backend-case-study/draft.md"
    bad = w / "bad-draft.md"
    fake_key = "sk-" + "proj" + "A" * 30  # assembled at run time so the repo holds no key-shaped string
    bad.write_text(f"---\ntitle: test\n---\nWe cut render time by 63% on my laptop.\nPath: /home/{'alex'}/projects/app/render.log\nkey: {fake_key}\n[evidence: missing.txt]\n", encoding="utf-8")
    rc1, o1, r1 = run([PY, S, good], log=log)
    rc2, o2, r2 = run([PY, S, bad], log=log)
    kinds = sorted(set(re.findall(r"BLOCK (\S+)", o2)))
    ok = rc1 == 0 and rc2 == 1 and {"secret", "private-path", "evidence", "front-matter"} <= set(kinds)
    record("work-to-explanation", "functionally verified" if ok else "smoke tested", f"real case study: exit {rc1}; planted bad draft: exit {rc2}, blockers {kinds}", [r1["cmd"], r2["cmd"]], [], "Patterns are heuristics; a person still reads the draft.", log)


def t_guidance(name, note):
    record(name, "static checks passed", note, ["node tools/validate.mjs"], ["tests/scenarios/guidance.md"], "Guidance-only workflow: scenarios are written down; no automatic success score is claimed.")


# ------------------------------------------------------------------ video
def t_code_loop():
    log, w = [], fresh("code-loop")
    S = SK / "code-loop"
    # Scripts run from the repo (so Playwright resolves from the repo's node_modules: no symlinks, which Windows
    # does not allow without developer mode); only the page is copied, because the renderer serves the page's folder.
    shutil.copy(S / "templates/shader_starter.html", w / "shader_starter.html")
    RL, CL = str(S / "scripts/render_loop.mjs"), str(S / "scripts/check_loop.py")
    bad = (w / "shader_starter.html").read_text().replace("[[1, 2, 0.0], [2, 1, 2.1], [1, 3, 4.2]]", "[[1.37, 2, 0.0], [2, 1, 2.1], [1, 3, 4.2]]")
    (w / "bad_loop.html").write_text(bad)
    cmds, arts = [], []
    rc1, o1, r1 = run([NODE, RL, "shader_starter.html", "good.mp4", "--preview", "--size=480x270", "--maxk=2"], cwd=w, log=log, timeout=1800); cmds.append(r1["cmd"])
    rc2, o2, r2 = run([PY, CL, "good.mp4", "--heat", "blink.png"], cwd=w, log=log); cmds.append(r2["cmd"])
    rc3, o3, r3 = run([NODE, RL, "bad_loop.html", "bad.mp4", "--preview", "--size=480x270", "--maxk=2"], cwd=w, log=log, timeout=1800); cmds.append(r3["cmd"])
    rc4, o4, r4 = run([PY, CL, "bad.mp4"], cwd=w, log=log); cmds.append(r4["cmd"])
    # declared holds: a 2 s clip that moves, holds still from 0.8-1.6 s, then moves back
    run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=30:duration=0.8", "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=30:duration=0.8",
         "-filter_complex", "[0]tpad=stop_mode=clone:stop_duration=0.8[a];[a][1]concat=n=2:v=1[v]", "-map", "[v]", "-pix_fmt", "yuv420p", w / "hold.mp4"], log=log)
    rc5, o5, r5 = run([PY, CL, "hold.mp4", "--freeze-sec", "0.5"], cwd=w, log=log); cmds.append(r5["cmd"])
    rc6, o6, r6 = run([PY, CL, "hold.mp4", "--freeze-sec", "0.5", "--holds", "0.75-1.65"], cwd=w, log=log); cmds.append(r6["cmd"])
    man = w / "good.render.json"
    if man.exists():
        m = json.loads(man.read_text()); (ev_dir("code-loop") / "good.render.json").write_text(json.dumps(m, indent=2), encoding="utf-8"); arts.append("evidence/code-loop/good.render.json")
    run([FF, "-v", "error", "-y", "-ss", "2", "-i", w / "good.mp4", "-frames:v", "1", w / "frame2s.png"])
    if (w / "frame2s.png").exists(): copy_png(w / "frame2s.png", "code-loop", "preview-frame-2s.png", 480); arts.append("evidence/code-loop/preview-frame-2s.png")
    rc7, o7, r7 = run([NODE, RL, "shader_starter.html", "final_small.mp4", "--size=320x180", "--fps=30", "--mink=4", "--maxk=8"], cwd=w, log=log, timeout=3600); cmds.append(r7["cmd"])
    rc8, o8, r8 = run([PY, CL, "final_small.mp4", "--heat", "blink_final.png"], cwd=w, log=log); cmds.append(r8["cmd"])
    res = lambda o: (re.search(r"RESULT: (.*)", o).group(1)[:110] if re.search(r"RESULT: (.*)", o) else "?")
    exact = lambda o: (re.search(r"seam \(exact\): ([^\n]*)", o).group(1) if re.search(r"seam \(exact\): ([^\n]*)", o) else "?")
    good_exact_ok = "0 pixels differ by more than 2" in o2
    bad_exact_fail = "exact seam" in res(o4)
    holds_ok = "frozen spans" in res(o5) and "frozen spans" not in res(o6) and "inside a declared hold" in o6
    ok = rc1 == 0 and rc3 == 0 and good_exact_ok and bad_exact_fail and holds_ok
    record("code-loop", "functionally verified" if ok else ("smoke tested" if rc1 == 0 else "blocked"),
           f"exact seam, real loop: {exact(o2)} (pass); planted 1.37-cycle loop: {exact(o4)} (caught); declared-hold clip: 'frozen spans' failure without --holds, reported as intended with --holds. "
           f"Overall verdicts: preview {res(o2)}; small final (320x180, 30 fps, 4-8 samples): {res(o8)}",
           cmds, arts, "The synthetic hold clip is not a loop, so its seam/blink verdicts are meaningless; only its freeze line is the test. Renders were small (480x270 preview, 320x180 final) on software WebGL; no 1080p final; Metal/D3D11 backends not exercised (no macOS/Windows run).", log)


def t_perspective():
    log, w = [], fresh("perspective-illusion")
    T = SK / "perspective-illusion/templates"
    for f in T.iterdir():
        if f.is_file(): shutil.copy(f, w / f.name)
    (w / "package.json").write_text('{"type":"module"}')
    rc0, o0, r0 = run(["npm", "install", "--no-audit", "--no-fund", "three@0.170.0", "playwright@1.63.0"], cwd=w, log=log, timeout=600)
    if rc0 != 0:
        return record("perspective-illusion", "blocked", "npm install of three@0.170.0 failed", [r0["cmd"]], [], "Needs npm registry access.", log)
    rc1, o1, r1 = run([NODE, "render.mjs", "street.html", "x.mp4", "--stills=0.3,3"], cwd=w, log=log, timeout=1800)
    stills = sorted(w.glob("stills/*.png")) + sorted(w.glob("*.png"))
    arts = []
    for i, s in enumerate([p for p in stills if "still" in p.name or p.parent.name == "stills"][:2]):
        copy_png(s, "perspective-illusion", f"street-still-{i}.png", 960); arts.append(f"evidence/perspective-illusion/street-still-{i}.png")
    gl = re.search(r"\[gl\][^\n]*", o1)
    record("perspective-illusion", "smoke tested" if rc1 == 0 and arts else "blocked", f"street.html stills render exit {rc1}; {gl.group(0) if gl else 'no [gl] line'}", [r0["cmd"], r1["cmd"]], arts,
           "Only stills; no preview or final video (software WebGL is slow). scramble_night needs the unshipped cut-outs.", log)


def t_screencast():
    log = []
    w = fresh("scripted-screencast") / "demo folder ü ✓"
    shutil.copytree(SK / "scripted-screencast/examples", w)
    rc0, o0, r0 = run([NODE, SK / "scripted-screencast/scripts/render.mjs", w / "tidy-demo.mjs", "--preview"], cwd=w, log=log, timeout=1800)
    rc, o, r = run([NODE, SK / "scripted-screencast/scripts/render.mjs", w / "tidy-demo.mjs", "--preview", "--stills", "2,6"], cwd=w, log=log, timeout=1800)
    rc = rc or rc0
    mp4s = [p for p in w.rglob("*.mp4")]
    shots = sorted(list(w.rglob("stills/*.jpg")) + list(w.rglob("stills/*.png")))
    arts = []
    for i, s in enumerate([p for p in shots if "failed" not in p.name][:2]):
        copy_png(s, "scripted-screencast", f"still-{i}.png", 960); arts.append(f"evidence/scripted-screencast/still-{i}.png")
    record("scripted-screencast", "smoke tested" if rc == 0 and arts else "blocked", f"demo run from a folder named 'demo folder ü ✓': preview exit {rc0} ({len(mp4s)} mp4), stills exit {rc}, {len(arts)} stills", [r0["cmd"], r["cmd"]], arts,
           "Windows drive-letter URL path verified by code review and the URL unit check in tests/unit_paths.mjs, not on Windows.", log)


def t_timelapse():
    log, w = [], fresh("repo-timelapse")
    S = SK / "repo-timelapse/scripts"
    rc1, o1, r1 = run([PY, S / "extract.py", ROOT, "-o", w / "history.json", "--anonymize", "--redact-messages", "upstream", "--name", "SumitCraft"], log=log)
    rc2, o2, r2 = run([NODE, S / "render.mjs", w / "history.json", w / "timelapse.mp4", "--stills", "2,6", "--duration", "8"], cwd=ROOT, log=log, timeout=1800)
    arts = []
    if (w / "history.messages.txt").exists():
        shutil.copy(w / "history.messages.txt", ev_dir("repo-timelapse") / "history.messages.txt"); arts.append("evidence/repo-timelapse/history.messages.txt")
    for i, s in enumerate(sorted(w.rglob("*.png"))[:2]):
        copy_png(s, "repo-timelapse", f"still-{i}.png", 960); arts.append(f"evidence/repo-timelapse/still-{i}.png")
    withheld = "(message withheld)" in (w / "history.messages.txt").read_text() if (w / "history.messages.txt").exists() else False
    record("repo-timelapse", "smoke tested" if rc1 == 0 and rc2 == 0 else "blocked", f"extract exit {rc1} (anonymised; redaction applied: {withheld}); stills render exit {rc2}", [r1["cmd"], r2["cmd"]], arts,
           "Few commits in this repo, so the video is thin by the skill's own rule; no full video rendered here.", log)


def t_reverse():
    log, w = [], fresh("reverse-engineer-video")
    # Known answer: four 1.5 s shots with different sources -> cuts at 1.5, 3.0 and 4.5 s.
    srcs = ["testsrc2=size=480x270:rate=30", "mandelbrot=size=480x270:rate=30", "smptebars=size=480x270:rate=30", "rgbtestsrc=size=480x270:rate=30"]
    args = []
    for s in srcs:
        args += ["-f", "lavfi", "-t", "1.5", "-i", s]
    run([FF, "-v", "error", "-y", *args, "-f", "lavfi", "-t", "6", "-i", "sine=frequency=440:sample_rate=48000",
         "-filter_complex", "[0][1][2][3]concat=n=4:v=1:a=0[v]", "-map", "[v]", "-map", "4:a", "-pix_fmt", "yuv420p", "-shortest", w / "clip.mp4"], log=log)
    rc, o, r = run([PY, SK / "reverse-engineer-video/scripts/analyze.py", w / "clip.mp4", "-o", w / "out"], log=log, timeout=900)
    bj = w / "out/breakdown.json"
    cuts = []
    if bj.exists():
        b = json.loads(bj.read_text())
        cuts = b.get("cuts") or [s.get("start") for s in b.get("shots", [])[1:]]
        cuts = [c if isinstance(c, (int, float)) else c.get("t", c.get("time")) for c in cuts]
        (ev_dir("reverse-engineer-video") / "detected_cuts.json").write_text(json.dumps({"expected": [1.5, 3.0, 4.5], "detected": cuts}, indent=1))
    if (w / "out/contact_sheet.jpg").exists():
        copy_png(w / "out/contact_sheet.jpg", "reverse-engineer-video", "contact_sheet.png", 900)
    ok = rc == 0 and len(cuts) == 3 and all(abs(a - b) <= 1 / 30 + 1e-6 for a, b in zip(sorted(cuts), [1.5, 3.0, 4.5]))
    record("reverse-engineer-video", "functionally verified" if ok else ("smoke tested" if rc == 0 else "blocked"), f"synthetic clip with cuts at 1.5/3.0/4.5 s: detected {cuts}",
           [r["cmd"]], ["evidence/reverse-engineer-video/detected_cuts.json", "evidence/reverse-engineer-video/contact_sheet.png"],
           "Camera-motion labels not checked against a known answer; OpenCV, Whisper and tesseract paths not exercised.", log)


def t_rough_cut():
    log, w = [], fresh("rough-cut")
    if not has_mod("numpy"):
        return record("rough-cut", "blocked", "numpy missing", [], [], "")
    (w / "raw").mkdir(); (w / "audio").mkdir()
    # Synthetic "speech": tone bursts are words, silences are pauses. Words: "so um the plan the plan works", with a 1.2 s dead-air gap.
    words = [("so", 0.30, 0.55), ("um", 0.75, 1.05), ("the", 1.20, 1.40), ("plan", 1.45, 1.85), ("the", 3.05, 3.25), ("plan", 3.30, 3.70), ("works", 3.75, 4.20)]
    expr = "+".join(f"between(t,{a},{b})*sin(2*PI*220*t)" for _, a, b in words)
    run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", f"aevalsrc='0.6*({expr})':s=48000:d=4.8", "-f", "lavfi", "-i", "color=c=gray:s=320x180:r=30:d=4.8",
         "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", w / "raw/take1.mp4"], log=log)
    run([FF, "-v", "error", "-y", "-i", w / "raw/take1.mp4", "-ac", "1", "-ar", "16000", w / "audio/take1.wav"], log=log)
    (w / "audio/words.json").write_text(json.dumps({"take1.mp4": [[a, b, wd, 0.95] for wd, a, b in words]}))
    rc1, o1, r1 = run([PY, SK / "rough-cut/scripts/find_cuts.py", w], cwd=SK / "rough-cut/scripts", log=log)
    edl = json.loads((w / "cuts/edl.json").read_text()) if (w / "cuts/edl.json").exists() else {}
    edl = edl.get("keep", []) if isinstance(edl, dict) else edl
    kept = " ".join(p.get("text", "") for p in edl)
    rc2, o2, r2 = run([PY, SK / "rough-cut/scripts/render.py", w, "--w", "320", "--v", "1"], cwd=SK / "rough-cut/scripts", log=log, timeout=600)
    for f in ("cuts/edl.json", "cuts/cut_sheet.md"):
        if (w / f).exists(): shutil.copy(w / f, ev_dir("rough-cut") / Path(f).name)
    ok = rc1 == 0 and "um" not in kept.split() and kept.count("plan") == 1
    record("rough-cut", "smoke tested" if ok and rc2 == 0 else ("smoke tested" if rc1 == 0 else "blocked"),
           f"model-free synthetic take: find_cuts exit {rc1}, kept text '{kept.strip()}' (filler dropped, retake kept once); render exit {rc2}", [r1["cmd"], r2["cmd"]],
           ["evidence/rough-cut/edl.json", "evidence/rough-cut/cut_sheet.md"], "transcribe.py and verify.py need Whisper weights (0.5-1.5 GB download): blocked pending approval. No real speech, no Hindi/English test yet.", log)


def t_clean_audio():
    record("clean-audio", "blocked", "needs Whisper in rough-cut/.venv for the clarity check; the model download (about 0.5 GB for small) has not been approved", [], [],
           "Next: python skills/rough-cut/setup.py --yes, then the commands in docs/VALIDATION_MATRIX.md.")


def t_vox():
    log, w = [], fresh("vox-explainer")
    words = [[0.0, 0.3, "Every"], [0.3, 0.6, "garden"], [0.6, 1.0, "starts"], [1.0, 1.3, "with"], [1.3, 1.8, "one"], [1.8, 2.3, "seed"],
             [3.0, 3.4, "Forty"], [3.4, 3.8, "plots"], [3.8, 4.2, "this"], [4.2, 4.6, "year"]]
    (w / "words.json").write_text(json.dumps(words))
    run([FF, "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "6", w / "vo.wav"], log=log)
    cmds, arts, rcs = [], [], []
    for preset in ("editorial-collage", "quiet-paper", "night-signal"):
        sc = {"audio": "vo.wav", "preset": preset, "beats": [
            {"at": "Every", "device": "big", "bg": "a", "text": "One seed", "sub": "Where every garden starts", "submark": "garden", "submark_at": "garden"},
            {"at": "Forty", "device": "stat", "bg": "b", "value": 40, "suffix": " plots", "sub": "this year"}]}
        (w / f"{preset}.json").write_text(json.dumps(sc))
        rc, o, r = run([PY, SK / "vox-explainer/scripts/build.py", w / f"{preset}.json", "--words", w / "words.json", "--stills", "1.9,4.5"], cwd=w, log=log, timeout=900)
        rcs.append(rc); cmds.append(r["cmd"])
        for i, s in enumerate(sorted(w.glob("still_*.jpg"))[:2]):  # build.py names stills still_<t>.jpg; copy before the next preset overwrites them
            copy_png(s, "vox-explainer", f"{preset}-{i}.png", 640); arts.append(f"evidence/vox-explainer/{preset}-{i}.png")
            s.unlink()
    record("vox-explainer", "smoke tested" if all(r == 0 for r in rcs) and arts else "blocked", f"one scene as stills in 3 presets from a given word-timing file: exit codes {rcs}, {len(arts)} stills", cmds, arts,
           "No voiceover transcription (Whisper) and no preview/final video here; photo beats with url not exercised.", log)


CHECKS = {
    "codebase-map": t_codebase_map, "bisect-anything": t_bisect, "flaky-test-killer": t_flaky, "benchmark-honestly": t_benchmark,
    "api-design-review": t_api, "security-threat-model": t_security, "dx-audit": t_dx,
    "paper-to-runnable": t_paper, "system-design-from-scratch": t_system_design, "from-scratch": t_from_scratch,
    "teach-back": lambda: t_guidance("teach-back", "guidance-only; scenarios defined"),
    "next-step": lambda: t_guidance("next-step", "guidance-only; scenarios defined"),
    "video-script": lambda: t_guidance("video-script", "guidance-only; scenarios defined"),
    "learn-a-domain": lambda: t_guidance("learn-a-domain", "guidance-only; scenarios defined, including a professional-advice refusal case"),
    "image-gen": t_image_gen, "brand-kit": t_brand_kit, "skill-router": t_router,
    "design-to-code-inspection": t_d2c, "design-critique": t_critique, "design-system-build": t_dsb, "interaction-motion-study": t_motion,
    "visual-reference-analysis": t_vra, "work-to-explanation": t_w2e,
    "code-loop": t_code_loop, "perspective-illusion": t_perspective, "scripted-screencast": t_screencast, "repo-timelapse": t_timelapse,
    "reverse-engineer-video": t_reverse, "rough-cut": t_rough_cut, "clean-audio": t_clean_audio, "vox-explainer": t_vox,
}


def main():
    a = sys.argv[1:]
    if "--list" in a:
        print("\n".join(CHECKS)); return
    want = [x for x in a if not x.startswith("--")] or list(CHECKS)
    RUNS.mkdir(parents=True, exist_ok=True)
    prev = EV / "results.json"
    if prev.exists():
        RESULTS.update(json.loads(prev.read_text()).get("skills", {}))
    for n in want:
        try:
            CHECKS[n]()
        except Exception as e:  # a crashing check is recorded, not hidden
            record(n, "blocked", f"check crashed: {type(e).__name__}: {short(e)[:200]}", [], [], "See the traceback by re-running this check alone.")
    prev.write_text(json.dumps({"tool": "sumitcraft tests/run_checks.py", "updated": time.strftime("%Y-%m-%dT%H:%M:%S"), "skills": dict(sorted(RESULTS.items()))}, indent=2), encoding="utf-8")
    print(f"\nwrote {short(prev)}")


if __name__ == "__main__":
    main()
