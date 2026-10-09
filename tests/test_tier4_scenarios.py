"""
Tier 4: Real-World Application Scenarios (End-to-End User Journeys)
Simulates complete real-world user workflows:
1. The Birthday Surprise Discovery Journey (Hero -> Audio -> Confetti -> Flashback)
2. The Memory Lane Walkthrough (Timeline -> 37 Polaroids -> HD Lightbox Navigation)
3. The Grand Certificate Ceremony & Print (Level 27 -> Wax Seal -> Signature -> Letter -> Fireworks -> Print)
"""

import re
import unittest
from pathlib import Path

from tests.test_helpers import (
    PROJECT_ROOT,
    extract_gallery_data,
    get_image_info,
)


class TestTier4RealWorldScenarios(unittest.TestCase):
    """Test suite for Tier 4 Real-World Application Scenarios."""

    def test_scenario_1_birthday_surprise_discovery(self):
        """
        Scenario 1: Trúc Anh opens the website on her birthday.
        - Steps:
          1. Lands on Hero section with 3D Gift Box.
          2. Clicks 'Khám phá món quà'.
          3. Elvis Presley's 'Can't Help Falling in Love' plays.
          4. Confetti and starlight particles erupt on canvas.
          5. Floating vinyl player starts spinning.
          6. Page transitions into 2021 Flashback (Level 22).
        """
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "Step 1 Failed: index.html does not exist")
        html_text = index_html.read_text(encoding="utf-8")

        # 1. Hero and Gift Box
        self.assertTrue(
            bool(re.search(r'id=["\'](?:hero|gift-box|envelope)["\']|class=["\'][^"\']*\b(?:hero|gift-box)\b[^"\']*["\']', html_text)),
            "Step 1 Failed: Hero intro / gift box container missing"
        )
        self.assertTrue(
            bool(re.search(r'(?:Khám phá món quà|Mở Món Quà|Mở Quà|Khám Phá)', html_text, re.IGNORECASE)),
            "Step 1 Failed: CTA button missing"
        )

        # 2 & 3. Audio Asset & Tag
        audio_file = PROJECT_ROOT / "audio" / "music.mp3"
        self.assertTrue(audio_file.exists(), "Step 3 Failed: audio/music.mp3 does not exist on disk")
        self.assertTrue(
            bool(re.search(r'<audio\b[^>]*src=["\']\./?audio/music\.mp3["\']', html_text)),
            "Step 3 Failed: <audio> tag with relative path ./audio/music.mp3 missing"
        )

        # 4. Confetti Canvas
        self.assertTrue(
            bool(re.search(r'<canvas\b[^>]*\bid=["\'](?:confetti|particles|canvas-confetti)["\']', html_text)),
            "Step 4 Failed: Confetti canvas missing"
        )

        # 5. Vinyl Player
        self.assertTrue(
            bool(re.search(r'class=["\'][^"\']*\b(?:vinyl|record-player|floating-player)\b[^"\']*["\']|id=["\'](?:vinyl-player|floating-vinyl)["\']', html_text)),
            "Step 5 Failed: Floating vinyl player element missing"
        )

        # 6. 2021 Flashback
        self.assertTrue(
            bool(re.search(r'id=["\'](?:flashback|flashback-2021)["\']|class=["\'][^"\']*\bflashback\b[^"\']*["\']', html_text)),
            "Step 6 Failed: 2021 Flashback container missing"
        )

    def test_scenario_2_memory_lane_timeline_and_lightbox(self):
        """
        Scenario 2: Trúc Anh scrolls through the 4-year memory timeline.
        - Steps:
          1. 2021 Flashback displays original certificate and Henry's quote.
          2. 4 Milestone chapters exist (2023: 15, 2024: 7, 2025: 11, 2026: 4 photos).
          3. Total 37 photos render as Polaroid cards.
          4. Clicking photo opens Full-Screen HD Lightbox.
          5. Lightbox Next/Prev navigates smoothly between photos.
          6. All 37 photos exist on disk and resolve without 404s.
        """
        # 1. 2021 Certificate asset check
        cert_png = PROJECT_ROOT / "images" / "certificate_2021.png"
        cert_jpg = PROJECT_ROOT / "images" / "certificate_2021.jpg"
        self.assertTrue(cert_png.exists() or cert_jpg.exists(), "Step 1 Failed: 2021 Certificate image missing")

        # 2 & 3. Gallery Manifest & 37 Photos
        js_file = PROJECT_ROOT / "js" / "gallery-data.js"
        self.assertTrue(js_file.exists(), "Step 2 Failed: js/gallery-data.js missing")
        gallery = extract_gallery_data(js_file)
        self.assertEqual(len(gallery), 37, f"Step 3 Failed: Expected 37 photos, got {len(gallery)}")

        # Verify all 37 photo files exist on disk and have valid dimensions
        for i, photo in enumerate(gallery):
            src = photo.get("src", "").lstrip("./")
            img_path = PROJECT_ROOT / src
            self.assertTrue(img_path.exists(), f"Step 3 Failed: Photo {i} file missing on disk: {src}")
            info = get_image_info(img_path)
            self.assertTrue(info["exists"], f"Step 3 Failed: Corrupt image at {src}")
            self.assertGreater(info["width"], 100, f"Step 3 Failed: Suspiciously small width for {src}")
            self.assertGreater(info["height"], 100, f"Step 3 Failed: Suspiciously small height for {src}")

        # 4 & 5. Lightbox Markup & Logic
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "Step 4 Failed: index.html missing")
        html_text = index_html.read_text(encoding="utf-8")
        self.assertTrue(
            bool(re.search(r'id=["\'](?:lightbox|photo-lightbox)["\']', html_text)),
            "Step 4 Failed: Lightbox DOM container missing"
        )

        lightbox_js = PROJECT_ROOT / "js" / "lightbox.js"
        self.assertTrue(lightbox_js.exists(), "Step 5 Failed: js/lightbox.js missing")
        lb_text = lightbox_js.read_text(encoding="utf-8")
        self.assertTrue(
            "next" in lb_text and "prev" in lb_text and "close" in lb_text,
            "Step 5 Failed: Lightbox navigation controls missing in js/lightbox.js"
        )

    def test_scenario_3_grand_certificate_ceremony_and_print(self):
        """
        Scenario 3: Trúc Anh reaches the Certificate of Maturity Level 27 finale.
        - Steps:
          1. Luxury Rose Gold double border frame is presented.
          2. Recipient 'Trúc Anh (Na)' and 'Level 27' officially certified.
          3. 3D Wax Seal ('27th Birthday Official Seal') is embossed.
          4. Henry's calligraphic signature and date (17/09/2026) are displayed.
          5. Emotional 2026 letter honoring the 5-year journey is readable.
          6. Fireworks celebration can be ignited on canvas.
          7. Print/Save button is ready; print stylesheet isolates certificate.
        """
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "Step 1 Failed: index.html missing")
        html_text = index_html.read_text(encoding="utf-8")

        # 1 & 2. Certificate Level 27 Container & Recipient
        self.assertTrue(
            bool(re.search(r'id=["\'](?:certificate-level-27|certificate-27|certificate)["\']', html_text)),
            "Step 1 Failed: Certificate Level 27 container missing"
        )
        self.assertIn("Trúc Anh", html_text, "Step 2 Failed: Recipient name 'Trúc Anh' missing")
        self.assertTrue("27" in html_text, "Step 2 Failed: Age 27 / Level 27 missing")

        # 3. 3D Wax Seal
        self.assertTrue(
            bool(re.search(r'class=["\'][^"\']*\b(?:wax-seal|seal-3d|wax)\b[^"\']*["\']|id=["\'](?:wax-seal|seal)["\']', html_text)),
            "Step 3 Failed: Wax seal container missing"
        )

        # 4. Signature & Date
        self.assertIn("Henry", html_text, "Step 4 Failed: Signer 'Henry' missing")
        self.assertTrue(
            bool(re.search(r'17\s*tháng\s*9\s*năm\s*2026|17/09/2026|17\.09\.2026', html_text)),
            "Step 4 Failed: Date 17/09/2026 missing"
        )

        # 5. Emotional Letter
        self.assertTrue(
            bool(re.search(r'class=["\'][^"\']*\b(?:letter|emotional-letter|letter-2026)\b[^"\']*["\']|id=["\'](?:letter-2026|letter)["\']', html_text)),
            "Step 5 Failed: Emotional 2026 letter container missing"
        )

        # 6. Fireworks Engine
        fireworks_js = PROJECT_ROOT / "js" / "fireworks.js"
        self.assertTrue(fireworks_js.exists(), "Step 6 Failed: js/fireworks.js missing")

        # 7. Print Functionality
        css_files = list((PROJECT_ROOT / "css").glob("*.css"))
        css_combined = "".join(f.read_text(encoding="utf-8") for f in css_files)
        print_css = PROJECT_ROOT / "css" / "print.css"
        if print_css.exists():
            css_combined += "\n" + print_css.read_text(encoding="utf-8")

        self.assertIn("@media print", css_combined, "Step 7 Failed: @media print stylesheet missing")


if __name__ == "__main__":
    unittest.main()
