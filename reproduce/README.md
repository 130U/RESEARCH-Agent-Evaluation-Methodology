# Reproduce

```bash
python reproduce/run_all.py          # every figure in the article, under a second
python -m unittest discover -s tests # the gates, 137 tests
python reproduce/archive_census.py   # rebuild the archive census from the published files
```

Python 3.12 or later. `run_all.py` and the gates use the standard library only; the two adapter test modules need
GEPA at its pinned revision (`pip install "git+https://github.com/gepa-ai/gepa@15ee314f9c7d34ec153b809d401f42f55c4dcd76"`)
and are skipped without it. `run_all.py` recomputes every figure in the article from the files in
[`evidence/`](../evidence/README.md), compares each with the text, writes [`results.md`](results.md) and exits
with status 1 if any figure disagrees. The tests and `run_all.py` run on every push.

## What is recomputed, and from what

| Part of the article | How it is recomputed | Model calls |
| --- | --- | ---: |
| §3 Archive census | `archive_census.py` downloads the four result files published at τ²-bench revision `2174a60`, checks each against its Git blob hash, and classifies every assistant-role message with `icfa.origin.classify_archived_message` | 0 |
| §3 Origin audit and initialization control | Counted from `evidence/origin_audit.json`: per task, three distinct prompt hashes and one opening hash | 0 |
| §4 Integrity contract | Every count from the 560 rows of `evidence/integrity_experiment.json`; the contract's status on each of the 14 reply types is rerun with `icfa.integrity` | 0 |
| §5 Natural diagnoses | The cross-table is rebuilt from the eight rows of `evidence/natural_diagnoses.json`, and each combined label is rederived from its three criterion labels | 0 |
| §6 Minimal pairs | Each card's outcome is rerun through `icfa.admission.compound_admission`; precision comes from `icfa.gate_math` in exact fractions | 0 |
| §7 Acceptance | `icfa.acceptance.decide_strategy` is rerun on the validation rows of `evidence/candidate_pilot.json`; quotations are located in `evidence/pilot_dialogues.json` | 0 |
| §8 Cost | Summed from the usage fields of the evidence files | 0 |
| Clean-run bounds | `icfa.gate_math.clean_run_upper_bound` | 0 |

The runs that produced the evidence called a model: gpt-5.6-sol at low reasoning effort, for the agent, the
simulated customer, the benchmark's reviewer, the assertion judge and the evidence gate. Their records are in
`evidence/`, and the design of each experiment is in the [design notes](../docs/design-notes.md).

## The archive census

```bash
python reproduce/archive_census.py --cache /path/to/keep/the/files
```

The four files total 92.7 MB and are kept outside the repository. Each is verified before it is read:

| File | Git blob SHA-1 | Bytes |
| --- | --- | ---: |
| `claude-3-7-sonnet-20250219_retail_default_gpt-4.1-2025-04-14_4trials.json` | `1b0e345db5bd9ae5cecfc70ff399f590be70c4f8` | 24,908,843 |
| `gpt-4.1-2025-04-14_retail_default_gpt-4.1-2025-04-14_4trials.json` | `b30d695834f16ddbb114e254e9fc35376d819f6b` | 22,044,059 |
| `gpt-4.1-mini-2025-04-14_retail_base_gpt-4.1-2025-04-14_4trials.json` | `8a55836aa5e9ed735c9900c0e357b1dd80f71c28` | 23,697,012 |
| `o4-mini-2025-04-16_retail_default_gpt-4.1-2025-04-14_4trials.json` | `bfd1be3546169e95d47f49c8b6fdf59e93a20188` | 22,066,527 |

The classification rules are positive rules. A message with a generation record (token usage and a raw model
response) is the model's. The orchestrator's opening constant at turn 0, with no generation record, zero cost and
no tool call, is the framework's. Any other combination is counted as unknown, and the archive contains none.

Two further counts use the message text. A run's first generated agent message counts as an authentication step
when it calls `find_user_id_by_email` or `find_user_id_by_name_zip`, or when its text matches
`e-?mail|zip|verify|authenticat|identity|identif`. For task 62, a run counts as naming the poem when a generated
agent message matches `Robert Frost|Road Not Taken`.

## The gates

| Module | Gate | What it decides |
| --- | --- | --- |
| [`icfa/integrity.py`](../src/icfa/integrity.py) | 1 | Whether a judge's reply is a complete record for this request: pass, fail, unknown or not applicable |
| [`icfa/origin.py`](../src/icfa/origin.py) | 2 | Which component produced a message, from a call ledger or from an archived generation record, and where a diagnosis about it goes |
| [`icfa/evidence.py`](../src/icfa/evidence.py) | 3 | The action-time view a judge is shown, and whether the quotes it cites are in that view |
| [`icfa/admission.py`](../src/icfa/admission.py) | 3 | The admission contract around the judge, and the intersection with origin |
| [`icfa/acceptance.py`](../src/icfa/acceptance.py) | 4 | Whether a candidate replaces the seed |
| [`icfa/gate_math.py`](../src/icfa/gate_math.py) | | Precision, classes of invalid feedback, break-even and exact clean-run bounds |
| [`icfa/gepa_adapter.py`](../src/icfa/gepa_adapter.py) · [`icfa/bound_admission.py`](../src/icfa/bound_admission.py) | | The seam to GEPA: two modes that differ in the diagnoses the reflection model reads |
