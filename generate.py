#!/usr/bin/env python3
"""
TasksAI Landing Page Generator
Generates one landing page per vertical from template.html + verticals.json
"""

import json
import os
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
TEMPLATE_FILE = BASE_DIR / "template.html"
VERTICALS_FILE = BASE_DIR / "verticals.json"
OUTPUT_DIR = BASE_DIR / "output"

# ── Helpers ────────────────────────────────────────────────────────────────

def build_logo_html(product_name: str, accent_color: str) -> str:
    """Split ProductNameTasksAI into logo with <span> around 'AI'."""
    if product_name.endswith("TasksAI"):
        base = product_name[:-2]          # e.g. "LawTasks"
        return f'{base}<span>AI</span>'
    # Fallback: accent the last two chars
    return f'{product_name[:-2]}<span>{product_name[-2:]}</span>'


def build_example_chips(tasks: list[str]) -> str:
    """Render example tasks as chip HTML."""
    chips = []
    for i, task in enumerate(tasks):
        cls = 'task-chip accent' if i == 0 else 'task-chip'
        chips.append(f'<span class="{cls}">{task}</span>')
    return "\n            ".join(chips)


def build_feature_cards(features: list[dict]) -> str:
    """Render feature cards HTML."""
    cards = []
    for f in features:
        # Use full_title if available (for onclick matching), else title
        full_title = f.get('full_title', f['title'])
        card = f"""<div class="feature-card" onclick="openCategory('{full_title}')">
                    <div class="feature-icon">{f['icon']}</div>
                    <h3>{f['title']}</h3>
                    <p>{f['desc']}</p>
                    <div class="card-cta">Browse tasks →</div>
                </div>"""
        cards.append(card)
    return "\n                ".join(cards)


def target_audience_short(full: str) -> str:
    """Return a shorter version of the target audience for headings."""
    # Return everything up to first comma, or first 50 chars
    parts = full.split(',')
    short = parts[0].strip()
    if len(short) > 60:
        short = short[:57] + '...'
    return short


def generate_page(template: str, vertical: dict) -> str:
    """Replace all placeholders in the template for one vertical."""

    # Support both old schema (slug/product_name) and new schema (product_id/name)
    slug = vertical.get("slug") or vertical.get("product_id", "unknown")
    product_name = vertical.get("product_name") or vertical.get("name", slug)
    domain = vertical["domain"]
    tagline = vertical["tagline"]
    target_audience = vertical.get("target_audience") or vertical.get("audience", "professionals")
    primary = vertical.get("primary_color", "#1a1a1a")
    accent = vertical.get("accent_color", "#6366F1")
    background = vertical.get("background_color", "#FAFAFA")
    tasks = vertical.get("example_tasks") or vertical.get("sample_tasks", [])
    claude_your = vertical.get("claude_your", f"Your {product_name} admin, automated")
    hero_count = vertical.get("hero_count") or f"{vertical.get('skill_count', 200)}+"
    hero_noun = vertical.get("hero_noun", "Expert Tasks")
    # Build features from categories if no explicit features list
    raw_features = vertical.get("features", [])
    if not raw_features:
        categories = vertical.get("categories", [])
        # Map categories to icons
        icon_map = {
            "estimat": "📋", "bid": "📋", "contract": "📝", "schedul": "📅",
            "financial": "💰", "billing": "💰", "payment": "💰", "safety": "⛑️",
            "compliance": "✅", "subcontract": "🤝", "vendor": "🤝", "supplier": "🤝",
            "licens": "🏅", "insurance": "🛡️", "business": "🏢", "closeout": "🏁",
            "patient": "🏥", "clinical": "🏥", "hipaa": "🔒", "intake": "📋",
            "member": "👥", "client": "👤", "customer": "👤", "staff": "👥",
            "tax": "🧾", "payroll": "💵", "bookkeep": "📒", "report": "📊",
            "marketing": "📣", "listing": "🏠", "transaction": "🔄", "event": "🎉",
            "crop": "🌾", "equipment": "🚜", "farm": "🌾", "land": "🏞️",
            "sermon": "📖", "ministry": "✝️", "volunteer": "🙋", "outreach": "🤲",
            "program": "📚", "curriculum": "📚", "lesson": "📚", "student": "🎓",
            "recipe": "🍽️", "food": "🍽️", "restaurant": "🍽️", "menu": "🍽️",
            "treatment": "💊", "prescription": "💊", "therapy": "🧠", "counsel": "🧠",
            "travel": "✈️", "itinerar": "🗺️", "booking": "🎫", "trip": "✈️",
            "animal": "🐾", "veterin": "🐾", "pet": "🐾",
        }
        for cat in categories:
            cat_lower = cat.lower()
            icon = "📄"
            for keyword, emoji in icon_map.items():
                if keyword in cat_lower:
                    icon = emoji
                    break
            # Strip "Category N:" prefix if present, and " Administration" suffix for brevity
            display = cat.replace(" Administration", "").replace(" Management", "")
            raw_features.append({
                "icon": icon,
                "title": display,
                "full_title": cat,  # full name for API category matching
                "desc": f"Purpose-built tasks covering {cat.lower()} for {target_audience_short(target_audience)}."
            })
    features = raw_features

    logo_html = build_logo_html(product_name, accent)
    example_chips = build_example_chips(tasks)
    feature_cards = build_feature_cards(features)
    audience_short = target_audience_short(target_audience)

    page = template
    replacements = {
        "{{PRODUCT_NAME}}": product_name,
        "{{TAGLINE}}": tagline,
        "{{TARGET_AUDIENCE}}": target_audience,
        "{{TARGET_AUDIENCE_SHORT}}": audience_short,
        "{{DOMAIN}}": domain,
        "{{PRODUCT_SLUG}}": slug,
        "{{PRODUCT_ID}}": slug,
        "{{PRIMARY_COLOR}}": primary,
        "{{ACCENT_COLOR}}": accent,
        "{{BACKGROUND_COLOR}}": background,
        "{{HERO_COUNT}}": hero_count,
        "{{HERO_NOUN}}": hero_noun,
        "{{CLAUDE_YOUR}}": claude_your,
        "{{EXAMPLE_TASKS}}": ", ".join(tasks),
        "{{EXAMPLE_TASK_CHIPS}}": example_chips,
        "{{FEATURE_CARDS}}": feature_cards,
        "{{LOGO_HTML}}": logo_html,
        "{{LOGO_HTML_FOOTER}}": logo_html,
    }

    for placeholder, value in replacements.items():
        page = page.replace(placeholder, value)

    return page


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    # Validate files exist
    if not TEMPLATE_FILE.exists():
        print(f"ERROR: template.html not found at {TEMPLATE_FILE}", file=sys.stderr)
        sys.exit(1)

    if not VERTICALS_FILE.exists():
        print(f"ERROR: verticals.json not found at {VERTICALS_FILE}", file=sys.stderr)
        sys.exit(1)

    # Load inputs
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    verticals = json.loads(VERTICALS_FILE.read_text(encoding="utf-8"))

    print(f"\n🚀 TasksAI Landing Page Generator")
    print(f"   Template: {TEMPLATE_FILE}")
    print(f"   Verticals: {len(verticals)} found")
    print(f"   Output: {OUTPUT_DIR}\n")

    generated = []
    errors = []

    for v in verticals:
        slug = v.get("slug") or v.get("product_id", "unknown")
        try:
            out_dir = OUTPUT_DIR / slug
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / "index.html"

            page = generate_page(template, v)
            out_file.write_text(page, encoding="utf-8")

            # Generate success.html
            success_template_path = TEMPLATE_FILE.parent / "success-template.html"
            if success_template_path.exists():
                success_tmpl = success_template_path.read_text(encoding="utf-8")
                product_name = v.get("name", slug)
                domain = v.get("domain", f"{slug}tasksai.com")
                accent = v.get("accent_color", "#2563eb")
                product_id = v.get("product_id", slug)
                # Split product name for logo: e.g. "RealtorTasksAI" -> "Realtor<span>TasksAI</span>"
                if "TasksAI" in product_name:
                    parts = product_name.split("TasksAI")
                    logo_split = f"{parts[0]}<span>TasksAI</span>"
                else:
                    logo_split = product_name
                success_page = success_tmpl \
                    .replace("{{PRODUCT_NAME}}", product_name) \
                    .replace("{{PRODUCT_NAME_SPLIT}}", logo_split) \
                    .replace("{{ACCENT_COLOR}}", accent) \
                    .replace("{{DOMAIN}}", domain) \
                    .replace("{{PRODUCT_ID}}", product_id)
                (out_dir / "success.html").write_text(success_page, encoding="utf-8")

            # Generate terms, privacy, support pages
            occupation = v.get("occupation", v.get("audience", slug))
            for tmpl_name, out_name in [
                ("terms-template.html", "terms.html"),
                ("privacy-template.html", "privacy.html"),
                ("support-template.html", "support.html"),
            ]:
                tmpl_path = TEMPLATE_FILE.parent / tmpl_name
                if tmpl_path.exists():
                    tmpl_content = tmpl_path.read_text(encoding="utf-8")
                    rendered = tmpl_content \
                        .replace("{{PRODUCT_NAME}}", product_name) \
                        .replace("{{PRODUCT_NAME_SPLIT}}", logo_split) \
                        .replace("{{ACCENT_COLOR}}", accent) \
                        .replace("{{DOMAIN}}", domain) \
                        .replace("{{PRODUCT_ID}}", product_id) \
                        .replace("{{OCCUPATION}}", occupation)
                    (out_dir / out_name).write_text(rendered, encoding="utf-8")

            # Quick sanity check: no unreplaced placeholders
            remaining = [tok for tok in ["{{PRODUCT_NAME}}", "{{PRIMARY_COLOR}}", "{{ACCENT_COLOR}}"] if tok in page]
            if remaining:
                print(f"  ⚠️  {slug}: unreplaced placeholders: {remaining}")

            size_kb = out_file.stat().st_size / 1024
            print(f"  ✅  {slug:20s}  →  output/{slug}/index.html  ({size_kb:.1f} KB)")
            generated.append(slug)

        except Exception as e:
            print(f"  ❌  {slug}: ERROR — {e}")
            errors.append((slug, str(e)))

    # Summary
    print(f"\n{'─'*50}")
    print(f"✅ Generated: {len(generated)}/{len(verticals)} pages")
    if errors:
        print(f"❌ Errors:    {len(errors)}")
        for slug, err in errors:
            print(f"   • {slug}: {err}")
    else:
        print(f"🎉 All {len(generated)} pages generated successfully!")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print()


if __name__ == "__main__":
    main()
