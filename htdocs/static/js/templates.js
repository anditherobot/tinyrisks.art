// TinyRisks.art - Template Inheritance System
// Base templates and layout components

// Base HTML Layout - all pages inherit from this
const baseLayout = {
  styles: `
    :root{
      --bg:#0f1115;
      --ink:#e8e5e0;
      --muted:#a7a39a;
      --accent:#d6a76c;
      --accent2:#00ffff;
      --line:#2a2e37;
      --card:#151922;
      --success:#4caf50;
      --error:#f44336;
    }
    [data-theme="cyan"] {
      --accent:#00ffff;
      --accent2:#d6a76c;
    }
    html,body{height:100%;scroll-behavior:smooth}
    body{
      margin:0; color:var(--ink); background:
        linear-gradient(90deg, transparent 0 49px, var(--line) 49px 50px, transparent 50px) repeat-x,
        linear-gradient(0deg,  transparent 0 49px, var(--line) 49px 50px, transparent 50px) repeat-y,
        linear-gradient(180deg, #0f1115, #121522);
      background-size: 50px 100%, 100% 50px, auto;
      font: 16px/1.6 ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
    }
    .container{max-width:1200px;margin:0 auto;padding:clamp(16px,3vw,48px)}

    /* Header */
    header{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;padding:clamp(16px,3vw,32px) clamp(16px,3vw,48px);position:relative}
    .mark{display:grid;place-items:center;width:56px;height:56px;border:1px solid var(--accent);position:relative}
    .mark:before,.mark:after{content:"";position:absolute;background:var(--accent)}
    .mark:before{width:70%;height:1px}
    .mark:after{height:70%;width:1px}
    .brand{letter-spacing:.2em;text-transform:uppercase;color:var(--muted);font-size:.85rem}
    nav ul{display:flex;gap:24px;list-style:none;padding:0;margin:0}
    nav a{color:var(--ink);text-decoration:none;transition:color .2s}
    nav a:hover{color:var(--accent)}
    .theme-toggle{background:transparent;border:1px solid var(--line);color:var(--accent);padding:8px 16px;cursor:pointer;font-size:.85rem;transition:all .2s}
    .theme-toggle:hover{border-color:var(--accent);background:rgba(214,167,108,.1)}

    /* Grid */
    .grid{display:grid;grid-template-columns:repeat(12,1fr);gap:clamp(12px,2vw,24px);margin:4rem 0}
    .section-title{grid-column:1/-1;font:700 1.8rem ui-serif,Georgia,serif;color:var(--accent);text-transform:uppercase;letter-spacing:.15em;margin:3rem 0 1rem;border-bottom:1px solid var(--line);padding-bottom:.5rem}

    /* Work cards */
    .work-card{
      grid-column:span 4;
      background:linear-gradient(180deg, var(--card), #0e1219);
      border:1px solid var(--line);
      padding:clamp(20px,3vw,32px);
      transition:all .3s ease;
      position:relative;
      overflow:hidden;
    }
    .work-card:before{
      content:"";
      position:absolute;
      top:0;left:0;
      width:100%;
      height:3px;
      background:var(--accent);
      transform:scaleX(0);
      transform-origin:left;
      transition:transform .3s;
    }
    .work-card:hover{transform:translateY(-4px);border-color:var(--accent)}
    .work-card:hover:before{transform:scaleX(1)}
    .work-meta{color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:.5rem}
    .work-card h3{font:600 1.4rem ui-serif,Georgia,serif;color:var(--ink);margin:.5rem 0}
    .work-card p{color:var(--muted);font-size:.95rem;line-height:1.6}
    .tag{background:var(--card);border:1px solid var(--line);padding:6px 12px;font-size:.85rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}

    .btn{
      display:inline-block;
      padding:12px 28px;
      background:transparent;
      border:2px solid var(--accent);
      color:var(--accent);
      text-decoration:none;
      text-transform:uppercase;
      letter-spacing:.12em;
      font-size:.85rem;
      font-weight:600;
      cursor:pointer;
      font-family:inherit;
      transition:all .3s;
    }
    .btn:hover{
      background:var(--accent);
      color:var(--bg);
      transform:translateY(-2px);
    }

    /* Footer */
    footer{margin-top:4rem;padding:2rem 0;border-top:1px solid var(--line);text-align:center;color:var(--muted);font-size:.9rem}

    /* Responsive */
    @media (max-width: 900px){
      .work-card{grid-column:span 6}
      nav ul{gap:16px;font-size:.9rem;flex-wrap:wrap}
    }
    @media (max-width: 640px){
      .work-card{grid-column:span 12}
    }
  `,

  header: (subtitle = 'Art Studio') => `
    <header>
      <div style="display:flex;align-items:center;gap:14px">
        <div class="mark"></div>
        <div>
          <div class="brand">TinyRisks</div>
          <div style="font-weight:600;color:var(--ink);font-size:.9rem">${subtitle}</div>
        </div>
      </div>
      <nav>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/#work">Work</a></li>
          <li><a href="/poseidon.html">Poseidon</a></li>
          <li><a href="/writing.html">Writing</a></li>
          <li><a href="/#contact">Contact</a></li>
          <li><button class="theme-toggle" onclick="toggleTheme()">Brass/Cyan</button></li>
        </ul>
      </nav>
    </header>
  `,

  footer: (text = 'TinyRisks.art — Built with semantic HTML + simple CSS.') => `
    <footer>
      <p>© <span class="year"></span> ${text}</p>
    </footer>
  `,

  scripts: `
    <script src="/components.js"></script>
    <script>
      // Set year
      document.querySelectorAll('.year').forEach(el => {
        el.textContent = new Date().getFullYear();
      });

      // Theme toggle
      function toggleTheme() {
        const body = document.body;
        const current = body.getAttribute('data-theme');
        body.setAttribute('data-theme', current === 'brass' ? 'cyan' : 'brass');
      }
    </script>
  `
};

// Template renderer
function renderTemplate({ title, subtitle, extraStyles = '', content, extraScripts = '' }) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${title} | TinyRisks.art</title>
  <style>
    ${baseLayout.styles}
    ${extraStyles}
  </style>
</head>
<body data-theme="brass">
  ${baseLayout.header(subtitle)}

  ${content}

  ${baseLayout.footer()}
  ${baseLayout.scripts}
  ${extraScripts}
</body>
</html>`;
}

// Hero template (used by homepage and writing page)
function heroTemplate({ kicker, title, poem, ctaText, ctaHref, backgroundImage }) {
  return `
    <section class="hero">
      <div class="hero-image" style="background-image: url('${backgroundImage}')"></div>
      <div class="hero-content">
        <div class="kicker">${kicker}</div>
        <h1>${title}</h1>
        ${poem ? `
          <div class="poem">
            ${poem.map(line => `<p>${line}</p>`).join('')}
          </div>
        ` : ''}
        ${ctaText ? `<a href="${ctaHref}" class="cta">${ctaText}</a>` : ''}
      </div>
    </section>
  `;
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { renderTemplate, heroTemplate, baseLayout };
}
