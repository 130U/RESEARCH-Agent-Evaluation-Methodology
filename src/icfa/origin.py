"""Gate 2: who produced the criticized message, and can this intervention reach it?

Three facts about a message are kept apart: the role label it carries, the
component that produced it, and the component the current optimization round
may change. A role of ``assistant`` and a matching text establish neither of
the last two. Origin is decided from execution records by positive rules, and
anything the rules do not establish stays ``unknown``.

The rules cover the tau2-bench text orchestrator at the pinned revision and one
intervention: editing the agent's system prompt. A model-produced message
remains subject to the evidence gate; origin says where a diagnosis may go, not
whether it is right.
"""
from dataclasses import dataclass

from .integrity import strict_json

ORCHESTRATOR_SHA256 = "ff6c2631a02b68a3341b1ca3d9a6122bb43ab872ee6acc960379c78015eca420"
INITIAL_GREETING = "Hi! How can I help you today?"
INTERVENTION = "system_prompt"
TRANSPORT = "structured_action"

MODEL = "model_agent"
FRAMEWORK = "framework_seed"
NON_AGENT = "non_agent"
UNKNOWN = "unknown"


@dataclass(frozen=True)
class OriginContext:
    """What is known about the run before any message is classified."""

    orchestrator_sha256: str
    solo_mode: bool
    initial_history_count: int
    intervention: str = INTERVENTION


def _result(origin, reachable, reason, intervention, call_id=None):
    return {"origin": origin, "reachable": reachable, "reason": reason,
            "call_id": call_id, "intervention": intervention}


def classify_action_origin(message, calls, context):
    """Bind one message of a recorded run to the component that produced it.

    ``calls`` is the run's call ledger: one record per model call, in order,
    with its role, its request and its structured output. Returns one of
    ``model_agent``, ``framework_seed``, ``non_agent`` or ``unknown`` together
    with ``reachable``: True when the system prompt is upstream of the message,
    False when it is not, None when the records do not decide.
    """
    if (not isinstance(context, OriginContext)
            or context.orchestrator_sha256 != ORCHESTRATOR_SHA256
            or context.intervention != INTERVENTION
            or type(context.solo_mode) is not bool
            or type(context.initial_history_count) is not int or context.initial_history_count < 0):
        return _result(UNKNOWN, None, "unsupported_or_unverified_run_context",
                       getattr(context, "intervention", None))

    def result(origin, reachable, reason, call_id=None):
        return _result(origin, reachable, reason, context.intervention, call_id)

    def unknown(reason):
        return result(UNKNOWN, None, reason)

    if not isinstance(message, dict) or not isinstance(calls, list):
        return unknown("missing_message_or_call_ledger")
    if message.get("role") in ("user", "tool"):
        return result(NON_AGENT, False, "message_role_outside_agent_policy")
    if message.get("role") != "assistant":
        return unknown("missing_or_unrecognized_message_role")
    raw = message.get("raw_data")
    if (context.solo_mode is False and context.initial_history_count == 0
            and message.get("turn_idx") == 0 and raw is not None):
        return unknown("generation_metadata_conflicts_with_pinned_initializer")
    if isinstance(raw, dict) and isinstance(raw.get("call_id"), str):
        call_id = raw["call_id"]
        matches = [c for c in calls if isinstance(c, dict) and c.get("call_id") == call_id]
        if len(matches) != 1:
            return unknown("missing_or_duplicate_call_identity")
        record = matches[0]
        value = record.get("structured_output")
        if (record.get("role") != "agent_response" or record.get("error_type")
                or raw.get("transport") != TRANSPORT
                or record.get("transport") != raw["transport"]
                or not isinstance(value, dict) or raw.get("output") != value):
            return unknown("call_role_status_or_output_binding_mismatch")
        try:
            expected_calls = [{"id": f"call_{call_id}_{i}", "name": c["name"],
                               "arguments": strict_json(c["arguments_json"]), "requestor": "assistant"}
                              for i, c in enumerate(value["tool_calls"])]
            if (value["kind"] not in {"message", "tool_calls"}
                    or (value["kind"] == "message" and (expected_calls or not isinstance(value["content"], str)))
                    or (value["kind"] == "tool_calls" and (not expected_calls or value["content"] is not None))
                    or any(not isinstance(c["arguments"], dict) for c in expected_calls)
                    or message.get("content") != value["content"]
                    or (message.get("tool_calls") or []) != expected_calls):
                return unknown("rendered_action_differs_from_recorded_model_output")
        except (KeyError, TypeError, ValueError):
            return unknown("malformed_recorded_output")
        return result(MODEL, True, "unique_recorded_agent_generation_matches_action", call_id)
    if raw is not None:
        return unknown("unrecognized_generation_metadata")
    # A positive rule, never `turn_idx == 0` alone: on a fresh, non-solo run the
    # orchestrator inserts its constant before the first call, and that first
    # call is the user simulator reading the constant.
    first = calls[0] if calls and isinstance(calls[0], dict) else {}
    first_request = first.get("request", {})
    requested = first_request.get("messages", []) if isinstance(first_request, dict) else []
    if (context.solo_mode is False and context.initial_history_count == 0
            and type(message.get("turn_idx")) is int and message["turn_idx"] == 0
            and message.get("content") == INITIAL_GREETING and not message.get("tool_calls")
            and message.get("usage") is None
            and type(message.get("cost")) in (int, float) and message["cost"] == 0
            and type(first.get("call_index")) is int and first["call_index"] == 0
            and first.get("role") == "user_simulator_response"
            and isinstance(first_request, dict)
            and first_request.get("participant") == "user_simulator_response"
            and isinstance(requested, list) and requested and isinstance(requested[-1], dict)
            and requested[-1].get("role") == "user"
            and requested[-1].get("content") == INITIAL_GREETING):
        return result(FRAMEWORK, False, "pinned_fresh_non_solo_initializer_precedes_model_calls")
    return unknown("no_verified_generation_or_framework_origin")


def classify_archived_message(message):
    """Classify one message of a published tau2-bench result file.

    The archive keeps no call ledger. It keeps each message's generation
    record: token usage, the raw model response and the cost. A message with a
    complete record was generated; the opening constant with no record, no cost
    and no tool call at turn 0 was inserted by the orchestrator. Every other
    combination is ``unknown``.
    """
    if not isinstance(message, dict):
        return _result(UNKNOWN, None, "missing_message", INTERVENTION)
    role = message.get("role")
    if role in ("user", "tool"):
        return _result(NON_AGENT, False, "message_role_outside_agent_policy", INTERVENTION)
    if role != "assistant":
        return _result(UNKNOWN, None, "missing_or_unrecognized_message_role", INTERVENTION)
    usage, raw = message.get("usage"), message.get("raw_data")
    if usage is not None and raw is not None:
        if message.get("turn_idx") == 0:
            return _result(UNKNOWN, None, "generation_metadata_conflicts_with_pinned_initializer", INTERVENTION)
        return _result(MODEL, True, "generation_record_present", INTERVENTION)
    if (usage is None and raw is None
            and type(message.get("turn_idx")) is int and message["turn_idx"] == 0
            and message.get("content") == INITIAL_GREETING and not message.get("tool_calls")
            and type(message.get("cost")) in (int, float) and message["cost"] == 0):
        return _result(FRAMEWORK, False, "opening_constant_without_generation_record", INTERVENTION)
    return _result(UNKNOWN, None, "no_verified_generation_or_framework_origin", INTERVENTION)


def route_feedback(origin):
    """Where a diagnosis about this message goes in a system-prompt round."""
    if origin.get("origin") == MODEL and origin.get("reachable") is True:
        return "continue_semantic_review"
    if origin.get("reachable") is False:
        return "route_to_harness_or_non_agent_review"
    return "abstain_origin_unknown"
