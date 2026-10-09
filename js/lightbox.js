/**
 * Full-Screen HD Lightbox Module
 * Trúc Anh (Na) 27th Birthday Web Album
 * High-definition viewer with keyboard shortcuts, touch swipe, and preloading.
 */

(function () {
  'use strict';

  var currentIndex = 0;
  var gallery = [];
  var lightboxEl = null;
  var imageEl = null;
  var captionEl = null;
  var dateEl = null;
  var counterEl = null;
  var touchStartX = 0;
  var touchStartY = 0;
  var previousBodyOverflow = '';

  function init() {
    lightboxEl = document.getElementById('lightbox') || document.getElementById('photo-lightbox');
    if (!lightboxEl) return;

    imageEl = lightboxEl.querySelector('.lightbox-image') || document.getElementById('lightbox-img');
    captionEl = lightboxEl.querySelector('.lightbox-caption') || document.getElementById('lightbox-caption');
    dateEl = lightboxEl.querySelector('.lightbox-date') || document.getElementById('lightbox-date');
    counterEl = lightboxEl.querySelector('.lightbox-counter') || document.getElementById('lightbox-counter');

    // Wire close button
    var closeBtn = lightboxEl.querySelector('.lightbox-close') || document.getElementById('lightbox-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        close();
      });
    }

    // Wire next / prev buttons
    var nextBtn = lightboxEl.querySelector('.lightbox-next') || document.getElementById('lightbox-next-btn');
    if (nextBtn) {
      nextBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        next();
      });
    }

    var prevBtn = lightboxEl.querySelector('.lightbox-prev') || document.getElementById('lightbox-prev-btn');
    if (prevBtn) {
      prevBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        prev();
      });
    }

    // Backdrop click closes lightbox
    lightboxEl.addEventListener('click', function (e) {
      if (e.target === lightboxEl || e.target.classList.contains('lightbox-backdrop') || e.target.classList.contains('lightbox-container')) {
        close();
      }
    });

    // Keyboard navigation
    window.addEventListener('keydown', function (e) {
      if (!lightboxEl.classList.contains('active') && lightboxEl.style.display !== 'flex' && lightboxEl.style.display !== 'block') {
        return;
      }

      if (e.key === 'ArrowRight' || e.keyCode === 39) {
        next();
      } else if (e.key === 'ArrowLeft' || e.keyCode === 37) {
        prev();
      } else if (e.key === 'Escape' || e.keyCode === 27) {
        close();
      }
    });

    // Touch swipe gestures
    lightboxEl.addEventListener('touchstart', function (e) {
      if (e.touches && e.touches.length > 0) {
        touchStartX = e.touches[0].clientX;
        touchStartY = e.touches[0].clientY;
      }
    }, { passive: true });

    lightboxEl.addEventListener('touchend', function (e) {
      if (!e.changedTouches || e.changedTouches.length === 0) return;
      var deltaX = e.changedTouches[0].clientX - touchStartX;
      var deltaY = e.changedTouches[0].clientY - touchStartY;

      if (Math.abs(deltaX) > 50 && Math.abs(deltaX) > Math.abs(deltaY)) {
        if (deltaX < 0) {
          next(); // Swipe left -> Next
        } else {
          prev(); // Swipe right -> Prev
        }
      }
    }, { passive: true });
  }

  function getGallery() {
    if (window.GALLERY_DATA && window.GALLERY_DATA.length > 0) {
      return window.GALLERY_DATA;
    }
    return gallery;
  }

  function preloadAdjacent(index, len) {
    var nextIdx = (index + 1) % len;
    var prevIdx = (index - 1 + len) % len;
    var data = getGallery();
    if (data[nextIdx] && data[nextIdx].src) {
      var imgNext = new Image();
      imgNext.src = data[nextIdx].src;
    }
    if (data[prevIdx] && data[prevIdx].src) {
      var imgPrev = new Image();
      imgPrev.src = data[prevIdx].src;
    }
  }

  function updateView() {
    var data = getGallery();
    if (!data || data.length === 0) return;

    var item = data[currentIndex];
    if (!item) return;

    if (imageEl) {
      imageEl.src = item.src;
      imageEl.alt = item.caption || 'Kỷ niệm sinh nhật Trúc Anh';
    }

    if (captionEl) {
      captionEl.textContent = item.caption || '';
    }

    if (dateEl) {
      dateEl.textContent = item.date || item.year || '';
    }

    if (counterEl) {
      counterEl.textContent = (currentIndex + 1) + ' / ' + data.length;
    }

    preloadAdjacent(currentIndex, data.length);
  }

  function isLightboxOpen() {
    return Boolean(lightboxEl && lightboxEl.classList.contains('active'));
  }

  function open(index) {
    if (!lightboxEl) {
      init();
    }
    if (!lightboxEl) return;

    var data = getGallery();
    var idx = typeof index === 'number' ? index : parseInt(index, 10);
    if (isNaN(idx) || idx < 0) idx = 0;
    if (data.length > 0 && idx >= data.length) idx = data.length - 1;

    if (isLightboxOpen() && currentIndex === idx) {
      return;
    }

    currentIndex = idx;

    // Only record previous body overflow if lightbox is not already open
    if (!isLightboxOpen()) {
      previousBodyOverflow = document.body ? document.body.style.overflow : '';
      if (document.body) {
        document.body.style.overflow = 'hidden';
      }
    }

    lightboxEl.classList.add('active');
    lightboxEl.setAttribute('aria-hidden', 'false');

    updateView();
  }

  function close() {
    if (!lightboxEl) return;
    lightboxEl.classList.remove('active');
    lightboxEl.setAttribute('aria-hidden', 'true');
    if (document.body) {
      document.body.style.overflow = previousBodyOverflow || '';
    }
  }

  function next() {
    var data = getGallery();
    if (!data || data.length === 0) return;
    currentIndex = (currentIndex + 1) % data.length;
    updateView();
  }

  function prev() {
    var data = getGallery();
    if (!data || data.length === 0) return;
    currentIndex = (currentIndex - 1 + data.length) % data.length;
    updateView();
  }

  // Auto-init when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export lightbox interface
  window.lightbox = {
    open: open,
    close: close,
    next: next,
    prev: prev,
    getCurrentIndex: function () { return currentIndex; },
    isOpen: isLightboxOpen
  };
})();
