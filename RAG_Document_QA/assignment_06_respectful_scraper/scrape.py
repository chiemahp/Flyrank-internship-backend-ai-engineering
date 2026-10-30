"""Small robots-aware scraper for explicitly configured public HTML pages."""

import argparse
import json
import logging
import time
from dataclasses import asdict, dataclass
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from requests import Response

USER_AGENT = "StudentRespectfulScraper/1.0 (+contact: student@example.invalid)"
REQUEST_TIMEOUT_SECONDS = 15
logger = logging.getLogger("respectful_scraper")


@dataclass
class Page:
    url: str
    title: str
    text: str


class RespectfulScraper:
    def __init__(self, delay: float = 2.0, max_pages: int = 10) -> None:
        if delay < 1.0:
            raise ValueError("delay must be at least one second")
        if max_pages < 1:
            raise ValueError("max_pages must be at least one")
        self.delay = delay
        self.max_pages = max_pages
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self._robots: dict[str, RobotFileParser] = {}
        self._last_request_at: float | None = None

    def _robots_for(self, url: str) -> RobotFileParser:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self._robots:
            robots_url = urljoin(origin, "/robots.txt")
            parser = RobotFileParser()
            parser.set_url(robots_url)
            try:
                response = self.session.get(
                    robots_url, timeout=REQUEST_TIMEOUT_SECONDS
                )
                if response.status_code == 404:
                    parser.parse([])
                else:
                    response.raise_for_status()
                    parser.parse(response.text.splitlines())
            except requests.RequestException as exc:
                logger.warning("Could not retrieve %s: %s", robots_url, exc)
                parser.disallow_all = True
            self._robots[origin] = parser
        return self._robots[origin]

    def _get(self, url: str) -> Response | None:
        if not self._robots_for(url).can_fetch(USER_AGENT, url):
            logger.warning("Blocked by robots.txt, skipping %s", url)
            return None
        if self._last_request_at is not None:
            wait = self.delay - (time.monotonic() - self._last_request_at)
            if wait > 0:
                time.sleep(wait)
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            self._last_request_at = time.monotonic()
            if response.status_code == 429:
                logger.warning("Rate limited (HTTP 429), stopping at %s", url)
                return None
            response.raise_for_status()
            if "text/html" not in response.headers.get("Content-Type", "").lower():
                logger.warning("Non-HTML response, skipping %s", url)
                return None
            return response
        except requests.RequestException as exc:
            logger.warning("Request failed for %s: %s", url, exc)
            return None

    def scrape(self, start_url: str) -> list[Page]:
        if urlparse(start_url).scheme not in {"http", "https"}:
            raise ValueError("start_url must use HTTP or HTTPS")

        start = urlparse(start_url)
        seen: set[str] = set()
        pending = [start_url]
        pages: list[Page] = []
        while pending and len(pages) < self.max_pages:
            url = pending.pop(0)
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or parsed.netloc != start.netloc:
                continue
            normalized = parsed._replace(fragment="").geturl()
            if normalized in seen:
                continue
            seen.add(normalized)
            response = self._get(normalized)
            if response is None:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            for unwanted in soup(["script", "style", "noscript", "svg"]):
                unwanted.decompose()
            title = soup.title.get_text(" ", strip=True) if soup.title else ""
            text = soup.get_text(" ", strip=True)
            pages.append(Page(url=normalized, title=title, text=text[:20_000]))

            for anchor in soup.find_all("a", href=True):
                candidate = urlparse(urljoin(normalized, anchor["href"]))
                if (
                    candidate.scheme in {"http", "https"}
                    and candidate.netloc == start.netloc
                ):
                    next_url = candidate._replace(fragment="").geturl()
                    if next_url not in seen and next_url not in pending:
                        pending.append(next_url)

        return pages


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Start URL on a public site you are permitted to scrape")
    parser.add_argument("--delay", type=float, default=2.0, help="Minimum seconds between page requests")
    parser.add_argument("--max-pages", type=int, default=10)
    parser.add_argument("--output", default="scraped_pages.json")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    pages = RespectfulScraper(delay=args.delay, max_pages=args.max_pages).scrape(args.url)
    with open(args.output, "w", encoding="utf-8") as output:
        json.dump([asdict(page) for page in pages], output, ensure_ascii=False, indent=2)
    print(f"Saved {len(pages)} page(s) to {args.output}")


if __name__ == "__main__":
    main()
