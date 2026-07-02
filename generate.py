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

def _installer_asset_name(product_name: str, product_id: str) -> str:
    """Return the GitHub release asset base name for installer downloads."""
    overrides = {
        "church": "ChurchTasksAI",
    }
    return overrides.get(product_id, product_name)


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


def build_youtube_section(video_id: str, product_name: str) -> str:
    """Build a YouTube embed section, or empty string if no video ID."""
    if not video_id:
        return ""
    return f"""
    <section class="video-section">
        <div class="container">
            <div class="video-eyebrow">See It In Action</div>
            <h2 class="section-title">Watch {product_name} Work</h2>
            <p class="section-subtitle">Same task. Raw AI vs. {product_name}. The difference is immediate.</p>
            <div class="video-outer">
                <div class="video-wrapper">
                    <iframe
                        src="https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
                        title="{product_name} explainer video"
                        frameborder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                        allowfullscreen
                        loading="lazy">
                    </iframe>
                </div>
            </div>
        </div>
    </section>"""


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


def build_hero_demo_html(demo_tasks: list, product_name: str, accent_color: str) -> str:
    """Build an animated CSS terminal card cycling through 3 demo tasks."""
    if not demo_tasks or len(demo_tasks) < 1:
        return ""

    # Pad to exactly 3 tasks
    tasks = (demo_tasks * 3)[:3]

    slides = ""
    for i, t in enumerate(tasks):
        prompt   = t.get("prompt", "")
        skill    = t.get("skill", "")
        chips    = t.get("chips", [])
        filename = t.get("filename", "output")
        preview  = t.get("preview", "")

        # Chips HTML — up to 3 shown + "+ more"
        chip_html = "".join(f'<span class="demo-chip">{c}</span>' for c in chips[:3])
        chip_html += '<span class="demo-chip demo-chip-more">+ more</span>'

        # Filename with live timestamp placeholder (filled by JS)
        file_html = f'<div class="demo-filename">&#128196; {filename}_<span class="demo-ts"></span>.docx</div>'

        # Preview text — truncate at 90 chars
        preview_short = (preview[:90] + "...") if len(preview) > 90 else preview
        preview_html  = f'<div class="demo-preview">&ldquo;{preview_short}&rdquo;</div>'

        slides += f"""
        <div class="demo-slide" data-index="{i}">
            <div class="demo-prompt-row">
                <span class="demo-caret">&gt;</span>
                <span class="demo-prompt-text">{prompt}</span><span class="demo-cursor">|</span>
            </div>
            <div class="demo-step step-skill">
                <span class="demo-spinner"></span>
                <span>Loading <span class="demo-product-name">{product_name}</span>: <strong>{skill}</strong></span>
            </div>
            <div class="demo-step step-output">
                <div class="demo-output-header">
                    <span class="demo-check">&#10003;</span>
                    <span><span class="demo-product-name">{product_name}</span> response ready</span>
                </div>
                <div class="demo-output-detail">
                    <div class="demo-chips">{chip_html}</div>
                    {file_html}
                    {preview_html}
                </div>
            </div>
        </div>"""

    dots = "".join(
        f'<span class="demo-dot{" active" if i == 0 else ""}" data-dot="{i}"></span>'
        for i in range(len(tasks))
    )

    return f"""
<div class="hero-demo" aria-hidden="true">
    <div class="demo-card">
        <div class="demo-card-header">
            <div class="demo-dots"><span></span><span></span><span></span></div>
            <span class="demo-card-title">{product_name}</span>
        </div>
        <div class="demo-card-body">
            <div class="demo-slides">{slides}
            </div>
        </div>
    </div>
    <div class="demo-indicators">{dots}</div>
</div>
<script>
(function(){{
    // Stamp all timestamp placeholders with current datetime
    var now = new Date();
    var ts  = now.getFullYear().toString()
            + String(now.getMonth()+1).padStart(2,'0')
            + String(now.getDate()).padStart(2,'0')
            + '_'
            + String(now.getHours()).padStart(2,'0')
            + String(now.getMinutes()).padStart(2,'0');
    document.querySelectorAll('.demo-ts').forEach(function(el){{ el.textContent = ts; }});

    var slides = document.querySelectorAll('.demo-slide');
    var dots   = document.querySelectorAll('.demo-dot');
    if (!slides.length) return;
    var current = 0;
    // ms: cursor blink, skill row, output row, read pause
    var PHASES = [800, 900, 1100, 3500];
    var total  = slides.length;

    function showSlide(idx) {{
        slides.forEach(function(s,i) {{
            s.classList.toggle('active', i === idx);
            s.classList.remove('phase-skill','phase-output');
        }});
        dots.forEach(function(d,i) {{ d.classList.toggle('active', i === idx); }});
        var s = slides[idx];
        setTimeout(function(){{ s.classList.add('phase-skill');  }}, PHASES[0]);
        setTimeout(function(){{ s.classList.add('phase-output'); }}, PHASES[0]+PHASES[1]);
    }}

    function next() {{
        current = (current + 1) % total;
        showSlide(current);
    }}

    showSlide(0);
    setInterval(next, PHASES[0]+PHASES[1]+PHASES[2]+PHASES[3]);

    dots.forEach(function(d,i) {{
        d.addEventListener('click', function() {{ current=i; showSlide(i); }});
    }});
}})();
</script>
"""


def build_social_proof_html(vertical: dict) -> str:
    """Build a social proof banner. Returns empty string if show_social_proof is False."""
    if not vertical.get("show_social_proof", False):
        return ""
    count = vertical.get("social_proof_count", 0)
    if count < 1:
        return ""
    product_name = vertical.get("name", vertical.get("product_id", ""))
    occupation = vertical.get("occupation", vertical.get("audience", "professionals"))
    # Use a short form of occupation for the banner
    occ_short = occupation.split(",")[0].strip()
    return f"""<section class="social-proof-section">
    <div class="container">
        <p>Join {count}+ {occ_short} already using {product_name}</p>
    </div>
</section>"""


def build_trust_bar_html(vertical: dict) -> str:
    """Build a trust/privacy bar. Generic version — the template now has it hardcoded."""
    # The template.html already has the trust bar hardcoded below the hero.
    # This function exists for future per-vertical customization but returns empty.
    return ""


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
        cards.append(f"""            <div class="compliance-card" style="background:#ffffff;padding:28px;border-radius:12px;border:1px solid color-mix(in srgb, var(--accent) 25%, #e5e7eb);box-shadow:0 2px 8px color-mix(in srgb, var(--accent) 10%, transparent);">
                <div style="display:inline-block;padding:5px 14px;border-radius:20px;background:var(--accent);color:#ffffff;font-size:1rem;font-weight:600;margin-bottom:12px;">{badge}</div>
                <h3 style="font-size:1.1rem;font-weight:600;color:#111827;margin-bottom:8px;">{title}</h3>
                <p style="font-size:1.05rem;color:#6b7280;line-height:1.6;">{description}</p>
            </div>""")

    cards_html = "\n".join(cards)
    return f"""<section class="compliance-section" style="padding:60px 0 80px;background:color-mix(in srgb, var(--accent) 8%, white);">
    <div class="container">
        <h2 class="section-title">{heading}</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px;margin-top:32px;">
{cards_html}
        </div>
    </div>
</section>"""


def build_pricing_html(tiers: list, hero_count: str, show_default_tryit: bool = True) -> str:
    """Render pricing cards HTML. If tiers is empty, return the default 3-tier pricing-grid HTML."""
    if not tiers:
        return f"""<div class="pricing-grid">
                <div class="pricing-card">
                    <h3>Starter</h3>
                    <div class="price">$29</div>
                    <div class="credits">50 credits</div>
                    <p class="per-credit">$0.58 per task</p>
                    <ul>
                        <li>\u2713 All {hero_count} tasks</li>
                        <li>\u2713 Credits never expire</li>
                        <li>\u2713 Great for occasional use</li>
                    </ul>
                    <button onclick="checkout('starter')" class="buy-btn">Get Started</button>
                </div>

                <div class="pricing-card featured">
                    <div class="badge">Most Popular</div>
                    <h3>Professional</h3>
                    <div class="price">$79</div>
                    <div class="credits">150 credits</div>
                    <p class="per-credit">$0.53 per task</p>
                    <ul>
                        <li>\u2713 All {hero_count} tasks</li>
                        <li>\u2713 Credits never expire</li>
                        <li>\u2713 Best for regular use</li>
                    </ul>
                    <button onclick="checkout('professional')" class="buy-btn">Best Value</button>
                </div>

                <div class="pricing-card">
                    <h3>Office</h3>
                    <div class="price">$199</div>
                    <div class="credits">500 credits</div>
                    <p class="per-credit">$0.40 per task</p>
                    <ul>
                        <li>\u2713 All {hero_count} tasks</li>
                        <li>\u2713 Credits never expire</li>
                        <li>\u2713 For high-volume workflows</li>
                    </ul>
                    <button onclick="checkout('office')" class="buy-btn">Get Credits</button>
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


def build_ga_tag(ga_id: str, ads_id: str = "") -> str:
    """Build Google gtag setup, or empty string if no Google IDs are configured."""
    ids = [item for item in [ga_id, ads_id] if item]
    if not ids:
        return ""
    config_lines = "\n".join(f"  gtag('config', '{item}');" for item in ids)
    return f"""<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={ids[0]}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
{config_lines}
</script>"""


def _ads_send_to(ads_id: str, conversion_label: str) -> str:
    """Return a Google Ads send_to value, or empty string when incomplete."""
    if not ads_id or not conversion_label:
        return ""
    return f"{ads_id}/{conversion_label}"


def build_signup_tracking_js(vertical: dict) -> str:
    """Build signup tracking helper with optional Google Ads conversion callback."""
    send_to = _ads_send_to(
        vertical.get("google_ads_id", ""),
        vertical.get("google_ads_signup_conversion_label", ""),
    )
    if not send_to:
        return """function trackSignupAndRedirect(doRedirect) {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'sign_up', {
                    method: 'email',
                    event_callback: doRedirect,
                    event_timeout: 2000
                });
            } else {
                doRedirect();
            }
        }"""
    return f"""function trackSignupAndRedirect(doRedirect) {{
            if (typeof gtag === 'undefined') {{
                doRedirect();
                return;
            }}
            let didRedirect = false;
            const redirectOnce = () => {{
                if (didRedirect) return;
                didRedirect = true;
                doRedirect();
            }};
            gtag('event', 'sign_up', {{ method: 'email' }});
            gtag('event', 'conversion', {{
                send_to: '{send_to}',
                event_callback: redirectOnce,
                event_timeout: 2000
            }});
            setTimeout(redirectOnce, 2200);
        }}"""


def build_checkout_tracking_js(vertical: dict) -> str:
    """Build checkout-start tracking helper with optional Google Ads conversion callback."""
    send_to = _ads_send_to(
        vertical.get("google_ads_id", ""),
        vertical.get("google_ads_checkout_conversion_label", ""),
    )
    if not send_to:
        return """function trackCheckoutStartAndRedirect(checkoutUrl, pack) {
            window.location.href = checkoutUrl;
        }"""
    return f"""function trackCheckoutStartAndRedirect(checkoutUrl, pack) {{
            if (typeof gtag === 'undefined') {{
                window.location.href = checkoutUrl;
                return;
            }}
            let didRedirect = false;
            const redirectOnce = () => {{
                if (didRedirect) return;
                didRedirect = true;
                window.location.href = checkoutUrl;
            }};
            gtag('event', 'begin_checkout', {{ product_id: PRODUCT_ID, pack: pack }});
            gtag('event', 'conversion', {{
                send_to: '{send_to}',
                event_callback: redirectOnce,
                event_timeout: 2000
            }});
            setTimeout(redirectOnce, 2200);
        }}"""


def build_purchase_tracking_js(vertical: dict) -> str:
    """Build purchase tracking helper with optional Google Ads conversion."""
    send_to = _ads_send_to(
        vertical.get("google_ads_id", ""),
        vertical.get("google_ads_purchase_conversion_label", ""),
    )
    if not send_to:
        return """function trackPurchaseIfConfigured(sessionId, data) {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'purchase', {
                    transaction_id: sessionId,
                    product_id: PRODUCT_ID,
                    credits: data.credits_purchased || 0
                });
            }
        }"""
    return f"""function trackPurchaseIfConfigured(sessionId, data) {{
            if (typeof gtag === 'undefined' || !sessionId) return;
            const storageKey = 'ads_purchase_tracked_' + PRODUCT_ID + '_' + sessionId;
            try {{
                if (sessionStorage.getItem(storageKey)) return;
                sessionStorage.setItem(storageKey, '1');
            }} catch (e) {{}}
            gtag('event', 'purchase', {{
                transaction_id: sessionId,
                product_id: PRODUCT_ID,
                credits: data.credits_purchased || 0
            }});
            gtag('event', 'conversion', {{
                send_to: '{send_to}',
                transaction_id: sessionId
            }});
        }}"""


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
    audience_short_early = target_audience_short(target_audience)
    # Build a clean occupation noun for the default headline
    _occ_raw = vertical.get("occupation", audience_short_early).lower()
    # Take just the first occupation term (before 'and' or comma)
    _occ_first = _occ_raw.split(',')[0].split(' and ')[0].strip()
    # Depluralize common patterns for headline readability
    if _occ_first.endswith('s') and not _occ_first.endswith('ss'):
        _occ_first = _occ_first.rstrip('s')
    # Trim overly long occupation phrases
    _occ_words = _occ_first.split()
    if len(_occ_words) > 3:
        _occ_first = ' '.join(_occ_words[:3])
    hero_h1 = vertical.get("hero_h1") or vertical.get("claude_your") or f"Your {_occ_first} paperwork. Done in minutes."
    # If hero_h1 ends with a complete sentence (period), use it as-is.
    # Otherwise append the brand tagline span.
    hero_h1_stripped = hero_h1.rstrip(".")
    if hero_h1.endswith(".") or vertical.get("hero_h1_no_span"):
        hero_h1_html = f"{hero_h1_stripped}."
    else:
        hero_h1_html = f"{hero_h1_stripped}.<br><span>No Prompt Engineering.</span>"
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
    ga_tag = build_ga_tag(vertical.get("ga_measurement_id", ""), vertical.get("google_ads_id", ""))

    # New optional fields
    pricing_tiers = vertical.get("pricing_tiers", [])
    pricing_cards = build_pricing_html(pricing_tiers, hero_count, show_tryit)

    demo_tasks = vertical.get("demo_tasks", [])
    # hero_demo_html kept for backward compat but no longer injected into pages
    hero_demo_html = ""  # Removed from template — demo animation replaced by YouTube/before-after
    _hero_demo_for_compat = build_hero_demo_html(demo_tasks, product_name, accent)  # kept but not used

    # Social proof and trust bar
    social_proof_html = build_social_proof_html(vertical)
    trust_bar_html = build_trust_bar_html(vertical)

    youtube_video_id = vertical.get("youtube_video_id", "")
    youtube_video_section = build_youtube_section(youtube_video_id, product_name)

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
        f"<strong>{hero_count} ready-to-use AI templates</strong> for {audience_short_early.lower()}. "
        f"Get professional output inside <strong>Claude Desktop</strong> (free app) \u2014 no prompt engineering, no learning curve. Just type what you need."
    )

    hero_fine_print_custom = vertical.get("hero_fine_print", "").strip()
    hero_fine_print_or_default = hero_fine_print_custom if hero_fine_print_custom else (
        "5 free credits on signup &nbsp;\u00b7&nbsp; Credits never expire &nbsp;\u00b7&nbsp; No subscription"
    )

    features_intro_custom = vertical.get("features_intro", "").strip()
    features_intro_or_default = features_intro_custom if features_intro_custom else f"Built for {audience_short}"

    features_subtitle_custom = vertical.get("features_subtitle", "").strip()
    features_subtitle_or_default = features_subtitle_custom if features_subtitle_custom else (
        f"Every task built for the real work {audience_short} do every day."
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
        "{{HERO_H1_HTML}}": hero_h1_html,
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
        "{{SIGNUP_TRACKING_JS}}": build_signup_tracking_js(vertical),
        "{{CHECKOUT_TRACKING_JS}}": build_checkout_tracking_js(vertical),
        "{{PURCHASE_TRACKING_JS}}": build_purchase_tracking_js(vertical),
        "{{TESTIMONIALS_SECTION}}": testimonials_section,
        "{{COMPLIANCE_SECTION}}": compliance_section,
        "{{PRICING_CARDS}}": pricing_cards,
        "{{HERO_DEMO_HTML}}": hero_demo_html,
        "{{YOUTUBE_VIDEO_SECTION}}": youtube_video_section,
        "{{SOCIAL_PROOF_HTML}}": social_proof_html,
        "{{TRUST_BAR_HTML}}": trust_bar_html,
    }

    for placeholder, value in replacements.items():
        page = page.replace(placeholder, value)

    # Waitlist mode: replace hero CTAs and pricing section for verticals without an installer
    if not vertical.get("has_installer", False):
        # Replace hero CTA button
        page = page.replace(
            '<a href="/signup" class="cta-button">Get My 5 Free Credits \u2192</a>',
            '<a href="/signup" class="cta-button">Join the Waitlist \u2014 Free</a>'
        )
        # Replace pricing section with waitlist CTA
        import re as _re
        page = _re.sub(
            r'<!-- ─── Pricing ─── -->.*?<!-- ─── Final CTA ─── -->',
            '''<!-- Waitlist CTA (replaces pricing for unreleased verticals) -->
    <section class="pricing" id="pricing" style="background:#f8fafc;">
        <div class="container" style="text-align:center;padding:60px 24px;">
            <h2 class="section-title" style="margin-bottom:16px;">''' + product_name + ''' is coming soon</h2>
            <p style="color:#6b7280;font-size:1rem;max-width:480px;margin:0 auto 32px;">We\'re putting the finishing touches on ''' + product_name + '''. Join the waitlist and be first to know when it launches \u2014 you\'ll get early access and a free trial.</p>
            <a href="/signup" style="display:inline-block;padding:14px 32px;background:var(--accent);color:white;border-radius:8px;font-weight:700;font-size:1rem;text-decoration:none;">Join the Waitlist &rarr;</a>
        </div>
    </section>

    <!-- ─── Final CTA ─── -->''',
            page,
            flags=_re.DOTALL
        )

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
                primary = v.get("primary_color", "#1a1a1a")
                background = v.get("background_color", "#FAFAFA")
                product_id = v.get("product_id", slug)
                hero_count = v.get("hero_count") or f"{v.get('skill_count', 200)}+"
                target_audience = v.get("target_audience") or v.get("audience", "professionals")
                show_tryit = v.get("show_tryit", True)
                pricing_tiers = v.get("pricing_tiers", [])
                pricing_cards = build_pricing_html(pricing_tiers, hero_count, show_tryit)
                disclaimer = v.get("api_cost_disclaimer", "")
                api_cost_disclaimer_bottom_text = disclaimer if disclaimer else ""
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
                    .replace("{{GA_TAG}}", build_ga_tag(v.get("ga_measurement_id", ""), v.get("google_ads_id", ""))) \
                    .replace("{{PURCHASE_TRACKING_JS}}", build_purchase_tracking_js(v))
                (out_dir / "success.html").write_text(success_page, encoding="utf-8")

            # Generate signup.html — use waitlist template for verticals without an installer
            has_installer = v.get("has_installer", False)
            if has_installer:
                signup_template_path = TEMPLATE_FILE.parent / "signup-template.html"
            else:
                signup_template_path = TEMPLATE_FILE.parent / "signup-waitlist-template.html"
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
                    .replace("{{SIGNUP_TRACKING_JS}}", build_signup_tracking_js(v)) \
                    .replace("{{PROFESSION}}", profession) \
                    .replace("{{PROFESSIONALS}}", professionals) \
                    .replace("{{ROLE_TITLE}}", role_title)
                (out_dir / "signup.html").write_text(signup_page, encoding="utf-8")

            # Generate install.html and getting-started.html from separate templates.
            install_template_path = TEMPLATE_FILE.parent / "install-template.html"
            getting_started_template_path = TEMPLATE_FILE.parent / "getting-started-template.html"
            if install_template_path.exists() and getting_started_template_path.exists():
                install_tmpl = install_template_path.read_text(encoding="utf-8")
                getting_started_tmpl = getting_started_template_path.read_text(encoding="utf-8")
                tasks_list = v.get("sample_tasks", [])
                example_task = tasks_list[0] if tasks_list else f"a {v.get('occupation', slug)} task"
                product_id_upper = product_id.upper() + "TASKSAI"
                installer_asset_name = v.get("installer_asset_name") or _installer_asset_name(product_name, product_id)
                repo_slug = domain.split(".")[0]
                install_page = install_tmpl \
                    .replace("{{PRODUCT_NAME}}", product_name) \
                    .replace("{{PRODUCT_NAME_SPLIT}}", logo_split) \
                    .replace("{{ACCENT_COLOR}}", accent) \
                    .replace("{{DOMAIN}}", domain) \
                    .replace("{{PRODUCT_ID}}", product_id) \
                    .replace("{{REPO_SLUG}}", repo_slug) \
                    .replace("{{PRODUCT_ID_UPPER}}", product_id_upper) \
                    .replace("{{INSTALLER_ASSET_NAME}}", installer_asset_name) \
                    .replace("{{LOGO_HTML}}", logo_split) \
                    .replace("{{EXAMPLE_TASK}}", example_task) \
                    .replace("{{GA_TAG}}", build_ga_tag(v.get("ga_measurement_id", ""), v.get("google_ads_id", "")))
                getting_started_page = getting_started_tmpl \
                    .replace("{{PRODUCT_NAME}}", product_name) \
                    .replace("{{PRODUCT_NAME_SPLIT}}", logo_split) \
                    .replace("{{ACCENT_COLOR}}", accent) \
                    .replace("{{DOMAIN}}", domain) \
                    .replace("{{PRODUCT_ID}}", product_id) \
                    .replace("{{REPO_SLUG}}", repo_slug) \
                    .replace("{{PRODUCT_ID_UPPER}}", product_id_upper) \
                    .replace("{{INSTALLER_ASSET_NAME}}", installer_asset_name) \
                    .replace("{{LOGO_HTML}}", logo_split) \
                    .replace("{{EXAMPLE_TASK}}", example_task) \
                    .replace("{{GA_TAG}}", build_ga_tag(v.get("ga_measurement_id", ""), v.get("google_ads_id", "")))
                (out_dir / "install.html").write_text(install_page, encoding="utf-8")
                (out_dir / "getting-started.html").write_text(getting_started_page, encoding="utf-8")

            # Generate connect.html (browser MCP approval)
            connect_template_path = TEMPLATE_FILE.parent / "connect-template.html"
            if connect_template_path.exists():
                connect_tmpl = connect_template_path.read_text(encoding="utf-8")
                repo_slug = domain.split(".")[0]
                connect_page = connect_tmpl \
                    .replace("{{PRODUCT_NAME}}", product_name) \
                    .replace("{{ACCENT_COLOR}}", accent) \
                    .replace("{{DOMAIN}}", domain) \
                    .replace("{{PRODUCT_ID}}", product_id) \
                    .replace("{{REPO_SLUG}}", repo_slug) \
                    .replace("{{GA_TAG}}", build_ga_tag(v.get("ga_measurement_id", ""), v.get("google_ads_id", "")))
                (out_dir / "connect.html").write_text(connect_page, encoding="utf-8")

            # Generate download.html (account portal)
            dl_template_path = TEMPLATE_FILE.parent / "download-template.html"
            if dl_template_path.exists():
                dl_tmpl = dl_template_path.read_text(encoding="utf-8")
                # Derive license key prefix from product_id
                prefix_map = {
                    "law": "lt_", "realtor": "rt_", "farmer": "ft_", "teacher": "tt_",
                    "therapist": "th_", "marketing": "mt_", "contractor": "ct_",
                    "accounting": "at_", "chiropractor": "ch_", "church": "cu_",
                    "dentist": "dt_", "designer": "ds_", "electrician": "el_",
                    "eventplanner": "ep_", "funeral": "fu_", "hr": "hr_",
                    "insurance": "in_", "landlord": "ll_", "militaryspouse": "ms_",
                    "mortgage": "mo_", "mortuary": "mu_", "nutritionist": "nt_",
                    "pastor": "pt_", "personaltrainer": "pp_", "plumber": "pl_",
                    "principal": "pr_", "restaurant": "re_", "salon": "sl_",
                    "travelagent": "ta_", "vet": "vt_",
                }
                lic_prefix = prefix_map.get(product_id, product_id[:2] + "_")
                dl_page = dl_tmpl \
                    .replace("{{PRODUCT_NAME}}", product_name) \
                    .replace("{{PRODUCT_ID}}", product_id) \
                    .replace("{{ACCENT_COLOR}}", accent) \
                    .replace("{{DOMAIN}}", domain) \
                    .replace("{{LICENSE_KEY_PREFIX}}", lic_prefix) \
                    .replace("{{GA_TAG}}", build_ga_tag(v.get("ga_measurement_id", ""), v.get("google_ads_id", "")))
                (out_dir / "download.html").write_text(dl_page, encoding="utf-8")

            # Generate header.js
            header_template_path = TEMPLATE_FILE.parent / "header-template.js"
            if header_template_path.exists():
                header_tmpl = header_template_path.read_text(encoding="utf-8")
                header_js = header_tmpl \
                    .replace("{{PRODUCT_NAME}}", product_name) \
                    .replace("{{LOGO_HTML}}", logo_split) \
                    .replace("{{ACCENT_COLOR}}", accent) \
                    .replace("{{DOMAIN}}", domain)
                (out_dir / "header.js").write_text(header_js, encoding="utf-8")

            # Generate terms, privacy, support, verified_safe pages
            occupation = v.get("occupation", v.get("audience", slug))
            for tmpl_name, out_name in [
                ("terms-template.html", "terms.html"),
                ("privacy-template.html", "privacy.html"),
                ("support-template.html", "support.html"),
                ("verified-safe-template.html", "verified_safe.html"),
                ("faq-template.html", "faq.html"),
                ("buy-credits-template.html", "buy-credits.html"),
                ("feedback-thanks-template.html", "feedback-thanks.html"),
                ("unsubscribe-template.html", "unsubscribe.html"),
            ]:
                tmpl_path = TEMPLATE_FILE.parent / tmpl_name
                if tmpl_path.exists():
                    tmpl_content = tmpl_path.read_text(encoding="utf-8")
                    support_email = v.get("support_email", f"hello@{domain}")
                    audience = v.get("audience", occupation)
                    footer_html = (
                        f'<footer style="background:#0f172a;color:#94a3b8;padding:48px 24px 32px;margin-top:60px;">'
                        f'<div style="max-width:900px;margin:0 auto;">'
                        f'<p style="font-size:0.82rem;color:#64748b;border:1px solid #1e293b;border-radius:8px;padding:12px 16px;margin-bottom:32px;">'
                        f'&#9888; <strong style="color:#94a3b8;">Not Professional Advice</strong> &mdash; '
                        f'{product_name} is software that assists {audience} with administrative work. '
                        f'It is not a licensed professional service and does not provide professional advice. '
                        f'Always apply your own professional review and judgment. Laudo Lux, LLC.</p>'
                        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:24px;margin-bottom:32px;">'
                        f'<div><a href="/index.html" style="font-size:1.1rem;font-weight:800;color:#fff;text-decoration:none;letter-spacing:-0.02em;">{logo_split}</a>'
                        f'<p style="margin-top:8px;font-size:0.88rem;">AI-powered workflows for {audience}.</p></div>'
                        f'<div style="display:flex;flex-direction:column;gap:10px;">'
                        f'<a href="/index.html" style="color:#94a3b8;text-decoration:none;font-size:0.9rem;">Home</a>'
                        f'<a href="/verified_safe.html" style="color:#94a3b8;text-decoration:none;font-size:0.9rem;">Verified Safe</a>'
                        f'<a href="mailto:{support_email}" style="color:#94a3b8;text-decoration:none;font-size:0.9rem;">{support_email}</a>'
                        f'</div></div>'
                        f'<div style="border-top:1px solid #1e293b;padding-top:20px;font-size:0.82rem;color:#475569;">'
                        f'&copy; 2026 Laudo Lux, LLC &nbsp;&middot;&nbsp; <a href="mailto:{support_email}" style="color:#475569;">{support_email}</a>'
                        f'</div></div></footer>'
                    )
                    # Build first_prompt from sample_tasks
                    _tasks_list = v.get("sample_tasks", [])
                    _first_task = _tasks_list[0] if _tasks_list else f"a {occupation} task"
                    _first_task_name = _first_task if isinstance(_first_task, str) else str(_first_task)
                    _first_prompt = f'I need help with {_first_task_name}'
                    _skill_count = str(v.get("skill_count", v.get("hero_count", "200+")))
                    # Darken accent by appending opacity for dark variant (simple approach)
                    _accent_dark = v.get("accent_color_dark", accent)
                    _api_base = v.get("api_base", "https://api.lawtasksai.com")
                    rendered = tmpl_content \
                        .replace("{{PRODUCT_NAME}}", product_name) \
                        .replace("{{PRODUCT_NAME_SPLIT}}", logo_split) \
                        .replace("{{PRIMARY_COLOR}}", primary) \
                        .replace("{{ACCENT_COLOR}}", accent) \
                        .replace("{{ACCENT_COLOR_DARK}}", _accent_dark) \
                        .replace("{{BACKGROUND_COLOR}}", background) \
                        .replace("{{DOMAIN}}", domain) \
                        .replace("{{PRODUCT_ID}}", product_id) \
                        .replace("{{PRODUCT_SLUG}}", slug) \
                        .replace("{{OCCUPATION}}", occupation) \
                        .replace("{{SUPPORT_EMAIL}}", support_email) \
                        .replace("{{LOGO_HTML}}", logo_split) \
                        .replace("{{LOGO_HTML_FOOTER}}", logo_split) \
                        .replace("{{NAME}}", product_name) \
                        .replace("{{HERO_COUNT}}", hero_count) \
                        .replace("{{SKILL_COUNT}}", _skill_count) \
                        .replace("{{FIRST_PROMPT}}", _first_prompt) \
                        .replace("{{EXAMPLE_TASK}}", _first_task_name) \
                        .replace("{{TARGET_AUDIENCE}}", target_audience) \
                        .replace("{{PRICING_CARDS}}", pricing_cards) \
                        .replace("{{API_COST_DISCLAIMER_BOTTOM_TEXT}}", api_cost_disclaimer_bottom_text) \
                        .replace("{{API_BASE}}", _api_base) \
                        .replace("{{FOOTER}}", footer_html) \
                        .replace("{{GA_TAG}}", build_ga_tag(v.get("ga_measurement_id", ""), v.get("google_ads_id", ""))) \
                        .replace("{{CHECKOUT_TRACKING_JS}}", build_checkout_tracking_js(v))
                    (out_dir / out_name).write_text(rendered, encoding="utf-8")

            # ── Blog posts ────────────────────────────────────────────────────
            blog_templates = [
                ("blog-prefix-template.html",      f"use-{product_id}tasksai-to-the-phrase-that-unlocks-everything.html"),
                ("blog-permissions-template.html", f"{product_id}tasksai-permissions-always-allow.html"),
            ]
            for blog_tmpl_name, blog_out_name in blog_templates:
                blog_tmpl_path = TEMPLATE_FILE.parent / blog_tmpl_name
                if not blog_tmpl_path.exists():
                    continue
                blog_dir = out_dir / "blog"
                blog_dir.mkdir(exist_ok=True)
                blog_content = blog_tmpl_path.read_text(encoding="utf-8")
                # Build prefixed example chips for the prefix post
                _tasks_list = v.get("sample_tasks", [])
                _prefixed_chips = "".join(
                    f'<div class="example-item"><span class="prefix">Use {{{{PRODUCT_NAME}}}} to</span> {t}</div>'
                    for t in _tasks_list[:5]
                ).replace("{{PRODUCT_NAME}}", product_name)
                example_task = _tasks_list[0] if _tasks_list else f"help me with a {occupation} task"
                _support_email = v.get("support_email", f"hello@{domain}")
                rendered_blog = blog_content \
                    .replace("{{PRODUCT_NAME}}", product_name) \
                    .replace("{{PRODUCT_ID}}", product_id) \
                    .replace("{{ACCENT_COLOR}}", accent) \
                    .replace("{{DOMAIN}}", domain) \
                    .replace("{{HERO_COUNT}}", hero_count) \
                    .replace("{{TARGET_AUDIENCE}}", target_audience) \
                    .replace("{{OCCUPATION}}", occupation) \
                    .replace("{{SUPPORT_EMAIL}}", _support_email) \
                    .replace("{{EXAMPLE_TASK}}", example_task) \
                    .replace("{{EXAMPLE_TASK_CHIPS_PREFIXED}}", _prefixed_chips) \
                    .replace("{{GA_TAG}}", build_ga_tag(v.get("ga_measurement_id", ""), v.get("google_ads_id", "")))
                (blog_dir / blog_out_name).write_text(rendered_blog, encoding="utf-8")

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
