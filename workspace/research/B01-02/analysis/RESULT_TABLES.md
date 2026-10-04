# Measured results

All percentages report accuracy or percentage-point differences, not relative improvements. OOD contains 384 examples from 96 independent program compositions. Training seeds are 11/22/33.

## Main experiment

| Condition | Mean IID | OOD seeds 11/22/33 | Mean OOD | Mean stress-set accuracy | Effective training target tokens per run | Mean generated tokens/example |
|---|---:|---|---:|---:|---:|---:|
| flat | 100.00 | 0.26 / 0.00 / 0.00 | 0.09 | 0.69 | 1,055,432 | 67.1 |
| macro | 100.00 | 30.73 / 37.76 / 20.83 | 29.77 | 36.11 | 1,055,432 | 90.7 |
| natural | 100.00 | 0.00 / 0.00 / 0.26 | 0.09 | 0.00 | 1,312,060 | 85.5 |
| shuffled | 100.00 | 1.04 / 1.04 / 0.00 | 0.69 | 4.86 | 1,055,432 | 71.1 |

## Interventions

| World | Mean IID | OOD seeds 11/22/33 | Mean OOD |
|---|---:|---|---:|
| original | 100.00 | 30.73 / 37.76 / 20.83 | 29.77 |
| renamed | 100.00 | 30.99 / 44.27 / 51.56 | 42.27 |
| semantic | 100.00 | 60.42 / 28.91 / 45.31 | 44.88 |

## Post hoc alignment controls

| Boundary label | Mean IID | OOD seeds 11/22/33 | Mean OOD | Effective training target tokens per run |
|---|---:|---|---:|---:|
| stable | 100.00 | 31.25 / 45.57 / 7.55 | 28.12 | 1,055,432 |
| call | 100.00 | 11.20 / 20.83 / 21.88 | 17.97 | 1,055,432 |

## Post hoc external-routing diagnostic

An external loop calls macros individually; the model supplies every intermediate state. This cannot replace autonomous-execution results. Each evaluation uses 96 independent programs.

| Model | Accuracy by seed | Mean |
|---|---|---:|
| flat | 100.00 / 100.00 / 100.00 | 100.00 |
| macro | 100.00 / 100.00 / 100.00 | 100.00 |
| frozen | 0.00 | 0.00 |

## Frozen baselines

| Prompt | IID | OOD | Stress set |
|---|---:|---:|---:|
| no-library | 0.00 | 0.00 | 6.25 |
| with-library | 0.00 | 0.00 | 0.00 |

## Primary statistics

```json
{
  "seed_differences": [
    0.3046875,
    0.3776041666666667,
    0.20833333333333334
  ],
  "mean_difference": 0.29687500000000006,
  "seed_t_interval_95": [
    0.08595824752326159,
    0.5077917524767386
  ],
  "descriptive_ast_bootstrap_95": [
    0.22133246527777778,
    0.37152777777777773
  ],
  "n_seeds": 3,
  "passes_screen": true,
  "warning": "n=3; AST interval conditional on trained checkpoints; zero-variance t interval omitted."
}
```
