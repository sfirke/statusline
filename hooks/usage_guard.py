#!/usr/bin/env python3
"""PreToolUse hook: require approval for every tool call once the 5h limit is nearly spent.

Reads the state file written by ~/.claude/statusline/statusline.sh
(~/.claude/state/statusline/<session_id>.json, falling back to latest.json, which holds the
account-wide limits from whichever session rendered last). At >= THRESHOLD percent of the
5-hour window the hook returns permissionDecision "ask", so you must approve each call.

Ignored (fail open, never blocks): missing/unparseable/stale state, or a window whose
resets_at has passed. Override the threshold with USAGE_GUARD_THRESHOLD (percent).
"""
import json
import os
import re
import sys
import time

THRESHOLD = float(os.environ.get("USAGE_GUARD_THRESHOLD", "95"))
MAX_STATE_AGE = 15 * 60  # seconds; the statusline refreshes at least every 60s while a session is open
STATE_DIR = os.path.expanduser("~/.claude/state/statusline")


def load(name):
    try:
        with open(os.path.join(STATE_DIR, name)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def main():
    try:
        sid = json.load(sys.stdin).get("session_id", "")
    except ValueError:
        return {}

    now = time.time()
    candidates = []
    if re.fullmatch(r"[A-Za-z0-9_-]+", sid or ""):
        candidates.append(load(sid + ".json"))
    candidates.append(load("latest.json"))

    for state in candidates:
        if not state or now - state.get("ts", 0) > MAX_STATE_AGE:
            continue
        five = state.get("five_hour") or {}
        pct, resets = five.get("used_percentage"), five.get("resets_at")
        if pct is None or (resets is not None and resets <= now):
            continue
        if pct < THRESHOLD:
            return {}
        extra = state.get("extra_usage") or {}
        spend = ""
        if extra.get("used_usd") is not None:
            spend = f" Extra usage so far this month: ${extra['used_usd']:.2f} of ${extra['limit_usd']:.2f}."
        reset_txt = time.strftime("%H:%M", time.localtime(resets)) if resets else "unknown"
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"5h usage is at {pct:.0f}% (threshold {THRESHOLD:.0f}%), window resets at {reset_txt} "
                f"local.{spend} Approve to keep going."),
        }}
    return {}


if __name__ == "__main__":
    out = main()
    if out:
        print(json.dumps(out))
