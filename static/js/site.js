/*
  爬客站点原生脚本（site-v2）：回到顶部 + 代码块复制 + 主题切换。
  无第三方依赖；行为均按元素存在与否自动挂载，六类页面共用同一入口。
*/
(function () {
  'use strict';

  var reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* —— 主题切换：data-theme 由 head 内联脚本先行判定，这里只接线 —— */
  var themeBtn = document.querySelector('.site-nav-belt__theme');
  if (themeBtn) {
    var THEME_KEY = 'pk-theme';
    var rootEl = document.documentElement;
    var darkMq = window.matchMedia('(prefers-color-scheme: dark)');
    var userPinned = (function () {
      try {
        var v = localStorage.getItem(THEME_KEY);
        return v === 'dark' || v === 'light';
      } catch (e) {
        return false;
      }
    })();

    var applyTheme = function (mode) {
      var isDark = mode === 'dark';
      rootEl.setAttribute('data-theme', mode);
      themeBtn.setAttribute('aria-pressed', String(isDark));
      themeBtn.setAttribute('aria-label', isDark ? '切换到亮色模式' : '切换到暗色模式');
      var icon = themeBtn.querySelector('i');
      if (icon) {
        icon.className = 'fa ' + (isDark ? 'fa-sun-o' : 'fa-moon-o');
      }
    };

    applyTheme(rootEl.getAttribute('data-theme') === 'dark' ? 'dark' : 'light');

    themeBtn.addEventListener('click', function () {
      var next = rootEl.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      try {
        localStorage.setItem(THEME_KEY, next);
      } catch (e) { /* 隐私模式等场景静默降级为不记忆 */ }
      userPinned = true;
      applyTheme(next);
    });

    // 未手动选择时跟随系统偏好实时变化
    var onSchemeChange = function () {
      if (!userPinned) {
        applyTheme(darkMq.matches ? 'dark' : 'light');
      }
    };
    if (darkMq.addEventListener) {
      darkMq.addEventListener('change', onSchemeChange);
    } else if (darkMq.addListener) {
      darkMq.addListener(onSchemeChange);
    }
  }

  /* —— 回到顶部 —— */
  var topBtn = document.querySelector('.scroll-to-top');
  if (topBtn) {
    var syncTopBtn = function () {
      topBtn.classList.toggle('is-visible', window.scrollY >= 500);
    };
    window.addEventListener('scroll', syncTopBtn, { passive: true });
    syncTopBtn();
    topBtn.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: reducedMotion.matches ? 'auto' : 'smooth' });
    });
  }

  /* —— 代码块复制按钮 —— */
  var copyFallback = function (text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.top = '-100px';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try {
      ok = document.execCommand('copy');
    } catch (err) {
      ok = false;
    }
    document.body.removeChild(ta);
    return ok;
  };

  Array.prototype.forEach.call(document.querySelectorAll('.blog-cc pre'), function (pre) {
    // 注入按钮前取源文本，保证剪贴板内容等于代码本身（textContent 不受渲染空白影响）
    var codeText = pre.textContent || '';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'v2-copy-btn';
    btn.textContent = '复制';
    btn.setAttribute('aria-label', '复制这段代码');
    var resetTimer = null;

    var feedback = function (ok) {
      btn.textContent = ok ? '已复制' : '复制失败';
      btn.classList.toggle('is-ok', ok);
      btn.classList.toggle('is-fail', !ok);
      if (resetTimer) {
        window.clearTimeout(resetTimer);
      }
      resetTimer = window.setTimeout(function () {
        btn.textContent = '复制';
        btn.classList.remove('is-ok');
        btn.classList.remove('is-fail');
      }, 1600);
    };

    btn.addEventListener('click', function () {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(codeText).then(
          function () { feedback(true); },
          function () { feedback(copyFallback(codeText)); }
        );
      } else {
        feedback(copyFallback(codeText));
      }
    });
    pre.appendChild(btn);
  });
})();
