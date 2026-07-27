#!/usr/bin/env bash
# Generate Ana's profile-picture options through the CDP ChatGPT chain.
#
#   bash chars/_gen/ana_pfp/run.sh opt1_hoian_lanterns opt2_hanoi_tahien
#   bash chars/_gen/ana_pfp/run.sh all
#
# One option per gen, SEQUENTIAL — gen_base_ref.js closes the shared browser when it finishes, so two
# concurrent runs kill each other. Each option retries (a "Something went wrong" moderation soft-block
# is intermittent; a fresh chat usually clears it). Output -> character/Ana/Profile Pictures/.
set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 1
GEN="chars/_gen/ana_pfp"
OUT="character/Ana/Profile Pictures"
LOG="$GEN/gen.log"
TRIES="${TRIES:-2}"

opts=("$@")
if [ "${1:-}" = "all" ] || [ $# -eq 0 ]; then
  opts=($(ls -d "$GEN"/opt*/ | xargs -n1 basename | sort))
fi

mkdir -p "$OUT"
for slug in "${opts[@]}"; do
  d="$GEN/$slug"
  [ -d "$d" ] || { echo "!! no such option: $slug"; continue; }
  title="$(cat "$d/title.txt")"
  out="$OUT/PFP 1x1 - $title.png"
  echo "=== $slug -> $title ===" | tee -a "$LOG"

  attach=()
  for f in "$d"/to_upload/*; do attach+=(--attach "$f"); done

  ok=0
  for try in $(seq 1 "$TRIES"); do
    echo "--- try $try ---" | tee -a "$LOG"
    node engine/design/gen_base_ref.js "${attach[@]}" \
         --prompt-file "$d/prompt.txt" --out "$out" 2>&1 | tee -a "$LOG"
    rc=${PIPESTATUS[0]}
    echo "exit=$rc $slug try$try" | tee -a "$LOG"
    if [ "$rc" -eq 0 ] && [ -s "$out" ]; then ok=1; break; fi
    sleep 5
  done
  [ "$ok" -eq 1 ] || echo "!! FAILED $slug after $TRIES tries" | tee -a "$LOG"
done
echo "ALLDONE" | tee -a "$LOG"
