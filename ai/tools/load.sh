#!/bin/bash
set -e

PRESET=$1

if [ -z "$PRESET" ]; then
  echo "Usage: load.sh <preset-file>"
  exit 1
fi

while read -r file; do
  echo ""
  echo "### SOURCE: $file"
  echo ""
  cat "$file"
  echo ""
done < "$PRESET"
