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
        cls = 'task-chip'
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


def build_testimonials_html(testimonials: list, heading: str = "What our users are saying") -> str:
    """Render testimonials section HTML, or empty string if no valid entries."""
    if not testimonials:
        return ""
    valid = [t for t in testimonials if t.get("quote", "").strip()]
    if not valid:
        return ""

    def esc(s):
        return (s or "").replace("<", "&lt;").replace(">", "&gt;")

    cards = []
    for t in valid:
        quote = esc(t.get("quote", ""))
        name = esc(t.get("name", ""))
        role = esc(t.get("role", ""))
        location = esc(t.get("location", ""))
        location_sep = " · " if role and location else ""
        cards.append(f"""            <div class="testimonial-card" style="background:var(--background);padding:28px;border-radius:12px;border:1px solid #e5e7eb;">
                <p style="font-size:1rem;color:#374151;line-height:1.7;margin-bottom:16px;">"{quote}"</p>
                <div style="font-weight:600;color:var(--primary);">{name}</div>
                <div style="font-size:0.85rem;color:#6b7280;">{role}{location_sep}{location}</div>
            </div>""")

    cards_html = "\n".join(cards)
    return f"""<section class="testimonials" style="padding:80px 0;background:#ffffff;">
    <div class="container">
        <h2 class="section-title">{heading}</h2>
        <div class="testimonial-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px;margin-top:32px;">
{cards_html}
        </div>
    </div>
</section>"""


def build_compliance_html(items: list, heading: str = "Trust & Compliance") -> str:
    """Render compliance/trust badges section HTML, or empty string if no items."""
    if not items:
        return ""

    def esc(s):
        return (s or "").replace("<", "&lt;").replace(">", "&gt;")

    cards = []
    for item in items:
        badge = esc(item.get("badge", ""))
        title = esc(item.get("title", ""))
        description = esc(item.get("description", ""))
        cards.append(f"""            <div class="compliance-card" style="background:#ffffff;padding:28px;border-radius:12px;border:1px solid #e5e7eb;">
                <div style="display:inline-block;padding:4px 12px;border-radius:20px;background:var(--accent);color:#ffffff;font-size:0.8rem;font-weight:600;margin-bottom:12px;">{badge}</div>
                <h3 style="font-size:1.1rem;font-weight:600;color:#111827;margin-bottom:8px;">{title}</h3>
                <p style="font-size:0.9rem;color:#6b7280;line-height:1.6;">{description}</p>
            </div>""")

    cards_html = "\n".join(cards)
    return f"""<section class="compliance-section" style="padding:60px 0 80px;background:#f9fafb;">
    <div class="container">
        <h2 class="section-title">{heading}</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px;margin-top:32px;">
{cards_html}
        </div>
    </div>
</section>"""


def build_pricing_html(tiers: list, hero_count: str, show_default_tryit: bool = True) -> str:
    """Render pricing cards HTML. If tiers is empty, return the default pricing-grid HTML."""
    if not tiers:
        tryit_block = ""
        if show_default_tryit:
            tryit_block = f"""                <div class="pricing-card">
                    <h3>Try It</h3>
                    <div class="price">$5</div>
                    <div class="credits">2 credits</div>
                    <p class="per-credit">$2.50 per task</p>
                    <ul>
                        <li>\u2713 All {hero_count} tasks</li>
                        <li>\u2713 Credits never expire</li>
                        <li>\u2713 Try before you commit</li>
                    </ul>
                    <button onclick="checkout('tryit')" class="buy-btn">Try It</button>
                </div>

"""
        return f"""<div class="pricing-grid">
{tryit_block}                <div class="pricing-card">
                    <h3>Starter</h3>
                    <div class="price">$29</div>
                    <div class="credits">15 credits</div>
                    <p class="per-credit">$1.93 per task</p>
                    <ul>
                        <li>\u2713 All {hero_count} tasks</li>
                        <li>\u2713 Credits never expire</li>
                        <li>\u2713 Perfect for getting started</li>
                    </ul>
                    <button onclick="checkout('starter')" class="buy-btn">Get Started</button>
                </div>

                <div class="pricing-card">
                    <h3>Pro</h3>
                    <div class="price">$99</div>
                    <div class="credits">60 credits</div>
                    <p class="per-credit">$1.65 per task \u00b7 14% off</p>
                    <ul>
                        <li>\u2713 All {hero_count} tasks</li>
                        <li>\u2713 Credits never expire</li>
                        <li>\u2713 Great for regular use</li>
                    </ul>
                    <button onclick="checkout('pro')" class="buy-btn">Get Credits</button>
                </div>

                <div class="pricing-card featured">
                    <div class="badge">Most Popular</div>
                    <h3>Business</h3>
                    <div class="price">$199</div>
                    <div class="credits">150 credits</div>
                    <p class="per-credit">$1.33 per task \u00b7 31% off</p>
                    <ul>
                        <li>\u2713 All {hero_count} tasks</li>
                        <li>\u2713 Credits never expire</li>
                        <li>\u2713 Best for active practices</li>
                    </ul>
                    <button onclick="checkout('business')" class="buy-btn">Get Credits</button>
                </div>

                <div class="pricing-card">
                    <h3>Power</h3>
                    <div class="price">$349</div>
                    <div class="credits">350 credits</div>
                    <p class="per-credit">$1.00 per task \u00b7 48% off</p>
                    <ul>
                        <li>\u2713 All {hero_count} tasks</li>
                        <li>\u2713 Credits never expire</li>
                        <li>\u2713 Serious savings for busy teams</li>
                    </ul>
                    <button onclick="checkout('power')" class="buy-btn">Get Credits</button>
                </div>

                <div class="pricing-card">
                    <h3>Unlimited</h3>
                    <div class="price">$599</div>
                    <div class="credits">800 credits</div>
                    <p class="per-credit">$0.75 per task \u00b7 61% off</p>
                    <ul>
                        <li>\u2713 All {hero_count} tasks</li>
                        <li>\u2713 Credits never expire</li>
                        <li>\u2713 Maximum value</li>
                    </ul>
                    <button onclick="checkout('unlimited')" class="buy-btn">Get Credits</button>
                </div>

                <div class="pricing-card">
                    <h3>Enterprise</h3>
                    <div class="price">$999</div>
                    <div class="credits">2,000 credits</div>
                    <p class="per-credit">$0.50 per task \u00b7 74% off</p>
                    <ul>
                        <li>\u2713 All {hero_count} tasks</li>
                        <li>\u2713 Credits never expire</li>
                        <li>\u2713 Best value for power users</li>
                    </ul>
                    <button onclick="checkout('enterprise')" class="buy-btn">Get Credits</button>
                </div>
            </div>"""

    def esc(s):
        return (s or "").replace("<", "&lt;").replace(">", "&gt;")

    cards = []
    for tier in tiers:
        name = esc(tier.get("name", ""))
        price = esc(tier.get("price", ""))
        credits = esc(tier.get("credits", ""))
        per_credit = esc(tier.get("per_credit", ""))
        features = tier.get("features") or [f"All {hero_count} tasks", "Credits never expire"]
        button_label = esc(tier.get("button_label", "Get Credits"))
        button_action = tier.get("button_action", "checkout")
        checkout_pack = esc(tier.get("checkout_pack", ""))
        contact_href = esc(tier.get("contact_href", ""))
        featured = tier.get("featured", False)
        badge_text = esc(tier.get("badge", "Most Popular"))

        card_class = 'pricing-card featured' if featured else 'pricing-card'
        badge_html = f'\n                    <div class="badge">{badge_text}</div>' if featured else ""
        credits_html = f'\n                    <div class="credits">{credits}</div>' if credits else ""
        per_credit_html = f'\n                    <p class="per-credit">{per_credit}</p>' if per_credit else ""

        feature_items = "\n".join(f"                        <li>\u2713 {esc(f)}</li>" for f in features)

        if button_action == "contact":
            button_html = f'<a href="{contact_href}" class="buy-btn" style="display:block;text-align:center;text-decoration:none;">{button_label}</a>'
        else:
            button_html = f'<button onclick="checkout(\'{checkout_pack}\')" class="buy-btn">{button_label}</button>'

        cards.append(f"""                <div class="{card_class}">{badge_html}
                    <h3>{name}</h3>
                    <div class="price">{price}</div>{credits_html}{per_credit_html}
                    <ul>
{feature_items}
                    </ul>
                    {button_html}
                </div>""")

    cards_html = "\n\n".join(cards)
    return f"""<div class="pricing-grid">
{cards_html}
            </div>"""


def target_audience_short(full: str) -> str:
    """Return a shorter version of the target audience for headings."""
    # Return everything up to first comma, or first 50 chars
    parts = full.split(',')
    short = parts[0].strip()
    if len(short) > 60:
        short = short[:57] + '...'
    return short


def build_schema_offers(show_tryit: bool) -> str:
    """Build the JSON-LD offers array, conditionally including the Try It tier."""
    offers = []
    if show_tryit:
        offers.append({"@type": "Offer", "name": "Try It", "price": "5.00",
                       "priceCurrency": "USD", "description": "2 credits"})
    offers += [
        {"@type": "Offer", "name": "Starter",    "price": "29.00",  "priceCurrency": "USD", "description": "15 credits"},
        {"@type": "Offer", "name": "Pro",         "price": "99.00",  "priceCurrency": "USD", "description": "60 credits"},
        {"@type": "Offer", "name": "Business",   "price": "199.00", "priceCurrency": "USD", "description": "150 credits"},
        {"@type": "Offer", "name": "Power",       "price": "349.00", "priceCurrency": "USD", "description": "350 credits"},
        {"@type": "Offer", "name": "Unlimited",   "price": "599.00", "priceCurrency": "USD", "description": "800 credits"},
        {"@type": "Offer", "name": "Enterprise",  "price": "999.00", "priceCurrency": "USD", "description": "2000 credits"},
    ]
    lines = []
    for i, offer in enumerate(offers):
        comma = "," if i < len(offers) - 1 else ""
        lines.append(
            f'            {{"@type": "Offer", "name": "{offer["name"]}", '
            f'"price": "{offer["price"]}", "priceCurrency": "USD", '
            f'"description": "{offer["description"]}"}}{comma}'
        )
    inner = "\n".join(lines)
    return f"[\n{inner}\n        ]"


def build_ga_tag(ga_id: str) -> str:
    """Build the Google Analytics script tag, or empty string if no GA ID."""
    if not ga_id:
        return ""
    return f"""<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{ga_id}');
</script>"""


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
    hero_h1 = vertical.get("hero_h1") or vertical.get("claude_your") or "Stop prompt engineering. Start getting work done"
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
            # Use the category name directly as the card title
            display = cat
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

    # Build Try It card (conditionally included)
    show_tryit = vertical.get("show_tryit", True)  # default True
    tryit_card = """"""
    if show_tryit:
        tryit_card = f"""<div class="pricing-card">
                    <h3>Try It</h3>
                    <div class="price">$5</div>
                    <div class="credits">2 credits</div>
                    <p class="per-credit">$2.50 per task</p>
                    <ul>
                        <li>\u2713 All {hero_count} tasks</li>
                        <li>\u2713 Credits never expire</li>
                        <li>\u2713 Try before you commit</li>
                    </ul>
                    <button onclick=\"checkout('tryit')\" class=\"buy-btn\">Try It</button>
                </div>"""

    api_base = vertical.get("api_base", "https://api.lawtasksai.com")

    # Build GA tag (empty string if no GA ID)
    ga_tag = build_ga_tag(vertical.get("ga_measurement_id", ""))

    # New optional fields
    pricing_tiers = vertical.get("pricing_tiers", [])
    pricing_cards = build_pricing_html(pricing_tiers, hero_count, show_tryit)

    testimonials = vertical.get("testimonials", [])
    testimonials_heading = vertical.get("testimonials_heading", "What our users are saying")
    testimonials_section = build_testimonials_html(testimonials, testimonials_heading)

    compliance_items = vertical.get("compliance", [])
    compliance_heading = vertical.get("compliance_heading", "Trust & Compliance")
    compliance_section = build_compliance_html(compliance_items, compliance_heading)

    # _OR_DEFAULT computed values
    hero_eyebrow_custom = vertical.get("hero_eyebrow", "").strip()
    hero_eyebrow_or_default = hero_eyebrow_custom if hero_eyebrow_custom else f"{hero_count} Purpose-Built {hero_noun}"

    hero_subhead_custom = vertical.get("hero_subhead", "").strip()
    hero_subhead_or_default = hero_subhead_custom if hero_subhead_custom else (
        f"A generic AI is a Swiss Army knife \u2014 useful for everything, optimized for nothing. "
        f"{product_name} is {hero_count} purpose-built tasks, each engineered for exactly the work <em>you</em> do."
    )

    hero_fine_print_custom = vertical.get("hero_fine_print", "").strip()
    hero_fine_print_or_default = hero_fine_print_custom if hero_fine_print_custom else (
        "5 free credits on signup &nbsp;\u00b7&nbsp; Credits never expire &nbsp;\u00b7&nbsp; No subscription"
    )

    features_intro_custom = vertical.get("features_intro", "").strip()
    features_intro_or_default = features_intro_custom if features_intro_custom else f"Built for {audience_short}"

    features_subtitle_custom = vertical.get("features_subtitle", "").strip()
    features_subtitle_or_default = features_subtitle_custom if features_subtitle_custom else (
        "Every task template was engineered with the specific terminology, workflows, and standards of "
        "your profession \u2014 not repurposed from generic business content."
    )

    pricing_tagline_custom = vertical.get("pricing_tagline", "").strip()
    pricing_tagline_or_default = pricing_tagline_custom if pricing_tagline_custom else (
        "No subscriptions. No monthly fees. Buy credits, use them whenever you need them. Credits never expire."
    )

    # API cost disclaimer handling
    api_cost_disclaimer = vertical.get("api_cost_disclaimer", "").strip()
    api_cost_disclaimer_position = vertical.get("api_cost_disclaimer_position", "bottom")
    default_disclaimer_text = (
        f"*{product_name} credits cover {product_name} tasks only. "
        "If you use a cloud AI provider (Anthropic, OpenAI, etc.), their API charges are separate."
    )
    disclaimer_text = api_cost_disclaimer if api_cost_disclaimer else default_disclaimer_text

    if api_cost_disclaimer_position == "top" and api_cost_disclaimer:
        api_cost_disclaimer_top_html = (
            f'<div style="background:#fef3c7;border:1px solid #fcd34d;border-radius:8px;'
            f'padding:16px 20px;margin-bottom:32px;color:#78350f;font-size:0.95rem;text-align:center;">'
            f'<strong>Heads up:</strong> {api_cost_disclaimer}</div>'
        )
        api_cost_disclaimer_bottom_text = ""
    else:
        api_cost_disclaimer_top_html = ""
        api_cost_disclaimer_bottom_text = disclaimer_text

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
        "{{HERO_H1}}": hero_h1,
        "{{CLAUDE_YOUR}}": hero_h1,
        "{{HERO_EYEBROW}}": vertical.get("hero_eyebrow", ""),
        "{{HERO_EYEBROW_OR_DEFAULT}}": hero_eyebrow_or_default,
        "{{HERO_SUBHEAD}}": vertical.get("hero_subhead", ""),
        "{{HERO_SUBHEAD_OR_DEFAULT}}": hero_subhead_or_default,
        "{{HERO_FINE_PRINT}}": vertical.get("hero_fine_print", ""),
        "{{HERO_FINE_PRINT_OR_DEFAULT}}": hero_fine_print_or_default,
        "{{FEATURES_INTRO}}": vertical.get("features_intro", ""),
        "{{FEATURES_INTRO_OR_DEFAULT}}": features_intro_or_default,
        "{{FEATURES_SUBTITLE}}": vertical.get("features_subtitle", ""),
        "{{FEATURES_SUBTITLE_OR_DEFAULT}}": features_subtitle_or_default,
        "{{PRICING_TAGLINE}}": vertical.get("pricing_tagline", ""),
        "{{PRICING_TAGLINE_OR_DEFAULT}}": pricing_tagline_or_default,
        "{{API_COST_DISCLAIMER}}": api_cost_disclaimer,
        "{{API_COST_DISCLAIMER_POSITION}}": api_cost_disclaimer_position,
        "{{API_COST_DISCLAIMER_TOP_HTML}}": api_cost_disclaimer_top_html,
        "{{API_COST_DISCLAIMER_BOTTOM_TEXT}}": api_cost_disclaimer_bottom_text,
        "{{EXAMPLE_TASKS}}": ", ".join(tasks),
        "{{EXAMPLE_TASK_CHIPS}}": example_chips,
        "{{FEATURE_CARDS}}": feature_cards,
        "{{LOGO_HTML}}": logo_html,
        "{{LOGO_HTML_FOOTER}}": logo_html,
        "{{API_BASE}}": api_base,

        "{{SCHEMA_OFFERS}}": build_schema_offers(show_tryit),
        "{{TRYIT_CARD}}": "",
        "{{GA_TAG}}": ga_tag,
        "{{TESTIMONIALS_SECTION}}": testimonials_section,
        "{{COMPLIANCE_SECTION}}": compliance_section,
        "{{PRICING_CARDS}}": pricing_cards,
    }

    for placeholder, value in replacements.items():
        page = page.replace(placeholder, value)

    return page


# ── Main ────────────────────────────────────────────────

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

    print(f"\n TasksAI Landing Page Generator")
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
                    .replace("{{PRODUCT_ID_UPPER}}", product_id.upper()) \
                    .replace("{{PRODUCT_ID}}", product_id) \
                    .replace("{{API_BASE}}", v.get("api_base", "https://api.lawtasksai.com")) \
                    .replace("{{GA_TAG}}", build_ga_tag(v.get("ga_measurement_id", "")))
                (out_dir / "success.html").write_text(success_page, encoding="utf-8")

            # Generate signup.html
            signup_template_path = TEMPLATE_FILE.parent / "signup-template.html"
            if signup_template_path.exists():
                signup_tmpl = signup_template_path.read_text(encoding="utf-8")
                profession = v.get("occupation", v.get("audience", slug))
                professionals = v.get("professionals", profession + "s")
                role_title = v.get("role_title", product_name.replace("TasksAI", ""))
                signup_page = signup_tmpl \
                    .replace("{{PRODUCT_NAME}}", product_name) \
                    .replace("{{PRODUCT_NAME_SPLIT}}", logo_split) \
                    .replace("{{ACCENT_COLOR}}", accent) \
                    .replace("{{DOMAIN}}", domain) \
                    .replace("{{PRODUCT_ID}}", product_id) \
                    .replace("{{API_BASE}}", v.get("api_base", "https://api.lawtasksai.com")) \
                    .replace("{{GA_MEASUREMENT_ID}}", v.get("ga_measurement_id", "")) \
                    .replace("{{PROFESSION}}", profession) \
                    .replace("{{PROFESSIONALS}}", professionals) \
                    .replace("{{ROLE_TITLE}}", role_title)
                (out_dir / "signup.html").write_text(signup_page, encoding="utf-8")

            # Generate mcp.html
            mcp_template_path = TEMPLATE_FILE.parent / "mcp-template.html"
            if mcp_template_path.exists():
                mcp_tmpl = mcp_template_path.read_text(encoding="utf-8")
                tasks_list = v.get("sample_tasks", [])
                example_task = tasks_list[0] if tasks_list else f"a {v.get('occupation', slug)} task"
                product_id_upper = product_id.upper() + "TASKSAI"
                mcp_page = mcp_tmpl \
                    .replace("{{PRODUCT_NAME}}", product_name) \
                    .replace("{{PRODUCT_NAME_SPLIT}}", logo_split) \
                    .replace("{{ACCENT_COLOR}}", accent) \
                    .replace("{{DOMAIN}}", domain) \
                    .replace("{{PRODUCT_ID}}", product_id) \
                    .replace("{{PRODUCT_ID_UPPER}}", product_id_upper) \
                    .replace("{{LOGO_HTML}}", logo_split) \
                    .replace("{{EXAMPLE_TASK}}", example_task) \
                    .replace("{{GA_TAG}}", build_ga_tag(v.get("ga_measurement_id", "")))
                (out_dir / "mcp.html").write_text(mcp_page, encoding="utf-8")

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
                        .replace("{{OCCUPATION}}", occupation) \
                        .replace("{{GA_TAG}}", build_ga_tag(v.get("ga_measurement_id", "")))
                    (out_dir / out_name).write_text(rendered, encoding="utf-8")

            # Quick sanity check: no unreplaced placeholders
            remaining = [tok for tok in ["{{PRODUCT_NAME}}", "{{PRIMARY_COLOR}}", "{{ACCENT_COLOR}}"] if tok in page]
            if remaining:
                print(f"  WARNING  {slug}: unreplaced placeholders: {remaining}")

            size_kb = out_file.stat().st_size / 1024
            print(f"  OK  {slug:20s}  ->  output/{slug}/index.html  ({size_kb:.1f} KB)")
            generated.append(slug)

        except Exception as e:
            print(f"  ERROR  {slug}: {e}")
            errors.append((slug, str(e)))

    # Summary
    print(f"\n{chr(45)*50}")
    print(f"Generated: {len(generated)}/{len(verticals)} pages")
    if errors:
        print(f"Errors: {len(errors)}")
        for slug, err in errors:
            print(f"   - {slug}: {err}")
    else:
        print(f"All {len(generated)} pages generated successfully!")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print()


if __name__ == "__main__":
    main()
