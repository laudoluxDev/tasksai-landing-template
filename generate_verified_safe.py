#!/usr/bin/env python3
"""
Generate verified_safe.html for all TasksAI verticals.
Reads verticals.json + verified-safe-template.html, outputs to each landing repo.
"""
import json, os, re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
TEMPLATE_FILE = SCRIPT_DIR / "verified-safe-template.html"
VERTICALS_FILE = SCRIPT_DIR / "verticals.json"
REPOS_BASE = Path.home() / "dev"

# Header/footer pulled from lawtasksai-landing as reference pattern
# Each vertical repo has its own header inlined in index.html
# We'll generate a generic header per vertical

def make_header(v):
    name = v['name']
    domain = v['domain']
    slug = v['product_id']
    support_email = v.get('support_email', f"hello@{domain}")
    # Simple nav — just logo + home link for security page
    return f"""<header>
  <div class="container">
    <div class="header-inner">
      <a href="/index.html" class="logo">{name.replace('TasksAI', 'Tasks<span>AI</span>')}</a>
      <nav class="nav-links">
        <a href="/index.html">Home</a>
        <a href="/verified_safe.html" class="active">Verified Safe</a>
      </nav>
    </div>
  </div>
</header>"""

def make_footer(v):
    name = v['name']
    domain = v['domain']
    support_email = v.get('support_email', f"hello@{domain}")
    audience = v.get('audience', 'professionals')
    return f"""<footer class="site-footer-shared">
  <div class="container">
    <div class="footer-disclaimer">
      <span class="disclaimer-label">&#9888; Not Professional Advice</span>
      <span>{name} is software that assists {audience} with their work. It is not a licensed professional service and does not provide professional advice. Always apply your own professional review and judgment to any output. Laudo Lux, LLC.</span>
    </div>
    <div class="footer-inner">
      <div class="footer-brand">
        <a href="/index.html" class="logo">{name.replace('TasksAI', 'Tasks<span>AI</span>')}</a>
        <p>AI-powered workflows for {audience}.</p>
      </div>
      <div class="footer-links">
        <a href="/index.html">Home</a>
        <a href="/verified_safe.html">Verified Safe</a>
        <a href="mailto:{support_email}">{support_email}</a>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2026 Laudo Lux, LLC &nbsp;&middot;&nbsp; <a href="mailto:{support_email}">{support_email}</a></p>
    </div>
  </div>
</footer>"""

def generate(v, template):
    html = template
    html = html.replace('{{GA_TAG}}', v.get('ga_measurement_id', ''))
    html = html.replace('{{NAME}}', v['name'])
    html = html.replace('{{DOMAIN}}', v['domain'])
    html = html.replace('{{PRODUCT_ID}}', v['product_id'])
    html = html.replace('{{SUPPORT_EMAIL}}', v.get('support_email', f"hello@{v['domain']}"))
    html = html.replace('{{HEADER}}', make_header(v))
    html = html.replace('{{FOOTER}}', make_footer(v))
    return html

def main():
    template = TEMPLATE_FILE.read_text()
    verticals = json.loads(VERTICALS_FILE.read_text())

    generated = []
    skipped = []

    for v in verticals:
        slug = v['product_id']
        repo_dir = REPOS_BASE / f"{slug}tasksai-landing"

        if not repo_dir.exists():
            skipped.append(slug)
            continue

        html = generate(v, template)
        out_file = repo_dir / "verified_safe.html"
        out_file.write_text(html)
        generated.append(f"  ✅ {slug} → {out_file}")

    print(f"Generated {len(generated)} pages:")
    for g in generated:
        print(g)

    if skipped:
        print(f"\nSkipped (no local repo): {', '.join(skipped)}")

if __name__ == '__main__':
    main()
