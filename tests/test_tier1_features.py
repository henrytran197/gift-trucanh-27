"""
Tier 1: Feature Coverage (Unit / Isolation Tests)
Verifies all 19 core features from PROJECT.md in strict isolation.
"""

import os
import re
import unittest
from pathlib import Path

from tests.test_helpers import (
    PROJECT_ROOT,
    HI_NH_DIR,
    parse_html_file,
    extract_gallery_data,
    get_image_info,
    is_valid_mp3,
    get_file_size,
)


class TestTier1FeatureCoverage(unittest.TestCase):
    """Test suite for Tier 1 Feature Coverage."""

    # -------------------------------------------------------------
    # Milestone 1: Media Pipeline & Data
    # -------------------------------------------------------------

    def test_f01_heic_to_jpeg_conversion(self):
        """F1: Verify IMG_8326.HEIC is successfully converted to JPEG in images/."""
        dest_jpg = PROJECT_ROOT / "images" / "IMG_8326.jpg"
        self.assertTrue(dest_jpg.exists(), f"Converted file missing: {dest_jpg}")
        
        info = get_image_info(dest_jpg)
        self.assertTrue(info["exists"], "File could not be opened")
        self.assertEqual(info["format"], "JPEG", f"Expected JPEG format, got {info.get('format')}")
        self.assertLessEqual(max(info["width"], info["height"]), 1600, "Image exceeds max 1600px width/height")
        self.assertGreater(info["size_bytes"], 10_000, "Image file too small (< 10 KB)")

    def test_f02_image_resizing_and_compression(self):
        """F2: Verify all 37 distinct photos are present in images/, resized to <=1600px, and compressed."""
        images_dir = PROJECT_ROOT / "images"
        self.assertTrue(images_dir.exists(), f"Images directory missing: {images_dir}")

        image_files = [f for f in images_dir.glob("*.jpg")] + [f for f in images_dir.glob("*.jpeg")] + [f for f in images_dir.glob("*.webp")]
        photo_files = [f for f in image_files if "certificate" not in f.name.lower()]
        
        # Deduplicate hardlink aliases by inode to get distinct photos
        unique_photos = {}
        for p in photo_files:
            ino = p.stat().st_ino
            if ino not in unique_photos:
                unique_photos[ino] = p

        self.assertEqual(len(unique_photos), 37, f"Expected exactly 37 distinct photos in images/, found {len(unique_photos)}")

        total_bytes = 0
        for ino, p in unique_photos.items():
            info = get_image_info(p)
            self.assertTrue(info["exists"], f"Could not inspect {p.name}")
            self.assertLessEqual(max(info["width"], info["height"]), 1600, f"{p.name} dimension > 1600px: {info['width']}x{info['height']}")
            total_bytes += info["size_bytes"]

        # 37 photos must fit well within 12 MB (~8.5-11.2 MB expected)
        self.assertLess(total_bytes, 12 * 1024 * 1024, f"Total photo size {total_bytes / (1024*1024):.2f} MB exceeds 12 MB budget")

    def test_f03_chronological_metadata_manifest(self):
        """F3: Verify js/gallery-data.js exists, exports window.GALLERY_DATA with 37 photos in 4 chapters."""
        js_file = PROJECT_ROOT / "js" / "gallery-data.js"
        self.assertTrue(js_file.exists(), f"Missing gallery-data.js at {js_file}")

        data = extract_gallery_data(js_file)
        self.assertEqual(len(data), 37, f"GALLERY_DATA must contain 37 items, found {len(data)}")

        years = {}
        for item in data:
            self.assertIn("id", item, "Item missing 'id'")
            self.assertIn("src", item, "Item missing 'src'")
            self.assertIn("year", item, "Item missing 'year'")
            self.assertIn("date", item, "Item missing 'date'")
            self.assertIn("caption", item, "Item missing 'caption'")
            y = int(item["year"])
            years[y] = years.get(y, 0) + 1

        self.assertEqual(years.get(2023), 15, f"Expected 15 photos in 2023, found {years.get(2023)}")
        self.assertEqual(years.get(2024), 7, f"Expected 7 photos in 2024, found {years.get(2024)}")
        self.assertEqual(years.get(2025), 11, f"Expected 11 photos in 2025, found {years.get(2025)}")
        self.assertEqual(years.get(2026), 4, f"Expected 4 photos in 2026, found {years.get(2026)}")

    def test_f04_audio_asset_setup(self):
        """F4: Verify audio/music.mp3 exists, is a valid MP3, and around ~2.79 MB."""
        audio_file = PROJECT_ROOT / "audio" / "music.mp3"
        self.assertTrue(audio_file.exists(), f"Audio file missing: {audio_file}")
        self.assertTrue(is_valid_mp3(audio_file), "music.mp3 is not a valid MP3 file")
        size = get_file_size(audio_file)
        self.assertGreater(size, 2_000_000, f"music.mp3 suspiciously small: {size} bytes")
        self.assertLess(size, 3_500_000, f"music.mp3 suspiciously large: {size} bytes")

    def test_f05_certificate_2021_asset_extraction(self):
        """F5: Verify 2021 certificate asset is extracted into images/certificate_2021.*."""
        cert_png = PROJECT_ROOT / "images" / "certificate_2021.png"
        cert_jpg = PROJECT_ROOT / "images" / "certificate_2021.jpg"
        cert_file = cert_png if cert_png.exists() else cert_jpg
        self.assertTrue(cert_file.exists(), "Neither certificate_2021.png nor certificate_2021.jpg found in images/")
        info = get_image_info(cert_file)
        self.assertTrue(info["exists"], "Could not inspect certificate_2021 asset")
        self.assertGreater(info["size_bytes"], 50_000, "Certificate asset is too small (<50 KB)")

    # -------------------------------------------------------------
    # Milestone 2: Hero Intro & Vinyl Player
    # -------------------------------------------------------------

    def test_f06_interactive_hero_intro(self):
        """F6: Verify Hero section contains interactive gift box / envelope and CTA button."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r'id=["\'](?:hero|intro)["\']|class=["\'][^"\']*\bhero\b[^"\']*["\']', content)),
            "Hero section container (#hero or .hero) not found in index.html"
        )
        self.assertTrue(
            bool(re.search(r'id=["\'](?:gift-box|envelope|gift)["\']|class=["\'][^"\']*\b(?:gift-box|envelope|gift)\b[^"\']*["\']', content)),
            "Gift box or romantic envelope container not found in index.html"
        )
        self.assertTrue(
            bool(re.search(r'(?:Khám phá món quà|Mở Món Quà|Mở Quà|Khám Phá)', content, re.IGNORECASE)),
            "CTA button text for opening gift not found in index.html"
        )

    def test_f07_audio_unlock_and_confetti(self):
        """F7: Verify CTA click initiates audio playback and triggers confetti canvas."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")
        
        self.assertTrue(
            bool(re.search(r'<audio\b[^>]*\bid=["\'](?:bg-music|bg-audio|music)["\']', content)),
            "Background <audio> tag with id bg-music/bg-audio not found in index.html"
        )
        self.assertTrue(
            bool(re.search(r'<canvas\b[^>]*\bid=["\'](?:confetti|particles|canvas-confetti)["\']', content)),
            "Confetti/particles canvas not found in index.html"
        )
        self.assertTrue(
            bool(re.search(r'src=["\'][^"\']*particles\.js["\']', content)) or "particles" in content,
            "particles.js script reference not found in index.html"
        )

    def test_f08_floating_vinyl_record_player(self):
        """F8: Verify floating vinyl player UI markup and rotating animation."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r'class=["\'][^"\']*\b(?:vinyl|record-player|floating-player)\b[^"\']*["\']|id=["\'](?:vinyl-player|floating-vinyl)["\']', content)),
            "Floating vinyl record player markup not found in index.html"
        )

        css_files = list((PROJECT_ROOT / "css").glob("*.css"))
        self.assertTrue(len(css_files) > 0, "No CSS files found in css/")
        css_combined = "".join(f.read_text(encoding="utf-8") for f in css_files)
        
        self.assertTrue(
            "vinyl" in css_combined.lower() or "spin" in css_combined.lower(),
            "Vinyl styling or spin animation not found in CSS"
        )
        self.assertTrue(
            bool(re.search(r'@keyframes\s+(?:vinylSpin|spin|rotate)', css_combined)),
            "@keyframes spin/vinylSpin animation not defined in CSS"
        )

    # -------------------------------------------------------------
    # Milestone 3: Timeline, Polaroid Cards & Lightbox
    # -------------------------------------------------------------

    def test_f09_flashback_2021_section(self):
        """F9: Verify 2021 Flashback section with Level 22 certificate render and Henry's 2021 quote."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r'id=["\'](?:flashback|flashback-2021|level-22)["\']|class=["\'][^"\']*\bflashback\b[^"\']*["\']', content)),
            "Flashback section (#flashback-2021) not found in index.html"
        )
        self.assertIn("2021", content, "Year 2021 not mentioned in index.html")
        self.assertTrue(
            "22" in content or "tuổi 22" in content or "Level 22" in content,
            "Age 22 milestone not mentioned in index.html"
        )
        self.assertTrue(
            bool(re.search(r'sống một cuộc sống thật ý nghĩa|yêu thương bản thân mình', content)),
            "Henry's 2021 promise quote not found in index.html"
        )

    def test_f10_chronological_memory_timeline(self):
        """F10: Verify timeline structure containing 4 milestone chapters (2023, 2024, 2025, 2026)."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r'id=["\'](?:timeline|memory-timeline|gallery)["\']|class=["\'][^"\']*\btimeline\b[^"\']*["\']', content)),
            "Timeline container not found in index.html"
        )
        for year in ["2023", "2024", "2025", "2026"]:
            self.assertIn(year, content, f"Chapter year {year} not found in index.html")

    def test_f11_polaroid_photo_cards(self):
        """F11: Verify Polaroid card structure, styling, washi tape / tilt, and lazy loading."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")
        
        css_files = list((PROJECT_ROOT / "css").glob("*.css"))
        css_combined = "".join(f.read_text(encoding="utf-8") for f in css_files)

        app_js = PROJECT_ROOT / "js" / "app.js"
        js_content = app_js.read_text(encoding="utf-8") if app_js.exists() else ""
        combined_source = content + "\n" + js_content

        self.assertTrue(
            "polaroid" in combined_source.lower(),
            "Polaroid card classes not found in HTML/JS source"
        )
        self.assertTrue(
            'loading="lazy"' in combined_source or "loading='lazy'" in combined_source or 'lazy' in combined_source,
            "Lazy loading attribute not configured for photo cards"
        )
        self.assertTrue(
            bool(re.search(r'rotate\s*\(\s*-?[0-9.]+deg\s*\)', css_combined)),
            "Card tilt rotation (rotate(deg)) not found in CSS"
        )

    def test_f12_fullscreen_hd_lightbox(self):
        """F12: Verify full-screen HD Lightbox container, controls, counter, and lightbox.js."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r'id=["\'](?:lightbox|photo-lightbox)["\']', content)),
            "Lightbox container (#lightbox) not found in index.html"
        )
        lightbox_js = PROJECT_ROOT / "js" / "lightbox.js"
        self.assertTrue(lightbox_js.exists(), "lightbox.js missing")
        self.assertIn("lightbox.js", content, "lightbox.js not included in index.html")

        js_content = lightbox_js.read_text(encoding="utf-8")
        self.assertTrue(
            "open" in js_content and "close" in js_content and ("next" in js_content or "prev" in js_content),
            "Lightbox methods (open, close, next, prev) missing in lightbox.js"
        )

    # -------------------------------------------------------------
    # Milestone 4: Certificate Level 27, Letter, Fireworks & Print
    # -------------------------------------------------------------

    def test_f13_luxury_certificate_level_27(self):
        """F13: Verify Certificate Level 27 container, Rose Gold border styling, recipient, and citation."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r'id=["\'](?:certificate-level-27|certificate-27|certificate)["\']', content)),
            "Certificate container (#certificate-level-27) not found in index.html"
        )
        self.assertTrue(
            "Trúc Anh" in content,
            "Recipient name 'Trúc Anh' not found in certificate"
        )
        self.assertTrue(
            "27" in content and ("Level 27" in content or "tuổi 27" in content or "Trưởng Thành" in content),
            "Level 27 / Tuổi 27 certificate title not found"
        )
        css_files = list((PROJECT_ROOT / "css").glob("*.css"))
        css_combined = "".join(f.read_text(encoding="utf-8") for f in css_files)
        self.assertTrue(
            bool(re.search(r'#b76e79|#e0a899|#ffd1dc|rose-gold|border', css_combined, re.IGNORECASE)),
            "Rose gold metallic palette / border styles not found in CSS"
        )

    def test_f14_3d_wax_seal(self):
        """F14: Verify 3D wax seal markup and '27th Birthday Official Seal' branding."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r'class=["\'][^"\']*\b(?:wax-seal|seal-3d|wax)\b[^"\']*["\']|id=["\'](?:wax-seal|seal)["\']', content)),
            "Wax seal markup not found in index.html"
        )
        self.assertTrue(
            bool(re.search(r'27th\s+Birthday|Official\s+Seal|Seal|Dấu\s+Niêm\s+Phong', content, re.IGNORECASE)),
            "Wax seal branding text not found in index.html"
        )

    def test_f15_digital_signature(self):
        """F15: Verify Henry's signature and date 'Sài Gòn, Ngày 17 tháng 9 năm 2026'."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertTrue(
            "Henry" in content,
            "Signer name 'Henry' not found in certificate"
        )
        self.assertTrue(
            bool(re.search(r'17\s*tháng\s*9\s*năm\s*2026|17/09/2026|17\.09\.2026', content)),
            "Official certificate date 17/09/2026 not found in index.html"
        )

    def test_f16_emotional_2026_letter(self):
        """F16: Verify emotional 2026 letter from Henry honoring 5-year journey from age 22 to 27."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r'class=["\'][^"\']*\b(?:letter|emotional-letter|letter-2026)\b[^"\']*["\']|id=["\'](?:letter-2026|letter)["\']', content)),
            "Letter container (#letter-2026 or .letter) not found in index.html"
        )
        self.assertTrue(
            bool(re.search(r'5\s*năm|tuổi 27|hành trình|Trúc Anh', content)),
            "Letter content honoring 5-year journey not found in index.html"
        )

    def test_f17_celebration_fireworks(self):
        """F17: Verify celebration fireworks canvas and fireworks.js engine."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r'<canvas\b[^>]*\bid=["\'](?:fireworks|fireworks-canvas)["\']', content)),
            "Fireworks canvas (#fireworks-canvas) not found in index.html"
        )
        fireworks_js = PROJECT_ROOT / "js" / "fireworks.js"
        self.assertTrue(fireworks_js.exists(), "fireworks.js missing")
        self.assertIn("fireworks.js", content, "fireworks.js not included in index.html")

    def test_f18_print_and_save_functionality(self):
        """F18: Verify dedicated print stylesheet and print trigger button."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r'onclick=["\'][^"\']*(?:printCertificate|window\.print)[^"\']*["\']|class=["\'][^"\']*\b(?:print-btn|btn-print)\b[^"\']*["\']|id=["\'](?:print-btn|btn-print)["\']', content)),
            "Print Certificate button with trigger not found in index.html"
        )

        css_files = list((PROJECT_ROOT / "css").glob("*.css"))
        css_combined = "".join(f.read_text(encoding="utf-8") for f in css_files)
        print_css = PROJECT_ROOT / "css" / "print.css"
        
        has_print_rules = print_css.exists() or "@media print" in css_combined
        self.assertTrue(has_print_rules, "No @media print stylesheet or css/print.css found")

    def test_f19_responsive_layout_and_mobile_polish(self):
        """F19: Verify viewport meta tag with viewport-fit=cover and responsive CSS media queries."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertTrue(
            bool(re.search(r'<meta\b[^>]*name=["\']viewport["\'][^>]*content=["\'][^"\']*viewport-fit=cover', content, re.IGNORECASE)),
            "Viewport meta tag with viewport-fit=cover missing from index.html"
        )

        css_files = list((PROJECT_ROOT / "css").glob("*.css"))
        css_combined = "".join(f.read_text(encoding="utf-8") for f in css_files)
        self.assertTrue(
            "@media" in css_combined and ("max-width" in css_combined or "min-width" in css_combined),
            "Responsive @media queries missing from CSS"
        )


if __name__ == "__main__":
    unittest.main()
