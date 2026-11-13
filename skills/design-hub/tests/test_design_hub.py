#!/usr/bin/env python3
"""Known-answer test for design-hub on a fixture folder of fake skills (no real installed skills involved).
   python tests/test_design_hub.py   (from the design-hub folder or anywhere)"""
import json, subprocess, sys, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
S = HERE.parent / "scripts" / "find_design_skills.py"
F = HERE.parent / "examples" / "fixture-home"
out = Path(tempfile.mkdtemp()) / "o.json"
subprocess.run([sys.executable, str(S), "--no-default-roots", "--root", str(F / "plugins"), "--root", str(F / "skills"),
                "--task", "critique my signup form and fix the error message copy", "--json", str(out)], check=True, capture_output=True)
d = json.loads(out.read_text())
got = {r["invoke"]: r for r in d["design_skills"]}
checks = [
    ("plugin skills get plugin:name", {"design:design-critique", "design:ux-copy"} <= set(got)),
    ("both critiques kept apart (plugin vs SumitCraft copy)", "design-critique" in got and got["design-critique"]["plugin"] == "sumitcraft" and got["design-critique"]["role"] == "measure"),
    ("known standalone skill classified", got.get("gsap-core", {}).get("stages") == ["motion"]),
    ("unknown design skill classified by keywords", "palette-picker" in got and not got["palette-picker"]["known"]),
    ("system-design wording is not a design skill", "graph-design" not in got),
    ("non-design skill excluded", "tax-helper" not in got),
    ("overlap reported for critique", "critique" in d["overlaps"]),
    ("plan covers copy and critique", [s["stage"] for s in d["plan"]["steps"]] == ["copy", "critique"]),
    ("critique step pairs a judge with SumitCraft evidence", d["plan"]["steps"][1]["primary"] == "design:design-critique" and d["plan"]["steps"][1]["evidence"] == "design-critique"),
]
for name, ok in checks:
    print(("ok   " if ok else "FAIL ") + name)
sys.exit(0 if all(ok for _, ok in checks) else 1)
