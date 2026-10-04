# B01-02 mechanism analysis: supported and unsupported claims

Status: pre-experiment analysis. The user authorized joint theory/experiment completion followed by review.

## 1. Formalization

Input domain X = (Z/10Z)^4. Six primitives permute coordinates, negate uniformly, add one uniformly, or add one at endpoints. Every program is affine: f(x)=Ax+b (mod 10). Abstraction a_i is a model-proposed length-2–3 primitive sequence, with no new primitive. For chain c=(i1,..., ik), target y=f_ik∘...∘f_i1(x). Training k∈{1,2}; primary tests k∈{3,4,5}.

The closed-domain verifier defines the mathematical environment. It reliably checks program outputs, totality, and equivalence there, not natural-language judgments of research value.

## 2. Why exact semantic deduplication works

For these affine functions, f(0) and f(e_j)-f(0), j=1..4 determine b and every column of A. Two programs share these five values exactly when they agree on all 10^4 inputs. signature() uses this property, not approximate equivalence from a small sample.

This requires genuinely affine primitives. Sorting, branching, multiplication, or other additions require a revised verifier. Independent property checks compare reconstructed signature outputs with direct execution to guard against implementation errors.

AST separation alone fails: rev; rev and an empty program differ syntactically but coincide semantically; inc; neg and other sequences can cancel. Primary tests exclude signatures equivalent to any training chain in both original and permuted worlds. IID tests permit training chains with fresh inputs and are reported separately.

## 3. Primary controls add no information

Prompt P specifies macro-call order. T_flat inserts neutral step labels at boundaries while retaining every primitive/state; T_macro replaces boundary j with macro name j from P. Boundaries are unchanged, so (P, T) deterministically converts either representation into the other, with identical answers.

There is no information-theoretic supervision advantage. With unlimited capacity/ideal optimization, this treatment does not imply better Bayes-optimal accuracy. Finite-budget differences concern representation organization, auxiliary prediction, and optimization paths, not additional truth. This makes the control suitable for screening structural utility under finite training.

The treatment also changes supervised-token identities and gradients, not just internal representations. Equal token counts do not identify a specific neural mechanism. Later boundary-label loss masking, hidden-state probes, or activation interventions could distinguish representation formation from simple name copying. Retain shuffled controls here and consider refinements if the core effect holds.

## 4. Intervention predictions

Name intervention applies fixed permutation π consistently to training/test a_i names, preserving definitions and input distributions. Large changes implicate token priors, name shortcuts, or unstable optimization. Unannounced test-only renaming cannot fairly establish failure to learn semantics.

Semantic intervention fixes names and cyclically permutes their primitive definitions, retraining paired models and scoring new-world truth. Where targets differ, report new-semantic accuracy and old-semantic matching separately. This tests training-semantics effects on behavior, not independently editable neural concepts.

Separate structural utility from internalization. Higher no-library accuracy supports operational parameter learning; outperforming information-matched flat supports additional structural utility. Reproducing learned definitions does not establish useful concept invention in unknown domains.

## 5. Evidence and limits of self-proposal

Abstractions must appear in actual base-model proposal outputs, with prompts, raw text, parsing, totality checks, and discovery-trace frequencies retained. Neither assistant nor human may fill in successful proposals to replace failures. Protocol-assigned neutral names support token matching/permutation.

Fixing one proposal library and studying internalization does not test improving proposal policies over rounds. Constructing tasks around that library makes it naturally useful and cannot establish better discovery than random/manual strategies. This deliberately bounded mechanism screen would need independent task distributions and matched-search-budget trained/untrained proposals in new domains to address learning innovation.

## 6. Reading results

| Observation | Supported interpretation | Unsupported interpretation |
|---|---|---|
| Low IID too | Current training/task is unlearnable or insufficient | Innovation capability does not exist |
| High IID, low semantically isolated OOD | Short chains learned; composition extrapolation fails | Composable abstractions mastered |
| macro≈flat | This boundary supervision adds little benefit | Every abstraction-internalization method fails |
| Macro beats only shuffled | Removing noise helps | Superiority to valid direct-trace training |
| Macro consistently beats flat and survives renaming | Structural-utility signal worth pursuing | Internal concept mechanism proved |
| Semantic intervention follows new definitions | Parameter behavior depends on training semantics | General innovation or multi-round recursive gains |

## 7. Theoretical context and differences

[LILO](https://arxiv.org/html/2310.19791v2) covers self-generated programs, library compression, and naming; [Notes to Self](https://arxiv.org/html/2607.20372v1) studies abstractions at training but not inference; [SPEE](https://arxiv.org/html/2608.02139v1) studies privileged experience internalization; [Rethinking Continual Experience Internalization](https://arxiv.org/html/2606.04703v1) analyzes stability. This round delivers controlled records of information, semantics, and training-world interventions, without claiming publication-level novelty.

## 8. Additional literature review during implementation: higher novelty risk

[From Reasoning Traces to Reusable Modules (2606.18089)](https://arxiv.org/html/2606.18089v1) already studies module/routing identification on synthetic strings, transfer to unseen compositions, and SFT/RL roles. Reusable modules from traces, synthetic composition, and length extrapolation are not original here. The remaining narrow comparison is information/token-matched macro-boundary organization and training-world interventions with a self-proposed library. Its value depends on effects and further review, not a promised paper.

[Lake & Baroni, Nature 2023](https://www.nature.com/articles/s41586-023-06668-3) already studies systematic composition through meta-learning. Random name permutation is a control, not a new concept.

Following this review, run only preregistered small-model screening rather than costly RL/large-model expansion. Weak primary effects warrant dropping this supervision scheme; even positive signals require clarifying the difference before paper development.

## 9. Closure of the actual proposed library

Actual proposals retain no ends operation for endpoint-only increments. All nine macros have f(x)=sPx+b·1 (mod 10), with s∈{±1}, coordinate permutation P, and b∈Z_10. At most 2×24×10=480 functions exist. Exact-signature closure reaches all 480; shortest macro depths 0/1/2/3/4/5 contain 1/9/52/166/198/54 functions.

Training depth ≤2 covers 62 semantics, the sum of the first three counts. Initial test construction failed because requested cross-world independent semantics exceeded library capacity, not from network/GPU issues. Multiple inputs per composition preserve separation but require composition-level statistical units rather than claims of independent examples.

This bounds extrapolation: the final experiment screens training organization in a finite 480-function space, not open-ended concept discovery.

## 10. Post hoc mechanism literature: content addressing is an existing explanation

[Your Context Is Not an Array (COLM 2024)](https://arxiv.org/html/2408.05506v1) connects length-generalization failures to indexing/random access, using mnemonic content-addressing markers and constant, misaligned, and cyclic variants. [Exploring Length Generalization (2022)](https://arxiv.org/abs/2207.04901) and [Show Your Work (2021)](https://arxiv.org/abs/2112.00114) study scratchpads/length generalization. Matching function names across input/traces and reduced early stopping are close to existing work, not a new general innovation mechanism.

External routing restoring flat performance and partial generalization from random call tags motivate distinguishing internal function mapping from autonomous routing without identifying neural circuits uniquely. Models were not trained to propose better abstractions in new domains here; the central learning-innovation claim remains unestablished.
