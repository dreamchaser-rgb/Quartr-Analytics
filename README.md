# SEC 10-K Fetcher

Fetches the latest 10-K (annual report) filing for a list of companies from
the SEC EDGAR API and converts each one to PDF.

Companies covered (edit `config.py` to change the list):
Apple, Meta, Alphabet, Amazon, Netflix, Goldman Sachs.

## How it works

1. **Ticker → CIK**: SEC identifies companies by CIK number, not ticker.
   `https://www.sec.gov/files/company_tickers.json` gives the mapping.
2. **Filing history**: `https://data.sec.gov/submissions/CIK{10-digit-cik}.json`
   returns each company's filing history. We filter for `form == "10-K"` and
   take the one with the most recent `filingDate`.
3. **Document download**: the filing's primary document (an HTML file) lives at
   `https://www.sec.gov/Archives/edgar/data/{cik}/{accession-no-without-dashes}/{primaryDocument}`.
4. **PDF conversion**: the HTML is rendered to PDF with WeasyPrint.
5. A `summary.json` is written alongside the PDFs with metadata (CIK,
   accession number, filing/report dates, source URL, PDF path) per company —
   this is the bit meant to be exposed to other teams.

## Setup

```bash
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Before running**, open `config.py` and put a real contact email in
`SEC_USER_AGENT`. SEC requires a descriptive User-Agent with contact info on
every request and will block generic/missing ones.

WeasyPrint needs a couple of system libraries (Pango/Cairo) to render HTML.
If `pip install weasyprint` doesn't work out of the box:
- macOS: `brew install pango`
- Debian/Ubuntu: `sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0`
- Windows: see WeasyPrint's install docs (GTK3 runtime needed)

If you'd rather avoid system dependencies entirely, swap `pdf_converter.py`
to use `pdfkit` (wraps the `wkhtmltopdf` binary) or Playwright's
headless-Chromium "print to PDF" — the rest of the code doesn't change.

## Run

```bash
python main.py
```

Output lands in `./output/`:
- `{TICKER}_10-K_{filing_date}.pdf` for each company
- `summary.json` with metadata for every company (including any failures)

## Notes / design choices

- **Rate limiting**: a small delay is added between requests to stay under
  SEC's 10 requests/second fair-access limit.
- **Error isolation**: if one company's fetch fails (e.g. no recent 10-K,
  network hiccup), it's recorded in `summary.json` with `status: "failed"`
  and the script keeps going for the rest.
- **Extending to other filing types**: change `FORM_TYPE` in `config.py`
  (e.g. `"10-Q"`) to reuse the same pipeline for other report types.
- **Turning this into a service**: `SECClient` and `html_to_pdf` are already
  separated from the CLI in `main.py`, so wrapping `get_latest_10k` +
  `download_document` + `html_to_pdf` behind an HTTP endpoint (e.g. FastAPI)
  is a small step from here — the core logic doesn't need to change.

## AI tool usage

An AI assistant (Claude) was used to help design and write this
implementation. See `PROMPT_LOG.md` for the conversation log, as required by
the assignment.
