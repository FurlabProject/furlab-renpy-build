#!/bin/bash
set -e

ROOT="$(dirname "$(realpath "$0")")"
cd "$ROOT"

PLATFORM="ios"

if [[ "$1" == "--platform" ]]; then
    PLATFORM="$2"
    shift 2
fi

exec uv --project renpy run -m renpybuild --platform "$PLATFORM" "$@"