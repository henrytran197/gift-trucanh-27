"""
Tier 3: Cross-Feature Interactions & Pairwise Integration
Verifies contract interfaces, cross-component signaling, and event wiring
between Hero, Audio Player, Lightbox, Timeline, and Certificate Print systems.
"""

import re
import unittest
from pathlib import Path

from tests.test_helpers import (
    PROJECT_ROOT,
    extract_gallery_data,
)


class TestTier3CrossFeatureInteractions(unittest.TestCase):
    """Test suite for Tier 3 Cross-Feature Interactions."""

    def test_hero_cta_triggers_audio_and_particles(self):
        """
        Verify Hero CTA button click handler synchronously triggers both
        audio playback and celebratory particle/confetti system.
        """
        app_js = PROJECT_ROOT / "js" / "app.js"
        self.assertTrue(app_js.exists(), "app.js missing")
        content = app_js.read_text(encoding="utf-8")

        # Must bind click to hero CTA
        has_click_binding = bool(re.search(r'addEventListener\s*\(\s*["\']click["\']', content))
        self.assertTrue(has_click_binding, "No click event listener bound in app.js")

        # Must call audio play
        has_audio_call = bool(re.search(r'(?:audioController|audio|bgMusic|musicPlayer)\.(?:play|start|toggle)', content))
        self.assertTrue(has_audio_call, "Audio playback is not triggered by CTA in app.js")

        # Must trigger particles / confetti
        has_particle_call = bool(re.search(r'(?:confetti|particles|createParticles|burst|launch)\s*\(', content))
        self.assertTrue(has_particle_call, "Particle / confetti burst is not triggered by CTA in app.js")

    def test_polaroid_card_opens_lightbox_with_index(self):
        """Verify Polaroid card click events are wired to window.lightbox.open(index)."""
        app_js = PROJECT_ROOT / "js" / "app.js"
        lightbox_js = PROJECT_ROOT / "js" / "lightbox.js"
        self.assertTrue(app_js.exists(), "app.js missing")
        self.assertTrue(lightbox_js.exists(), "lightbox.js missing")

        app_content = app_js.read_text(encoding="utf-8")
        lb_content = lightbox_js.read_text(encoding="utf-8")

        # app.js must call lightbox.open(index) or trigger open
        wires_lightbox = bool(re.search(r'(?:lightbox|window\.lightbox)\.open\s*\(', app_content)) or \
                         bool(re.search(r'open\s*\(\s*(?:index|idx|i)\s*\)', app_content))
        self.assertTrue(wires_lightbox, "Card click does not invoke lightbox.open(index) in app.js")

        # lightbox.js must define open(index)
        has_open_fn = bool(re.search(r'(?:function\s+open|open\s*:\s*function|open\s*\(index\)|open\s*=\s*function)', lb_content))
        self.assertTrue(has_open_fn, "lightbox.open function definition missing in lightbox.js")

    def test_lightbox_keyboard_shortcuts_wiring(self):
        """Verify Lightbox handles ArrowRight (Next), ArrowLeft (Prev), and Escape (Close)."""
        lightbox_js = PROJECT_ROOT / "js" / "lightbox.js"
        self.assertTrue(lightbox_js.exists(), "lightbox.js missing")
        lb_content = lightbox_js.read_text(encoding="utf-8")

        # Must listen to keydown / keyup
        self.assertTrue(
            bool(re.search(r'addEventListener\s*\(\s*["\']key(?:down|up)["\']', lb_content)),
            "Lightbox does not add keyboard event listener in lightbox.js"
        )
        # Must check ArrowRight or keyCode 39
        self.assertTrue(
            "ArrowRight" in lb_content or "39" in lb_content,
            "Lightbox does not handle ArrowRight (Next) key"
        )
        # Must check ArrowLeft or keyCode 37
        self.assertTrue(
            "ArrowLeft" in lb_content or "37" in lb_content,
            "Lightbox does not handle ArrowLeft (Prev) key"
        )
        # Must check Escape or keyCode 27
        self.assertTrue(
            "Escape" in lb_content or "27" in lb_content,
            "Lightbox does not handle Escape (Close) key"
        )

    def test_audio_controller_and_vinyl_sync(self):
        """
        Verify audio state changes synchronize vinyl rotation animation
        (running on play, paused on pause).
        """
        audio_js = PROJECT_ROOT / "js" / "audio-player.js"
        self.assertTrue(audio_js.exists(), "audio-player.js missing")
        content = audio_js.read_text(encoding="utf-8")

        # Must listen to 'play' and 'pause' events or handle state toggles
        has_play_handler = "play" in content
        has_pause_handler = "pause" in content
        self.assertTrue(has_play_handler and has_pause_handler, "Audio controller lacks play/pause sync logic")

        # Must manipulate class or style on vinyl element (e.g. is-playing, active, animationPlayState)
        manipulates_vinyl = bool(re.search(r'(?:classList\.(?:add|remove|toggle)|style\.animationPlayState)', content))
        self.assertTrue(
            manipulates_vinyl,
            "Audio controller does not toggle vinyl playing classes or animationPlayState"
        )

    def test_certificate_print_stylesheet_isolation(self):
        """
        Verify print stylesheet hides interactive web chrome (Hero, Timeline, Lightbox, Vinyl)
        and leaves only the Certificate Level 27 visible for printing.
        """
        css_files = list((PROJECT_ROOT / "css").glob("*.css"))
        css_combined = "".join(f.read_text(encoding="utf-8") for f in css_files)
        print_css = PROJECT_ROOT / "css" / "print.css"
        if print_css.exists():
            css_combined += "\n" + print_css.read_text(encoding="utf-8")

        # Must have @media print
        self.assertIn("@media print", css_combined, "No @media print rules found")

        # Must set display: none on non-certificate elements
        print_section = css_combined.split("@media print")[1]
        self.assertIn("display: none", print_section, "Print styles do not hide web chrome (display: none missing)")

        # Verify selectors hidden include hero, vinyl, timeline, or controls
        hidden_keywords = ["hero", "vinyl", "timeline", "lightbox", "btn", "button", "player"]
        found_hidden = [kw for kw in hidden_keywords if kw in print_section.lower()]
        self.assertGreaterEqual(
            len(found_hidden), 2,
            f"Print stylesheet does not hide sufficient web chrome elements: found {found_hidden}"
        )

    def test_fireworks_engine_interface(self):
        """Verify fireworks.js exports an executable launch API."""
        fireworks_js = PROJECT_ROOT / "js" / "fireworks.js"
        self.assertTrue(fireworks_js.exists(), "fireworks.js missing")
        content = fireworks_js.read_text(encoding="utf-8")

        # Must export window.fireworks or define launch/start function
        has_api = bool(re.search(r'(?:window\.fireworks|fireworks\s*=\s*\{|function\s+(?:launch|startFireworks|triggerFireworks))', content))
        self.assertTrue(has_api, "fireworks.js does not export standard launch / trigger API")


if __name__ == "__main__":
    unittest.main()
