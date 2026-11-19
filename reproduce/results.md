# Results

Every figure in the article, recomputed.

187 of 187 figures agree with the article

## Origin, message by message (Section 3)

| Quantity | Recomputed | Article | Where | Agrees |
| --- | ---: | ---: | --- | :---: |
| Completed development runs | 18 | 18 | §3 | ✓ |
| Tasks they cover | 12 | 12 | §3 | ✓ |
| Assistant-role messages in those runs | 181 | 181 | §3 | ✓ |
| Bound to the framework | 18 | 18 | §3 | ✓ |
| Bound to the model | 163 | 163 | §3 | ✓ |
| Framework and model messages account for every assistant-role message |  | holds | §3 | ✓ |
| Model messages that are tool calls | 100 | 100 | §3 | ✓ |
| Calls in the ledger | 248 | 248 | §3 | ✓ |
| Agent calls | 163 | 163 | §3 | ✓ |
| User-simulator calls | 81 | 81 | §3 | ✓ |
| Assertion-judge calls | 4 | 4 | §3 | ✓ |
| Agent calls match model messages one to one |  | holds | §3 | ✓ |
| Initializations | 36 | 36 | §3 | ✓ |
| Tasks in the initialization control | 12 | 12 | §3 | ✓ |
| Each task received three different system prompts |  | holds | §3 | ✓ |
| Tasks whose opening is identical under all three prompts | 12 | 12 | §3 | ✓ |
| Model calls in the initialization control | 0 | 0 | §3 | ✓ |
| 36 of 36: upper bound on the rate at which a prompt alters the opening (%) | 7.9847 | 7.98 | §3, D3 | ✓ |
| Archived result files | 4 | 4 | §3 | ✓ |
| Their size (MB) | 92.7164 | 92.7 | reproduce | ✓ |
| claude-3-7-sonnet: runs | 456 | 456 | §3 | ✓ |
| claude-3-7-sonnet: assistant-role messages | 6,743 | 6,743 | §3 | ✓ |
| claude-3-7-sonnet: framework | 456 | 456 | §3 | ✓ |
| claude-3-7-sonnet: model | 6,287 | 6,287 | §3 | ✓ |
| claude-3-7-sonnet: tasks | 114 | 114 | §3 | ✓ |
| gpt-4.1: runs | 456 | 456 | §3 | ✓ |
| gpt-4.1: assistant-role messages | 5,560 | 5,560 | §3 | ✓ |
| gpt-4.1: framework | 456 | 456 | §3 | ✓ |
| gpt-4.1: model | 5,104 | 5,104 | §3 | ✓ |
| gpt-4.1: tasks | 114 | 114 | §3 | ✓ |
| gpt-4.1-mini: runs | 456 | 456 | §3 | ✓ |
| gpt-4.1-mini: assistant-role messages | 6,124 | 6,124 | §3 | ✓ |
| gpt-4.1-mini: framework | 456 | 456 | §3 | ✓ |
| gpt-4.1-mini: model | 5,668 | 5,668 | §3 | ✓ |
| gpt-4.1-mini: tasks | 114 | 114 | §3 | ✓ |
| o4-mini: runs | 456 | 456 | §3 | ✓ |
| o4-mini: assistant-role messages | 6,409 | 6,409 | §3 | ✓ |
| o4-mini: framework | 456 | 456 | §3 | ✓ |
| o4-mini: model | 5,953 | 5,953 | §3 | ✓ |
| o4-mini: tasks | 114 | 114 | §3 | ✓ |
| Archived runs | 1,824 | 1,824 | §3 | ✓ |
| Assistant-role messages in the archive | 24,836 | 24,836 | §3 | ✓ |
| Framework-written | 1,824 | 1,824 | §3 | ✓ |
| Bound to a generation record | 23,012 | 23,012 | §3 | ✓ |
| Unknown | 0 | 0 | §3 | ✓ |
| Framework share of assistant-role messages (%) | 7.3442 | 7.34 | §3 | ✓ |
| One message in | 13.6162 | 13.6 | §3 | ✓ |
| Distinct framework-written texts | 1 | 1 | §3 | ✓ |
| The first generated agent message is at turn 2 in every run |  | holds | §3 | ✓ |
| Runs opening with the framework message | 1,824 | 1,824 | §3 | ✓ |
| Clean run of 1,824: upper bound on the rate of exceptions (%) | 0.1641 | 0.16 | §3, D3 | ✓ |
| Runs whose first own action is an authentication step | 1,801 | 1,801 | §3 | ✓ |
| As a share of runs (%) | 98.7390 | 98.7 | §3 | ✓ |
| Model calls made by the census | 0 | 0 | §3 | ✓ |

## The integrity contract (Section 4)

| Quantity | Recomputed | Article | Where | Agrees |
| --- | ---: | ---: | --- | :---: |
| Tasks that carry assertions | 40 | 40 | §4 | ✓ |
| Reply types | 14 | 14 | §4 | ✓ |
| Controlled replies | 560 | 560 | §4 | ✓ |
| Valid records | 120 | 120 | §4 | ✓ |
| Valid records returned as pass | 80 | 80 | §4 | ✓ |
| Valid records returned as fail | 40 | 40 | §4 | ✓ |
| Anomalous replies | 440 | 440 | §4 | ✓ |
| Anomalous replies held as unknown | 440 | 440 | §4 | ✓ |
| Anomalous replies on which the evaluator's component reads 1 | 360 | 360 | §4 | ✓ |
| Anomalous replies on which the evaluator raises an exception | 80 | 80 | §4 | ✓ |
| Every reply type has 40 inputs |  | holds | §4 | ✓ |
| Per-row 'component reads 1' column of the table |  | holds | §4 | ✓ |
| Anomalies accepted with strict parsing and the type check alone | 200 | 200 | §4 | ✓ |
| After adding the count | 95 | 95 | §4 | ✓ |
| After adding identity | 40 | 40 | §4 | ✓ |
| After adding the binding | 0 | 0 | §4 | ✓ |
| Tasks without assertions, returned as not applicable | 74 | 74 | §4 | ✓ |
| Median time of the check (microseconds) | 10.9000 | 10.9 | §4 | ✓ |
| The contract in src/icfa returns the tabled status on all 14 reply types |  | holds | §4 | ✓ |
| A conjunction over no results is true |  | holds | §4 | ✓ |

## Evidence at the moment of action (Section 5)

| Quantity | Recomputed | Article | Where | Agrees |
| --- | ---: | ---: | --- | :---: |
| Runs reviewed | 18 | 18 | §5 | ✓ |
| Runs that drew a diagnosis | 6 | 6 | §5 | ✓ |
| Diagnoses | 8 | 8 | §5 | ✓ |
| Criterion judgments on which the two reviewers agreed | 20 | 20 | §5 | ✓ |
| Criterion judgments in all | 24 | 24 | §5 | ✓ |
| Each combined label follows from its three criterion labels |  | holds | §5 | ✓ |
| Diagnoses supported on all three questions | 0 | 0 | §5 | ✓ |
| Insufficient | 6 | 6 | §5 | ✓ |
| Unsupported | 2 | 2 | §5 | ✓ |
| Insufficient, gate rejects | 3 | 3 | §5 | ✓ |
| Insufficient, gate abstains | 2 | 2 | §5 | ✓ |
| Insufficient, gate admits | 1 | 1 | §5 | ✓ |
| Unsupported, gate rejects | 2 | 2 | §5 | ✓ |
| Gate rejects | 5 | 5 | §5 | ✓ |
| Gate abstains | 2 | 2 | §5 | ✓ |
| Gate admits | 1 | 1 | §5 | ✓ |
| Kept out by the gate | 7 | 7 | §5 | ✓ |
| Zero in eight: upper bound on the share of fully supported diagnoses (%) | 31.2344 | 31.2 | §5, D3 | ✓ |
| The admitted diagnosis criticizes the opening sentence at turn 0 |  | holds | §1, §5 | ✓ |
| The judge's reason contains 'The actor controlled that response' |  | holds | Summary, §1 | ✓ |
| The reviewer's claim and correction are quoted as written |  | holds | §1 | ✓ |
| Its origin is the framework and the agent's first generated message is at turn 2 |  | holds | §1, §5 | ✓ |
| Runs in the later batch | 4 | 4 | §5 | ✓ |
| Further diagnoses that reached the gate | 2 | 2 | §5 | ✓ |
| Of which rejected | 2 | 2 | §5 | ✓ |

## What the origin gate adds to a judge (Section 6)

| Quantity | Recomputed | Article | Where | Agrees |
| --- | ---: | ---: | --- | :---: |
| Cards | 12 | 12 | §6 | ✓ |
| Minimal pairs | 6 | 6 | §6 | ✓ |
| Supported cards | 5 | 5 | §6 | ✓ |
| Unsupported cards | 3 | 3 | §6 | ✓ |
| Insufficient cards | 4 | 4 | §6 | ✓ |
| Supported, judge admits | 5 | 5 | §6 | ✓ |
| Unsupported, judge rejects | 3 | 3 | §6 | ✓ |
| Insufficient, judge admits | 2 | 2 | §6 | ✓ |
| Insufficient, judge rejects | 1 | 1 | §6 | ✓ |
| Insufficient, judge abstains | 1 | 1 | §6 | ✓ |
| Admitted by the judge | 7 | 7 | §6 | ✓ |
| Rejected by the judge | 4 | 4 | §6 | ✓ |
| compound_admission in src/icfa reproduces every card's outcome |  | holds | §6 | ✓ |
| Admitted after origin | 6 | 6 | §6 | ✓ |
| Supported, admitted after origin | 5 | 5 | §6 | ✓ |
| Insufficient, admitted after origin | 1 | 1 | §6 | ✓ |
| Unsupported, admitted after origin | 0 | 0 | §6 | ✓ |
| The origin pair: one claim, one sentence, two producers |  | holds | §6 | ✓ |
| The judge admitted both members of the origin pair |  | holds | §6 | ✓ |
| Origin routes the framework member out and passes the model member on |  | holds | §6 | ✓ |
| Judge alone: t = 5/5 and f = 2/7 |  | holds | §6 | ✓ |
| With origin: f = 1/7 and t unchanged |  | holds | §6 | ✓ |
| Judge alone: share of admitted diagnoses that are supported (%) | 71.4286 | 71.4 | §6, D4 | ✓ |
| With origin (%) | 83.3333 | 83.3 | §6, D4 | ✓ |
| Precision rises exactly when t > f, on a grid of 8,000 gates |  | holds | §6, D4 | ✓ |
| Evidence gate: input tokens over the 8 diagnoses | 130,049 | 130,049 | §6, §8 | ✓ |
| Per diagnosis | 16256.1250 | 16,256 | §6 | ✓ |
| Per card | 15242.5000 | 15,243 | §6 | ✓ |
| Episodes it took to test the native arm's candidate | 4 | 4 | §6 | ✓ |
| Their input tokens | 1,076,788 | 1,076,788 | §6 | ✓ |
| Gate call as a share of one candidate test (%) | 1.5097 | 1.5 | §6 | ✓ |
| Diagnoses screened per prevented candidate at break-even | 66.2389 | 66 | §6, D6 | ✓ |

## Admission is not acceptance (Section 7)

| Quantity | Recomputed | Article | Where | Agrees |
| --- | ---: | ---: | --- | :---: |
| Training tasks | 2 | 2 | §7 | ✓ |
| Validation tasks | 2 | 2 | §7 | ✓ |
| Test tasks | 6 | 6 | §7 | ✓ |
| Proposals per arm | 1 | 1 | §7 | ✓ |
| Native arm: training tasks the seed passed | 1 | 1 | §7 | ✓ |
| Length of the native arm's candidate (characters) | 2,214 | 2,214 | §7 | ✓ |
| Native arm: training tasks the candidate passed | 2 | 2 | §7 | ✓ |
| Validation, official reward: candidate | 2 | 2 | §7 | ✓ |
| Validation, official reward: seed | 2 | 2 | §7 | ✓ |
| Validation, qualified: candidate | 1 | 1 | §7 | ✓ |
| Validation, qualified: seed | 2 | 2 | §7 | ✓ |
| The candidate's closing message promises the refund deadline, as quoted |  | holds | §7 | ✓ |
| Both reviewers marked that answer unsound |  | holds | §7 | ✓ |
| The strategy texts hash to the identities in the evidence |  | holds | §7 | ✓ |
| The acceptance rule in src/icfa keeps the seed |  | holds | §7 | ✓ |
| Its reasons: the optimizer kept the seed, the qualified count is not higher, a qualified task regressed |  | holds | §7 | ✓ |
| The rule keeps the seed even if the optimizer had selected the candidate |  | holds | §7, D9 | ✓ |
| Token cap of the acceptance rule (times the seed's cost) | 1.2500 | 1.25 | §7 | ✓ |
| Admitted arm: training tasks the seed passed | 2 | 2 | §7 | ✓ |
| Admitted arm: training tasks the candidate passed | 2 | 2 | §7 | ✓ |
| The admitted arm's candidate was not adopted |  | holds | §7 | ✓ |
| Tasks on which the two arms ran the seed | 4 | 4 | §7 | ✓ |
| Tasks whose outcome differed between the two runs of the seed | 2 | 2 | §7 | ✓ |
| Every arm's selected strategy is the seed |  | holds | §7 | ✓ |
| Completed test runs | 18 | 18 | §7 | ✓ |
| Passed on the official reward | 8 | 8 | §7 | ✓ |
| Qualified | 5 | 5 | §7 | ✓ |
| Passed and did not qualify | 3 | 3 | §7 | ✓ |
| They are the three runs of one task |  | holds | §7 | ✓ |
| In each of them the agent names a poem and its author and scores 1 |  | holds | §7 | ✓ |
| Archived runs of that task | 16 | 16 | §7 | ✓ |
| In which the agent names the poem | 10 | 10 | §7 | ✓ |
| Of those, with the full official reward | 9 | 9 | §7 | ✓ |
| In one run of the paired batch both reviewers confirm the simulated customer departed from its instructions |  | holds | §7 | ✓ |
| Episodes completed in the paired study | 4 | 4 | §7 | ✓ |
| Episodes planned | 120 | 120 | §7 | ✓ |

## What it cost (Section 8)

| Quantity | Recomputed | Article | Where | Agrees |
| --- | ---: | ---: | --- | :---: |
| Reviewer: calls | 18 | 18 | §8 | ✓ |
| Reviewer: input tokens | 284,840 | 284,840 | §8 | ✓ |
| Reviewer: output tokens | 6,894 | 6,894 | §8 | ✓ |
| Evidence gate on diagnoses: calls | 8 | 8 | §8 | ✓ |
| Evidence gate on diagnoses: output tokens | 4,315 | 4,315 | §8 | ✓ |
| Evidence gate on cards: calls | 12 | 12 | §8 | ✓ |
| Evidence gate on cards: input tokens | 182,910 | 182,910 | §8 | ✓ |
| Evidence gate on cards: output tokens | 4,128 | 4,128 | §8 | ✓ |
| Optimization: calls | 240 | 240 | §8 | ✓ |
| Optimization: input tokens | 3,589,164 | 3,589,164 | §8 | ✓ |
| Optimization: output tokens | 27,027 | 27,027 | §8 | ✓ |
| Final test: calls | 273 | 273 | §8 | ✓ |
| Final test: input tokens | 3,689,217 | 3,689,217 | §8 | ✓ |
| Final test: output tokens | 21,717 | 21,717 | §8 | ✓ |
| Interrupted test runs | 1 | 1 | §8 | ✓ |
| Paired batch: calls | 61 | 61 | §8 | ✓ |
| Paired batch: input tokens | 893,326 | 893,326 | §8 | ✓ |
| Paired batch: output tokens | 9,586 | 9,586 | §8 | ✓ |
| Model calls made by the integrity experiment | 0 | 0 | §8 | ✓ |

## The gate code

| Quantity | Recomputed | Article | Where | Agrees |
| --- | ---: | ---: | --- | :---: |
| Tests in the suite | 137 | 137 | Problem and Approach | ✓ |
