// TinyRisks.art - Reusable Components
// Shared UI components across all pages

// Hero Component
function createHero({ kicker, title, poem, ctaText, ctaHref, backgroundImage }) {
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

// Work Card Component
function createWorkCard({ meta, title, description, link, image, imageAlt, imageCaption, tags, content }) {
  return `
    <article class="work-card">
      ${image ? `
        <figure style="margin:0 0 16px;border:1px solid var(--line);background:var(--card);overflow:hidden">
          <img src="${image}" alt="${imageAlt || title}" style="display:block;width:100%;height:auto" />
          ${imageCaption ? `
            <figcaption style="padding:12px 14px;color:var(--muted);font-size:.9rem;border-top:1px solid var(--line);font-style:italic">
              ${imageCaption}
            </figcaption>
          ` : ''}
        </figure>
      ` : ''}

      <div class="work-meta">${meta}</div>
      <h3>${title}</h3>
      ${description ? `<p>${description}</p>` : ''}
      ${content ? content : ''}

      ${tags && tags.length > 0 ? `
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:1rem">
          ${tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
        </div>
      ` : ''}

      ${link ? `<a href="${link}" style="color:var(--accent);text-decoration:none;margin-top:.5rem;display:inline-block;font-size:.85rem">View →</a>` : ''}
    </article>
  `;
}

// Post Card Component (for writing/blog)
function createPostCard({ index, title, content, tags, createdAt }) {
  const date = new Date(createdAt).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });

  return `
    <article class="work-card" style="grid-column:span 12">
      <span class="work-meta">${String(index).padStart(3, '0')} · ${date}</span>
      <h3>${title}</h3>
      <p style="color:var(--muted);margin:10px 0;line-height:1.8;white-space:pre-wrap">${content}</p>
      ${tags && tags.length > 0 ? `
        <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:1rem">
          ${tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
        </div>
      ` : ''}
    </article>
  `;
}

// Header Component
function createHeader({ brand = 'TinyRisks', subtitle = 'Art Studio' }) {
  return `
    <header>
      <div style="display:flex;align-items:center;gap:14px">
        <div class="mark"></div>
        <div>
          <div class="brand">${brand}</div>
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
          <li><button class="theme-toggle" onclick="toggleTheme()">Theme</button></li>
        </ul>
      </nav>
    </header>
  `;
}

// Footer Component
function createFooter({ year = new Date().getFullYear(), text = 'TinyRisks.art — Built with semantic HTML + simple CSS.' }) {
  return `
    <footer>
      <p>© ${year} ${text}</p>
    </footer>
  `;
}

// Theme Toggle Function (shared across all pages)
function toggleTheme() {
  const body = document.body;
  const current = body.getAttribute('data-theme');
  const themes = ['brass', 'cyan', 'light'];
  const currentIndex = themes.indexOf(current);
  const nextIndex = (currentIndex + 1) % themes.length;
  body.setAttribute('data-theme', themes[nextIndex]);
}

// Work Listing Component - renders multiple work cards
function createWorkListing(items) {
  return items.map(item => createWorkCard(item)).join('');
}

// Featured Gallery Carousel
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('carousel-container');
  if (!container) return;

  const prevBtn = document.getElementById('carousel-prev');
  const nextBtn = document.getElementById('carousel-next');

  const scrollAmount = () => container.querySelector('.carousel-item').offsetWidth * 0.8;

  prevBtn.addEventListener('click', () => {
    container.scrollBy({ left: -scrollAmount(), behavior: 'smooth' });
  });

  nextBtn.addEventListener('click', () => {
    container.scrollBy({ left: scrollAmount(), behavior: 'smooth' });
  });
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    createHero,
    createWorkCard,
    createPostCard,
    createHeader,
    createFooter,
    createWorkListing,
    toggleTheme
  };
}