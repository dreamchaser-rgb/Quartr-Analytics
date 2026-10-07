"""Configuration for the SEC 10-K fetcher service."""

# SEC requires a descriptive User-Agent with real contact info on every
# request. Requests without one get rejected or throttled.
# -> Replace the email below before running.
SEC_USER_AGENT = "dummymail123@gmail.com"

# Ticker -> display name for the companies this assignment asks for.
COMPANIES = {
    "AAPL": "Apple Inc.",
    "META": "Meta Platforms, Inc.",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com, Inc.",
    "NFLX": "Netflix, Inc.",
    "GS": "The Goldman Sachs Group, Inc.",
}

FORM_TYPE = "10-K"

OUTPUT_DIR = "output"

# SEC's fair-access policy asks automated tools to stay under 10 req/sec.
REQUEST_DELAY_SECONDS = 0.15
