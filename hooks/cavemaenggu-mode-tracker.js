#!/usr/bin/env node
// cavemaenggu — UserPromptSubmit hook to track which cavemaenggu mode is active.
// Inspects user input for /cavemaenggu (and /mg short alias) commands and writes
// the resolved mode to the flag file. Also handles natural-language activation
// in English ("activate cavemaenggu") and Korean ("맹구야").

const fs = require('fs');
const path = require('path');
const os = require('os');
const { getDefaultMode, safeWriteFlag, readFlag } = require('./cavemaenggu-config');

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const flagPath = path.join(claudeDir, '.cavemaenggu-active');

let input = '';
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const prompt = (data.prompt || '').trim().toLowerCase();
    // Hangul has no case — keep the raw prompt so future tweaks to lowercasing
    // do not silently break Korean activation.
    const rawPrompt = (data.prompt || '').trim();

    // Hangul activation/deactivation matchers. Defined once so the deactivation
    // block below can reuse the same regex.
    //
    // Activation is intentionally permissive: any mention of 맹구 (e.g. "맹구야",
    // "맹구 모드", "맹구로 말해") flips the flag to `maeng-gu` (alias for
    // maeng-gu-full). README documents the trade-off — a prompt asking about the
    // cartoon character of the same name will also activate. Users revert with
    // "stop caveman", "보통 모드", or any /cavemaenggu slash.
    //
    // Deactivation matches "맹구 꺼/그만/종료/해제/중단/중지" and any of the common
    // "normal mode" Korean glosses (보통/정상/기본/일반/평소 + 모드/말투).
    const KOREAN_ACTIVATE = /맹구/u;
    const KOREAN_DEACTIVATE = /맹구\s*(?:꺼|그만|종료|해제|중단|중지)|(?:보통|정상|기본|일반|평소)\s*(?:모드|말투)/u;

    // Natural language activation matches both the new brand ("cavemaenggu") and
    // the upstream brand ("caveman") — the README still tells users that "talk
    // like caveman" works, and we want to stay friendly to anyone migrating.
    const NL_BRAND = /\b(?:cavemaenggu|caveman)\b/i;
    if (NL_BRAND.test(prompt) &&
        (/\b(activate|enable|turn on|start|talk like)\b/i.test(prompt) ||
         /\bmode\b/i.test(prompt))) {
      if (!/\b(stop|disable|turn off|deactivate)\b/i.test(prompt)) {
        const mode = getDefaultMode();
        if (mode !== 'off') {
          safeWriteFlag(flagPath, mode);
        }
      }
    }

    // Korean (Hangul) natural-language activation for maeng-gu mode.
    // Always writes 'maeng-gu' (= maeng-gu-full alias) regardless of
    // CAVEMAENGGU_DEFAULT_MODE — the user explicitly chose CJK-script compression
    // by speaking Korean, so respect that intent over the configured default.
    // Still honors the off switch: if default mode is 'off', user has globally
    // disabled auto-activation and we do not override.
    if (KOREAN_ACTIVATE.test(rawPrompt) && !KOREAN_DEACTIVATE.test(rawPrompt)) {
      if (getDefaultMode() !== 'off') {
        safeWriteFlag(flagPath, 'maeng-gu');
      }
    }

    // Match /cavemaenggu and /mg slash commands. /caveman is intentionally NOT
    // matched here — that namespace belongs to the upstream caveman plugin so
    // both can be installed side by side without collision.
    if (/^\/(?:cavemaenggu|mg)(?:[-:\s]|$)/.test(prompt)) {
      const parts = prompt.split(/\s+/);
      const cmd = parts[0];
      const arg = parts[1] || '';

      let mode = null;

      if (cmd === '/cavemaenggu-commit' || cmd === '/mg-commit') {
        mode = 'commit';
      } else if (cmd === '/cavemaenggu-review' || cmd === '/mg-review') {
        mode = 'review';
      } else if (cmd === '/cavemaenggu-compress' ||
                 cmd === '/mg-compress' ||
                 cmd === '/cavemaenggu:cavemaenggu-compress') {
        mode = 'compress';
      } else if (cmd === '/cavemaenggu' ||
                 cmd === '/cavemaenggu:cavemaenggu' ||
                 cmd === '/mg') {
        if (arg === 'lite') mode = 'lite';
        else if (arg === 'ultra') mode = 'ultra';
        else if (arg === 'maeng-gu-lite') mode = 'maeng-gu-lite';
        else if (arg === 'maeng-gu' || arg === 'maeng-gu-full') mode = 'maeng-gu';
        else if (arg === 'maeng-gu-ultra') mode = 'maeng-gu-ultra';
        else mode = getDefaultMode();
      }

      if (mode && mode !== 'off') {
        safeWriteFlag(flagPath, mode);
      } else if (mode === 'off') {
        try { fs.unlinkSync(flagPath); } catch (e) {}
      }
    }

    // Detect deactivation — natural language (English + Korean) and slash commands.
    // We still match "stop caveman" because the README has historically taught users
    // to say that and we don't want to surprise migrating users with a dead phrase.
    if (/\b(stop|disable|deactivate|turn off)\b.*\b(?:cavemaenggu|caveman)\b/i.test(prompt) ||
        /\b(?:cavemaenggu|caveman)\b.*\b(stop|disable|deactivate|turn off)\b/i.test(prompt) ||
        /\bnormal mode\b/i.test(prompt) ||
        KOREAN_DEACTIVATE.test(rawPrompt)) {
      try { fs.unlinkSync(flagPath); } catch (e) {}
    }

    // Per-turn reinforcement: emit a structured reminder when cavemaenggu is active.
    // The SessionStart hook injects the full ruleset once, but models lose it
    // when other plugins inject competing style instructions every turn.
    // This keeps cavemaenggu visible in the model's attention on every user message.
    //
    // Skip independent modes (commit, review, compress) — they have their own
    // skill behavior and the base cavemaenggu rules would conflict.
    // readFlag enforces symlink-safe read + size cap + VALID_MODES whitelist.
    // If the flag is missing, corrupted, oversized, or a symlink pointing at
    // something like ~/.ssh/id_rsa, readFlag returns null and we emit nothing
    // — never inject untrusted bytes into model context.
    const INDEPENDENT_MODES = new Set(['commit', 'review', 'compress']);
    const activeMode = readFlag(flagPath);
    if (activeMode && !INDEPENDENT_MODES.has(activeMode)) {
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: {
          hookEventName: "UserPromptSubmit",
          additionalContext: "CAVEMAENGGU MODE ACTIVE (" + activeMode + "). " +
            "Drop articles/filler/pleasantries/hedging. Fragments OK. " +
            "Code/commits/security: write normal."
        }
      }));
    }
  } catch (e) {
    // Silent fail
  }
});
