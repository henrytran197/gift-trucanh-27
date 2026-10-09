"""
Test Helpers and Fixtures for gift_trucanh_27 Test Suite
Provides DOM, CSS, JS, and Media inspection utilities using Python standard library + Pillow.
"""

import os
import re
import json
import struct
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Dict, Optional, Any

# Root directory of gift_trucanh_27
PROJECT_ROOT = Path(__file__).resolve().parent.parent
HI_NH_DIR = PROJECT_ROOT.parent / "Hình"


class SimpleDOMNode:
    def __init__(self, tag: str, attrs: Dict[str, str], parent: Optional['SimpleDOMNode'] = None):
        self.tag = tag.lower()
        self.attrs = {k.lower(): v for k, v in attrs.items()}
        self.parent = parent
        self.children: List['SimpleDOMNode'] = []
        self.text: str = ""

    def get_attr(self, name: str) -> Optional[str]:
        return self.attrs.get(name.lower())

    @property
    def id(self) -> Optional[str]:
        return self.attrs.get("id")

    @property
    def classes(self) -> List[str]:
        c = self.attrs.get("class", "")
        return [cls.strip() for cls in c.split() if cls.strip()]

    def find_all(self, tag: Optional[str] = None, class_name: Optional[str] = None, id_attr: Optional[str] = None) -> List['SimpleDOMNode']:
        results = []
        match = True
        if tag is not None and self.tag != tag.lower():
            match = False
        if class_name is not None and class_name not in self.classes:
            match = False
        if id_attr is not None and self.id != id_attr:
            match = False

        if match and self.tag != "root":
            results.append(self)

        for child in self.children:
            results.extend(child.find_all(tag=tag, class_name=class_name, id_attr=id_attr))
        return results

    def find_first(self, tag: Optional[str] = None, class_name: Optional[str] = None, id_attr: Optional[str] = None) -> Optional['SimpleDOMNode']:
        matches = self.find_all(tag=tag, class_name=class_name, id_attr=id_attr)
        return matches[0] if matches else None


class SimpleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = SimpleDOMNode("root", {})
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = SimpleDOMNode(tag, dict(attrs), parent=self.current)
        self.current.children.append(node)
        # Self-closing tags in HTML5
        if tag.lower() not in {"meta", "link", "img", "br", "hr", "input", "source"}:
            self.current = node

    def handle_endtag(self, tag):
        if self.current.parent is not None and self.current.tag == tag.lower():
            self.current = self.current.parent

    def handle_data(self, data):
        if self.current:
            self.current.text += data


def parse_html_file(file_path: Path) -> SimpleDOMNode:
    """Parse an HTML file into a SimpleDOMNode tree."""
    if not file_path.exists():
        raise FileNotFoundError(f"HTML file not found: {file_path}")
    content = file_path.read_text(encoding="utf-8")
    parser = SimpleHTMLParser()
    parser.feed(content)
    return parser.root


def extract_gallery_data(js_path: Path) -> List[Dict[str, Any]]:
    """
    Extract window.GALLERY_DATA array from gallery-data.js.
    Uses regex and JSON deserialization to validate format.
    """
    if not js_path.exists():
        raise FileNotFoundError(f"gallery-data.js not found: {js_path}")
    content = js_path.read_text(encoding="utf-8")
    
    # Match window.GALLERY_DATA = [ ... ];
    match = re.search(r'(?:window\.)?GALLERY_DATA\s*=\s*(\[.*?\])\s*;?', content, re.DOTALL)
    if not match:
        raise ValueError("Could not find window.GALLERY_DATA array definition in JS file")
    
    raw_json = match.group(1)
    # Allow JS trailing commas and unquoted keys if necessary
    # Standard cleaner: remove trailing commas before closing braces/brackets
    cleaned_json = re.sub(r',\s*([\]}])', r'\1', raw_json)
    
    try:
        return json.loads(cleaned_json)
    except json.JSONDecodeError:
        # Fallback regex extraction of objects
        objects = []
        obj_matches = re.finditer(r'\{([^{}]+)\}', raw_json)
        for obj_match in obj_matches:
            item = {}
            body = obj_match.group(1)
            for line in body.split(','):
                if ':' in line:
                    k, v = line.split(':', 1)
                    k = k.strip().strip('"').strip("'")
                    v = v.strip().strip('"').strip("'")
                    try:
                        if v.isdigit():
                            v = int(v)
                        elif re.match(r'^-?\d+(\.\d+)?$', v):
                            v = float(v)
                    except ValueError:
                        pass
                    item[k] = v
            if item:
                objects.append(item)
        if objects:
            return objects
        raise ValueError(f"Failed to parse GALLERY_DATA JSON: {raw_json[:100]}...")


def get_file_size(path: Path) -> int:
    """Return size in bytes if file exists, else 0."""
    return path.stat().st_size if path.exists() else 0


def get_image_info(path: Path) -> Dict[str, Any]:
    """Inspect image format and dimensions using PIL."""
    if not path.exists():
        return {"exists": False}
    try:
        from PIL import Image
        with Image.open(path) as img:
            return {
                "exists": True,
                "format": img.format,
                "width": img.width,
                "height": img.height,
                "size_bytes": path.stat().st_size,
                "mode": img.mode,
            }
    except Exception as e:
        return {"exists": True, "error": str(e), "size_bytes": path.stat().st_size}


def is_valid_mp3(path: Path) -> bool:
    """Check if file starts with valid MP3 ID3 header or sync word."""
    if not path.exists():
        return False
    with open(path, "rb") as f:
        head = f.read(10)
        if len(head) < 4:
            return False
        # ID3v2 tag
        if head[:3] == b"ID3":
            return True
        # MPEG audio sync word (11 bits set: 0xFF 0xE0 or 0xFF 0xF0)
        if head[0] == 0xFF and (head[1] & 0xE0) == 0xE0:
            return True
    return False
