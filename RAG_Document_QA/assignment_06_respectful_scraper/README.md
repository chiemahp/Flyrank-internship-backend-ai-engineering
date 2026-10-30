# Assignment 6 — A scraper that respects the sites it collects from

The scraper is intentionally limited to one site origin, requires permission from `robots.txt` when it is available, waits at least one second between page requests (two seconds by default), caps pages, uses timeouts, skips non-HTML content, and stops on HTTP 429. A failed robots.txt request fails closed.

Use it only on public pages you are authorized to access. Do not bypass access controls, logins, CAPTCHAs, or site restrictions. Review the site's terms and robots policy and identify the scraper with an honest contact before use.

## Run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scrape.py https://example.org --max-pages 5 --delay 2 --output results.json
```

Output is JSON containing the URL, page title, and extracted text. This is an educational example, not a guarantee that a site's terms permit automated collection.
