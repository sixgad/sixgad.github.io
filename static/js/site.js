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
      /* 图标切换改由双图标 CSS 交叉淡换驱动（data-theme 属性即状态源），JS 不再改写图标 class */
    };

    applyTheme(rootEl.getAttribute('data-theme') === 'dark' ? 'dark' : 'light');

    themeBtn.addEventListener('click', function () {
      var next = rootEl.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      var run = function () {
        try {
          localStorage.setItem(THEME_KEY, next);
        } catch (e) { /* 隐私模式等场景静默降级为不记忆 */ }
        userPinned = true;
        applyTheme(next);
      };
      /* v2.3 主题 morph：仅包裹点击路径（初始应用由 frag_theme 先行定值，包裹徒增空快照）；
         三分支统一门控口径：motionOn（v2-motion 总开关）且非 reduce 才有过渡，
         否则裸 run() —— 修复独立复审 Spec#2/C2（VT 分支漏查开关、reduce 中途开启时误加颜色过渡） */
      if (rootEl.classList.contains('v2-motion') && !reducedMotion.matches && document.startViewTransition) {
        document.startViewTransition(run);
      } else if (rootEl.classList.contains('v2-motion') && !reducedMotion.matches) {
        document.body.classList.add('v2-theme-fade');
        run();
        window.setTimeout(function () { document.body.classList.remove('v2-theme-fade'); }, 240);
      } else {
        run();
      }
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
    var pulseTopBtn = function (btn) {
      /* v2.3 点击脉冲环：一次性，动画结束即摘类（动画不运行的环境 900ms 兜底摘除） */
      btn.classList.remove('v2-pulse');
      void btn.offsetWidth; /* 重启一次性动画 */
      btn.classList.add('v2-pulse');
      var clear = function () { btn.classList.remove('v2-pulse'); };
      btn.addEventListener('animationend', function onEnd(ev) {
        if (ev.animationName === 'v2-pulse-ring') { clear(); btn.removeEventListener('animationend', onEnd); }
      });
      window.setTimeout(clear, 900);
    };
    topBtn.addEventListener('click', function (e) {
      e.preventDefault();
      if (document.documentElement.classList.contains('v2-motion')) { pulseTopBtn(topBtn); }
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

  /* —— v2.3 入场编排：首屏卡片批次级联浮现（仅 v2-motion + v2-intro 会话首文档执行；其余卡片不被触碰） —— */
  var motionOn = document.documentElement.classList.contains('v2-motion');
  if (motionOn && document.documentElement.classList.contains('v2-intro')) {
    var cascadeSel = '.content-page > .blog-post, .acg-grid > .acg-card, .hub-grid > .hub-card';
    var vh0 = window.innerHeight || document.documentElement.clientHeight;
    var v2items = [];
    Array.prototype.forEach.call(document.querySelectorAll(cascadeSel), function (el) {
      var r = el.getBoundingClientRect();
      if (v2items.length < 16 && r.top < vh0 * 1.05 && r.bottom > -40) {
        v2items.push(el);
      }
    });
    if (v2items.length) {
      v2items.forEach(function (el, i) {
        el.classList.add('v2-enter');
        el.style.setProperty('--v2-enter-delay', (i * 80) + 'ms');
      });
      var revealDone = false;
      var revealCards = function () {
        if (revealDone) { return; }
        revealDone = true;
        v2items.forEach(function (el) {
          el.classList.add('v2-in');
          /* 入场过渡结束后摘除动效临时类：`.v2-enter.v2-in` 的 transform:none 与 transition
             声明若常驻，会以同特异度+后源序压过 v2.1 卡片 hover/active 变换与过渡（独立复审 High）。
             摘类后卡片回归基线规则，v2.1 悬停行为不受影响 */
          var drop = function (ev) {
            if (ev && ev.propertyName !== 'transform') { return; }
            el.classList.remove('v2-in');
            el.classList.remove('v2-enter');
            el.style.removeProperty('--v2-enter-delay');
          };
          el.addEventListener('transitionend', function onT(ev) {
            if (ev.propertyName === 'transform') { drop(ev); el.removeEventListener('transitionend', onT); }
          });
          /* 兜底：过渡被挂起/跳过的环境（隐藏页、reduced 中途开启等）超时摘类，最迟观感等同完成态 */
          window.setTimeout(drop, 80 * v2items.length + 900);
        });
      };
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(revealCards);
      });
      /* 兜底：rAF 被挂起/节流的引擎（隐藏页、异常环境）仍保证入场到达完成态；正常路径 rAF 先行 */
      window.setTimeout(revealCards, 90);
    }
  }

  /* —— v2.3 签名 · 元素 inspector 悬停：四角选区括号 + 实时尺寸 chip（仅 hover 设备） —— */
  if (motionOn && window.matchMedia && window.matchMedia('(hover: hover)').matches) {
    var inspectMap = [
      ['a.hub-card', 'hub-card'],
      ['a.acg-card.eli5-card', 'eli5-card'],
      ['article.acg-card', 'acg-card'],
      ['div.blog-post', 'blog-post']
    ];
    inspectMap.forEach(function (pair) {
      Array.prototype.forEach.call(document.querySelectorAll(pair[0]), function (el) {
        el.setAttribute('data-v2-inspect', pair[1]);
      });
    });
    var ensureInspectOverlay = function (card) {
      var ov = card.querySelector('.v2-inspect');
      if (!ov) {
        ov = document.createElement('div');
        ov.className = 'v2-inspect';
        ov.setAttribute('aria-hidden', 'true');
        ov.innerHTML = '<b class="v2-ib v2-ib-tl"></b><b class="v2-ib v2-ib-tr"></b>' +
          '<b class="v2-ib v2-ib-bl"></b><b class="v2-ib v2-ib-br"></b>' +
          '<span class="v2-ichip"></span>';
        card.appendChild(ov);
      }
      return ov;
    };
    Array.prototype.forEach.call(document.querySelectorAll('[data-v2-inspect]'), function (card) {
      card.addEventListener('mouseenter', function () {
        var ov = ensureInspectOverlay(card);
        var r = card.getBoundingClientRect();
        ov.querySelector('.v2-ichip').textContent = card.tagName.toLowerCase() + '.' +
          card.getAttribute('data-v2-inspect') + ' · ' +
          Math.round(r.width) + '×' + Math.round(r.height);
        void ov.offsetWidth; /* 强制回算 overlay 初始样式，保证首次悬停也走 180ms 过渡（复审 C3：同帧插入+激活会跳过过渡） */
        card.classList.add('v2-inspected');
      });
      card.addEventListener('mouseleave', function () {
        card.classList.remove('v2-inspected');
      });
    });
  }

  /* —— v2.3 阅读进度束带（仅详情页；顶栏内沿下缘，scaleX 随滚动比例） —— */
  if (motionOn && document.querySelector('.blog-cc')) {
    var topbarEl = document.querySelector('.site-topbar');
    if (topbarEl) {
      var band = document.createElement('div');
      band.className = 'v2-progress';
      band.setAttribute('aria-hidden', 'true');
      topbarEl.appendChild(band);
      var bandRaf = null;
      var syncBand = function () {
        bandRaf = null;
        var h = document.documentElement.scrollHeight - window.innerHeight;
        var p = h > 0 ? Math.min(1, window.scrollY / h) : 0;
        band.style.transform = 'scaleX(' + p.toFixed(4) + ')';
      };
      window.addEventListener('scroll', function () {
        if (!bandRaf) { bandRaf = window.requestAnimationFrame(syncBand); }
      }, { passive: true });
      syncBand();
    }
  }

  /* —— v2.3 作者头像鼠标微浮（±4px，仅 hover 设备；离开回弹） —— */
  var pic = document.querySelector('.my-pic');
  if (motionOn && pic && window.matchMedia && window.matchMedia('(hover: hover)').matches) {
    var picImg = pic.querySelector('img');
    if (picImg) {
      var picRaf = null;
      var picTarget = { x: 0, y: 0 };
      var clamp4 = function (v) { return Math.max(-4, Math.min(4, v)); };
      pic.addEventListener('mousemove', function (e) {
        var r = pic.getBoundingClientRect();
        picTarget.x = clamp4(((e.clientX - (r.left + r.width / 2)) / (r.width / 2)) * 4);
        picTarget.y = clamp4(((e.clientY - (r.top + r.height / 2)) / (r.height / 2)) * 4);
        if (!picRaf) {
          picRaf = window.requestAnimationFrame(function () {
            picRaf = null;
            picImg.style.transform = 'translate(' + picTarget.x.toFixed(1) + 'px, ' + picTarget.y.toFixed(1) + 'px)';
          });
        }
      }, { passive: true });
      pic.addEventListener('mouseleave', function () {
        picImg.style.transform = '';
      });
    }
  }
})();
