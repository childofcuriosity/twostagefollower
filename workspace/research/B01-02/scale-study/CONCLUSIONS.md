# Model scale and long execution after short-task training: stage-one results

Stage-one scale validation is complete and awaits user review. All planned training, frozen/fixed-checkpoint evaluations, independent confirmation, and learning-rate/Instruct supplements have ended. Coverage, example-level computation, and hash checks passed for 174 raw-output files containing 95,200 records. These are controlled-task findings, not a claim of paper readiness or validated real-agent methods.

## What was tested

Models are Qwen2.5 Base 1.5B, 3B, 7B, and 32B. Given four numbers and a sequence of tool names, the model outputs the numbers after each primitive operation, then a final answer. Nine tools compose six deterministic primitives; an interpreter recomputes every answer exactly. This is controlled text execution, not extended interaction by a real coding agent.

Training conditions differ only in trajectory-segment headers: flat always writes `step:`, while macro writes the current tool name. Inputs, operations, answers, example order, and target-token counts are paired. This is a training intervention, not a prompt added at inference. Of 4,096 training examples, approximately 90.38% require two calls and the remainder one. Settings are fixed at 512 steps, effective batch 32, LoRA rank 16/alpha 32, learning rate 3e-4, and seeds 11/22/33 per condition. The original 560 tests contain 128 short examples, 384 unseen 3–5-call examples, and 48 stress examples. A separate 480-example confirmation set covers 3/4/5/6/8 calls.

“Early answer after a correct prefix” requires every emitted operation and number to be correct, followed by an answer equal to the current state before all required operations are completed. This reliably identifiable subset excludes termination after earlier errors. Also retain stopping after exactly two correct tools, segment counts, wrong operations, arithmetic errors, and generation-limit evidence. These metrics are not interchangeable.

## Scale: the user concern is partly supported

Means over three training seeds on the original 384 long-call examples:

| Base model | Flat answer accuracy | Macro answer accuracy | Flat early answer after correct prefix | Macro early answer after correct prefix | Flat early answer after exactly two tools |
|---|---:|---:|---:|---:|---:|
| 1.5B | 0.09% | 29.77% | 87.59% | 43.23% | 86.89% |
| 3B | 0.09% | 60.76% | 89.15% | 20.57% | 88.19% |
| 7B | 18.06% | 58.94% | 58.68% | 26.39% | 23.00% |
| 32B | 44.36% | 73.70% | 38.37% | 21.70% | 0.26% |

The 32B model rarely stops mechanically after two tools, so the fixed two-segment behavior in small models does not generalize unchanged to tens of billions of parameters. Longer tasks remain difficult and name-label gains persist. At 3/4/5 calls, 32B flat answer accuracy is 94.79%/33.07%/5.21%, versus 96.09%/73.18%/51.82% for macro.

Across seeds, 32B macro−flat answer gains are 23.18, 26.04, and 38.80 percentage points, averaging 29.34, with a three-seed t interval of [8.68,50.00]. Correct-prefix early-answer rates do not improve in all seeds; the interval for the mean −16.67-point difference crosses zero. Not all accuracy gains can be attributed to reduced early stopping; operation errors also change.

## Independent confirmation: gains persist, but length extrapolation remains limited

The independent set was frozen before formal results were visible. Each length contains 24 independent programs and four inputs per program, excluding exact affine functions in the original train/dev/test sets. Numeric variants of one program are not counted as independent programs.

| Required calls | 32B flat complete-trajectory accuracy | 32B macro complete-trajectory accuracy |
|---|---:|---:|
| 3 | 87.85% | 94.10% |
| 4 | 35.42% | 71.53% |
| 5 | 4.17% | 57.99% |
| 6 | 0.69% | 32.64% |
| 8 | 0.00% | 24.65% |

Name-label gains extend beyond original test programs but do not establish unlimited length generalization. At eight calls, macro has a higher correct-prefix early-answer rate than flat (41.32% versus 17.71%) alongside higher completion. Flat often encounters other errors earlier, reducing the correct-prefix metric. A decrease in that metric alone can therefore misrepresent method quality.

## Learning rate, definitions, and instruction tuning change the interpretation

Reducing the 32B learning rate from 3e-4 to the preregistered 1e-4 changes original long-task flat/macro accuracy from 44.36%/73.70% to 30.38%/55.56%. Correct-prefix early answers decrease in both groups, yet overall accuracy also falls. A lower learning rate is not a validated fix for this task.

With tool definitions supplied, low-learning-rate 32B flat/macro accuracy is 87.50%/79.17%, reversing the name advantage; at the original learning rate it is 63.54%/71.96%. Tool names are therefore not always better: effects depend on training dose and inference information. Supplying definitions is an additional test condition, distinct from the original no-definition protocol.

32B-Instruct uses the official chat template consistently in training and testing. Without definitions, flat/macro accuracy is 34.64%/65.19%; with definitions, 57.47%/59.11%. Instruction post-training does not automatically eliminate the difference. Base and Instruct differ in templates and weight history, preventing attribution solely to prior stability. Low-learning-rate 3B runs use a 5090 versus PRO6000 for original 3B, introducing hardware confounding. Both 32B learning-rate groups use PRO6000.

Frozen 7B/32B and 32B-Instruct produce no correct original long-task answers under this prompt and strict-answer protocol even with definitions. Frozen models at every scale also produce no fully correct independent-confirmation trajectories. This does not establish generally poor execution or a premise of preexisting capability damaged by fine-tuning. Evidence mainly supports structural-generalization differences after short-task training.

## Training intensity and scoring limits

| Model | Trainable LoRA parameters | Share of total parameters including adapter |
|---|---:|---:|
| 1.5B | 18,464,768 | 1.1820% |
| 3B | 29,933,568 | 0.9607% |
| 7B | 40,370,176 | 0.5273% |
| 32B | 134,217,728 | 0.4080% |

Equal steps, examples, and rank do not imply equal FLOPs or proportional weight perturbation. Within-family scale associations are not randomized experiments changing only parameter count.

Full review of 13,440 main-test outputs finds 6,772 with correct answers and prescribed trajectories, 23 with different trajectories equivalent to the target function on every input, and 32 with correct answers only by coincidence on the current input. The 13,440 independent-confirmation and 21,280 supplementary outputs receive the same classification in `analysis/outcome-diagnostics.jsonl`. Equivalence uses complete affine signatures rather than random input sampling. Broader early-answer counts and complete segment-count distributions are in [STOPPING_DIAGNOSTICS.md](STOPPING_DIAGNOSTICS.md). Primary tables retain strict prescribed-trajectory scores and separately report final-answer scores; chance-correct answers are not complete execution.

Old generation records retain non-EOS token counts but no final token IDs, with a shared EOS/PAD ID. Stop evidence therefore distinguishes cap exhaustion, boundary ambiguity, and inferred EOS before the cap. It does not directly log every underlying termination reason.

The plan proposed mastery-matched checkpoints selected using a predefined short-development threshold, but registration omitted its numeric value. A threshold chosen after observing results cannot become preregistered. Explicitly exploratory 90%/95%/99% threshold sensitivity analyses retain every threshold and select checkpoints without test scores. They do not repair the original preregistration omission.

At the 95% threshold, both labels and all three seeds for 7B/32B first select step 64. Long-task flat/macro accuracy is then 13.37%/55.73% for 7B and 35.24%/55.38% for 32B. Name gains appear when both groups have mastered short tasks, but wide three-seed intervals do not exclude every learning-speed explanation. In particular, 32B macro correct-prefix early answering is 38.72%, above flat at 31.77%, again separating accuracy gains from this stopping subset. See all thresholds and seeds in `analysis/mastery-diagnostics.json`. At 99%, only 32B flat seed 33 shifts its first qualifying checkpoint to step 128; all others remain at step 64. Complete comparisons are saved.

## Interpretation and recommended next steps

In this controlled execution task fine-tuned on short call sequences, outputting tool identity is associated with better long-composition completion. Paired training permits testing the label intervention, and gains persist at 32B and on independent programs. Scale substantially reduces fixed two-segment stopping but does not eliminate longer-composition failures.

The study does not establish that repeating plans prevents Codex from stopping midway, that failures reflect missing innovation ability, that training damages preexisting long-task capability, or that tool names act only through stopping behavior.

For the next stage, establish an executable baseline on real interactive tasks with a strong instruction model, then compare a common marker, current tool identity, position/remaining-count markers, and irrelevant length-matched labels. Measure completion, wrong operations, premature stopping, repeated unproductive actions, and token costs separately. Verify that the baseline exhibits the stopping problem of interest and that interventions do not alter the question by adding budget or changing tasks. Proceed to real-agent experiments after user review of the complete results.

Evidence: `analysis/results.json`, `analysis/paired-inference.json`, `analysis/extended-results.json`, `analysis/matched-context.json`, `SUPPLEMENT.md`, and `analysis/supplement-results.json`. The [main report](REPORT.md), [acceptance matrix](COMPLETION_AUDIT.md), and [fixed training curves](figures/learning-curves.png) are complete. Recorded process durations total approximately 59.61 GPU-hours, including some waiting rather than only kernel activity; see `analysis/cost.json`. All raw trajectories, adapters, failures, and environments remain in the project.
