# Nexora Searchengine

Nexora is a modern, lightweight search frontend featuring a high-performance multithreaded Python web crawler. The project is designed to be straightforward, portable, and self-contained — requiring no server, no Node.js, and no build tools.

## Key Points

- **Frontend:** Static HTML / CSS / JS — simply open `index.html` in your browser to search.
- **Crawler:** Python script (`webcrawler/webcrawler.py`) that optionally generates `crawled_data.json` for search content.
- **No Node.js or build tooling required.**

## Features

- Efficient, multithreaded Python crawler (fully configurable)
- Crawl data stored as JSON for seamless frontend use
- Service Worker for offline-ready search and speed
- Modern, responsive UI for local JSON search
- Easy customization: modular frontend and backend

## Quick Start (Recommended)

You do **not** need to run the crawler to use the search — a ready-to-use `crawled_data.json` is included! For most use cases:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Developer012345678910/Searchengine.git
   cd Searchengine
   ```
2. **Start a sever with  ```python -m http.server 8000```**
3. **Then open the port in your webbrowser ```localhost:8000```**

If `crawled_data.json` is available in the project directory, the UI will immediately provide search results from that dataset.

---

## Optional: Generate or Update Crawl Data

The crawler is for those who want to generate or refresh their own dataset. Maintainers periodically update the default `crawled_data.json` for releases and demos; you only need to run the crawler if you wish to customize or extend the indexed sites.

**Install dependencies:**
```bash
pip install -r webcrawler/requirements.txt
```

**Run the crawler (example):**
```bash
python webcrawler/webcrawler.py \
  --start-url https://www.example.com/ \
  --max-pages 50 \
  --json-file crawled_data.json
```

**Notes:**
- The crawler will honor robots.txt where possible.
- Crawler execution is optional and intended for dataset refresh and development, not for production frontend use.

---

## Project Structure

```
Searchengine/
├── CSS/                   # Stylesheets
├── JS/                    # Frontend logic & service worker
├── webcrawler/            # Python crawler code
│   ├── webcrawler.py
│   ├── requirements.txt
│   └── How_to_use.txt
├── index.html             # Main application
├── crawled_data.json      # Example/search data (optional)
├── README.md
├── CONTRIBUTING.md
└── LICENSE.md
```

## Contributing

Community contributions are welcomed! If your PR changes or adds crawl data, please document which seed URL(s) and crawler options you used. Be sure to see `CONTRIBUTING.md` for guidelines.

## License

MIT License — see `LICENSE.md`.
