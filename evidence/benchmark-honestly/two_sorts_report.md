# Benchmark report

**Verdict:** No clear difference between b and a: time ratio 1.027, 95% CI 0.954 to 1.081 includes 1.0 or the test disagrees (p=0.47). Do not claim a speedup. More runs or a quieter machine may narrow it.

## Warnings

- environment: Busy processes right now: python3 (22%).
- environment: Running inside a VM or container. Neighbours on the same host add noise.

## Results (wall time)

| Command | Median | 95% CI of median | p5 | p95 | Min | Max | MAD | CPU time (median) | Peak RSS (median) |
|---|---|---|---|---|---|---|---|---|---|
| `a` | 177.68 ms | 171.72 ms to 184.53 ms | 171.49 ms | 204.59 ms | 171.40 ms | 211.48 ms | 9.01 ms | 176.81 ms | 27.6 MiB |
| `b` | 182.41 ms | 172.71 ms to 186.67 ms | 170.44 ms | 209.93 ms | 168.86 ms | 218.02 ms | 11.62 ms | 181.21 ms | 27.6 MiB |

## Comparisons

| Candidate vs baseline | Time ratio | CI | Mann-Whitney p | Cliff's delta | P(candidate faster) | Floor subtracted |
|---|---|---|---|---|---|---|
| b vs a | 1.027 | 0.954 to 1.081 | 0.47 | 0.18 | 41% | no |

Time ratio = candidate median / baseline median. Below 1.0 means the candidate is faster. CI is a percentile bootstrap (5000 resamples).

## Commands

- `a`: `"/usr/local/bin/python3" "/home/user/sumitcraft/skills/benchmark-honestly/examples/two_sorts.py" a`
- `b`: `"/usr/local/bin/python3" "/home/user/sumitcraft/skills/benchmark-honestly/examples/two_sorts.py" b`

## Method

2 warmup and 12 measured runs per command, order: shuffled, seed 12345.

## Reproduce

```
python3 bench.py -n a -n b '"/usr/local/bin/python3" "/home/user/sumitcraft/skills/benchmark-honestly/examples/two_sorts.py" a' '"/usr/local/bin/python3" "/home/user/sumitcraft/skills/benchmark-honestly/examples/two_sorts.py" b' --runs 12 --warmup 2 --md /home/user/sumitcraft/evidence/runs/benchmark-honestly/report.md --json /home/user/sumitcraft/evidence/runs/benchmark-honestly/report.json --shell
```

## Environment

| Setting | Value |
|---|---|
| Captured | 2026-11-13 10:13:30 UTC |
| Host / user | vm / root |
| OS | Ubuntu 24.04.5 LTS (kernel 6.18.44-fc-v445), docker |
| CPU | Intel(R) Xeon(R) Processor @ 2.30GHz, x86_64 |
| Cores | 4 physical, 4 logical |
| SMT | off |
| CPUs allowed | 4 |
| Memory | 15.7 GB total, 95% free |
| Power | unknown |
| Load average (1/5/15 min) | 0.82 / 0.28 / 0.09 |
| Python | CPython 3.13.18 |

**Environment warnings**

- Busy processes right now: python3 (22%).
- Running inside a VM or container. Neighbours on the same host add noise.

**Not controlled on this OS**

- Pin with 'taskset -c N', set the governor to performance, disable turbo, and drop caches with 'echo 3 | sudo tee /proc/sys/vm/drop_caches' when you need cold-cache numbers. Note which of these you did.
