/* Theme bootstrap + toggle for AI Signal Desk.
   Loaded synchronously in <head> so the correct theme is applied before
   first paint (no inline script, keeping the strict CSP intact). */
(function () {
  var KEY = 'asd-theme';
  var root = document.documentElement;

  function preferred() {
    try {
      var saved = localStorage.getItem(KEY);
      if (saved === 'light' || saved === 'dark') return saved;
    } catch (e) {}
    try {
      if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
    } catch (e) {}
    return 'light';
  }

  function apply(theme) {
    root.setAttribute('data-theme', theme);
    var btns = document.querySelectorAll('[data-theme-toggle]');
    for (var i = 0; i < btns.length; i++) {
      var b = btns[i];
      var icon = b.querySelector('[data-theme-icon]');
      var label = b.querySelector('[data-theme-label]');
      // In light mode we offer to switch to dark, and vice versa.
      if (icon) icon.textContent = theme === 'light' ? '☾' : '☀';
      if (label) label.textContent = theme === 'light' ? 'Dark' : 'Light';
      b.setAttribute('aria-label', theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme');
    }
  }

  // Apply immediately (before body paints).
  apply(preferred());

  function toggle() {
    var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem(KEY, next); } catch (e) {}
    apply(next);
  }

  function wire() {
    var btns = document.querySelectorAll('[data-theme-toggle]');
    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener('click', toggle);
    }
    // Re-sync labels now that the buttons exist in the DOM.
    apply(root.getAttribute('data-theme') || preferred());
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire);
  } else {
    wire();
  }
})();
