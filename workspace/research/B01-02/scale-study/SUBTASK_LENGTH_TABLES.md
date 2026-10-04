# Long-task decomposition by scale and length

Independent confirmation: 24 programs × four inputs × three training seeds = 288 trajectories per scale and length. A covers every required call position, with missing names scored incorrect. B checks operations and numbers within emitted valid-name segments, excluding unobserved missing segments. Predictions aggregate existing five-fold program-held-out (pA*pB)^L estimates within length and seed. Actual whole-task scores require complete correct trajectories.

## qwen1.5b

| Calls | A: correct name | B: correct expansion | Product whole-task prediction | Actual name-condition whole task | Actual step whole task |
|---|---:|---:|---:|---:|---:|
| 3 | 82.06% | 99.59% | 56.03% | 52.43% | 0.00% |
| 4 | 71.09% | 96.24% | 22.25% | 21.18% | 0.00% |
| 5 | 55.35% | 96.48% | 4.35% | 5.90% | 0.00% |
| 6 | 47.40% | 92.38% | 0.86% | 0.69% | 0.00% |
| 8 | 36.81% | 85.66% | 0.01% | 1.04% | 0.00% |

## qwen3b

| Calls | A: correct name | B: correct expansion | Product whole-task prediction | Actual name-condition whole task | Actual step whole task |
|---|---:|---:|---:|---:|---:|
| 3 | 93.63% | 99.03% | 81.82% | 83.68% | 0.00% |
| 4 | 91.75% | 95.26% | 59.09% | 60.76% | 0.00% |
| 5 | 81.60% | 92.53% | 25.64% | 28.47% | 0.00% |
| 6 | 69.97% | 86.23% | 5.23% | 9.38% | 0.00% |
| 8 | 52.21% | 80.30% | 0.16% | 2.08% | 0.00% |

## qwen7b

| Calls | A: correct name | B: correct expansion | Product whole-task prediction | Actual name-condition whole task | Actual step whole task |
|---|---:|---:|---:|---:|---:|
| 3 | 95.60% | 98.57% | 85.00% | 86.81% | 60.76% |
| 4 | 90.54% | 95.07% | 56.05% | 52.08% | 0.00% |
| 5 | 77.85% | 92.21% | 21.12% | 23.61% | 0.00% |
| 6 | 73.96% | 91.63% | 11.01% | 22.57% | 0.00% |
| 8 | 56.81% | 78.99% | 0.28% | 0.00% | 0.00% |

## qwen32b

| Calls | A: correct name | B: correct expansion | Product whole-task prediction | Actual name-condition whole task | Actual step whole task |
|---|---:|---:|---:|---:|---:|
| 3 | 98.03% | 100.00% | 94.24% | 94.10% | 87.85% |
| 4 | 92.27% | 99.53% | 72.18% | 71.53% | 35.42% |
| 5 | 85.35% | 99.77% | 47.35% | 57.99% | 4.17% |
| 6 | 74.83% | 99.29% | 21.01% | 32.64% | 0.69% |
| 8 | 67.40% | 97.91% | 9.54% | 24.65% | 0.00% |
