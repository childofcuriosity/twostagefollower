# Stage-one delivery acceptance

Acceptance follows the current goal, `../agent-completion-plan/SCALE_AMENDMENT.md`, and user instructions on workspace location, infrequent monitoring, retaining failures, and server use. This covers only approved stage one; real-agent experiments and new mechanism groups are not counted as complete.

| Requirement | Evidence and scope | Outcome |
|---|---|---|
| Freeze and fully download 32B | `models/qwen32b/download-manifest.json` fixes revision 1818d35814b8319459f4bd55ed1ac8709630f003 and per-file SHA; `analysis/qwen32b-remote-hash-audit.json` verifies 17 weight shards | Complete |
| Freeze same-family 7B reference and Instruct bridge | Respective download manifests; revisions d149729398750b98c0af14eb82c78cfe92750796 and 5ede1c97bbab6ce5cda5812749b4c0bdf79b18dd | Complete |
| Measure memory and throughput before formal training | `analysis/qwen7b-calibration.json`, `qwen32b-calibration.json`, and probe summaries; 32B microbatch 16/effective batch 32 works; report contains measurements | Complete |
| Three flat/macro seeds at 512 steps for each 7B/32B model | Six returncode-0 entries in each `*-completed.json`; verification checks continuous steps, finite values, and 16384 cumulative examples | Complete |
| Complete original 1.5B/3B comparisons | Original 24 main-test groups × 560 = 13440 outputs; paths/hashes in results and verification; no conditioning on macro success/flat failure | Complete |
| Paired data, training dose, and tokens | Registered data hashes unchanged; all 4096 examples pass token checks; counts pair across 12 new main runs; gradient checkpointing preserves microbatch 16 | Complete; equal steps do not imply equal FLOPs or LoRA proportion |
| Every fixed checkpoint 0/16/64/128/256/512 | Twelve groups × six intermediate adapters plus final copies: 84 file hashes; final copies equal step 512; all 560 examples tested at every step for all seeds | Complete |
| Short/long task, trajectory, and stopping curves | results.curves contains 180 split/checkpoint records; step 512 is primary; learning-curves.png/svg/pdf and segment-distribution CSV | Complete |
| Development mastery matching | All 72 development files and 9216 short outputs; complete 90/95/99% sensitivity and selected-test comparisons without missing entries; checkpoint selection does not read test scores | Exploratory completion; omitted numeric preregistration threshold cannot be restored |
| Frozen baselines with definitions at each scale | 480 independent-confirmation examples for each of four models with common raw-text prompts/full definitions; original 560-example frozen tests also for 7/32B; official-chat frozen Instruct baseline | Complete; reliable initial frozen long-execution capability is not established |
| Matched-prompt pre/post-training comparison | matched-context.json checks 26880 repeated measurements for 7/32B with/without definitions, identical IDs/inputs, and exact agreement across six frozen output copies | Complete; repeated frozen outputs are not independent seeds |
| Learning-rate and Instruct supplements | Six low-LR groups each for 3B/32B and six 32B-Instruct groups: 18 runs; 21280 raw outputs, 126 adapter hashes, complete steps/counts verified | Complete; 3B hardware confounding disclosed |
| Independent held-out program confirmation | 480 examples, 120 exactly distinct affine programs, registered SHA; seven evaluations per model across four models = 13440 outputs; complete coverage/source hashes | Complete |
| Raw behavior, local errors, and formatting attribution | Per-example recomputation of truth, reported states/operations, strict answers, formatting, multiple answers, correct prefixes, and two-tool stopping; broad metric and segment distributions added | Complete; overlapping metrics are not mutually exclusive causal categories |
| Equivalent trajectories and chance-correct answers | outcome-diagnostics audits 48160 final main/independent/supplementary outputs; exact affine signatures establish equivalence over all inputs | Complete |
| Stop reasons and generation caps | Original non-EOS counts, caps, inferred EOS-before-cap, boundary ambiguity, and cap-exhaustion categories retained | Record audit complete; historical final token IDs are unavailable, so direct stop reasons cannot be reconstructed |
| Paired seed and program uncertainty | paired-inference and extended-results include seed differences, three-seed t intervals, and complete-program-clustered bootstrap with distinct interpretations | Complete; repeated inputs are not independent templates |
| Complete raw-output acceptance | verification.json checks 174 files/95200 outputs: 13440 final main + 47040 checkpoint/definition + 13440 independent + 21280 supplementary; IDs, inputs, splits, computation, and hashes verified | Pass; matched-context reaudits are not counted again |
| Reviewable figures and reports | REPORT, CONCLUSIONS, SUPPLEMENT, STOPPING_DIAGNOSTICS; three PNG/SVG/PDF figure groups visually checked for unobscured labels and agreement with statistics | Complete |
| Failures and reproduction materials | Failed microbatch check and successful checkpointing check retained; TLS/startup logs and failed eight-example cross-GPU 5090 agreement probe retained outside primary results; source, locked environment, data, weights, and all adapters preserved | Complete |
| Project-local environments and infrequent monitoring | Project .venv/.training-venv/.analysis-venv/.cache/.runtime and training-env; remote runs use the same shared directory; normal checks approximately every 15 minutes | Followed |
| Resource cleanup | Final compute-app queries empty locally and on both PRO servers; no scale-study Python jobs; 5090 returned and not accessed again | Complete; user servers not shut down |

## Review judgment

Results support that scale reduces fixed two-tool stopping while tool-identity labels retain long-composition accuracy gains at 32B. They do not attribute all gains to reduced correct-prefix early answering or establish fine-tuning damage to preexisting long-execution ability. Missing preregistered thresholds and unrecoverable historical stop tokens remain explicit limits; post hoc analyses are not presented as original-protocol success.

Real-agent applications, dynamic tool renaming, position/remaining-step cues, and irrelevant length-matched labels are proposals for the next stage, pending user review. They are neither claimed complete nor launched without authorization.
