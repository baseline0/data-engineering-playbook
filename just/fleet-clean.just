# Vendored from fleet-base @ v0.7.0. Do not edit: the next install overwrites this file.
# Update: uv run python -m fleet_base.vendor_just install <this repo> (run in fleet-base's checkout)
# fleet-clean-sha256: a2dd5c316a6853d5bac649aea613dadc5bd4e259cfbbe76ec145de8be217907b
# fleet-clean-body
# Remove tool caches at every depth of the repo. Never touches .venv, .git, .fleet (job state), or any non-cache file.
# Usage: just clean-cache true   (lists only; nothing removed)
#        just clean-cache false  (removes)
# The argument is positional: `dry_run=true` is passed through literally, so it is refused.
[group("dev")]
clean-cache mode="false":
    #!/usr/bin/env bash
    set -euo pipefail
    names=(-name __pycache__ -o -name .pytest_cache -o -name .ruff_cache -o -name .mypy_cache -o -name .pytype)
    find_caches=(find . \( -path ./.venv -o -path ./.git -o -path ./.fleet \) -prune -o \( "${names[@]}" \) -type d -prune -print)
    case "{{mode}}" in
        true)
            "${find_caches[@]}"
            echo "dry run: nothing removed" ;;
        false)
            "${find_caches[@]}" -exec rm -rf {} + ;;
        *)
            echo "clean-cache: mode must be true (list only) or false (remove); got '{{mode}}'" >&2
            exit 2 ;;
    esac

# Clean cache directories. A repository whose clean removes more than caches names that work apart from this recipe.
[group("dev")]
clean: clean-cache

# Verify this copy is unedited: the hash in its header must match the body below the marker.
[group("dev")]
check-fleet-clean:
    #!/usr/bin/env bash
    set -euo pipefail
    want=$(sed -n 's/^# fleet-clean-sha256: //p' just/fleet-clean.just)
    got=$(sed -n '/^# fleet-clean-body$/,$p' just/fleet-clean.just | sha256sum | cut -d' ' -f1)
    if [ "$want" != "$got" ]; then
        echo "just/fleet-clean.just was edited by hand (header $want, body $got). Reinstall it from fleet-base." >&2
        exit 1
    fi
    echo "just/fleet-clean.just matches fleet-base"
