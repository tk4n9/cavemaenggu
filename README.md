<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/rock_1faa8.png" width="120" />
</p>

<h1 align="center">cavemaenggu</h1>

<p align="center">
  <strong>why use many token when few do trick</strong>
</p>

<p align="center">
  <a href="https://github.com/tk4n9/cavemaenggu/stargazers"><img src="https://img.shields.io/github/stars/tk4n9/cavemaenggu?style=flat&color=yellow" alt="Stars"></a>
  <a href="https://github.com/tk4n9/cavemaenggu/commits/main"><img src="https://img.shields.io/github/last-commit/tk4n9/cavemaenggu?style=flat" alt="Last Commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/tk4n9/cavemaenggu?style=flat" alt="License"></a>
</p>

<p align="center">
  <a href="#before--after">Before/After</a> •
  <a href="#install">Install</a> •
  <a href="#intensity-levels">Levels</a> •
  <a href="#cavemaenggu-skills">Skills</a> •
  <a href="#benchmarks">Benchmarks</a> •
  <a href="#evals">Evals</a>
</p>

---

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill/plugin and Codex plugin that makes agent talk like smart caveman — cutting **~75% of output tokens** while keeping full technical accuracy. Now with [맹구 mode](#맹구-maeng-gu-mode), [terse commits](#cavemaenggu-commit), [one-line code reviews](#cavemaenggu-review), and a [compression tool](#cavemaenggu-compress) that cuts **~46% of input tokens** every session.

Cavemaenggu = **caveman** (English compression) + **맹구** (Korean compression family). Forked from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman), adds the maeng-gu family for Korean 개조식/전보체 output. Same brain. Two languages. Same compression.

## Before / After

<table>
<tr>
<td width="50%">

### 🗣️ Normal Claude (69 tokens)

> "The reason your React component is re-rendering is likely because you're creating a new object reference on each render cycle. When you pass an inline object as a prop, React's shallow comparison sees it as a different object every time, which triggers a re-render. I'd recommend using useMemo to memoize the object."

</td>
<td width="50%">

### 🪨 Cavemaenggu Claude (19 tokens)

> "New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`."

</td>
</tr>
<tr>
<td>

### 🗣️ Normal Claude

> "Sure! I'd be happy to help you with that. The issue you're experiencing is most likely caused by your authentication middleware not properly validating the token expiry. Let me take a look and suggest a fix."

</td>
<td>

### 🪨 Cavemaenggu Claude

> "Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:"

</td>
</tr>
</table>

**Same fix. 75% less word. Brain still big.**

**Pick your level of grunt:**

<table>
<tr>
<td width="25%">

#### 🪶 Lite

> "Your component re-renders because you create a new object reference each render. Inline object props fail shallow comparison every time. Wrap it in `useMemo`."

</td>
<td width="25%">

#### 🪨 Full

> "New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`."

</td>
<td width="25%">

#### 🔥 Ultra

> "Inline obj prop → new ref → re-render. `useMemo`."

</td>
<td width="25%">

#### 🇰🇷 맹구

> "인라인 객체 prop → 신참조 → 리렌더. `useMemo`."

</td>
</tr>
</table>

**Same answer. You pick how many word.** *(Korean card shows maeng-gu-ultra; illustrative, not a measured benchmark.)*

```
┌─────────────────────────────────────┐
│  TOKENS SAVED          ████████ 75% │
│  TECHNICAL ACCURACY    ████████ 100%│
│  SPEED INCREASE        ████████ ~3x │
│  VIBES                 ████████ OOG │
└─────────────────────────────────────┘
```

- **Faster response** — less token to generate = speed go brrr
- **Easier to read** — no wall of text, just the answer
- **Same accuracy** — all technical info kept, only fluff removed ([science say so](https://arxiv.org/abs/2604.00025))
- **Save money** — ~71% less output token = less cost
- **Korean too** — 맹구 family for 개조식/전보체 output, same compression vibe
- **Fun** — every code review become comedy

## Install

Pick your agent. One command. Done.

| Agent | Install |
|-------|---------|
| **Claude Code** | `claude plugin marketplace add tk4n9/cavemaenggu && claude plugin install cavemaenggu@cavemaenggu` |
| **Codex** | Clone repo → `/plugins` → Search "Cavemaenggu" → Install |
| **Gemini CLI** | `gemini extensions install https://github.com/tk4n9/cavemaenggu` |
| **Cursor** | `npx skills add tk4n9/cavemaenggu -a cursor` |
| **Windsurf** | `npx skills add tk4n9/cavemaenggu -a windsurf` |
| **Copilot** | `npx skills add tk4n9/cavemaenggu -a github-copilot` |
| **Cline** | `npx skills add tk4n9/cavemaenggu -a cline` |
| **Any other** | `npx skills add tk4n9/cavemaenggu` |

Install once. Use in every session for that install target after that. One rock. That it.

### What You Get

Auto-activation is built in for Claude Code, Gemini CLI, and the repo-local Codex setup below. `npx skills add` installs the skill for other agents, but does **not** install repo rule/instruction files, so Cavemaenggu does not auto-start there unless you add the always-on snippet below.

| Feature | Claude Code | Codex | Gemini CLI | Cursor | Windsurf | Cline | Copilot |
|---------|:-----------:|:-----:|:----------:|:------:|:--------:|:-----:|:-------:|
| Cavemaenggu mode | Y | Y | Y | Y | Y | Y | Y |
| Auto-activate every session | Y | Y¹ | Y | —² | —² | —² | —² |
| `/cavemaenggu` (or `/mg`) command | Y | Y¹ | Y | — | — | — | — |
| Mode switching (lite/full/ultra/maeng-gu) | Y | Y¹ | Y | Y³ | Y³ | — | — |
| Statusline badge | Y⁴ | — | — | — | — | — | — |
| cavemaenggu-commit | Y | — | Y | Y | Y | Y | Y |
| cavemaenggu-review | Y | — | Y | Y | Y | Y | Y |
| cavemaenggu-compress | Y | Y | Y | Y | Y | Y | Y |
| cavemaenggu-help | Y | — | Y | Y | Y | Y | Y |

> [!NOTE]
> Auto-activation works differently per agent: Claude Code uses SessionStart hooks, this repo's Codex dogfood setup uses `.codex/hooks.json`, Gemini uses context files. Cursor/Windsurf/Cline/Copilot can be made always-on, but `npx skills add` installs only the skill, not the repo rule/instruction files.
>
> ¹ Codex uses `$cavemaenggu` syntax, not `/cavemaenggu`. This repo ships `.codex/hooks.json`, so cavemaenggu auto-starts when you run Codex inside this repo. The installed plugin itself gives you `$cavemaenggu`; copy the same hook into another repo if you want always-on behavior there too. cavemaenggu-commit and cavemaenggu-review are not in the Codex plugin bundle — use the SKILL.md files directly.
> ² Add the "Want it always on?" snippet below to those agents' system prompt or rule file if you want session-start activation.
> ³ Cursor and Windsurf receive the full SKILL.md with all intensity levels. Mode switching works on-demand via the skill; no slash command.
> ⁴ Available in Claude Code, but plugin install only nudges setup. Standalone `install.sh` / `install.ps1` configures it automatically when no custom `statusLine` exists.

<details>
<summary><strong>Claude Code — full details</strong></summary>

The plugin install gives you skills + auto-loading hooks. If no custom `statusLine` is configured, Cavemaenggu nudges Claude to offer badge setup on first session.

```bash
claude plugin marketplace add tk4n9/cavemaenggu
claude plugin install cavemaenggu@cavemaenggu
```

**Standalone hooks (without plugin):** If you prefer not to use the plugin system:
```bash
# macOS / Linux / WSL
bash <(curl -s https://raw.githubusercontent.com/tk4n9/cavemaenggu/main/hooks/install.sh)

# Windows (PowerShell)
irm https://raw.githubusercontent.com/tk4n9/cavemaenggu/main/hooks/install.ps1 | iex
```

Or from a local clone: `bash hooks/install.sh` / `powershell -File hooks\install.ps1`

Uninstall: `bash hooks/uninstall.sh` or `powershell -File hooks\uninstall.ps1`

**Statusline badge:** Shows `[MAENGGU]`, `[MAENGGU:ULTRA]`, `[MAENGGU:MAENG-GU]`, etc. in your Claude Code status bar.

- **Plugin install:** If you do not already have a custom `statusLine`, Claude should offer to configure it on first session
- **Standalone install:** Configured automatically by `install.sh` / `install.ps1` unless you already have a custom statusline
- **Custom statusline:** Installer leaves your existing statusline alone. See [`hooks/README.md`](hooks/README.md) for the merge snippet

</details>

<details>
<summary><strong>Codex — full details</strong></summary>

**macOS / Linux:**
1. Clone repo → Open Codex in the repo directory → `/plugins` → Search "Cavemaenggu" → Install
2. Repo-local auto-start is already wired by `.codex/hooks.json` + `.codex/config.toml`

**Windows:**
1. Enable symlinks first: `git config --global core.symlinks true` (requires Developer Mode or admin)
2. Clone repo → Open VS Code → Codex Settings → Plugins → find "Cavemaenggu" under local marketplace → Install → Reload Window
3. Codex hooks are currently disabled on Windows, so use `$cavemaenggu` to start manually

This repo also ships `.codex/hooks.json` and enables hooks in `.codex/config.toml`, so cavemaenggu auto-activates while you run Codex inside this repo on macOS/Linux. The installed plugin gives you `$cavemaenggu`; if you want always-on behavior in other repos too, copy the same `SessionStart` hook there and enable:

```toml
[features]
codex_hooks = true
```

</details>

<details>
<summary><strong>Gemini CLI — full details</strong></summary>

```bash
gemini extensions install https://github.com/tk4n9/cavemaenggu
```

Update: `gemini extensions update cavemaenggu` · Uninstall: `gemini extensions uninstall cavemaenggu`

Auto-activates via `GEMINI.md` context file. Also ships custom Gemini commands:
- `/cavemaenggu` (or `/mg`) — switch intensity level (lite/full/ultra/maeng-gu)
- `/cavemaenggu-commit` (or `/mg-commit`) — generate terse commit message
- `/cavemaenggu-review` (or `/mg-review`) — one-line code review

</details>

<details>
<summary><strong>Cursor / Windsurf / Cline / Copilot — full details</strong></summary>

`npx skills add` installs the skill file only — it does **not** install the agent's rule/instruction file, so cavemaenggu does not auto-start. For always-on, add the "Want it always on?" snippet below to your agent's rules or system prompt.

| Agent | Command | Not installed | Mode switching | Always-on location |
|-------|---------|--------------|:--------------:|--------------------|
| Cursor | `npx skills add tk4n9/cavemaenggu -a cursor` | `.cursor/rules/cavemaenggu.mdc` | Y | Cursor rules |
| Windsurf | `npx skills add tk4n9/cavemaenggu -a windsurf` | `.windsurf/rules/cavemaenggu.md` | Y | Windsurf rules |
| Cline | `npx skills add tk4n9/cavemaenggu -a cline` | `.clinerules/cavemaenggu.md` | — | Cline rules or system prompt |
| Copilot | `npx skills add tk4n9/cavemaenggu -a github-copilot` | `.github/copilot-instructions.md` + `AGENTS.md` | — | Copilot custom instructions |

Uninstall: `npx skills remove cavemaenggu`

Copilot works with Chat, Edits, and Coding Agent.

</details>

<details>
<summary><strong>Any other agent (opencode, Roo, Amp, Goose, Kiro, and 40+ more)</strong></summary>

[npx skills](https://github.com/vercel-labs/skills) supports 40+ agents:

```bash
npx skills add tk4n9/cavemaenggu           # auto-detect agent
npx skills add tk4n9/cavemaenggu -a amp
npx skills add tk4n9/cavemaenggu -a augment
npx skills add tk4n9/cavemaenggu -a goose
npx skills add tk4n9/cavemaenggu -a kiro-cli
npx skills add tk4n9/cavemaenggu -a roo
# ... and many more
```

Uninstall: `npx skills remove cavemaenggu`

> **Windows note:** `npx skills` uses symlinks by default. If symlinks fail, add `--copy`: `npx skills add tk4n9/cavemaenggu --copy`

**Important:** These agents don't have a hook system, so cavemaenggu won't auto-start. Say `/cavemaenggu` or "talk like caveman" to activate each session.

**Want it always on?** Paste this into your agent's system prompt or rules file — cavemaenggu will be active from the first message, every session:

```
Terse like caveman. Technical substance exact. Only fluff die.
Drop: articles, filler (just/really/basically), pleasantries, hedging.
Fragments OK. Short synonyms. Code unchanged.
Pattern: [thing] [action] [reason]. [next step].
ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift.
Code/commits/PRs: normal. Off: "stop caveman" / "normal mode".
```

Where to put it:
| Agent | File |
|-------|------|
| opencode | `.config/opencode/AGENTS.md` |
| Roo | `.roo/rules/cavemaenggu.md` |
| Amp | your workspace system prompt |
| Others | your agent's system prompt or rules file |

</details>

## Usage

Trigger with:
- `/cavemaenggu` (or short alias `/mg`) or Codex `$cavemaenggu`
- "talk like caveman"
- "cavemaenggu mode" or "caveman mode"
- "less tokens please"
- Korean: "맹구야", "맹구 모드", "맹구 켜"

Stop with: "stop caveman", "normal mode", or Korean equivalent ("보통 모드", "맹구 꺼")

### Intensity Levels

| Level | Trigger | Short alias | What it do |
|-------|---------|-------------|------------|
| **Lite** | `/cavemaenggu lite` | `/mg lite` | Drop filler, keep grammar. Professional but no fluff |
| **Full** | `/cavemaenggu full` | `/mg full` | Default caveman. Drop articles, fragments, full grunt |
| **Ultra** | `/cavemaenggu ultra` | `/mg ultra` | Maximum compression. Telegraphic. Abbreviate everything |

### 맹구 (Maeng-Gu) Mode

Korean compression family. 맹구 = classic Korean cartoon character, dim-but-sincere — caveman cousin from across sea. 개조식, 명사형, 전보체. Drop particles, lean Sino-Korean, Hanja when natural. Brain still big. 머리 크다.

| Level | Trigger | Short alias | What it do |
|-------|---------|-------------|------------|
| **Maeng-Gu-Lite** | `/cavemaenggu maeng-gu-lite` | `/mg maeng-gu-lite` | 개조식. Drop filler, drop honorifics, keep grammar |
| **Maeng-Gu-Full** | `/cavemaenggu maeng-gu` | `/mg maeng-gu` | 명사형/전보체. Drop particles, Sino-Korean preferred, arrows for causality |
| **Maeng-Gu-Ultra** | `/cavemaenggu maeng-gu-ultra` | `/mg maeng-gu-ultra` | Pure noun strings. Aggressive Hanja. `[명사] [명사] → [결과]. [조치].` |

Korean technical English unchanged: `useMemo`, `API`, `DB`, `handshake`, `middleware`. Code blocks pass through. Auto-clarity carve-outs apply (security warnings, irreversible ops).

Examples (hand-authored illustrations, not measured benchmarks):

- `maeng-gu-lite` — "커넥션 풀은 요청마다 새로 만들지 않고 열린 연결을 재사용한다. 반복적인 handshake 부하를 피한다."
- `maeng-gu-full` — "풀 = 열린 DB 연결 재사용. 요청마다 신연결 X. handshake 부하 생략."
- `maeng-gu-ultra` — "풀 = DB 연결 재사용. handshake 생략 → 부하시 高速."

Level stick until you change it or session end.

## Cavemaenggu Skills

### cavemaenggu-commit

`/cavemaenggu-commit` (or `/mg-commit`) — terse commit messages. Conventional Commits. ≤50 char subject. Why over what.

### cavemaenggu-review

`/cavemaenggu-review` (or `/mg-review`) — one-line PR comments: `L42: 🔴 bug: user null. Add guard.` No throat-clearing.

### cavemaenggu-help

`/cavemaenggu-help` — quick-reference card. All modes, skills, commands, one command away.

### cavemaenggu-compress

`/cavemaenggu:compress <filepath>` — cavemaenggu make Claude *speak* with fewer tokens. **Compress** make Claude *read* fewer tokens.

Your `CLAUDE.md` loads on **every session start**. Cavemaenggu Compress rewrites memory files into caveman-speak so Claude reads less — without you losing the human-readable original.

```
/cavemaenggu:compress CLAUDE.md
```

```
CLAUDE.md          ← compressed (Claude reads this every session — fewer tokens)
CLAUDE.original.md ← human-readable backup (you read and edit this)
```

| File | Original | Compressed | Saved |
|------|----------:|----------:|------:|
| `claude-md-preferences.md` | 706 | 285 | **59.6%** |
| `project-notes.md` | 1145 | 535 | **53.3%** |
| `claude-md-project.md` | 1122 | 636 | **43.3%** |
| `todo-list.md` | 627 | 388 | **38.1%** |
| `mixed-with-code.md` | 888 | 560 | **36.9%** |
| **Average** | **898** | **481** | **46%** |

Code blocks, URLs, file paths, commands, headings, dates, version numbers — anything technical passes through untouched. Only prose gets compressed. See the full [cavemaenggu-compress README](cavemaenggu-compress/README.md) for details. [Security note](./cavemaenggu-compress/SECURITY.md): Snyk flags this as High Risk due to subprocess/file patterns — it's a false positive.

## Benchmarks

Real token counts from the Claude API ([reproduce it yourself](benchmarks/)):

<!-- BENCHMARK-TABLE-START -->
| Task | Normal (tokens) | Cavemaenggu (tokens) | Saved |
|------|---------------:|---------------------:|------:|
| Explain React re-render bug | 1180 | 159 | 87% |
| Fix auth middleware token expiry | 704 | 121 | 83% |
| Set up PostgreSQL connection pool | 2347 | 380 | 84% |
| Explain git rebase vs merge | 702 | 292 | 58% |
| Refactor callback to async/await | 387 | 301 | 22% |
| Architecture: microservices vs monolith | 446 | 310 | 30% |
| Review PR for security issues | 678 | 398 | 41% |
| Docker multi-stage build | 1042 | 290 | 72% |
| Debug PostgreSQL race condition | 1200 | 232 | 81% |
| Implement React error boundary | 3454 | 456 | 87% |
| **Average** | **1214** | **294** | **65%** |

*Range: 22%–87% savings across prompts. Numbers carried from upstream caveman benchmarks; the maeng-gu fork inherits the same English compression behavior.*
<!-- BENCHMARK-TABLE-END -->

> [!IMPORTANT]
> Cavemaenggu only affects output tokens — thinking/reasoning tokens are untouched. Cavemaenggu no make brain smaller. Cavemaenggu make *mouth* smaller. Biggest win is **readability and speed**, cost savings are a bonus.

A March 2026 paper ["Brevity Constraints Reverse Performance Hierarchies in Language Models"](https://arxiv.org/abs/2604.00025) found that constraining large models to brief responses **improved accuracy by 26 percentage points** on certain benchmarks and completely reversed performance hierarchies. Verbose not always better. Sometimes less word = more correct.

## Evals

Cavemaenggu not just claim 75%. Cavemaenggu **prove** it.

The `evals/` directory has a three-arm eval harness that measures real token compression against a proper control — not just "verbose vs skill" but "terse vs skill". Because comparing cavemaenggu to verbose Claude conflate the skill with generic terseness. That cheating. Cavemaenggu not cheat.

```bash
# Run the eval (needs claude CLI)
uv run python evals/llm_run.py

# Read results (no API key, runs offline)
uv run --with tiktoken python evals/measure.py
```

## Star This Repo

If cavemaenggu save you mass token, mass money — leave mass star. ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=tk4n9/cavemaenggu&type=Date)](https://star-history.com/#tk4n9/cavemaenggu&Date)

## Credits

Forked from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) — original caveman compression skill, hooks, and plugin scaffolding. The maeng-gu (맹구) family and `/mg` short alias are added in this fork.

## License

MIT — free like mass mammoth on open plain.
