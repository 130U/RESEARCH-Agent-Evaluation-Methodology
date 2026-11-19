# Design notes

Why each piece of the design is the way it is, what it was chosen over, and how the experiments were set up.
Proofs are in [derivations](derivations.md); figures are recomputed in [results](../reproduce/results.md).

## Choices and the alternatives they beat

| Choice | Alternative | Why | When I would switch |
| --- | --- | --- | --- |
| **Admit diagnoses one by one** | Feed the optimizer every reviewer diagnosis | None of the eight diagnoses the reviewer produced was supported on all three questions (§5) | A reviewer with a measured precision high enough that Equation (6.3) turns negative |
| **Admissibility relative to the intervention** | A single verdict of true or false per diagnosis | The greeting diagnosis is right on the policy and has no route to its target through the prompt ([D1](derivations.md#d1-reach-and-zero-effect-outside-it)); for a framework review it is the right input | No case: a single intervention is the special case of one reach |
| **Origin from execution records** | Origin from the role label, or from a judge's reading | The producer is not identifiable from the transcript ([D2](derivations.md#d2-the-producer-is-not-identifiable-from-the-transcript)); the judge wrote "The actor controlled that response" about a framework message | A framework that signs each message with its producer, which makes the record part of the transcript |
| **Positive rules, unknown otherwise** | Treat any assistant-role message without a framework marker as the model's | A default assigns blame for what the records do not show; in the archive the rules decided 24,836 of 24,836 messages without one | No case |
| **Route a refused diagnosis** | Discard it | Every refusal has a least intervention that reaches it ([D7](derivations.md#d7-admissibility-is-monotone-and-every-refusal-has-an-address)); the framework's owner is the reader who can use it | No case |
| **Judge on the action-time view** | Give the judge the full trace and the task's reference | Knowledge of the outcome changes what looks foreseeable; two diagnoses in §5 rested on a fallback not yet mentioned and on the task's reference actions | Diagnoses about outcomes, such as a wrong final database state, where the outcome is the evidence |
| **Three outcomes: admit, reject, abstain** | Admit or reject | A refuted claim and an undecided one need different handling; in §5 two of eight were abstentions | No case |
| **Pass the admitted diagnosis verbatim** | Let the gate rewrite or strengthen it | The arms then differ in selection alone, so an effect is attributable to selection | A separate experiment on rewriting, with its own control |
| **An empty admission stays empty** | Fall back to the unfiltered feedback | A fallback would re-admit exactly what the gate refused | No case |
| **Integrity first, with unknown as a status** | Trust any reply that parses | The evaluator's component read 1 on 360 of 440 anomalous replies ([D8](derivations.md#d8-what-each-clause-of-the-integrity-contract-removes)) | No case |
| **Free gates before the judge** | Judge first | A conjunction commutes and its cost does not: order by cost per unit of refusal ([D6](derivations.md#d6-when-a-gate-pays-and-the-order-of-gates)) | Experiments that need each gate's decision on the full set, as in §6 |
| **Acceptance on qualification** | Acceptance on the official reward | 3 of 8 official passes in the final test did not qualify; a candidate passed validation while promising a deadline the policy does not give | Tasks whose reward checks every statement the agent makes |
| **Strict improvement with no regression** | Accept on a tie, or on a net gain | Two of four tasks changed outcome between two runs of the identical seed strategy; a tie or a one-task swap is inside that noise | Validation sets large enough to put an interval on the difference |
| **Simulated-user validity as an acceptance term** | Assume the customer follows its instructions | In the paired batch a customer agreed to a cancellation reason its instructions contradict, and the database was written with it | A user simulator with a measured fidelity score |

## The gates and their exits

```text
diagnosis d about message m, for intervention I
│
├─ 1 integrity     record incomplete or misfiled ........ exit: unknown evaluation   (to: evaluator owner)
│                  task has no assertions ................ status: not applicable
├─ 2 origin        m produced outside Reach(I) ........... exit: routed              (to: owner of the producer)
│                  records do not decide ................. exit: origin unknown      (to: logging)
├─ 3 evidence      claim refuted on the action-time view . exit: rejected
│                  undecided ............................. exit: abstained
│                  supported, responsible, correctable ... admitted, verbatim
│
└─ optimizer writes a candidate from admitted diagnoses
   │
   └─ 4 acceptance  qualifies on more tasks, regresses on none,
                    no new critical violation, within the token cap ... adopt
                    anything else, including unknown .................. keep the seed
```

Gates 1 and 2 are deterministic functions of records. Gate 3 calls a model once. Gate 4 runs the candidate.

## What an execution record has to hold

Origin is decidable when the system keeps, for every model call, a ledger entry with five things: a call
identity, the role of the call (agent, user simulator, judge), its position in the run, the request it was given,
and its structured output. A generated message then carries the call identity and is the model's when that
identity is unique in the ledger and the message's text, tool names and tool arguments equal the entry's output.
A framework message is recognized by the framework's own source: the branch that writes it, the constant it
writes, and the fact that the first ledger entry is another component reading that constant.

The public archive keeps less, a per-message generation record with usage, raw response and cost, and that was
enough to decide every message. A system that keeps neither can still run gates 1, 3 and 4, and gate 2 returns
origin unknown for everything.

## How the experiments were set up

**Pinned parts.** τ²-bench at `2174a603f6d014ef94473ffa95957f6ce27100db`, GEPA at
`15ee314f9c7d34ec153b809d401f42f55c4dcd76`, and one model, gpt-5.6-sol at low reasoning effort, for the agent, the
simulated customer, the benchmark's reviewer, the assertion judge and the evidence gate. The model's sampling seed
is not controllable, so two runs of one strategy are two draws; the pilot shows what that is worth.

**The intervention.** One component is editable: a strategy text of at most 6,000 characters appended to the
agent's system prompt. The policy, the tools, the orchestrator and the user simulator are fixed.

**Labels before decisions.** Reference labels for the eight natural diagnoses and reference tiers for the twelve
cards were fixed before the evidence gate was called. They were assigned by model reviewers working
independently: two reviewers and an adjudication for the diagnoses, the designed tier confirmed from an
anonymized packet for the cards. The run qualifications of §7 come from two independent model reviewers, and a
disagreement between them leaves the run unknown.

**Each gate observed on the full set.** In the experiments the evidence gate ran on every diagnosis, and origin
was intersected afterwards. That is the costlier order, and it is the one that lets §6 report what the judge does
alone and what origin adds.

**The optimizer's settings.** One proposal per arm, strict improvement on training, GEPA's merge step and its
evaluation cache off, and its rule that skips reflection when the parent scores perfectly switched off, so that
both arms write a candidate. Both arms pass the same instance-data projection, which removes identifiers and
record-specific values before anything reaches the reflection model.

**Splits.** Training on tasks 76 and 0, validation on 16 and 19, test on 36, 40, 62, 68, 77 and 79. Tasks that
share entities were kept in the same split.

**Stopping rules.** A run whose transport reports an error is not accepted and not repeated, and a batch in which
the simulated customer departs from its instructions ends. The final test completed 18 of 36 planned runs before
a network interruption on the nineteenth, and the paired study completed 4 of 120 planned episodes before a
customer agreed to a reason its instructions contradict. Counts in the article are over completed runs, and the
planned totals are in the evidence files.

## What the adapter guarantees

The seam to GEPA is one class with two modes. In `native` mode the reflection model reads the reviewer's
diagnoses; in `admitted` mode it reads the diagnoses a named filter returns. The adapter enforces four things,
each with a test:

1. The two modes build the reflective record through one code path, with the same inputs, outputs and score, and
   differ only in the diagnoses it carries, so the treatment is the selection.
2. An empty admission is reported as "no admissible feedback" and never replaced by the reviewer's feedback.
3. A stored verdict is replayed through the admission contract before it is used, and a verdict bound to another
   diagnosis, another view or another episode is refused.
4. The gate's reasons and the refused diagnoses never reach the reflection model.

## What to monitor in operation

| Quantity | What it tells | Measured here |
| --- | --- | --- |
| Share of assistant-role messages outside the prompt's reach | How much of the transcript the prompt cannot change | 7.34% in the archive, 18 of 181 in my runs |
| Share of diagnoses routed by origin | How often feedback is addressed to the wrong component | 1 of 8 natural diagnoses |
| Admission rate of the evidence gate | What fraction of reviewer output survives | 1 of 8 natural diagnoses, 7 of 12 cards |
| Unknown rate of the integrity contract | Whether the evaluator is returning complete records | 0 of 120 valid records, 440 of 440 anomalous ones |
| Qualified over official passes | What the score leaves unchecked | 5 of 8 in the final test |
| Outcome changes between runs of one strategy | The noise floor for any accepted gain | 2 of 4 tasks |

## Next

1. **The downstream comparison.** The paired design gives both arms the same parent runs and the same reviewer
   output, tests every candidate either arm writes on common validation tasks, and counts an arm as treated only
   when its reflective input differs. It measures what admission does to the optimizer's score and cost.
2. **A labelled set for the judge.** The evidence gate's own error is in the middle tier: it admitted two of four
   diagnoses whose evidence was insufficient. A set of diagnoses labelled by people, including fully supported
   natural ones, puts numbers on $`t`$ and $`f`$ for Equation (6.1).
3. **Origin rules for other frameworks.** The rules here cover one orchestrator. The same three questions apply
   to any system that inserts messages, rewrites tool results or injects reminders: which component wrote this,
   from which constant or call, and can the editable component reach it.
4. **Wider interventions.** With the framework editable, the greeting diagnosis is admissible and the routing
   lattice of [D7](derivations.md#d7-admissibility-is-monotone-and-every-refusal-has-an-address) has a second
   level to deliver to.
