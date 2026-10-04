# B01-02 binary-reward GRPO: research conclusions

**This study provides preliminary evidence that NAME learns faster, but no consistent advantage at the training endpoint.** The setting is Qwen2.5-14B-Instruct, fixed L2, 3 paired seeds, and strict full-trajectory binary rewards. All 6 main runs completed 100 updates and every scheduled validation and endpoint evaluation. These findings are not generalized to a universal identity mechanism or real-agent capability.

## Did training work, and was the endpoint better?

The fresh test set has 512 examples per condition. step0 is the original model, explicitly shared as a baseline across seeds.

| Condition | step0 | step100 mean±seed sample SD | Mean gain over condition-specific step0 |
|---|---:|---:|---:|
| STEP | 51.17% | 98.76% ± 1.14 pp | +47.59 pp |
| NAME | 49.61% | 99.15% ± 0.30 pp | +49.54 pp |

Per-seed NAME−STEP endpoint differences are **+1.95, −0.78, and 0.00 pp**, with mean **+0.39 pp** and sample SD **1.41 pp**. One seed is positive, one negative, and one tied. These results do not establish a consistent final-accuracy improvement for NAME. Three seeds with nearly saturated endpoints also cannot establish equivalence. NAME's mean learning gain is larger by 1.95 pp, partly reflecting its 1.56 pp lower step0 baseline; gain magnitude cannot replace an endpoint comparison at the same budget.

## Did it learn faster?

Each cell below gives the first update count reaching a fixed validation threshold, ordered by seeds 301/302/303.

| Validation threshold | STEP | NAME | Seeds where NAME was earlier |
|---|---|---|---:|
| 60% | 20 / 30 / 20 | 20 / 20 / 20 | 1/3 |
| 70% | 30 / 30 / 30 | 20 / 20 / 30 | 2/3 |
| 80% | 40 / 40 / 30 | 30 / 30 / 30 | 2/3 |
| 90% | 50 / 40 / 40 | 40 / 40 / 40 | 1/3 |

The remaining seeds reached the threshold at the same checkpoint; every threshold was eventually reached. In particular, NAME seed303 scored 179/256=69.92% at step20, below 70%. Under the frozen threshold it is recorded as step30, without rounding it into a pass.

The supplementary full-curve descriptive statistic, trapezoidal area/100, favors NAME for all three paired seeds, with differences of **+4.84, +1.54, and +1.54 pp**. Mean values are 86.99% for NAME and 84.35% for STEP. STEP is higher at some late checkpoints, so NAME does not dominate throughout training. Taken together, the thresholds and curves support a limited early-learning speed benefit, with three seeds still constituting preliminary replication.

For the two seeds that reached 70% earlier, NAME used 20 rather than 30 updates, or 2560 rather than 3840 candidates. Measured cumulative sampling/update GPU time fell by approximately 32.4% and 33.2%. Both conditions took 30 steps for the third seed, with essentially the same time. These timings exclude initialization, saving, and validation and must be distinguished from whole-run allocated GPU time.

## What do the error changes show?

The clearest difference accompanies an earlier decrease in operation-expansion/order errors. At step20, as an example from the early curves, mean operation-sequence errors across three seeds were 46 for STEP and 7 for NAME per 256 validation examples, versus 59 and 39 at step0. Numerical errors were 84 and 112 at step0, and 62 and 68 at step20: NAME started with more numerical errors, and both conditions reduced errors substantially through training. See [REPORT.md](REPORT.md) for every fixed-checkpoint error curve. These overlapping flags cannot be summed into a causal decomposition or directly establish internal attention or credit-assignment mechanisms.

Endpoint errors are almost all numerical, with one missing-operation case and one incorrectly copied final Answer for STEP. All 49/4 heading violations for NAME seeds 302/303 are extra `Trace:` headings; the tool names and order are correct. The original scorer allows generic heading lines, so strict scores are unaffected and heading compliance is reported separately. Examples and complete categories are in [CASE_REVIEW.md](CASE_REVIEW.md). All main training candidates and evaluation outputs ended with EOS, with no generation-cap truncations.

## Costs and implementation

Each condition sampled 38400 main responses. STEP generated 2,551,654 tokens and NAME 2,550,930, a difference of −0.03%, effectively the same. Across three runs, allocated GPU time including process startup, model loading, and saving was 6.954 hours for STEP and 7.049 for NAME, about 1.36% more for NAME. step100 test output tokens totaled 101,000 and 101,116, about 0.11% more for NAME; measured generation time was about 0.71% longer. These are measurements on this hardware; equal updates are not treated as equal compute.

Main training totaled 14.003 GPU-hours. Actual evaluation-task wall time totaled 1.550 GPU-hours, including 1.503 GPU-hours of generation. Evaluation-worker lifecycles occupied 5.005 GPU-hours, including checkpoint waiting, which must not be counted as active inference. Timed prechecks and recovery totaled 1.711 GPU-hours. Complete durations are unavailable for two initial argument-parsing failures and infrastructure diagnostics; these are disclosed separately, without inventing total GPU-kernel activity time. See [COMPLETION_AUDIT.md](COMPLETION_AUDIT.md) for accounting definitions.

Both conditions learned the task successfully with binary rewards; binary rewards did not fail overall. Approximately 14%–18% of example groups in each run had mixed 0/1 rewards. Remaining all-0/all-1 groups were retained under the original protocol. Despite substantial sampling duplication, enough learning signal was available. Occasional KL/gradient peaks were not used as reasons to stop training. Complete curves and finite-value records support the absence of sustained optimization collapse. Numerical nondeterminism in precheck recovery was fixed before main training; main runs had no interruptions or configuration changes.

The most appropriate statement is: **On a supplied-plan, fixed-L2 symbolic execution task, NAME shows an early GRPO learning-efficiency benefit over STEP; final success is nearly saturated, and endpoint advantages are inconsistent.** Method gains, format compliance, and mechanism hypotheses should be stated separately. Transfer across models, longer call chains, mathematics, or real execution tasks remains unestablished, as does paper novelty.

For follow-up, retain this binary-reward baseline and prioritize testing whether the learning-speed benefit transfers to harder practical execution tasks. There is currently no evidence that internal rewards are required because binary rewards failed. Learned prompt optimization, fine-grained rewards, additional models, and practical tasks require separate protocols. This study was neither automatically expanded nor publicly released.
