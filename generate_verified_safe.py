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
    logo_html = name.replace('TasksAI', 'Tasks<span>AI</span>')
    return f"""<footer style="background:#0f172a;color:#94a3b8;padding:48px 24px 32px;margin-top:60px;">
  <div style="max-width:900px;margin:0 auto;">
    <p style="font-size:0.82rem;color:#64748b;border:1px solid #1e293b;border-radius:8px;padding:12px 16px;margin-bottom:32px;">
      &#9888; <strong style="color:#94a3b8;">Not Professional Advice</strong> &mdash;
      {name} is software that assists {audience} with administrative work. It is not a licensed professional service and does not provide professional advice. Always apply your own professional review and judgment. Laudo Lux, LLC.
    </p>
    <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:24px;margin-bottom:32px;">
      <div>
        <a href="/index.html" style="font-size:1.1rem;font-weight:800;color:#fff;text-decoration:none;letter-spacing:-0.02em;">{logo_html}</a>
        <p style="margin-top:8px;font-size:0.88rem;">AI-powered workflows for {audience}.</p>
      </div>
      <div style="display:flex;flex-direction:column;gap:10px;">
        <a href="/index.html" style="color:#94a3b8;text-decoration:none;font-size:0.9rem;">Home</a>
        <a href="/verified_safe.html" style="color:#94a3b8;text-decoration:none;font-size:0.9rem;">Verified Safe</a>
        <a href="mailto:{support_email}" style="color:#94a3b8;text-decoration:none;font-size:0.9rem;">{support_email}</a>
      </div>
    </div>
    <div style="border-top:1px solid #1e293b;padding-top:20px;font-size:0.82rem;color:#475569;">
      &copy; 2026 Laudo Lux, LLC &nbsp;&middot;&nbsp; <a href="mailto:{support_email}" style="color:#475569;">{support_email}</a>
    </div>
  </div>
</footer>"""

def make_logo_html(name):
    """Split 'FarmerTasksAI' -> 'FarmerTasks<span>AI</span>'"""
    if name.endswith('AI'):
        return name[:-2] + 'Tasks<span>AI</span>' if 'Tasks' not in name[:-2] else name.replace('TasksAI', 'Tasks<span>AI</span>')
    return name

def generate(v, template):
    name = v['name']
    domain = v['domain']
    ga_id = v.get('ga_measurement_id', '')

    # Handle GA tag block: remove entirely if no ID
    html = template
    if ga_id:
        html = html.replace('{{GA_TAG}}', ga_id)
    else:
        html = re.sub(
            r'<!-- Google tag \(gtag\.js\) -->\s*<script async[^<]*</script>\s*<script>.*?gtag\(\'config\',\s*\'{{GA_TAG}}\'\);\s*</script>',
            '',
            html,
            flags=re.DOTALL
        )
        html = html.replace('{{GA_TAG}}', '')

    html = html.replace('{{NAME}}', name)
    html = html.replace('{{PRODUCT_NAME}}', name)
    html = html.replace('{{DOMAIN}}', domain)
    html = html.replace('{{PRODUCT_ID}}', v['product_id'])
    html = html.replace('{{SUPPORT_EMAIL}}', v.get('support_email', f"hello@{domain}"))
    html = html.replace('{{LOGO_HTML}}', make_logo_html(name))
    html = html.replace('{{FOOTER}}', make_footer(v))
    return html

# Repo name overrides (product_id → actual repo name in laudoluxDev org)
REPO_NAME_OVERRIDES = {
    'law':      'lawtasksai-landing',
    'realtor':  'realtor-landing',
    'marketing':'marketingtasksai-landing',
    'mortuary': 'mortician-landing',
    'church':   'churchadmin-landing',
}

def repo_name(product_id):
    return REPO_NAME_OVERRIDES.get(product_id, f"{product_id}-landing")

def main():
    template = TEMPLATE_FILE.read_text()
    verticals = json.loads(VERTICALS_FILE.read_text())

    generated = []
    skipped = []

    for v in verticals:
        slug = v['product_id']
        repo_dir = REPOS_BASE / repo_name(slug)

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
