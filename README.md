# Nexora Searchengine 🚀🔍

Nexora is a modern, lightweight search frontend powered by a high-performance multithreaded Python web crawler. The project is designed to be straightforward, portable, and self-contained — with no Node.js, no build tools, and no heavy server stacks required.

---

✨ Key Points

- **Frontend:** Static HTML / CSS / JS — just open `index.html` in your browser to search! 😃  
- **Crawler:** Python script (`webcrawler/webcrawler.py`) that optionally generates `crawled_data.json` for search content 🐍  
- **No Node.js or build tools required**  
- **You need Python to run a local server for best experience** 🖥️

---

🎯 Features

- ⚡ Efficient, multithreaded Python crawler (fully configurable)  
- 📦 Crawl data stored as JSON for seamless frontend use  
- ✅ Service Worker for offline-ready search & fast performance  
- ✨ Modern, responsive UI for local JSON search  
- 🛠️ Easy customization: modular frontend & backend

---

🚦 Quick Start

You do not need to run the crawler to use the search — a ready-to-use `crawled_data.json` is included! For most users:

1. Clone the repository:
```bash
git clone https://github.com/Developer012345678910/Searchengine.git
cd Searchengine
```

2. Install Python  
Download and install the newest Python version from [python.org](https://www.python.org/) 🐍

3. Run a local server:
Start a local server for best results:
```bash
python -m http.server 8000
```

4. Open your browser:  
Visit http://localhost:8000 🌟

If `crawled_data.json` is present, you’ll instantly get search results from that dataset.

---

🕹️ Optional: Generate or Update Crawl Data

Use the crawler if you want to create or refresh your own search dataset.

1. Install dependencies:
```bash
pip install -r webcrawler/requirements.txt
```

2. Run the crawler (example):
```bash
python webcrawler/webcrawler.py \
  --start-url https://www.example.com/ \
  --max-pages 50 \
  --json-file crawled_data.json
```

Notes:
- 🛑 The crawler honors `robots.txt` where possible.  
- ⚙️ Running the crawler is optional and intended for dataset updates & development — not required for everyday searching.

---

🗂️ Project Structure

```
Searchengine/
├── CSS/                   # 🎨 Stylesheets
├── JS/                    # ✨ Frontend logic & service worker
├── webcrawler/            # 🐍 Python crawler code
│   ├── webcrawler.py
│   ├── requirements.txt
│   └── How_to_use.txt
├── index.html             # 🏠 Main application
├── crawled_data.json      # 🔎 Example/search data (optional)
├── README.md
├── CONTRIBUTING.md
└── LICENSE.md
```

---

🤝 Contributing

PRs and ideas are welcome! 🙌 If your PR changes or adds crawl data, please document which seed URL(s) and crawler options you used. See [CONTRIBUTING.md](https://github.com/Developer012345678910/Searchengine?tab=contributing-ov-file#contributing-to-nexora-searchengine) for details.

---

📄 License

MIT License — see [LICENSE.md](https://github.com/Developer012345678910/Searchengine?tab=MIT-1-ov-file)
