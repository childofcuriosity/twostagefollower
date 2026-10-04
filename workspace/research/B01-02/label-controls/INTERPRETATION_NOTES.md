# Distinctions to preserve when interpreting the results

These interpretation notes were added while new jobs were running. They do not change registered training, prompts, data, or scoring.

## Inputs contain tool identities in every condition

Original STEP, position numbering, Original NAME, and fixed aliases all receive the complete tool list. The comparison is therefore whether a stable tool identity is explicitly repeated when outputting the current segment, relative to a uniform boundary or position cue. The position condition can retrieve identity from the corresponding input-list item; names may reduce this binding/retrieval step.

Better NAME/alias performance would support the usefulness of stable identity cues in outputs, but would not mean STEP has no identity information. Every condition has segment boundaries, with no boundary-free condition, so the total effect of boundaries cannot be estimated.

## Position extrapolation is not unseen-token extrapolation

Training contains only label combinations step1 and step2; testing includes step3 and later. Tokens for digits 3?8 occur widely in training numerical states and are not unseen vocabulary tokens. What is untrained is their combination/use as segment-initial position labels. Position success demonstrates extrapolation; failure may include extrapolation difficulty.

## Arbitrary aliases may be harder to distinguish

The original color words differ from one another, whereas toolA?toolI share the tool prefix and rely on the following letter for distinction. These representations also differ in token length and pretrained familiarity. Position labels step1?step8 likewise share a prefix. Only the two user-specified conditions are added, without moving the goal by introducing random single-token names or more alias groups.

Original NAME and aliases both match input and output names, so they do not directly test name consistency. Aliases rename both input and output vocabulary and are not a pure output intervention. One fixed mapping is reused across models/training seeds, leaving mapping-specific chance effects unresolved.

## Label length and budget

Prechecked target-token counts match across four scales: Original NAME has 263858 per pass; position and alias each have 271656, approximately 2.96% more. Position and alias match output-token counts, but alias input lists are longer. No post hoc compensation changes the original models, training steps, masks, microbatches, or prompts.

Maximum correct-reference length including EOS in original tests is 172 for old labels and 177 for new labels, below the 256 cap; in the independent set it is 268 and 276, below 512. No correct reference exceeds budget because of new labels. Abnormal model generations may still hit the cap and count as failures; budgets are not raised to help new conditions.

## Retain both full-success metrics

The original primary full-trajectory score requires correct operations, numerical states at every step, and the final Answer, without enforcing label identity. New numerical/uppercase labels only extend legal segment-heading syntax. The separately reported label_aware_complete metric also requires the correct label sequence, exposing cases where a model completes operations while ignoring new labels.

All emitted-segment operations correct is scored against the corresponding position in the required tool list, consistently across conditions. It neither redefines correct operations from the emitted name nor measures all required operations under the earlier oracle setting. Missing segments appear in full-success/label-sequence metrics. Operation performance conditional on correct labels is descriptive stratification, not an unbiased causal comparison.

## Do not assume the conclusion

Alias performance close to Original NAME would show that this fixed mapping can preserve gains, not that arbitrary naming never matters. Weaker aliases could support an effect of name form on usability without identifying a specific attention or pretraining mechanism. Position performance close to Original NAME would support the usefulness of progress cues without excluding an identity contribution. If all groups perform poorly or differ by scale/seed, report that and narrow the interpretation rather than adding outcome-driven conditions.
