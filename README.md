# twostagefollower

## Research overview

An agent can have a plan and still leave it unfinished. It may skip a step, lose track of the current operation, or stop before completing the sequence. We study this gap between having a plan and following it through in a controlled execution task.

The intervention is simple: **train the model to write the current tool's unique identifier before executing it.** Each tool has a fixed identity, repeated whenever that tool is called. We compare this NAME format with a STEP format that uses the same `step:` marker for every call. Both formats require the model to produce the full execution trace and final answer.

Tool identifiers improved whole-task performance in our training experiments. We observed gains with supervised fine-tuning (SFT) and with reinforcement learning using GRPO. The SFT studies include Qwen2.5-7B Base; the GRPO studies use Qwen2.5-7B-Instruct and Qwen2.5-14B-Instruct. The benefit depends on task length and training conditions, with the hardest settings still showing low success.

Our working explanation is that an explicit tool identity makes two subtasks clearer: tracking which step of the plan comes next, and carrying out the operations within that step. Separate-training and composition experiments support studying this decomposition, although they do not isolate it as the sole cause of the gains. Here, the plan is supplied in the input: the first subtask is following that plan and stopping correctly, rather than inventing a plan from a goal.

**The result concerns training, not a general prompt-engineering recipe.** In a separate prompt-only test of Qwen2.5-14B-Instruct, NAME achieved 45.12% full-trajectory success versus 45.90% for STEP. Simply asking an unmodified model to repeat the tool name did not reproduce the training benefit in that test.

## Controlled task

The model starts with a four-digit state and a prescribed sequence of calls to nine deterministic tools. Each tool consists of basic operations on the digits. The model must expand every call, compute the intermediate states, and return the final answer. An interpreter checks the entire trace, so a correct final answer alone does not count as successful execution.

This setting lets us measure skipped calls, incorrect operations, and premature stopping directly. It also separates the question of executing a known plan from the broader problem of autonomous planning. Experiments with real agents are kept in separate study directories.

## Training results

In the SFT study, models trained on one- and two-tool tasks were tested on longer sequences. On the independent 480-example test set spanning three to eight calls, Qwen2.5-7B achieved **37.01%** complete-trajectory success with NAME, compared with **12.15%** with STEP, averaged over three training seeds. See the [SFT study](workspace/research/B01-02/scale-study/CONCLUSIONS.md) and [label-control results](workspace/research/B01-02/label-controls/CONCLUSIONS.md).

### GRPO

The latest study, completed on September 29, 2026, uses GRPO with a binary reward: the entire execution trajectory must be correct. We ran six model/length settings, two output formats, and three paired seeds, for 36 runs of 100 updates each.

L is the number of tool calls. Test success below is averaged over three seeds, using 512 fresh test examples per setting.

| Setting | STEP | NAME |
|---|---:|---:|
| 7B L3 | 8.27% | 32.75% |
| 7B L4 | 0.91% | 4.17% |
| 7B L5 | 0.00% | 0.85% |
| 14B L5 | 32.94% | 70.77% |
| 14B L6 | 4.56% | 38.74% |
| 14B L7 | 0.72% | 7.29% |

NAME scored higher in all six settings, though success fell sharply as tasks grew longer. We observed no learning improvement at 7B L5.

14B L5 was the only setting within the preregistered STEP validation range of 20%–90%. There, NAME led by 37.83 percentage points on the test set. The formats also had different prompt-only baselines; after accounting for those starting points, the difference in learning gains was 32.75 points.

The training gains vary with task length; the longest settings remain difficult. Transfer to real-agent tasks remains to be evaluated.

See the [report](workspace/research/B01-02/grpo-length-study/REPORT.md), [method](workspace/research/B01-02/grpo-length-study/METHOD.md), [conclusions](workspace/research/B01-02/grpo-length-study/CONCLUSIONS.md), and [completion audit](workspace/research/B01-02/grpo-length-study/COMPLETION_AUDIT.md) for details. Internal reports, protocols, and research notes are available in English.

## Why split plan following from execution?

Writing a tool identifier gives each call an explicit identity before the model begins its internal operations. This suggests a division of labor: one component follows the tool sequence, while another executes the selected tool on the current state.

We tested that division directly by training separate models for tool-name/sequence output and operation output, then connecting them during inference. On fresh programs, separate training increased mean full-task success from 35.67% to 51.17% for Qwen2.5-3B and from 79.58% to 90.75% for Qwen2.5-32B when both used full history. Giving the operation component just the current tool and actual state improved execution further. These experiments make the decomposition useful to investigate; separate training also changes loss normalization and total adapter capacity, and its gains vary across seeds and contexts.

See the [decomposition and stability results](workspace/research/B01-02/stability-study/CONCLUSIONS.md) for the component comparisons, and the [prompt-only study](workspace/research/B01-02/prompt-only/REPORT.md) for the distinction between training the representation and requesting it at inference time.

## Where to look

Experiments live under `workspace/research/B01-02/`. Each study keeps its own code, protocol, and reports.

| Directory | Study |
|---|---|
| `grpo-length-study/` | The six settings reported above |
| `grpo-binary/` | Earlier fixed-length GRPO experiments |
| `oracle-study/`, `stability-study/` | Training sequence and operation prediction separately, then composing them |
| `label-controls/`, `label-seed-replication/` | Label position, renaming, and seed replication |
| `scale-study/` | Model size and output labels |
| `prompt-only/`, `prompt-only-length-short-20260929/` | Prompt-only baselines |
| `followup/`, `rsi-study/` | Execution training, proposal quality, and closed-loop experiments |
| `agent-study/`, `agent-study-v3/`, `agent-reliability/` | Separate experiments with real agents and tool protocols |
| `agent-completion-plan/` | Plans for studying long-task completion |
| `qwen05b-fixedlength/`, `qwen05b-indomain/` | Early small-model controls |
| `src/`, root `PROTOCOL.md` and `REPORT.md` | The original task and first experiments |

The initial [candidate ideas](workspace/research/2026-09-23-batch01/candidates.md) and [literature notes](workspace/research/2026-09-23-batch01/sources.md) are also retained. Status files describe work at the time they were written; use each study's final report and conclusions when reading its results.

## Running the code

Start with the protocol or method document for the study you want to reproduce. Dependencies are recorded in `training-requirements.in` and `training-requirements.lock.txt`; you will need a Python/CUDA environment suited to your hardware.

Keep the directory layout intact, since some scripts import code from neighboring studies. Before running a script, check its model paths, output paths, GPU settings, and scheduling configuration. Several scripts still use paths and assumptions from the original machines. The lock file records that environment, so installation may need adjustments on yours.

The archive includes source, configurations, reports, figures, and small JSON/CSV summaries. Model weights, checkpoints, raw per-example trajectories, logs, runtime environments, and private server configuration are omitted. Some historical reports link to those omitted files. Reproducing the experiments requires obtaining the models and regenerating the data; auditing the original runs in full requires their raw artifacts.

[ARCHIVE_MANIFEST.json](ARCHIVE_MANIFEST.json) lists the current archive files and their hashes. Historical source-freeze records describe the original experiment files; translated report generators have new hashes. No license has been added.
