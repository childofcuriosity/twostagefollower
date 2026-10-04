# Reproduction and resource accounting

This study uses only the existing project training/analysis environments and local PRO6000 GPUs. Per-run config.json, driver_snapshot.py, train.jsonl, model adapters, and outputs are retained in runs. analysis/preflight.json and baseline-freeze.json record hashes of data, original source, and earlier outputs; analysis/launch.json records the generation-wrapper version. Initial adapters for large models are checked file by file against the original same-seed adapters.

Routine monitoring is hourly, with process-completion events handled automatically rather than minute-by-minute GPU polling. Any failure logs are retained without overwriting and rerunning. Apart from calls to target-construction functions, training algorithms retain the original source; see TRAINER_DIFF.md for the exact diff.

|Model|New jobs|Total single-GPU process wall hours|
|---|---:|---:|
|qwen1.5b|6|0.65|
|qwen3b|6|1.01|
|qwen7b|6|4.41|
|qwen32b|6|15.91|

Total: 21.98 GPU-hours. This includes model loading, training, development-set/formal inference; it is neither active GPU-kernel time nor pure training time, and excludes historical training costs for the original baselines.

After completion, rerun offline scoring/statistics from the project root if needed. This refreshes derived reports without retraining or overwriting raw outputs:

```bash
source training-env.sh
python workspace/research/B01-02/label-controls/src/analyze.py
```

New training uses worker.py --job INDEX, with configurations from analysis/jobs.json and scheduling records in analysis/dispatch.json. The worker refuses to overwrite existing runs. To reproduce training, first create a separate experiment directory at the same level and preserve original records; do not directly delete existing runs. Full base models and previous controls depend on original project paths, so this directory is not a standalone software package.
