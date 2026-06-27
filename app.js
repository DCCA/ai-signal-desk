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

  // "This week at a glance": verdict counts scoped to the most recent week so
  // the label stays literally true as the back-catalog grows.
  function fillGlance(items) {
    var scoped = items;
    if (SD.weekKey && items.length) {
      var latest = items.reduce(function (max, it) {
        var k = SD.weekKey(it.published_date);
        return k > max ? k : max;
      }, '');
      scoped = items.filter(function (it) { return SD.weekKey(it.published_date) === latest; });
    }
    var s = { learn: 0, try: 0, watch: 0, ignore: 0 };
    scoped.forEach(function (it) { if (s[it.status] != null) s[it.status]++; });
    document.querySelectorAll('[data-glance]').forEach(function (n) {
      var k = n.getAttribute('data-glance');
      if (s[k] != null) n.textContent = s[k];
    });
  }

  function fillUpdated(updated) {
    if (!updated) return;
    document.querySelectorAll('[data-updated]').forEach(function (n) {
      n.textContent = updated;
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

  fetch('/content/digest.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var items = (data && data.items) || [];
      fillWayfinding(items);
      fillGlance(items);
      fillUpdated(data && data.updated);
      renderTop(items);
    })
    .catch(function () {
      grid.textContent = '';
      grid.appendChild(SD.el('p', 'empty-note', 'Could not load signals. Run a static server from the repo root.'));
    });
})();
