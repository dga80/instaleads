/**
 * Application interactions, scroll tracking, essay reader and UI
 * for Luis Codera Puzo (Aesthetic of ecidni.com)
 */

(function () {
  'use strict';

  var doc = document.documentElement;
  doc.classList.add('js');

  var RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (RM) doc.classList.add('rm');

  /* ---------- Rail and Chapter Tracking ---------- */
  var secs = [].slice.call(document.querySelectorAll('.ch'));
  var links = [].slice.call(document.querySelectorAll('.rail ol a'));
  var tops = [];
  var active = -1;
  var first = true;
  var hero = document.getElementById('ground');
  var heroH = 0;
  var vh = window.innerHeight;
  var seqOn = false;

  function measure() {
    tops = secs.map(function (s) { return s.offsetTop; });
    heroH = hero ? hero.offsetHeight : 0;
    vh = window.innerHeight;
  }

  function pulse(i) {
    if (RM) return;
    var a = links[i];
    if (!a) return;
    a.classList.remove('pulse');
    void a.offsetWidth; // force reflow
    a.classList.add('pulse');
  }

  function setActive(i) {
    if (seqOn || i === active) return;
    active = i;
    links.forEach(function (a, j) {
      a.classList.toggle('lit', j < i);
      a.classList.toggle('now', j === i);
      if (j === i) a.setAttribute('aria-current', 'true');
      else a.removeAttribute('aria-current');
    });

    if (!first && window.SynthEngine && window.SynthEngine.isTonesOn()) {
      window.SynthEngine.playTone(i);
      pulse(i);
    }
    first = false;
  }

  function whichActive(y) {
    var probe = y + vh * 0.45;
    var i = 0;
    for (var k = 0; k < tops.length; k++) {
      if (tops[k] <= probe) i = k;
    }
    return i;
  }

  // Clean pulse class on animation end
  var railOl = document.querySelector('.rail ol');
  if (railOl) {
    railOl.addEventListener('animationend', function (e) {
      if (e.target.classList) e.target.classList.remove('pulse');
    });

    // Keyboard navigation on rail
    railOl.addEventListener('keydown', function (e) {
      var i = links.indexOf(document.activeElement);
      if (i < 0) return;
      var n = null;
      if (e.key === 'ArrowDown' || e.key === 'ArrowRight') n = Math.min(i + 1, links.length - 1);
      else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') n = Math.max(i - 1, 0);
      else if (e.key === 'Home') n = 0;
      else if (e.key === 'End') n = links.length - 1;

      if (n !== null && n !== i) {
        e.preventDefault();
        links[n].focus();
      }
    });
  }

  // Smooth scroll click handler
  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!a || a.getAttribute('href') === '#') return;
    var targetId = a.getAttribute('href').slice(1);
    var t = document.getElementById(targetId);
    if (!t) return;
    e.preventDefault();
    t.scrollIntoView({ behavior: RM ? 'auto' : 'smooth', block: 'start' });
    if (!t.hasAttribute('tabindex')) t.setAttribute('tabindex', '-1');
    t.focus({ preventScroll: true });

    try {
      history.replaceState(null, '', '#' + targetId);
    } catch (err) {}

    var idx = links.indexOf(a);
    if (idx >= 0 && idx === active && !seqOn && window.SynthEngine && window.SynthEngine.isTonesOn()) {
      window.SynthEngine.playTone(idx);
      pulse(idx);
    }
  });

  /* ---------- Tones Toggle ---------- */
  var tonesBtn = document.getElementById('tones');
  if (tonesBtn) {
    tonesBtn.addEventListener('click', function () {
      if (!window.SynthEngine) return;
      var isOn = window.SynthEngine.toggleTones();
      tonesBtn.setAttribute('aria-pressed', String(isOn));
      if (isOn) {
        var idx = Math.max(active, 0);
        window.SynthEngine.playTone(idx);
        pulse(idx);
      }
    });
  }

  /* ---------- Play Harmonic Sequence ---------- */
  var playScaleBtn = document.getElementById('playScale');
  var seqTimers = [];

  function endSeq() {
    seqTimers.forEach(clearTimeout);
    seqTimers = [];
    links.forEach(function (a) { a.classList.remove('seq'); });
    seqOn = false;
    active = -1;
    setActive(whichActive(window.scrollY || 0));
  }

  if (playScaleBtn) {
    playScaleBtn.addEventListener('click', function () {
      if (seqOn || !window.SynthEngine) return;
      seqOn = true;
      links.forEach(function (a) { a.classList.remove('lit', 'now'); });

      for (var i = 0; i < 8; i++) {
        (function (i) {
          window.SynthEngine.playTone(i, 0.05 + i * 0.26);
          seqTimers.push(setTimeout(function () {
            if (links[i]) {
              links[i].classList.add('seq');
              pulse(i);
            }
          }, 50 + i * 260));
        })(i);
      }
      seqTimers.push(setTimeout(endSeq, 50 + 8 * 260 + 260));
    });
  }

  /* ---------- Reveal Animation Observer ---------- */
  if (!RM && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.rv').forEach(function (el) {
      io.observe(el);
    });
  }

  /* ---------- Main Scroll Loop ---------- */
  var y = window.scrollY || 0;
  window.addEventListener('scroll', function () {
    y = window.scrollY || 0;
  }, { passive: true });

  function heroProgress() {
    var span = heroH - vh;
    if (span <= 0) return 1;
    var p = y / span;
    return p < 0 ? 0 : (p > 1 ? 1 : p);
  }

  function loop(now) {
    setActive(whichActive(y));
    if (window.HeroCanvas && y < heroH + vh) {
      window.HeroCanvas.draw(heroProgress(), now * 0.001);
    }
    requestAnimationFrame(loop);
  }

  measure();
  if (window.HeroCanvas) window.HeroCanvas.sizeCv();

  if (RM) {
    if (window.HeroCanvas) window.HeroCanvas.draw(1, 0);
    setActive(whichActive(y));
  } else {
    requestAnimationFrame(loop);
  }

  window.addEventListener('resize', function () {
    measure();
  }, { passive: true });

  /* ---------- Catalogue Filtering ---------- */
  var catBtns = document.querySelectorAll('.cat-btn');
  var workItems = document.querySelectorAll('.work-item');

  catBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      catBtns.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var filter = btn.getAttribute('data-filter');

      workItems.forEach(function (item) {
        if (filter === 'all' || item.getAttribute('data-category') === filter) {
          item.style.display = 'flex';
        } else {
          item.style.display = 'none';
        }
      });
    });
  });

  /* ---------- Essay Drawer / Modal Reader ---------- */
  var essaysData = [];
  var essayModal = document.getElementById('essayModal');
  var essayClose = document.getElementById('essayClose');
  var essayContainer = document.getElementById('essayContainer');

  // Load essays JSON
  fetch('data/essays.json')
    .then(function (res) { return res.json(); })
    .then(function (data) {
      essaysData = data;
    })
    .catch(function (err) {
      console.warn('Could not load essays.json', err);
    });

  function openEssay(slug) {
    var essay = essaysData.find(function (e) { return e.slug === slug; });
    if (!essay) return;

    var kicker = window.I18n ? window.I18n.t('modal.kicker') : 'Luis Codera Puzo · Ideas &amp; Essays';
    var linksLabel = window.I18n ? window.I18n.t('modal.links') : 'Related links:';

    var html = '<div class="essay-kicker">' + kicker + '</div>';
    html += '<h2>' + escapeHtml(essay.title) + '</h2>';
    html += '<div class="essay-body">';

    essay.paragraphs.forEach(function (p) {
      var text = escapeHtml(p.text);
      if (p.tag === 'h1' || p.tag === 'h2' || p.tag === 'h3') {
        html += '<h3>' + text + '</h3>';
      } else if (p.tag === 'blockquote') {
        html += '<blockquote>' + text + '</blockquote>';
      } else {
        html += '<p>' + text + '</p>';
      }
    });
    html += '</div>';

    if (essay.links && essay.links.length > 0) {
      html += '<div class="essay-links"><p style="color:var(--slate);margin-bottom:.5rem;">' + linksLabel + '</p>';
      essay.links.forEach(function (l) {
        if (l.href) {
          html += '<a href="' + escapeHtml(l.href) + '" target="_blank" rel="noopener">→ ' + escapeHtml(l.text || l.href) + '</a> ';
        }
      });
      html += '</div>';
    }

    if (essayContainer) essayContainer.innerHTML = html;
    if (essayModal) {
      essayModal.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
  }

  function closeEssay() {
    if (essayModal) {
      essayModal.classList.remove('open');
      document.body.style.overflow = '';
    }
  }

  if (essayClose) essayClose.addEventListener('click', closeEssay);
  if (essayModal) {
    essayModal.addEventListener('click', function (e) {
      if (e.target === essayModal) closeEssay();
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeEssay();
  });

  // Attach click listeners to essay cards and links
  document.addEventListener('click', function (e) {
    var card = e.target.closest ? e.target.closest('[data-essay]') : null;
    if (card) {
      e.preventDefault();
      var slug = card.getAttribute('data-essay');
      openEssay(slug);
    }
  });

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

})();
