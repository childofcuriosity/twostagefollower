# B01-02 GRPO length scaling: conclusions

All 36 main runs, fixed-checkpoint evaluations, and record-level audits are complete. **14B, L5 is the only setting in this study within the preregistered 20%–90% STEP endpoint validation window.** It leaves room for learning while showing a clear benefit from NAME training. Substantial gains were also observed at 7B, L3 and 14B, L6, although STEP success remained low.

The primary metric is strict full-trajectory success. The table reports three-seed means ± sample SD on 512 fresh test examples per setting; differences are in percentage points. STEP and NAME have different original-model prompt baselines, so the difference in learning gains relative to step0 is also reported to separate existing prompt differences from training gains.

| Setting | STEP step0→100 | NAME step0→100 | NAME−STEP endpoint difference, mean±SD | Difference in learning gains |
|---|---:|---:|---:|---:|
| 7b-L3 | 3.91%→8.27% ±0.60pp | 7.23%→32.75% ±3.72pp | +24.48 ±4.30 | +21.16 |
| 7b-L4 | 0.78%→0.91% ±0.11pp | 2.93%→4.17% ±0.30pp | +3.26 ±0.23 | +1.11 |
| 7b-L5 | 0.00%→0.00% ±0.00pp | 0.98%→0.85% ±0.30pp | +0.85 ±0.30 | -0.13 |
| 14b-L5 | 5.47%→32.94% ±8.91pp | 10.55%→70.77% ±14.80pp | +37.83 ±8.40 | +32.75 |
| 14b-L6 | 2.93%→4.56% ±0.49pp | 5.66%→38.74% ±15.69pp | +34.18 ±15.23 | +31.45 |
| 14b-L7 | 0.78%→0.72% ±0.23pp | 3.52%→7.29% ±1.19pp | +6.58 ±0.98 | +3.84 |

![Length curves before and after training](figures/test-success-vs-length.png)

## Suitable difficulty and limits of the gains

At 14B, L5, STEP endpoint validation success was 26.95%, 35.55%, and 44.14%, averaging 35.55%. This setting was selected by the preregistered baseline-difficulty rule, not by the size of NAME's advantage. NAME test endpoints were 53.71%, 78.32%, and 80.27%, versus 24.41%, 32.23%, and 42.19% for STEP; paired differences were +29.30, +46.09, and +38.09 percentage points. NAME improved by an average of 60.22 points over its own step0, versus 27.47 for STEP, giving a learning-gain difference of +32.75 points.

At 7B, L3, mean NAME test success was 32.75%, versus 8.27% for STEP, with a learning-gain difference of +21.16 points. At 14B, L6, the corresponding values were 38.74% and 4.56%, with a learning-gain difference of +31.45 points. NAME's three L6 seeds scored 29.10%, 30.27%, and 56.84%, showing substantial variation; reporting only the best seed would be misleading. Neither setting meets the study's STEP 20%–90% candidate window, which is retained unchanged.

7B, L4 and 14B, L7 have positive endpoint differences but still low overall success. At 7B, L5, STEP remains at 0%, while NAME moves from 0.98% at step0 to 0.85%, with no observed learning improvement. All 18 endpoint paired differences across the six settings are positive, but this does not establish training gains in all six settings.

## Does learning become faster?

The [full report](REPORT.md) contains all 36 fixed validation curves and the preset 60%/70%/80%/90% thresholds. At 14B, L5, NAME seeds 302 and 303 first reached 60% at step70 and first reached 70% at step90 and step80, respectively. NAME seed301 and every STEP run failed to reach 60% within 100 steps. No setting reached the 80% or 90% validation thresholds. A test endpoint above 80% does not count as reaching the validation threshold.

The complete curves support improved NAME learning at 7B L3 and 14B L5/L6. For STEP runs that never reach a threshold, no step count can be assigned to claim a speedup factor. Matching 100 updates matches example and sampling budgets, not compute.

![All fixed validation learning curves](figures/all-learning-curves.png)

## Errors and low-success settings

Across 512 endpoint examples at 14B, L5, the mean operation-sequence mismatch count fell from 197 for STEP to 50.33 for NAME, while local numerical errors fell from 229.33 to 112. The corresponding changes were 352.33→112.33 and 415.33→252 at 14B, L6, and 324.67→113.33 and 390.67→300.33 at 7B, L3. These flags can overlap and must not be summed into a failure count. The gains involve both operation expansion and numerical execution, rather than heading format or reduced early stopping alone.

At 7B, L5, only 0.23% of STEP candidate groups and 0.75% of NAME groups had differing rewards within an example; mean training rewards were 0.08% and 0.25%, respectively. Under binary rewards and the 100-update budget, the learning signal was extremely sparse. Failure to learn here is neither an implementation interruption nor evidence that other budgets or methods cannot learn the task. Fewer than 1% of STEP groups at 7B, L4 had differing rewards as well. All zero-reward groups and low-scoring seeds were retained, with no added local rewards or best-of-retry selection.

Heading compliance is counted separately: an extra Trace heading, for example, is not an extra tool call. Raw operation counts are also distinct from high-level tool-call counts. Each setting's CASE_REVIEW.md provides mutually exclusive interpretation categories, heading boundaries, and raw/reference trajectory examples selected by the smallest example ID. Classification by category priority is not temporal first-error attribution.

## Outputs and costs

Precheck, main-training, and evaluation workers occupied a total of 136.00 GPU-hours: 108.77 for main training, 21.36 for evaluation, and 5.87 for prechecks and recovery. These totals include startup and waiting. Main training generated 460800 candidates and 67172424 output tokens; scheduled evaluations actually generated 119808 responses and 17552357 output tokens. All 9 training truncations and 2 evaluation truncations were retained; other responses ended with EOS. EOS does not indicate successful execution.

For the focal 14B, L5 setting, NAME used 2.74% fewer training output tokens and 4.24% less training-segment GPU time after NCCL initialization than STEP. At step100, greedy test outputs averaged 149.52 versus 151.87 tokens, a 1.55% reduction, with 5.04% less measured generate time. Other settings showed different endpoint output/time changes: at 14B L7, NAME generated 1.37% more tokens and took 6.74% more generate time. These are timings from this study, not general speedup rates. See [COSTS.md](COSTS.md) for all components, nested timing definitions, and per-setting data.

## Strength of evidence and next steps

The evidence supports better NAME learning at 7B L3 and 14B L5/L6 under the supplied-call-plan, nine-tool numerical execution task and fixed binary-GRPO budget used here. 14B L5 is the preferred difficulty for a later independent confirmation. Three seeds constitute preliminary replication; the six settings were selected by the user for exploration, and the selected setting is not a new independent confirmation. The two L5 models share underlying data; the other lengths do not form a fully crossed model comparison.

Tool names may help locate steps, expand operations, or supply semantic cues. This study does not distinguish these mechanisms or establish an identity concept, an attention mechanism, or general prompt-only effectiveness. It includes no POSITION/ALIAS controls, internal rewards, additional models/lengths, or real tasks, and does not establish novelty or transfer to real agents. Further reward or transfer studies should have separate protocols and retain these binary-reward results. No follow-up experiments were started automatically.

Deliverables: [full results](REPORT.md), [costs](COSTS.md), [methods and verification](METHOD.md), and [itemized completion audit](COMPLETION_AUDIT.md). All raw data, candidates, checkpoints, evaluation outputs, and failure/scheduling records were retained in this directory in the original workspace. Model processes on all 16 GPUs had exited and GPU memory was cleared.
