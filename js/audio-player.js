/**
 * Floating Vinyl Record Player & Audio Controller
 * Trúc Anh (Na) 27th Birthday Web Album
 * Manages playback of Elvis Presley - Can't Help Falling in Love
 * Synchronizes vinyl disc rotation, rose-gold tonearm, and equalizer bars.
 * Supports autoplay on open, immediate fallback on first gesture, and seamless looping.
 */

(function () {
  'use strict';

  var audio = null;
  var vinylContainer = null;
  var vinylDisc = null;
  var tonearm = null;
  var playBtn = null;
  var promptBanner = null;
  var isPlaying = false;
  var unlocked = false;
  var audioContext = null;

  function init() {
    audio = (typeof document !== 'undefined' && (document.getElementById('bg-music') || document.getElementById('bg-audio'))) || null;
    controller.audio = audio;
    vinylContainer = (typeof document !== 'undefined' && (document.getElementById('vinyl-player') || document.querySelector('.vinyl-player'))) || null;
    vinylDisc = (typeof document !== 'undefined' && (document.querySelector('.vinyl-disc') || document.querySelector('.vinyl-record'))) || null;
    tonearm = (typeof document !== 'undefined' && document.querySelector('.tonearm')) || null;
    playBtn = (typeof document !== 'undefined' && (document.getElementById('vinyl-play-toggle') || document.querySelector('.vinyl-toggle-btn'))) || null;
    promptBanner = (typeof document !== 'undefined' && document.getElementById('audio-prompt-banner')) || null;

    if (!audio) return;

    // Enforce looping & preload buffer
    audio.loop = true;
    try {
      audio.load();
    } catch (e) {}

    // Synchronize UI on native audio events
    audio.addEventListener('play', function () {
      isPlaying = true;
      syncUI(true);
      hidePromptBanner();
    });

    audio.addEventListener('pause', function () {
      isPlaying = false;
      syncUI(false);
    });

    audio.addEventListener('ended', function () {
      if (audio) {
        audio.currentTime = 0;
        var p = audio.play();
        if (p && typeof p.catch === 'function') {
          p.catch(function () {});
        }
      }
    });

    audio.addEventListener('canplay', function () {
      if (!unlocked && !isPlaying) {
        attemptAutoplay();
      }
    });

    // Wire player click toggle
    if (playBtn) {
      playBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        toggle();
      });
    }

    if (vinylContainer) {
      vinylContainer.addEventListener('click', function (e) {
        if (e.target && e.target.tagName !== 'A') {
          toggle();
        }
      });
    }

    // Wire prompt banner click and touch
    if (promptBanner) {
      promptBanner.addEventListener('click', function (e) {
        e.stopPropagation();
        play();
      });
      promptBanner.addEventListener('touchend', function (e) {
        e.stopPropagation();
        play();
      });
    }

    // Proactively attach gesture fallback for first interaction
    attachGestureFallback();

    // Attempt direct autoplay immediately on open
    attemptAutoplay();
  }

  function hidePromptBanner() {
    if (promptBanner) {
      promptBanner.classList.add('hidden');
    }
  }

  function showPromptBanner() {
    if (promptBanner && !isPlaying) {
      promptBanner.classList.remove('hidden');
    }
  }

  function syncUI(playing) {
    if (vinylContainer) {
      if (playing) {
        vinylContainer.classList.add('is-playing');
        vinylContainer.classList.remove('is-paused');
      } else {
        vinylContainer.classList.remove('is-playing');
        vinylContainer.classList.add('is-paused');
      }
    }

    if (vinylDisc) {
      vinylDisc.style.animationPlayState = playing ? 'running' : 'paused';
      if (playing) {
        vinylDisc.classList.add('spinning');
      } else {
        vinylDisc.classList.remove('spinning');
      }
    }

    if (tonearm) {
      if (playing) {
        tonearm.classList.add('on-record');
      } else {
        tonearm.classList.remove('on-record');
      }
    }

    if (playBtn) {
      playBtn.setAttribute('aria-label', playing ? 'Tạm dừng nhạc' : 'Phát nhạc');
      var icon = playBtn.querySelector('.toggle-icon');
      if (icon) {
        icon.textContent = playing ? '⏸' : '▶';
      }
    }
  }

  function unlockAudioContext() {
    try {
      var AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        if (!audioContext) {
          audioContext = new AudioCtx();
        }
        if (audioContext.state === 'suspended') {
          audioContext.resume();
        }
      }
    } catch (e) {}
  }

  function onFirstGesture() {
    if (unlocked) {
      removeGestureListeners();
      return;
    }

    var a = (controller && controller.audio) || audio;
    if (!a || typeof a.play !== 'function') return;

    unlockAudioContext();
    a.loop = true;

    var p = a.play();
    if (p && typeof p.then === 'function') {
      p.then(function () {
        unlocked = true;
        isPlaying = true;
        syncUI(true);
        hidePromptBanner();
        removeGestureListeners();
      }).catch(function () {
        // Keep active for next valid touch/click
      });
    } else {
      unlocked = true;
      isPlaying = true;
      syncUI(true);
      hidePromptBanner();
      removeGestureListeners();
    }
  }

  function removeGestureListeners() {
    if (typeof window === 'undefined' || typeof document === 'undefined') return;
    var events = ['click', 'touchend', 'pointerup', 'keydown'];
    events.forEach(function (evt) {
      if (window.removeEventListener) window.removeEventListener(evt, onFirstGesture, true);
      if (document.removeEventListener) document.removeEventListener(evt, onFirstGesture, true);
    });
  }

  function attachGestureFallback() {
    if (typeof window === 'undefined' || typeof document === 'undefined') return;
    // Strictly avoid 'scroll', 'wheel', or passive 'touchstart' which throw NotAllowedError on iOS WebKit!
    var events = ['click', 'touchend', 'pointerup', 'keydown'];
    events.forEach(function (evt) {
      if (window.addEventListener) window.addEventListener(evt, onFirstGesture, true);
      if (document.addEventListener) document.addEventListener(evt, onFirstGesture, true);
    });
  }

  function attemptAutoplay() {
    var a = (controller && controller.audio) || audio;
    if (!a || typeof a.play !== 'function') return;

    a.loop = true;

    try {
      var p = a.play();
      if (p && typeof p.then === 'function') {
        p.then(function () {
          unlocked = true;
          isPlaying = true;
          syncUI(true);
          hidePromptBanner();
          removeGestureListeners();
        }).catch(function () {
          // Autoplay blocked by browser policy; reveal prompt banner
          showPromptBanner();
        });
      } else {
        hidePromptBanner();
      }
    } catch (e) {
      showPromptBanner();
    }
  }

  function play() {
    var a = (this && this.audio) || controller.audio || audio;
    if (!a) {
      a = (typeof document !== 'undefined' && (document.getElementById('bg-music') || document.getElementById('bg-audio'))) || null;
      if (this) this.audio = a;
      controller.audio = a;
      audio = a;
    }
    if (!a || typeof a.play !== 'function') return Promise.resolve();

    unlockAudioContext();
    a.loop = true;
    unlocked = true;
    removeGestureListeners();

    var p = a.play();
    if (p && typeof p.then === 'function') {
      return p.then(function () {
        isPlaying = true;
        syncUI(true);
        hidePromptBanner();
      }).catch(function (err) {
        console.warn('Audio playback error:', err);
        showPromptBanner();
      });
    } else {
      isPlaying = true;
      syncUI(true);
      hidePromptBanner();
      return Promise.resolve();
    }
  }

  function pause() {
    var a = (this && this.audio) || controller.audio || audio;
    if (!a || typeof a.pause !== 'function') return;
    a.pause();
    isPlaying = false;
    syncUI(false);
    unlocked = true;
    removeGestureListeners();
  }

  function toggle() {
    var a = (this && this.audio) || controller.audio || audio;
    if (!a) {
      a = (typeof document !== 'undefined' && (document.getElementById('bg-music') || document.getElementById('bg-audio'))) || null;
      if (this) this.audio = a;
      controller.audio = a;
      audio = a;
    }
    if (!a) return;

    if (a.paused) {
      play.call(this);
    } else {
      pause.call(this);
    }
  }

  // Export audioController API
  var controller = {
    audio: null,
    play: play,
    pause: pause,
    toggle: toggle,
    isPlaying: function () {
      if (!this || !this.audio) return false;
      return Boolean(this.audio && !this.audio.paused && this.audio.currentTime > 0);
    }
  };

  window.audioController = controller;

  // Auto-init when DOM ready
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  }
})();
