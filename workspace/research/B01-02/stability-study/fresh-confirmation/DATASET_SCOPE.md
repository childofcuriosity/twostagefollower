# Dataset scope of the confirmation set

The earlier 480-example generator deduplicates final affine functions and excludes functions from earlier training/development/test sets. The new confirmation set deduplicates tool-name sequences as registered. These are different conditions; new tool sequences are not automatically new final functions.

The new confirmation set has 100 distinct tool sequences and 400 examples, corresponding to 85 distinct final functions. Of these sequences, 18 have final functions equivalent to training-set functions, and 72 have final functions equivalent to functions in any earlier input set at this stage, including the old independent set.

This does not mean the long tool sequences or full operation trajectories appeared in training. Strict scoring requires every specified operation and intermediate state; reaching the same final state alone is insufficient. The limitation concerns claims of transfer to new functions.

The primary analysis retains all 400 preregistered frozen examples and reports the two batches separately. Data are not reselected based on output scores. Program-level labels and counts by length are in the parent analysis/dataset-semantics.json.

This scope check occurred after some new-confirmation jobs had completed, without changing data, methods, or scoring.
