# Evidence requirements for the final report

- Base the primary conclusion only on the prespecified three-seed paired macro−flat comparison. natural/shuffled are secondary; do not select the most favorable control to claim a win.
- Report IID and OOD, splitting OOD by depth 3/4/5. The 384 OOD examples represent 96 independent compositions with four inputs each; cluster intervals by composition. Three-training-seed intervals differ from example bootstraps.
- Recheck matched supervised tokens using cumulative training logs rather than relying solely on data-generation audits.
- Report actual LoRA updates, not full-parameter pretraining, complete SPEE replication, or acceptance of a fully autonomous EvoScientist research product.
- Real abstraction-proposal success is low and most discovery traces are incorrect. Executability in a finite domain does not establish useful innovation.
- Library-free success supports parameter adaptation and behavioral generalization only. Finite behavioral experiments cannot uniquely identify internal algorithms.
- Score permuted-semantic worlds against their new truth. Only examples with different old/new targets can compare dependence on old versus new semantics.
- High IID and low OOD can reject compositional transfer in this setup. Low IID indicates inadequate learning of this setup, not falsification of abstraction hypotheses.
- Even a passing effect is initially a mechanism signal worth replication. Assess novelty with new nearby literature rather than immediately presenting a paper or résumé achievement.
- Use actual logs for GPU-hours, separately recording calibration, discovery, baselines, training, and evaluation. Installation/download wall time is not training time. Scheduler wall time conservatively estimates device reservation, not kernel activity.
- Cyclic semantic permutations change some macro expansion lengths; original-versus-permuted scores do not isolate semantics. Test following new truth where targets differ and report actual world-specific tokens. Name permutations preserve definitions.
- Primary training tokens match strictly, but inference shares only the 256-token cap. Actual generation can differ, so total inference compute is unequal. Early stopping and longer outputs may themselves matter; report real generated tokens and time by group.
