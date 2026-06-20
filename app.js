const grid = document.querySelector('[data-digest-grid]');
const filters = document.querySelectorAll('[data-filter]');
let items = [];

const labelClass = {
  concept: 'concept',
  product: 'product',
  repo: 'repo',
  workflow: 'workflow',
};

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function escapeAttr(value) {
  return escapeHtml(value).replaceAll('`', '&#96;');
}

// Only allow http(s)/mailto absolute URLs or same-origin relative paths. Any
// other scheme (javascript:, data:, vbscript:, ...) is rejected so that
// automated or ingested digest content cannot inject an active-content link.
function safeUrl(value) {
  const url = String(value ?? '').trim();
  if (/^(https?:|mailto:)/i.test(url)) return url;
  if (/^[a-z][a-z0-9+.-]*:/i.test(url)) return '';
  return url;
}

function cardTitle(item) {
  const title = escapeHtml(item.title);
  const href = safeUrl(item.post_url);
  return href ? `<a href="${escapeAttr(href)}">${title}</a>` : title;
}

function sourceLine(item) {
  const href = safeUrl(item.source_url);
  if (!href) return '';
  return `<p class="source-line"><strong>Source:</strong> <a href="${escapeAttr(href)}">${escapeHtml(item.source_label)}</a> - confidence: ${escapeHtml(item.confidence)}</p>`;
}

function scoreFor(item, key, fallback) {
  return item[key] || fallback;
}

function renderCards(filter = 'all') {
  const visible = filter === 'all' ? items : items.filter((item) => item.category === filter);
  if (!visible.length) {
    grid.innerHTML = '<p class="digest-card">No signals in this category yet.</p>';
    return;
  }
  grid.innerHTML = visible
    .map((item) => {
      // Number from the item's position in the full list so the index stays
      // stable when filters change.
      const number = items.indexOf(item) + 1;
      return `
        <article class="digest-card">
          <div class="meta">
            <span class="pill ${labelClass[item.category] || 'concept'}">${String(number).padStart(2, '0')} / ${escapeHtml(item.category)}</span>
            <span class="status">${escapeHtml(item.status)}</span>
          </div>
          <h3>${cardTitle(item)}</h3>
          <p>${escapeHtml(item.summary)}</p>
          <div class="scoreboard" aria-label="Signal and hype scores">
            <span>Signal <strong>${escapeHtml(scoreFor(item, 'signal_score', 80))}</strong></span>
            <span>Hype <strong>${escapeHtml(scoreFor(item, 'hype_score', 25))}</strong></span>
          </div>
          <p><strong>Why it matters:</strong> ${escapeHtml(item.why_it_matters)}</p>
          ${sourceLine(item)}
          <p class="try-this"><strong>Try this:</strong> ${escapeHtml(item.try_this)}</p>
        </article>
      `;
    })
    .join('');
}

function applyMeta(data) {
  const tagline = document.querySelector('[data-tagline]');
  if (tagline && data.tagline) {
    tagline.textContent = data.tagline;
  }
  const updated = document.querySelector('[data-updated]');
  if (updated && data.updated) {
    updated.textContent = `Updated ${data.updated}`;
    updated.hidden = false;
  }
}

async function loadDigest() {
  try {
    const response = await fetch('content/digest.json');
    const data = await response.json();
    items = data.items || [];
    applyMeta(data);
    renderCards();
  } catch (error) {
    grid.innerHTML = '<p class="digest-card">Could not load digest cards locally. Run a static server from the repo root.</p>';
  }
}

filters.forEach((button) => {
  button.addEventListener('click', () => {
    filters.forEach((candidate) => {
      candidate.classList.remove('active');
      candidate.setAttribute('aria-pressed', 'false');
    });
    button.classList.add('active');
    button.setAttribute('aria-pressed', 'true');
    renderCards(button.dataset.filter);
  });
});

loadDigest();
