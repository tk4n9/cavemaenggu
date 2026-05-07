# CLAUDE.md — cavemaenggu

## README is a product artifact

README = product front door. Non-technical people read it to decide if cavemaenggu worth install. Treat like UI copy.

**Rules for any README change:**

- Readable by non-AI-agent users. If you write "SessionStart hook injects system context," invisible to most — translate it.
- Keep Before/After examples first. That the pitch.
- Install table always complete + accurate. One broken install command costs real user.
- What You Get table must sync with actual code. Feature ships or removed → update table.
- Preserve voice. Caveman speak in README on purpose. "Brain still big." "Cost go down forever." "One rock. That it." — intentional brand. Don't normalize.
- Benchmark numbers from real runs in `benchmarks/` and `evals/`. Never invent or round. Re-run if doubt.
- Adding new agent to install table → add detail block in `<details>` section below.
- Readability check before any README commit: would non-programmer understand + install within 60 seconds?

---

## Project overview

Cavemaenggu makes AI coding agents respond in compressed caveman-style prose (English) or 개조식/전보체 maeng-gu-style prose (Korean) — cuts ~65-75% output tokens, full technical accuracy. Forked from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman); the maeng-gu (맹구) family and `/mg` short alias are this fork's additions. Ships as Claude Code plugin, Codex plugin, Gemini CLI extension, agent rule files for Cursor, Windsurf, Cline, Copilot, 40+ others via `npx skills`.

---

## File structure and what owns what

### Single source of truth files — edit only these

| File | What it controls |
|------|-----------------|
| `skills/cavemaenggu/SKILL.md` | Cavemaenggu behavior: intensity levels, rules, maeng-gu mode, auto-clarity, persistence. Only file to edit for behavior changes. |
| `rules/cavemaenggu-activate.md` | Always-on auto-activation rule body. CI injects into Cursor, Windsurf, Cline, Copilot rule files. Edit here, not agent-specific copies. |
| `skills/cavemaenggu-commit/SKILL.md` | Commit message behavior. Fully independent skill. |
| `skills/cavemaenggu-review/SKILL.md` | Code review behavior. Fully independent skill. |
| `skills/cavemaenggu-help/SKILL.md` | Quick-reference card. One-shot display, not a persistent mode. |
| `skills/cavemaenggu-stats/SKILL.md` | Claude Code stats receipt behavior. Hook-backed; model does not compute numbers. |
| `skills/cavecrew/SKILL.md` | Delegation guide for compressed subagent presets. |
| `cavemaenggu-compress/SKILL.md` | Compress sub-skill behavior. |

### Auto-generated / auto-synced — do not edit directly

Overwritten by CI on push to main when sources change. Edits here lost.

| File | Synced from |
|------|-------------|
| `cavemaenggu/SKILL.md` | `skills/cavemaenggu/SKILL.md` |
| `plugins/cavemaenggu/skills/cavemaenggu/SKILL.md` | `skills/cavemaenggu/SKILL.md` |
| `.cursor/skills/cavemaenggu/SKILL.md` | `skills/cavemaenggu/SKILL.md` |
| `.windsurf/skills/cavemaenggu/SKILL.md` | `skills/cavemaenggu/SKILL.md` |
| `cavemaenggu.skill` | ZIP of `skills/cavemaenggu/` directory |
| `.clinerules/cavemaenggu.md` | `rules/cavemaenggu-activate.md` |
| `.github/copilot-instructions.md` | `rules/cavemaenggu-activate.md` |
| `.cursor/rules/cavemaenggu.mdc` | `rules/cavemaenggu-activate.md` + Cursor frontmatter |
| `.windsurf/rules/cavemaenggu.md` | `rules/cavemaenggu-activate.md` + Windsurf frontmatter |

---

## CI sync workflow

`.github/workflows/sync-skill.yml` triggers on main push when `skills/cavemaenggu/SKILL.md` or `rules/cavemaenggu-activate.md` changes.

What it does:
1. Copies `skills/cavemaenggu/SKILL.md` to all agent-specific SKILL.md locations
2. Rebuilds `cavemaenggu.skill` as a ZIP of `skills/cavemaenggu/`
3. Rebuilds all agent rule files from `rules/cavemaenggu-activate.md`, prepending agent-specific frontmatter (Cursor needs `alwaysApply: true`, Windsurf needs `trigger: always_on`)
4. Commits and pushes with `[skip ci]` to avoid loops

CI bot commits as `github-actions[bot]`. After PR merge, wait for workflow before declaring release complete.

---

## Hook system (Claude Code)

Four hooks/scripts in `hooks/` plus a `cavemaenggu-config.js` shared module and a `package.json` CommonJS marker. Communicate via flag file at `$CLAUDE_CONFIG_DIR/.cavemaenggu-active` (falls back to `~/.claude/.cavemaenggu-active`).

```
SessionStart hook ──writes "full"──▶ $CLAUDE_CONFIG_DIR/.cavemaenggu-active ◀──writes mode── UserPromptSubmit hook
                                                       │
                                                    reads
                                                       ▼
                                              cavemaenggu-statusline.sh
                                            [MAENGGU] / [MAENGGU:ULTRA] / ...
```

`hooks/package.json` pins the directory to `{"type": "commonjs"}` so the `.js` hooks resolve as CJS even when an ancestor `package.json` (e.g. `~/.claude/package.json` from another plugin) declares `"type": "module"`. Without this, `require()` blows up with `ReferenceError: require is not defined in ES module scope`.

All hooks honor `CLAUDE_CONFIG_DIR` for non-default Claude Code config locations.

### `hooks/cavemaenggu-config.js` — shared module

Exports:
- `getDefaultMode()` — resolves default mode from `CAVEMAENGGU_DEFAULT_MODE` env var, then `$XDG_CONFIG_HOME/cavemaenggu/config.json` / `~/.config/cavemaenggu/config.json` / `%APPDATA%\cavemaenggu\config.json`, then `'full'`
- `safeWriteFlag(flagPath, content)` — symlink-safe flag write. Resolves symlinked parent dirs only when owned by current user / under home on Windows. Opens with `O_NOFOLLOW` where supported. Atomic temp + rename. Creates with `0600`. Protects against local attackers replacing the predictable flag path with a symlink to clobber files writable by the user. Used by both write hooks. Silent-fails on all filesystem errors.
- `readFlag(flagPath)` — symlink-safe read with size cap (`MAX_FLAG_BYTES = 64`) and a `VALID_MODES` whitelist; anything else → null. Prevents oversized or arbitrary flag content from being trusted.
- `appendFlag(filePath, line)` / `readHistory(filePath)` — symlink-safe stats history append/read helpers for `.cavemaenggu-history.jsonl`.

### `hooks/cavemaenggu-activate.js` — SessionStart hook

Runs once per Claude Code session start. Three things:
1. Writes the active mode to `$CLAUDE_CONFIG_DIR/.cavemaenggu-active` via `safeWriteFlag` (creates if missing)
2. Emits cavemaenggu ruleset as hidden stdout — Claude Code injects SessionStart hook stdout as system context, invisible to user
3. Checks `settings.json` for statusline config; if missing, appends nudge to offer setup on first interaction

Silent-fails on all filesystem errors — never blocks session start.

### `hooks/cavemaenggu-mode-tracker.js` — UserPromptSubmit hook

Reads JSON from stdin. Three responsibilities:

**1. Slash-command activation.** Slash dispatch matches `/^\/(?:cavemaenggu|mg)(?:[-:\s]|$)/` — explicitly excluding `/caveman` so the upstream caveman plugin can install side by side. Either prefix writes mode to flag file via `safeWriteFlag`:
- `/cavemaenggu` or `/mg` → configured default (see `cavemaenggu-config.js`, defaults to `full`)
- `/cavemaenggu lite` / `/mg lite` → `lite`
- `/cavemaenggu ultra` / `/mg ultra` → `ultra`
- `/cavemaenggu maeng-gu` or `/cavemaenggu maeng-gu-full` (also `/mg maeng-gu`) → `maeng-gu`
- `/cavemaenggu maeng-gu-lite` / `/mg maeng-gu-lite` → `maeng-gu-lite`
- `/cavemaenggu maeng-gu-ultra` / `/mg maeng-gu-ultra` → `maeng-gu-ultra`
- `/cavemaenggu-commit` / `/mg-commit` → `commit`
- `/cavemaenggu-review` / `/mg-review` → `review`
- `/cavemaenggu-compress` / `/mg-compress` → `compress`

**Stats command.** `/cavemaenggu-stats` / `/mg-stats` blocks the prompt and returns measured Claude Code session stats from `hooks/cavemaenggu-stats.js`. Supported flags: `--share`, `--all`, `--since 7d`.

**2. Natural-language activation/deactivation.** Matches phrases like "activate cavemaenggu", "talk like caveman", "cavemaenggu mode", and Hangul triggers via `/맹구/u` (e.g. "맹구야", "맹구 모드", "맹구 켜") and writes the configured default mode. Matches "stop caveman", "disable cavemaenggu", "normal mode", "보통 모드", "맹구 꺼" etc. and deletes the flag file. The English regex stays `cavemaenggu|caveman` so existing muscle memory from upstream caveman keeps working — that back-compat is intentional.

**3. Per-turn reinforcement.** When flag is set to a non-independent mode (i.e. not `commit`/`review`/`compress`), emits a small `hookSpecificOutput` JSON reminder so the model keeps cavemaenggu style after other plugins inject competing instructions mid-conversation. The full ruleset still comes from SessionStart — this is just an attention anchor.

### `hooks/cavemaenggu-statusline.sh` — Statusline badge

Reads flag file at `$CLAUDE_CONFIG_DIR/.cavemaenggu-active`. Outputs colored badge string for Claude Code statusline:
- `full` or empty → `[MAENGGU]` (orange)
- anything else → `[MAENGGU:<MODE_UPPERCASED>]` (orange) — e.g. `[MAENGGU:ULTRA]`, `[MAENGGU:MAENG-GU]`
- optional savings suffix from `.cavemaenggu-statusline-suffix`, written by `/cavemaenggu-stats`; disable with `CAVEMAENGGU_STATUSLINE_SAVINGS=0`

Configured in `settings.json` under `statusLine.command`. PowerShell counterpart at `hooks/cavemaenggu-statusline.ps1` for Windows.

### Hook installation

**Plugin install** — hooks wired automatically by plugin system.

**Standalone install** — `hooks/install.sh` (macOS/Linux) or `hooks/install.ps1` (Windows) copies hook files into `~/.claude/hooks/` and patches `~/.claude/settings.json` to register SessionStart and UserPromptSubmit hooks plus statusline. Both installers honor `CAVEMAENGGU_SETTINGS` (custom settings.json path) and `CAVEMAENGGU_HOOKS_DIR` (custom hooks directory) env vars.

**Uninstall** — `hooks/uninstall.sh` / `hooks/uninstall.ps1` removes hook files and patches settings.json.

---

## Skill system

Skills = Markdown files with YAML frontmatter consumed by Claude Code's skill/plugin system and by `npx skills` for other agents.

### Intensity levels

Defined in `skills/cavemaenggu/SKILL.md`. Six levels: `lite`, `full` (default), `ultra`, three maeng-gu (`maeng-gu-lite`, `maeng-gu-full`, `maeng-gu-ultra`). Persists until changed or session ends. The wenyan (文言文) family inherited from upstream was removed in favor of maeng-gu to keep the SKILL.md footprint small for prompt-cache efficiency.

### Auto-clarity rule

Cavemaenggu drops to normal prose for: security warnings, irreversible action confirmations, multi-step sequences where fragment ambiguity risks misread, user confused or repeating question. Resumes after. Defined in skill — preserve in any SKILL.md edit.

### cavemaenggu-compress

Sub-skill in `cavemaenggu-compress/SKILL.md`. Takes file path, compresses prose to caveman style, writes to original path, saves backup at `<filename>.original.md`. Validates headings, code blocks, URLs, file paths, commands preserved. Retries up to 2 times on failure with targeted patches only. Requires Python 3.10+.

### cavemaenggu-commit / cavemaenggu-review

Independent skills in `skills/cavemaenggu-commit/SKILL.md` and `skills/cavemaenggu-review/SKILL.md`. Both have own `description` and `name` frontmatter so they load independently. cavemaenggu-commit: Conventional Commits, ≤50 char subject. cavemaenggu-review: one-line comments in `L<line>: <severity> <problem>. <fix>.` format.

### cavemaenggu-stats / cavemaenggu-init / cavecrew

- `cavemaenggu-stats` is hook-backed. `hooks/cavemaenggu-mode-tracker.js` intercepts `/cavemaenggu-stats`, calls `hooks/cavemaenggu-stats.js`, and returns a `decision: "block"` JSON response. Do not ask the model to estimate numbers.
- `tools/cavemaenggu-init.js` writes repo-local always-on rule files for Cursor, Windsurf, Cline, Copilot, and `AGENTS.md`. Commands: `/cavemaenggu-init`, `/mg-init`.
- `cavecrew` ships compressed subagent presets in `agents/` and plugin copies in `plugins/cavemaenggu/agents/`.

### cavemaenggu-shrink

MCP stdio proxy in `mcp-servers/cavemaenggu-shrink/`. Wraps an upstream MCP server and compresses prose fields (default: `description`) in `tools/list`, `prompts/list`, and `resources/list`. Env vars: `CAVEMAENGGU_SHRINK_FIELDS`, `CAVEMAENGGU_SHRINK_DEBUG`.

### Slash commands

`commands/` ships paired TOML files: each `cavemaenggu*.toml` has a `mg*.toml` twin with identical prompt, so `/mg`, `/mg-commit`, `/mg-review`, `/mg-init`, and `/mg-stats` resolve through Claude Code's command system to the same prompts.

---

## Agent distribution

How cavemaenggu reaches each agent type:

| Agent | Mechanism | Auto-activates? |
|-------|-----------|----------------|
| Claude Code | Plugin (hooks + skills) or standalone hooks | Yes — SessionStart hook injects rules |
| Codex | Plugin in `plugins/cavemaenggu/` plus repo `.codex/hooks.json` and `.codex/config.toml` | Yes on macOS/Linux — SessionStart hook |
| Gemini CLI | Extension with `GEMINI.md` context file | Yes — context file loads every session |
| Cursor | `.cursor/rules/cavemaenggu.mdc` with `alwaysApply: true` | Yes — always-on rule |
| Windsurf | `.windsurf/rules/cavemaenggu.md` with `trigger: always_on` | Yes — always-on rule |
| Cline | `.clinerules/cavemaenggu.md` (auto-discovered) | Yes — Cline injects all .clinerules files |
| Copilot | `.github/copilot-instructions.md` + `AGENTS.md` | Yes — repo-wide instructions |
| Others | `npx skills add tk4n9/cavemaenggu` | No — user must say `/cavemaenggu` (or `/mg`) each session |

For agents without hook systems, minimal always-on snippet lives in README under "Want it always on?" — keep current with `rules/cavemaenggu-activate.md`.

---

## Evals

`evals/` has three-arm harness:
- `__baseline__` — no system prompt
- `__terse__` — `Answer concisely.`
- `<skill>` — `Answer concisely.\n\n{SKILL.md}`

Honest delta = **skill vs terse**, not skill vs baseline. Baseline comparison conflates skill with generic terseness — that cheating. Harness designed to prevent this.

`llm_run.py` calls `claude -p --system-prompt ...` per (prompt, arm), saves to `evals/snapshots/results.json`. `measure.py` reads snapshot offline with tiktoken (OpenAI BPE — approximates Claude tokenizer, ratios meaningful, absolute numbers approximate).

Add skill: drop `skills/<name>/SKILL.md`. Harness auto-discovers. Add prompt: append line to `evals/prompts/en.txt`.

Snapshots committed to git. CI reads without API calls. Only regenerate when SKILL.md or prompts change.

---

## Benchmarks

`benchmarks/` runs real prompts through Claude API (not Claude Code CLI), records raw token counts. Results committed as JSON in `benchmarks/results/`. Benchmark table in README generated from results — update when regenerating.

To reproduce: `uv run python benchmarks/run.py` (needs `ANTHROPIC_API_KEY` in `.env.local`).

---

## Key rules for agents working here

- Edit `skills/cavemaenggu/SKILL.md` for behavior changes. Never edit synced copies.
- Edit `rules/cavemaenggu-activate.md` for auto-activation rule changes. Never edit agent-specific rule copies.
- README most important file for user-facing impact. Optimize for non-technical readers. Preserve caveman voice.
- Benchmark and eval numbers must be real. Never fabricate or estimate.
- CI workflow commits back to main after merge. Account for when checking branch state.
- Hook files must silent-fail on all filesystem errors. Never let hook crash block session start.
- Any new flag file write must go through `safeWriteFlag()` in `cavemaenggu-config.js`. Direct `fs.writeFileSync` on predictable user-owned paths reopens the symlink-clobber attack surface.
- Hooks must respect `CLAUDE_CONFIG_DIR` env var, not hardcode `~/.claude`. Same for `install.sh` / `install.ps1` / statusline scripts. Settings/hooks dirs respect `CAVEMAENGGU_SETTINGS` / `CAVEMAENGGU_HOOKS_DIR`.
- Slash dispatch regex must continue to exclude `/caveman` so the upstream plugin can coexist. The natural-language regex (`cavemaenggu|caveman` plus `/맹구/u`) is intentionally permissive — that is back-compat for muscle memory and Korean activation.
