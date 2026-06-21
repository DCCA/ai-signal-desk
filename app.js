/* AI Signal Desk — home "best of" grid.
   The home page is a lean front door: it shows the top signals by score and
   sends readers to archive.html for the full, date-grouped, filterable history.
   Cards are built by the shared SignalDesk.buildCard (DOM API only, no
   innerHTML), so the strict CSP holds.
   Data: content/digest.json -> { tagline, updated, items: Signal[] }. */
(function () {
  var SD = window.SignalDesk;
  var grid = document.querySelector('[data-digest-grid]');
  if (!grid || !SD) return;

  var countEl = document.querySelector('[data-results-count]');
  var TOP_N = 9;

  function fillWayfinding(items) {
    var c = { concept: 0, product: 0, repo: 0, workflow: 0 };
    items.forEach(function (it) { if (c[it.category] != null) c[it.category]++; });
    document.querySelectorAll('[data-count]').forEach(function (n) {
      var k = n.getAttribute('data-count');
      if (c[k] != null) n.textContent = c[k];
    });
  }

  function renderTop(items) {
    // Keep the original digest index so deep links (signal.html?i=N) stay stable.
    var rows = items.map(function (it, i) { return { it: it, i: i }; });
    rows.sort(function (a, b) { return b.it.signal_score - a.it.signal_score; });
    var top = rows.slice(0, TOP_N);

    grid.textContent = '';
    top.forEach(function (x) { grid.appendChild(SD.buildCard(x.it, x.i)); });
    if (countEl) countEl.textContent = 'Top ' + top.length + ' signals';
  }

  fetch('content/digest.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var items = (data && data.items) || [];
      fillWayfinding(items);
      renderTop(items);
    })
    .catch(function () {
      grid.textContent = '';
      grid.appendChild(SD.el('p', 'empty-note', 'Could not load signals. Run a static server from the repo root.'));
    });
})();
