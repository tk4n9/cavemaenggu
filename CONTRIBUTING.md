# Contributing

Improvements to the SKILL.md prompt are welcome — open a PR with before/after examples showing the change.

## How

1. Fork repo
2. Edit `skills/cavemaenggu/SKILL.md` — this is the only copy you need to touch
3. Open PR with:
   - **Before:** what cavemaenggu say now
   - **After:** what cavemaenggu say with change
   - One sentence why change better

> **Note:** `cavemaenggu/SKILL.md`, `plugins/cavemaenggu/skills/cavemaenggu/SKILL.md`, `.cursor/skills/cavemaenggu/SKILL.md`, `.windsurf/skills/cavemaenggu/SKILL.md`, and `cavemaenggu.skill` are auto-synced by CI after merge. Do not edit them directly.
>
> **Note on compress skill:** If you are modifying the compress skill, edit `cavemaenggu-compress/SKILL.md` or `cavemaenggu-compress/scripts/`. CI will automatically sync these changes to `skills/compress/` and `plugins/cavemaenggu/skills/compress/`.

> **Note on slash commands:** `commands/cavemaenggu*.toml` and `commands/mg*.toml` are paired — the `/mg` short alias must stay in sync with `/cavemaenggu`. Edit both when changing prompts.

Small focused change > big rewrite. Caveman like simple.

## Ideas

See [issues labeled `good first issue`](../../issues?q=label%3A%22good+first+issue%22) for starter tasks.
