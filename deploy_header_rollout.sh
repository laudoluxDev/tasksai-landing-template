#!/usr/bin/env bash
# Header.js uniformity rollout — pushes 10 files per vertical to GitHub
# Usage: bash deploy_header_rollout.sh

set -euo pipefail

GITHUB_TOKEN="YOUR_GITHUB_TOKEN_HERE"
ORG="laudoluxDev"
OUTPUT_DIR="/Users/clio/dev/tasksai-landing-template/output"
COMMIT_MSG="feat: uniform header.js nav across all pages"

# Mapping: product_id → repo_name
declare -A REPO_MAP=(
  [contractor]="contractor-landing"
  [realtor]="realtor-landing"
  [accounting]="accounting-landing"
  [chiropractor]="chiropractor-landing"
  [church]="churchadmin-landing"
  [dentist]="dentist-landing"
  [designer]="designer-landing"
  [electrician]="electrician-landing"
  [eventplanner]="eventplanner-landing"
  [farmer]="farmer-landing"
  [funeral]="funeral-landing"
  [hr]="hr-landing"
  [insurance]="insurance-landing"
  [landlord]="landlord-landing"
  [militaryspouse]="militaryspouse-landing"
  [mortgage]="mortgage-landing"
  [mortuary]="mortician-landing"
  [nutritionist]="nutritionist-landing"
  [pastor]="pastor-landing"
  [personaltrainer]="personaltrainer-landing"
  [plumber]="plumber-landing"
  [principal]="principal-landing"
  [restaurant]="restaurant-landing"
  [salon]="salon-landing"
  [teacher]="teacher-landing"
  [therapist]="therapist-landing"
  [travelagent]="travelagent-landing"
  [vet]="vet-landing"
  [marketing]="marketingtasksai-landing"
)

FILES=(
  "header.js"
  "index.html"
  "task-library.html"
  "verified_safe.html"
  "getting-started.html"
  "signup.html"
  "success.html"
  "support.html"
  "privacy.html"
  "terms.html"
)

# Tracking
declare -A RESULTS  # product_id → "X/10 files succeeded"
TOTAL_SUCCESS=0
TOTAL_FAIL=0

push_file() {
  local repo="$1"
  local filename="$2"
  local filepath="$3"

  # Base64-encode the file
  local content
  content=$(base64 < "$filepath")

  # GET existing SHA
  local sha=""
  local get_response
  get_response=$(curl -s -o /tmp/gh_get_response.json -w "%{http_code}" \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${ORG}/${repo}/contents/${filename}")

  if [ "$get_response" = "200" ]; then
    sha=$(python3 -c "import json,sys; d=json.load(open('/tmp/gh_get_response.json')); print(d.get('sha',''))")
  fi

  # Build PUT payload
  local payload
  if [ -n "$sha" ]; then
    payload=$(python3 -c "
import json
print(json.dumps({
  'message': '${COMMIT_MSG}',
  'content': '''${content}''',
  'sha': '${sha}'
}))
")
  else
    payload=$(python3 -c "
import json
print(json.dumps({
  'message': '${COMMIT_MSG}',
  'content': '''${content}'''
}))
")
  fi

  # PUT
  local put_response
  put_response=$(curl -s -o /tmp/gh_put_response.json -w "%{http_code}" \
    -X PUT \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "https://api.github.com/repos/${ORG}/${repo}/contents/${filename}")

  if [ "$put_response" = "200" ] || [ "$put_response" = "201" ]; then
    echo "  ✅ ${filename} (HTTP ${put_response})"
    return 0
  else
    echo "  ❌ ${filename} (HTTP ${put_response})"
    cat /tmp/gh_put_response.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('     Error:', d.get('message','unknown'))" 2>/dev/null || true
    return 1
  fi
}

echo "==================================================="
echo " Header.js uniformity rollout — 29 verticals"
echo "==================================================="
echo ""

VERTICAL_NUM=0
for PRODUCT_ID in "${!REPO_MAP[@]}"; do
  VERTICAL_NUM=$((VERTICAL_NUM + 1))
  REPO="${REPO_MAP[$PRODUCT_ID]}"
  PRODUCT_DIR="${OUTPUT_DIR}/${PRODUCT_ID}"

  echo "[$VERTICAL_NUM/29] ${PRODUCT_ID} → ${ORG}/${REPO}"

  if [ ! -d "$PRODUCT_DIR" ]; then
    echo "  ⚠️  Directory not found: ${PRODUCT_DIR} — SKIPPING"
    RESULTS[$PRODUCT_ID]="SKIP (no dir)"
    continue
  fi

  success=0
  fail=0

  for FILENAME in "${FILES[@]}"; do
    FILEPATH="${PRODUCT_DIR}/${FILENAME}"
    if [ ! -f "$FILEPATH" ]; then
      echo "  ⚠️  File missing: ${FILEPATH}"
      fail=$((fail + 1))
      continue
    fi

    if push_file "$REPO" "$FILENAME" "$FILEPATH"; then
      success=$((success + 1))
    else
      fail=$((fail + 1))
    fi

    # Small delay to avoid rate limits
    sleep 0.3
  done

  RESULTS[$PRODUCT_ID]="${success}/10 succeeded, ${fail} failed"
  TOTAL_SUCCESS=$((TOTAL_SUCCESS + success))
  TOTAL_FAIL=$((TOTAL_FAIL + fail))

  echo "  → Result: ${success}/10 files pushed"
  echo ""

  # Pause between repos
  sleep 1
done

echo "==================================================="
echo " FINAL SUMMARY"
echo "==================================================="
for PRODUCT_ID in $(echo "${!RESULTS[@]}" | tr ' ' '\n' | sort); do
  printf "  %-20s %s\n" "${PRODUCT_ID}" "${RESULTS[$PRODUCT_ID]}"
done
echo ""
echo "Total: ${TOTAL_SUCCESS} files succeeded, ${TOTAL_FAIL} files failed"
echo "==================================================="
