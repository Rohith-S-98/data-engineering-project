from __future__ import annotations

import sys

from scripts.live_public_api_integration import DEFAULT_REGISTRY_PATH, PublicApiRegistryError, load_registry


def main() -> int:
    try:
        registry = load_registry(DEFAULT_REGISTRY_PATH)
    except PublicApiRegistryError as exc:
        print("Public API registry validation FAILED")
        print(f"- {exc}")
        return 1

    sources = registry["sources"]
    live_enabled_count = sum(1 for source in sources if source.get("live_enabled") is True)
    print("Public API registry validation SUCCESS")
    print(f"Validated sources: {len(sources)}")
    print(f"Live-enabled sources: {live_enabled_count}")
    print(f"CI safe mode: {registry['ci_safe_mode']}")
    print(f"Validated registry: {DEFAULT_REGISTRY_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
