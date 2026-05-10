#!/usr/bin/env bash
# Reads .env and pushes each value as a GitHub Actions secret.
# Usage: bash scripts/sync_secrets.sh [--env .env]

set -euo pipefail

ENV_FILE=".env"
FILTER=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --env) ENV_FILE="$2"; shift 2 ;;
    --only) IFS=',' read -ra FILTER <<< "$2"; shift 2 ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: $ENV_FILE not found"
  exit 1
fi

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
if [[ -z "$REPO" ]]; then
  echo "Error: not in a GitHub repo or not authenticated (run: gh auth login)"
  exit 1
fi

echo "Syncing secrets to $REPO from $ENV_FILE..."

while IFS= read -r line; do
  # Skip comments and blank lines
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  [[ -z "${line// }" ]] && continue
  # Skip lines without =
  [[ "$line" != *"="* ]] && continue

  key="${line%%=*}"
  value="${line#*=}"

  # Skip if key is empty
  [[ -z "$key" ]] && continue

  # Skip if not in filter list (when filter is set)
  if [[ ${#FILTER[@]} -gt 0 ]]; then
    match=0
    for f in "${FILTER[@]}"; do
      [[ "$key" == "$f" ]] && match=1 && break
    done
    [[ $match -eq 0 ]] && continue
  fi

  gh secret set "$key" --body "$value" --repo "$REPO"
  echo "  ✓ $key"
done < "$ENV_FILE"

echo "Done."
