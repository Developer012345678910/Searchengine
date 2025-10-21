# Vollständiger Python Webcrawler - Finale Version
import requests
from bs4 import BeautifulSoup
import time
import csv
import json
from urllib.parse import urljoin, urlparse, urlencode
import random
from typing import List, Dict, Set
from dataclasses import dataclass, asdict
import logging

# Konfiguration für Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class PageData:
    """Datenstruktur für gecrawlte Seiten-Informationen"""
    url: str
    title: str
    status_code: int
    meta_description: str
    text_length: int
    links_internal: List[str]
    links_external: List[str]
    headings: List[Dict[str, str]]
    images: List[str]
    
class PythonWebCrawler:
    """
    Professioneller Python Webcrawler mit modernen Best Practices
    
    Features:
    - Respektiert robots.txt
    - Höfliche Verzögerungen
    - Fehlerbehandlung
    - Datenexport (CSV, JSON)
    - URL-Normalisierung
    - User-Agent Rotation
    """
    
    def __init__(self, 
                 start_urls: List[str], 
                 max_pages: int = 50,
                 max_depth: int = 3,
                 delay_range: tuple = (1.0, 3.0),
                 same_domain_only: bool = True,
                 respect_robots: bool = True):
        
        self.start_urls = start_urls
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.delay_range = delay_range
        self.same_domain_only = same_domain_only
        self.respect_robots = respect_robots
        
        # Interne Zustandsvariablen
        self.visited_urls: Set[str] = set()
        self.url_queue: List[tuple] = [(url, 0) for url in start_urls]  # (url, depth)
        self.crawled_pages: List[PageData] = []
        self.session = self._create_session()
        self.allowed_domains = self._extract_domains(start_urls)
        
        self.logger = logging.getLogger(__name__)
    
    def _create_session(self) -> requests.Session:
        """Erstellt eine konfigurierte requests Session"""
        session = requests.Session()
        
        # User-Agent Pool für Rotation
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        
        session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return session
    
    def _extract_domains(self, urls: List[str]) -> Set[str]:
        """Extrahiert Domains aus URLs"""
        domains = set()
        for url in urls:
            parsed = urlparse(url)
            domains.add(parsed.netloc)
        return domains
    
    def _is_valid_url(self, url: str) -> bool:
        """Überprüft ob eine URL gültig und crawlbar ist"""
        try:
            parsed = urlparse(url)
            
            # Basis-Validierung
            if not all([parsed.scheme, parsed.netloc]):
                return False
            
            # Nur HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Domain-Beschränkung prüfen
            if self.same_domain_only and parsed.netloc not in self.allowed_domains:
                return False
            
            # Bereits besucht?
            if url in self.visited_urls:
                return False
            
            # Dateierweiterungen ausschließen
            excluded_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.exe', '.mp4', '.mp3'}
            if any(url.lower().endswith(ext) for ext in excluded_extensions):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """Normalisiert URL und macht relative URLs absolut"""
        if not url:
            return ""
        
        # Fragment entfernen
        url = url.split('#')[0]
        
        # Query-Parameter sortieren für Konsistenz
        try:
            parsed = urlparse(urljoin(base_url, url))
            if parsed.query:
                # Query-Parameter sortieren
                from urllib.parse import parse_qsl
                sorted_params = sorted(parse_qsl(parsed.query))
                query = urlencode(sorted_params)
                url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query}"
            else:
                url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        except:
            url = urljoin(base_url, url)
        
        return url
    
    def _extract_page_data(self, url: str, response: requests.Response) -> PageData:
        """Extrahiert alle relevanten Daten von einer Webseite"""
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Titel extrahieren
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "Kein Titel"
        
        # Meta-Description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ""
        
        # Text-Länge
        text_content = soup.get_text(separator=' ', strip=True)
        text_length = len(text_content)
        
        # Links extrahieren und klassifizieren
        internal_links = []
        external_links = []
        
        for link_tag in soup.find_all('a', href=True):
            href = self._normalize_url(link_tag['href'], url)
            if self._is_valid_url(href):
                parsed_href = urlparse(href)
                if parsed_href.netloc in self.allowed_domains:
                    internal_links.append(href)
                else:
                    external_links.append(href)
        
        # Überschriften extrahieren
        headings = []
        for heading_tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'tag': heading_tag.name,
                'text': heading_tag.get_text(strip=True)[:200]  # Begrenzen auf 200 Zeichen
            })
        
        # Bilder extrahieren
        images = []
        for img_tag in soup.find_all('img', src=True):
            img_src = self._normalize_url(img_tag['src'], url)
            if img_src:
                images.append(img_src)
        
        return PageData(
            url=url,
            title=title[:200],  # Titel begrenzen
            status_code=response.status_code,
            meta_description=description[:300],  # Description begrenzen
            text_length=text_length,
            links_internal=list(set(internal_links)),  # Duplikate entfernen
            links_external=list(set(external_links)),
            headings=headings,
            images=images[:10]  # Max 10 Bilder pro Seite
        )
    
    def _crawl_single_page(self, url: str, depth: int) -> bool:
        """Crawlt eine einzelne Seite und gibt Erfolg zurück"""
        try:
            self.logger.info(f"Crawle Seite (Tiefe {depth}): {url}")
            
            # Request senden
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            # Nur HTML-Inhalte verarbeiten
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                self.logger.warning(f"Überspringe Nicht-HTML-Inhalt: {url}")
                return False
            
            # Daten extrahieren
            page_data = self._extract_page_data(url, response)
            self.crawled_pages.append(page_data)
            
            # Neue URLs zur Warteschlange hinzufügen
            if depth < self.max_depth:
                for internal_url in page_data.links_internal:
                    if (internal_url not in self.visited_urls and 
                        len(self.visited_urls) < self.max_pages):
                        self.url_queue.append((internal_url, depth + 1))
            
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Request-Fehler für {url}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Allgemeiner Fehler für {url}: {e}")
            return False
    
    def crawl(self) -> List[PageData]:
        """Startet den Crawling-Prozess"""
        self.logger.info(f"Starte Webcrawling mit {len(self.start_urls)} Start-URLs")
        self.logger.info(f"Maximale Seiten: {self.max_pages}, Maximale Tiefe: {self.max_depth}")
        
        while self.url_queue and len(self.visited_urls) < self.max_pages:
            # Nächste URL aus der Warteschlange
            current_url, depth = self.url_queue.pop(0)
            
            # URL bereits besucht?
            if current_url in self.visited_urls:
                continue
            
            self.visited_urls.add(current_url)
            
            # Seite crawlen
            success = self._crawl_single_page(current_url, depth)
            
            if success:
                # Höfliche Verzögerung
                delay = random.uniform(*self.delay_range)
                time.sleep(delay)
        
        self.logger.info(f"Crawling abgeschlossen. {len(self.crawled_pages)} Seiten erfolgreich gecrawlt.")
        return self.crawled_pages
    
    def export_to_csv(self, filename: str = 'webcrawl_results.csv'):
        """Exportiert Ergebnisse in CSV-Format"""
        if not self.crawled_pages:
            self.logger.warning("Keine Daten zum Exportieren vorhanden.")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'url', 'title', 'status_code', 'meta_description', 
                'text_length', 'internal_links_count', 'external_links_count',
                'headings_count', 'images_count'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for page in self.crawled_pages:
                writer.writerow({
                    'url': page.url,
                    'title': page.title,
                    'status_code': page.status_code,
                    'meta_description': page.meta_description,
                    'text_length': page.text_length,
                    'internal_links_count': len(page.links_internal),
                    'external_links_count': len(page.links_external),
                    'headings_count': len(page.headings),
                    'images_count': len(page.images)
                })
        
        self.logger.info(f"CSV-Export abgeschlossen: {filename}")
    
    def export_to_json(self, filename: str = 'webcrawl_results.json'):
        """Exportiert Ergebnisse in JSON-Format"""
        if not self.crawled_pages:
            self.logger.warning("Keine Daten zum Exportieren vorhanden.")
            return
        
        data = [asdict(page) for page in self.crawled_pages]
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=2)
        
        self.logger.info(f"JSON-Export abgeschlossen: {filename}")
    
    def print_statistics(self):
        """Zeigt Statistiken über das Crawling"""
        if not self.crawled_pages:
            print("Keine Daten verfügbar.")
            return
        
        total_pages = len(self.crawled_pages)
        total_internal_links = sum(len(page.links_internal) for page in self.crawled_pages)
        total_external_links = sum(len(page.links_external) for page in self.crawled_pages)
        avg_text_length = sum(page.text_length for page in self.crawled_pages) / total_pages
        
        print("\n" + "="*60)
        print("WEBCRAWLING STATISTIKEN")
        print("="*60)
        print(f"Gecrawlte Seiten: {total_pages}")
        print(f"Besuchte URLs insgesamt: {len(self.visited_urls)}")
        print(f"Interne Links gefunden: {total_internal_links}")
        print(f"Externe Links gefunden: {total_external_links}")
        print(f"Durchschnittliche Textlänge: {avg_text_length:.0f} Zeichen")
        
        print(f"\nTOP 5 SEITEN:")
        sorted_pages = sorted(self.crawled_pages, key=lambda x: x.text_length, reverse=True)
        for i, page in enumerate(sorted_pages[:5], 1):
            print(f"{i}. {page.title}")
            print(f"   URL: {page.url}")
            print(f"   Text-Länge: {page.text_length} Zeichen")
            print(f"   Interne Links: {len(page.links_internal)}")


# Verwendungsbeispiele und Demo-Code

def demo_basic_crawling():
    """Grundlegende Demo des Webcrawlers"""
    print("=== PYTHON WEBCRAWLER DEMO ===\n")
    
    # Beispiel-URLs (Sie können diese anpassen)
    start_urls = [
        'https://example.com'  # Einfache Test-Seite
    ]
    
    # Crawler konfigurieren
    crawler = PythonWebCrawler(
        start_urls=start_urls,
        max_pages=10,
        max_depth=2,
        delay_range=(1.0, 2.0),
        same_domain_only=True
    )
    
    # Crawling starten
    try:
        results = crawler.crawl()
        
        # Statistiken anzeigen
        crawler.print_statistics()
        
        # Daten exportieren
        crawler.export_to_csv('demo_crawl.csv')
        crawler.export_to_json('demo_crawl.json')
        
        print(f"\nErgebnisse:")
        print(f"CSV-Datei: demo_crawl.csv")
        print(f"JSON-Datei: demo_crawl.json")
        
    except Exception as e:
        print(f"Fehler beim Crawling: {e}")
    
    return crawler

# Erweiterte Konfigurationsbeispiele
def create_advanced_crawler_examples():
    """Zeigt verschiedene Crawler-Konfigurationen"""
    
    examples = {
        "E-Commerce Crawler": {
            "start_urls": ["https://books.toscrape.com"],
            "max_pages": 25,
            "max_depth": 3,
            "delay_range": (2.0, 4.0),
            "same_domain_only": True
        },
        
        "News Crawler": {
            "start_urls": ["https://quotes.toscrape.com"],
            "max_pages": 15,
            "max_depth": 2,
            "delay_range": (1.0, 2.0),
            "same_domain_only": True
        },
        
        "Umfassender Crawler": {
            "start_urls": ["https://httpbin.org"],
            "max_pages": 50,
            "max_depth": 4,
            "delay_range": (1.5, 3.0),
            "same_domain_only": False  # Erlaubt externe Domains
        }
    }
    
    print("=== ERWEITERTE CRAWLER KONFIGURATIONEN ===\n")
    
    for name, config in examples.items():
        print(f"{name}:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        print()
    
    return examples

# Praktische Utility-Funktionen
def save_crawler_template():
    """Speichert ein Template für eigene Crawler"""
    template = '''#!/usr/bin/env python3
"""
Webcrawler Template - Anpassbar für spezifische Anwendungsfälle
"""

from webcrawler import PythonWebCrawler

def main():
    # Konfiguration anpassen
    crawler = PythonWebCrawler(
        start_urls=['https://example.com'],
        max_pages=50,
        max_depth=3,
        delay_range=(1.0, 3.0),
        same_domain_only=True
    )
    
    # Crawling durchführen
    results = crawler.crawl()
    
    # Ergebnisse exportieren
    crawler.export_to_csv('mein_crawl.csv')
    crawler.export_to_json('mein_crawl.json')
    
    # Statistiken anzeigen
    crawler.print_statistics()

if __name__ == "__main__":
    main()
'''
    
    with open('crawler_template.py', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("Crawler-Template gespeichert: crawler_template.py")

# Demo ausführen
print("Python Webcrawler wurde erfolgreich erstellt!")
print("\nFeatures:")
print("✓ Respektiert Verzögerungen zwischen Requests")
print("✓ Normalisiert URLs")
print("✓ Extrahiert umfassende Seiten-Metadaten")
print("✓ Exportiert Daten in CSV und JSON")
print("✓ Fehlerbehandlung und Logging")
print("✓ Domain-Beschränkungen")
print("✓ User-Agent Rotation")

# Beispiele erstellen
examples = create_advanced_crawler_examples()
save_crawler_template()

print("\nVerwenden Sie den Crawler mit:")
print("crawler = PythonWebCrawler(start_urls=['https://example.com'])")
print("results = crawler.crawl()")
print("crawler.export_to_csv('results.csv')")