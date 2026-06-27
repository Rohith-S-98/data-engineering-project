# V19.0.0 - Docker Containerized Local Runtime

V19 adds a containerized local runtime for the data engineering pipeline.

## Goal

The goal is to make the project reproducible outside the developer's local virtual environment by packaging Python, Java, PySpark, Delta Lake dependencies, and pipeline commands into Docker artifacts.

## V19 Additions

- Dockerfile for Python 3.11 + Java 17 runtime
- `.dockerignore` to exclude virtual environments, Spark artifacts, and runtime outputs from Docker builds
- `docker-compose.yml` for repeatable dry-run and release-verification commands
- Docker artifact validation script
- V19 unit tests for Docker artifact checks
- Release verification updated to include Docker artifact validation and V19 docker tests

## Docker Commands

Build the image:

```bash
docker compose build
```

Run dry-run orchestration in Docker:

```bash
docker compose run --rm data-engineering-pipeline
```

Run release verification in Docker without real data writes:

```bash
docker compose run --rm release-verification
```

## Local Validation Commands

These commands validate V19 without requiring Docker daemon execution:

```bash
python -m scripts.validate_docker_artifacts
python -m unittest tests.test_v19_docker_artifacts
python -m scripts.release_verification --version v19.0.0 --skip-real-run --skip-alerting
```

## Production Explanation

In production data engineering, containerization makes local, CI, and deployment environments more consistent. It reduces setup drift by packaging runtime dependencies and standard commands into repeatable infrastructure artifacts.

## Interview Explanation

I containerized my PySpark medallion pipeline by adding a Dockerfile, Docker Compose service definitions, Docker ignore rules, static Docker validation checks, and CI-friendly tests. This made the project easier to run consistently across machines and closer to production deployment practices.
