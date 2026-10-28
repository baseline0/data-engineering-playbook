# Vendored from fleet-base @ v0.7.0. Do not edit: the next install overwrites this file.
# Update: uv run python -m fleet_base.vendor_just install <this repo> (run in fleet-base's checkout)
# fleet-commit-sha256: d29f3a8fd3b2f6a6fa6c72f3d4cea54f8e64680decc4db3c1a4081c7a6e3b38d
# fleet-commit-body

# COMMIT_MODEL: model used by commitmate (fast by default; mistral:7b for more detailed).
# Not exported: it is passed to commitmate with --model, so it must not leak into other recipes.
COMMIT_MODEL := env("COMMIT_MODEL", "qwen2.5-coder:1.5b")

# Generate and commit staged changes with LLM or custom message
# Uses commitmate with COMMIT_MODEL (default: qwen2.5-coder:1.5b, ~1.5B params, fast)
# Falls back to manual commit if Ollama unavailable or commitmate fails
commit:
    #!/bin/bash
    set -e

    STAGED=$(git diff --cached --name-only | wc -l)
    if [ "$STAGED" -eq 0 ]; then
        echo "[!] No staged changes. Stage files first: git add <files>"
        exit 1
    fi

    # Why: FILES names the exact set of files this commit is for. The index must match it, so work another session
    # staged cannot ride along. Nothing is unstaged for you; the mismatch is reported and the commit refused.
    if [ -n "${FILES:-}" ]; then
        named=$(printf '%s\n' $FILES | sort -u)
        staged=$(git diff --cached --name-only | sort -u)
        extra=$(comm -13 <(echo "$named") <(echo "$staged") | sed '/^$/d')
        missing=$(comm -23 <(echo "$named") <(echo "$staged") | sed '/^$/d')
        if [ -n "$extra" ] || [ -n "$missing" ]; then
            if [ -n "$extra" ]; then
                echo "[!] Staged but not named in FILES (unstage with git restore --staged, or add to FILES):"
                echo "$extra" | sed 's/^/    /'
            fi
            if [ -n "$missing" ]; then
                echo "[!] Named in FILES but not staged (git add them):"
                echo "$missing" | sed 's/^/    /'
            fi
            exit 1
        fi
    fi

    # Fleet rule R6 (fleet_base.hook_standard): every repo is a uv project, so uv run and tool pins work.
    if [ ! -f pyproject.toml ]; then
        echo "[!] This repo has no pyproject.toml; every fleet repo needs one."
        echo "[*] Create it: uv init --bare --python 3.13 --vcs none --name $(basename "$(git rev-parse --show-toplevel)")"
        exit 1
    fi

    # Hook standard R5 (fleet_base.hook_standard): a repo with a hook config must have its hooks installed,
    # or this commit would skip every check. A missing push hook is only warned about, so work is not blocked.
    if [ -f .pre-commit-config.yaml ]; then
        if [ ! -f "$(git rev-parse --git-path hooks/pre-commit)" ]; then
            echo "[!] pre-commit hooks are not installed in this clone, so this commit would skip every check."
            echo "[*] Install them: ~/projects/fleet-ops/.venv/bin/pre-commit install   (or pre-commit install, if it is on PATH)"
            exit 1
        fi
        if [ ! -f "$(git rev-parse --git-path hooks/pre-push)" ]; then
            echo "[!] The pre-push hook is not installed, so pushes from this clone skip the test gate. Same command installs it."
        fi
    fi

    # Hold the repo's fleet lock until this recipe exits. fleet-ops' fleet-push takes the same lock around each
    # rebase-and-push, so a commit never lands mid-rebase and a push never rebases under a commit's hooks.
    # The lock is in the git common dir, so every worktree of this repo shares it.
    LOCK="$(git rev-parse --git-common-dir)/fleet.lock"
    exec 9>>"$LOCK"
    if ! flock -w "${FLEET_LOCK_WAIT:-300}" 9; then
        echo "[!] $LOCK is held by another process (most likely a fleet push). Waited ${FLEET_LOCK_WAIT:-300}s."
        echo "[*] Try again when it finishes, or raise FLEET_LOCK_WAIT."
        exit 1
    fi

    # If MESSAGE is set, use it directly
    if [ -n "$MESSAGE" ]; then
        # Why: a pre-commit hook that rewrites a staged file (ruff format, a whitespace fixer) aborts the commit. Re-stage
        # exactly the paths that were staged before, and retry once. Nothing else is added, so unrelated work stays out.
        staged_before=$(git diff --cached --name-only)
        if git commit -m "$MESSAGE"; then
            exit 0
        fi
        if [ -z "$staged_before" ]; then
            exit 1
        fi
        echo "[*] A hook changed staged files. Re-staging the same files and retrying once."
        # Why: a staged deletion has no file on disk, and once staged it is gone from the index too, so `git add` and
        # `git add -A` both fail with "pathspec did not match". Re-stage a removal with `git rm --cached` (a no-op when
        # the index already lacks the path); re-stage everything else with `git add`.
        printf '%s\n' "$staged_before" | while IFS= read -r path; do
            if [ -e "$path" ]; then
                git add -- "$path"
            else
                git rm -q --cached --ignore-unmatch -- "$path"
            fi
        done
        git commit -m "$MESSAGE"
        exit 0
    fi

    # Check Ollama availability
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "[!] Ollama not running. Start: ollama serve"
        echo "[*] Or use custom message: MESSAGE=\"fix: description\" just commit"
        exit 1
    fi

    # Why: commitmate asks accept/edit/cancel on stdin. Without a terminal that prompt reads EOF and the commit fails
    # half-way, so a non-interactive caller has to pass MESSAGE.
    if [ ! -t 0 ]; then
        echo "[!] No terminal for commitmate's prompt. Use MESSAGE=\"type: description\" just commit"
        exit 1
    fi

    # Try commitmate with model (only for small diffs to avoid timeouts)
    if [ "$STAGED" -lt 10 ]; then
        # Run with timeout (30s should be plenty for 1.5B model)
        if timeout 30s commitmate --model "{{COMMIT_MODEL}}"; then
            exit 0
        else
            EXIT_CODE=$?
            if [ $EXIT_CODE -eq 124 ]; then
                echo "[!] Commitmate timeout (30s). Model may be slow or overloaded."
                echo "[*] Options:"
                echo "    1. Wait for Ollama to free up and retry"
                echo "    2. Use faster model: COMMIT_MODEL=qwen2.5-coder:1.5b just commit"
                echo "    3. Use custom message: MESSAGE=\"fix: description\" just commit"
                exit 1
            fi
        fi
    else
        echo "[*] Diff is large ($STAGED files). Skipping LLM generation."
        echo "[!] Use custom message: MESSAGE=\"type: description\" just commit"
        exit 1
    fi

    # Catch-all: commitmate failed for unknown reason
    echo "[!] Commitmate failed. Checking diagnostics..."
    echo "[*] Available models at http://localhost:11434/api/tags"
    echo "[*] Use custom message: MESSAGE=\"type: description\" just commit"
    exit 1

# Verify this copy is unedited: the hash in its header must match the body below the marker.
check-fleet-commit:
    #!/usr/bin/env bash
    set -euo pipefail
    want=$(sed -n 's/^# fleet-commit-sha256: //p' just/fleet-commit.just)
    got=$(sed -n '/^# fleet-commit-body$/,$p' just/fleet-commit.just | sha256sum | cut -d' ' -f1)
    if [ "$want" != "$got" ]; then
        echo "just/fleet-commit.just was edited by hand (header $want, body $got). Reinstall it from fleet-base." >&2
        exit 1
    fi
    echo "just/fleet-commit.just matches fleet-base"
