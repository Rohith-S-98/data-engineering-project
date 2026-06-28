from __future__ import annotations

import sys
from pathlib import Path

STORYTELLING_DIR = Path("docs/storytelling")
REQUIRED_FILES = {
    "project_overview_2_minute.md": [
        "Two-Minute Project Overview",
        "Apexon",
        "IQVIA",
        "production-style",
    ],
    "deep_dive_walkthrough.md": [
        "Deep-Dive Project Walkthrough",
        "Bronze",
        "Silver",
        "Gold",
        "SCD Type 2",
        "Performance Thinking",
    ],
    "resume_bullets.md": [
        "Resume Bullet Bank",
        "PySpark",
        "Databricks",
        "CI/CD",
        "SCD Type 2",
    ],
    "apexon_iqvia_mapping.md": [
        "Apexon / IQVIA Mapping",
        "OneKey",
        "Veeva",
        "Reltio-style JSON",
        "quarantine",
    ],
    "mock_interview_questions.md": [
        "Mock Interview Questions",
        "Project Explanation",
        "PySpark",
        "Azure",
        "Behavioral",
    ],
}
FORBIDDEN_PHRASES = {
    "I am an expert in everything",
    "guaranteed job",
    "fake experience",
    "live public api integration is completed",
}


class StorytellingPackValidationError(ValueError):
    """Raised when V29 storytelling pack artifacts are invalid."""


def read_required_file(filename: str) -> str:
    path = STORYTELLING_DIR / filename
    if not path.exists():
        raise StorytellingPackValidationError(f"missing storytelling file: {path}")
    return path.read_text(encoding="utf-8")


def validate_storytelling_file(filename: str, required_terms: list[str]) -> list[str]:
    issues: list[str] = []
    content = read_required_file(filename)
    lowered = content.lower()

    if len(content.strip()) < 300:
        issues.append(f"{filename}: content is too short")

    for term in required_terms:
        if term.lower() not in lowered:
            issues.append(f"{filename}: missing required term '{term}'")

    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in lowered:
            issues.append(f"{filename}: contains forbidden phrase '{phrase}'")

    return issues


def validate_storytelling_pack() -> list[str]:
    issues: list[str] = []
    for filename, required_terms in REQUIRED_FILES.items():
        issues.extend(validate_storytelling_file(filename, required_terms))
    return issues


def assert_valid_storytelling_pack() -> None:
    issues = validate_storytelling_pack()
    if issues:
        raise StorytellingPackValidationError("; ".join(issues))


def main() -> int:
    issues = validate_storytelling_pack()
    if issues:
        print("Storytelling pack validation FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Storytelling pack validation SUCCESS")
    print(f"Validated storytelling files: {len(REQUIRED_FILES)}")
    print(f"Validated directory: {STORYTELLING_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
