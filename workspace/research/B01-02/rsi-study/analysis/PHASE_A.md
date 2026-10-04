# Stage A: cross-model and prompt robustness, complete

This summarizes the completed stage only; loop/causal conclusions remain pending at this point.

| Model | Condition | IID | OOD | Primary-setting proposal compression |
|---|---|---:|---:|---:|
| qwen1.5b | base | See frozen baseline | See frozen baseline | 39.01% |
| qwen1.5b | flat | 100.00% | 0.09% | 3.39% |
| qwen1.5b | macro | 100.00% | 29.77% | 9.06% |
| qwen3b | base | See frozen baseline | See frozen baseline | 40.42% |
| qwen3b | flat | 100.00% | 0.09% | 3.19% |
| qwen3b | macro | 100.00% | 60.76% | 9.15% |
| smol1.7b | base | See frozen baseline | See frozen baseline | 35.39% |
| smol1.7b | flat | 100.00% | 0.00% | 5.80% |
| smol1.7b | macro | 100.00% | 22.66% | 9.01% |

Across all prompts/budgets:
- qwen1.5b: macro−base is negative in 12/12 settings.
- qwen3b: macro−base is negative in 12/12 settings.
- smol1.7b: macro−base is negative in 12/12 settings.

Finite-budget proposal utility declines across models after learning in-distribution execution. Missing ends coverage still requires control; subsequent-learning branches must test the RSI-related causal path.
