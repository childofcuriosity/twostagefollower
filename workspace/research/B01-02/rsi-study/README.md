# Separating execution learning from improvement capability

This research phase was completed and was awaiting a consolidated results review. Start with the [conclusions and recommendations](CONCLUSIONS.md), followed by the [full report](REPORT.md), [supplementary controls](SUPPLEMENT.md), and [work status](WORK_STATUS.md). Design references: [protocol](PROTOCOL.md), [theory and identifiability](MECHANISM.md), and [closest prior work](literature/NEAREST.md).

## Data and runs

The paths below describe the original workspace. This archive retains selected source files and summaries; datasets, model weights, and raw runs are omitted.

- `data/families.json`: 32 independent latent-pattern families, split into 12 training, 4 development, and 16 test families, with 12 support examples and 64 test examples. The protocol defines exact semantic isolation and the domain of applicability.
- `data/loop-eval-*.json`: 256 fixed evaluation examples for each of two execution semantics. Short programs, unseen family combinations, and longer/harder stress sets are kept separate.
- `models/`: fixed Hub revisions and download SHA-256 hashes for two additional models; the original 1.5B model uses `../model`.
- `replications/*/runs/`: first-round setting replications for the new models, with 512-step LoRA training, per-example outputs, and adapters.
- `runs/robust-*`: evaluations across three prompts, temperatures, and K budgets; grouped raw proposals in JSONL.
- `runs/loop-*`: three rounds of parameter updates, including checkpoints, execution outputs, proposals, training examples, and losses for rounds 0–3.
- `runs/branch-*`: 128-step branches from the same shared-condition round-1 starting point, with updated or frozen proposal sources.
- `runs/gradient-*`: read-only gradient-alignment diagnostics with no parameter updates.
- `analysis/`: registrations, amendments, results, statistics, and completeness audits.
- `figures/`: six sets of PNG/SVG/PDF figures covering all seeds and the main intervals.

## Environment and commands

All commands are run from the project root. The original workflow used `.training-venv` for training and a separate `.analysis-venv` for analysis and plotting. `source training-env.sh` configured caches, temporary files, and the proxy without changing the global environment. That script and the runtime environments are omitted from this archive; configure replacements before adapting the workflow below.

```bash
source training-env.sh
python workspace/research/B01-02/rsi-study/src/analyze_robust.py
python workspace/research/B01-02/rsi-study/src/analyze_loops.py
python workspace/research/B01-02/rsi-study/src/verify.py
.analysis-venv/bin/python workspace/research/B01-02/rsi-study/src/plots.py
```

All training and diagnostic launchers had completed in the original workspace. Avoid relaunching them over existing evidence. Individual entry points, such as `src/loop.py --domain digits --condition shared --seed 11`, refuse to overwrite existing directories. Use a new research directory or run ID for reproduction and preserve existing evidence.

Dependencies are recorded in the root `training-requirements.lock.txt` and this directory's `analysis-requirements.lock.txt`. New model downloads use the standard library and curl, adding no training dependencies.

See `src/finish.py` for the complete analysis order. Run `src/supplements.py` after generating the report; the conclusions review document is maintained separately. `analysis/final-artifacts.json` records hashes of the final deliverables, while `analysis/verification.json` contains the original training audit. All ten phases were completed, with no GPU jobs remaining at that time.
