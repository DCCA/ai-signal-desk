const grid = document.querySelector('[data-digest-grid]');
const filters = document.querySelectorAll('[data-filter]');
let items = [];

const labelClass = {
  concept: 'concept',
  product: 'product',
  repo: 'repo',
  workflow: 'workflow',
};

function scoreFor(item, key, fallback) {
  return item[key] || fallback;
}

function renderCards(filter = 'all') {
  const visible = filter === 'all' ? items : items.filter((item) => item.category === filter);
  grid.innerHTML = visible
    .map(
      (item, index) => `
        <article class="digest-card">
          <div class="meta">
            <span class="pill ${labelClass[item.category] || 'concept'}">${String(index + 1).padStart(2, '0')} / ${item.category}</span>
            <span class="status">${item.status}</span>
          </div>
          <h3>${item.title}</h3>
          <p>${item.summary}</p>
          <div class="scoreboard" aria-label="Signal and hype scores">
            <span>Signal <strong>${scoreFor(item, 'signal_score', 80)}</strong></span>
            <span>Hype <strong>${scoreFor(item, 'hype_score', 25)}</strong></span>
          </div>
          <p><strong>Why it matters:</strong> ${item.why_it_matters}</p>
          <p class="try-this"><strong>Try this:</strong> ${item.try_this}</p>
        </article>
      `
    )
    .join('');
}

async function loadDigest() {
  try {
    const response = await fetch('content/digest.json');
    const data = await response.json();
    items = data.items || [];
    renderCards();
  } catch (error) {
    grid.innerHTML = '<p class="digest-card">Could not load digest cards locally. Run a static server from the repo root.</p>';
  }
}

filters.forEach((button) => {
  button.addEventListener('click', () => {
    filters.forEach((candidate) => candidate.classList.remove('active'));
    button.classList.add('active');
    renderCards(button.dataset.filter);
  });
});

loadDigest();
