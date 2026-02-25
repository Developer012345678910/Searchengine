#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MultithreadCrawler:
    def __init__(
        self,
        start_url: str,
        max_pages: int = 50,
        delay: float = 0.0,
        max_workers: int = 5,
        json_file: str = "crawled_data.json",
        timeout: int = 10,
    ):
        # Validate start URL
        self._validate_url(start_url)

        self.start_url = start_url
        self.max_pages = max_pages
        self.delay = float(delay)
        self.max_workers = max_workers
        self.json_file = json_file
        self.timeout = timeout

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        parsed = urlparse(start_url)
        self.domain = parsed.netloc

        self.to_visit = deque([start_url])
        self.to_visit_set = {self.normalize_url(start_url)}
        self.visited = set()
        self.processed_names = set()  # Track processed page names for O(1) lookup
        self.data = []
        self.lock = Lock()

        # Initialize session with connection pooling and retry strategy
        self.session = self._create_session()
        self.robot_parser = self._load_robots()

    @staticmethod
    def _validate_url(url: str) -> None:
        """Validate that the URL is properly formatted."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError(f"Invalid URL format: {url}")
        except Exception as e:
            raise ValueError(f"Invalid URL: {url}") from e

    def _create_session(self) -> requests.Session:
        """Create a requests session with connection pooling and retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _load_robots(self) -> RobotFileParser | None:
        """Load and parse robots.txt file from the domain."""
        robots_url = urljoin(f"{urlparse(self.start_url).scheme}://{self.domain}", "/robots.txt")
        rp = RobotFileParser()
        try:
            rp.set_url(robots_url)
            rp.read()
            logger.info(f"Successfully loaded robots.txt from {robots_url}")
            return rp
        except requests.RequestException as e:
            logger.warning(f"Failed to load robots.txt from {robots_url}: {e}. Crawling will be allowed by default.")
            return None
        except Exception as e:
            logger.warning(f"Error parsing robots.txt: {e}. Crawling will be allowed by default.")
            return None

    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and trailing slashes."""
        try:
            parsed = urlparse(url)
            no_frag = parsed._replace(fragment="")
            norm = no_frag.geturl()
            if norm.endswith("/") and no_frag.path not in ("", "/"):
                norm = norm.rstrip("/")
            return norm
        except (ValueError, AttributeError) as e:
            logger.debug(f"Error normalizing URL {url}: {e}")
            return url

    def can_fetch(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""
        try:
            if not self.robot_parser:
                return True
            return self.robot_parser.can_fetch("*", self.normalize_url(url))
        except (ValueError, AttributeError, TypeError) as e:
            logger.debug(f"Error checking robots.txt for {url}: {e}")
            return True

    def is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain."""
        try:
            return urlparse(url).netloc == self.domain
        except (ValueError, AttributeError) as e:
            logger.debug(f"Error checking domain for {url}: {e}")
            return False

    def fetch(self, url: str) -> str | None:
        """Fetch HTML content from URL, respecting robots.txt and rate limits."""
        if not self.can_fetch(url):
            logger.debug(f"robots.txt disallows fetching {url}")
            return None
        try:
            resp = self.session.get(url, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            if self.delay:
                time.sleep(self.delay)
            return resp.text
        except requests.HTTPError as e:
            logger.debug(f"HTTP error fetching {url}: {e.response.status_code}")
            return None
        except requests.Timeout:
            logger.debug(f"Timeout fetching {url}")
            return None
        except requests.RequestException as e:
            logger.debug(f"Error fetching {url}: {e}")
            return None

    def extract_title_and_links(self, base_url: str, html: str) -> tuple[str, list[str]]:
        """Extract page title and internal links from HTML content."""
        try:
            soup = BeautifulSoup(html, "html.parser")
            title_tag = soup.title
            title = title_tag.string.strip() if title_tag and title_tag.string else "No Title"

            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if not href:
                    continue
                absolute = urljoin(base_url, href)
                if self.is_same_domain(absolute):
                    links.append(self.normalize_url(absolute))

            return title, links
        except AttributeError as e:
            logger.debug(f"BeautifulSoup parsing error for {base_url}: {e}")
            return "No Title", []
        except Exception as e:
            logger.debug(f"Error parsing HTML from {base_url}: {e}")
            return "No Title", []

    def make_name_from_url(self, url: str) -> str:
        """Generate a unique name from URL for deduplication."""
        parsed = urlparse(url)
        name = parsed.netloc + parsed.path
        if name.endswith("/") and name != parsed.netloc + "/":
            name = name[:-1]
        return name

    def worker(self) -> None:
        """Worker thread that crawls URLs from the queue."""
        while True:
            # Critical section: get next URL and mark as visited
            with self.lock:
                # Exit if queue is empty or max pages reached
                if not self.to_visit or len(self.visited) >= self.max_pages:
                    return

                # Get URL from queue
                url = self.to_visit.popleft()
                self.to_visit_set.discard(self.normalize_url(url))
                norm = self.normalize_url(url)

                # Check if already visited (avoid duplicate processing)
                if norm in self.visited:
                    continue

                # Mark as visited before releasing lock
                self.visited.add(norm)

            # Non-critical section: fetch and process URL (no lock held)
            logger.info(f"Crawling ({len(self.visited)}/{self.max_pages}): {norm}")

            html = self.fetch(url)
            if not html:
                continue

            title, links = self.extract_title_and_links(url, html)
            name = self.make_name_from_url(url)

            # Critical section: add data if not already processed
            with self.lock:
                if name not in self.processed_names:
                    self.processed_names.add(name)
                    self.data.append([name, title])

            # Critical section: add new links to queue
            with self.lock:
                for link in links:
                    if link in self.visited or link in self.to_visit_set:
                        continue
                    if len(self.visited) + len(self.to_visit) >= self.max_pages:
                        break
                    self.to_visit.append(link)
                    self.to_visit_set.add(link)

    def crawl(self) -> list[list[str]]:
        """Start the multi-threaded crawling process."""
        logger.info(
            f"Starting multi-threaded crawl: {self.start_url} "
            f"(max_pages={self.max_pages}, workers={self.max_workers})"
        )
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.worker) for _ in range(self.max_workers)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Worker thread error: {e}", exc_info=True)

        logger.info(
            f"Crawl complete: {len(self.visited)} pages visited, {len(self.data)} entries collected."
        )
        return self.data

    def save_json(self) -> None:
        """Save crawled data to JSON file, merging with existing data."""
        try:
            existing = []
            if os.path.exists(self.json_file):
                try:
                    with open(self.json_file, "r", encoding="utf-8") as f:
                        existing = json.load(f) or []
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Error reading existing JSON file: {e}. Starting fresh.")
                    existing = []

            seen = {tuple(item) for item in existing if isinstance(item, list) and len(item) == 2}
            merged = list(existing)

            for rec in self.data:
                key = tuple(rec)
                if key in seen:
                    continue
                seen.add(key)
                merged.append(rec)

            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(merged, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {self.json_file} ({len(merged)} total entries).")
        except IOError as e:
            logger.error(f"Error writing JSON file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving JSON: {e}")


def main() -> None:
    """Parse arguments and run the crawler."""
    parser = argparse.ArgumentParser(
        description="Multi-threaded web crawler that extracts page titles and links as JSON"
    )
    parser.add_argument(
        "--start-url",
        default="https://huggingface.co/",
        help="Starting URL for crawling",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Maximum number of pages to crawl",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Delay between requests in seconds (per request)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=12,
        help="Number of concurrent worker threads",
    )
    parser.add_argument(
        "--json-file",
        default="crawled_data.json",
        help="Output JSON file for results",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Request timeout in seconds",
    )
    args = parser.parse_args()

    try:
        crawler = MultithreadCrawler(
            start_url=args.start_url,
            max_pages=args.max_pages,
            delay=args.delay,
            max_workers=args.workers,
            json_file=args.json_file,
            timeout=args.timeout,
        )

        data = crawler.crawl()
        crawler.save_json()

        print("\n=== Crawl Summary ===")
        print(f"Start URL: {args.start_url}")
        print(f"Domain: {crawler.domain}")
        print(f"Collected entries: {len(data)}")
        print(f"JSON file: {args.json_file}")

        print("\n=== JSON Output (Sample) ===")
        print(json.dumps(data[:10], ensure_ascii=False, indent=2))
        if len(data) > 10:
            print(f"... and {len(data) - 10} more entries")
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        parser.print_help()
        exit(1)
    except KeyboardInterrupt:
        logger.info("Crawling interrupted by user")
        exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()
