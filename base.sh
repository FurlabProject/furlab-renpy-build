#!/bin/bash

set -e


ROOT=$(cd $(dirname $0); pwd)
REFS=$ROOT
BASE="$ROOT"

source $HOME/.local/bin/env
export PATH="$HOME/.local/bin:$PATH"

# Install the programs and virtualenvs.

VENV="$ROOT/renpy/.venv"

export RENPY_DEPS_INSTALL=/usr::/usr/lib/x86_64-linux-gnu/



. $BASE/nightly/git.sh
. $BASE/nightly/python.sh
