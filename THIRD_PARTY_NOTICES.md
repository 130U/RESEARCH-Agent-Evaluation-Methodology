# Third-party notices

This repository builds on two open-source projects. Neither is redistributed here; both are used at a pinned
revision.

| Project | Revision | License | Used for |
| --- | --- | --- | --- |
| [τ²-bench](https://github.com/sierra-research/tau2-bench/tree/2174a603f6d014ef94473ffa95957f6ce27100db) (Sierra Research) | `2174a603f6d014ef94473ffa95957f6ce27100db` | MIT, [text](third_party/TAU2_LICENSE.txt) | The retail environment, its policy, tools, user simulator and evaluator, and the published result files read by the archive census |
| [GEPA](https://github.com/gepa-ai/gepa/tree/15ee314f9c7d34ec153b809d401f42f55c4dcd76) | `15ee314f9c7d34ec153b809d401f42f55c4dcd76` | MIT, [text](third_party/GEPA_LICENSE.txt) | Reflective prompt optimization; `src/icfa/gepa_adapter.py` implements its adapter interface |

The customers, orders, addresses and products that appear in [`evidence/pilot_dialogues.json`](evidence/pilot_dialogues.json)
and in quoted diagnoses are the benchmark's own data. Policy sentences are quoted from the benchmark's retail policy.
