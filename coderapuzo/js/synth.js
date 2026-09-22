/**
 * Web Audio Modular Synthesizer Engine for Luis Codera Puzo
 * Inspired by analogue synthesis, pure tones and microtonality.
 */

(function () {
  'use strict';

  var ac = null;
  var masterComp = null;
  var masterGain = null;
  var tonesOn = false;

  // Harmonic overtone ratios based on microtonal and harmonic series (Sa / Fundamental A3 = 220Hz)
  // Shifted up one octave from 110Hz to 220Hz so it reproduces richly on laptop & mobile speakers
  var baseFreq = 220.0; // A3
  var ratios = [
    1.0,        // Fundamental (220 Hz)
    9 / 8,      // Major second (247.5 Hz)
    5 / 4,      // Just major third (275 Hz)
    11 / 8,     // 11th harmonic / augmented 4th (302.5 Hz)
    3 / 2,      // Perfect fifth (330 Hz)
    13 / 8,     // Neutral sixth (357.5 Hz)
    7 / 4,      // Harmonic seventh (385 Hz)
    2.0         // Octave (440 Hz)
  ];

  function ensureAc() {
    if (!ac) {
      var AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return false;
      ac = new AudioCtx();

      // Master Limiter / Compressor to avoid digital clipping while delivering full, rich volume
      masterComp = ac.createDynamicsCompressor();
      masterComp.threshold.setValueAtTime(-6, ac.currentTime);
      masterComp.knee.setValueAtTime(10, ac.currentTime);
      masterComp.ratio.setValueAtTime(5, ac.currentTime);
      masterComp.attack.setValueAtTime(0.003, ac.currentTime);
      masterComp.release.setValueAtTime(0.12, ac.currentTime);

      masterGain = ac.createGain();
      masterGain.gain.setValueAtTime(0.95, ac.currentTime);

      masterComp.connect(masterGain);
      masterGain.connect(ac.destination);
    }
    if (ac.state === 'suspended') {
      ac.resume();
    }
    return true;
  }

  /**
   * Play an analog-modeled synthetic tone
   * Uses dual oscillators (triangle + sub sine) with resonant lowpass filter & warm envelope
   */
  function playSynthTone(index, at, customFreq) {
    if (!ensureAc()) return;

    var startTime = ac.currentTime + (at || 0.01);
    var duration = 0.68;
    var freq = customFreq || (baseFreq * (ratios[index % ratios.length] || 1.0));

    // Dual Oscillators: Primary Triangle + Analog detuned Sub
    var osc1 = ac.createOscillator();
    var osc2 = ac.createOscillator();
    var filter = ac.createBiquadFilter();
    var amp = ac.createGain();

    osc1.type = 'triangle';
    osc1.frequency.setValueAtTime(freq, startTime);

    // Warm sub-fundamental with slight detuning for analog drift
    osc2.type = 'sine';
    osc2.frequency.setValueAtTime(freq * 0.5 + 0.3, startTime);

    // Resonant lowpass filter with dynamic envelope for analog punch and presence
    filter.type = 'lowpass';
    var startFilter = Math.max(Math.min(freq * 6.0, 4800), 2200);
    var endFilter = Math.max(Math.min(freq * 2.2, 1600), 700);
    filter.frequency.setValueAtTime(startFilter, startTime);
    filter.frequency.exponentialRampToValueAtTime(endFilter, startTime + duration);
    filter.Q.setValueAtTime(2.6, startTime);

    // ADSR Envelope: Significantly boosted volume (from 0.08 peak to 0.28 peak)
    amp.gain.setValueAtTime(0.0001, startTime);
    amp.gain.linearRampToValueAtTime(0.28, startTime + 0.02); // punchy, smooth attack
    amp.gain.exponentialRampToValueAtTime(0.14, startTime + 0.18); // resonant body
    amp.gain.exponentialRampToValueAtTime(0.0001, startTime + duration); // smooth release

    // Signal chain
    osc1.connect(filter);
    osc2.connect(filter);
    filter.connect(amp);
    amp.connect(masterComp || ac.destination);

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
