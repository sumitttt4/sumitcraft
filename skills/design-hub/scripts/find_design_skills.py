#!/usr/bin/env python3
"""Find every design skill installed on this machine, sort them into design stages, show overlaps, and merge them
into one plan for a task. Standard library only; read-only (it never copies, edits or installs a skill).

  python find_design_skills.py                       grouped table of installed design skills
  python find_design_skills.py --task "polish my pricing page and make it accessible"
  python find_design_skills.py --json out.json       machine-readable inventory (+ plan if --task)
  python find_design_skills.py --root DIR [--root DIR] [--no-default-roots]   scan other folders (tests, teams)

Where it looks (whatever exists on this machine): <home>/.claude/skills (including synced packs), <home>/.claude/plugins
(plugin skills, named plugin:skill), ./.claude/skills (project), $CLAUDE_CONFIG_DIR/skills and /plugins, /mnt/skills
(cloud images), and the SumitCraft skills folder this script ships in. Windows: <home> is %USERPROFILE%.

Classification: known.json first (by "name@plugin", then "name"), otherwise stage keywords from stages.json matched
against the name and description. A skill counts as design-related if it is known or matches design words.
It reports only names, stages and its own one-line summaries; it does not reproduce other skills' text.
"""
import json, os, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent          # the design-hub skill folder
STAGES = json.loads((HERE / "stages.json").read_text(encoding="utf-8"))
KNOWN = json.loads((HERE / "known.json").read_text(encoding="utf-8"))["skills"]
ORDER = [s["id"] for s in STAGES["stages"]]
KNOWN_NOT_DESIGN = set(json.loads((HERE / "known.json").read_text(encoding="utf-8")).get("not_design", []))
LABEL = {s["id"]: s["label"] for s in STAGES["stages"]}
SKIP = {"node_modules", ".venv", "__pycache__", ".git", "examples", "templates", "tests", "fixture-home"}


def default_roots():
    home = Path.home()
    roots = [home / ".claude" / "skills", home / ".claude" / "plugins", Path.cwd() / ".claude" / "skills",
             Path("/mnt/skills"), HERE.parent]
    cfg = os.environ.get("CLAUDE_CONFIG_DIR")
    if cfg:
        roots += [Path(cfg) / "skills", Path(cfg) / "plugins"]
    return roots


def frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    out, key = {}, None
    for line in (m.group(1).splitlines() if m else []):
        kv = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if kv:
            key = kv.group(1); out[key] = kv.group(2).strip().strip("\"'")
        elif key and line.startswith((" ", "\t")):
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def plugin_of(skill_md, stop):
    """Name of the plugin that owns this skill, from the nearest .claude-plugin/plugin.json above it (max 4 levels)."""
    d = skill_md.parent
    for _ in range(4):
        d = d.parent
        pj = d / ".claude-plugin" / "plugin.json"
        if pj.exists():
            try:
                return json.loads(pj.read_text(encoding="utf-8")).get("name")
            except (OSError, ValueError):
                return None
        if d == d.parent:
            break
    return None


def walk(root, depth=6):
    if not root.is_dir():
        return
    stack = [(root, 0)]
    while stack:
        d, n = stack.pop()
        try:
            entries = list(os.scandir(d))
        except OSError:
            continue
        for e in entries:
            if e.is_file() and e.name == "SKILL.md":
                yield Path(e.path)
            elif e.is_dir(follow_symlinks=False) and n < depth and e.name not in SKIP:
                stack.append((Path(e.path), n + 1))


def classify(name, plugin, desc):
    k = KNOWN.get(f"{name}@{plugin}") or KNOWN.get(name)
    if k:
        return k["stages"], k["role"], k["summary"], k["from"], True
    text = f"{name.replace('-', ' ')} {desc}".lower()
    hits = {s["id"]: sum(kw in text for kw in s["keywords"]) for s in STAGES["stages"]}
    stages = [s for s in ORDER if hits[s] > 0]
    stages = sorted(stages, key=lambda s: -hits[s])[:2]
    # Unknown skills need real design vocabulary: at least two distinct design words, not counting "design" itself
    # (which also means "system design", "API design").
    words = {w for w in STAGES["design_words"] if w != "design" and re.search(rf"\b{re.escape(w)}\b", text)}
    design = bool(stages) and len(words) >= 2 and name not in KNOWN_NOT_DESIGN
    summary = re.split(r"(?<=[.!?])\s", desc.strip())[0][:110] if desc else ""
    return (stages if design else []), "unknown", summary, plugin or "installed skill", False


def inventory(roots):
    found, seen = [], {}
    for root in roots:
        for md in walk(root):
            try:
                fm = frontmatter(md.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
            name = fm.get("name") or md.parent.name
            plugin = plugin_of(md, root)
            if plugin is None and (md.parent / ".sumitcraft-install.json").exists():
                plugin = "sumitcraft"  # copied in by tools/install.mjs: same skill, no plugin namespace
            invoke_plugin = plugin if plugin_of(md, root) else None
            key = (name, plugin)
            if key in seen:
                seen[key]["also_at"] += 1
                continue
            stages, role, summary, src, known = classify(name, plugin, fm.get("description", ""))
            row = {"name": name, "plugin": plugin, "invoke": f"{invoke_plugin}:{name}" if invoke_plugin else name, "stages": stages, "role": role,
                   "summary": summary, "from": src, "known": known, "location": root_label(md, root), "also_at": 0}
            seen[key] = row
            found.append(row)
    return found


def root_label(md, root):
    try:
        rel = md.parent.relative_to(root)
    except ValueError:
        rel = md.parent
    r = str(root).replace(str(Path.home()), "~")
    label = f"{r}/{rel.parts[0] if rel.parts else ''}".replace("\\", "/")
    return re.sub(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}[0-9a-f_-]*", "<id>", label)  # account/org ids stay private


def plan(task, rows):
    t = task.lower()
    want = [s["id"] for s in STAGES["stages"] if any(kw in t for kw in s["keywords"])]
    if not want:  # a design task with no stage words: direction -> build -> critique -> accessibility
        want = ["direction", "build", "critique", "accessibility"]
    steps = []
    for st in ORDER:
        if st not in want:
            continue
        cands = [r for r in rows if st in r["stages"]]
        if not cands:
            steps.append({"stage": st, "label": LABEL[st], "primary": None, "evidence": None, "alternatives": [], "note": "no installed skill covers this stage; do it directly"})
            continue
        doers = [r for r in cands if r["role"] in ("make", "judge", "guide", "unknown")]
        meas = [r for r in cands if r["role"] == "measure"]
        rank = lambda r: (r["role"] != ("make" if st in ("build", "copy", "handoff", "visual-assets", "brand") else "judge"), not r["known"], r["plugin"] is None, r["name"])
        doers.sort(key=rank)
        primary = doers[0] if doers else meas[0]
        evidence = next((m for m in meas if m is not primary), None)
        alts = [r["invoke"] for r in doers[1:]]
        steps.append({"stage": st, "label": LABEL[st], "primary": primary["invoke"], "evidence": evidence["invoke"] if evidence else None,
                      "alternatives": alts, "note": f"{len(cands)} installed skills cover this stage" + ("; pick one, do not run them all" if len(doers) > 1 else "")})
    return {"task": task, "stages": want, "steps": steps}


def main():
    a = sys.argv[1:]
    roots = [] if "--no-default-roots" in a else default_roots()
    roots += [Path(a[i + 1]) for i, x in enumerate(a) if x == "--root"]
    rows = inventory(roots)
    design = [r for r in rows if r["stages"]]
    by_stage = {st: [r for r in design if st in r["stages"]] for st in ORDER}
    out = {"tool": "sumitcraft design-hub", "roots_scanned": [str(r).replace(str(Path.home()), "~") for r in roots if r.is_dir()],
           "skills_seen": len(rows), "design_skills": design,
           "overlaps": {st: [r["invoke"] for r in v] for st, v in by_stage.items() if len(v) > 1}}
    task = a[a.index("--task") + 1] if "--task" in a else None
    if task:
        out["plan"] = plan(task, design)
    if "--json" in a:
        Path(a[a.index("--json") + 1]).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"{len(design)} design skills found among {len(rows)} installed skills ({', '.join(out['roots_scanned'])})\n")
    for st in ORDER:
        v = by_stage[st]
        if not v:
            print(f"{LABEL[st]}: none installed"); continue
        print(f"{LABEL[st]}:")
        for r in v:
            print(f"  {r['invoke']:42} {r['role']:8} {r['summary'][:70]}{'' if r['known'] else '  [classified by keywords]'}")
    if out["overlaps"]:
        print("\nOverlaps (same stage, several skills): " + "; ".join(f"{LABEL[s]} x{len(v)}" for s, v in out["overlaps"].items()))
    if task:
        print(f"\nMerged plan for: {task}")
        for i, s in enumerate(out["plan"]["steps"], 1):
            line = f"  {i}. {s['label']}: " + (s["primary"] or "(none installed)")
            if s["evidence"]:
                line += f"  + evidence: {s['evidence']}"
            if s["alternatives"]:
                line += f"  (alternatives: {', '.join(s['alternatives'][:3])})"
            print(line)


if __name__ == "__main__":
    main()
