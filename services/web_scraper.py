"""
Web Scraping Service
Handles web scraping with rate limiting, error handling, and caching
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
import time
import logging
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
import json
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class WebScraper:
    """
    Web scraping service with rate limiting, robots.txt respect, and caching
    """
    
    def __init__(self, cache_dir: Optional[Path] = None, delay: float = 1.0):
        """
        Initialize web scraper
        
        Args:
            cache_dir: Directory to cache scraped content (optional)
            delay: Delay between requests in seconds (default: 1.0)
        """
        self.delay = delay
        self.last_request_time = {}
        self.cache_dir = cache_dir
        self.robots_parsers = {}  # Cache robots.txt parsers
        
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # User agent to identify ourselves
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def _get_cache_path(self, url: str) -> Optional[Path]:
        """Get cache file path for URL"""
        if not self.cache_dir:
            return None
        
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.json"
    
    def _load_from_cache(self, url: str) -> Optional[Dict[str, Any]]:
        """Load scraped content from cache"""
        cache_path = self._get_cache_path(url)
        if cache_path and cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache for {url}: {e}")
        return None
    
    def _save_to_cache(self, url: str, data: Dict[str, Any]):
        """Save scraped content to cache"""
        cache_path = self._get_cache_path(url)
        if cache_path:
            try:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"Failed to save cache for {url}: {e}")
    
    def _get_robots_parser(self, url: str) -> Optional[RobotFileParser]:
        """Get or create robots.txt parser for domain"""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        if domain not in self.robots_parsers:
            robots_url = urljoin(domain, '/robots.txt')
            rp = RobotFileParser()
            try:
                rp.set_url(robots_url)
                rp.read()
                self.robots_parsers[domain] = rp
            except Exception as e:
                logger.debug(f"Could not read robots.txt for {domain}: {e}")
                self.robots_parsers[domain] = None
        
        return self.robots_parsers.get(domain)
    
    def _can_fetch(self, url: str) -> bool:
        """Check if we can fetch URL according to robots.txt"""
        rp = self._get_robots_parser(url)
        if rp is None:
            return True  # If we can't read robots.txt, allow by default
        return rp.can_fetch(self.headers["User-Agent"], url)
    
    def _rate_limit(self, url: str):
        """Enforce rate limiting"""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < self.delay:
                sleep_time = self.delay - elapsed
                time.sleep(sleep_time)
        
        self.last_request_time[domain] = time.time()
    
    def scrape(
        self,
        url: str,
        use_cache: bool = True,
        timeout: int = 10,
        extract_text: bool = True,
        extract_links: bool = False
    ) -> Dict[str, Any]:
        """
        Scrape a URL and return structured content
        
        Args:
            url: URL to scrape
            use_cache: Whether to use cached content if available
            timeout: Request timeout in seconds
            extract_text: Whether to extract text content
            extract_links: Whether to extract links
        
        Returns:
            Dict with 'url', 'title', 'text', 'links', 'html', 'status_code'
        """
        # Check cache first
        if use_cache:
            cached = self._load_from_cache(url)
            if cached:
                logger.debug(f"Using cached content for {url}")
                return cached
        
        # Check robots.txt
        if not self._can_fetch(url):
            logger.warning(f"robots.txt disallows fetching {url}")
            return {
                "url": url,
                "error": "robots.txt disallows fetching",
                "status_code": 403
            }
        
        # Rate limiting
        self._rate_limit(url)
        
        # Make request
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) or 500
            }
        
        # Parse HTML
        try:
            soup = BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            logger.warning(f"Failed to parse HTML for {url}, trying html5lib: {e}")
            try:
                soup = BeautifulSoup(response.content, 'html5lib')
            except Exception as e2:
                logger.error(f"Failed to parse HTML for {url}: {e2}")
                return {
                    "url": url,
                    "error": f"HTML parsing failed: {e2}",
                    "status_code": response.status_code
                }
        
        # Extract content
        result = {
            "url": url,
            "status_code": response.status_code,
            "title": soup.title.string if soup.title else None,
            "html": str(soup) if not extract_text else None
        }
        
        if extract_text:
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            result["text"] = text
        
        if extract_links:
            links = []
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                links.append({
                    "text": link.get_text(strip=True),
                    "url": absolute_url
                })
            result["links"] = links
        
        # Save to cache
        if use_cache:
            self._save_to_cache(url, result)
        
        return result
    
    def scrape_multiple(
        self,
        urls: List[str],
        max_concurrent: int = 1,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs (sequentially for now, respects rate limits)
        
        Args:
            urls: List of URLs to scrape
            max_concurrent: Maximum concurrent requests (currently not used, sequential)
            **kwargs: Additional arguments passed to scrape()
        
        Returns:
            List of scrape results
        """
        results = []
        for url in urls:
            result = self.scrape(url, **kwargs)
            results.append(result)
        return results
    
    def extract_specific_content(
        self,
        url: str,
        selectors: Dict[str, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract specific content using CSS selectors
        
        Args:
            url: URL to scrape
            selectors: Dict mapping field names to CSS selectors
            **kwargs: Additional arguments passed to scrape()
        
        Returns:
            Dict with extracted content
        """
        result = self.scrape(url, extract_text=False, **kwargs)
        
        if "error" in result:
            return result
        
        try:
            soup = BeautifulSoup(result.get("html", ""), 'lxml')
        except Exception as e:
            return {
                "url": url,
                "error": f"Failed to parse HTML: {e}"
            }
        
        extracted = {"url": url}
        for field, selector in selectors.items():
            elements = soup.select(selector)
            if elements:
                if len(elements) == 1:
                    extracted[field] = elements[0].get_text(strip=True)
                else:
                    extracted[field] = [elem.get_text(strip=True) for elem in elements]
            else:
                extracted[field] = None
        
        return extracted


# Global instance
_cache_dir = Path("data/cache")
if _cache_dir.parent.exists():
    _cache_dir.mkdir(parents=True, exist_ok=True)
    web_scraper = WebScraper(cache_dir=_cache_dir)
else:
    web_scraper = WebScraper(cache_dir=None)

