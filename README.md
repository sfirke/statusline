# statusline

Additions on top of [daniel3303/ClaudeCodeStatusLine](https://github.com/daniel3303/ClaudeCodeStatusLine):
a few status line improvements, plus a hook that uses the status line's usage data to guard against
running out of quota.

For the base status line (layout, model/token/usage segments, themes), see the upstream project.
`statusline.sh` is a modified copy used under its MIT license (see `LICENSE`); the original design and
most of the script are Daniel Oliveira's.

## Added: usage guard hook

`hooks/usage_guard.py` is a PreToolUse hook that asks for approval on every tool call once 5h usage
reaches 95%, so a long-running session can't burn through the rest of the window unattended.

- Reads the state files the status line writes (see below).
- Override the threshold with `USAGE_GUARD_THRESHOLD` (percent).
- Fails open: missing, unparseable or stale state, or a window whose `resets_at` has passed, never blocks.

## Added: state files for hooks

The status line writes `~/.claude/state/statusline/<session_id>.json` and `latest.json`
(account-wide limits from whichever session rendered last) so hooks can read usage without
calling the API themselves.

## Changed in `statusline.sh`

- **Prompt cache segment** (`cache 3m/5m`) with TTL-aware colors
- **`OVERAGE` marker** when the 5h window is at 100% and extra usage is enabled
- **Expired windows show 0%** when `resets_at` has passed, instead of the stale value
- **Extra-usage spend refreshes**: the usage API cache is no longer rewritten on every run, which used to freeze it
- **Times in America/New_York**
- **API User-Agent** uses the installed Claude Code version

## Install

```bash
mkdir -p ~/.claude/statusline ~/.claude/hooks
cp statusline.sh ~/.claude/statusline/ && chmod +x ~/.claude/statusline/statusline.sh
cp hooks/usage_guard.py ~/.claude/hooks/
```

Then merge `settings-snippet.json` into `~/.claude/settings.json` (keep any existing PreToolUse hooks).
Requires `jq`, `curl`, `python3`.

The usage numbers come from an undocumented Anthropic OAuth endpoint, so it may change without notice.
