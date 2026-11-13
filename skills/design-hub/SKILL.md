---
name: design-hub
description: The front door to every design skill installed on this machine, not only SumitCraft's. Finds the design skills present (global, plugin, project and cloud-image folders: design-plugin skills like critique, handoff, ux-copy and accessibility review; frontend-design, ui-taste, impeccable, shadcn, GSAP, Figma and art skills; SumitCraft's own), sorts them into design stages (research, direction, brand, system, build, motion, copy, accessibility, critique, inspection, handoff, visual assets), shows where several overlap, and merges them into one plan for the task, pairing each step with a SumitCraft check that produces evidence. Use when the user asks for design work that spans stages ("design and polish this page", "make it accessible and animate it"), asks "which design skill should I use", or has many design skills installed and wants one workflow. For a single clear design task, the matching skill can be used directly.
---

# Design hub

People install design skills from many places: a design plugin, a frontend-taste pack, an animation library's
official skills, Figma, SumitCraft. Several cover the same stage in different ways, and none knows the others exist.
This skill finds what is actually installed, decides which one does each stage, and adds measurement where taste
alone is not enough. It never copies or edits another skill; it calls them by name.

`<skill>` is the folder with this SKILL.md. Python 3.9+, standard library, read-only.

## Steps

1. **Find what is installed** (run it every time; installs differ between machines, users and cloud images):
   ```
   python <skill>/scripts/find_design_skills.py --task "<the user's request in their words>"
   ```
   It lists every design skill by stage with its role (make, judge, guide, measure), reports overlaps, and prints a
   merged plan: for each stage the request touches, a primary skill, a SumitCraft evidence check, and alternatives.
   Skills it does not know are classified from their own descriptions and marked "[classified by keywords]": read
   their SKILL.md before trusting the label.
2. **Decide the plan with the user** when it has more than two stages or a real taste choice. Show it like:
   ```
   Task: polish the pricing page, make it accessible, add a menu animation
   Plan: design:design-critique (findings) -> design:accessibility-review (WCAG issues)
         -> emil-design-eng (motion judgement) ; evidence: sumitcraft:design-critique (before/after pixels),
         sumitcraft:interaction-motion-study (keyboard, focus, reduced motion)
   Why not impeccable for critique: overlaps; one critic is enough
   ```
3. **Run each stage with one skill.** Load the primary skill with the Skill tool and follow it fully. When two skills
   overlap, pick by input: mockups, screenshots or Figma links suit the design plugin's critique; a rendered page in a
   repo suits SumitCraft's critique (it measures before/after). Never run three critics on the same screen and merge
   their opinions into mush.
4. **Back every claim with the evidence step**: contrast and token checks (`design-system-build`), spec mismatches
   (`design-to-code-inspection`), before/after pixels (`design-critique`), keyboard and reduced motion
   (`interaction-motion-study`). A finding that cannot be measured stays labelled as judgement.
5. **Hand over** in one place: what each skill did, the evidence, what is still a taste decision for the user, and
   which installed skills were available but not used (so they know).

## Merge rules

- One skill per stage. Others are alternatives, not extra passes.
- Order follows the work: research, direction, brand, system, build, motion, copy, accessibility, critique,
  inspection, handoff. Visual assets slot in wherever they are needed.
- A brand skill made for one company's own look (for example a skill that applies its maker's brand) is used only for
  that company's work.
- Safety and cost rules of each skill still apply inside the plan (image-gen's spend gate, Figma's required first step).
- If a stage has no installed skill, say so and do that stage directly; do not pretend a skill covered it.

## Example

`examples/fixture-home/` is a fake skills folder (a "design" plugin, a GSAP skill, an unknown palette skill, two
non-design skills, and a copy-installed SumitCraft skill). `tests/test_design_hub.py` checks the known answers:
plugin names, overlaps, exclusions, and the merged plan.

Contract, prerequisites and validation status: [contract.md](contract.md).
