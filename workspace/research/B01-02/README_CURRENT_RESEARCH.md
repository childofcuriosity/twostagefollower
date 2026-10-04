> Historical update: the position-label and fixed-renaming conditions were completed across four model scales and three seeds. See the [label-control conclusions](label-controls/CONCLUSIONS.md) and [completion audit](label-controls/COMPLETION_AUDIT.md). The earlier stage notes below are retained for context. For the latest archived study, see the [repository overview](../../../README.md).

> On 2026-09-26, the original workspace provided a review package in `review-package-2026-09-26/`, including `RESEARCH_REVIEW_CN.md`, `REVIEW_PROMPT_CN.md`, and evidence snapshots. That package is omitted from this archive. The stability study, operation-context intervention, and fresh-program confirmation had been completed; see `stability-study/CONCLUSIONS.md` for conclusions from that stage.

# Research question at this stage

The active research directory at this stage was `stability-study`. Its `WORK_STATUS.md` and `GOAL.json` record the running status and objectives.

We study a controlled question: when a model is trained on tasks with one or two tools, why does it skip work, stop early, or expand tools incorrectly on tasks with three to eight tools? Can separately training tool-name output and within-tool operation output improve whole-task completion?

The input already supplies the correct tool sequence. Here, sequence capability means preserving that order, completing each item, and stopping correctly. Autonomous planning in real-world tasks is a separate capability. The tools are nine fixed small programs.

## Three layers of evidence

1. The original NAME-versus-STEP experiments change the output representation and evaluate complete execution and longer tasks. They provide initial evidence for the benefit of tool-name representations.
2. `oracle-study` holds the training text and output protocol constant while training all outputs, name tokens only, or operation tokens only. During evaluation of one component, a program supplies the correct content for the other component to isolate learning capabilities. The product of the two accuracies under correct contexts is distinct from success under actual composition.
3. `stability-study` examines checkpoints at 64, 128, 256, and 512 steps, connects the two specialist models, and then replaces one component at a time. Generation uses neither reference answers nor corrections to intermediate states. This stage tests whether the gains translate to whole-task success and how they depend on training seeds and additional cost.

## Supported findings and open questions

The available evidence supports further investigation of the decomposition between tool names and fixed operations. Stable improvements on real-agent long tasks and a specific learning mechanism remain open questions.

This study must report all seeds, task lengths, and registered checkpoints. Average gains should be distinguished from gains on every seed. Two specialists trained for 512 steps each have a different training cost from one model trained for 512 steps. Combining two specialists trained for 256 steps each matches the cumulative example exposure of a single 512-step model, while doubling the total adapter parameters.

In joint training, name-related targets account for approximately 11.14% of the objective and operations for approximately 88.86%. Separate training changes both loss normalization and parameter sharing. Supervision weighting, parameter capacity, and context changes therefore remain alternative explanations for successful composition.

The original workspace retained final raw trajectories, paired comparisons, both subtask metrics, error cases, execution costs, and audit records. This archive includes selected artifacts. Unfinished experiments and diagnostics must remain identified as pending rather than presented as findings.
