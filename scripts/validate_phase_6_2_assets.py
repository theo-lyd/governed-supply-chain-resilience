#!/usr/bin/env python3
"""Validate defense-ready Phase 6 assets for PR gating."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    ROOT / "docs/planning/thesis-defense-runbook.md",
    ROOT / "docs/planning/thesis-defense-narrative.md",
    ROOT / "docs/phase-reports/SCR-P6-B6.1-report.md",
    ROOT / "docs/phase-reports/SCR-P6-B6.2-report.md",
    ROOT / "docs/command/phase-6-commands.md",
    ROOT / "docs/planning/thesis-execution-roadmap.md",
    ROOT / ".github/workflows/ci-quality-gates.yml",
]

CONTENT_CHECKS = {
    ROOT / "docs/planning/thesis-execution-roadmap.md": [
        "✅ Completed/Verified (DuckDB controls + incident logging)",
        "✅ Completed/Verified (PR validation + defense package)",
        "docs/planning/thesis-defense-runbook.md",
        "docs/planning/thesis-defense-narrative.md",
    ],
    ROOT / "docs/command/phase-6-commands.md": [
        "Batch 6.2 PR validation and defense assets",
    ],
    ROOT / ".github/workflows/ci-quality-gates.yml": [
        "Validate Phase 6.2 defense assets",
    ],
    ROOT / "docs/planning/thesis-defense-runbook.md": [
        "Defense Runbook",
        "Primary Validation Commands",
        "Evidence Checklist",
    ],
    ROOT / "docs/planning/thesis-defense-narrative.md": [
        "Defense Narrative",
        "Storyline",
        "Closing Statement",
    ],
}


def main() -> None:
    errors: list[str] = []

    for path in REQUIRED_FILES:
        if not path.exists():
            errors.append(f"Missing required file: {path.relative_to(ROOT)}")

    for path, snippets in CONTENT_CHECKS.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"Missing snippet in {path.relative_to(ROOT)}: {snippet}")

    if errors:
        print("Phase 6.2 asset validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Phase 6.2 asset validation passed.")


if __name__ == "__main__":
    main()
