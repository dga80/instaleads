/**
 * Web Audio Modular Synthesizer Engine for Luis Codera Puzo
 * Inspired by analogue synthesis, pure tones and microtonality.
 */

(function () {
  'use strict';

  var ac = null;
  var tonesOn = false;

  // Harmonic overtone ratios based on microtonal and harmonic series (Sa / Fundamental A2 = 110Hz)
  var baseFreq = 110.0; // A2
  var ratios = [
    1.0,        // Fundamental (110 Hz)
    9 / 8,      // Major second (123.75 Hz)
    5 / 4,      // Just major third (137.5 Hz)
    11 / 8,     // 11th harmonic / augmented 4th (151.25 Hz)
    3 / 2,      // Perfect fifth (165 Hz)
    13 / 8,     // Neutral sixth (178.75 Hz)
    7 / 4,      // Harmonic seventh (192.5 Hz)
    2.0         // Octave (220 Hz)
  ];

  function ensureAc() {
    if (!ac) {
      var AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return false;
      ac = new AudioCtx();
    }
    if (ac.state === 'suspended') {
      ac.resume();
    }
    return true;
  }

  /**
   * Play an analog-modeled synthetic tone
   * Uses dual oscillators (triangle + sub sine) with a gentle resonant lowpass filter
   */
  function playSynthTone(index, at, customFreq) {
    if (!ensureAc()) return;

    var startTime = ac.currentTime + (at || 0.01);
    var duration = 0.55;
    var freq = customFreq || (baseFreq * (ratios[index % ratios.length] || 1.0));

    // Dual Oscillators: Primary Triangle + Sub Sine
    var osc1 = ac.createOscillator();
    var osc2 = ac.createOscillator();
    var filter = ac.createBiquadFilter();
    var amp = ac.createGain();

    osc1.type = 'triangle';
    osc1.frequency.setValueAtTime(freq, startTime);

    osc2.type = 'sine';
    osc2.frequency.setValueAtTime(freq * 0.5, startTime); // warm sub-octave

    // Lowpass filter with mild analog warmth
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(Math.min(freq * 4.5, 3200), startTime);
    filter.frequency.exponentialRampToValueAtTime(Math.min(freq * 1.8, 1200), startTime + duration);
    filter.Q.setValueAtTime(2.2, startTime);

    // ADSR Envelope
    amp.gain.setValueAtTime(0.0001, startTime);
    amp.gain.linearRampToValueAtTime(0.08, startTime + 0.025); // quick smooth attack
    amp.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

    // Signal chain
    osc1.connect(filter);
    osc2.connect(filter);
    filter.connect(amp);
    amp.connect(ac.destination);

    osc1.start(startTime);
    osc2.start(startTime);
    osc1.stop(startTime + duration + 0.05);
    osc2.stop(startTime + duration + 0.05);
  }

  /**
   * Play an ascending harmonic arpeggio (The Overtone Series)
   */
  function playSequence(callback) {
    if (!ensureAc()) return;
    for (var i = 0; i < 8; i++) {
      playSynthTone(i, 0.04 + i * 0.22);
    }
    if (typeof callback === 'function') {
      setTimeout(callback, 50 + 8 * 220 + 200);
    }
  }

  // Hook into DOM
  window.SynthEngine = {
    ensureAc: ensureAc,
    playTone: playSynthTone,
    playSequence: playSequence,
    isTonesOn: function () { return tonesOn; },
    toggleTones: function () {
      tonesOn = !tonesOn;
      return tonesOn;
    }
  };

})();
