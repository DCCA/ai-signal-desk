const grid = document.querySelector('[data-digest-grid]');
const filters = document.querySelectorAll('[data-filter]');
let items = [];

const labelClass = {
  concept: 'blue',
  product: 'pink',
  repo: 'red',
  workflow: 'dark',
};

function renderCards(filter = 'all') {
  const visible = filter === 'all' ? items : items.filter((item) => item.category === filter);
  grid.innerHTML = visible
    .map(
      (item) => `
        <article class="card digest-card">
          <div class="meta">
            <span class="pill ${labelClass[item.category] || 'blue'}">${item.category}</span>
            <span class="status">${item.status}</span>
          </div>
          <h3>${item.title}</h3>
          <p>${item.summary}</p>
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
    grid.innerHTML = '<p class="card compact">Could not load digest cards locally. Run a static server from the repo root.</p>';
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
