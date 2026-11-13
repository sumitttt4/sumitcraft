# Cross-skill chains

Every skill works on its own. A chain is worth it only when the work has distinct stages and each stage hands a
concrete artifact to the next. "Demonstrated" means the handoff ran in this repository (evidence linked); "proposed"
means it is a sensible plan that has not been run end to end here.

| Chain | Handoff artifact | Status |
|---|---|---|
| brand-kit → vox-explainer | `brand.json` (palette, fonts, edges) → vox theme; the board renders two vox frames in the brand's look | **Demonstrated** with a fictional brand: [evidence/brand-kit/board.png](../evidence/brand-kit/board.png) |
| design-critique → design-system-build | contrast evidence measured with `tokens.py --pair`; the fix becomes a token decision | **Demonstrated**: [evidence/design-critique/run.log.txt](../evidence/design-critique/run.log.txt) |
| code-loop → work-to-explanation | render manifest and check output → an evidence-linked case study that passes preflight | **Demonstrated**: [skills/work-to-explanation/examples/webgl-backend-case-study/draft.md](../skills/work-to-explanation/examples/webgl-backend-case-study/draft.md) |
| design-hub → (installed design skills) + SumitCraft checks | a merged plan: one installed skill per stage, plus a SumitCraft evidence check | **Demonstrated as a plan** on this machine's 107 installed skills: [evidence/design-hub/this-machine.json](../evidence/design-hub/this-machine.json); the plan's steps were not executed end to end |
| visual-reference-analysis → design-system-build | measured palette and value structure → candidate tokens the user chooses between | Proposed |
| design-system-build → design-to-code-inspection | tokens become the spec's expected colours and sizes | Proposed |
| rough-cut → clean-audio → vox-explainer | `edl.json` and cleaned clips → `verify_vN_words.json` as `--words` for the explainer | Proposed (blocked here: speech model not downloaded) |
| reverse-engineer-video → code-loop or perspective-illusion | `breakdown.json` cut times and camera paths → keyframes | Proposed (upstream chain) |
| paper-to-runnable → vox-explainer | mechanism animation and measured numbers → beats | Proposed (upstream chain) |
| benchmark-honestly → bisect-anything | a trustworthy slowdown oracle → `bench_oracle.py` thresholds | Proposed (upstream chain) |
| codebase-map → flaky-test-killer | the traced path and hotspots → which tests to measure first | Proposed (upstream chain) |
| learn-a-domain → teach-back | the learner's plan and prediction log → gap-finding questions | Proposed |

skill-router plans chains like these at run time from the installed skills' descriptions; see its SKILL.md.
