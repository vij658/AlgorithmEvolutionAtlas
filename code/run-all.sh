#!/usr/bin/env bash
# Run every Java program under code/ and compare its output with expected-output.txt in the same folder.
# Usage: bash code/run-all.sh [filter]     (filter: only folders whose path contains this text)
# Needs JDK 17 or newer on the PATH. Exit status is non-zero if any program fails or its output differs.
set -u
cd "$(dirname "$0")"
filter="${1:-}"
pass=0; fail=0
while IFS= read -r f; do
  dir=$(dirname "$f"); name=$(basename "$f" .java)
  case "$dir" in *tools*) continue ;; esac
  if [ -n "$filter" ] && [[ "$dir" != *"$filter"* ]]; then continue; fi
  actual=$(cd "$dir" && java "$name.java" 2>&1); status=$?
  if [ $status -eq 0 ] && [ "$actual" == "$(cat "$dir/expected-output.txt")" ]; then
    pass=$((pass + 1)); echo "PASS  $dir  ($(echo "$actual" | tail -n 1))"
  else
    fail=$((fail + 1)); echo "FAIL  $dir  (exit status $status)"
    diff <(echo "$actual") "$dir/expected-output.txt" | head -n 20
  fi
done < <(find . -name '*.java' | sort)
echo "$pass passed, $fail failed"
[ $fail -eq 0 ]
