# What changes in local operation context?

This is a protocol illustration, not an experimental result or a selected success case.

The task supplies four digits and tool order, for example input `1 2 3 4` with `red blue black`. Tools are fixed: `red` rotates left then increments every digit; `blue` reverses, rotates left, then increments; `black` increments then swaps the first two digits. The model must output every operation and numerical state.

The same existing model weights are used before and after intervention. Only context supplied during operation generation changes.

## Names still see the full task

The model sees the original four digits, complete user-supplied tool list, and prior actual outputs. Suppose it first emits `red:`, executes it to obtain `3 4 5 2`, then emits `blue:`.

The program does not choose the next tool for the name component. If the model emits `black:` instead of `blue:`, it is not replaced with the correct name.

## Operations receive only the selected tool and actual current state

The ordinary version passes all previous history to the operation model. The new version constructs a single-tool input:

```text
Input: 3 4 5 2
Functions: blue
Trace:
blue:
```

Actual inputs still include primitive-operation descriptions and format requirements from the original protocol; only the changed task portion is shown here. `blue` comes from the newly emitted name, and `3 4 5 2` is the final state actually output by the preceding tool.

The model should next generate:

```text
rev 2 5 4 3
rot 5 4 3 2
inc 6 5 4 3
EndTool
```

These correct operations illustrate the protocol; inference never supplies them in advance. Actual model outputs are recorded and appended to global history, after which the name model chooses the next call or termination.

## Errors receive no correction

If the previous output is actually `9 9 9 9`, the operation component receives `Input: 9 9 9 9`. The script does not restore the correct state. Even if later computation is correct, the earlier error fails the whole task. Early `Done` terminates normally and fails; execution is not forced to the requested length.

The program reads generated text, constructs the next input, and checks format. It does not calculate correct operations during inference to fill in answers.

## What this can answer

The same joint model also receives this input construction. If it recovers too, recovery cannot all be credited to separate training. Specialist gains after matching input construction would instead support complementarity.

The intervention removes both prior trajectories and the full remaining-tool list from the operation component, while converting input to the single-tool format seen in training. It tests operation-context scope, not the isolated causal effect of context token length.

This remains a controlled task with correct tool order supplied in advance. It neither tests real-agent autonomous planning nor proves that AI has learned scientific innovation.
