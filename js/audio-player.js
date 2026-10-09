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
  var isPlaying = false;
  var unlocked = false;

  function init() {
    audio = (typeof document !== 'undefined' && (document.getElementById('bg-music') || document.getElementById('bg-audio'))) || null;
    controller.audio = audio;
    vinylContainer = (typeof document !== 'undefined' && (document.getElementById('vinyl-player') || document.querySelector('.vinyl-player'))) || null;
    vinylDisc = (typeof document !== 'undefined' && (document.querySelector('.vinyl-disc') || document.querySelector('.vinyl-record'))) || null;
    tonearm = (typeof document !== 'undefined' && document.querySelector('.tonearm')) || null;
    playBtn = (typeof document !== 'undefined' && (document.getElementById('vinyl-play-toggle') || document.querySelector('.vinyl-toggle-btn'))) || null;

    if (!audio) return;

    // Explicitly enforce loop property
    audio.loop = true;

    // Listen to native audio element events
    audio.addEventListener('play', function () {
      isPlaying = true;
      syncUI(true);
    });

    audio.addEventListener('pause', function () {
      isPlaying = false;
      syncUI(false);
    });

    // Seamless continuous looping restart fallback
    audio.addEventListener('ended', function () {
      if (audio) {
        audio.currentTime = 0;
        var p = audio.play();
        if (p && typeof p.catch === 'function') {
          p.catch(function () {});
        }
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
        // Toggle if clicking container unless clicked on specific sub-links
        if (e.target && e.target.tagName !== 'A') {
          toggle();
        }
      });
    }

    // Try autoplay on open + fallback to first user gesture
    setupAutoplayAndGestureFallback();
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

  function removeGestureListeners() {
    if (typeof window === 'undefined' || typeof document === 'undefined') return;
    var events = ['click', 'touchstart', 'touchend', 'pointerdown', 'keydown', 'scroll', 'wheel'];
    events.forEach(function (evt) {
      if (window.removeEventListener) window.removeEventListener(evt, onFirstGesture, true);
      if (document.removeEventListener) document.removeEventListener(evt, onFirstGesture, true);
    });
  }

  function onFirstGesture() {
    if (unlocked) {
      removeGestureListeners();
      return;
    }
    var a = (controller && controller.audio) || audio;
    if (!a || typeof a.play !== 'function') return;

    a.loop = true;
    var p = a.play();
    if (p && typeof p.then === 'function') {
      p.then(function () {
        unlocked = true;
        isPlaying = true;
        syncUI(true);
        removeGestureListeners();
      }).catch(function () {
        // Still blocked by browser policy, keep listeners active for next interaction
      });
    } else {
      unlocked = true;
      removeGestureListeners();
    }
  }

  function attachGestureFallback() {
    if (typeof window === 'undefined' || typeof document === 'undefined') return;
    var events = ['click', 'touchstart', 'touchend', 'pointerdown', 'keydown', 'scroll', 'wheel'];
    events.forEach(function (evt) {
      if (window.addEventListener) window.addEventListener(evt, onFirstGesture, { capture: true, passive: true });
      if (document.addEventListener) document.addEventListener(evt, onFirstGesture, { capture: true, passive: true });
    });
  }

  function setupAutoplayAndGestureFallback() {
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
        }).catch(function () {
          // Autoplay blocked by browser policy -> listen for first interaction anywhere
          attachGestureFallback();
        });
      } else {
        attachGestureFallback();
      }
    } catch (e) {
      attachGestureFallback();
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

    a.loop = true;
    unlocked = true;
    removeGestureListeners();

    return a.play().then(function () {
      isPlaying = true;
      syncUI(true);
    }).catch(function (err) {
      console.warn('Audio playback prevented or failed:', err);
    });
  }

  function pause() {
    var a = (this && this.audio) || controller.audio || audio;
    if (!a || typeof a.pause !== 'function') return;
    a.pause();
    isPlaying = false;
    syncUI(false);
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
