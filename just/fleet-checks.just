# Vendored from fleet-base @ v0.6.0. Do not edit: the next install overwrites this file.
# Update: uv run python -m fleet_base.vendor_just install <this repo> (run in fleet-base's checkout)
# fleet-checks-sha256: 0451bf0db64269da85bf46cbbf3796426b33aa5436efe7f73e1a6e757dc8bf14
# fleet-checks-body

# Lint the whole repository with ruff. Read-only.
[group("dev")]
fleet-lint:
    uv run ruff check .

# Lint, then run the repository's type check when it has one (a check-types recipe). Read-only.
[group("dev")]
fleet-check: fleet-lint
    @if just --summary | tr ' ' '\n' | grep -qx check-types; then just check-types; else echo "fleet-check: no check-types recipe here; lint only"; fi

# Verify this copy is unedited: the hash in its header must match the body below the marker.
[group("dev")]
check-fleet-checks:
    #!/usr/bin/env bash
    set -euo pipefail
    want=$(sed -n 's/^# fleet-checks-sha256: //p' just/fleet-checks.just)
    got=$(sed -n '/^# fleet-checks-body$/,$p' just/fleet-checks.just | sha256sum | cut -d' ' -f1)
    if [ "$want" != "$got" ]; then
        echo "just/fleet-checks.just was edited by hand (header $want, body $got). Reinstall it from fleet-base." >&2
        exit 1
    fi
    echo "just/fleet-checks.just matches fleet-base"
