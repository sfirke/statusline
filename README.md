# statusline

My Claude Code status line and a usage-guard hook.

`statusline.sh` is a fork of [daniel3303/ClaudeCodeStatusLine](https://github.com/daniel3303/ClaudeCodeStatusLine),
used under its MIT license (see `LICENSE`). All credit for the original design and most of the script goes to
Daniel Oliveira; the changes below are mine.

Changes from upstream:
- Prompt cache segment (`cache 3m/5m`) with TTL-aware colors
- Usage API cache is no longer rewritten each run, so extra-usage spend refreshes (it used to freeze)
- Usage windows whose `resets_at` has passed show 0% instead of the stale value
- `OVERAGE` marker when the 5h window is at 100% and extra usage is enabled
- Times shown in America/New_York
- API User-Agent uses the installed Claude Code version
- Writes `~/.claude/state/statusline/<session_id>.json` and `latest.json` for hooks

`hooks/usage_guard.py` is a PreToolUse hook that asks for approval on every tool call once 5h usage
reaches 95% (`USAGE_GUARD_THRESHOLD` to change). It fails open if state is missing or stale.

## Install
```bash
mkdir -p ~/.claude/statusline ~/.claude/hooks
cp statusline.sh ~/.claude/statusline/ && chmod +x ~/.claude/statusline/statusline.sh
cp hooks/usage_guard.py ~/.claude/hooks/
```
Then merge `settings-snippet.json` into `~/.claude/settings.json` (keep any existing PreToolUse hooks).
Requires `jq`, `curl`, `python3`.

The usage numbers come from an undocumented Anthropic OAuth endpoint, so it may change without notice.
