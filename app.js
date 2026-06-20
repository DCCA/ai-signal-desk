/* AI Signal Desk — home digest.
   Builds cards with the DOM API (no innerHTML, no inline styles) so the
   strict CSP holds and untrusted-looking fields are never interpolated as
   markup. Dynamic bar widths use the CSSOM (allowed under style-src 'self').
   Data: content/digest.json -> { tagline, updated, items: Signal[] }. */
(function () {
  var grid = document.querySelector('[data-digest-grid]');
  if (!grid) return;

  var chipsEl = document.querySelector('[data-filters]');
  var sortsEl = document.querySelector('[data-sorts]');
  var countEl = document.querySelector('[data-results-count]');
  var searchEl = document.querySelector('[data-search]');
  var searchBtn = document.querySelector('[data-search-btn]');

  var CATEGORIES = ['concept', 'product', 'repo', 'workflow'];
  var FILTER_DEFS = [
    ['all', 'All'], ['concept', 'Concepts'], ['product', 'Products'],
    ['repo', 'Repos'], ['workflow', 'Workflows']
  ];
  var SORT_DEFS = [['signal', 'Top signal'], ['hype', 'Least hype'], ['newest', 'Newest']];

  var items = [];
  var state = { filter: 'all', sort: 'signal', query: '' };

  // ---- URL params (nav category links, deep-linkable filter) ----
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

  // ---- helpers ----
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function counts() {
    var c = { all: items.length, concept: 0, product: 0, repo: 0, workflow: 0 };
    items.forEach(function (it) { if (c[it.category] != null) c[it.category]++; });
    return c;
  }

  function bar(kind, score) {
    var row = el('div', 'bar-row');
    row.appendChild(el('span', 'bar-label', kind === 'signal' ? 'Signal' : 'Hype'));
    var track = el('div', 'bar-track');
    var fill = el('div', 'bar-fill bar-fill-' + kind);
    var pct = Math.max(0, Math.min(100, Number(score) || 0));
    fill.style.setProperty('--w', pct + '%'); // CSSOM: allowed under strict CSP
    track.appendChild(fill);
    row.appendChild(track);
    row.appendChild(el('span', 'bar-val', String(pct)));
    return row;
  }

  function card(it, origIdx) {
    var cat = CATEGORIES.indexOf(it.category) !== -1 ? it.category : 'concept';
    var status = ['learn', 'try', 'watch', 'ignore'].indexOf(it.status) !== -1 ? it.status : 'watch';
    var num = String(origIdx + 1).padStart(2, '0');

    var a = el('a', 'signal-card');
    a.setAttribute('href', 'signal.html?i=' + origIdx);

    var top = el('div', 'card-top');
    var tag = el('span', 'cat-tag cat-' + cat);
    tag.appendChild(el('span', 'dot dot-' + cat));
    tag.appendChild(document.createTextNode(num + ' / ' + cat));
    top.appendChild(tag);
    top.appendChild(el('span', 'verdict verdict-' + status, status.toUpperCase()));
    a.appendChild(top);

    var body = el('div');
    body.appendChild(el('h3', 'card-title', it.title));
    body.appendChild(el('p', 'card-summary', it.summary));
    a.appendChild(body);

    var bars = el('div', 'bars');
    bars.appendChild(bar('signal', it.signal_score));
    bars.appendChild(bar('hype', it.hype_score));
    a.appendChild(bars);

    var tryRow = el('div', 'card-try');
    var p = el('p');
    p.appendChild(el('b', null, 'Try this:'));
    p.appendChild(document.createTextNode(' ' + (it.try_this || '')));
    tryRow.appendChild(p);
    a.appendChild(tryRow);

    a.appendChild(el('span', 'card-cta', 'Read full signal →'));
    return a;
  }

  function visibleItems() {
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

  function renderCards() {
    var rows = visibleItems();
    if (state.sort === 'signal') rows.sort(function (a, b) { return b.it.signal_score - a.it.signal_score; });
    else if (state.sort === 'hype') rows.sort(function (a, b) { return a.it.hype_score - b.it.hype_score; });
    else rows.sort(function (a, b) { return b.i - a.i; });

    grid.textContent = '';
    if (!rows.length) {
      grid.appendChild(el('p', 'empty-note', 'No signals match this filter yet.'));
    } else {
      rows.forEach(function (x) { grid.appendChild(card(x.it, x.i)); });
    }
    if (countEl) countEl.textContent = rows.length + ' result' + (rows.length === 1 ? '' : 's');
  }

  function renderChips() {
    if (!chipsEl) return;
    var c = counts();
    chipsEl.textContent = '';
    FILTER_DEFS.forEach(function (def) {
      var key = def[0];
      var btn = el('button', 'chip' + (state.filter === key ? ' is-active' : ''), def[1] + ' ' + c[key]);
      btn.setAttribute('type', 'button');
      btn.setAttribute('aria-pressed', state.filter === key ? 'true' : 'false');
      btn.addEventListener('click', function () {
        state.filter = key; syncUrl(); renderChips(); renderCards();
      });
      chipsEl.appendChild(btn);
    });
  }

  function renderSorts() {
    if (!sortsEl) return;
    sortsEl.textContent = '';
    SORT_DEFS.forEach(function (def) {
      var key = def[0];
      var btn = el('button', 'seg-btn' + (state.sort === key ? ' is-active' : ''), def[1]);
      btn.setAttribute('type', 'button');
      btn.setAttribute('aria-pressed', state.sort === key ? 'true' : 'false');
      btn.addEventListener('click', function () {
        state.sort = key; renderSorts(); renderCards();
      });
      sortsEl.appendChild(btn);
    });
  }

  function fillWayfinding() {
    var c = counts();
    document.querySelectorAll('[data-count]').forEach(function (n) {
      var k = n.getAttribute('data-count');
      if (c[k] != null) n.textContent = c[k];
    });
  }

  function wireSearch() {
    if (searchEl) {
      searchEl.addEventListener('input', function () {
        state.query = searchEl.value; syncUrl(); renderCards();
      });
      searchEl.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); jumpToDigest(); }
      });
      if (state.query) searchEl.value = state.query;
    }
    if (searchBtn) searchBtn.addEventListener('click', jumpToDigest);
  }
  function jumpToDigest() {
    var d = document.getElementById('digest');
    if (d) d.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  fetch('content/digest.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      items = (data && data.items) || [];
      readParams();
      renderChips();
      renderSorts();
      fillWayfinding();
      wireSearch();
      renderCards();
    })
    .catch(function () {
      grid.textContent = '';
      grid.appendChild(el('p', 'empty-note', 'Could not load signals. Run a static server from the repo root.'));
    });
})();
