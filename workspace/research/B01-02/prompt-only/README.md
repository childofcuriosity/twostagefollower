# B01-02 prompt-only study

An independent prompt-only comparison of four heading formats, with no training or adapters. See `REGISTRATION.md` for the study design. Existing training experiments are treated as read-only.

## Original workflow

The original workspace used `source training-env.sh` from the project root before running the scripts in this directory's `src/`. That environment script is omitted from the archive; configure an equivalent environment before adapting these commands.

- `download.py`: pin official model revisions and record file hashes.
- `validate.py`: validate the DSL over all states and check scoring on correct trajectories and deliberately incorrect variants.
- `prepare.py --phase {precheck,explore,formal} --lengths ...`: prepare data, four prompt conditions, token budgets, and frozen manifests.
- `dispatch.py --phase ... --lengths ... --conditions STEP NAME ...`: schedule jobs across eight GPUs. For a formal experiment at one length, split each condition into two disjoint example shards to use all eight GPUs. Record hourly monitoring checks.
- `worker.py`: use BF16, SDPA, and greedy decoding; save raw text, token IDs, stopping reasons, and costs. On an out-of-memory error, halve the batch size and retain a record of the adjustment.
- `score.py`: cross-check the original strict scorer against an independent implementation; evaluate heading compliance, first errors, and paired bootstrap estimates.
- `select.py`: use STEP alone to choose supplementary evaluations or the formal task length; `--final` writes the length-selection record.

In the original workspace, raw outputs were stored in `runs/`, scores in `analysis/`, and data and frozen manifests in `data/`. `complete.json` marks process completion. Exception logs were retained in `logs/` and each run directory. This archive omits raw outputs, datasets, and logs; see the [repository overview](../../../../README.md) for archive scope.
