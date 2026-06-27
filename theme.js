/* Theme + locale bootstrap for AI Signal Desk.
   Loaded synchronously in <head> on every page (so the correct theme is applied
   before first paint, and the i18n helpers exist before the renderers run) —
   no inline script, keeping the strict CSP intact.

   i18n: locale is path-based (/pt/* is Portuguese, else English). SD_T(key)
   localizes UI labels; SD_PICK(item, field) returns the item's `<field>_pt`
   value on pt pages, falling back to English when a translation is absent. */
(function () {
  var KEY = 'asd-theme';
  var root = document.documentElement;

  // --- Shared locale + string table -------------------------------------
  var LOCALE = /^\/pt(\/|$)/.test(location.pathname) ? 'pt' : 'en';
  var STR = {
    en: {
      sig: 'Signal', hype: 'Hype', tryThis: 'Try this:', readFull: 'Read full signal →',
      cat_concept: 'concept', cat_product: 'product', cat_repo: 'repo', cat_workflow: 'workflow',
      st_learn: 'LEARN', st_try: 'TRY', st_watch: 'WATCH', st_ignore: 'IGNORE',
      themeDark: 'Dark', themeLight: 'Light',
      weekOf: 'Week of',
      back: '← Back to digest', whatItIs: 'What it is', whyItMatters: 'Why it matters',
      tryKicker: 'Try this', confidence: 'Confidence',
      conf_high: 'high', conf_medium: 'medium', conf_low: 'low',
      source: 'Source', viewSource: 'View source →', srcLang: '',
      related: 'Related signals',
      fl_all: 'All', fl_concept: 'Concepts', fl_product: 'Products', fl_repo: 'Repos', fl_workflow: 'Workflows',
      noMatch: 'No signals match this filter yet.',
      loadErr: 'Could not load signals. Run a static server from the repo root.',
      noneAvail: 'No signals available.',
      g_learn: 'Learn', g_learn_note: 'Concepts worth understanding',
      g_try: 'Try', g_try_note: 'Concrete use case attached',
      g_watch: 'Watch', g_watch_note: 'Promising, wait for signal',
      g_ignore: 'Ignore', g_ignore_note: 'The hype filter',
      months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    },
    pt: {
      sig: 'Sinal', hype: 'Hype', tryThis: 'Para testar:', readFull: 'Ler sinal completo →',
      cat_concept: 'conceito', cat_product: 'produto', cat_repo: 'repositório', cat_workflow: 'fluxo',
      st_learn: 'APRENDER', st_try: 'TESTAR', st_watch: 'OBSERVAR', st_ignore: 'IGNORAR',
      themeDark: 'Escuro', themeLight: 'Claro',
      weekOf: 'Semana de',
      back: '← Voltar ao resumo', whatItIs: 'O que é', whyItMatters: 'Por que importa',
      tryKicker: 'Para testar', confidence: 'Confiança',
      conf_high: 'alta', conf_medium: 'média', conf_low: 'baixa',
      source: 'Fonte', viewSource: 'Ver fonte →', srcLang: 'conteúdo em inglês',
      related: 'Sinais relacionados',
      fl_all: 'Tudo', fl_concept: 'Conceitos', fl_product: 'Produtos', fl_repo: 'Repositórios', fl_workflow: 'Fluxos',
      noMatch: 'Nenhum sinal corresponde a este filtro ainda.',
      loadErr: 'Não foi possível carregar os sinais. Rode um servidor estático na raiz do repositório.',
      noneAvail: 'Nenhum sinal disponível.',
      g_learn: 'Aprender', g_learn_note: 'Conceitos que vale entender',
      g_try: 'Testar', g_try_note: 'Só com um caso de uso concreto',
      g_watch: 'Observar', g_watch_note: 'Promissor, aguardando sinal',
      g_ignore: 'Ignorar', g_ignore_note: 'O filtro de hype',
      months: ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
    }
  };
  window.SD_LOCALE = LOCALE;
  window.SD_T = function (k) {
    var d = STR[LOCALE] || STR.en;
    return d[k] != null ? d[k] : (STR.en[k] != null ? STR.en[k] : k);
  };
  window.SD_PICK = function (it, f) {
    if (LOCALE === 'pt' && it) {
      var v = it[f + '_pt'];
      if (v != null && String(v).length) return v;
    }
    return it ? it[f] : '';
  };

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
      if (label) label.textContent = theme === 'light' ? window.SD_T('themeDark') : window.SD_T('themeLight');
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
