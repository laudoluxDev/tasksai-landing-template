#!/usr/bin/env python3
"""Push only download.html to all 29 vertical repos."""

import base64, json, os, time, urllib.request, urllib.error

GITHUB_TOKEN = "REMOVED_TOKEN"
ORG = "laudoluxDev"
OUTPUT_DIR = "/Users/clio/dev/tasksai-landing-template/output"
COMMIT_MSG = "feat: multi-vertical account dashboard on download page"

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

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
    "User-Agent": "clio-deploy/1.0",
}

def gh_get_sha(repo, filename):
    url = f"https://api.github.com/repos/{ORG}/{repo}/contents/{filename}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()).get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise

def gh_put(repo, filename, filepath, sha):
    with open(filepath, "rb") as f:
        content = base64.b64encode(f.read()).decode("ascii")
    payload = {"message": COMMIT_MSG, "content": content}
    if sha:
        payload["sha"] = sha
    url = f"https://api.github.com/repos/{ORG}/{repo}/contents/{filename}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS, method="PUT")
    try:
        with urllib.request.urlopen(req) as r:
            return True, f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            msg = json.loads(body).get("message", body[:200])
        except:
            msg = body[:200]
        return False, f"HTTP {e.code}: {msg}"

ok = err = skip = 0
for vertical, repo in REPO_MAP.items():
    filepath = os.path.join(OUTPUT_DIR, vertical, "download.html")
    if not os.path.exists(filepath):
        print(f"  SKIP  {vertical:20s}  (no output file)")
        skip += 1
        continue
    sha = gh_get_sha(repo, "download.html")
    success, msg = gh_put(repo, "download.html", filepath, sha)
    status = "  OK  " if success else "  ERR "
    print(f"{status} {vertical:20s}  {repo}  {msg}")
    if success: ok += 1
    else: err += 1
    time.sleep(0.3)

print(f"\nDone: {ok} pushed, {err} errors, {skip} skipped")
