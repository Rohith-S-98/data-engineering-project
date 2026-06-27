from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_FILES = [
    "Dockerfile",
    ".dockerignore",
    "docker-compose.yml",
]

REQUIRED_DOCKERFILE_SNIPPETS = [
    "FROM python:3.11-slim",
    "openjdk-17-jre-headless",
    "COPY requirements.txt requirements.txt",
    "pip install --no-cache-dir -r requirements.txt",
    "scripts.pipeline_orchestrator",
]

REQUIRED_DOCKERIGNORE_SNIPPETS = [
    ".venv",
    "__pycache__",
    "data/bronze",
    "output/observability",
    "data/raw/customer_data.csv",
]

REQUIRED_COMPOSE_SNIPPETS = [
    "data-engineering-pipeline:",
    "release-verification:",
    "data-engineering-project:v19",
    "scripts.pipeline_orchestrator",
    "scripts.release_verification",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_docker_artifacts(root: Path | str = Path(".")) -> list[str]:
    root_path = Path(root)
    issues: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root_path / relative_path).exists():
            issues.append(f"missing file: {relative_path}")

    dockerfile_path = root_path / "Dockerfile"
    dockerignore_path = root_path / ".dockerignore"
    compose_path = root_path / "docker-compose.yml"

    if dockerfile_path.exists():
        dockerfile_text = _read(dockerfile_path)
        for snippet in REQUIRED_DOCKERFILE_SNIPPETS:
            if snippet not in dockerfile_text:
                issues.append(f"Dockerfile missing required snippet: {snippet}")

    if dockerignore_path.exists():
        dockerignore_text = _read(dockerignore_path)
        for snippet in REQUIRED_DOCKERIGNORE_SNIPPETS:
            if snippet not in dockerignore_text:
                issues.append(f".dockerignore missing required snippet: {snippet}")

    if compose_path.exists():
        compose_text = _read(compose_path)
        for snippet in REQUIRED_COMPOSE_SNIPPETS:
            if snippet not in compose_text:
                issues.append(f"docker-compose.yml missing required snippet: {snippet}")

    return issues


def main() -> int:
    issues = validate_docker_artifacts()
    if issues:
        print("Docker artifact validation FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Docker artifact validation SUCCESS")
    print(f"Validated files: {len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
