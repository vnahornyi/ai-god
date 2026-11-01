#!/usr/bin/env bash
# Collect the day's (or week's) commit evidence for worklog planning.
#
#   collect_commits.sh <since> [until]
#
#   collect_commits.sh 2026-07-22                # that single day
#   collect_commits.sh 2026-07-20 2026-07-26     # inclusive range
#
# Sweeps every local and remote branch, skips merges and git-notes commits,
# and filters to the author emails in .claude/worklog.json (falling back to
# the repo's configured user.email).
#
# Prints a per-commit block: date, hash, subject, tracker tag, change volume,
# and the meaningful changed paths. Paths matter more than commit messages —
# a commit filed under the wrong ticket still touches the right files.

set -euo pipefail

SINCE="${1:?usage: collect_commits.sh <since> [until]}"
UNTIL="${2:-$SINCE}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
CONFIG="$REPO_ROOT/.claude/worklog.json"

# Author emails: config first, then git config.
# (macOS ships bash 3.2, so no mapfile / readarray here.)
EMAILS=()
if [[ -f "$CONFIG" ]] && command -v python3 >/dev/null 2>&1; then
  while IFS= read -r line; do
    [[ -n "$line" ]] && EMAILS+=("$line")
  done < <(python3 -c '
import json,sys
try:
    cfg = json.load(open(sys.argv[1]))
    for e in cfg.get("author", {}).get("emails", []):
        print(e)
except Exception:
    pass
' "$CONFIG")
fi
if [[ ${#EMAILS[@]} -eq 0 ]]; then
  EMAILS=("$(git config user.email)")
fi

# Noise that inflates the diffstat without telling you anything about the work.
EXCLUDES=(
  ':(exclude)*.lock' ':(exclude)*package-lock.json' ':(exclude)*yarn.lock'
  ':(exclude)*Podfile.lock' ':(exclude)*.map' ':(exclude)*node_modules*'
  ':(exclude)*.png' ':(exclude)*.jpg' ':(exclude)*.jpeg' ':(exclude)*.webp'
  ':(exclude)*.svg' ':(exclude)*.ttf' ':(exclude)*.otf'
)

AUTHOR_ARGS=()
for e in "${EMAILS[@]}"; do AUTHOR_ARGS+=(--author="$e"); done

echo "=== WINDOW: $SINCE .. $UNTIL ==="
echo "=== AUTHORS: ${EMAILS[*]} ==="
echo

HASHES=$(git log --branches --remotes --no-merges "${AUTHOR_ARGS[@]}" \
  --since="$SINCE 00:00" --until="$UNTIL 23:59" \
  --pretty=format:'%H' | sort -u)

if [[ -z "$HASHES" ]]; then
  echo "NO COMMITS in window."
  echo
  echo "This is not automatically a problem — it means the day's evidence has to"
  echo "come from the developer. Ask what the day was spent on rather than"
  echo "borrowing work from an adjacent day."
  exit 0
fi

# Sort by commit date so the output reads chronologically.
for h in $HASHES; do
  printf '%s %s\n' "$(git show -s --format=%cI "$h")" "$h"
done | sort | while read -r _iso h; do

  DATE=$(git show -s --format=%cd --date=format:'%Y-%m-%d %a' "$h")
  SUBJ=$(git show -s --format=%s "$h")
  SHORT=$(git rev-parse --short=10 "$h")

  # Ticket key from the subject, e.g. ABC-12 / XYZ-345 / PROJ-2933.
  TICKET=$(printf '%s' "$SUBJ" | grep -oE '[A-Z][A-Z0-9]+-[0-9]+' | head -1 || true)
  # Tracker tag, e.g. "#time 1h 22m" or "#time 15m".
  TAG=$(printf '%s' "$SUBJ" | grep -oE '#time[[:space:]]+([0-9]+h[[:space:]]*)?([0-9]+m)?' | head -1 || true)

  echo "----------------------------------------------------------------"
  echo "DATE   : $DATE"
  echo "COMMIT : $SHORT"
  echo "TICKET : ${TICKET:-<none in message>}"
  echo "TRACKER: ${TAG:-<untagged>}"
  echo "SUBJECT: $SUBJ"

  STAT=$(git show --shortstat --format='' "$h" -- "${EXCLUDES[@]}" | tail -1 | sed 's/^ *//')
  echo "VOLUME : ${STAT:-<no meaningful changes>}"

  # Collect first, then truncate. Piping straight into `head` makes the
  # upstream git process take SIGPIPE, which under `pipefail` aborts the run
  # on any commit with more files than the limit.
  PATHS=$(git show --name-only --format='' "$h" -- "${EXCLUDES[@]}" | grep -v '^$' || true)
  TOTAL=$(printf '%s\n' "$PATHS" | grep -cv '^$' || true)

  echo "PATHS  :"
  printf '%s\n' "$PATHS" | sed -n '1,40p' | sed 's/^/         /'
  if [[ "$TOTAL" -gt 40 ]]; then
    echo "         ... and $((TOTAL - 40)) more"
  fi
  echo
done

echo "================================================================"
echo "PER-DAY TRACKER TOTALS (floor only — editor time, not real time)"
echo "================================================================"

for h in $HASHES; do
  printf '%s\t%s\n' "$(git show -s --format=%cd --date=short "$h")" \
                    "$(git show -s --format=%s "$h")"
done | python3 -c '
import sys, re, collections, datetime

WINDOW_FROM, WINDOW_TO = sys.argv[1], sys.argv[2]

per_day_ticket = collections.OrderedDict()
per_day = collections.defaultdict(lambda: [0, 0])

for line in sys.stdin:
    if not line.strip():
        continue
    date, _, subject = line.rstrip("\n").partition("\t")

    m = re.search(r"[A-Z][A-Z0-9]+-\d+", subject)
    ticket = m.group(0) if m else "<none in message>"

    t = re.search(r"#time\s+(?:(\d+)h)?\s*(?:(\d+)m)?", subject)
    mins = 0
    if t:
        mins = int(t.group(1) or 0) * 60 + int(t.group(2) or 0)

    key = (date, ticket)
    if key not in per_day_ticket:
        per_day_ticket[key] = [0, 0]
    per_day_ticket[key][0] += 1
    per_day_ticket[key][1] += mins
    per_day[date][0] += 1
    per_day[date][1] += mins

def hm(x):
    return "%dh %02dm" % (x // 60, x % 60)

last = None
for (date, ticket) in sorted(per_day_ticket):
    if last is not None and date != last:
        print()
    if date != last:
        n, mins = per_day[date]
        print("%s   TOTAL %d commits, %s tracked" % (date, n, hm(mins)))
        last = date
    n, mins = per_day_ticket[(date, ticket)]
    print("    %-22s %2d commits   %s" % (ticket, n, hm(mins)))

d0 = datetime.date.fromisoformat(WINDOW_FROM)
d1 = datetime.date.fromisoformat(WINDOW_TO)
gaps = []
d = d0
while d <= d1:
    iso = d.isoformat()
    if iso not in per_day:
        gaps.append("%s %s" % (iso, d.strftime("%a")))
    d += datetime.timedelta(days=1)

if gaps:
    print()
    print("DAYS IN WINDOW WITH NO COMMITS:")
    for g in gaps:
        print("    " + g)
    print()
    print("    Weekends here are expected. A working day here needs an answer")
    print("    from the developer — do not fill it from a neighbouring day.")
' "$SINCE" "$UNTIL"

echo
echo "Reminder: tracker totals count active editor time only. Design review,"
echo "on-device QA, build cycles and debugging are absent from these numbers."
echo "Use them for the split between tickets, not for the size of the day."
