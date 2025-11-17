"""
Website and Social Media Scraper
Extracts content from websites, social media platforms, and links
"""

import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urljoin
import logging

from services.web_scraper import web_scraper
from config.llm_config import llm_config, LLMProvider

logger = logging.getLogger(__name__)


class WebsiteScraper:
    """
    Scraper for websites and social media platforms
    """
    
    def __init__(self):
        """Initialize website scraper"""
        self.social_media_patterns = {
            'linkedin': r'linkedin\.com',
            'twitter': r'(twitter\.com|x\.com)',
            'facebook': r'facebook\.com',
            'instagram': r'instagram\.com',
            'youtube': r'youtube\.com',
            'github': r'github\.com',
        }
        logger.info("WebsiteScraper initialized")
    
    def scrape_url(self, url: str, extract_structured: bool = True) -> Dict[str, Any]:
        """
        Scrape content from a URL (website or social media)
        
        Args:
            url: URL to scrape
            extract_structured: Whether to extract structured information
        
        Returns:
            Dict with scraped content and metadata
        """
        # Detect platform type
        platform = self._detect_platform(url)
        
        # Scrape using web scraper
        scraped_data = web_scraper.scrape(
            url,
            extract_text=True,
            extract_links=True,
            timeout=30
        )
        
        if "error" in scraped_data:
            return {
                "url": url,
                "platform": platform,
                "error": scraped_data["error"],
                "success": False
            }
        
        result = {
            "url": url,
            "platform": platform,
            "title": scraped_data.get("title"),
            "text": scraped_data.get("text", ""),
            "links": scraped_data.get("links", []),
            "success": True
        }
        
        # Extract structured information if requested
        if extract_structured and result["text"]:
            structured = self._extract_structured_info(result["text"], platform, url)
            result["structured_info"] = structured
        
        return result
    
    def _detect_platform(self, url: str) -> str:
        """Detect the platform type from URL"""
        url_lower = url.lower()
        
        for platform, pattern in self.social_media_patterns.items():
            if re.search(pattern, url_lower):
                return platform
        
        return "website"
    
    def _extract_structured_info(
        self,
        text: str,
        platform: str,
        url: str
    ) -> Dict[str, Any]:
        """Extract structured information from scraped content"""
        text_preview = text[:8000] if len(text) > 8000 else text
        
        prompt = f"""Extract structured information from this {platform} page.

URL: {url}
Platform: {platform}

Content:
{text_preview}

Extract and return JSON with:

For LinkedIn profiles/pages:
{{
    "profile_name": "...",
    "headline": "...",
    "about": "...",
    "experience": [...],
    "education": [...],
    "skills": [...],
    "organizations": [...]
}}

For Twitter/X:
{{
    "profile_name": "...",
    "bio": "...",
    "recent_tweets": [...],
    "topics": [...],
    "engagement_metrics": {{}}
}}

For Facebook:
{{
    "page_name": "...",
    "about": "...",
    "posts": [...],
    "contact_info": {{}}
}}

For Instagram:
{{
    "profile_name": "...",
    "bio": "...",
    "posts_count": "...",
    "followers": "...",
    "content_themes": [...]
}}

For GitHub:
{{
    "username": "...",
    "repositories": [...],
    "languages": [...],
    "projects": [...],
    "contributions": "..."
}}

For general websites:
{{
    "organization_name": "...",
    "mission": "...",
    "services": [...],
    "projects": [...],
    "team": [...],
    "contact_info": {{}},
    "key_points": [...]
}}

Return ONLY valid JSON, no other text.
"""
        
        try:
            response = llm_config.call_llm(
                prompt=prompt,
                task_type="research",
                provider=LLMProvider.GEMINI,
                temperature=0.3,
                max_tokens=3000
            )
            
            import json
            import re
            
            json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response["content"])
        
        except Exception as e:
            logger.error(f"Error extracting structured info: {e}")
            return {
                "error": str(e),
                "raw_text": text_preview[:1000]
            }
    
    def scrape_multiple_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs
        
        Args:
            urls: List of URLs to scrape
        
        Returns:
            List of scraped data
        """
        results = []
        for url in urls:
            try:
                result = self.scrape_url(url)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                results.append({
                    "url": url,
                    "error": str(e),
                    "success": False
                })
        return results


# Global instance
website_scraper = WebsiteScraper()

