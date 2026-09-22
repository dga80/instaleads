/**
 * Interactive Soundwave / Oscilloscope Canvas for Luis Codera Puzo
 * An evolving modular oscillator wave settling into a distilled structural grid.
 */

(function () {
  'use strict';

  var cv = document.getElementById('cv');
  if (!cv) return;

  var cx = cv.getContext('2d');
  var RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var FINE = matchMedia('(pointer: fine)').matches;

  var W = 0, H = 0;
  var parts = [];
  var N = 220;
  var gx = 0, gy = 0, gw = 0, gh = 0, cw = 0, chh = 0, wcY = 0, wAmp = 0;

  function layoutGrid() {
    if (W > 720) {
      gx = W * 0.48;
      gw = W * 0.45;
      gy = H * 0.25;
      gh = H * 0.48;
      wcY = H * 0.58;
      wAmp = H * 0.12;
    } else {
      gx = W * 0.06;
      gw = W * 0.88;
      gy = H * 0.08;
      gh = H * 0.28;
      wcY = H * 0.20;
      wAmp = H * 0.06;
    }
    cw = gw / 8;
    chh = gh / 5;
  }

  function sizeCv() {
    var d = Math.min(window.devicePixelRatio || 1, 2);
    W = cv.clientWidth;
    H = cv.clientHeight;
    cv.width = Math.max(1, W * d);
    cv.height = Math.max(1, H * d);
    cx.setTransform(d, 0, 0, d, 0, 0);
    layoutGrid();
  }

  // Initialize particle points for wave synthesis
  for (var i = 0; i < N; i++) {
    parts.push({
      fx: Math.random(),
      ph: Math.random() * Math.PI * 2,
      sp: 0.5 + Math.random() * 0.9,
      am: 0.4 + Math.random() * 0.8,
      cell: i % 40,
      jx: (Math.random() - 0.5),
      jy: (Math.random() - 0.5),
      ox: 0,
      oy: 0
    });
  }

  var pTrack = false, px = -1e4, py = -1e4;
  if (FINE && !RM) {
    var hero = document.getElementById('ground');
    if (hero) {
      var stick = hero.querySelector('.sticky');
      if (stick) {
        stick.addEventListener('pointermove', function (e) {
          var r = cv.getBoundingClientRect();
          px = e.clientX - r.left;
          py = e.clientY - r.top;
          pTrack = true;
        }, { passive: true });
        stick.addEventListener('pointerleave', function () {
          pTrack = false;
        }, { passive: true });
      }
    }
  }

  function waveY(x, t, ph, am) {
    return wcY + Math.sin(x * 0.0055 + t * 0.75 + ph) * wAmp * am
      + Math.sin(x * 0.012 - t * 0.5) * (wAmp * 0.25);
  }

  function draw(p, t) {
    cx.clearRect(0, 0, W, H);
    var e = p * p * (3 - 2 * p); // smoothstep

    // Faint guide wave (oscilloscope line)
    if (e < 0.985) {
      cx.beginPath();
      for (var x = 0; x <= W; x += 12) {
        var y = waveY(x, t, 0, 0.95);
        if (x === 0) cx.moveTo(x, y);
        else cx.lineTo(x, y);
      }
      cx.strokeStyle = 'rgba(237, 232, 220, ' + (0.12 * (1 - e)) + ')';
      cx.lineWidth = 1;
      cx.stroke();
    }

    // Settling modular structural matrix / pitch grid
    if (e > 0.02) {
      cx.strokeStyle = 'rgba(217, 164, 68, ' + (0.22 * e) + ')';
      cx.lineWidth = 1;
      cx.strokeRect(gx, gy, gw, gh);

      for (var c = 1; c < 8; c++) {
        cx.beginPath();
        cx.moveTo(gx + c * cw, gy);
        cx.lineTo(gx + c * cw, gy + gh);
        cx.strokeStyle = 'rgba(217, 164, 68, ' + ((c === 4 || c === 6 ? 0.22 : 0.09) * e) + ')';
        cx.stroke();
      }
      for (var r = 1; r < 5; r++) {
        cx.beginPath();
        cx.moveTo(gx, gy + r * chh);
        cx.lineTo(gx + gw, gy + r * chh);
        cx.strokeStyle = 'rgba(217, 164, 68, ' + (0.08 * e) + ')';
        cx.stroke();
      }
    }

    var infl = pTrack ? (1 - e * 0.55) : 0;
    for (var k = 0; k < N; k++) {
      var q = parts[k];
      var wx = (q.fx * W + t * 20 * q.sp) % W;
      if (wx < 0) wx += W;
      var wy = waveY(wx, t, q.ph, q.am) + q.jy * 12;

      var col = q.cell % 8;
      var row = (q.cell / 8) | 0;
      var sx = gx + (col + 0.5) * cw + q.jx * cw * 0.35;
      var sy = gy + (row + 0.5) * chh + q.jy * chh * 0.35;

      var xx = wx + (sx - wx) * e;
      var yy = wy + (sy - wy) * e;

      var tox = 0, toy = 0;
      if (infl > 0) {
        var dx = xx - px, dy = yy - py;
        var d2 = dx * dx + dy * dy;
        if (d2 < 8500 && d2 > 0.01) {
          var d = Math.sqrt(d2);
          var f = (1 - d / 92) * 9 * infl;
          tox = (dx / d) * f;
          toy = (dy / d) * f;
        }
      }

      q.ox += (tox - q.ox) * 0.14;
      q.oy += (toy - q.oy) * 0.14;
      xx += q.ox;
      yy += q.oy;

      cx.beginPath();
      cx.arc(xx, yy, 1.4 + e * 0.8, 0, 6.2832);
      cx.fillStyle = 'rgba(217, 164, 68, ' + (0.32 + 0.55 * e) + ')';
      cx.fill();
    }
  }

  window.HeroCanvas = {
    sizeCv: sizeCv,
    draw: draw,
    isRM: RM
  };

  window.addEventListener('resize', sizeCv, { passive: true });
})();
