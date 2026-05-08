(function () {
  var PRODUCT_NAME = "TeacherTasksAI";
  var LOGO_HTML = "Teacher<span>TasksAI</span>";
  var ACCENT = "#0D9488";
  var DOMAIN = "teachertasksai.com";

  /* ── CSS ── */
  var style = document.createElement("style");
  style.textContent = [
    "/* ── TasksAI Site Header ── */",
    "#site-header header {",
    "  background: #fff;",
    "  border-bottom: 1px solid #e5e7eb;",
    "  position: sticky;",
    "  top: 0;",
    "  z-index: 200;",
    "  padding: 0;",
    "}",
    "#site-header .sh-inner {",
    "  max-width: 1100px;",
    "  margin: 0 auto;",
    "  padding: 0 24px;",
    "  display: flex;",
    "  justify-content: space-between;",
    "  align-items: center;",
    "  height: 64px;",
    "}",
    "#site-header .sh-logo {",
    "  font-size: 1.35rem;",
    "  font-weight: 800;",
    "  color: #0f172a;",
    "  text-decoration: none;",
    "  letter-spacing: -0.02em;",
    "  flex-shrink: 0;",
    "}",
    "#site-header .sh-logo span { color: " + ACCENT + "; }",
    "#site-header .sh-nav {",
    "  display: flex;",
    "  align-items: center;",
    "  gap: 4px;",
    "}",
    "#site-header .sh-nav a {",
    "  color: #4b5563;",
    "  text-decoration: none;",
    "  font-size: 0.9rem;",
    "  font-weight: 500;",
    "  padding: 6px 12px;",
    "  border-radius: 6px;",
    "  transition: color 0.15s, background 0.15s;",
    "}",
    "#site-header .sh-nav a:hover { color: #111; background: #f3f4f6; }",
    "#site-header .sh-nav a.sh-cta {",
    "  background: " + ACCENT + ";",
    "  color: #fff !important;",
    "  font-weight: 600;",
    "  padding: 8px 18px;",
    "  border-radius: 7px;",
    "  margin-left: 8px;",
    "}",
    "#site-header .sh-nav a.sh-cta:hover { opacity: 0.88; background: " + ACCENT + "; }",
    "#site-header .sh-nav a.sh-active { color: " + ACCENT + "; font-weight: 600; }",
    /* Hamburger */
    "#site-header .sh-hamburger {",
    "  display: none;",
    "  background: none;",
    "  border: none;",
    "  cursor: pointer;",
    "  padding: 8px;",
    "  flex-direction: column;",
    "  gap: 5px;",
    "  z-index: 201;",
    "}",
    "#site-header .sh-hamburger span {",
    "  display: block;",
    "  width: 22px;",
    "  height: 2px;",
    "  background: #374151;",
    "  border-radius: 2px;",
    "  transition: all 0.25s;",
    "}",
    "#site-header .sh-overlay {",
    "  display: none;",
    "  position: fixed;",
    "  inset: 0;",
    "  background: rgba(0,0,0,0.35);",
    "  z-index: 199;",
    "}",
    /* Mobile */
    "@media (max-width: 768px) {",
    "  #site-header .sh-hamburger { display: flex; }",
    "  #site-header .sh-nav {",
    "    display: none;",
    "    position: fixed;",
    "    top: 0; right: 0;",
    "    width: 280px;",
    "    height: 100vh;",
    "    background: #fff;",
    "    flex-direction: column;",
    "    align-items: flex-start;",
    "    padding: 80px 28px 32px;",
    "    gap: 0;",
    "    box-shadow: -4px 0 24px rgba(0,0,0,0.12);",
    "    z-index: 200;",
    "    overflow-y: auto;",
    "  }",
    "  #site-header .sh-nav.sh-open { display: flex; }",
    "  #site-header .sh-overlay.sh-open { display: block; }",
    "  #site-header .sh-nav a {",
    "    padding: 14px 4px;",
    "    font-size: 1.05rem;",
    "    border-bottom: 1px solid #f3f4f6;",
    "    width: 100%;",
    "    border-radius: 0;",
    "  }",
    "  #site-header .sh-nav a.sh-cta {",
    "    margin-left: 0;",
    "    margin-top: 16px;",
    "    text-align: center;",
    "    border-radius: 7px;",
    "  }",
    "}"
  ].join("\n");
  document.head.appendChild(style);

  /* ── Mark active nav link based on current path ── */
  function getActiveHref() {
    var p = window.location.pathname.replace(/\/$/, "") || "/";
    if (p === "" || p === "/" || p.endsWith("/index.html")) return "/";
    if (p.indexOf("task-library") > -1) return "/task-library.html";
    if (p.indexOf("getting-started") > -1) return "/getting-started.html";
    if (p.indexOf("verified_safe") > -1) return "/verified_safe.html";
    if (p.indexOf("faq") > -1) return "/faq.html";
    if (p.indexOf("support") > -1) return "/support.html";
    if (p.indexOf("signup") > -1) return "/signup.html";
    return "";
  }

  /* ── Build HTML ── */
  var activeHref = getActiveHref();
  var navItems = [
    { href: "/",                    label: "Home" },
    { href: "/task-library.html",   label: "Task Library" },
    { href: "/getting-started.html",label: "Getting Started" },
    { href: "/verified_safe.html",  label: "🛡️ Verified Safe" },
    { href: "/faq.html",            label: "FAQ" },
    { href: "/support.html",        label: "Support" },
  ];

  var navHTML = navItems.map(function (item) {
    var cls = (item.href === activeHref) ? ' class="sh-active"' : '';
    return '<a href="' + item.href + '"' + cls + '>' + item.label + '</a>';
  }).join("\n        ");

  var html = [
    '<header>',
    '  <div class="sh-inner">',
    '    <a href="/" class="sh-logo">' + LOGO_HTML + '</a>',
    '    <nav class="sh-nav" id="shNav">',
    '      ' + navHTML,
    '      <a href="/signup.html" class="sh-cta">Try Free</a>',
    '    </nav>',
    '    <button class="sh-hamburger" id="shHamburger" aria-label="Menu" aria-expanded="false">',
    '      <span></span><span></span><span></span>',
    '    </button>',
    '    <div class="sh-overlay" id="shOverlay"></div>',
    '  </div>',
    '</header>'
  ].join("\n");

  var el = document.getElementById("site-header");
  if (el) el.innerHTML = html;

  /* ── Hamburger toggle ── */
  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("shHamburger");
    var nav = document.getElementById("shNav");
    var overlay = document.getElementById("shOverlay");
    if (!btn || !nav) return;

    function openMenu() {
      nav.classList.add("sh-open");
      overlay.classList.add("sh-open");
      btn.setAttribute("aria-expanded", "true");
      document.body.style.overflow = "hidden";
    }
    function closeMenu() {
      nav.classList.remove("sh-open");
      overlay.classList.remove("sh-open");
      btn.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
    }

    btn.addEventListener("click", function () {
      nav.classList.contains("sh-open") ? closeMenu() : openMenu();
    });
    overlay.addEventListener("click", closeMenu);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeMenu();
    });
  });
})();
