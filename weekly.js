/* AI Signal Desk — weekly field brief.
   Groups the digest items by action status (learn, try, watch, ignore) in a
   fixed order, omitting empty groups, and renders each group with the DOM API
   (no innerHTML, no inline styles) so the strict CSP holds and untrusted-looking
   fields are never interpolated as markup.
   Data: content/digest.json -> { tagline, updated, items: Signal[] }. */
(function () {
  var groupsEl = document.querySelector('[data-weekly-groups]');
  if (!groupsEl) return;

  var CATEGORIES = ['concept', 'product', 'repo', 'workflow'];

  var GROUP_DEFS = [
    { key: 'learn', label: 'Learn', note: 'Concepts worth understanding' },
    { key: 'try', label: 'Try', note: 'Concrete use case attached' },
    { key: 'watch', label: 'Watch', note: 'Promising, wait for signal' },
    { key: 'ignore', label: 'Ignore', note: 'The hype filter' }
  ];

  // ---- helper (matches app.js convention) ----
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function row(it, origIdx) {
    var cat = CATEGORIES.indexOf(it.category) !== -1 ? it.category : 'concept';
    var num = String(origIdx + 1).padStart(2, '0');

    var a = el('a', 'wk-row');
    a.setAttribute('href', 'signal.html?i=' + origIdx);

    a.appendChild(el('span', 'wk-num', num));
    a.appendChild(el('span', 'dot dot-' + cat));

    var main = el('div', 'wk-row-main');
    main.appendChild(el('div', 'wk-row-title', it.title));
    main.appendChild(el('div', 'wk-row-summary', it.summary));
    a.appendChild(main);

    var sScore = Number(it.signal_score) || 0;
    var hScore = Number(it.hype_score) || 0;
    a.appendChild(el('span', 'wk-score', 'S ' + sScore + ' · H ' + hScore));
    a.appendChild(el('span', 'wk-arrow', '→'));
    return a;
  }

  // Keep only the most recent calendar week (Monday-start). Items carry their
  // original digest index so deep links (signal.html?i=N) stay stable.
  function currentWeek(items) {
    var SD = window.SignalDesk;
    var rows = items.map(function (it, i) { return { it: it, i: i }; });
    if (!SD || !rows.length) return rows;
    var latest = rows.reduce(function (max, x) {
      var k = SD.weekKey(x.it.published_date);
      return k > max ? k : max;
    }, '');
    return rows.filter(function (x) { return SD.weekKey(x.it.published_date) === latest; });
  }

  function renderGroups(items) {
    groupsEl.textContent = '';
    var week = currentWeek(items);
    GROUP_DEFS.forEach(function (g) {
      var rows = week.filter(function (x) { return x.it.status === g.key; });
      if (!rows.length) return;

      var group = el('div');

      var head = el('div', 'wk-group-head');
      head.appendChild(el('span', 'dot dot-' + g.key));
      head.appendChild(el('h2', null, g.label));
      head.appendChild(el('span', 'wk-group-note', g.note));
      head.appendChild(el('span', 'wk-group-count', String(rows.length)));
      group.appendChild(head);

      rows.forEach(function (x) { group.appendChild(row(x.it, x.i)); });
      groupsEl.appendChild(group);
    });
  }

  fetch('content/digest.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var items = (data && data.items) || [];
      if (data && data.updated) {
        document.querySelectorAll('[data-updated]').forEach(function (n) {
          n.textContent = data.updated;
        });
      }
      renderGroups(items);
    })
    .catch(function () {
      groupsEl.textContent = '';
      groupsEl.appendChild(el('p', 'empty-note', 'Could not load signals. Run a static server from the repo root.'));
    });
})();
