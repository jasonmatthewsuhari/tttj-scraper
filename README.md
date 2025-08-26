# tttj-scraper

Python scraper for Google Maps place info, reviews, and reviewer details using Playwright.

Important: Scraping Google services may violate their Terms of Service. Use responsibly for your own data collection, respect robots.txt, rate limits, and legal constraints. Prefer official APIs or third‑party compliant APIs when possible.

## Quick start (Windows)

1. Create venv and install deps

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m playwright install
```

2. Run CLI

```powershell
.\.venv\Scripts\python -m tttj_scraper --help
```

Examples:

```powershell
# By place URL
.\.venv\Scripts\python -m tttj_scraper scrape --place-url "https://www.google.com/maps/place/?q=place_id:ChIJN1t_tDeuEmsRUsoyG83frY4" --out out/place.json

# By search query + location
.\.venv\Scripts\python -m tttj_scraper scrape --query "coffee" --location "New York, NY" --max-places 3 --out out/nyc_coffee.json
```

Outputs JSON; CSV export optional via `--csv`.

## Features

- Place metadata: name, rating, reviews count, address, website, phone, hours, categories, plus code, coordinates
- Reviews: star rating, date, text, photos count, likes, owner response
- Reviewer: display name, profile URL, contribution count, location (when public)

## Notes

- "All reviews" requires scrolling pagination; heavy volumes may trigger rate‑limits/CAPTCHA. The CLI supports `--max-reviews` to cap volume and `--headful` to visualize.
- Prefer off‑peak hours and backoff. Consider rotating proxies.

## Development

```powershell
.\.venv\Scripts\python -m pip install -e .
```
