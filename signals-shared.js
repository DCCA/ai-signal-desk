/* AI Signal Desk — shared rendering + date helpers.
   The signal-card DOM builder and the week helpers used by both the home grid
   (app.js) and the archive (archive.js). Cards are built with the DOM API (no
   innerHTML, no inline styles) so the strict CSP holds and untrusted-looking
   fields are never interpolated as markup. Bar widths use the CSSOM
   (setProperty('--w', ...)), which is allowed under style-src 'self'. */
(function () {
  var CATEGORIES = ['concept', 'product', 'repo', 'workflow'];
  var STATUSES = ['learn', 'try', 'watch', 'ignore'];
  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
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

  // Build a signal card. origIdx is the 0-based index into the unfiltered
  // digest, so deep links (signal.html?i=N) stay stable across filters/sorts.
  function buildCard(it, origIdx) {
    var cat = CATEGORIES.indexOf(it.category) !== -1 ? it.category : 'concept';
    var status = STATUSES.indexOf(it.status) !== -1 ? it.status : 'watch';
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

  // ---- week helpers (ISO week, Monday start) ----
  function parseDate(dateStr) {
    var parts = String(dateStr || '').split('-');
    // Local-time date avoids UTC off-by-one when bucketing by day.
    return new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
  }
  function weekStart(dateStr) {
    var d = parseDate(dateStr);
    var dow = (d.getDay() + 6) % 7; // 0 = Monday
    d.setDate(d.getDate() - dow);
    d.setHours(0, 0, 0, 0);
    return d;
  }
  function pad2(n) { return String(n).padStart(2, '0'); }
  function weekKey(dateStr) {
    var d = weekStart(dateStr);
    return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate());
  }
  function weekLabel(dateStr) {
    var d = weekStart(dateStr);
    return 'Week of ' + MONTHS[d.getMonth()] + ' ' + d.getDate() + ', ' + d.getFullYear();
  }

  window.SignalDesk = {
    el: el,
    buildCard: buildCard,
    weekStart: weekStart,
    weekKey: weekKey,
    weekLabel: weekLabel,
    CATEGORIES: CATEGORIES
  };
})();
