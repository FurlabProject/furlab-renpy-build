#!/usr/bin/env bash
set -e

ROOT="$(dirname "$(realpath "$0")")"
cd "$ROOT"

TMP_DIR="$ROOT/tmp"
EXPORT_DIR="$ROOT/renpy-ios-runtime"

CLEAN=0
ARGS=()

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --clean)
      CLEAN=1
      ;;
    *)
      ARGS+=("$arg")
      ;;
  esac
done

# Clean step
if [[ $CLEAN -eq 1 ]]; then
  echo "Cleaning build directories..."

  rm -rf "$TMP_DIR"
  rm -rf "$EXPORT_DIR"

  echo "Clean complete"
fi

# Default command if none provided
if [[ ${#ARGS[@]} -eq 0 ]]; then
  ARGS=(build)
fi

exec uv --project renpy run -m renpybuild "${ARGS[@]}"