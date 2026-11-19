"""Gate 2: origin binding on constructed call ledgers and on archived messages."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from icfa.origin import (OriginContext, ORCHESTRATOR_SHA256, INITIAL_GREETING,
    classify_action_origin, classify_archived_message, route_feedback)


class OriginTests(unittest.TestCase):
    def setUp(self):
        self.context = OriginContext(ORCHESTRATOR_SHA256, False, 0)
        self.seed = {"role": "assistant", "turn_idx": 0, "content": INITIAL_GREETING,
                     "tool_calls": None, "raw_data": None, "usage": None, "cost": 0.0}
        self.user = {"call_index": 0, "role": "user_simulator_response", "request": {
            "participant": "user_simulator_response", "messages": [{"role": "user", "content": INITIAL_GREETING}]}}
        value = {"kind": "message", "content": INITIAL_GREETING, "tool_calls": []}
        self.record = {"call_index": 1, "call_id": "case-call", "role": "agent_response",
            "transport": "structured_action", "structured_output": value}
        self.generated = {"role": "assistant", "turn_idx": 2, "content": INITIAL_GREETING,
            "tool_calls": None, "raw_data": {"call_id": "case-call", "output": deepcopy(value),
                                             "transport": "structured_action"}}

    def classify(self, message, calls):
        return classify_action_origin(message, calls, self.context)

    def test_framework_seed_is_routed_outside_strategy(self):
        result = self.classify(self.seed, [self.user])
        self.assertEqual(result["origin"], "framework_seed")
        self.assertEqual(route_feedback(result), "route_to_harness_or_non_agent_review")

    def test_identical_generated_text_is_not_classified_by_text(self):
        result = self.classify(self.generated, [self.user, self.record])
        self.assertEqual(result["origin"], "model_agent")
        self.assertEqual(route_feedback(result), "continue_semantic_review")

    def test_seed_needs_positive_context_and_first_call(self):
        for calls in ([], [self.record], [{**self.user, "call_index": 1}]):
            with self.subTest(calls=calls):
                self.assertEqual(self.classify(self.seed, calls)["origin"], "unknown")
        for context in (OriginContext("unverified", False, 0), OriginContext(ORCHESTRATOR_SHA256, True, 0),
                        OriginContext(ORCHESTRATOR_SHA256, False, 1)):
            self.assertEqual(classify_action_origin(self.seed, [self.user], context)["origin"], "unknown")

    def test_forged_generation_cannot_override_initializer(self):
        self.generated["turn_idx"] = 0
        self.assertEqual(self.classify(self.generated, [self.record])["origin"], "unknown")

    def test_missing_duplicate_wrong_role_and_changed_output(self):
        variants = [[], [self.record, self.record], [{**self.record, "role": "user_simulator_response"}],
                    [{**self.record, "error_type": "Interrupted"}]]
        for records in variants:
            self.assertEqual(self.classify(self.generated, records)["origin"], "unknown")
        self.generated["content"] = "Changed after generation"
        self.assertEqual(self.classify(self.generated, [self.record])["origin"], "unknown")

    def test_tool_identity_and_arguments_are_bound(self):
        value = {"kind": "tool_calls", "content": None,
                 "tool_calls": [{"name": "lookup", "arguments_json": '{"id":"A"}'}]}
        self.record["structured_output"] = value
        self.generated.update(content=None, tool_calls=[{"id": "call_case-call_0", "name": "lookup",
                              "arguments": {"id": "A"}, "requestor": "assistant"}])
        self.generated["raw_data"]["output"] = deepcopy(value)
        self.assertEqual(self.classify(self.generated, [self.record])["origin"], "model_agent")
        self.generated["tool_calls"][0]["arguments"]["id"] = "B"
        self.assertEqual(self.classify(self.generated, [self.record])["origin"], "unknown")

    def test_unknown_does_not_become_non_agent_or_false_editability(self):
        result = self.classify({}, [])
        self.assertIsNone(result["reachable"])
        self.assertEqual(route_feedback(result), "abstain_origin_unknown")
        self.assertEqual(self.classify({"role": "user"}, [])["origin"], "non_agent")

    def test_malformed_role_or_first_request_abstains(self):
        self.assertEqual(self.classify({"role": []}, [])["origin"], "unknown")
        malformed = {**self.user, "request": []}
        self.assertEqual(self.classify(self.seed, [malformed])["origin"], "unknown")



class ArchivedMessages(unittest.TestCase):
    def setUp(self):
        self.seed = {"role": "assistant", "turn_idx": 0, "content": INITIAL_GREETING,
                     "tool_calls": None, "cost": 0.0, "usage": None, "raw_data": None}
        self.generated = {"role": "assistant", "turn_idx": 2, "content": INITIAL_GREETING,
                          "tool_calls": None, "cost": 0.01,
                          "usage": {"completion_tokens": 9, "prompt_tokens": 5000},
                          "raw_data": {"finish_reason": "stop"}}

    def test_same_text_two_origins(self):
        self.assertEqual(classify_archived_message(self.seed)["origin"], "framework_seed")
        self.assertEqual(classify_archived_message(self.generated)["origin"], "model_agent")
        self.assertEqual(self.seed["content"], self.generated["content"])

    def test_routes(self):
        self.assertEqual(route_feedback(classify_archived_message(self.seed)),
                         "route_to_harness_or_non_agent_review")
        self.assertEqual(route_feedback(classify_archived_message(self.generated)),
                         "continue_semantic_review")

    def test_anything_short_of_the_positive_rules_is_unknown(self):
        variants = [{**self.seed, "turn_idx": 4}, {**self.seed, "content": "Hello."},
                    {**self.seed, "cost": 0.2}, {**self.seed, "usage": {"completion_tokens": 1}},
                    {**self.seed, "tool_calls": [{"name": "lookup"}]},
                    {**self.generated, "turn_idx": 0}, {**self.generated, "raw_data": None}, {}, None]
        for message in variants:
            with self.subTest(message=message):
                self.assertEqual(classify_archived_message(message)["origin"], "unknown")

    def test_user_and_tool_messages_are_outside_the_agent(self):
        for role in ("user", "tool"):
            self.assertEqual(classify_archived_message({"role": role})["origin"], "non_agent")


if __name__ == "__main__":
    unittest.main()
