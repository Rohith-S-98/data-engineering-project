# Pull Request Checklist

Use this checklist before merging a version branch into `main`.

## Code and Config

- Python syntax validation passed.
- Config validation passed.
- Targeted tests passed.
- Full test suite passed.
- Dry-run orchestrator passed.
- Runtime-output cleanliness check passed.

## Documentation

- README version and version table are updated.
- Version documentation is added under `docs/`.
- Run commands are documented.
- Interview explanation is documented.

## Release Safety

- Runtime outputs are not committed.
- Working tree is clean before tagging.
- Release tag does not already exist.
- Version tag is created only after final verification.
