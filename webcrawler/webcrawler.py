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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MultithreadCrawler:
    def __init__(self, start_url, max_pages=50, delay=0.0, max_workers=5, json_file="crawled_data.json"):
        self.start_url = start_url
        self.max_pages = max_pages
        self.delay = float(delay)
        self.max_workers = max_workers
        self.json_file = json_file

        self.headers = {
            "User-Agent": "MyWebCrawler"
        }

        parsed = urlparse(start_url)
        self.domain = parsed.netloc

        self.to_visit = deque([start_url])
        self.to_visit_set = {self.normalize_url(start_url)}
        self.visited = set()
        self.data = []
        self.lock = Lock()

        self.robot_parser = self._load_robots()

    def _load_robots(self):
        robots_url = urljoin(f"{urlparse(self.start_url).scheme}://{self.domain}", "/robots.txt")
        rp = RobotFileParser()
        try:
            rp.set_url(robots_url)
            rp.read()
            logger.info(f"robots.txt geladen von {robots_url}")
            return rp
        except Exception:
            logger.warning("robots.txt konnte nicht geladen werden; Crawling wird standardmäßig erlaubt.")
            return None

    def normalize_url(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            no_frag = parsed._replace(fragment="")
            norm = no_frag.geturl()
            if norm.endswith('/') and no_frag.path not in ('', '/'):
                norm = norm.rstrip('/')
            return norm
        except Exception:
            return url

    def can_fetch(self, url: str) -> bool:
        try:
            if not self.robot_parser:
                return True
            return self.robot_parser.can_fetch("*", self.normalize_url(url))
        except Exception:
            return True

    def is_same_domain(self, url: str) -> bool:
        try:
            return urlparse(url).netloc == self.domain
        except Exception:
            return False

    def fetch(self, url: str) -> str | None:
        if not self.can_fetch(url):
            logger.debug(f"robots.txt verbietet {url}")
            return None
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            if self.delay:
                time.sleep(self.delay)
            return resp.text
        except Exception as e:
            logger.debug(f"Fehler beim Abrufen {url}: {e}")
            return None

    def extract_title_and_links(self, base_url: str, html: str):
        try:
            soup = BeautifulSoup(html, "html.parser")
            title_tag = soup.title
            title = title_tag.string.strip() if title_tag and title_tag.string else "Kein Titel"

            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if not href:
                    continue
                absolute = urljoin(base_url, href)
                if self.is_same_domain(absolute):
                    links.append(self.normalize_url(absolute))

            return title, links
        except Exception as e:
            logger.debug(f"Fehler beim Parsen von {base_url}: {e}")
            return "Kein Titel", []

    def make_name_from_url(self, url: str) -> str:
        parsed = urlparse(url)
        name = parsed.netloc + parsed.path
        if name.endswith("/") and name != parsed.netloc + "/":
            name = name[:-1]
        return name

    def worker(self):
        while True:
            with self.lock:
                if not self.to_visit or len(self.visited) >= self.max_pages:
                    return
                url = self.to_visit.popleft()
                self.to_visit_set.discard(self.normalize_url(url))
                norm = self.normalize_url(url)
                if norm in self.visited:
                    continue
                self.visited.add(norm)

            logger.info(f"Crawle ({len(self.visited)}/{self.max_pages}): {norm}")

            html = self.fetch(url)
            if not html:
                continue

            title, links = self.extract_title_and_links(url, html)

            name = self.make_name_from_url(url)

            with self.lock:
                if not any(item[0] == name for item in self.data):
                    self.data.append([name, title])

            with self.lock:
                for link in links:
                    if link in self.visited or link in self.to_visit_set:
                        continue
                    if len(self.visited) + len(self.to_visit) >= self.max_pages:
                        break
                    self.to_visit.append(link)
                    self.to_visit_set.add(link)

    def crawl(self):
        logger.info(f"Starte Multithread-Crawl: {self.start_url} (max_pages={self.max_pages}, workers={self.max_workers})")
        with ThreadPoolExecutor(max_workers=self.max_workers) as exe:
            futures = [exe.submit(self.worker) for _ in range(self.max_workers)]
            for f in as_completed(futures):
                try:
                    f.result()
                except Exception as e:
                    logger.debug(f"Worker-Fehler: {e}")

        logger.info(f"Crawl abgeschlossen: {len(self.visited)} Seiten besucht, {len(self.data)} Einträge gesammelt.")
        return self.data

    def save_json(self):
        try:
            existing = []
            if os.path.exists(self.json_file):
                try:
                    with open(self.json_file, "r", encoding="utf-8") as f:
                        existing = json.load(f) or []
                except Exception:
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
            logger.info(f"Ergebnis gespeichert in {self.json_file} ({len(merged)} Einträge insgesamt).")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der JSON-Datei: {e}")


def main():
    parser = argparse.ArgumentParser(description="Multithreaded Webcrawler (Pfad + Titel als JSON)")
    parser.add_argument("--start-url", default="https://huggingface.co/", help="Start-URL zum Crawlen")
    parser.add_argument("--max-pages", type=int, default=50, help="Maximale Anzahl Seiten zum Crawlen")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay zwischen Anfragen in Sekunden (pro Anfrage)")
    parser.add_argument("--workers", type=int, default=12, help="Anzahl gleichzeitiger Threads")
    parser.add_argument("--json-file", default="crawled_data.json", help="JSON-Datei zum Speichern der Ergebnisse")
    args = parser.parse_args()

    crawler = MultithreadCrawler(
        start_url=args.start_url,
        max_pages=args.max_pages,
        delay=args.delay,
        max_workers=args.workers,
        json_file=args.json_file,
    )

    data = crawler.crawl()
    crawler.save_json()

    print("\n=== Crawl-Zusammenfassung ===")
    print(f"Start-URL: {args.start_url}")
    print(f"Domain: {crawler.domain}")
    print(f"Gesammelte Einträge: {len(data)}")
    print(f"JSON-Datei: {args.json_file}")

    print("\n=== JSON-Ausgabe (Beispiel) ===")
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
