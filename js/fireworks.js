/**
 * Celebration Fireworks Engine
 * Trúc Anh (Na) 27th Birthday Web Album
 * Canvas fireworks with sparkling trails (rose-gold, gold, crimson, champagne)
 */

(function () {
  'use strict';

  var canvas = null;
  var ctx = null;
  var rockets = [];
  var particles = [];
  var animationId = null;
  var isAutoLaunching = false;
  var autoLaunchTimer = null;

  var colors = [
    '#B76E79', // Rose gold
    '#D4AF37', // Gold
    '#FF3366', // Crimson Ruby
    '#FFD1DC', // Pastel Pink
    '#F5D6CE', // Champagne Peach
    '#FFFFFF', // Sparkling White
    '#FFB347'  // Warm Amber
  ];

  function init() {
    canvas = document.getElementById('fireworks') || document.getElementById('fireworks-canvas');
    if (!canvas) return;

    ctx = canvas.getContext('2d');
    resize();
    window.addEventListener('resize', resize);
  }

  function resize() {
    if (!canvas) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function createRocket(targetX, targetY) {
    if (!canvas) return;
    var startX = Math.random() * (canvas.width * 0.8) + (canvas.width * 0.1);
    var startY = canvas.height;
    var endX = targetX !== undefined ? targetX : Math.random() * (canvas.width * 0.7) + (canvas.width * 0.15);
    var endY = targetY !== undefined ? targetY : Math.random() * (canvas.height * 0.45) + (canvas.height * 0.1);

    var angle = Math.atan2(endY - startY, endX - startX);
    var distance = Math.hypot(endX - startX, endY - startY);
    var speed = 14 + Math.random() * 4;

    rockets.push({
      x: startX,
      y: startY,
      targetX: endX,
      targetY: endY,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      trail: [],
      color: colors[Math.floor(Math.random() * colors.length)],
      distanceTraveled: 0,
      totalDistance: distance
    });
  }

  function explodeRocket(x, y, color) {
    var count = 60 + Math.floor(Math.random() * 40);
    var baseColor = color || colors[Math.floor(Math.random() * colors.length)];

    for (var i = 0; i < count; i++) {
      var angle = Math.random() * Math.PI * 2;
      var speed = Math.random() * 6 + 1.5;

      particles.push({
        x: x,
        y: y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        alpha: 1,
        decay: Math.random() * 0.018 + 0.012,
        color: Math.random() > 0.3 ? baseColor : colors[Math.floor(Math.random() * colors.length)],
        size: Math.random() * 2.5 + 1.5,
        gravity: 0.07,
        sparkle: Math.random() > 0.5
      });
    }
  }

  function update() {
    if (!ctx || !canvas) return;

    ctx.globalCompositeOperation = 'destination-out';
    ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.globalCompositeOperation = 'lighter';

    // Update rockets
    for (var i = rockets.length - 1; i >= 0; i--) {
      var r = rockets[i];
      var step = Math.hypot(r.vx, r.vy);
      r.distanceTraveled += step;
      r.x += r.vx;
      r.y += r.vy;

      // Draw rocket trail
      ctx.beginPath();
      ctx.arc(r.x, r.y, 2.5, 0, Math.PI * 2);
      ctx.fillStyle = r.color;
      ctx.fill();

      if (r.distanceTraveled >= r.totalDistance || r.vy >= 0 || r.y <= r.targetY) {
        explodeRocket(r.x, r.y, r.color);
        rockets.splice(i, 1);
      }
    }

    // Update particles
    for (var j = particles.length - 1; j >= 0; j--) {
      var p = particles[j];
      p.x += p.vx;
      p.y += p.vy;
      p.vy += p.gravity;
      p.vx *= 0.98;
      p.alpha -= p.decay;

      if (p.alpha <= 0) {
        particles.splice(j, 1);
        continue;
      }

      ctx.save();
      ctx.globalAlpha = p.alpha;
      ctx.fillStyle = p.color;

      if (p.sparkle && Math.random() > 0.4) {
        ctx.fillStyle = '#FFFFFF';
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    if (rockets.length > 0 || particles.length > 0) {
      animationId = requestAnimationFrame(update);
    } else {
      cancelAnimationFrame(animationId);
      animationId = null;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }

  function launch(count) {
    if (!canvas) init();
    if (!canvas) return;

    var numRockets = count || 4;
    for (var i = 0; i < numRockets; i++) {
      setTimeout(function () {
        createRocket();
        if (!animationId) {
          update();
        }
      }, i * 280);
    }
  }

  function startContinuousShow(durationMs) {
    if (isAutoLaunching) return;
    isAutoLaunching = true;
    var duration = durationMs || 6000;
    var startTime = Date.now();

    launch(3);
    autoLaunchTimer = setInterval(function () {
      if (Date.now() - startTime > duration) {
        clearInterval(autoLaunchTimer);
        isAutoLaunching = false;
        return;
      }
      createRocket();
      if (!animationId) {
        update();
      }
    }, 450);
  }

  // Auto-init when DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export fireworks API
  window.fireworks = {
    launch: launch,
    startFireworks: launch,
    triggerFireworks: launch,
    startContinuousShow: startContinuousShow
  };
  window.launchFireworks = launch;
})();
