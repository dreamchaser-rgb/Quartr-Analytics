"""Entry point: fetch the latest 10-K for each configured company and
convert it to PDF.

Usage:
    python main.py
"""
import json
import logging
import os

from config import COMPANIES, OUTPUT_DIR
from sec_client import SECClient
from pdf_converter import html_to_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    client = SECClient()
    results = []

    for ticker, company_name in COMPANIES.items():
        try:
            filing = client.get_latest_10k(ticker, company_name)
            html_bytes = client.download_document(filing)

            pdf_filename = f"{ticker}_10-K_{filing.filing_date}.pdf"
            pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
            html_to_pdf(html_bytes, pdf_path)

            results.append({
                "ticker": filing.ticker,
                "company_name": filing.company_name,
                "cik": filing.cik,
                "accession_number": filing.accession_number,
                "filing_date": filing.filing_date,
                "report_date": filing.report_date,
                "source_url": filing.document_url,
                "pdf_path": pdf_path,
                "status": "success",
            })
            logger.info("Done: %s -> %s", ticker, pdf_path)

        except Exception as exc:
            logger.exception("Failed to process %s", ticker)
            results.append({
                "ticker": ticker,
                "company_name": company_name,
                "status": "failed",
                "error": str(exc),
            })

    summary_path = os.path.join(OUTPUT_DIR, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info("Summary written to %s", summary_path)


if __name__ == "__main__":
    main()
