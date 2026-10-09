/**
 * Main Application Controller
 * Trúc Anh (Na) 27th Birthday Web Album & Level 27 Certificate
 * Coordinates gallery rendering, Hero gift opening, audio & confetti unlock,
 * scroll observers, and certificate interactions.
 */

(function () {
  'use strict';

  var chapterMeta = {
    2023: {
      title: 'Chương I • 2023: Khởi Đầu Hành Trình & Những Kỷ Niệm Ngọt Ngào',
      subtitle: '15 khoảnh khắc đầu tiên của những chuyến đi và nụ cười rạng rỡ bên nhau'
    },
    2024: {
      title: 'Chương II • 2024: Từng Bước Trưởng Thành & Những Cột Mốc Đáng Nhớ',
      subtitle: '7 khoảnh khắc ghi dấu sự kiên cường và những trải nghiệm mới'
    },
    2025: {
      title: 'Chương III • 2025: Sóng Gió Vượt Qua, Bình Yên Ở Lại',
      subtitle: '11 khoảnh khắc gắn kết sâu sắc, cùng nhau đi qua mọi thăng trầm'
    },
    2026: {
      title: 'Chương IV • 2026: Tuổi 27 Rạng Rỡ & Vững Chãi',
      subtitle: '4 khoảnh khắc hiện tại đón chào tuổi mới kiêu hãnh và an nhiên'
    }
  };

  function init() {
    setupHeroCTA();
    renderGalleryTimeline();
    setupObservers();
    setupCertificateButtons();
    setupLetterModal();
  }

  /**
   * Hero CTA Button: Triggers audio playback & particle burst synchronously
   */
  function setupHeroCTA() {
    var ctaBtn = document.getElementById('hero-cta-btn') || document.querySelector('.hero-cta');
    var giftBox = document.getElementById('gift-box') || document.querySelector('.gift-box');

    if (!ctaBtn) return;

    if (giftBox) {
      giftBox.addEventListener('click', function (e) {
        if (e.target !== ctaBtn && !ctaBtn.contains(e.target)) {
          ctaBtn.click();
        }
      });
      giftBox.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          if (e.target !== ctaBtn && !ctaBtn.contains(e.target)) {
            e.preventDefault();
            ctaBtn.click();
          }
        }
      });
    }

    ctaBtn.addEventListener('click', function (e) {
      e.preventDefault();

      // 1. Play audio synchronously inside user gesture
      if (window.audioController && typeof window.audioController.play === 'function') {
        window.audioController.play();
      } else {
        var bgMusic = document.getElementById('bg-music') || document.getElementById('bg-audio');
        if (bgMusic) {
          bgMusic.play().catch(function (err) {
            console.warn('Audio play error:', err);
          });
        }
      }

      // 2. Trigger celebratory particle burst
      if (typeof window.launchConfetti === 'function') {
        window.launchConfetti(window.innerWidth / 2, window.innerHeight * 0.45, 140);
      } else if (typeof window.createParticles === 'function') {
        window.createParticles();
      }

      // 3. Animate gift box open
      if (giftBox) {
        giftBox.classList.add('opened');
      }
      ctaBtn.classList.add('activated');
      ctaBtn.textContent = '✨ Món quà đã mở! Cùng thưởng thức nào ✨';

      // 4. Smooth scroll to 2021 Flashback after slight reveal pause
      setTimeout(function () {
        var flashback = document.getElementById('flashback-2021') || document.getElementById('flashback');
        if (flashback) {
          flashback.scrollIntoView({ behavior: 'smooth' });
        }
      }, 900);
    });
  }

  /**
   * Renders 37 photos grouped into 4 chapters dynamically from window.GALLERY_DATA
   */
  function renderGalleryTimeline() {
    var timelineContainer = document.getElementById('timeline-chapters');
    if (!timelineContainer) {
      timelineContainer = document.getElementById('timeline');
    }
    if (!timelineContainer || !window.GALLERY_DATA) return;

    var gallery = window.GALLERY_DATA;
    var chapters = [2023, 2024, 2025, 2026];

    // Group photos by year
    var grouped = { 2023: [], 2024: [], 2025: [], 2026: [] };
    gallery.forEach(function (photo, globalIndex) {
      var y = parseInt(photo.year, 10);
      if (grouped[y]) {
        photo._globalIndex = globalIndex;
        grouped[y].push(photo);
      }
    });

    timelineContainer.innerHTML = '';

    chapters.forEach(function (year) {
      var photos = grouped[year] || [];
      var meta = chapterMeta[year] || { title: 'Năm ' + year, subtitle: '' };

      var chapterEl = document.createElement('section');
      chapterEl.className = 'timeline-chapter';
      chapterEl.id = 'chapter-' + year;

      var headerEl = document.createElement('div');
      headerEl.className = 'chapter-header';
      headerEl.innerHTML =
        '<div class="chapter-badge"><span class="chapter-year">' + year + '</span></div>' +
        '<h3 class="chapter-title">' + meta.title + '</h3>' +
        '<p class="chapter-subtitle">' + meta.subtitle + '</p>';
      chapterEl.appendChild(headerEl);

      var gridEl = document.createElement('div');
      gridEl.className = 'polaroid-grid';

      photos.forEach(function (photo, idx) {
        var card = document.createElement('article');
        var tiltClass = idx % 2 === 0 ? 'polaroid-tilt-left' : 'polaroid-tilt-right';
        card.className = 'polaroid-card ' + tiltClass;
        card.setAttribute('data-index', photo._globalIndex);
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        card.setAttribute('aria-label', 'Xem ảnh: ' + (photo.caption || 'Kỷ niệm ' + year));

        var washiColor = (idx % 3 === 0) ? 'washi-rose' : ((idx % 3 === 1) ? 'washi-gold' : 'washi-blush');

        card.innerHTML =
          '<div class="washi-tape ' + washiColor + '"></div>' +
          '<div class="polaroid-image-wrapper">' +
            '<img class="polaroid-image" src="' + photo.src + '" alt="' + (photo.caption || 'Kỷ niệm sinh nhật') + '" loading="lazy">' +
            '<div class="polaroid-overlay"><span class="zoom-icon">🔍 Phóng to</span></div>' +
          '</div>' +
          '<div class="polaroid-caption-wrapper">' +
            '<p class="polaroid-caption">' + photo.caption + '</p>' +
            '<span class="polaroid-date">' + photo.date + '</span>' +
          '</div>';

        // Polaroid card click wires to lightbox.open(index)
        card.addEventListener('click', function () {
          if (window.lightbox && typeof window.lightbox.open === 'function') {
            window.lightbox.open(photo._globalIndex);
          }
        });

        card.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            if (window.lightbox && typeof window.lightbox.open === 'function') {
              window.lightbox.open(photo._globalIndex);
            }
          }
        });

        gridEl.appendChild(card);
      });

      chapterEl.appendChild(gridEl);
      timelineContainer.appendChild(chapterEl);
    });
  }

  /**
   * Intersection Observers for animations and fireworks trigger
   */
  function setupObservers() {
    // Fireworks observer when certificate comes into view
    var certSection = document.getElementById('certificate-level-27') || document.querySelector('.certificate-section');
    if (certSection && 'IntersectionObserver' in window) {
      var firedFireworks = false;
      var certObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting && !firedFireworks) {
            firedFireworks = true;
            if (window.fireworks && typeof window.fireworks.launch === 'function') {
              window.fireworks.launch(5);
            }
          }
        });
      }, { threshold: 0.35 });

      certObserver.observe(certSection);
    }
  }

  /**
   * Certificate interactions: Print button & Fireworks trigger button
   */
  function setupCertificateButtons() {
    var printBtn = document.getElementById('print-btn') || document.querySelector('.btn-print');
    if (printBtn) {
      printBtn.addEventListener('click', function (e) {
        e.preventDefault();
        printCertificate();
      });
    }

    var fireworksBtn = document.getElementById('fireworks-trigger-btn') || document.querySelector('.btn-fireworks');
    if (fireworksBtn) {
      fireworksBtn.addEventListener('click', function (e) {
        e.preventDefault();
        if (window.fireworks && typeof window.fireworks.launch === 'function') {
          window.fireworks.launch(6);
        }
      });
    }
  }

  /**
   * 2021 Letter Modal viewer
   */
  function setupLetterModal() {
    var openBtn = document.getElementById('open-letter-2021-btn');
    var modal = document.getElementById('letter-2021-modal');
    var closeBtn = document.getElementById('close-letter-2021-btn');

    if (openBtn && modal) {
      openBtn.addEventListener('click', function (e) {
        e.preventDefault();
        modal.classList.add('active');
        modal.setAttribute('aria-hidden', 'false');
      });
    }

    if (closeBtn && modal) {
      closeBtn.addEventListener('click', function (e) {
        e.preventDefault();
        modal.classList.remove('active');
        modal.setAttribute('aria-hidden', 'true');
      });
    }

    if (modal) {
      modal.addEventListener('click', function (e) {
        if (e.target === modal || e.target.classList.contains('modal-backdrop')) {
          modal.classList.remove('active');
          modal.setAttribute('aria-hidden', 'true');
        }
      });
    }
  }

  /**
   * Print Certificate Trigger API
   */
  function printCertificate() {
    window.print();
  }

  // Export globally
  window.printCertificate = printCertificate;

  // Initialize on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
