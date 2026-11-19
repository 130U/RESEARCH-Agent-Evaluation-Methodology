# Evidence

The measurements behind the article. Every figure in it is recomputed from these files by
[`reproduce/run_all.py`](../reproduce/run_all.py).

| File | What it holds | Article |
| --- | --- | --- |
| [`archive_census.json`](archive_census.json) | Origin of every assistant-role message in the 1,824 published τ²-bench retail runs, per file and in total; the first action of each run; the 16 runs of task 62. Written by [`reproduce/archive_census.py`](../reproduce/archive_census.py) | §3, §7 |
| [`origin_audit.json`](origin_audit.json) | The 181 assistant-role messages of 18 development runs by producer, the call ledger's composition, and the 36 initializations of 12 tasks under three system prompts, with the hash of each prompt and each opening | §3 |
| [`integrity_experiment.json`](integrity_experiment.json) | 560 controlled replies to the benchmark's assertion evaluator: for each, what the evaluator's component read and what each clause of the contract returned; 74 tasks without assertions | §4 |
| [`natural_diagnoses.json`](natural_diagnoses.json) | The eight diagnoses the benchmark's reviewer produced, verbatim, with both reviewers' labels on three criteria, the final labels and the gate's decision and reason | §1, §5 |
| [`admission_cards.json`](admission_cards.json) | Twelve diagnoses in six minimal pairs: claim, correction, criticized action, reference tier, the judge's decision, the producer and the outcome after origin | §6 |
| [`candidate_pilot.json`](candidate_pilot.json) | One optimization pass per arm with GEPA: the strategies executed, each episode's reward and qualification terms, the selection decisions, and the 36 planned units of the final test | §7, §8 |
| [`pilot_dialogues.json`](pilot_dialogues.json) | Every message and tool call of the 14 optimization episodes and 18 completed test runs, with two reviewers' verdicts on each | §7 |
| [`paired_batch.json`](paired_batch.json) | The first four runs of the paired study, the reviewer's diagnoses on them and the gate's decisions | §5, §7 |

## Reading the fields

**Arms.** `seed` is the unoptimized seed strategy, `native` is GEPA reflecting on the reviewer's diagnoses, and
`admitted` is GEPA reflecting on admitted diagnoses only.

**Origin.** `framework_seed` is a message the orchestrator wrote, `model_agent` one the model generated,
`non_agent` a user or tool message, and `unknown` anything the rules do not decide. `reachable` says whether the
system prompt is upstream of the message.

**Qualification.** A run is `success` under `official` when the benchmark's reward is 1. It is `success` under
`qualification` when, in addition, its evaluation record is complete, both reviewers find the answer sound and the
simulated customer valid, and neither finds a critical violation. A disagreement between the reviewers leaves the
run `unknown`.

**Labels.** Reference labels and tiers were assigned by model reviewers working independently of each other and
were fixed before the gate they are compared with was called. `reviewer_a` and `reviewer_b` are the two reviewers.

**Strategies.** A strategy is identified by the SHA-256 of its text. The seed is
`86aa62048c4845c3564aba229035c6bab5cbe20057b36108abbb5c8407ac0961`.

**Data.** Customers, orders, addresses and products are those of the public benchmark. Token counts are the
model's reported usage per call.
