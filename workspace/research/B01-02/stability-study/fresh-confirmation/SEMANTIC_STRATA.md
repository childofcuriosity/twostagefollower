# Function-equivalence strata in the new confirmation set: post hoc diagnosis
Primary results still include all 400 examples. This stratification was added after some outputs existed to explain dataset scope, not to promote a better-performing subset to the primary result. The two groupings overlap and are not two additional independent experiments.
All earlier data includes training, development, old tests, and the old independent set, not just training data. Groups use exact affine signatures of final functions; tool sequences themselves are all distinct from earlier data.

|Model|Training|Function reference set|Equivalent function seen before|Programs / functions|Full-history success|Local-operation-input success|Three seed changes pp|
|---|---|---|---|---|---:|---:|---|
|qwen3b|Joint training|Training set|No|82 / 71|34.96%|38.52%|+1.52 / +4.57 / +4.57|
|qwen3b|Joint training|Training set|Yes|18 / 14|38.89%|44.91%|+12.50 / +0.00 / +5.56|
|qwen3b|Joint training|All earlier data|No|28 / 24|37.80%|42.86%|+0.00 / +9.82 / +5.36|
|qwen3b|Joint training|All earlier data|Yes|72 / 61|34.84%|38.43%|+4.86 / +1.39 / +4.51|
|qwen3b|Two specialist models|Training set|No|82 / 71|50.00%|62.40%|+25.00 / +1.52 / +10.67|
|qwen3b|Two specialist models|Training set|Yes|18 / 14|56.48%|61.57%|+15.28 / +0.00 / +0.00|
|qwen3b|Two specialist models|All earlier data|No|28 / 24|56.55%|68.45%|+26.79 / +0.00 / +8.93|
|qwen3b|Two specialist models|All earlier data|Yes|72 / 61|49.07%|59.84%|+21.88 / +1.74 / +8.68|
|qwen32b|Joint training|Training set|No|82 / 71|77.85%|93.70%|+30.18 / +7.62 / +9.76|
|qwen32b|Joint training|Training set|Yes|18 / 14|87.50%|94.91%|+12.50 / +4.17 / +5.56|
|qwen32b|Joint training|All earlier data|No|28 / 24|76.49%|97.02%|+41.96 / +4.46 / +15.18|
|qwen32b|Joint training|All earlier data|Yes|72 / 61|80.79%|92.71%|+21.18 / +7.99 / +6.60|
|qwen32b|Two specialist models|Training set|No|82 / 71|89.74%|95.73%|+8.54 / +8.54 / +0.91|
|qwen32b|Two specialist models|Training set|Yes|18 / 14|95.37%|97.22%|+0.00 / +5.56 / +0.00|
|qwen32b|Two specialist models|All earlier data|No|28 / 24|86.61%|93.75%|+9.82 / +11.61 / +0.00|
|qwen32b|Two specialist models|All earlier data|Yes|72 / 61|92.36%|96.88%|+5.90 / +6.60 / +1.04|
