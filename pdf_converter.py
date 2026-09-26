"""Convert a downloaded SEC filing (HTML) into a PDF using headless Chromium.

We render from a local temp file rather than letting the browser navigate
directly to the live SEC URL, since SEC's automated-traffic detection can
flag a headless browser's own fingerprint even with a compliant
User-Agent. The HTML is downloaded first via requests (which SEC does
accept) and rendered locally instead.
"""
import logging
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


def html_to_pdf(html_bytes: bytes, output_path: str) -> None:
    logger.info("Converting to PDF: %s", output_path)
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        tmp.write(html_bytes)
        tmp_path = Path(tmp.name)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(tmp_path.as_uri())
            page.pdf(path=output_path, format="A4", print_background=True)
            browser.close()
    finally:
        tmp_path.unlink(missing_ok=True)
