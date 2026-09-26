"""Convert a downloaded HTML filing into a PDF."""
import logging

from weasyprint import HTML

logger = logging.getLogger(__name__)


def html_to_pdf(html_bytes: bytes, base_url: str, output_path: str) -> None:
    """Render an SEC filing (HTML) to PDF.

    base_url is required so any relative image/CSS references inside the
    filing resolve against the original SEC URL.
    """
    logger.info("Converting to PDF: %s", output_path)
    HTML(string=html_bytes, base_url=base_url).write_pdf(output_path)
