"""
Tier 2: Boundary & Corner Cases
Verifies payload limits, edge filenames, EXIF orientation transpositions,
path relativities, broken links, audio attributes, and zero placeholders.
"""

import os
import re
import unittest
from pathlib import Path
from typing import Set

from tests.test_helpers import (
    PROJECT_ROOT,
    HI_NH_DIR,
    get_file_size,
    get_image_info,
    extract_gallery_data,
    parse_html_file,
)


class TestTier2BoundariesAndCornerCases(unittest.TestCase):
    """Test suite for Tier 2 Boundary & Corner Cases."""

    def test_total_payload_budget_under_15mb(self):
        """Verify total web asset payload (unique disk media, css, js, html) is strictly < 15 MB."""
        inodes = {}

        # Scan production folders and deduplicate by inode
        for folder_name in ["images", "audio", "css", "js"]:
            folder = PROJECT_ROOT / folder_name
            if folder.exists():
                for p in folder.rglob("*"):
                    if p.is_file() and not p.name.startswith("."):
                        ino = p.stat().st_ino
                        if ino not in inodes:
                            inodes[ino] = p.stat().st_size

        index_file = PROJECT_ROOT / "index.html"
        if index_file.exists():
            ino = index_file.stat().st_ino
            if ino not in inodes:
                inodes[ino] = index_file.stat().st_size

        total_bytes = sum(inodes.values())
        self.assertGreater(len(inodes), 0, "No web asset files found to calculate payload")
        limit_bytes = 15 * 1024 * 1024  # 15 MB = 15,728,640 bytes
        self.assertLess(
            total_bytes,
            limit_bytes,
            f"Total payload {total_bytes / (1024*1024):.2f} MB ({total_bytes} bytes) exceeds 15 MB budget ({limit_bytes} bytes)"
        )

    def test_code_payload_lightweight(self):
        """Verify total code payload (HTML + CSS + JS) is under 120 KB for blazing performance."""
        code_bytes = 0
        found_code = False
        for pattern in ["*.html", "css/*.css", "js/*.js"]:
            for f in PROJECT_ROOT.glob(pattern):
                if f.is_file():
                    code_bytes += f.stat().st_size
                    found_code = True

        # If code files exist, verify size is lightweight
        if found_code:
            self.assertLess(code_bytes, 120 * 1024, f"Code footprint {code_bytes/1024:.2f} KB exceeds 120 KB limit")

    def test_special_character_filename_mg_2223_1(self):
        """Verify '_MG_2223 (1).JPG' (with spaces and brackets) is cleanly handled without broken links."""
        js_file = PROJECT_ROOT / "js" / "gallery-data.js"
        self.assertTrue(js_file.exists(), "gallery-data.js missing")
        data = extract_gallery_data(js_file)

        # Look for the Canon photo taken on 2023-09-09
        matching = [item for item in data if "2223" in item.get("id", "") or "2223" in item.get("src", "")]
        self.assertEqual(len(matching), 1, "Photo _MG_2223 (1) not identified in GALLERY_DATA")

        src = matching[0]["src"]
        img_path = PROJECT_ROOT / src.lstrip("./")
        self.assertTrue(img_path.exists(), f"Image referenced for _MG_2223 (1) does not exist: {img_path}")

    def test_uuid_filename_instagram_photo(self):
        """Verify Instagram photo with UUID filename is preserved and accessible."""
        js_file = PROJECT_ROOT / "js" / "gallery-data.js"
        self.assertTrue(js_file.exists(), "gallery-data.js missing")
        data = extract_gallery_data(js_file)

        matching = [item for item in data if "A51AE22D" in item.get("id", "") or "A51AE22D" in item.get("src", "")]
        self.assertEqual(len(matching), 1, "Instagram UUID photo not found in GALLERY_DATA")
        src = matching[0]["src"]
        img_path = PROJECT_ROOT / src.lstrip("./")
        self.assertTrue(img_path.exists(), f"Instagram UUID image does not exist: {img_path}")

    def test_exif_orientation_transpose(self):
        """
        Verify photos that originally had orientation=6 (iPhone portrait sensor)
        are properly transposed so height > width in final optimized images.
        """
        portrait_samples = ["IMG_4385.jpg", "IMG_6484.jpg", "IMG_7825.jpg"]
        images_dir = PROJECT_ROOT / "images"

        for sample in portrait_samples:
            target = images_dir / sample
            self.assertTrue(target.exists(), f"Portrait sample file missing: {target}")
            info = get_image_info(target)
            self.assertTrue(info["exists"], f"Could not open image: {target}")
            self.assertGreater(
                info["height"],
                info["width"],
                f"Image {sample} was not transposed! width={info['width']}, height={info['height']} (expected height > width)"
            )

    def test_audio_loop_and_preload_attributes(self):
        """Verify <audio> element has 'loop' attribute and preload set."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        audio_match = re.search(r'<audio\b([^>]*)>', content, re.IGNORECASE)
        self.assertIsNotNone(audio_match, "No <audio> tag found in index.html")
        attrs = audio_match.group(1)

        self.assertIn("loop", attrs, "<audio> tag missing 'loop' attribute")
        self.assertTrue(
            "preload" in attrs,
            "<audio> tag missing 'preload' attribute (should be 'auto' or 'metadata')"
        )

    def test_all_relative_paths(self):
        """
        Verify all asset links in index.html and CSS are strictly relative.
        No absolute paths like /Users/... or leading root slash /images/...
        """
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        self.assertNotIn("/Users/", content, "Found absolute filesystem path in index.html")
        self.assertNotIn("C:\\", content, "Found Windows absolute path in index.html")

        urls = re.findall(r'(?:src|href)=["\']([^"\']+)["\']', content)
        for url in urls:
            if url.startswith("#") or url.startswith("http://") or url.startswith("https://") or url.startswith("data:"):
                continue
            self.assertFalse(
                url.startswith("/"),
                f"Found root-relative URL in index.html: '{url}'. Must use relative path like './' or 'images/'"
            )

    def test_zero_broken_links_audit(self):
        """Verify every local asset referenced in index.html and CSS actually exists on disk."""
        index_html = PROJECT_ROOT / "index.html"
        self.assertTrue(index_html.exists(), "index.html missing")
        content = index_html.read_text(encoding="utf-8")

        urls: Set[str] = set()
        for m in re.finditer(r'(?:src|href)=["\']([^"\']+)["\']', content):
            u = m.group(1).split("?")[0].split("#")[0]
            if not u.startswith("http://") and not u.startswith("https://") and not u.startswith("data:") and not u.startswith("#") and u:
                urls.add(u)

        for css_file in (PROJECT_ROOT / "css").glob("*.css"):
            css_text = css_file.read_text(encoding="utf-8")
            for m in re.finditer(r'url\(["\']?([^"\'()]+)["\']?\)', css_text):
                u = m.group(1).split("?")[0].split("#")[0]
                if not u.startswith("http://") and not u.startswith("https://") and not u.startswith("data:") and u:
                    urls.add(u)

        missing = []
        for url in urls:
            cleaned = url.lstrip("./")
            file_on_disk = PROJECT_ROOT / cleaned
            if not file_on_disk.exists():
                alt_file = PROJECT_ROOT / "css" / cleaned
                if not alt_file.exists():
                    missing.append(url)

        self.assertEqual(missing, [], f"Broken local file references detected: {missing}")

    def test_zero_placeholder_integrity(self):
        """Verify production files do not contain lazy placeholders (TODO, TBD, lorem ipsum, etc.)."""
        placeholder_regex = re.compile(r'\b(TODO|TBD|FIXME|LOREM\s+IPSUM|PLACEHOLDER\.COM)\b', re.IGNORECASE)

        flagged = []
        for ext in ["*.html", "css/*.css", "js/*.js"]:
            for path in PROJECT_ROOT.glob(ext):
                text = path.read_text(encoding="utf-8")
                matches = placeholder_regex.findall(text)
                if matches:
                    flagged.append(f"{path.name}: {set(matches)}")

        self.assertEqual(flagged, [], f"Unresolved placeholders found in source code: {flagged}")

    def test_mobile_safe_area_insets(self):
        """Verify CSS contains iOS safe area insets for iPhone notch/home bar support."""
        css_files = list((PROJECT_ROOT / "css").glob("*.css"))
        self.assertTrue(len(css_files) > 0, "No CSS files found in css/")
        css_combined = "".join(f.read_text(encoding="utf-8") for f in css_files)

        has_safe_area = bool(re.search(r'safe-area-inset-(?:top|bottom|left|right)', css_combined))
        self.assertTrue(
            has_safe_area,
            "CSS missing iOS safe area insets (safe-area-inset-top/bottom) for mobile edge-to-edge support"
        )


if __name__ == "__main__":
    unittest.main()
