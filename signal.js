/* AI Signal Desk - signal deep-dive (article view).
   Renders a single classified signal selected by ?i= using the DOM API
   (no innerHTML, no inline styles) so the strict CSP holds and untrusted-
   looking fields are never interpolated as markup. Dynamic bar widths use
   the CSSOM (allowed under style-src 'self'). The source link is run through
   a scheme allowlist before it reaches the DOM.
   Data: content/digest.json -> { tagline, updated, items: Signal[] }. */
(function () {
  var root = document.querySelector('[data-article]');
  if (!root) return;

  var CATEGORIES = ['concept', 'product', 'repo', 'workflow'];
  var STATUSES = ['learn', 'try', 'watch', 'ignore'];

  // ---- helpers ----
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  // URL allowlist: strip control chars, then permit only http(s)/mailto or
  // relative paths. Anything else (javascript:, data:, etc.) returns ''.
  function safeUrl(value) {
    if (value == null) return '';
    var s = String(value).replace(/[\x00-\x1F\x7F]/g, '').trim();
    if (!s) return '';
    if (/^(https?:|mailto:)/i.test(s)) return s;
    // reject anything with a scheme that is not allowed above
    if (/^[a-z][a-z0-9+.-]*:/i.test(s)) return '';
    // relative paths (including ./, ../, /path, #frag, ?query) are allowed
    return s;
  }

  function clampScore(score) {
    return Math.max(0, Math.min(100, Number(score) || 0));
  }

  function readIndex(len) {
    var i = 0;
    try {
      var raw = new URLSearchParams(window.location.search).get('i');
      var parsed = parseInt(raw, 10);
      if (!isNaN(parsed)) i = parsed;
    } catch (e) {}
    if (i < 0) i = 0;
    if (i > len - 1) i = len - 1;
    return i;
  }

  function catOf(it) {
    return CATEGORIES.indexOf(it.category) !== -1 ? it.category : 'concept';
  }
  function statusOf(it) {
    return STATUSES.indexOf(it.status) !== -1 ? it.status : 'watch';
  }

  function catTag(it) {
    var cat = catOf(it);
    var tag = el('span', 'cat-tag cat-' + cat);
    tag.appendChild(el('span', 'dot dot-' + cat));
    tag.appendChild(document.createTextNode(cat));
    return tag;
  }

  function bar(kind, score) {
    var row = el('div', 'bar-row');
    row.appendChild(el('span', 'bar-label', kind === 'signal' ? 'Signal' : 'Hype'));
    var track = el('div', 'bar-track');
    var fill = el('div', 'bar-fill bar-fill-' + kind);
    var pct = clampScore(score);
    fill.style.setProperty('--w', pct + '%'); // CSSOM: allowed under strict CSP
    track.appendChild(fill);
    row.appendChild(track);
    row.appendChild(el('span', 'bar-val', String(pct)));
    return row;
  }

  function proseBlock(kicker, body) {
    var wrap = el('div');
    wrap.appendChild(el('div', 'prose-kicker', kicker));
    wrap.appendChild(el('p', 'prose-body', body || ''));
    return wrap;
  }

  function relatedCard(it, origIdx) {
    var a = el('a', 'related-card');
    a.setAttribute('href', 'signal.html?i=' + origIdx);
    a.appendChild(catTag(it));
    a.appendChild(el('div', 'related-title', it.title));
    a.appendChild(el(
      'span',
      'related-score',
      'Signal ' + clampScore(it.signal_score) + ' · Hype ' + clampScore(it.hype_score)
    ));
    return a;
  }

  // Related = same category (excluding current), backfilled with other items
  // until we have up to 3, matching the prototype.
  function relatedFor(items, idx) {
    var current = items[idx];
    var related = [];
    items.forEach(function (it, i) {
      if (i !== idx && it.category === current.category && related.length < 3) {
        related.push({ it: it, i: i });
      }
    });
    if (related.length < 3) {
      items.forEach(function (it, i) {
        if (related.length >= 3) return;
        if (i === idx) return;
        var already = related.some(function (r) { return r.i === i; });
        if (!already) related.push({ it: it, i: i });
      });
    }
    return related;
  }

  function render(items, idx) {
    var it = items[idx];
    var status = statusOf(it);

    root.textContent = '';

    // 1) back link
    var back = el('a', 'back-link', '← Back to digest');
    back.setAttribute('href', 'index.html');
    root.appendChild(back);

    // 2) tag row: category + verdict
    var tagrow = el('div', 'article-tagrow');
    tagrow.appendChild(catTag(it));
    tagrow.appendChild(el('span', 'verdict verdict-' + status, status.toUpperCase()));
    root.appendChild(tagrow);

    // 3) title + lead
    root.appendChild(el('h1', 'article-h1', it.title));
    root.appendChild(el('p', 'article-lead', it.summary));

    // 4) meta card
    var meta = el('div', 'meta-card');
    var left = el('div', 'meta-left');
    var bars = el('div', 'bars bars-lg');
    bars.appendChild(bar('signal', it.signal_score));
    bars.appendChild(bar('hype', it.hype_score));
    left.appendChild(bars);
    meta.appendChild(left);

    var right = el('div', 'meta-right');
    right.appendChild(el('span', 'meta-conf-label', 'Confidence'));
    right.appendChild(el('span', 'meta-conf-val', it.confidence || ''));
    meta.appendChild(right);
    root.appendChild(meta);

    // 5) prose
    var prose = el('div', 'prose');
    prose.appendChild(proseBlock('What it is', it.summary));
    prose.appendChild(proseBlock('Why it matters', it.why_it_matters));

    var tryPanel = el('div', 'try-panel');
    tryPanel.appendChild(el('div', 'prose-kicker', 'Try this'));
    tryPanel.appendChild(el('p', 'prose-body', it.try_this || ''));
    prose.appendChild(tryPanel);

    // 6) source row (only when a safe source URL exists)
    var sourceUrl = safeUrl(it.source_url);
    if (sourceUrl) {
      var srcRow = el('div', 'source-row');
      var srcInfo = el('div');
      srcInfo.appendChild(el('div', 'source-label-kicker', 'Source'));
      srcInfo.appendChild(el('div', 'source-label', it.source_label || ''));
      srcRow.appendChild(srcInfo);

      var srcLink = el('a', 'btn-accent', 'View source →');
      srcLink.setAttribute('href', sourceUrl);
      srcLink.setAttribute('target', '_blank');
      srcLink.setAttribute('rel', 'noopener noreferrer');
      srcRow.appendChild(srcLink);
      prose.appendChild(srcRow);
    }
    root.appendChild(prose);

    // 7) related signals
    var relWrap = el('div', 'related-wrap');
    relWrap.appendChild(el('h3', null, 'Related signals'));
    var relGrid = el('div', 'related-grid');
    relatedFor(items, idx).forEach(function (r) {
      relGrid.appendChild(relatedCard(r.it, r.i));
    });
    relWrap.appendChild(relGrid);
    root.appendChild(relWrap);

    document.title = it.title + ' — AI Signal Desk';
  }

  fetch('content/digest.json')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var items = (data && data.items) || [];
      if (!items.length) {
        root.textContent = '';
        root.appendChild(el('p', 'empty-note', 'No signals available.'));
        return;
      }
      var idx = readIndex(items.length);
      render(items, idx);
    })
    .catch(function () {
      root.textContent = '';
      root.appendChild(el('p', 'empty-note', 'Could not load this signal. Run a static server from the repo root.'));
    });
})();
