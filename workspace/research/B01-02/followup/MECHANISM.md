# Identifiability and limits of this round

The causal chain has three steps: execution training changes parameters; proposal distributions change given new-task experience; selected abstractions provide utility on unseen tasks. The previous round tested compositional outputs after execution training. This round checks the latter two steps without directly optimizing a proposal policy.

Fix support S, test T, and candidate budget K=16. Policy pθ(a|S) samples candidate set A; every method uses selector g(S, A) to obtain library L. Primary utility U(T, L) is net description-length reduction from dynamic-programming compression after definition costs. Selection sees only S.

Macro versus base includes all execution-training effects; macro versus flat isolates the earlier trajectory-label training difference. Macro versus mismatch holds parameters/selector fixed and changes support context seen by the proposer. Mismatch still selects on true support, so it tests incremental proposal-context adaptation rather than complete task independence. Random/model methods share grammar, budget, and selector. Heuristics/full enumeration are separate references with unequal search compute.

Program search is separate from string compression. A library can compress existing text yet reduce discovery under a fixed expansion budget by increasing branching. Targets use complete function semantics, avoiding chance matches on four-digit inputs. A macro action executes 2–3 primitives; log primitive counts because equal expansions are not equal compute. Breadth-first, primitive-first search is one fixed searcher. Negative results do not exclude benefits for a specially trained neural searcher.

The three checkpoint seeds are genuine independent earlier training runs; base seeds vary sampling only. Family bootstrap is conditional on existing checkpoints and eight constructed families, not population uncertainty across models/natural tasks. The proposal space has only 252 short programs. Grammar constraints remove format failures but may expose continuation preferences. Even full success supports bounded transfer from execution learning to abstraction selection, not open-ended innovation.

After failure, do not tune prompts, temperatures, or budgets on the test set and declare success. Learning a proposal policy requires separate training families, utility rewards, and strict out-of-family evaluation. Failure without that training does not refute the broader direction.
