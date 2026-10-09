/**
 * Floating Vinyl Record Player & Audio Controller
 * Trúc Anh (Na) 27th Birthday Web Album
 * Manages playback of Elvis Presley - Can't Help Falling in Love
 * Synchronizes vinyl disc rotation, rose-gold tonearm, and equalizer bars.
 */

(function () {
  'use strict';

  var audio = null;
  var vinylContainer = null;
  var vinylDisc = null;
  var tonearm = null;
  var playBtn = null;
  var isPlaying = false;

  function init() {
    audio = document.getElementById('bg-music') || document.getElementById('bg-audio');
    controller.audio = audio;
    vinylContainer = document.getElementById('vinyl-player') || document.querySelector('.vinyl-player');
    vinylDisc = document.querySelector('.vinyl-disc') || document.querySelector('.vinyl-record');
    tonearm = document.querySelector('.tonearm');
    playBtn = document.getElementById('vinyl-play-toggle') || document.querySelector('.vinyl-toggle-btn');

    if (!audio) return;

    // Listen to native audio element events
    audio.addEventListener('play', function () {
      isPlaying = true;
      syncUI(true);
    });

    audio.addEventListener('pause', function () {
      isPlaying = false;
      syncUI(false);
    });

    audio.addEventListener('ended', function () {
      isPlaying = false;
      syncUI(false);
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
        if (e.target.tagName !== 'A') {
          toggle();
        }
      });
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

  function play() {
    var a = (this && this.audio) || controller.audio || audio;
    if (!a) {
      a = document.getElementById('bg-music') || document.getElementById('bg-audio');
      if (this) this.audio = a;
      controller.audio = a;
      audio = a;
    }
    if (!a || typeof a.play !== 'function') return Promise.resolve();

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
      a = document.getElementById('bg-music') || document.getElementById('bg-audio');
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
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
