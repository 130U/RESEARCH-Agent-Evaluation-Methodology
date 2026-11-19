"""Recompute every figure in the article and compare it with the text.

    python reproduce/run_all.py

Reads the files in evidence/, runs the gates in src/icfa on them where a gate
can be rerun without a model, writes reproduce/results.md and exits with
status 1 if any figure disagrees. Standard library only (Python 3.12+).
"""

from __future__ import annotations

import ast
import collections
import hashlib
import json
import pathlib
import re
import sys
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from icfa import gate_math  # noqa: E402
from icfa.acceptance import decide_strategy  # noqa: E402
from icfa.admission import AdmissionRecord, compound_admission  # noqa: E402
from icfa.integrity import RequestBinding, validate_bound_result, validate_nl_result  # noqa: E402

EVIDENCE = ROOT / "evidence"
POEM = re.compile(r"by (Robert Frost|Edgar Allan Poe)")
REFUND_PROMISE = "The PayPal refunds should be processed within 5–7 business days."


def load(name: str):
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def contract_statuses() -> dict[str, str]:
    """The contract's verdict on each of the 14 reply types, recomputed on a two-assertion task."""
    expected = ["The agent confirms the order total.", "The agent states the refund method."]

    def row(assertion, met=True):
        return {"expectedOutcome": assertion, "metExpectation": met, "reasoning": "stated in the final message"}

    def reply(rows, **extra):
        return json.dumps({"results": rows, **extra})

    full = [row(a) for a in expected]
    replies = {
        "valid_all_true": reply(full),
        "valid_one_false": reply([row(expected[0]), row(expected[1], False)]),
        "valid_reordered": reply(list(reversed(full))),
        "missing_results": "{}",
        "empty_results": reply([]),
        "partial_results": reply(full[:1]),
        "duplicate_outcome": reply([row(expected[0]), row(expected[0])]),
        "wrong_outcome": reply([row(expected[0]), row("The agent offers a discount.")]),
        "string_boolean": reply([row(expected[0], "true"), row(expected[1])]),
        "integer_boolean": reply([row(expected[0], 1), row(expected[1])]),
        "malformed_json": reply(full)[:-1],
        "wrong_top_level": json.dumps(full),
        "duplicate_json_key": '{"results": [], "results": ' + json.dumps(full) + "}",
    }
    out = {name: validate_nl_result(expected, raw).status for name, raw in replies.items()}
    mine = RequestBinding.create(run_id="run-a", task_id="t", trajectory=[], expected=expected, evaluator_revision="rev")
    other = RequestBinding.create(run_id="run-b", task_id="t", trajectory=[], expected=expected, evaluator_revision="rev")
    out["cross_run_swap"] = validate_bound_result(expected, reply(full), requested=mine, received=other).status
    return out


def main() -> int:
    sections: list[tuple[str, list]] = []
    rows: list = []

    def section(title: str) -> None:
        nonlocal rows
        rows = []
        sections.append((title, rows))

    def check(label, value, article, where, tol=0, shown=None):
        rows.append((label, value, shown if shown is not None else article, where, abs(value - article) <= tol))

    def check_true(label, ok, where, shown="holds"):
        rows.append((label, None, shown, where, bool(ok)))

    origin = load("origin_audit.json")
    census = load("archive_census.json")
    integrity = load("integrity_experiment.json")
    natural = load("natural_diagnoses.json")
    cards = load("admission_cards.json")
    pilot = load("candidate_pilot.json")
    dialogues = load("pilot_dialogues.json")
    batch = load("paired_batch.json")

    # ------------------------------------------------------------------ Section 3
    section("Origin, message by message (Section 3)")
    check("Completed development runs", origin["runs"]["completed"], 18, "§3")
    check("Tasks they cover", origin["runs"]["distinct_tasks"], 12, "§3")
    check("Assistant-role messages in those runs", origin["assistant_messages"], 181, "§3")
    check("Bound to the framework", origin["origin"]["framework_seed"], 18, "§3")
    check("Bound to the model", origin["origin"]["model_agent"], 163, "§3")
    check_true("Framework and model messages account for every assistant-role message",
               origin["origin"]["framework_seed"] + origin["origin"]["model_agent"] == origin["assistant_messages"], "§3")
    check("Model messages that are tool calls", origin["model_tool_call_messages"], 100, "§3")
    ledger = origin["call_ledger"]
    check("Calls in the ledger", sum(ledger.values()), 248, "§3")
    check("Agent calls", ledger["agent"], 163, "§3")
    check("User-simulator calls", ledger["user_simulator"], 81, "§3")
    check("Assertion-judge calls", ledger["assertion_judge"], 4, "§3")
    check_true("Agent calls match model messages one to one", ledger["agent"] == origin["origin"]["model_agent"], "§3")
    init = origin["initialization_control"]
    by_task = collections.defaultdict(list)
    for r in init["rows"]:
        by_task[r["task_id"]].append(r)
    check("Initializations", len(init["rows"]), 36, "§3")
    check("Tasks in the initialization control", len(by_task), 12, "§3")
    check_true("Each task received three different system prompts",
               all(len({r["system_prompt_sha256"] for r in v}) == 3 for v in by_task.values()), "§3")
    check("Tasks whose opening is identical under all three prompts",
          sum(len({r["opening_trajectory_sha256"] for r in v}) == 1 for v in by_task.values()), 12, "§3")
    check("Model calls in the initialization control", init["model_calls"], 0, "§3")
    check("36 of 36: upper bound on the rate at which a prompt alters the opening (%)",
          100 * gate_math.clean_run_upper_bound(36), 7.98, "§3, D3", tol=0.005)

    check("Archived result files", len(census["files"]), 4, "§3")
    check("Their size (MB)", sum(f["bytes"] for f in census["files"]) / 1e6, 92.7, "reproduce", tol=0.05)
    names = {"claude-3-7-sonnet-20250219": "claude-3-7-sonnet", "gpt-4.1-2025-04-14": "gpt-4.1",
             "gpt-4.1-mini-2025-04-14": "gpt-4.1-mini", "o4-mini-2025-04-16": "o4-mini"}
    table = {"claude-3-7-sonnet": (456, 6743, 456, 6287), "gpt-4.1": (456, 5560, 456, 5104),
             "gpt-4.1-mini": (456, 6124, 456, 5668), "o4-mini": (456, 6409, 456, 5953)}
    for f in census["files"]:
        name = names[f["agent_model"]]
        want = table[name]
        check(f"{name}: runs", f["runs"], want[0], "§3")
        check(f"{name}: assistant-role messages", f["assistant_messages"], want[1], "§3")
        check(f"{name}: framework", f["framework_seed"], want[2], "§3")
        check(f"{name}: model", f["model_agent"], want[3], "§3")
        check(f"{name}: tasks", f["tasks"], 114, "§3")
    tot = census["total"]
    check("Archived runs", tot["runs"], 1824, "§3")
    check("Assistant-role messages in the archive", tot["assistant_messages"], 24836, "§3")
    check("Framework-written", tot["framework_seed"], 1824, "§3")
    check("Bound to a generation record", tot["model_agent"], 23012, "§3")
    check("Unknown", tot.get("unknown", 0), 0, "§3")
    check("Framework share of assistant-role messages (%)", 100 * census["framework_share_of_assistant_messages"], 7.34, "§3", tol=0.005)
    check("One message in", tot["assistant_messages"] / tot["framework_seed"], 13.6, "§3", tol=0.05)
    check("Distinct framework-written texts", len(census["distinct_framework_texts"]), 1, "§3")
    check_true("The first generated agent message is at turn 2 in every run",
               census["first_generated_agent_turn"] == {"2": 1824}, "§3")
    check("Runs opening with the framework message", tot["runs_opening_with_framework_message"], 1824, "§3")
    check("Clean run of 1,824: upper bound on the rate of exceptions (%)",
          100 * gate_math.clean_run_upper_bound(1824), 0.16, "§3, D3", tol=0.005)
    check("Runs whose first own action is an authentication step", tot["first_own_action_is_authentication"], 1801, "§3")
    check("As a share of runs (%)", 100 * tot["first_own_action_is_authentication"] / tot["runs"], 98.7, "§3", tol=0.05)
    check("Model calls made by the census", census["model_calls"], 0, "§3")

    # ------------------------------------------------------------------ Section 4
    section("The integrity contract (Section 4)")
    irows = integrity["rows"]
    valid_cases = {"valid_all_true", "valid_one_false", "valid_reordered"}
    anomalies = [r for r in irows if r["case"] not in valid_cases]
    valid = [r for r in irows if r["case"] in valid_cases]
    check("Tasks that carry assertions", len({r["task_id"] for r in irows}), 40, "§4")
    check("Reply types", len(integrity["cases"]), 14, "§4")
    check("Controlled replies", len(irows), 560, "§4")
    check("Valid records", len(valid), 120, "§4")
    check("Valid records returned as pass", sum(r["contract_status"] == "pass" for r in valid), 80, "§4")
    check("Valid records returned as fail", sum(r["contract_status"] == "fail" for r in valid), 40, "§4")
    check("Anomalous replies", len(anomalies), 440, "§4")
    check("Anomalous replies held as unknown", sum(r["contract_status"] == "unknown" for r in anomalies), 440, "§4")
    check("Anomalous replies on which the evaluator's component reads 1",
          sum(r["upstream_component"] == 1 and not r["upstream_exception"] for r in anomalies), 360, "§4")
    check("Anomalous replies on which the evaluator raises an exception", sum(r["upstream_exception"] for r in anomalies), 80, "§4")
    per_case = collections.defaultdict(list)
    for r in irows:
        per_case[r["case"]].append(r)
    check_true("Every reply type has 40 inputs", all(len(v) == 40 for v in per_case.values()), "§4")
    reads_one = {c: sum(r["upstream_component"] == 1 and not r["upstream_exception"] for r in v) for c, v in per_case.items()}
    check_true("Per-row 'component reads 1' column of the table",
               reads_one == {**{c: 40 for c in integrity["cases"]}, "valid_one_false": 0, "malformed_json": 0, "wrong_top_level": 0},
               "§4")
    check("Anomalies accepted with strict parsing and the type check alone", sum(r["schema_accepts"] for r in anomalies), 200, "§4")
    check("After adding the count", sum(r["count_accepts"] for r in anomalies), 95, "§4")
    check("After adding identity", sum(r["identity_status"] in ("pass", "fail") for r in anomalies), 40, "§4")
    check("After adding the binding", sum(r["contract_status"] in ("pass", "fail") for r in anomalies), 0, "§4")
    check("Tasks without assertions, returned as not applicable",
          sum(c["contract_status"] == "not_applicable" for c in integrity["controls_without_assertions"]), 74, "§4")
    check("Median time of the check (microseconds)", integrity["contract_median_microseconds"], 10.9, "§4")
    live = contract_statuses()
    tabled = {c: "unknown" for c in integrity["cases"]} | {"valid_all_true": "pass", "valid_one_false": "fail", "valid_reordered": "pass"}
    check_true("The contract in src/icfa returns the tabled status on all 14 reply types", live == tabled, "§4")
    check_true("A conjunction over no results is true", all([]) is True, "§4")

    # ------------------------------------------------------------------ Section 5
    section("Evidence at the moment of action (Section 5)")
    nrows = natural["rows"]
    check("Runs reviewed", natural["runs_reviewed"], 18, "§5")
    check("Runs that drew a diagnosis", natural["runs_with_a_diagnosis"], 6, "§5")
    check("Diagnoses", len(nrows), 8, "§5")
    criteria = natural["reference_labels"]["criteria"]
    agreed = sum(r["reference_labels"]["reviewer_a"][c] == r["reference_labels"]["reviewer_b"][c] for r in nrows for c in criteria)
    check("Criterion judgments on which the two reviewers agreed", agreed, 20, "§5")
    check("Criterion judgments in all", len(nrows) * len(criteria), 24, "§5")

    def combined(final):
        values = [final[c] for c in criteria]
        if all(v == "supported" for v in values):
            return "supported"
        return "unsupported" if "unsupported" in values else "insufficient"

    check_true("Each combined label follows from its three criterion labels",
               all(combined(r["reference_labels"]["final"]) == r["reference_labels"]["combined"] for r in nrows), "§5")
    cross = collections.Counter((r["reference_labels"]["combined"], r["gate"]["decision"]) for r in nrows)
    check("Diagnoses supported on all three questions", sum(v for (k, _), v in cross.items() if k == "supported"), 0, "§5")
    check("Insufficient", sum(v for (k, _), v in cross.items() if k == "insufficient"), 6, "§5")
    check("Unsupported", sum(v for (k, _), v in cross.items() if k == "unsupported"), 2, "§5")
    check("Insufficient, gate rejects", cross[("insufficient", "reject")], 3, "§5")
    check("Insufficient, gate abstains", cross[("insufficient", "abstain")], 2, "§5")
    check("Insufficient, gate admits", cross[("insufficient", "accept")], 1, "§5")
    check("Unsupported, gate rejects", cross[("unsupported", "reject")], 2, "§5")
    decisions = collections.Counter(r["gate"]["decision"] for r in nrows)
    check("Gate rejects", decisions["reject"], 5, "§5")
    check("Gate abstains", decisions["abstain"], 2, "§5")
    check("Gate admits", decisions["accept"], 1, "§5")
    check("Kept out by the gate", decisions["reject"] + decisions["abstain"], 7, "§5")
    check("Zero in eight: upper bound on the share of fully supported diagnoses (%)",
          100 * gate_math.clean_run_upper_bound(8), 31.2, "§5, D3", tol=0.05)
    admitted = [r for r in nrows if r["gate"]["decision"] == "accept"]
    check_true("The admitted diagnosis criticizes the opening sentence at turn 0",
               len(admitted) == 1 and admitted[0]["turn_idx"] == 0
               and admitted[0]["action_excerpt"] == "Hi! How can I help you today?", "§1, §5")
    check_true("The judge's reason contains 'The actor controlled that response'",
               "The actor controlled that response" in admitted[0]["gate"]["reason"], "Summary, §1")
    check_true("The reviewer's claim and correction are quoted as written",
               "first asked how it could help rather than initiating authentication" in admitted[0]["reviewer_claim"]
               and admitted[0]["reviewer_correction"].startswith("Begin by requesting the account email"), "§1")
    check_true("Its origin is the framework and the agent's first generated message is at turn 2",
               natural["accepted_diagnosis_origin"]["origin"] == "framework_seed"
               and natural["accepted_diagnosis_origin"]["first_generated_agent_turn"] == 2, "§1, §5")
    check("Runs in the later batch", len(batch["episodes"]), 4, "§5")
    check("Further diagnoses that reached the gate", len(batch["gate_decisions"]), 2, "§5")
    check("Of which rejected", sum(g["decision"] == "reject" for g in batch["gate_decisions"]), 2, "§5")

    # ------------------------------------------------------------------ Section 6
    section("What the origin gate adds to a judge (Section 6)")
    crows = cards["rows"]
    check("Cards", len(crows), 12, "§6")
    check("Minimal pairs", len({r["pair"] for r in crows}), 6, "§6")
    tier = collections.Counter(r["reference_tier"] for r in crows)
    check("Supported cards", tier["supported"], 5, "§6")
    check("Unsupported cards", tier["unsupported"], 3, "§6")
    check("Insufficient cards", tier["insufficient"], 4, "§6")
    judge = collections.Counter((r["reference_tier"], r["semantic_decision"]) for r in crows)
    check("Supported, judge admits", judge[("supported", "accept")], 5, "§6")
    check("Unsupported, judge rejects", judge[("unsupported", "reject")], 3, "§6")
    check("Insufficient, judge admits", judge[("insufficient", "accept")], 2, "§6")
    check("Insufficient, judge rejects", judge[("insufficient", "reject")], 1, "§6")
    check("Insufficient, judge abstains", judge[("insufficient", "abstain")], 1, "§6")
    check("Admitted by the judge", sum(r["semantic_decision"] == "accept" for r in crows), 7, "§6")
    check("Rejected by the judge", sum(r["semantic_decision"] == "reject" for r in crows), 4, "§6")

    def exit_of(r):
        record = AdmissionRecord(r["semantic_decision"], "evidence", "0" * 64, "0" * 64, True)
        return compound_admission(record, r["route"])

    exits = [exit_of(r) for r in crows]
    check_true("compound_admission in src/icfa reproduces every card's outcome",
               all((e == "admitted") == r["compound_admitted"] for e, r in zip(exits, crows)), "§6")
    after = collections.Counter(r["reference_tier"] for r, e in zip(crows, exits) if e == "admitted")
    check("Admitted after origin", sum(after.values()), 6, "§6")
    check("Supported, admitted after origin", after["supported"], 5, "§6")
    check("Insufficient, admitted after origin", after["insufficient"], 1, "§6")
    check("Unsupported, admitted after origin", after["unsupported"], 0, "§6")
    pair = [r for r in crows if r["contrast"].startswith("Fixed framework greeting")]
    check_true("The origin pair: one claim, one sentence, two producers",
               len(pair) == 2 and pair[0]["claim"] == pair[1]["claim"]
               and pair[0]["criticized_action"] == pair[1]["criticized_action"] == "Hi! How can I help you today?"
               and {p["origin"] for p in pair} == {"framework_seed", "model_agent"}, "§6")
    check_true("The judge admitted both members of the origin pair", all(p["semantic_decision"] == "accept" for p in pair), "§6")
    check_true("Origin routes the framework member out and passes the model member on",
               {p["origin"]: exit_of(p) for p in pair} == {"framework_seed": "routed_to_framework_review", "model_agent": "admitted"}, "§6")
    p0 = Fraction(tier["supported"], len(crows))
    invalid = len(crows) - tier["supported"]
    t_judge = Fraction(judge[("supported", "accept")], tier["supported"])
    f_judge = Fraction(sum(r["semantic_decision"] == "accept" and r["reference_tier"] != "supported" for r in crows), invalid)
    f_both = Fraction(sum(e == "admitted" and r["reference_tier"] != "supported" for r, e in zip(crows, exits)), invalid)
    check_true("Judge alone: t = 5/5 and f = 2/7", (t_judge, f_judge) == (1, Fraction(2, 7)), "§6")
    check_true("With origin: f = 1/7 and t unchanged", f_both == Fraction(1, 7), "§6")
    check("Judge alone: share of admitted diagnoses that are supported (%)",
          float(100 * gate_math.precision(p0, t_judge, f_judge)), 71.4, "§6, D4", tol=0.05)
    check("With origin (%)", float(100 * gate_math.precision(p0, t_judge, f_both)), 83.3, "§6, D4", tol=0.05)
    check_true("Precision rises exactly when t > f, on a grid of 8,000 gates",
               all((gate_math.precision(p, t, f) > p) == (t > f)
                   for p in (Fraction(i, 21) for i in range(1, 21))
                   for t in (Fraction(i, 20) for i in range(1, 21))
                   for f in (Fraction(i, 20) for i in range(1, 21))), "§6, D4")
    usage = natural["usage"]["gate"]
    per_call = usage["input_tokens"] / usage["calls"]
    check("Evidence gate: input tokens over the 8 diagnoses", usage["input_tokens"], 130049, "§6, §8")
    check("Per diagnosis", per_call, 16256, "§6", tol=0.5)
    check("Per card", cards["usage"]["input_tokens"] / cards["judge_calls"], 15243, "§6", tol=0.5)
    seed_sha = pilot["selection"]["seed"]["final_strategy_sha256"]
    judgements = pilot["optimization"]["episode_judgements"]
    native_cand = [j for j in judgements if j["arm"] == "native" and j["strategy_sha256"] != seed_sha]
    cand_tokens = sum(j["input_tokens"] for j in native_cand)
    check("Episodes it took to test the native arm's candidate", len(native_cand), 4, "§6")
    check("Their input tokens", cand_tokens, 1076788, "§6")
    check("Gate call as a share of one candidate test (%)", 100 * per_call / cand_tokens, 1.5, "§6", tol=0.05)
    check("Diagnoses screened per prevented candidate at break-even",
          gate_math.break_even_diagnoses(per_call, cand_tokens), 66, "§6, D6", tol=0.5)

    # ------------------------------------------------------------------ Section 7
    section("Admission is not acceptance (Section 7)")
    splits = pilot["splits"]
    check("Training tasks", len(splits["train"]), 2, "§7")
    check("Validation tasks", len(splits["validation"]), 2, "§7")
    check("Test tasks", len(splits["test"]), 6, "§7")
    check("Proposals per arm", pilot["optimizer"]["proposals_per_arm"], 1, "§7")

    def arm_rows(arm, candidate, tasks):
        return [j for j in judgements if j["arm"] == arm and (j["strategy_sha256"] != seed_sha) == candidate and j["task_id"] in tasks]

    def passed(rows_):
        return sum(j["official_reward"] == 1 for j in rows_)

    def qualified(rows_):
        return sum(j["official_reward"] == 1 and j["structural_status"] == "pass" and j["semantic_status"] == "pass"
                   and j["user_validity"] == "pass" and j["critical_violation"] is False for j in rows_)

    check("Native arm: training tasks the seed passed", passed(arm_rows("native", False, splits["train"])), 1, "§7")
    native_text = pilot["optimization"]["strategies_executed"]["native"][1]["text"]
    check("Length of the native arm's candidate (characters)", len(native_text), 2214, "§7")
    check("Native arm: training tasks the candidate passed", passed(arm_rows("native", True, splits["train"])), 2, "§7")
    check("Validation, official reward: candidate", passed(arm_rows("native", True, splits["validation"])), 2, "§7")
    check("Validation, official reward: seed", passed(arm_rows("native", False, splits["validation"])), 2, "§7")
    check("Validation, qualified: candidate", qualified(arm_rows("native", True, splits["validation"])), 1, "§7")
    check("Validation, qualified: seed", qualified(arm_rows("native", False, splits["validation"])), 2, "§7")
    promise = [e for e in dialogues["episodes"] if e["phase"] == "optimization" and e["arm"] == "native"
               and e["strategy_sha256"] != seed_sha and e["task_id"] in splits["validation"]
               and any(REFUND_PROMISE in (m.get("content") or "") for m in e["messages"])]
    check_true("The candidate's closing message promises the refund deadline, as quoted",
               len(promise) == 1 and "The total refund is $8,276.23." in promise[0]["messages"][-2]["content"] + promise[0]["messages"][-1].get("content", ""),
               "§7")
    check_true("Both reviewers marked that answer unsound",
               len(promise) == 1 and all(r["semantic_status"] == "fail" for r in promise[0]["reviews"]), "§7")

    def acceptance_rows(rows_):
        return [{"task_id": j["task_id"], "strategy_sha256": j["strategy_sha256"], "native_reward": int(j["official_reward"]),
                 "structural_status": j["structural_status"], "semantic_status": j["semantic_status"],
                 "user_validity": j["user_validity"], "critical_violation": j["critical_violation"],
                 "input_tokens": j["input_tokens"], "output_tokens": j["output_tokens"]} for j in rows_]

    seed_text = pilot["seed_strategy"]
    check_true("The strategy texts hash to the identities in the evidence",
               hashlib.sha256(seed_text.encode()).hexdigest() == seed_sha
               and hashlib.sha256(native_text.encode()).hexdigest() == native_cand[0]["strategy_sha256"], "§7")
    decision = decide_strategy(seed_text, native_text, False,
                               acceptance_rows(arm_rows("native", False, splits["validation"])),
                               acceptance_rows(arm_rows("native", True, splits["validation"])), splits["validation"])
    check_true("The acceptance rule in src/icfa keeps the seed", decision["decision"] == "keep_seed", "§7")
    check_true("Its reasons: the optimizer kept the seed, the qualified count is not higher, a qualified task regressed",
               decision["reasons"] == ["optimizer_did_not_select_new_candidate", "qualified_count_not_strictly_higher",
                                       "baseline_qualified_task_regressed_or_unresolved"], "§7")
    forced = decide_strategy(seed_text, native_text, True,
                             acceptance_rows(arm_rows("native", False, splits["validation"])),
                             acceptance_rows(arm_rows("native", True, splits["validation"])), splits["validation"])
    check_true("The rule keeps the seed even if the optimizer had selected the candidate", forced["decision"] == "keep_seed", "§7, D9")
    check("Token cap of the acceptance rule (times the seed's cost)", decision["validation_token_cost"]["maximum_ratio"], 1.25, "§7")
    check("Admitted arm: training tasks the seed passed", passed(arm_rows("admitted", False, splits["train"])), 2, "§7")
    check("Admitted arm: training tasks the candidate passed", passed(arm_rows("admitted", True, splits["train"])), 2, "§7")
    check_true("The admitted arm's candidate was not adopted",
               pilot["optimization"]["completion"]["admitted"]["endpoint"] == "candidate_rejected"
               and pilot["selection"]["admitted"]["decision"] == "keep_seed", "§7")
    seed_runs = {arm: {j["task_id"]: j["official_reward"] for j in judgements if j["arm"] == arm and j["strategy_sha256"] == seed_sha}
                 for arm in ("native", "admitted")}
    check("Tasks on which the two arms ran the seed", len(seed_runs["native"]), 4, "§7")
    check("Tasks whose outcome differed between the two runs of the seed",
          sum(seed_runs["native"][t] != seed_runs["admitted"][t] for t in seed_runs["native"]), 2, "§7")
    units = pilot["final_test"]["units"]
    done = [u for u in units if u["official"] in ("success", "failure")]
    check_true("Every arm's selected strategy is the seed",
               len({pilot["selection"][a]["final_strategy_sha256"] for a in ("seed", "native", "admitted")}) == 1, "§7")
    check("Completed test runs", len(done), 18, "§7")
    check("Passed on the official reward", sum(u["official"] == "success" for u in done), 8, "§7")
    check("Qualified", sum(u["qualification"] == "success" for u in done), 5, "§7")
    gap = [u for u in done if u["official"] == "success" and u["qualification"] != "success"]
    check("Passed and did not qualify", len(gap), 3, "§7")
    check_true("They are the three runs of one task", {u["task_id"] for u in gap} == {"62"} and len({u["arm"] for u in gap}) == 3, "§7")
    poem_runs = [e for e in dialogues["episodes"] if e["phase"] == "test" and e["task_id"] == "62"]
    check_true("In each of them the agent names a poem and its author and scores 1",
               len(poem_runs) == 3 and all(e["official_reward"] == 1 and any(
                   m["role"] == "assistant" and POEM.search(m.get("content") or "") for m in e["messages"]) for e in poem_runs), "§7")
    probe = census["task_62_probe"]
    check("Archived runs of that task", probe["runs"], 16, "§7")
    check("In which the agent names the poem", probe["agent_named_the_poem"], 10, "§7")
    check("Of those, with the full official reward", probe["agent_named_the_poem_and_official_reward_1"], 9, "§7")
    departed = [e for e in batch["episodes"] if any(r["user_departed_from_instructions"] for r in e["reviews"])]
    check_true("In one run of the paired batch both reviewers confirm the simulated customer departed from its instructions",
               len(departed) == 1 and all(r["user_departed_from_instructions"] for r in departed[0]["reviews"]), "§7")
    check("Episodes completed in the paired study", batch["completed"]["parent_episodes"], 4, "§7")
    check("Episodes planned", batch["planned"]["optimization_episodes"], 120, "§7")

    # ------------------------------------------------------------------ Section 8
    section("What it cost (Section 8)")
    rev = natural["usage"]["review"]
    check("Reviewer: calls", rev["calls"], 18, "§8")
    check("Reviewer: input tokens", rev["input_tokens"], 284840, "§8")
    check("Reviewer: output tokens", rev["output_tokens"], 6894, "§8")
    check("Evidence gate on diagnoses: calls", usage["calls"], 8, "§8")
    check("Evidence gate on diagnoses: output tokens", usage["output_tokens"], 4315, "§8")
    check("Evidence gate on cards: calls", cards["judge_calls"], 12, "§8")
    check("Evidence gate on cards: input tokens", cards["usage"]["input_tokens"], 182910, "§8")
    check("Evidence gate on cards: output tokens", cards["usage"]["output_tokens"], 4128, "§8")
    opt = pilot["optimization"]["usage"]
    check("Optimization: calls", sum(v["calls"] for v in opt.values()), 240, "§8")
    check("Optimization: input tokens", sum(v["input_tokens"] for v in opt.values()), 3589164, "§8")
    check("Optimization: output tokens", sum(v["output_tokens"] for v in opt.values()), 27027, "§8")
    test = pilot["final_test"]["usage"]
    check("Final test: calls", sum(v["calls"] for v in test.values()), 273, "§8")
    check("Final test: input tokens", sum(v["input_tokens"] for v in test.values()), 3689217, "§8")
    check("Final test: output tokens", sum(v["output_tokens"] for v in test.values()), 21717, "§8")
    check("Interrupted test runs", sum(u["official"] == "interrupted" for u in units), 1, "§8")
    check("Paired batch: calls", batch["usage"]["calls"], 61, "§8")
    check("Paired batch: input tokens", batch["usage"]["input_tokens"], 893326, "§8")
    check("Paired batch: output tokens", batch["usage"]["output_tokens"], 9586, "§8")
    check("Model calls made by the integrity experiment", integrity["model_calls"], 0, "§8")

    # ------------------------------------------------------------------ The code
    section("The gate code")
    tests = 0
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        tests += sum(isinstance(node, ast.FunctionDef) and node.name.startswith("test")
                     for cls in tree.body if isinstance(cls, ast.ClassDef) for node in cls.body)
    check("Tests in the suite", tests, 137, "Problem and Approach")

    def fmt(x):
        if x is None:
            return ""
        if isinstance(x, bool):
            return str(x)
        if isinstance(x, int) or float(x).is_integer():
            return f"{int(x):,}"
        return f"{x:.4f}"

    def art(x):
        if isinstance(x, str):
            return x
        if isinstance(x, int) or float(x).is_integer():
            return f"{int(x):,}"
        return f"{x:g}"

    total = sum(len(r) for _, r in sections)
    agree = sum(ok for _, r in sections for *_, ok in r)
    lines = ["# Results", "", "Every figure in the article, recomputed.", "", f"{agree} of {total} figures agree with the article", ""]
    for title, items in sections:
        lines += [f"## {title}", "", "| Quantity | Recomputed | Article | Where | Agrees |", "| --- | ---: | ---: | --- | :---: |"]
        for label, value, article, where, ok in items:
            lines.append(f"| {label.replace('|', chr(92) + '|')} | {fmt(value)} | {art(article)} | {where} | {'✓' if ok else '✗'} |")
        lines.append("")
    (ROOT / "reproduce" / "results.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"{agree} of {total} figures agree with the article")
    for title, items in sections:
        for label, value, article, where, ok in items:
            if not ok:
                print("  DISAGREES:", title, "|", label, "|", value, "vs", article)
    return 0 if agree == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
