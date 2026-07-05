#!/usr/bin/env python3
"""
Manual Cloudflare Pages deploy helper for generated TasksAI vertical sites.

The normal deploy path is the GitHub Actions workflow in this repository. Use
this helper only when a direct Pages deploy is needed from the generated output
in this checkout.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOCAL_HOME = ROOT / ".wrangler" / "home"

PAGES_PROJECTS = {
    "contractor": "contractor-landing",
    "realtor": "realtor-landing",
    "accounting": "accounting-landing",
    "chiropractor": "chiropractor-landing",
    "church": "churchadmin-landing",
    "dentist": "dentist-landing",
    "designer": "designer-landing",
    "electrician": "electrician-landing",
    "eventplanner": "eventplanner-landing",
    "farmer": "farmer-landing",
    "funeral": "funeral-landing",
    "hr": "hr-landing",
    "insurance": "insurance-landing",
    "landlord": "landlord-landing",
    "militaryspouse": "militaryspouse-landing",
    "mortgage": "mortgage-landing",
    "mortuary": "mortician-landing",
    "nutritionist": "nutritionist-landing",
    "pastor": "pastor-landing",
    "personaltrainer": "personaltrainer-landing",
    "plumber": "plumber-landing",
    "principal": "principal-landing",
    "restaurant": "restaurant-landing",
    "salon": "salon-landing",
    "teacher": "teacher-landing",
    "therapist": "therapist-landing",
    "travelagent": "travelagent-landing",
    "vet": "vet-landing",
    "marketing": "marketingtasksai-landing",
}


def load_env_files() -> None:
    """Load optional local environment files without baking secrets into code."""
    candidates = [
        ROOT / ".env",
        Path.home() / "clio_obsidian_vault" / "Workspace_Admin" / ".env",
    ]
    for env_path in candidates:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy generated vertical output to Cloudflare Pages."
    )
    parser.add_argument(
        "--vertical",
        action="append",
        choices=sorted(PAGES_PROJECTS),
        help="Deploy one vertical. Repeat for more than one. Defaults to all verticals.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Optional file names to require before deploying. The full vertical output directory is always deployed.",
    )
    return parser.parse_args()


def build_env() -> dict[str, str]:
    env = dict(os.environ)
    has_token = bool(env.get("CLOUDFLARE_API_TOKEN"))
    has_key_pair = bool(env.get("CLOUDFLARE_EMAIL") and env.get("CLOUDFLARE_API_KEY"))
    if not has_token and not has_key_pair:
        raise SystemExit(
            "Missing Cloudflare credentials. Set CLOUDFLARE_API_TOKEN, or set "
            "CLOUDFLARE_EMAIL and CLOUDFLARE_API_KEY in your shell or local .env."
        )

    LOCAL_HOME.mkdir(parents=True, exist_ok=True)
    (LOCAL_HOME / "Library" / "Preferences").mkdir(parents=True, exist_ok=True)
    env.setdefault("HOME", str(LOCAL_HOME))
    env.setdefault("WRANGLER_SEND_METRICS", "false")
    return env


def main() -> int:
    args = parse_args()
    load_env_files()
    env = build_env()

    if not shutil.which("npx"):
        raise SystemExit("Missing npx. Install Node.js/npm before running this helper.")
    if not OUTPUT_DIR.is_dir():
        raise SystemExit(f"Missing generated output directory: {OUTPUT_DIR}")

    slugs = args.vertical or sorted(PAGES_PROJECTS)
    required_files = args.files
    ok = err = skip = 0

    print(f"Deploying {len(slugs)} generated vertical site(s) from {OUTPUT_DIR}\n")

    for slug in slugs:
        project = PAGES_PROJECTS[slug]
        vertical_dir = OUTPUT_DIR / slug
        if not vertical_dir.is_dir():
            print(f"  SKIP  {slug:20s}  no output dir")
            skip += 1
            continue

        missing = [name for name in required_files if not (vertical_dir / name).exists()]
        if missing:
            print(f"  SKIP  {slug:20s}  missing: {missing}")
            skip += 1
            continue

        result = subprocess.run(
            [
                "npx",
                "wrangler",
                "pages",
                "deploy",
                str(vertical_dir),
                "--project-name",
                project,
                "--branch",
                "main",
                "--commit-dirty=true",
                "--commit-message",
                f"deploy generated {slug} site",
            ],
            capture_output=True,
            text=True,
            env=env,
            timeout=90,
        )

        if result.returncode == 0:
            url_line = next(
                (
                    line
                    for line in result.stdout.splitlines()
                    if "pages.dev" in line or "Deployment complete" in line
                ),
                "",
            )
            print(f"  OK    {slug:20s}  {project}  {url_line.strip()[:80]}")
            ok += 1
        else:
            output = result.stderr.strip() or result.stdout.strip()
            err_msg = output.splitlines()[-1] if output else "wrangler failed"
            print(f"  ERR   {slug:20s}  {project}  {err_msg[:100]}")
            err += 1

        time.sleep(0.3)

    print(f"\nDone: {ok} deployed, {err} errors, {skip} skipped")
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
