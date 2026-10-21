# Vendored from fleet-base @ v0.6.0. Do not edit: the next install overwrites this file.
# Update: uv run python -m fleet_base.vendor_just install <this repo> (run in fleet-base's checkout)
# fleet-test-sha256: 27fb538f836516990c7beef5baabd22277724581bc89aeb3d18b71671d81182d
# fleet-test-body

# Run the unit tests in tests/unit. Arguments go to pytest, for example: just fleet-test -k parser
[group("test")]
fleet-test *ARGS:
    uv run pytest tests/unit -q {{ARGS}}

# Verify this copy is unedited: the hash in its header must match the body below the marker.
[group("test")]
check-fleet-test:
    #!/usr/bin/env bash
    set -euo pipefail
    want=$(sed -n 's/^# fleet-test-sha256: //p' just/fleet-test.just)
    got=$(sed -n '/^# fleet-test-body$/,$p' just/fleet-test.just | sha256sum | cut -d' ' -f1)
    if [ "$want" != "$got" ]; then
        echo "just/fleet-test.just was edited by hand (header $want, body $got). Reinstall it from fleet-base." >&2
        exit 1
    fi
    echo "just/fleet-test.just matches fleet-base"
