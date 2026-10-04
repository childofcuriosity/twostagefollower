# Post-result sensitivity-analysis declaration

After completing and inspecting preregistered primary results, two interpretation issues motivated added analyses without changing primary results or generating proposals:

1. Original selection deduplicated semantics first and retained the first spelling, while compression requires literal contiguous matching. Lexicographic representatives from full enumeration can therefore fit a task poorly, explaining why enumeration need not beat frequency heuristics. Add a selector that first compares support gains for all spellings, then excludes semantic equivalents after selection, still choosing at most three distinct macros.
2. Original search budgets 3,000 action expansions, with 2–3 primitives per macro. Add a 3,000-primitive-execution budget to check gains due solely to variable action cost. This still does not match CPU wall time or neural tokens.

Cross both factors in a 2×2 design using original proposals/support/tests. Retain primary results, thresholds, and decisions. No retraining or prompt tuning follows test results.
