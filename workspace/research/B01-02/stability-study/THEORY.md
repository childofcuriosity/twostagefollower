# What does the product of two subtasks test?

This discussion concerns a fixed tool library with correct order supplied in the input. The name model chooses the next tool and Done; the operation model generates within-tool operations and numbers. The analysis idealizes this experiment and is not evidence of internal model structure.

## Distinguish three success events

- A: in a name-component test, the program correctly executes selected tools and the name model makes every required call and terminates correctly.
- B: in an operation-component test, the program supplies required correct names in order and the operation model correctly expands every required call.
- C: the two models actually run together, without program-supplied correct answers, and complete the whole task correctly.

All events are defined for the same input. Primary comparisons still use accuracy under each training condition and actual C, rather than replacing execution with paired both-correct rates from separate tests.

## A property with explicit assumptions

If decoding is deterministic, identical input-token prefixes always yield identical outputs, and program-supplied correct segments have exactly the same tokenization as correct generated segments, then along the correct execution path:

\[
C(x)=A(x)B(x).
\]

Consider the first error. If it occurs in a name, prior history is correct, so the name model also fails at the identical prefix in the program-correct-execution test. If it occurs in operations, the operation model likewise fails at the same prefix in the correct-name test. Conversely, if both components are always correct along their respective correct histories, their composition remains correct step by step through termination.

This is a property of serial composition and strict whole-trajectory correctness. It also applies when both components reuse one jointly trained model; independent training is not required.

Actual experiments involve dynamic batches, BF16 numerical differences, and potentially different tokenizations of the same text. This idealized property cannot replace real composition calibration. We ran all compositions, retained actual token histories, and separately disclosed cases where the first divergence occurred in an unchanged component.

## Multiplying accuracies needs another assumption

Under those idealized conditions, fix one training seed and task length:

\[
P(C)=P(A)P(B)+\operatorname{Cov}(A,B).
\]

A product close to full success supports weak association between the two kinds of success/failure under this task distribution. It does not imply independent internal modules or, alone, better learning from separate training. Disagreement may also involve prefix/decoding differences and cannot all be attributed to learning dependence without interface checks.

Task length changes both subtask difficulties; seeds also change both abilities. Multiply within each seed and length, then aggregate with the target task-distribution weights. Pooling lengths and seeds before multiplication introduces shared-factor associations. This study reports both directly pooled and length-stratified results, without selecting lengths by test performance.

## What current evidence means

At fixed 512 steps with length stratification, separate training predicts 56.04% versus actual 55.83% at 3B, and 93.20% versus 93.19% at 32B. Joint models are similarly close:41.17% versus 40.49% at 3B,85.43% versus 85.35% at 32B. Decomposition is therefore a useful performance diagnostic; learning benefits from separation require training-condition and actual component-replacement controls.

A single-tool correct target is completely determined by the current tool and four-digit state. These two values suffice for operation output; prior trajectories and future tools are unnecessary for that tool. Local operation inputs are therefore a valid capability test without supplying answers. They jointly change visible history, future-tool information, and task-length format, so effects cannot be isolated to one attention mechanism or token length.

After changing operation inputs, B must be interpreted under matched new inputs. Old full-history B cannot remain the operation-ability estimate for the new method. Real-agent state may not fit such a small interface; transfer requires separate validation.
