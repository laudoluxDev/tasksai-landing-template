#!/usr/bin/env python3
"""
Header.js uniformity rollout — pushes 10 files per vertical to GitHub.
"""

import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error

GITHUB_TOKEN = "YOUR_GITHUB_TOKEN_HERE"
ORG = "laudoluxDev"
OUTPUT_DIR = "/Users/clio/dev/tasksai-landing-template/output"
COMMIT_MSG = "feat: uniform header.js nav across all pages"

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

FILES = [
    "header.js",
    "index.html",
    "task-library.html",
    "verified_safe.html",
    "getting-started.html",
    "signup.html",
    "success.html",
    "support.html",
    "privacy.html",
    "terms.html",
]

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
    "User-Agent": "clio-deploy-script/1.0",
}


def gh_get(repo: str, filename: str) -> str | None:
    """GET the current SHA of a file, or None if it doesn't exist."""
    url = f"https://api.github.com/repos/{ORG}/{repo}/contents/{filename}"
    req = urllib.request.Request(url, headers=HEADERS, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def gh_put(repo: str, filename: str, filepath: str, sha: str | None) -> tuple[bool, str]:
    """PUT a file to GitHub. Returns (success, message)."""
    with open(filepath, "rb") as f:
        content = base64.b64encode(f.read()).decode("ascii")

    payload = {
        "message": COMMIT_MSG,
        "content": content,
    }
    if sha:
        payload["sha"] = sha

    url = f"https://api.github.com/repos/{ORG}/{repo}/contents/{filename}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=HEADERS, method="PUT")

    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            return True, f"HTTP {status}"
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            msg = json.loads(body).get("message", body[:200])
        except Exception:
            msg = body[:200]
        return False, f"HTTP {e.code}: {msg}"


def push_file(repo: str, filename: str, filepath: str) -> tuple[bool, str]:
    """Fetch SHA then push file."""
    try:
        sha = gh_get(repo, filename)
    except urllib.error.HTTPError as e:
        return False, f"GET failed HTTP {e.code}"
    except Exception as ex:
        return False, f"GET error: {ex}"

    try:
        ok, msg = gh_put(repo, filename, filepath, sha)
        return ok, msg
    except Exception as ex:
        return False, f"PUT error: {ex}"


def main():
    print("=" * 55)
    print(" Header.js uniformity rollout — 29 verticals")
    print("=" * 55)
    print()

    results = {}
    total_success = 0
    total_fail = 0

    verticals = sorted(REPO_MAP.keys())

    for idx, product_id in enumerate(verticals, 1):
        repo = REPO_MAP[product_id]
        product_dir = os.path.join(OUTPUT_DIR, product_id)

        print(f"[{idx:02d}/29] {product_id} → {ORG}/{repo}")

        if not os.path.isdir(product_dir):
            print(f"  ⚠️  Directory not found: {product_dir} — SKIPPING")
            results[product_id] = "SKIP (no dir)"
            print()
            continue

        success = 0
        fail = 0
        file_results = []

        for filename in FILES:
            filepath = os.path.join(product_dir, filename)
            if not os.path.isfile(filepath):
                print(f"  ⚠️  Missing: {filename}")
                file_results.append((filename, False, "file not found"))
                fail += 1
                continue

            ok, msg = push_file(repo, filename, filepath)
            icon = "✅" if ok else "❌"
            print(f"  {icon} {filename:<30} {msg}")
            file_results.append((filename, ok, msg))

            if ok:
                success += 1
            else:
                fail += 1

            # Respect rate limits: ~0.3s between files
            time.sleep(0.35)

        results[product_id] = (success, fail, file_results)
        total_success += success
        total_fail += fail

        print(f"  → {success}/10 files pushed successfully")
        print()

        # Pause between repos
        time.sleep(1.0)

    # Final summary
    print("=" * 55)
    print(" FINAL SUMMARY")
    print("=" * 55)
    for product_id in sorted(results.keys()):
        r = results[product_id]
        if isinstance(r, str):
            print(f"  {product_id:<20} {r}")
        else:
            s, f, _ = r
            status = "✅" if f == 0 else "⚠️ "
            print(f"  {status} {product_id:<20} {s}/10 ok, {f} failed")

    print()
    print(f"Grand total: {total_success} files pushed, {total_fail} failed")
    print("=" * 55)

    # Exit non-zero if any failures
    if total_fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
