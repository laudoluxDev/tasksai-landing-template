#!/usr/bin/env python3
"""
Deploy specific files directly to Cloudflare Pages for all 29 verticals.
Uses wrangler pages deploy with a temp directory containing only the changed files.
"""

import os, sys, time, subprocess, shutil, tempfile
from pathlib import Path

# Load .env — check script dir first, then vault backup location
_env_candidates = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
    os.path.expanduser("~/clio_obsidian_vault/Workspace_Admin/.env"),
]
for _env in _env_candidates:
    if os.path.exists(_env):
        for _l in open(_env):
            _l = _l.strip()
            if _l and not _l.startswith("#") and "=" in _l:
                _k, _v = _l.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())
        break

CF_EMAIL   = "kentmercier@gmail.com"
CF_API_KEY = "3994dcbe5afdd67ca6c8c4f8e9139fc71aead"  # global key — has Pages permissions
OUTPUT_DIR = "/Users/clio/dev/tasksai-landing-template/output"

REPO_MAP = {
    "contractor":     "contractor-landing",
    "realtor":        "realtor-landing",
    "accounting":     "accounting-landing",
    "chiropractor":   "chiropractor-landing",
    "church":         "churchadmin-landing",
    "dentist":        "dentist-landing",
    "designer":       "designer-landing",
    "electrician":    "electrician-landing",
    "eventplanner":   "eventplanner-landing",
    "farmer":         "farmer-landing",
    "funeral":        "funeral-landing",
    "hr":             "hr-landing",
    "insurance":      "insurance-landing",
    "landlord":       "landlord-landing",
    "militaryspouse": "militaryspouse-landing",
    "mortgage":       "mortgage-landing",
    "mortuary":       "mortician-landing",
    "nutritionist":   "nutritionist-landing",
    "pastor":         "pastor-landing",
    "personaltrainer":"personaltrainer-landing",
    "plumber":        "plumber-landing",
    "principal":      "principal-landing",
    "restaurant":     "restaurant-landing",
    "salon":          "salon-landing",
    "teacher":        "teacher-landing",
    "therapist":      "therapist-landing",
    "travelagent":    "travelagent-landing",
    "vet":            "vet-landing",
    "marketing":      "marketingtasksai-landing",
}

# Which files to deploy — pass as args, default to download.html
FILES_TO_DEPLOY = sys.argv[1:] if len(sys.argv) > 1 else ["download.html"]

env = {
    **os.environ,
    "CLOUDFLARE_API_TOKEN": "",  # clear token — use global key instead
    "CLOUDFLARE_EMAIL": CF_EMAIL,
    "CLOUDFLARE_API_KEY": CF_API_KEY,
}

ok = err = skip = 0
print(f"Deploying {FILES_TO_DEPLOY} to {len(REPO_MAP)} CF Pages projects via wrangler...\n")

for vertical, project in REPO_MAP.items():
    # Build a temp dir with all current files for this vertical PLUS the updated ones
    # We need ALL files because wrangler replaces the full deployment
    vertical_dir = os.path.join(OUTPUT_DIR, vertical)
    if not os.path.isdir(vertical_dir):
        print(f"  SKIP  {vertical:20s}  no output dir")
        skip += 1
        continue

    # Verify target files exist
    missing = [f for f in FILES_TO_DEPLOY if not os.path.exists(os.path.join(vertical_dir, f))]
    if missing:
        print(f"  SKIP  {vertical:20s}  missing: {missing}")
        skip += 1
        continue

    # Deploy the full vertical directory (wrangler handles incremental hashing)
    result = subprocess.run(
        ["npx", "wrangler", "pages", "deploy", vertical_dir,
         "--project-name", project,
         "--branch", "main",
         "--commit-message", f"deploy: {', '.join(FILES_TO_DEPLOY)}"],
        capture_output=True, text=True, env=env, timeout=60
    )

    if result.returncode == 0:
        # Extract deployment URL from output
        url_line = next((l for l in result.stdout.splitlines() if "pages.dev" in l or "Deployment complete" in l), "")
        print(f"  OK   {vertical:20s}  {project}  {url_line.strip()[:60]}")
        ok += 1
    else:
        err_msg = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else result.stdout.strip().splitlines()[-1]
        print(f"  ERR  {vertical:20s}  {project}  {err_msg[:80]}")
        err += 1

    time.sleep(0.3)

print(f"\nDone: {ok} deployed, {err} errors, {skip} skipped")
