> Historical update: the position-label and fixed-renaming conditions were completed across four model scales and three seeds. See the [label-control conclusions](label-controls/CONCLUSIONS.md) and [completion audit](label-controls/COMPLETION_AUDIT.md). The stage-specific notes below are retained for historical context. For the latest archived study, see the [repository overview](../../../README.md).

# B01-02 workspace

The [RSI extension protocol](rsi-study/PROTOCOL.md) describes the next research phase; its progress is recorded in [rsi-study/WORK_STATUS.md](rsi-study/WORK_STATUS.md). The original research scope included user-authorized experiments with multiple models, closed loops, and causal interventions.

The authorized [follow-up proposal-utility experiment](followup/REPORT.md) was completed and found weaker proposal performance after execution training than with the frozen base model. The original first-round report was retained unchanged.

At this stage, the theoretical and experimental work was complete and awaiting a consolidated results review. Start with the [results report](REPORT.md). Files were retained in the original project workspace; this source archive includes a subset, as described in the repository overview.

The study completed 30 main training runs, one calibration run, two frozen baselines, and seven routing diagnostics. The second environment is under `secondary/`. The report distinguishes preregistered main experiments from post hoc diagnostics.

- `MECHANISM.md`: theoretical derivation, identifiability, confounds, and scope of conclusions.
- `PROTOCOL.md`: pre-experiment protocol and proceed/stop criteria.
- `src/`: code for downloads, model-generated proposals, verification, data, training, evaluation, and analysis.
- `data/`: original proposals and trajectories, abstraction libraries, isolated datasets, audits, and hashes.
- `runs/`: checkpoints, training logs, and per-example outputs organized by condition, seed, and world.
- `analysis/`: protocol hashes, amendments, job status, and final statistics.
- `model/`: the original model at a fixed revision and download hashes.

## Original execution workflow

The original project used `training-env.sh` to configure project-local caches and the corporate proxy, and `install-training-env.sh` to rebuild an isolated `.training-venv`, without modifying the system torch/transformers installation. These environment scripts and private settings are omitted from this archive; configure your own environment using the dependency records before adapting the commands below.

In the original workspace, the environment was activated from the project root with:

```bash
source ./training-env.sh
```

Run `src/download_model.py`, `src/discover.py`, and `src/build_data.py` in order. Training calibration uses `src/run.py --condition flat --steps 20 --calibrate`. Main runs are scheduled by `src/launch_suite.py` as independent GPU processes. The calibration decision file records the fixed final training step count. `src/analyze.py` analyzes completed jobs and treats missing results as missing, rather than as zero scores.
