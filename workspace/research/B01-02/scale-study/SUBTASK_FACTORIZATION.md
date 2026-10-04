# Single-tool decomposition and product predictions from existing trajectories

This offline analysis reads existing outputs without inference or training. It covers four Qwen2.5 Base scales and three seeds each: 10368 name-condition trajectories and 10368 corresponding step trajectories. Name outputs contain 48384 required call positions and 40119 emitted segments. Per model, the original test has 384 examples × three seeds and independent confirmation has 480 × three seeds. These trajectories are not all independent programs.

## Scoring and prediction

- A: the name in emitted position i equals the requested name at position i. Missing names fail; the denominator includes unfilled positions.
- B: after an emitted valid name, the full primitive sequence matches that name and numeric transitions are correct. A wrong selected name can still have correct B if expanded correctly. Numeric checks use the actual input state, not an oracle-correct state.
- B is unobserved for calls whose names were never emitted; these are neither successes nor failures. This survivor selection prevents direct interpretation as independent call accuracy.
- Primary prediction: estimate pA and pB within model, seed, and length, then predict (pA×pB)^L. Use five folds grouped by complete tool sequence, fitting on four folds and predicting the held-out fold. Numeric variants and all three seeds for a sequence share a fold.
- Sensitivity analyses multiply position-specific pA(L, i) by tool-specific pB(tool), then across calls, and separately retain products of position-specific joint success. Estimates depend on finite samples and conditioning; selecting the closest prediction cannot establish independence.
- The primary whole-task score requires the specified operation trajectory, every number, and the final answer, rather than only the answer. All 10368 reconstructed scores match existing strict scores. Extra segments, final answers, and formatting are checked. The product model does not separately fit final termination, a limitation of its scope.
- Minimal scoring checks cover a wrong name with correct expansion, a missing segment, within-tool truncation, and arithmetic errors.

## Original 3–5-call examples

| Model | Name accuracy per position | Correct expansion of emitted names | Complete name sequence correct | Simple product whole-task prediction | Actual name-condition whole task | Actual step whole task |
|---|---:|---:|---:|---:|---:|---:|
| qwen1.5b | 69.94% | 97.88% | 32.64% | 30.35% | 29.77% | 0.00% |
| qwen3b | 88.95% | 94.65% | 73.18% | 57.39% | 59.72% | 0.00% |
| qwen7b | 88.52% | 95.96% | 69.53% | 60.32% | 57.90% | 17.97% |
| qwen32b | 90.56% | 99.55% | 74.65% | 71.95% | 73.00% | 44.27% |

## 32B by length: simple and stratified products

| Dataset | Calls | Simple product | Position/tool-stratified product | Actual name condition | Actual step |
|---|---:|---:|---:|---:|---:|
| main | 3 | 96.32% | 94.61% | 96.09% | 94.79% |
| main | 4 | 72.95% | 69.20% | 73.18% | 32.81% |
| main | 5 | 46.60% | 43.44% | 49.74% | 5.21% |
| independent | 3 | 94.24% | 92.07% | 94.10% | 87.85% |
| independent | 4 | 72.18% | 68.62% | 71.53% | 35.42% |
| independent | 5 | 47.35% | 41.82% | 57.99% | 4.17% |
| independent | 6 | 21.01% | 15.53% | 32.64% | 0.69% |
| independent | 8 | 9.54% | 7.64% | 24.65% | 0.00% |

## Interpretation

On the original 3–5-call examples, simple product predictions differ from actual name-condition accuracy by approximately 0.6–2.4 percentage points. This aggregate agreement quantitatively supports the proposed two-part decomposition. For 32B, complete expansion after emitted names is approximately 99.6%, complete name-sequence accuracy 74.7%, and complete execution 73.0%. Descriptively, most loss concerns name-sequence completeness/selection rather than arithmetic after generated names.

On independent 32B confirmation at 5/6/8 calls, however, the simple product substantially underpredicts: 47.35/21.01/9.54% versus 57.99/32.64/24.65% actual accuracy. Agreement on the original test therefore does not establish general independence. Position/tool stratification still underpredicts. Failures may cluster within trajectories, including the structural dependence created by missing all subsequent names after early stopping, as well as program/state difficulty and selection on unobserved B. The approximation is useful at some lengths but does not identify independent internal learning.

The more stratified product predicts 22.83/52.59/55.47/69.09% across the four scales on the original test, versus 29.77/59.72/57.90/73.00% actual accuracy. Aggregate agreement depends on probability estimation; the more favorable formula cannot be shown alone.

Nameless step outputs contain no independently observable name-selection event, so equivalent A/B events cannot be manufactured from those trajectories. Their strict whole-task scores serve as baselines; operation segments are not treated as explicit name choices.

This is not an oracle experiment: names are not corrected and unperformed executions are not supplied. Oracle interventions are needed to measure those counterfactual capabilities.

## Auditable files

- `src/subtask_factorization.py`: raw-file reading, hash verification, segment scoring, and program-grouped cross-prediction.
- `analysis/subtask-factorization.json`: sources, seed/length metrics, summaries, and conditional bootstrap intervals. These resample programs with fixed prediction residuals, omit fitting uncertainty, and do not establish statistical equivalence.
- `analysis/subtask-factorization-segments.jsonl`: all names, primitives, states, and itemized A/B scores.
- `analysis/subtask-factorization-predictions.jsonl`: held-out predictions and outcomes per example.
- `analysis/subtask-factorization-checks.json`: scoring-boundary checks.
