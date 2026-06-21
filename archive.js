/* AI Signal Desk — the archive.
   Renders every signal card grouped by calendar week (Monday start), newest
   week first, with a category filter and free-text search. Date is the spine;
   there is deliberately no sort control. Cards are built by the shared
   SignalDesk.buildCard (DOM API only, no innerHTML), so the strict CSP holds.
   Deep-link contract: ?filter=<category> and ?q=<text> mirror the old home grid.
   Data: content/digest.json -> { tagline, updated, items: Signal[] }. */
(function () {
  var SD = window.SignalDesk;
  var mount = document.querySelector('[data-archive]');
  if (!mount || !SD) return;

  var chipsEl = document.querySelector('[data-filters]');
  var searchEl = document.querySelector('[data-search]');
  var countEl = document.querySelector('[data-results-count]');

  var CATEGORIES = SD.CATEGORIES; // ['concept','product','repo','workflow']
  var FILTER_DEFS = [
    ['all', 'All'], ['concept', 'Concepts'], ['product', 'Products'],
    ['repo', 'Repos'], ['workflow', 'Workflows']
  ];

  var items = [];
  var state = { filter: 'all', query: '' };

  // ---- URL params (nav category links, deep-linkable filter/search) ----
  function readParams() {
    try {
      var p = new URLSearchParams(window.location.search);
      var f = p.get('filter');
      if (f && (f === 'all' || CATEGORIES.indexOf(f) !== -1)) state.filter = f;
      var q = p.get('q');
      if (q) state.query = q;
    } catch (e) {}
  }
  function syncUrl() {
    try {
      var p = new URLSearchParams(window.location.search);
      if (state.filter && state.filter !== 'all') p.set('filter', state.filter); else p.delete('filter');
      if (state.query) p.set('q', state.query); else p.delete('q');
      var qs = p.toString();
      history.replaceState(null, '', qs ? '?' + qs : window.location.pathname);
    } catch (e) {}
  }

  function counts() {
    var c = { all: items.length, concept: 0, product: 0, repo: 0, workflow: 0 };
    items.forEach(function (it) { if (c[it.category] != null) c[it.category]++; });
    return c;
  }

  // Surviving rows keep their original digest index for stable deep links.
  function visibleRows() {
    var q = state.query.trim().toLowerCase();
    return items
      .map(function (it, i) { return { it: it, i: i }; })
      .filter(function (x) {
        if (state.filter !== 'all' && x.it.category !== state.filter) return false;
        if (q) {
          var hay = (x.it.title + ' ' + x.it.summary + ' ' + x.it.category).toLowerCase();
          if (hay.indexOf(q) === -1) return false;
        }
        return true;
      });
  }

  // Group rows by week key, returned newest week first.
  function groupByWeek(rows) {
    var map = {};
    rows.forEach(function (x) {
      var key = SD.weekKey(x.it.published_date);
      (map[key] || (map[key] = [])).push(x);
    });
    return Object.keys(map)
      .sort(function (a, b) { return a < b ? 1 : a > b ? -1 : 0; })
      .map(function (key) { return { key: key, rows: map[key] }; });
  }

  function render() {
    var rows = visibleRows();
    mount.textContent = '';

    if (!rows.length) {
      mount.appendChild(SD.el('p', 'empty-note', 'No signals match this filter yet.'));
      if (countEl) countEl.textContent = '0 results';
      return;
    }

    groupByWeek(rows).forEach(function (week) {
      var section = SD.el('section', 'archive-week');

      var head = SD.el('div', 'archive-week-head');
      head.appendChild(SD.el('h2', null, SD.weekLabel(week.rows[0].it.published_date)));
      head.appendChild(SD.el('span', 'archive-week-count',
        week.rows.length + ' signal' + (week.rows.length === 1 ? '' : 's')));
      section.appendChild(head);

      var grid = SD.el('div', 'cards-grid');
      // Strongest signal first within a week.
      week.rows.sort(function (a, b) { return b.it.signal_score - a.it.signal_score; });
      week.rows.forEach(function (x) { grid.appendChild(SD.buildCard(x.it, x.i)); });
      section.appendChild(grid);

      mount.appendChild(section);
    });

    if (countEl) countEl.textContent = rows.length + ' result' + (rows.length === 1 ? '' : 's');
  }

  function renderChips() {
    if (!chipsEl) return;
    var c = counts();
    chipsEl.textContent = '';
    FILTER_DEFS.forEach(function (def) {
      var key = def[0];
      var btn = SD.el('button', 'chip' + (state.filter === key ? ' is-active' : ''), def[1] + ' ' + c[key]);
      btn.setAttribute('type', 'button');
      btn.setAttribute('aria-pressed', state.filter === key ? 'true' : 'false');
      btn.addEventListener('click', function () {
        state.filter = key; syncUrl(); renderChips(); render();
      });
      chipsEl.appendChild(btn);
    });
  }

  function wireSearch() {
    if (!searchEl) return;
    searchEl.addEventListener('input', function () {
      state.query = searchEl.value; syncUrl(); render();
    });
    if (state.query) searchEl.value = state.query;
  }

  fetch('content/digest.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      items = (data && data.items) || [];
      readParams();
      renderChips();
      wireSearch();
      render();
    })
    .catch(function () {
      mount.textContent = '';
      mount.appendChild(SD.el('p', 'empty-note', 'Could not load signals. Run a static server from the repo root.'));
    });
})();
