#!/usr/bin/env python3
"""
generate_task_library.py
Fetches skills from the API and generates a static task-library.html
for each vertical (or a specified one).

Usage:
    python3 generate_task_library.py              # all verticals
    python3 generate_task_library.py contractor   # single vertical
"""

import json, re, sys, urllib.request, os
from pathlib import Path

API_BASE = "https://api.lawtasksai.com"
SCRIPT_DIR = Path(__file__).parent
VERTICALS_FILE = SCRIPT_DIR / "verticals.json"

def fetch_skills(product_id):
    url = f"{API_BASE}/v1/skills?limit=500"
    req = urllib.request.Request(url, headers={"X-Product-ID": product_id})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def category_slug(category_name):
    slug = category_name.lower()
    slug = re.sub(r'\s*&\s*', '_and_', slug)
    slug = re.sub(r'[^a-z0-9]+', '_', slug)
    return slug.strip('_')

def badge_class(idx):
    classes = ['badge-cat0','badge-cat1','badge-cat2','badge-cat3',
               'badge-cat4','badge-cat5','badge-cat6','badge-cat7']
    return classes[idx % len(classes)]

def ensure_plural(text):
    """Return a clean plural audience label for use in headings.

    1. If the text contains ' and ', use only the part before it
       (e.g. 'Chiropractors and chiropractic office staff' -> 'Chiropractors').
    2. If the resulting text already ends in 's', return as-is.
    3. Otherwise append 's'.

    Examples:
        'Marketing managers'                          -> 'Marketing managers'
        'Chiropractors and chiropractic office staff' -> 'Chiropractors'
        'Mortuary science professionals and ...'      -> 'Mortuary science professionals'
        'Farmer'                                      -> 'Farmers'
    """
    # Strip at " and " to avoid awkward compound plurals
    if ' and ' in text:
        text = text.split(' and ')[0].strip()
    word = text.rstrip().split()[-1] if text.strip() else ''
    if word.lower().endswith('s'):
        return text  # already plural
    return text + 's'


def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def generate_task_library(vertical, skills):
    name        = vertical['name']
    product_id  = vertical['product_id']
    domain      = vertical['domain']
    accent      = vertical['accent_color']
    icon        = vertical['icon']
    categories  = vertical['categories']
    audience    = vertical['audience']

    r, g, b = hex_to_rgb(accent)
    accent_light = f"rgba({r},{g},{b},0.1)"
    accent_hover_dark = f"rgba({r},{g},{b},0.85)"

    # Group skills by category
    groups = {}  # category_name -> [skill, ...]
    for cat in categories:
        groups[cat] = []

    for skill in skills:
        cid = (skill.get('category_id') or '').lower()
        matched = False
        for i, cat in enumerate(categories):
            prefix = (product_id + '_' + category_slug(cat))[:40]
            if cid.startswith(prefix):
                groups[cat].append(skill)
                matched = True
                break
        if not matched:
            # fallback: first category
            groups[categories[0]].append(skill)

    total = sum(len(v) for v in groups.values())

    # Build filter nav
    filter_nav_items = f'<a href="#all" class="filter-btn active">All {total}</a>\n'
    for i, cat in enumerate(categories):
        slug = category_slug(cat)
        count = len(groups[cat])
        filter_nav_items += f'            <a href="#{slug}" class="filter-btn" data-cat="{slug}">{cat} ({count})</a>\n'

    # Build category sections
    sections_html = ''
    for i, cat in enumerate(categories):
        slug = category_slug(cat)
        skill_list = groups[cat]
        count = len(skill_list)

        cards = ''
        for s in skill_list:
            desc = (s.get('description') or '').replace('<', '&lt;').replace('>', '&gt;')
            task_name = (s.get('name') or '').replace('<', '&lt;').replace('>', '&gt;').capitalize()
            cards += f'''
                <div class="task-card">
                    <h3>{task_name}</h3>
                    <p>{desc}</p>
                    <div class="task-footer">
                        <span class="task-badge {badge_class(i)}">{cat}</span>
                        <a href="/verified_safe.html" title="Security verified" style="display:inline-flex;align-items:center;gap:4px;background:#10b981;color:white;padding:3px 9px;border-radius:100px;font-size:0.75rem;font-weight:600;text-decoration:none;white-space:nowrap;">🛡️ Verified Safe</a>
                    </div>
                </div>'''

        sections_html += f'''
    <!-- {cat} -->
    <section class="category-section" id="{slug}">
        <div class="container">
            <div class="category-header">
                <h2>{cat}</h2>
                <span class="category-count">{count} task{"s" if count != 1 else ""}</span>
            </div>
            <div class="task-grid">{cards}
            </div>
        </div>
    </section>
'''

    # Badge color palette (8 colors, cycles)
    badge_palette = [
        ('badge-cat0', accent_light, accent),
        ('badge-cat1', '#fef3c7', '#92400e'),
        ('badge-cat2', '#f0fdf4', '#15803d'),
        ('badge-cat3', '#fdf4ff', '#7e22ce'),
        ('badge-cat4', '#fff7ed', '#9a3412'),
        ('badge-cat5', '#f0f9ff', '#0369a1'),
        ('badge-cat6', '#fef2f2', '#b91c1c'),
        ('badge-cat7', '#f5f3ff', '#5b21b6'),
    ]
    badge_css = ''
    for cls, bg, color in badge_palette:
        badge_css += f'        .{cls} {{ background: {bg}; color: {color}; }}\n'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Library — {total} Purpose-Built {ensure_plural(audience.split(",")[0])} Tools — {name}</title>
    <meta name="description" content="Browse all {total} {name} task templates. Purpose-built for {audience} — every task engineered for your specific workflows.">
    <link rel="canonical" href="https://{domain}/task-library">
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6; color: #1a1a1a; background: #fafafa;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; padding: 0 24px; }}

        /* Header */
        header {{
            padding: 20px 0; background: white;
            border-bottom: 1px solid #e5e7eb;
            position: sticky; top: 0; z-index: 100;
        }}
        header .container {{ display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 1.4rem; font-weight: 700; color: #1a1a1a; text-decoration: none; letter-spacing: -0.02em; }}
        .logo span {{ color: {accent}; }}
        .nav-links {{ display: flex; align-items: center; gap: 24px; }}
        .nav-links a {{ color: #4b5563; text-decoration: none; font-weight: 500; transition: color 0.2s; }}
        .nav-links a:hover {{ color: {accent}; }}
        .header-cta {{
            padding: 10px 20px; border-radius: 6px; font-weight: 600;
            font-size: 0.9rem; background: {accent}; color: white !important;
        }}
        .header-cta:hover {{ opacity: 0.88; }}
        .hamburger {{ display: none; background: none; border: none; cursor: pointer; padding: 8px; z-index: 300; }}
        .hamburger span {{ display: block; width: 24px; height: 2px; background: #1a1a1a; margin: 5px 0; transition: all 0.3s; }}
        .hamburger.active span:nth-child(1) {{ transform: rotate(45deg) translate(5px, 5px); }}
        .hamburger.active span:nth-child(2) {{ opacity: 0; }}
        .hamburger.active span:nth-child(3) {{ transform: rotate(-45deg) translate(5px, -5px); }}
        .mobile-overlay {{ display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 150; }}
        .mobile-overlay.active {{ display: block; }}

        /* Hero */
        .page-hero {{
            padding: 64px 0 48px; text-align: center;
            background: linear-gradient(180deg, white 0%, #f9fafb 100%);
        }}
        .page-hero .eyebrow {{
            display: inline-block; background: {accent_light}; color: {accent};
            font-size: 0.85rem; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.08em; padding: 6px 16px; border-radius: 20px; margin-bottom: 20px;
        }}
        .page-hero h1 {{ font-size: 2.5rem; font-weight: 700; margin-bottom: 16px; letter-spacing: -0.02em; }}
        .page-hero h1 span {{ color: {accent}; }}
        .page-hero p {{ font-size: 1.1rem; color: #6b7280; max-width: 580px; margin: 0 auto; }}

        /* Filter nav */
        .filter-nav {{
            background: white; border-bottom: 1px solid #e5e7eb;
            padding: 16px 0; position: sticky; top: 62px; z-index: 90;
        }}
        .filter-nav .container {{ display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }}
        .filter-btn {{
            display: inline-block; padding: 8px 18px; border-radius: 20px;
            font-size: 0.85rem; font-weight: 600; border: 2px solid #e5e7eb;
            color: #4b5563; background: white; transition: all 0.2s;
            white-space: nowrap; cursor: pointer; text-decoration: none;
        }}
        .filter-btn:hover, .filter-btn.active {{
            border-color: {accent}; color: {accent}; background: {accent_light};
        }}

        /* Category sections */
        .category-section {{ padding: 56px 0; }}
        .category-section:nth-child(even) {{ background: white; }}
        .category-section:nth-child(odd) {{ background: #f9fafb; }}
        .category-header {{ display: flex; align-items: baseline; gap: 16px; margin-bottom: 32px; }}
        .category-header h2 {{ font-size: 1.75rem; font-weight: 700; }}
        .category-count {{ font-size: 0.9rem; color: #6b7280; font-weight: 500; white-space: nowrap; }}

        /* Task grid */
        .task-grid {{
            display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px;
        }}
        .task-card {{
            background: white; border-radius: 10px; padding: 20px 22px;
            border: 1px solid #e5e7eb; transition: all 0.2s;
            display: flex; flex-direction: column;
        }}
        .task-card:hover {{
            border-color: {accent}; box-shadow: 0 4px 12px rgba({r},{g},{b},0.1);
            transform: translateY(-1px);
        }}
        .task-card h3 {{ font-size: 0.97rem; font-weight: 700; margin-bottom: 7px; color: #1a1a1a; }}
        .task-card p {{ font-size: 0.87rem; color: #6b7280; line-height: 1.55; flex: 1; margin-bottom: 12px; }}
        .task-footer {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap; }}
        .task-badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600; }}


        /* Badge colors */
{badge_css}
        /* CTA */
        .bottom-cta {{
            padding: 80px 0; text-align: center;
            background: linear-gradient(180deg, #f9fafb 0%, white 100%);
        }}
        .bottom-cta h2 {{ font-size: 2rem; font-weight: 700; margin-bottom: 16px; }}
        .bottom-cta p {{ color: #6b7280; margin-bottom: 8px; font-size: 1.05rem; }}
        .bottom-cta .subp {{ color: #9ca3af; font-size: 0.9rem; margin-bottom: 28px; }}
        .cta-button {{
            display: inline-block; background: {accent}; color: white;
            padding: 16px 36px; border-radius: 8px; text-decoration: none;
            font-weight: 600; font-size: 1.05rem; transition: all 0.2s;
            box-shadow: 0 4px 14px rgba({r},{g},{b},0.3);
        }}
        .cta-button:hover {{ opacity: 0.88; transform: translateY(-2px); }}

        /* Footer */
        footer {{
            padding: 40px 0; background: #f9fafb; border-top: 1px solid #e5e7eb;
            text-align: center; color: #6b7280; font-size: 0.9rem;
        }}
        footer a {{ color: #6b7280; text-decoration: none; margin: 0 12px; }}
        footer a:hover {{ color: {accent}; }}

        @media (max-width: 768px) {{
            .page-hero h1 {{ font-size: 1.8rem; }}
            .filter-nav {{ top: 56px; }}
            .hamburger {{ display: block; }}
            .nav-links {{
                display: none; position: fixed; top: 0; right: 0;
                width: 280px; height: 100vh; background: white;
                flex-direction: column; padding: 80px 32px 32px; gap: 0;
                box-shadow: -4px 0 20px rgba(0,0,0,0.15); z-index: 200; align-items: flex-start;
            }}
            .nav-links.active {{ display: flex; }}
            .nav-links a {{ padding: 14px 0; font-size: 1.05rem; border-bottom: 1px solid #f3f4f6; width: 100%; }}
            .header-cta {{ width: 100%; text-align: center; margin-top: 16px; }}
            .task-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div id="site-header"></div>
    <script src="/header.js"></script>

    <section class="page-hero">
        <div class="container">
            <div class="eyebrow">{icon} {total} tasks available</div>
            <h1><span>{total}</span> Purpose-Built Tools<br>for {ensure_plural(audience.split(",")[0])}</h1>
            <p>Every task is engineered for one specific workflow — not a generic prompt, a purpose-built template.</p>
        </div>
    </section>

    <nav class="filter-nav" id="filterNav" aria-label="Task categories">
        <div class="container">
            {filter_nav_items}
        </div>
    </nav>

    {sections_html}

    <section class="bottom-cta" id="all">
        <div class="container">
            <h2>Access All {total} Tools</h2>
            <p>$29 gets you 15 tasks. Credits never expire. No subscription.</p>
            <p class="subp">Every task produces professional output ready for your review — never raw AI.</p>
            <a href="/#pricing" class="cta-button">Get Started — $29 Starter</a>
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2026 {name}. All rights reserved.</p>
            <p style="margin-top:8px;">
                <a href="/privacy">Privacy Policy</a>
                <a href="/terms">Terms of Service</a>
                <a href="/support">Support</a>
            </p>
        </div>
    </footer>

    <script>
        // Mobile nav
        const hamburger = document.getElementById('hamburger');
        const navLinks = document.getElementById('navLinks');
        const overlay = document.getElementById('overlay');
        function toggleNav() {{
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
            overlay.classList.toggle('active');
        }}
        hamburger.addEventListener('click', toggleNav);
        overlay.addEventListener('click', toggleNav);
        navLinks.querySelectorAll('a').forEach(a => {{
            a.addEventListener('click', () => {{ if (navLinks.classList.contains('active')) toggleNav(); }});
        }});

        // Category filter — scroll to section + highlight button
        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', function(e) {{
                e.preventDefault();
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                const href = this.getAttribute('href');
                const target = document.querySelector(href);
                if (target) {{
                    const offset = 130;
                    const top = target.getBoundingClientRect().top + window.scrollY - offset;
                    window.scrollTo({{ top, behavior: 'smooth' }});
                }} else {{
                    window.scrollTo({{ top: 0, behavior: 'smooth' }});
                }}
            }});
        }});

        // Highlight filter button on scroll
        const sections = document.querySelectorAll('.category-section');
        const filterBtns = document.querySelectorAll('.filter-btn[href^="#"]:not([href="#all"])');
        window.addEventListener('scroll', () => {{
            let current = '';
            sections.forEach(sec => {{
                if (window.scrollY >= sec.offsetTop - 160) current = sec.id;
            }});
            filterBtns.forEach(btn => {{
                btn.classList.remove('active');
                if (btn.getAttribute('href') === '#' + current) btn.classList.add('active');
            }});
            if (!current) document.querySelector('.filter-btn[href="#all"]').classList.add('active');
        }});
    </script>
</body>
</html>'''

    return html


def main():
    verticals = json.loads(VERTICALS_FILE.read_text())

    # Filter to specific product_id if passed as arg
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target:
        verticals = [v for v in verticals if v['product_id'] == target]
        if not verticals:
            print(f"No vertical found with product_id '{target}'")
            sys.exit(1)

    for vertical in verticals:
        pid = vertical['product_id']
        out_dir = SCRIPT_DIR / 'output' / pid
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / 'task-library.html'

        print(f"  Fetching skills for {pid}...", end=' ', flush=True)
        try:
            skills = fetch_skills(pid)
            if not skills:
                print(f"no skills found, skipping.")
                continue
            print(f"{len(skills)} skills found.")
        except Exception as e:
            print(f"ERROR: {e}, skipping.")
            continue

        html = generate_task_library(vertical, skills)
        out_file.write_text(html, encoding='utf-8')
        print(f"  ✅ Written: {out_file}")

    print("\nDone.")


if __name__ == '__main__':
    main()
