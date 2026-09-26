"""Thin client around the SEC EDGAR APIs.

Reference docs:
- https://www.sec.gov/os/accessing-edgar-data
- https://www.sec.gov/edgar/sec-api-documentation
"""
from __future__ import annotations

import time
import logging
from dataclasses import dataclass
from typing import Optional

import requests

from config import SEC_USER_AGENT, REQUEST_DELAY_SECONDS, FORM_TYPE

logger = logging.getLogger(__name__)

TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{document}"


@dataclass
class FilingInfo:
    ticker: str
    company_name: str
    cik: int
    accession_number: str
    primary_document: str
    filing_date: str
    report_date: str

    @property
    def document_url(self) -> str:
        accession_no_dashes = self.accession_number.replace("-", "")
        return ARCHIVE_URL.format(
            cik=self.cik,
            accession_no_dashes=accession_no_dashes,
            document=self.primary_document,
        )


class SECClient:
    def __init__(self, user_agent: str = SEC_USER_AGENT):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept-Encoding": "gzip, deflate",
        })
        self._cik_map: Optional[dict] = None

    def _get(self, url: str) -> requests.Response:
        resp = self.session.get(url, timeout=30)
        time.sleep(REQUEST_DELAY_SECONDS)  # stay comfortably under SEC's rate limit
        resp.raise_for_status()
        return resp

    def _load_cik_map(self) -> dict:
        if self._cik_map is None:
            logger.info("Fetching ticker -> CIK map from SEC")
            data = self._get(TICKERS_URL).json()
            # data shape: {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}, ...}
            self._cik_map = {row["ticker"].upper(): row["cik_str"] for row in data.values()}
        return self._cik_map

    def get_cik(self, ticker: str) -> int:
        cik_map = self._load_cik_map()
        try:
            return cik_map[ticker.upper()]
        except KeyError:
            raise ValueError(f"Ticker '{ticker}' not found in SEC ticker list")

    def get_latest_10k(self, ticker: str, company_name: str) -> FilingInfo:
        cik = self.get_cik(ticker)
        url = SUBMISSIONS_URL.format(cik=cik)
        logger.info("Fetching filing history for %s (CIK %s)", ticker, cik)
        data = self._get(url).json()

        recent = data["filings"]["recent"]
        forms = recent["form"]
        accession_numbers = recent["accessionNumber"]
        primary_docs = recent["primaryDocument"]
        filing_dates = recent["filingDate"]
        report_dates = recent["reportDate"]

        candidates = [i for i, form in enumerate(forms) if form == FORM_TYPE]
        if not candidates:
            # Companies with a long filing history sometimes have older filings
            # paginated under data["filings"]["files"] instead of "recent".
            # Not needed for these six companies (they all have a recent 10-K),
            # but that's where you'd look if this ever comes up.
            raise ValueError(f"No {FORM_TYPE} filings found for {ticker} in recent submissions")

        # filingDate is ISO-formatted (YYYY-MM-DD), so string comparison sorts correctly.
        latest_idx = max(candidates, key=lambda i: filing_dates[i])

        return FilingInfo(
            ticker=ticker,
            company_name=company_name,
            cik=cik,
            accession_number=accession_numbers[latest_idx],
            primary_document=primary_docs[latest_idx],
            filing_date=filing_dates[latest_idx],
            report_date=report_dates[latest_idx],
        )

    def download_document(self, filing: FilingInfo) -> bytes:
        logger.info("Downloading %s 10-K document from %s", filing.ticker, filing.document_url)
        return self._get(filing.document_url).content
