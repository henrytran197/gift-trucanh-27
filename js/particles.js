/**
 * Romantic Particle & Confetti Engine
 * Trúc Anh (Na) 27th Birthday Web Album
 * Canvas particle bursts (rose-gold stars, confetti, hearts) & Midnight Starfield
 */

(function () {
  'use strict';

  // =========================================================================
  // 1. STARFIELD ENGINE (Twinkling Starlight & Shooting Stars)
  // =========================================================================
  var starCanvas = document.getElementById('starfield');
  var starCtx = starCanvas ? starCanvas.getContext('2d') : null;
  var stars = [];
  var shootingStars = [];
  var starAnimId = null;

  var starColors = [
    'rgba(255, 255, 255, ',    // Diamond White
    'rgba(245, 214, 206, ',    // Soft Blush
    'rgba(243, 229, 171, ',    // Warm Champagne Gold
    'rgba(224, 168, 153, '     // Warm Rose Gold
  ];

  function resizeStarCanvas() {
    if (!starCanvas) return;
    starCanvas.width = window.innerWidth;
    starCanvas.height = window.innerHeight;
    initStars();
  }

  function initStars() {
    if (!starCanvas) return;
    stars = [];
    var count = Math.floor((starCanvas.width * starCanvas.height) / 8000);
    count = Math.max(80, Math.min(count, 180));

    for (var i = 0; i < count; i++) {
      stars.push({
        x: Math.random() * starCanvas.width,
        y: Math.random() * starCanvas.height,
        radius: Math.random() * 1.6 + 0.6,
        colorPrefix: starColors[Math.floor(Math.random() * starColors.length)],
        baseAlpha: Math.random() * 0.5 + 0.25,
        twinkleSpeed: Math.random() * 0.03 + 0.015,
        phase: Math.random() * Math.PI * 2
      });
    }
  }

  function createShootingStar() {
    if (!starCanvas) return;
    shootingStars.push({
      x: Math.random() * starCanvas.width * 0.8,
      y: Math.random() * starCanvas.height * 0.4,
      length: Math.random() * 90 + 70,
      speed: Math.random() * 8 + 10,
      angle: Math.PI / 4 + (Math.random() - 0.5) * 0.2,
      opacity: 1,
      decay: 0.02
    });
  }

  var lastShootingStarTime = Date.now();

  function updateStarfield() {
    if (!starCtx || !starCanvas) return;
    starCtx.clearRect(0, 0, starCanvas.width, starCanvas.height);

    var now = Date.now();

    // Render twinkling stars
    for (var i = 0; i < stars.length; i++) {
      var s = stars[i];
      var alpha = s.baseAlpha + Math.sin(now * s.twinkleSpeed * 0.1 + s.phase) * 0.35;
      alpha = Math.max(0.1, Math.min(alpha, 0.95));

      starCtx.beginPath();
      starCtx.arc(s.x, s.y, s.radius, 0, Math.PI * 2);
      starCtx.fillStyle = s.colorPrefix + alpha + ')';
      starCtx.shadowBlur = s.radius > 1.4 ? 4 : 0;
      starCtx.shadowColor = 'rgba(243, 229, 171, 0.5)';
      starCtx.fill();
    }
    starCtx.shadowBlur = 0;

    // Trigger occasional shooting star
    if (now - lastShootingStarTime > 5500 + Math.random() * 4000) {
      createShootingStar();
      lastShootingStarTime = now;
    }

    // Render shooting stars
    for (var j = shootingStars.length - 1; j >= 0; j--) {
      var ss = shootingStars[j];
      var tailX = ss.x - Math.cos(ss.angle) * ss.length;
      var tailY = ss.y - Math.sin(ss.angle) * ss.length;

      var grad = starCtx.createLinearGradient(tailX, tailY, ss.x, ss.y);
      grad.addColorStop(0, 'rgba(255, 255, 255, 0)');
      grad.addColorStop(1, 'rgba(243, 229, 171, ' + ss.opacity + ')');

      starCtx.beginPath();
      starCtx.moveTo(tailX, tailY);
      starCtx.lineTo(ss.x, ss.y);
      starCtx.strokeStyle = grad;
      starCtx.lineWidth = 1.8;
      starCtx.stroke();

      ss.x += Math.cos(ss.angle) * ss.speed;
      ss.y += Math.sin(ss.angle) * ss.speed;
      ss.opacity -= ss.decay;

      if (ss.opacity <= 0 || ss.x > starCanvas.width || ss.y > starCanvas.height) {
        shootingStars.splice(j, 1);
      }
    }

    starAnimId = requestAnimationFrame(updateStarfield);
  }

  if (starCanvas) {
    resizeStarCanvas();
    window.addEventListener('resize', resizeStarCanvas);
    starAnimId = requestAnimationFrame(updateStarfield);
  }

  // =========================================================================
  // 2. CELEBRATORY CONFETTI & HEARTS BURST ENGINE
  // =========================================================================
  var canvas = document.getElementById('confetti');
  if (!canvas) {
    canvas = document.getElementById('confetti-canvas');
  }

  var ctx = canvas ? canvas.getContext('2d') : null;
  var particles = [];
  var animationId = null;
  var colors = [
    '#B76E79', // Rose gold
    '#F5D6CE', // Soft blush
    '#D4AF37', // Champagne gold
    '#FF6B81', // Coral pink
    '#FFFFFF', // Starlight white
    '#FFD1DC', // Pastel rose
    '#E0A899'  // Warm peach
  ];

  function resizeCanvas() {
    if (!canvas) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  window.addEventListener('resize', resizeCanvas);
  if (canvas) {
    resizeCanvas();
  }

  function createParticle(x, y) {
    var angle = Math.random() * Math.PI * 2;
    var speed = Math.random() * 8 + 3;
    var size = Math.random() * 8 + 4;
    var type = Math.random() > 0.4 ? 'rect' : (Math.random() > 0.5 ? 'circle' : 'heart');

    return {
      x: x !== undefined ? x : canvas.width / 2,
      y: y !== undefined ? y : canvas.height / 2,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - Math.random() * 4,
      size: size,
      color: colors[Math.floor(Math.random() * colors.length)],
      alpha: 1,
      rotation: Math.random() * 360,
      vRotation: (Math.random() - 0.5) * 12,
      type: type,
      gravity: 0.18,
      drag: 0.985,
      decay: Math.random() * 0.012 + 0.008
    };
  }

  function drawHeart(c, x, y, size) {
    c.save();
    c.translate(x, y);
    c.beginPath();
    var topCurveHeight = size * 0.3;
    c.moveTo(0, topCurveHeight);
    c.bezierCurveTo(0, 0, -size / 2, 0, -size / 2, topCurveHeight);
    c.bezierCurveTo(-size / 2, (size + topCurveHeight) / 2, 0, size, 0, size);
    c.bezierCurveTo(0, size, size / 2, (size + topCurveHeight) / 2, size / 2, topCurveHeight);
    c.bezierCurveTo(size / 2, 0, 0, 0, 0, topCurveHeight);
    c.closePath();
    c.fill();
    c.restore();
  }

  function update() {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (var i = particles.length - 1; i >= 0; i--) {
      var p = particles[i];
      p.vx *= p.drag;
      p.vy = (p.vy + p.gravity) * p.drag;
      p.x += p.vx;
      p.y += p.vy;
      p.rotation += p.vRotation;
      p.alpha -= p.decay;

      if (p.alpha <= 0 || p.y > canvas.height + 20) {
        particles.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.globalAlpha = Math.max(0, p.alpha);
      ctx.fillStyle = p.color;

      if (p.type === 'heart') {
        drawHeart(ctx, p.x, p.y, p.size * 1.5);
      } else if (p.type === 'circle') {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size / 2, 0, Math.PI * 2);
        ctx.fill();
      } else {
        ctx.translate(p.x, p.y);
        ctx.rotate((p.rotation * Math.PI) / 180);
        ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 1.2);
      }
      ctx.restore();
    }

    if (particles.length > 0) {
      animationId = requestAnimationFrame(update);
    } else {
      cancelAnimationFrame(animationId);
      animationId = null;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }

  function launchConfetti(originX, originY, count) {
    if (!canvas) {
      canvas = document.getElementById('confetti') || document.getElementById('confetti-canvas');
      if (canvas) {
        ctx = canvas.getContext('2d');
        resizeCanvas();
      } else {
        return;
      }
    }

    var numParticles = count || 140;
    var x = originX !== undefined ? originX : canvas.width / 2;
    var y = originY !== undefined ? originY : canvas.height * 0.45;

    for (var i = 0; i < numParticles; i++) {
      particles.push(createParticle(x, y));
    }

    if (!animationId) {
      update();
    }
  }

  // Export globally
  window.launchConfetti = launchConfetti;
  window.createParticles = launchConfetti;
  window.confetti = {
    burst: launchConfetti,
    launch: launchConfetti
  };
})();
