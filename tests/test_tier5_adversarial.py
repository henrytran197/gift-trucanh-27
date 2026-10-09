"""
Tier 5: Adversarial Stress & Hardening Coverage Suite
Validates white-box edge cases and hardening refinements identified during empirical stress testing:
1. Re-entrant Lightbox open calls do not permanently lock body scroll overflow.
2. Direct clicks on #gift-box container element delegate to CTA unlock.
3. Audio controller handles uninitialized/null audio elements without throwing errors.
4. Dedicated print stylesheet enforces page-break-inside avoid, viewport bounds, and total web chrome isolation.
5. All 37 gallery photos have valid dimensions > 0, aspect ratios, and payload bounds.
"""

import json
import re
import subprocess
import unittest
from pathlib import Path
from PIL import Image

from tests.test_helpers import (
    PROJECT_ROOT,
    extract_gallery_data,
    get_image_info,
)


class TestTier5AdversarialStress(unittest.TestCase):
    """Test suite for Tier 5 Adversarial Stress & Hardening Refinements."""

    def test_consecutive_lightbox_open_scroll_unlock(self):
        """
        Adversarial Test 1: Rapid consecutive Lightbox open() calls verify
        body scroll unlocks correctly on close().
        """
        lightbox_js = PROJECT_ROOT / "js" / "lightbox.js"
        self.assertTrue(lightbox_js.exists(), "lightbox.js missing")
        lb_code = lightbox_js.read_text(encoding="utf-8")

        # 1. Static code verification: previousBodyOverflow must only be recorded when not already active/open
        guard_pattern = bool(re.search(r'!\s*(?:isLightboxOpen|lightboxEl\.classList\.contains\([\'"]active[\'"]\))', lb_code))
        self.assertTrue(guard_pattern, "previousBodyOverflow is captured unconditionally without checking if already open")

        # 2. Dynamic Node.js simulation: consecutive open() calls followed by close()
        node_script = f"""
const vm = require('vm');

class Element {{
  constructor(tag, id, cls) {{
    this.tagName = tag.toUpperCase();
    this.id = id || '';
    this.className = cls || '';
    this._classes = new Set((cls || '').split(' ').filter(Boolean));
    this.classList = {{
      contains: (c) => this._classes.has(c),
      add: (c) => this._classes.add(c),
      remove: (c) => this._classes.delete(c)
    }};
    this.style = {{ overflow: '' }};
    this.listeners = {{}};
    this.children = [];
  }}
  addEventListener(evt, fn) {{
    this.listeners[evt] = this.listeners[evt] || [];
    this.listeners[evt].push(fn);
  }}
  dispatchEvent(evt) {{
    evt.target = evt.target || this;
    if (this.listeners[evt.type]) {{
      for (const fn of this.listeners[evt.type]) fn(evt);
    }}
  }}
  setAttribute(k, v) {{ this[k] = v; }}
  getAttribute(k) {{ return this[k]; }}
  querySelector() {{ return null; }}
  querySelectorAll() {{ return []; }}
}}

const body = new Element('body');
body.style.overflow = '';
const lightboxEl = new Element('div', 'lightbox');

const doc = {{
  body: body,
  readyState: 'complete',
  getElementById(id) {{
    if (id === 'lightbox' || id === 'photo-lightbox') return lightboxEl;
    return null;
  }},
  querySelector() {{ return null; }},
  querySelectorAll() {{ return []; }},
  addEventListener(evt, fn) {{ body.addEventListener(evt, fn); }}
}};

const win = {{
  document: doc,
  addEventListener(evt, fn) {{ body.addEventListener(evt, fn); }},
  GALLERY_DATA: [
    {{ src: 'images/IMG_3328.jpg', caption: 'Photo 1', year: 2023 }},
    {{ src: 'images/IMG_3329.jpg', caption: 'Photo 2', year: 2023 }}
  ]
}};

const ctx = vm.createContext({{
  window: win,
  document: doc,
  console: console,
  Image: function() {{ this.src = ''; }},
  Boolean: Boolean,
  parseInt: parseInt,
  isNaN: isNaN
}});

vm.runInContext({json.dumps(lb_code)}, ctx);

// Scenario A: Starting with default empty overflow
doc.body.style.overflow = '';
win.lightbox.open(0);
if (doc.body.style.overflow !== 'hidden') throw new Error('Body overflow should be hidden after first open, got: ' + doc.body.style.overflow);

// Consecutive re-entrant open calls
win.lightbox.open(0);
win.lightbox.open(1);
win.lightbox.open(0);

// Close lightbox
win.lightbox.close();
if (doc.body.style.overflow !== '') throw new Error('Body overflow not restored to empty string on close, got: ' + doc.body.style.overflow);

// Scenario B: Starting with preexisting custom overflow 'auto'
doc.body.style.overflow = 'auto';
win.lightbox.open(0);
if (doc.body.style.overflow !== 'hidden') throw new Error('Body overflow should be hidden when opened');
win.lightbox.open(1);
win.lightbox.close();
if (doc.body.style.overflow !== 'auto') throw new Error('Preexisting body overflow auto not restored on close, got: ' + doc.body.style.overflow);

console.log('SUCCESS');
"""
        proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Lightbox re-entrant test failed: {proc.stderr}\n{proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_gift_box_container_click_unlock_delegation(self):
        """
        Adversarial Test 2: Clicking #gift-box container element triggers
        unlock just like the button.
        """
        app_js = PROJECT_ROOT / "js" / "app.js"
        self.assertTrue(app_js.exists(), "app.js missing")
        app_code = app_js.read_text(encoding="utf-8")

        # 1. Static code check: giftBox listener delegating to ctaBtn.click()
        has_gift_box_listener = bool(re.search(r'giftBox\.addEventListener\s*\(\s*[\'"]click[\'"]', app_code))
        self.assertTrue(has_gift_box_listener, "giftBox container missing click event listener in app.js")

        has_delegation = bool(re.search(r'ctaBtn\.click\s*\(\s*\)', app_code))
        self.assertTrue(has_delegation, "giftBox click does not delegate to ctaBtn.click()")

        # 2. Dynamic Node.js DOM simulation
        node_script = f"""
const vm = require('vm');

class Element {{
  constructor(tag, id, cls) {{
    this.tagName = tag.toUpperCase();
    this.id = id || '';
    this.className = cls || '';
    this._classes = new Set((cls || '').split(' ').filter(Boolean));
    this.classList = {{
      contains: (c) => this._classes.has(c),
      add: (c) => this._classes.add(c),
      remove: (c) => this._classes.delete(c)
    }};
    this.listeners = {{}};
    this.children = [];
    this.parentNode = null;
  }}
  addEventListener(evt, fn) {{
    this.listeners[evt] = this.listeners[evt] || [];
    this.listeners[evt].push(fn);
  }}
  dispatchEvent(evt) {{
    evt.target = evt.target || this;
    if (this.listeners[evt.type]) {{
      for (const fn of this.listeners[evt.type]) fn(evt);
    }}
  }}
  click() {{
    this.dispatchEvent({{ type: 'click', target: this, preventDefault: () => {{}} }});
  }}
  contains(el) {{ return this.children.includes(el); }}
  setAttribute(k, v) {{ this[k] = v; }}
  getAttribute(k) {{ return this[k]; }}
  appendChild(c) {{ c.parentNode = this; this.children.push(c); }}
}}

const giftBoxEl = new Element('div', 'gift-box');
const ctaEl = new Element('button', 'hero-cta-btn');
giftBoxEl.appendChild(ctaEl);

let ctaClicked = 0;
ctaEl.addEventListener('click', (e) => {{
  ctaClicked++;
}});

const doc = {{
  readyState: 'complete',
  getElementById(id) {{
    if (id === 'gift-box') return giftBoxEl;
    if (id === 'hero-cta-btn') return ctaEl;
    return null;
  }},
  querySelector() {{ return null; }},
  querySelectorAll() {{ return []; }},
  addEventListener() {{}}
}};

const win = {{
  document: doc,
  addEventListener() {{}},
  audioController: {{ play: () => {{}} }},
  launchConfetti: () => {{}}
}};

const ctx = vm.createContext({{
  window: win,
  document: doc,
  console: console,
  setTimeout: (fn) => fn(),
  Boolean: Boolean
}});

vm.runInContext({json.dumps(app_code)}, ctx);

// Dispatch direct click on outer gift-box container (outside cta button)
giftBoxEl.dispatchEvent({{ type: 'click', target: giftBoxEl, preventDefault: () => {{}} }});

if (ctaClicked !== 1) {{
  throw new Error('Clicking gift-box container failed to delegate click to CTA button. ctaClicked: ' + ctaClicked);
}}

console.log('SUCCESS');
"""
        proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Gift box delegation test failed: {proc.stderr}\n{proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_audio_controller_handles_null_uninitialized(self):
        """
        Adversarial Test 3: Audio controller handles uninitialized/null audio
        element without throwing errors.
        """
        audio_js = PROJECT_ROOT / "js" / "audio-player.js"
        self.assertTrue(audio_js.exists(), "audio-player.js missing")
        audio_code = audio_js.read_text(encoding="utf-8")

        # 1. Static code check: isPlaying null guard and Boolean return
        has_safe_guard = bool(re.search(r'Boolean\s*\(\s*this\.audio\s*&&\s*!this\.audio\.paused', audio_code)) or \
                         bool(re.search(r'this\.audio\s*\?', audio_code)) or \
                         bool(re.search(r'if\s*\(\s*!this\s*\|\|\s*!this\.audio\s*\)\s*return false', audio_code))
        self.assertTrue(has_safe_guard, "audio-player.js lacks explicit null guard in isPlaying()")

        # 2. Dynamic Node.js stress testing with null/uninitialized audio
        node_script = f"""
const vm = require('vm');

class Element {{
  constructor(tag, id) {{
    this.tagName = tag.toUpperCase();
    this.id = id || '';
    this.classList = {{
      add: () => {{}},
      remove: () => {{}},
      contains: () => false
    }};
    this.style = {{}};
    this.listeners = {{}};
  }}
  addEventListener(evt, fn) {{
    this.listeners[evt] = this.listeners[evt] || [];
    this.listeners[evt].push(fn);
  }}
  querySelector() {{ return null; }}
  setAttribute() {{}}
}}

// DOM without any audio element
const doc = {{
  readyState: 'complete',
  getElementById(id) {{
    if (id === 'bg-music' || id === 'bg-audio') return null; // Uninitialized/null
    return new Element('div', id);
  }},
  querySelector() {{ return null; }},
  querySelectorAll() {{ return []; }},
  addEventListener() {{}}
}};

const win = {{
  document: doc,
  addEventListener() {{}}
}};

const ctx = vm.createContext({{
  window: win,
  document: doc,
  console: console,
  Boolean: Boolean,
  Promise: Promise
}});

vm.runInContext({json.dumps(audio_code)}, ctx);

const ctrl = win.audioController;
if (!ctrl) throw new Error('window.audioController is not defined');

// Call all methods when audio element is null
const playing1 = ctrl.isPlaying();
if (playing1 !== false) throw new Error('isPlaying() should return false when audio is null, got: ' + playing1);

// play, pause, toggle must not throw
ctrl.pause();
ctrl.toggle();
ctrl.play();

// Explicitly set audio to null and test again
ctrl.audio = null;
if (ctrl.isPlaying() !== false) throw new Error('isPlaying() should return false when ctrl.audio is explicitly null');
ctrl.pause();
ctrl.toggle();

// Provide mock active audio object and test isPlaying
ctrl.audio = {{
  paused: false,
  currentTime: 12.4,
  play: () => Promise.resolve(),
  pause: () => {{}}
}};
if (ctrl.isPlaying() !== true) throw new Error('isPlaying() should return true when active audio is playing with currentTime > 0');

// Provide paused audio object
ctrl.audio.paused = true;
if (ctrl.isPlaying() !== false) throw new Error('isPlaying() should return false when audio is paused');

console.log('SUCCESS');
"""
        proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Audio null handling test failed: {proc.stderr}\n{proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_print_stylesheet_page_break_and_isolation(self):
        """
        Adversarial Test 4: Print stylesheet contains page-break-inside: avoid,
        viewport dimensions, and strict chrome isolation rules.
        """
        print_css = PROJECT_ROOT / "css" / "print.css"
        self.assertTrue(print_css.exists(), "css/print.css does not exist")
        css_text = print_css.read_text(encoding="utf-8")

        # Must have @media print
        self.assertIn("@media print", css_text, "Missing @media print block in print.css")

        # Must enforce page-break-inside: avoid on certificate container and/or card
        has_page_break_avoid = "page-break-inside: avoid" in css_text or "break-inside: avoid" in css_text
        self.assertTrue(has_page_break_avoid, "print.css missing 'page-break-inside: avoid' rule")

        # Must enforce max-width: 100vw or 100% and max-height: 100vh on certificate container
        has_max_vw = bool(re.search(r'max-width\s*:\s*100vw', css_text)) or "max-width: 100%" in css_text
        self.assertTrue(has_max_vw, "print.css certificate container missing max-width bound")

        has_max_vh = bool(re.search(r'max-height\s*:\s*100vh', css_text))
        self.assertTrue(has_max_vh, "print.css certificate container missing max-height: 100vh bound")

        # Isolation checks: suppresses hero, vinyl player, timeline, lightbox, buttons, canvas
        hidden_elements = [
            "#hero",
            "#vinyl-player",
            "#timeline",
            "#lightbox",
            "button",
            "#confetti-canvas",
            "#fireworks-canvas"
        ]
        for selector in hidden_elements:
            self.assertIn(
                selector,
                css_text,
                f"Print isolation missing rule to hide '{selector}'"
            )

        # Must use display: none !important to guarantee suppression
        self.assertIn(
            "display: none !important",
            css_text,
            "Print isolation missing 'display: none !important' rule"
        )

    def test_gallery_all_37_photos_valid_dimensions_and_aspect_ratios(self):
        """
        Adversarial Test 5: Verify all 37 photo records in gallery-data.js have
        valid image dimensions > 0 and correct photographic aspect ratios.
        """
        gallery_js = PROJECT_ROOT / "js" / "gallery-data.js"
        self.assertTrue(gallery_js.exists(), "js/gallery-data.js does not exist")

        photos = extract_gallery_data(gallery_js)
        self.assertEqual(len(photos), 37, f"Expected 37 photos, found {len(photos)}")

        for idx, photo in enumerate(photos):
            self.assertIn("src", photo, f"Photo #{idx} missing 'src' field")
            src_path = photo["src"].lstrip("./")
            file_path = PROJECT_ROOT / src_path
            self.assertTrue(file_path.exists(), f"Photo #{idx} file does not exist: {file_path}")

            info = get_image_info(file_path)
            self.assertTrue(info.get("exists"), f"Failed to inspect photo #{idx}: {file_path}")
            self.assertNotIn("error", info, f"Error opening photo #{idx}: {info.get('error')}")

            width = info.get("width", 0)
            height = info.get("height", 0)

            # Dimensions must be positive non-zero
            self.assertGreater(width, 0, f"Photo #{idx} has invalid width: {width}")
            self.assertGreater(height, 0, f"Photo #{idx} has invalid height: {height}")

            # Longest edge must be <= 1600 (budget constraint)
            longest = max(width, height)
            self.assertLessEqual(longest, 1600, f"Photo #{idx} exceeds 1600px max edge: {longest}px")

            # Aspect ratio must be within reasonable photograph bounds (portrait or landscape, 0.4 to 2.5)
            aspect_ratio = width / height
            self.assertGreaterEqual(
                aspect_ratio,
                0.4,
                f"Photo #{idx} ({src_path}) has abnormal aspect ratio {aspect_ratio:.2f} (< 0.4)"
            )
            self.assertLessEqual(
                aspect_ratio,
                2.5,
                f"Photo #{idx} ({src_path}) has abnormal aspect ratio {aspect_ratio:.2f} (> 2.5)"
            )

            # Caption and Year verification
            self.assertIn("caption", photo, f"Photo #{idx} missing caption")
            self.assertTrue(len(photo["caption"].strip()) > 0, f"Photo #{idx} has empty caption")
            self.assertIn("year", photo, f"Photo #{idx} missing year")
            year_int = int(photo["year"])
            self.assertIn(year_int, [2023, 2024, 2025, 2026], f"Photo #{idx} year {year_int} out of range")


if __name__ == "__main__":
    unittest.main()
