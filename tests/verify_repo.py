#!/usr/bin/env python3
"""Local verification runner for cavemaenggu install surfaces."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CheckFailure(RuntimeError):
    pass


def section(title: str) -> None:
    print(f"\n== {title} ==")


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def run(
    args: list[str],
    *,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    result = subprocess.run(
        args,
        cwd=cwd,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise CheckFailure(
            f"Command failed ({result.returncode}): {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def read_json(path: Path) -> object:
    return json.loads(path.read_text())


def verify_synced_files() -> None:
    section("Synced Files")
    skill_source = ROOT / "skills/cavemaenggu/SKILL.md"
    rule_source = ROOT / "rules/cavemaenggu-activate.md"

    skill_copies = [
        ROOT / "cavemaenggu/SKILL.md",
        ROOT / "plugins/cavemaenggu/skills/cavemaenggu/SKILL.md",
        ROOT / ".cursor/skills/cavemaenggu/SKILL.md",
        ROOT / ".windsurf/skills/cavemaenggu/SKILL.md",
    ]
    for copy in skill_copies:
        ensure(copy.read_text() == skill_source.read_text(), f"Skill copy mismatch: {copy}")

    rule_copies = [
        ROOT / ".clinerules/cavemaenggu.md",
        ROOT / ".github/copilot-instructions.md",
    ]
    for copy in rule_copies:
        ensure(copy.read_text() == rule_source.read_text(), f"Rule copy mismatch: {copy}")

    with zipfile.ZipFile(ROOT / "cavemaenggu.skill") as archive:
        ensure(
            "cavemaenggu/SKILL.md" in archive.namelist(),
            "cavemaenggu.skill missing cavemaenggu/SKILL.md",
        )
        ensure(
            archive.read("cavemaenggu/SKILL.md").decode("utf-8") == skill_source.read_text(),
            "cavemaenggu.skill payload mismatch",
        )

    print("Synced copies and cavemaenggu.skill zip OK")


def verify_manifests_and_syntax() -> None:
    section("Manifests And Syntax")

    manifest_paths = [
        ROOT / ".agents/plugins/marketplace.json",
        ROOT / ".claude-plugin/plugin.json",
        ROOT / ".claude-plugin/marketplace.json",
        ROOT / ".codex/hooks.json",
        ROOT / "gemini-extension.json",
        ROOT / "plugins/cavemaenggu/.codex-plugin/plugin.json",
    ]
    for path in manifest_paths:
        read_json(path)

    run(["node", "--check", "hooks/cavemaenggu-config.js"])
    run(["node", "--check", "hooks/cavemaenggu-activate.js"])
    run(["node", "--check", "hooks/cavemaenggu-mode-tracker.js"])
    run(["bash", "-n", "hooks/install.sh"])
    run(["bash", "-n", "hooks/uninstall.sh"])
    run(["bash", "-n", "hooks/cavemaenggu-statusline.sh"])

    # Ensure install/uninstall scripts include cavemaenggu-config.js
    install_sh = (ROOT / "hooks/install.sh").read_text()
    uninstall_sh = (ROOT / "hooks/uninstall.sh").read_text()
    ensure("cavemaenggu-config.js" in install_sh, "install.sh missing cavemaenggu-config.js")
    ensure("cavemaenggu-config.js" in uninstall_sh, "uninstall.sh missing cavemaenggu-config.js")

    print("JSON manifests and JS/bash syntax OK")


def verify_powershell_static() -> None:
    section("PowerShell Static Checks")
    install_text = (ROOT / "hooks/install.ps1").read_text()
    uninstall_text = (ROOT / "hooks/uninstall.ps1").read_text()
    statusline_text = (ROOT / "hooks/cavemaenggu-statusline.ps1").read_text()

    ensure("cavemaenggu-config.js" in install_text, "install.ps1 missing cavemaenggu-config.js")
    ensure("cavemaenggu-config.js" in uninstall_text, "uninstall.ps1 missing cavemaenggu-config.js")
    ensure("cavemaenggu-statusline.ps1" in install_text, "install.ps1 missing statusline.ps1")
    ensure("cavemaenggu-statusline.ps1" in uninstall_text, "uninstall.ps1 missing statusline.ps1")
    ensure("-AsHashtable" not in install_text, "install.ps1 should stay compatible with Windows PowerShell 5.1")
    ensure(
        "powershell -ExecutionPolicy Bypass -File" in install_text,
        "install.ps1 missing PowerShell statusline command",
    )
    ensure("[MAENGGU" in statusline_text, "cavemaenggu-statusline.ps1 missing badge output")

    print("Windows install path statically wired")


def load_compress_modules():
    sys.path.insert(0, str(ROOT / "cavemaenggu-compress"))
    import scripts.benchmark  # noqa: F401
    import scripts.cli as cli
    import scripts.compress  # noqa: F401
    import scripts.detect as detect
    import scripts.validate as validate

    return cli, detect, validate


def verify_compress_fixtures() -> None:
    section("Compress Fixtures")
    _, detect, validate = load_compress_modules()

    fixtures = sorted((ROOT / "tests/cavemaenggu-compress").glob("*.original.md"))
    ensure(fixtures, "No cavemaenggu-compress fixtures found")

    for original in fixtures:
        compressed = original.with_name(original.name.replace(".original.md", ".md"))
        ensure(compressed.exists(), f"Missing compressed fixture for {original.name}")
        result = validate.validate(original, compressed)
        ensure(result.is_valid, f"Fixture validation failed for {compressed.name}: {result.errors}")
        ensure(detect.should_compress(compressed), f"Fixture should be compressible: {compressed.name}")

    print(f"Validated {len(fixtures)} cavemaenggu-compress fixture pairs")


def verify_compress_cli() -> None:
    section("Compress CLI")

    skip_result = run(
        ["python3", "-m", "scripts", "../hooks/install.sh"],
        cwd=ROOT / "cavemaenggu-compress",
        check=False,
    )
    ensure(skip_result.returncode == 0, "compress CLI skip path should exit 0")
    ensure("Detected: code" in skip_result.stdout, "compress CLI skip path missing detection output")
    ensure(
        "Skipping: file is not natural language" in skip_result.stdout,
        "compress CLI skip path missing skip output",
    )

    missing_result = run(
        ["python3", "-m", "scripts", "../does-not-exist.md"],
        cwd=ROOT / "cavemaenggu-compress",
        check=False,
    )
    ensure(missing_result.returncode == 1, "compress CLI missing-file path should exit 1")
    ensure("File not found" in missing_result.stdout, "compress CLI missing-file output mismatch")

    print("Compress CLI skip/error paths OK")


def verify_hook_install_flow() -> None:
    section("Claude Hook Flow")

    ensure(shutil.which("node") is not None, "node is required for hook verification")
    ensure(shutil.which("bash") is not None, "bash is required for hook verification")

    with tempfile.TemporaryDirectory(prefix="cavemaenggu-verify-") as temp_root:
        temp_root_path = Path(temp_root)
        home = temp_root_path / "home"
        claude_dir = home / ".claude"
        claude_dir.mkdir(parents=True)

        existing_settings = {
            "statusLine": {"type": "command", "command": "bash /tmp/existing-statusline.sh"},
            "hooks": {"Notification": [{"hooks": [{"type": "command", "command": "echo keep-me"}]}]},
        }
        (claude_dir / "settings.json").write_text(json.dumps(existing_settings, indent=2) + "\n")

        run(["bash", "hooks/install.sh"], env={"HOME": str(home)})

        settings = read_json(claude_dir / "settings.json")
        hooks = settings["hooks"]
        ensure(settings["statusLine"]["command"] == "bash /tmp/existing-statusline.sh", "install.sh clobbered existing statusLine")
        ensure("SessionStart" in hooks, "SessionStart hook missing after install")
        ensure("UserPromptSubmit" in hooks, "UserPromptSubmit hook missing after install")

        activate = run(
            ["node", "hooks/cavemaenggu-activate.js"],
            env={"HOME": str(home)},
        )
        ensure("CAVEMAENGGU MODE ACTIVE" in activate.stdout, "activation output missing cavemaenggu banner")
        ensure("STATUSLINE SETUP NEEDED" not in activate.stdout, "activation should stay quiet when custom statusline exists")
        ensure((claude_dir / ".cavemaenggu-active").read_text() == "full", "activation flag should default to full")

        # Test configurable default mode via CAVEMAENGGU_DEFAULT_MODE env var
        activate_custom = run(
            ["node", "hooks/cavemaenggu-activate.js"],
            env={"HOME": str(home), "CAVEMAENGGU_DEFAULT_MODE": "ultra"},
        )
        ensure("CAVEMAENGGU MODE ACTIVE" in activate_custom.stdout, "activation with custom default missing banner")
        ensure((claude_dir / ".cavemaenggu-active").read_text() == "ultra", "CAVEMAENGGU_DEFAULT_MODE=ultra should set flag to ultra")
        # Test "off" mode — activation skipped, flag removed
        activate_off = run(
            ["node", "hooks/cavemaenggu-activate.js"],
            env={"HOME": str(home), "CAVEMAENGGU_DEFAULT_MODE": "off"},
        )
        ensure("CAVEMAENGGU MODE ACTIVE" not in activate_off.stdout, "off mode should not emit cavemaenggu banner")
        ensure(not (claude_dir / ".cavemaenggu-active").exists(), "off mode should remove flag file")

        # Test mode tracker with /cavemaenggu when default is off — should NOT write flag
        subprocess.run(
            ["node", "hooks/cavemaenggu-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home), "CAVEMAENGGU_DEFAULT_MODE": "off"},
            text=True,
            input='{"prompt":"/cavemaenggu"}',
            capture_output=True,
            check=True,
        )
        ensure(not (claude_dir / ".cavemaenggu-active").exists(), "/cavemaenggu with off default should not write flag")

        # Reset back to full for subsequent tests
        (claude_dir / ".cavemaenggu-active").write_text("full")

        run(
            ["node", "hooks/cavemaenggu-mode-tracker.js"],
            env={"HOME": str(home)},
            check=True,
        )

        ultra_prompt = subprocess.run(
            ["node", "hooks/cavemaenggu-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            input='{"prompt":"/cavemaenggu ultra"}',
            capture_output=True,
            check=True,
        )
        ultra_out = ultra_prompt.stdout.strip()
        ensure(
            ultra_out == "" or ultra_out.startswith("{"),
            "mode tracker output should be empty or JSON reinforcement, got: " + ultra_out[:200],
        )
        ensure((claude_dir / ".cavemaenggu-active").read_text() == "ultra", "mode tracker did not record ultra")

        # /mg short alias must work the same as /cavemaenggu
        subprocess.run(
            ["node", "hooks/cavemaenggu-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            input='{"prompt":"/mg lite"}',
            capture_output=True,
            check=True,
        )
        ensure(
            (claude_dir / ".cavemaenggu-active").read_text() == "lite",
            "/mg lite should set flag to lite",
        )

        subprocess.run(
            ["node", "hooks/cavemaenggu-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            input='{"prompt":"normal mode"}',
            capture_output=True,
            check=True,
        )
        ensure(not (claude_dir / ".cavemaenggu-active").exists(), "normal mode should remove flag file")

        # maeng-gu (Korean) family — replaces the removed wenyan family
        (claude_dir / ".cavemaenggu-active").write_text("maeng-gu-ultra")
        statusline_mg = run(
            ["bash", "hooks/cavemaenggu-statusline.sh"],
            env={"HOME": str(home)},
        )
        ensure(
            "[MAENGGU:MAENG-GU-ULTRA]" in statusline_mg.stdout,
            "statusline badge missing maeng-gu-ultra",
        )

        # wenyan was removed — confirm the statusline whitelist no longer accepts it
        (claude_dir / ".cavemaenggu-active").write_text("wenyan-ultra")
        statusline_wenyan = run(
            ["bash", "hooks/cavemaenggu-statusline.sh"],
            env={"HOME": str(home)},
        )
        ensure(
            statusline_wenyan.stdout == "",
            "statusline should ignore removed wenyan mode, got: " + statusline_wenyan.stdout,
        )
        # restore a valid flag for any subsequent checks
        (claude_dir / ".cavemaenggu-active").write_text("maeng-gu-ultra")

        subprocess.run(
            ["node", "hooks/cavemaenggu-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            input='{"prompt":"/cavemaenggu maeng-gu"}',
            capture_output=True,
            check=True,
        )
        ensure(
            (claude_dir / ".cavemaenggu-active").read_text() == "maeng-gu",
            "mode tracker did not record maeng-gu",
        )

        subprocess.run(
            ["node", "hooks/cavemaenggu-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            input='{"prompt":"/cavemaenggu maeng-gu-ultra"}',
            capture_output=True,
            check=True,
        )
        ensure(
            (claude_dir / ".cavemaenggu-active").read_text() == "maeng-gu-ultra",
            "mode tracker did not record maeng-gu-ultra",
        )

        # /mg alias must accept the maeng-gu sub-modes too
        subprocess.run(
            ["node", "hooks/cavemaenggu-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            input='{"prompt":"/mg maeng-gu-lite"}',
            capture_output=True,
            check=True,
        )
        ensure(
            (claude_dir / ".cavemaenggu-active").read_text() == "maeng-gu-lite",
            "/mg maeng-gu-lite should set flag to maeng-gu-lite",
        )

        # wenyan slash command should NOT write a flag (removed mode)
        (claude_dir / ".cavemaenggu-active").write_text("full")
        subprocess.run(
            ["node", "hooks/cavemaenggu-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            input='{"prompt":"/cavemaenggu wenyan"}',
            capture_output=True,
            check=True,
        )
        ensure(
            (claude_dir / ".cavemaenggu-active").read_text() == "full",
            "/cavemaenggu wenyan should fall through to default 'full', got: "
            + (claude_dir / ".cavemaenggu-active").read_text(),
        )

        # Korean (Hangul) natural-language activation: any 맹구 mention writes
        # the maeng-gu alias regardless of CAVEMAENGGU_DEFAULT_MODE.
        for phrase in ("맹구야 안녕", "맹구 모드로 답해", "맹구로 말해"):
            (claude_dir / ".cavemaenggu-active").unlink(missing_ok=True)
            subprocess.run(
                ["node", "hooks/cavemaenggu-mode-tracker.js"],
                cwd=ROOT,
                env={**os.environ, "HOME": str(home)},
                text=True,
                input=json.dumps({"prompt": phrase}),
                capture_output=True,
                check=True,
            )
            ensure(
                (claude_dir / ".cavemaenggu-active").read_text() == "maeng-gu",
                f"Korean phrase '{phrase}' should set maeng-gu, got: "
                + (claude_dir / ".cavemaenggu-active").read_text(),
            )

        # Korean deactivation phrases must clear the flag even when 맹구 is in
        # the same prompt — activation regex must NOT win over deactivation.
        for phrase in ("맹구 꺼", "맹구 그만", "보통 모드", "정상 말투로 돌아가"):
            (claude_dir / ".cavemaenggu-active").write_text("maeng-gu")
            subprocess.run(
                ["node", "hooks/cavemaenggu-mode-tracker.js"],
                cwd=ROOT,
                env={**os.environ, "HOME": str(home)},
                text=True,
                input=json.dumps({"prompt": phrase}),
                capture_output=True,
                check=True,
            )
            ensure(
                not (claude_dir / ".cavemaenggu-active").exists(),
                f"Korean deactivation '{phrase}' should remove flag",
            )

        # CAVEMAENGGU_DEFAULT_MODE=off must veto Korean auto-activation as well.
        (claude_dir / ".cavemaenggu-active").unlink(missing_ok=True)
        subprocess.run(
            ["node", "hooks/cavemaenggu-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home), "CAVEMAENGGU_DEFAULT_MODE": "off"},
            text=True,
            input='{"prompt":"맹구야"}',
            capture_output=True,
            check=True,
        )
        ensure(
            not (claude_dir / ".cavemaenggu-active").exists(),
            "Korean 맹구 should not activate when CAVEMAENGGU_DEFAULT_MODE=off",
        )

        activate_mg = run(
            ["node", "hooks/cavemaenggu-activate.js"],
            env={"HOME": str(home), "CAVEMAENGGU_DEFAULT_MODE": "maeng-gu-full"},
        )
        ensure(
            "maeng-gu-full" in activate_mg.stdout,
            "activation banner missing maeng-gu-full label",
        )
        ensure(
            "**maeng-gu-full**" in activate_mg.stdout,
            "activation should retain maeng-gu-full intensity row",
        )
        ensure(
            "**maeng-gu-lite**" not in activate_mg.stdout,
            "activation should filter out non-active maeng-gu rows",
        )
        ensure(
            "wenyan" not in activate_mg.stdout.lower(),
            "activation should not mention removed wenyan mode",
        )
        ensure(
            (claude_dir / ".cavemaenggu-active").read_text() == "maeng-gu-full",
            "CAVEMAENGGU_DEFAULT_MODE=maeng-gu-full should set flag",
        )

        reinstall = run(["bash", "hooks/install.sh"], env={"HOME": str(home)})
        ensure("Nothing to do" in reinstall.stdout, "install.sh should be idempotent")

        run(["bash", "hooks/uninstall.sh"], env={"HOME": str(home)})
        settings_after = read_json(claude_dir / "settings.json")
        ensure(settings_after == existing_settings, "uninstall.sh did not restore non-cavemaenggu settings")
        ensure(not (claude_dir / ".cavemaenggu-active").exists(), "uninstall.sh should remove flag file")

    with tempfile.TemporaryDirectory(prefix="cavemaenggu-verify-fresh-") as temp_root:
        home = Path(temp_root) / "home"
        run(["bash", "hooks/install.sh"], env={"HOME": str(home)})
        claude_dir = home / ".claude"
        settings = read_json(claude_dir / "settings.json")
        ensure("statusLine" in settings, "fresh install should configure statusline")
        activate = run(["node", "hooks/cavemaenggu-activate.js"], env={"HOME": str(home)})
        ensure("STATUSLINE SETUP NEEDED" not in activate.stdout, "fresh install should not nudge for statusline")
        run(["bash", "hooks/uninstall.sh"], env={"HOME": str(home)})
        ensure(read_json(claude_dir / "settings.json") == {}, "fresh uninstall should leave empty settings")

    print("Claude hook install/uninstall flow OK")


def main() -> int:
    checks = [
        verify_synced_files,
        verify_manifests_and_syntax,
        verify_powershell_static,
        verify_compress_fixtures,
        verify_compress_cli,
        verify_hook_install_flow,
    ]

    try:
        for check in checks:
            check()
    except CheckFailure as exc:
        print(f"\nFAIL: {exc}", file=sys.stderr)
        return 1

    print("\nAll local verification checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
