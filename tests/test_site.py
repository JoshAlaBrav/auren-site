from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = (ROOT / "index.html", ROOT / "privacy" / "index.html", ROOT / "terms" / "index.html")
TEXT_SUFFIXES = {".html", ".css", ".svg", ".md", ".txt", ".xml"}


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.resources: list[str] = []
        self.images_without_alt: list[str] = []
        self.tags: list[str] = []
        self.has_viewport = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        self.tags.append(tag)
        if tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")
        if tag in {"script", "img"} or (tag == "link" and values.get("rel") in {"stylesheet", "icon"}):
            source = values.get("href") or values.get("src")
            if source:
                self.resources.append(source)
        if tag == "img" and "alt" not in values:
            self.images_without_alt.append(values.get("src") or "<sin src>")
        if tag == "meta" and values.get("name") == "viewport":
            self.has_viewport = True


def local_target(source_file: Path, href: str) -> Path | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or href.startswith("#"):
        return None
    path = unquote(parsed.path)
    target = (source_file.parent / path).resolve()
    if path.endswith("/") or target.is_dir():
        target /= "index.html"
    return target


class PublicSiteTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for path in (*HTML_FILES, ROOT / "styles.css", ROOT / "assets" / "auren-emblem.svg"):
            self.assertTrue(path.is_file(), path)

    def test_html_is_responsive_and_links_resolve(self) -> None:
        for path in HTML_FILES:
            parser = SiteParser()
            parser.feed(path.read_text(encoding="utf-8"))
            self.assertTrue(parser.has_viewport, path)
            self.assertFalse(parser.images_without_alt, path)
            self.assertNotIn("script", parser.tags, path)
            for reference in (*parser.links, *parser.resources):
                target = local_target(path, reference)
                if target is not None:
                    self.assertTrue(target.is_file(), f"{path}: {reference} -> {target}")

    def test_required_public_copy(self) -> None:
        home = (ROOT / "index.html").read_text(encoding="utf-8").lower()
        for phrase in (
            "asistente personal de ia",
            "plataforma experimental de automatización",
            "proyecto personal",
            "en desarrollo",
            "auren.assistant@gmail.com",
        ):
            self.assertIn(phrase, home)

    def test_legal_pages_and_contact_are_linked(self) -> None:
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="./privacy/"', home)
        self.assertIn('href="./terms/"', home)
        self.assertIn('href="mailto:auren.assistant@gmail.com"', home)

    def test_only_official_contact_and_no_secret_shape(self) -> None:
        public_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in ROOT.rglob("*")
            if path.is_file() and ".git" not in path.parts and path.suffix.lower() in TEXT_SUFFIXES
        )
        emails = set(re.findall(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", public_text.lower()))
        self.assertEqual({"auren.assistant@gmail.com"}, emails)
        secret_terms = "|".join(("app_" + "secret", "access_" + "token"))
        suspicious = re.compile(rf"(?i)({secret_terms}|bearer\s+[a-z0-9._-]{{20,}}|-----begin [a-z ]+private key-----)")
        self.assertIsNone(suspicious.search(public_text))

    def test_no_third_party_runtime_resources(self) -> None:
        for path in HTML_FILES:
            parser = SiteParser()
            parser.feed(path.read_text(encoding="utf-8"))
            remote_resources = [url for url in parser.resources if urlsplit(url).scheme in {"http", "https"}]
            self.assertEqual([], remote_resources, path)

    def test_mobile_breakpoints_exist(self) -> None:
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn("@media (max-width: 820px)", css)
        self.assertIn("@media (max-width: 540px)", css)
        self.assertIn("prefers-reduced-motion", css)


if __name__ == "__main__":
    unittest.main()