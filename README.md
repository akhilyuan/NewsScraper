# TechCrunch News Scraper

A professional-grade asynchronous web scraper built with Python for extracting articles from TechCrunch. This project demonstrates advanced web scraping techniques, asynchronous programming, and data processing capabilities.

## 🚀 Features

- **Asynchronous Architecture**: Built with `aiohttp` and `asyncio` for high-performance concurrent scraping
- **Smart Rate Limiting**: Configurable random delays between requests to avoid being blocked
- **User Agent Rotation**: Multiple browser user agents to mimic real user behavior
- **Robust Error Handling**: Comprehensive error tracking and reporting
- **Data Export**: Clean CSV output with structured data
- **Command Line Interface**: Flexible CLI with multiple configuration options
- **Detailed Reporting**: Comprehensive scraping statistics and analytics
- **Professional Code Structure**: Clean, maintainable code with proper documentation

## 📋 Requirements

```
Python 3.7+
aiohttp>=3.8.0
beautifulsoup4>=4.11.0
pandas>=1.5.0
requests>=2.28.0
```

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/techcrunch-scraper.git
cd techcrunch-scraper
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📁 Project Structure

```
techcrunch-scraper/
├── scraper.py          # Main scraper implementation
├── utils.py            # Utility functions (clean_text, get_hash)
├── README.md          # This file
└── output/            # Default output directory
    └── .gitkeep
```

## 🚀 Quick Start

### Basic Usage

```bash
python scraper.py
```

This will scrape 5 pages from TechCrunch and save results to `techcrunch_articles.csv`.

### Advanced Usage

```bash
python scraper.py --pages 10 --output tech_news.csv --delay-min 2 --delay-max 5
```

## 📖 Usage Examples

### Command Line Options

```bash
# Scrape 20 pages with custom delays
python scraper.py --pages 20 --delay-min 1.5 --delay-max 4.0

# Custom output file
python scraper.py --output my_articles.csv

# Skip the detailed report
python scraper.py --no-report

# Enable debug logging
python scraper.py --log-level DEBUG
```

### Programmatic Usage

```python
import asyncio
from scraper import TechCrunchScraper

async def main():
    async with TechCrunchScraper(max_pages=10) as scraper:
        articles = await scraper.scrape_all_pages()
        print(f"Scraped {len(articles)} articles")
        
        for article in articles[:5]:  # Print first 5
            print(f"Title: {article.title}")
            print(f"Author: {article.author}")
            print(f"Published: {article.publish_time}")
            print("-" * 50)

asyncio.run(main())
```

## 📊 Data Structure

Each scraped article contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Always "TechCrunch" |
| `title` | string | Article headline |
| `url` | string | Full article URL |
| `author` | string | Article author name |
| `publish_time` | string | Publication date (YYYY-MM-DD HH:MM) |
| `hash` | string | Unique hash of the title |
| `category` | string | Article category (future feature) |
| `excerpt` | string | Article excerpt (future feature) |
| `scraped_at` | string | Timestamp when scraped |

## 🎯 Key Technical Features

### Async/Await Architecture
- Non-blocking I/O operations for better performance
- Concurrent request handling with connection pooling
- Proper resource management with context managers

### Anti-Detection Measures
- Random user agent rotation from real browser strings
- Configurable delays between requests (1-3 seconds default)
- Respectful scraping practices to avoid being blocked

### Error Handling & Monitoring
- Comprehensive error tracking and logging
- Graceful handling of network failures
- Detailed reporting with success/failure statistics

### Data Quality Assurance
- Text cleaning and normalization
- Duplicate detection via content hashing
- Structured data validation

## 📊 Sample Output

### CSV Export
```csv
source,title,url,author,publish_time,hash,category,excerpt,scraped_at
TechCrunch,"OpenAI announces new GPT-4 features",https://techcrunch.com/...,Sarah Perez,2024-01-15 10:30,abc123,,,2024-01-15 14:25:33
TechCrunch,"Tesla's latest software update includes...",https://techcrunch.com/...,Rebecca Bellan,2024-01-15 09:15,def456,,,2024-01-15 14:25:35
```

### Console Report
```
==================================================
SCRAPING REPORT
==================================================
Total articles scraped: 87
Pages attempted: 5
Errors encountered: 0

Latest article: OpenAI announces new GPT-4 features
Oldest article: Tesla's latest software update includes...

Top authors:
  - Sarah Perez: 12 articles
  - Rebecca Bellan: 8 articles
  - Kyle Wiggers: 7 articles
==================================================
```

## ⚙️ Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--pages` | 5 | Number of pages to scrape |
| `--output` | techcrunch_articles.csv | Output filename |
| `--delay-min` | 1.0 | Minimum delay between requests (seconds) |
| `--delay-max` | 3.0 | Maximum delay between requests (seconds) |
| `--log-level` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `--log-file` | None | Optional log file path |
| `--no-report` | False | Skip generating detailed report |

## 🛡️ Best Practices & Ethics

This scraper is designed with responsible web scraping principles:

- **Rate Limiting**: Built-in delays to respect server resources
- **User Agent Rotation**: Mimics real browser behavior
- **Error Handling**: Graceful failure handling without overwhelming servers
- **Respectful Scraping**: Follows robots.txt guidelines (manual verification recommended)

## 🔧 Customization & Extension

### Adding New Data Fields

```python
# In parse_article_from_card method
category_tag = card.find('span', class_='category')
category = clean_text(category_tag.text) if category_tag else None

excerpt_tag = card.find('div', class_='excerpt')
excerpt = clean_text(excerpt_tag.text) if excerpt_tag else None
```

### Custom Output Formats

```python
# Add JSON export capability
import json

def save_articles_to_json(articles, filename):
    data = [article.__dict__ for article in articles]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

## 📈 Performance Metrics

- **Speed**: ~2-3 seconds per page (including delays)
- **Efficiency**: 10 concurrent connections max
- **Memory Usage**: Minimal, processes data in streams
- **Error Rate**: <1% under normal conditions

## 🐛 Troubleshooting

### Common Issues

1. **Connection Timeout**
   ```bash
   # Increase timeout in TechCrunchScraper.__aenter__()
   timeout=aiohttp.ClientTimeout(total=60)
   ```

2. **Rate Limited**
   ```bash
   # Increase delays
   python scraper.py --delay-min 3 --delay-max 8
   ```

3. **Empty Results**
   - Check if TechCrunch has changed their HTML structure
   - Verify internet connection
   - Check if site is accessible

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Contact & Support

- **Author**: [Your Name]
- **Email**: [your.email@example.com]
- **GitHub**: [https://github.com/yourusername]
- **LinkedIn**: [https://linkedin.com/in/yourusername]

## 🏆 Portfolio Highlights

This project demonstrates proficiency in:

- **Python Development**: Advanced Python programming with modern best practices
- **Asynchronous Programming**: Expert use of asyncio and aiohttp
- **Web Scraping**: Professional-grade scraping techniques with anti-detection measures
- **Data Processing**: Clean data extraction, validation, and export
- **Error Handling**: Robust error management and reporting
- **CLI Development**: User-friendly command-line interface
- **Code Documentation**: Comprehensive documentation and code comments
- **Software Architecture**: Clean, maintainable, and extensible code structure

---

*Built with ❤️ for the web scraping community*