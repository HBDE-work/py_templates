#!/usr/bin/env bash

set -euo pipefail

CLI="python3 cli.py"

# ---- help ----------------------------------------------------
$CLI -h
$CLI text -h
$CLI error -h
$CLI text count -h
$CLI text reverse -h
$CLI text shout -h
$CLI text space -h
$CLI text upper -h
$CLI error notfound -h

# ---- version -------------------------------------------------
$CLI version

# ---- text group ----------------------------------------------
$CLI text count "hello"
$CLI text count "one two three"

$CLI text reverse "hello"
$CLI text reverse "hello world"

$CLI text shout "hello"
$CLI text shout "World"

$CLI text space "hello"

$CLI text upper "hello world"

# ---- global arg --verbose / -v -------------------------------
$CLI text upper "hello" --verbose
$CLI text upper "hello" -v
$CLI --verbose text upper "hello"

# commands without verbose param ignore the flag silently
$CLI text count "hello world" --verbose
$CLI text reverse "hello" --verbose

# ---- error group (expected non-zero exit) ---------------------
$CLI error notfound "[Demo] something missing" && exit 1 || true

echo "all done"
