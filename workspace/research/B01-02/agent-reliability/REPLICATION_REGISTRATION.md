# Fixed-sample replication of explicit operational notes

Earlier independent explicit-note comparison: plan10/12, reminder11/12, identity12/12, todo12/12. Two paired gains over baseline are insufficient for a stable conclusion; identity does not outperform the strong todo comparator. This motivates one larger fixed replication, not selecting only the family with favorable preliminary outcomes.

Before new inference, freeze36 instances: files/data/code ×12 new seeds20265001–12, each12 requirements. Same `native_notes.py`, same32B checkpoint, same budgets, zero-shot. Four conditions retained,144 trajectories total. Primary comparison identity versus empty note. Reminder and todo remain mandatory competitors. Report all outcomes and costs, no early stop upon favorable results, no seed removal. This evaluates long *checklists*, not long interaction horizons; sequential experiments are reported separately. No token-length-matched label-diversity control is present, so this cannot establish a unique causal benefit of semantic identity versus other structured notes.

Inference is conditional on these three synthetic generator families; exact paired tests do not establish broad production-agent generalization. The sample size is fixed pragmatically for available local resources, not a claim of definitive statistical power.
