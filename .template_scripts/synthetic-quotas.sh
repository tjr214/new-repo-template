#!/usr/bin/env bash
set -euo pipefail

API_URL="https://api.synthetic.new/v2/quotas"

usage() {
  cat <<'EOF'
Usage: scripts/synthetic-quotas.sh

Requires:
  - SYNTHETIC_PLAN_API_KEY environment variable
  - curl and jq installed
EOF
}

fail() {
  printf "Error: %s\n" "$1" >&2
  exit 1
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command: $1"
}

format_time() {
  local iso="$1"
  local base="${iso%%.*}"
  local epoch formatted
  if epoch=$(date -u -j -f "%Y-%m-%dT%H:%M:%S" "$base" "+%s" 2>/dev/null) \
    && formatted=$(date -r "$epoch" "+%I:%M %p %m/%d/%Y (%Z)" 2>/dev/null); then
    printf "%s" "$formatted"
    return
  fi
  printf "%s" "$iso"
}

format_until() {
  local iso="$1"
  local base="${iso%%.*}"
  local epoch now delta hours mins
  if epoch=$(date -u -j -f "%Y-%m-%dT%H:%M:%S" "$base" "+%s" 2>/dev/null); then
    now=$(date +%s)
    delta=$((epoch - now))
    if (( delta < 0 )); then
      delta=0
    fi
    hours=$((delta / 3600))
    mins=$(((delta % 3600) / 60))
    printf "%dh %dm" "$hours" "$mins"
    return
  fi
  printf "%s" "unknown"
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

require_cmd curl
require_cmd jq

if [[ -z "${SYNTHETIC_PLAN_API_KEY:-}" ]]; then
  fail "SYNTHETIC_PLAN_API_KEY is not set"
fi

if ! response=$(curl -sS -f -H "Authorization: Bearer ${SYNTHETIC_PLAN_API_KEY}" "$API_URL"); then
  fail "Request failed. Check API key and network connectivity."
fi

if ! data=$(jq -e -r '[
  .subscription.limit,
  .subscription.requests,
  (.subscription.limit - .subscription.requests),
  .subscription.renewsAt,
  .search.hourly.limit,
  .search.hourly.requests,
  (.search.hourly.limit - .search.hourly.requests),
  .search.hourly.renewsAt
] | @tsv' <<<"$response"); then
  fail "Unexpected JSON format from API"
fi

IFS=$'\t' read -r sub_limit sub_requests sub_remaining sub_renews \
  search_limit search_requests search_remaining search_renews <<<"$data"

sub_renews_fmt=$(format_time "$sub_renews")
sub_renews_in=$(format_until "$sub_renews")
search_renews_fmt=$(format_time "$search_renews")
search_renews_in=$(format_until "$search_renews")

bold=$(printf '\033[1m')
cyan=$(printf '\033[36m')
section_cyan=$(printf '\033[38;5;159m')
green=$(printf '\033[32m')
yellow=$(printf '\033[33m')
bold_red=$(printf '\033[1;31m')
header_bg=$(printf '\033[48;5;52m')
section_bg=$(printf '\033[48;5;18m')
reset=$(printf '\033[0m')

remaining_color() {
  local used="$1"
  local limit="$2"
  local percent
  if [[ "$limit" =~ ^[0-9]+$ ]] && (( limit > 0 )); then
    percent=$(( used * 100 / limit ))
    if (( percent >= 80 )); then
      printf "%s" "$bold_red"
      return
    fi
    if (( percent > 50 )); then
      printf "%s" "$yellow"
      return
    fi
  fi
  printf "%s" "$green"
}

sub_remaining_color=$(remaining_color "$sub_requests" "$sub_limit")
search_remaining_color=$(remaining_color "$search_requests" "$search_limit")

rows=(
  "section| • Agentic Coding (5-Hour)"
  "row|Limit|$sub_limit|$green"
  "row|Used|$sub_requests|$yellow"
  "row|Remaining|$sub_remaining|$sub_remaining_color"
  "row|Renews at|$sub_renews_fmt|$cyan"
  "row|Renews in|$sub_renews_in|$cyan"
  "section| • Search (Hourly)"
  "row|Limit|$search_limit|$green"
  "row|Used|$search_requests|$yellow"
  "row|Remaining|$search_remaining|$search_remaining_color"
  "row|Renews at|$search_renews_fmt|$cyan"
  "row|Renews in|$search_renews_in|$cyan"
)

label_width=0
value_width=0
for entry in "${rows[@]}"; do
  IFS='|' read -r kind label value _color <<<"$entry"
  if [[ "$kind" == "row" ]]; then
    if (( ${#label} > label_width )); then
      label_width=${#label}
    fi
    if (( ${#value} > value_width )); then
      value_width=${#value}
    fi
  fi
done

inner_width=$((label_width + value_width + 5))
border_top="┌$(printf '%*s' "$inner_width" '' | tr ' ' '─')┐"
border_mid="├$(printf '%*s' "$inner_width" '' | tr ' ' '─')┤"
border_bottom="└$(printf '%*s' "$inner_width" '' | tr ' ' '─')┘"

printf "%s\n" "$border_top"
title_text="* Synthetic.New Request Limits *"
title_pad=$((inner_width - 2 - ${#title_text}))
title_pad_left=$((title_pad / 2))
title_pad_right=$((title_pad - title_pad_left))
printf "│ %s%s%s%*s%s%*s%s │\n" \
  "$bold" "$yellow" "$header_bg" "$title_pad_left" "" "$title_text" \
  "$title_pad_right" "" "$reset"
printf "%s\n" "$border_mid"

first_section=true
for entry in "${rows[@]}"; do
  IFS='|' read -r kind label value color <<<"$entry"
  if [[ "$kind" == "section" ]]; then
    if [[ "$first_section" == false ]]; then
      printf "%s\n" "$border_mid"
    fi
    first_section=false
    section_pad=$((inner_width - 2 - ${#label}))
    printf "│ %s%s%s%*s%s │\n" \
      "$section_cyan" "$section_bg" "$label" "$section_pad" "" "$reset"
    printf "%s\n" "$border_mid"
    continue
  fi
  label_pad=$((label_width - ${#label}))
  value_pad=$((value_width - ${#value}))
  printf "│ %s%*s │ %s%s%s%*s │\n" \
    "$label" "$label_pad" "" "$color" "$value" "$reset" "$value_pad" ""
done
printf "%s\n" "$border_bottom"
