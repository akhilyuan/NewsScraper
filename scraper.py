import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import random
import time
from utils import clean_text, get_hash
from dataclasses import dataclass, field
from typing import List, Optional
import argparse

BASE_URL = "https://techcrunch.com"

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
]

@dataclass
class Article:
    """Article data structure for storing scraped article information."""
    source: str
    title: str
    url: str
    author: str
    publish_time: str
    hash: str
    category: Optional[str] = None
    excerpt: Optional[str] = None
    scraped_at: str = None
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@dataclass
class TechCrunchScraper:
    """
    Asynchronous scraper for fetching articles from TechCrunch.
    
    Features:
    - Async/await support for better performance
    - Random delays to avoid being blocked
    - User agent rotation
    - Error handling and retry logic
    """
    max_pages: int = 5
    delay_range: tuple = (1, 3)
    session: Optional[aiohttp.ClientSession] = field(default=None, init=False)
    errors: List[str] = field(default_factory=list, init=False)

    async def __aenter__(self):
        """Initialize aiohttp session when entering async context."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),  
            connector=aiohttp.TCPConnector(limit=10)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up aiohttp session when exiting async context."""
        if self.session:
            await self.session.close()

    def get_headers(self) -> dict:
        """Generate HTTP headers with random user agent to mimic browser requests."""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    async def random_delay(self):
        """Add random delay between requests to avoid being rate limited."""
        delay = random.uniform(*self.delay_range)
        await asyncio.sleep(delay)

    async def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch a single page and return parsed BeautifulSoup object.
        
        Args:
            url: The URL to fetch
            
        Returns:
            BeautifulSoup object if successful, None if failed
        """
        headers = self.get_headers()
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    return BeautifulSoup(html, 'html.parser')
                else:
                    error_msg = f"Failed to fetch {url}: HTTP {response.status}"
                    self.errors.append(error_msg)
                    print(f"Error: {error_msg}")
                    return None
        except Exception as e:
            error_msg = f"Exception while fetching {url}: {str(e)}"
            self.errors.append(error_msg)
            print(f"Error: {error_msg}")
            return None

    async def scrape_page(self, page_num: int = 1) -> List[Article]:
        """
        Scrape articles from a single page.
        
        Args:
            page_num: Page number to scrape (1-indexed)
            
        Returns:
            List of Article objects found on the page
        """
        if page_num == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}/page/{page_num}/"
            
        print(f"Scraping page {page_num}: {url}")
        soup = await self.fetch_page(url)
        if not soup:
            return []
            
        # Find article cards on the page
        cards = soup.find_all('div', class_='loop-card__content')
        
        articles = []
        for card in cards:
            article = self.parse_article_from_card(card)
            if article:
                articles.append(article)
        
        print(f"Found {len(articles)} articles on page {page_num}")
        return articles
        
    async def scrape_all_pages(self) -> List[Article]:
        """
        Scrape articles from multiple pages.
        
        Returns:
            List of all Article objects scraped from all pages
        """
        all_articles = []
        # Note: range(1, max_pages+1) to include the last page
        for page_num in range(1, self.max_pages + 1):
            articles = await self.scrape_page(page_num)
            all_articles.extend(articles)

            # If no articles found, likely reached the end
            if not articles:
                print(f"No articles found on page {page_num}, stopping.")
                break
                
            # Add delay between pages (except for the last page)
            if page_num < self.max_pages:
                await self.random_delay()

        return all_articles

    def parse_article_from_card(self, card) -> Optional[Article]:
        """
        Parse article information from a single article card element.
        
        Args:
            card: BeautifulSoup element containing article information
            
        Returns:
            Article object if parsing successful, None otherwise
        """
        # Extract title and URL
        title_tag = card.find('a', class_='loop-card__title-link')
        if not title_tag:
            return None
            
        title = clean_text(title_tag.text)
        if not title:
            return None
            
        # Extract URL
        url = title_tag.get('href', '')
        if url and not url.startswith('http'):
            url = f"{BASE_URL}{url}" if url.startswith('/') else f"{BASE_URL}/{url}"
        
        # Extract author
        author_tag = card.find('a', class_='loop-card__author')
        author = clean_text(author_tag.text) if author_tag else 'Unknown'
        
        # Extract publish time
        time_tag = card.find('time')
        raw_time = time_tag.get('datetime') if time_tag and time_tag.has_attr('datetime') else ''
        try:
            if raw_time:
                # Handle ISO format datetime
                dt_obj = datetime.fromisoformat(raw_time.replace('Z', '+00:00'))
                publish_time = dt_obj.strftime("%Y-%m-%d %H:%M")
            else:
                publish_time = 'Unknown'
        except ValueError:
            # Fallback: use first 19 characters if parsing fails
            publish_time = raw_time[:19] if raw_time else 'Unknown'

        # TODO: Extract category and excerpt in future versions
        # category_tag = card.find('span', class_='category')
        # excerpt_tag = card.find('div', class_='excerpt')

        return Article(
            source='TechCrunch',
            title=title,
            url=url,
            author=author,
            publish_time=publish_time,
            hash=get_hash(title),
            category=None,  # TODO: Implement category extraction
            excerpt=None    # TODO: Implement excerpt extraction
        )

def save_articles_to_csv(articles: List[Article], filename: str):
    """
    Save articles to CSV file.
    
    Args:
        articles: List of Article objects to save
        filename: Output filename
    """
    if not articles:
        print("No articles to save.")
        return
        
    # Convert articles to dictionary format for pandas
    data = []
    for article in articles:
        data.append({
            'source': article.source,
            'title': article.title,
            'url': article.url,
            'author': article.author,
            'publish_time': article.publish_time,
            'hash': article.hash,
            'category': article.category,
            'excerpt': article.excerpt,
            'scraped_at': article.scraped_at
        })
    
    df = pd.DataFrame(data)
    df.to_csv(f'output/{filename}', index=False, encoding='utf-8')
    print(f"Saved {len(articles)} articles to {filename}")

def generate_report(articles: List[Article], scraper: TechCrunchScraper):
    """
    Generate and print scraping report.
    
    Args:
        articles: List of scraped articles
        scraper: Scraper instance with error information
    """
    print("\n" + "="*50)
    print("SCRAPING REPORT")
    print("="*50)
    print(f"Total articles scraped: {len(articles)}")
    print(f"Pages attempted: {scraper.max_pages}")
    print(f"Errors encountered: {len(scraper.errors)}")
    
    if scraper.errors:
        print("\nErrors:")
        for error in scraper.errors:
            print(f"  - {error}")
    
    if articles:
        print(f"\nLatest article: {articles[0].title}")
        print(f"Oldest article: {articles[-1].title}")
        
        # Author statistics
        authors = [article.author for article in articles if article.author != 'Unknown']
        if authors:
            from collections import Counter
            author_counts = Counter(authors)
            print(f"\nTop authors:")
            for author, count in author_counts.most_common(3):
                print(f"  - {author}: {count} articles")
    
    print("="*50)

async def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description='TechCrunch News Scraper')
    parser.add_argument('--pages', '-p', type=int, default=5, 
                       help='Number of pages to scrape (default: 5)')
    parser.add_argument('--output', '-o', type=str, default='techcrunch_articles.csv',
                       help='Output filename (default: techcrunch_articles.csv)')
    parser.add_argument('--log-level', '-l', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    parser.add_argument('--log-file', type=str, default=None,
                       help='Log file path (optional)')
    parser.add_argument('--delay-min', type=float, default=1.0,
                       help='Minimum delay between requests in seconds (default: 1.0)')
    parser.add_argument('--delay-max', type=float, default=3.0,
                       help='Maximum delay between requests in seconds (default: 3.0)')
    parser.add_argument('--no-report', action='store_true',
                       help='Skip generating scraping report')
    args = parser.parse_args()

    # Validate arguments
    if args.pages <= 0:
        print("Error: Number of pages must be greater than 0")
        return
    if args.delay_min < 0 or args.delay_max < args.delay_min:
        print("Error: Invalid delay parameters")
        return
    
    print(f"Starting TechCrunch scraper...")
    print(f"Pages to scrape: {args.pages}")
    print(f"Delay range: {args.delay_min}-{args.delay_max} seconds")
    print(f"Output file: {args.output}")
    
    try:
        async with TechCrunchScraper(
            max_pages=args.pages,
            delay_range=(args.delay_min, args.delay_max)
        ) as scraper:
            articles = await scraper.scrape_all_pages()
            
            if articles:
                save_articles_to_csv(articles, args.output)
                
                if not args.no_report:
                    generate_report(articles, scraper)
            else:
                print("No articles were scraped successfully.")
                
    except Exception as e:
        print(f"Scraping failed with error: {e}")
        return

if __name__ == '__main__':
    asyncio.run(main())