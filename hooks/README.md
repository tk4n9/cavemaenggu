# Cavemaenggu Hooks

These hooks are **bundled with the cavemaenggu plugin** and activate automatically when the plugin is installed. No manual setup required.

If you installed cavemaenggu standalone (without the plugin), you can use `bash hooks/install.sh` to wire them into your settings.json manually.

Cavemaenggu uses its own `cavemaenggu-*` file names and `.cavemaenggu-active` flag, separate from the upstream `caveman` plugin, so both can be installed side by side without collision.

## What's Included

### `cavemaenggu-activate.js` — SessionStart hook

- Runs once when Claude Code starts
- Writes `full` to `~/.claude/.cavemaenggu-active` (flag file)
- Emits cavemaenggu rules as hidden SessionStart context
- Detects missing statusline config and emits setup nudge (Claude will offer to help)

### `cavemaenggu-mode-tracker.js` — UserPromptSubmit hook

- Fires on every user prompt, checks for `/cavemaenggu` (or `/mg`) commands and Korean activation phrases (`맹구`, `맹구야`, `맹구 모드`, ...)
- Writes the active mode to the flag file when a cavemaenggu command or trigger phrase is detected
- Supports: `full`, `lite`, `ultra`, `maeng-gu`, `maeng-gu-lite`, `maeng-gu-ultra`, `commit`, `review`, `compress`

### `cavemaenggu-statusline.sh` / `cavemaenggu-statusline.ps1` — Statusline badge script

- Reads `~/.claude/.cavemaenggu-active` and outputs a colored badge
- Shows `[MAENGGU]`, `[MAENGGU:ULTRA]`, `[MAENGGU:MAENG-GU]`, etc.

## Statusline Badge

The statusline badge shows which cavemaenggu mode is active directly in your Claude Code status bar.

**Plugin users:** If you do not already have a `statusLine` configured, Claude will detect that on your first session after install and offer to set it up for you. Accept and you're done.

If you already have a custom statusline, cavemaenggu does not overwrite it and Claude stays quiet. Add the badge snippet to your existing script instead.

**Standalone users:** `install.sh` / `install.ps1` wires the statusline automatically if you do not already have a custom statusline. If you do, the installer leaves it alone and prints the merge note.

**Manual setup:** If you need to configure it yourself, add one of these to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash /path/to/cavemaenggu-statusline.sh"
  }
}
```

```json
{
  "statusLine": {
    "type": "command",
    "command": "powershell -ExecutionPolicy Bypass -File C:\\path\\to\\cavemaenggu-statusline.ps1"
  }
}
```

Replace the path with the actual script location (e.g. `~/.claude/hooks/` for standalone installs, or the plugin install directory for plugin installs).

**Custom statusline:** If you already have a statusline script, add this snippet to it:

```bash
cavemaenggu_text=""
cavemaenggu_flag="$HOME/.claude/.cavemaenggu-active"
if [ -f "$cavemaenggu_flag" ]; then
  cavemaenggu_mode=$(cat "$cavemaenggu_flag" 2>/dev/null)
  if [ "$cavemaenggu_mode" = "full" ] || [ -z "$cavemaenggu_mode" ]; then
    cavemaenggu_text=$'\033[38;5;172m[MAENGGU]\033[0m'
  else
    cavemaenggu_suffix=$(echo "$cavemaenggu_mode" | tr '[:lower:]' '[:upper:]')
    cavemaenggu_text=$'\033[38;5;172m[MAENGGU:'"${cavemaenggu_suffix}"$']\033[0m'
  fi
fi
```

Badge examples:
- `/cavemaenggu` (or `/mg`) → `[MAENGGU]`
- `/cavemaenggu ultra` → `[MAENGGU:ULTRA]`
- `/cavemaenggu maeng-gu` → `[MAENGGU:MAENG-GU]`
- `/cavemaenggu maeng-gu-ultra` → `[MAENGGU:MAENG-GU-ULTRA]`
- `/cavemaenggu-commit` → `[MAENGGU:COMMIT]`
- `/cavemaenggu-review` → `[MAENGGU:REVIEW]`

## How It Works

```
SessionStart hook ──writes "full"──▶ ~/.claude/.cavemaenggu-active ◀──writes mode── UserPromptSubmit hook
                                              │
                                           reads
                                              ▼
                                     Statusline script
                                    [MAENGGU:ULTRA] │ ...
```

SessionStart stdout is injected as hidden system context — Claude sees it, users don't. The statusline runs as a separate process. The flag file is the bridge.

## Uninstall

If installed via plugin: disable the plugin — hooks deactivate automatically.

If installed via `install.sh`:
```bash
bash hooks/uninstall.sh
```

Or manually:
1. Remove `~/.claude/hooks/cavemaenggu-activate.js`, `~/.claude/hooks/cavemaenggu-mode-tracker.js`, `~/.claude/hooks/cavemaenggu-config.js`, and the matching statusline script (`cavemaenggu-statusline.sh` on macOS/Linux or `cavemaenggu-statusline.ps1` on Windows)
2. Remove the SessionStart, UserPromptSubmit, and statusLine entries from `~/.claude/settings.json`
3. Delete `~/.claude/.cavemaenggu-active`
