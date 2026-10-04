# Completion checklist established before formal outputs

This file lists requirements; it does not certify that they have passed. Record final evidence for each item in COMPLETION_AUDIT.md.

1. **Model and scope:** Official original 7B weights. Any 14B fallback must have a documented short-task floor and implementation diagnosis. No adapters or training; leave earlier training experiments unchanged.
2. **Prompt controls:** Full definitions and one shared underlying example in all four groups. STEP/POSITION/NAME change only header requirements and example headers. ALIAS uses the existing mapping in both inputs and outputs. Evidence: prompts, method-audit, and actual rendered chat inputs.
3. **Complete exploration:** All initial lengths, 32 examples each, one STEP/NAME output per example; additional tests only under the registered rule. Retain all exploration and 7B failures. Select using STEP rather than NAME.
4. **Freeze and fresh examples:** Freeze model revision, prompts, code, data, and decoding before the first formal run. Use 512 new examples per selected length, disjoint from prechecks, exploration, and the example. Share underlying examples across conditions; no repeated generation followed by selection.
5. **Capacity and decoding:** Greedy decoding, original weights, and a common generation limit across conditions. Every correct target fits; full input plus generation budget fits the context. Actual tokens and EOS are auditable.
6. **Strict scoring:** The existing scorer and independent line-by-line implementation agree on operations, all intermediate states, and Answer. Report headers separately. Retain complete paired raw outputs and scores.
7. **Statistics and errors:** Report group success, example-level differences from STEP with 95% intervals, and discordant counts. Make first errors, overlapping error flags, EOS versus truncation, and header compliance traceable.
8. **Costs:** Input/output tokens, synchronized batch generate seconds, outer allocated GPU time, and NAME increments over STEP. Do not interpret batch wall time as per-example latency or kernel-active time.
9. **Run audit:** All jobs ended; OOM/interruption records and fixes retained. Use the eight local GPUs and inspect normal long-running jobs hourly. Check for residual inference processes at completion.
10. **Delivery and conclusions:** A concise top-level REPORT.md answers whether the method helps, at which call lengths, with which errors and output/inference costs. Separate exploration from formal results without presuming gains. Explain model selection and label-form/token/prompt limitations. Independent cross-model validation, real-task transfer, and external publication are outside scope.
