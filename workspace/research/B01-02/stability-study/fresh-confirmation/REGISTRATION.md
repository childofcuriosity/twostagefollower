# New tool-composition confirmation set: preregistration

The main matrix and context intervention use earlier examples. Add a preregistered frozen new program set to test whether observed effects are confined to repeatedly inspected examples.

Generate before any actual local-context model inference: fixed random seed2026092501;20 tool compositions per length3/4/5/6/8;4 distinct four-digit inputs per composition;100 programs and 400 examples total. Exclude every tool composition seen in oracle-study train/dev/test/independent inputs. Tools remain the original nine, so this is not transfer to new tools. Files/hashes are data/independent.jsonl and analysis/dataset-manifest.json. Generation does not read model predictions.

Fix3B/32B, seeds11/22/33,512 steps. Compare only joint models generating all outputs and actual composition of two specialists, each with full history and local operation context:2 scales x3 seeds x2 routes x2 contexts x400 examples =9600 new inferences. Do not select checkpoints, seeds, or routes based on existing confirmation results or tune methods on this set.

Primary comparisons: local versus full context within training type, and separate versus joint training within local context. Report all three seeds, lengths, subtask accuracies, full-task accuracy, and paired gains/losses. Context-scope changes are not token-length-only effects. Disclose the greater parameter storage and original training costs of two specialists.

Run after the main matrix and first context intervention finish and pass audits, reusing the same evaluator calibrated with actual models. Reconstruct actual generation inputs and audit scores record by record. Report all results, not only improved scales. Source, inputs, raw trajectories, and logs remain here. This set is not used for training or method selection.
