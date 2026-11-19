"""Origin census of the public tau2-bench retail archive.

The benchmark's authors publish four result files for the retail domain: four
agent models, 114 tasks, four trials each, 1,824 runs. This script downloads the
files at the pinned revision, verifies each against its Git blob hash, binds
every assistant-role message to its producer with ``icfa.origin``, and writes
the counts to ``evidence/archive_census.json``.

    python reproduce/archive_census.py            # download if needed, verify, count
    python reproduce/archive_census.py --cache D  # keep the files in directory D

No model is called. The four files total 92.7 MB.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from icfa.origin import INITIAL_GREETING, classify_archived_message, route_feedback  # noqa: E402

REPOSITORY = "sierra-research/tau2-bench"
COMMIT = "2174a603f6d014ef94473ffa95957f6ce27100db"
FILES = [
    ("claude-3-7-sonnet-20250219_retail_default_gpt-4.1-2025-04-14_4trials.json",
     "1b0e345db5bd9ae5cecfc70ff399f590be70c4f8", 24908843),
    ("gpt-4.1-2025-04-14_retail_default_gpt-4.1-2025-04-14_4trials.json",
     "b30d695834f16ddbb114e254e9fc35376d819f6b", 22044059),
    ("gpt-4.1-mini-2025-04-14_retail_base_gpt-4.1-2025-04-14_4trials.json",
     "8a55836aa5e9ed735c9900c0e357b1dd80f71c28", 23697012),
    ("o4-mini-2025-04-16_retail_default_gpt-4.1-2025-04-14_4trials.json",
     "bfd1be3546169e95d47f49c8b6fdf59e93a20188", 22066527),
]


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def load(name: str, sha: str, size: int, cache: pathlib.Path) -> bytes:
    """The pinned file, from the cache or downloaded; only verified bytes are cached or returned."""
    path = cache / name
    if path.exists():
        data = path.read_bytes()
    else:
        url = f"https://raw.githubusercontent.com/{REPOSITORY}/{COMMIT}/data/tau2/results/final/{name}"
        request = urllib.request.Request(url, headers={"User-Agent": "icfa-archive-census"})
        with urllib.request.urlopen(request, timeout=300) as response:
            data = response.read(size + 1)
    if len(data) != size or git_blob_sha1(data) != sha:
        raise SystemExit(f"{name}: bytes differ from the pinned blob {sha}")
    if not path.exists():
        path.write_bytes(data)
    return data


# The retail policy opens with "you have to authenticate the user identity by
# locating their user id via email, or via name + zip code". A first action
# counts as an authentication step when it calls an identity lookup or asks for
# those details.
AUTHENTICATION_TEXT = re.compile(r"e-?mail|zip|verify|authenticat|identity|identif", re.IGNORECASE)
AUTHENTICATION_TOOLS = ("find_user_id_by_email", "find_user_id_by_name_zip")

# Task 62: the simulated user first asks the agent to name a poem from its first
# line. The policy forbids knowledge "not provided by the user or the tools".
PROBE_TASK = "62"
PROBE_ANSWER = re.compile(r"Robert Frost|Road Not Taken", re.IGNORECASE)


def census(cache: pathlib.Path) -> dict:
    per_file, total = [], collections.Counter()
    no_record_texts, first_generated_turns = collections.Counter(), collections.Counter()
    probe = collections.Counter()
    for name, sha, size in FILES:
        archive = json.loads(load(name, sha, size, cache).decode("utf-8"))
        counts = collections.Counter()
        agent_model = archive["info"]["agent_info"]["llm"]
        tasks = set()
        for run in archive["simulations"]:
            counts["runs"] += 1
            tasks.add(run["task_id"])
            first_generated, named_the_poem = None, False
            for message in run["messages"]:
                if message.get("role") != "assistant":
                    continue
                counts["assistant_messages"] += 1
                origin = classify_archived_message(message)
                counts[origin["origin"]] += 1
                counts["route:" + route_feedback(origin)] += 1
                if origin["origin"] == "framework_seed":
                    no_record_texts[message.get("content")] += 1
                elif origin["origin"] == "model_agent":
                    text = message.get("content") or ""
                    names = [call.get("name") for call in (message.get("tool_calls") or [])]
                    if first_generated is None:
                        first_generated = message.get("turn_idx")
                        if AUTHENTICATION_TEXT.search(text) or any(n in AUTHENTICATION_TOOLS for n in names):
                            counts["first_own_action_is_authentication"] += 1
                    if names:
                        counts["model_tool_call_messages"] += 1
                    if text.strip() == INITIAL_GREETING:
                        counts["model_messages_with_the_opening_text"] += 1
                    if PROBE_ANSWER.search(text):
                        named_the_poem = True
            opening = run["messages"][0] if run["messages"] else {}
            if classify_archived_message(opening)["origin"] == "framework_seed":
                counts["runs_opening_with_framework_message"] += 1
            first_generated_turns[first_generated] += 1
            if str(run["task_id"]) == PROBE_TASK:
                reward = run["reward_info"]["reward"]
                probe["runs"] += 1
                probe["official_reward_1"] += reward == 1
                if named_the_poem:
                    probe["agent_named_the_poem"] += 1
                    probe["agent_named_the_poem_and_official_reward_1"] += reward == 1
        counts["tasks"] = len(tasks)
        per_file.append({"file": name, "git_blob_sha1": sha, "bytes": size, "agent_model": agent_model,
                         **{k: counts[k] for k in sorted(counts)}})
        total.update({k: v for k, v in counts.items() if k != "tasks"})
    assistant = total["assistant_messages"]
    return {
        "source": {"repository": REPOSITORY, "commit": COMMIT, "directory": "data/tau2/results/final"},
        "files": per_file,
        "total": {k: total[k] for k in sorted(total)},
        "framework_share_of_assistant_messages": total["framework_seed"] / assistant,
        "distinct_framework_texts": dict(no_record_texts),
        "first_generated_agent_turn": {str(k): v for k, v in sorted(first_generated_turns.items(), key=lambda kv: str(kv[0]))},
        "task_62_probe": {k: int(probe[k]) for k in ("runs", "official_reward_1", "agent_named_the_poem",
                                                     "agent_named_the_poem_and_official_reward_1")},
        "model_calls": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cache", default=str(ROOT / "reproduce" / ".cache"))
    parser.add_argument("--output", default=str(ROOT / "evidence" / "archive_census.json"))
    args = parser.parse_args()
    cache = pathlib.Path(args.cache)
    cache.mkdir(parents=True, exist_ok=True)
    result = census(cache)
    pathlib.Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                                         encoding="utf-8", newline="\n")
    t = result["total"]
    print(f"{t['runs']} runs, {t['assistant_messages']} assistant-role messages: "
          f"{t['framework_seed']} framework, {t['model_agent']} model, {t.get('unknown', 0)} unknown")


if __name__ == "__main__":
    main()
