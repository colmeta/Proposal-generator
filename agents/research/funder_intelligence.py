"""
Funder Intelligence Agent
Researches ANY funding organization dynamically (not just hardcoded ones)
"""

import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
from services.web_scraper import web_scraper


class FunderIntelligenceAgent(BaseAgent):
    """
    Funder Intelligence Agent - Researches ANY funder dynamically
    """
    
    def __init__(self):
        super().__init__(
            name="Funder Intelligence Agent",
            role="Research funding organizations and extract requirements",
            task_type="research"
        )
        self.funder_db_path = Path("data/funder_database.json")
        self._load_funder_database()
    
    def _load_funder_database(self):
        """Load seed funder database"""
        self.funder_database = {}
        if self.funder_db_path.exists():
            try:
                with open(self.funder_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for funder in data.get("funders", []):
                        self.funder_database[funder["name"].lower()] = funder
                self.logger.info(f"Loaded {len(self.funder_database)} funders from database")
            except Exception as e:
                self.logger.warning(f"Failed to load funder database: {e}")
                self.funder_database = {}
    
    def research_funder(
        self,
        funder_name: str,
        website: Optional[str] = None,
        deep_research: bool = True
    ) -> Dict[str, Any]:
        """
        Research a funding organization
        
        Args:
            funder_name: Name of the funding organization
            website: Optional website URL (will be searched if not provided)
            deep_research: Whether to do deep research (scraping, etc.)
        
        Returns:
            Dict with funder information, requirements, deadlines, etc.
        """
        self.log_action(f"Researching funder: {funder_name}")
        
        # Check if we have cached data
        funder_key = funder_name.lower()
        if funder_key in self.funder_database and not deep_research:
            self.logger.info(f"Using cached data for {funder_name}")
            return self.funder_database[funder_key]
        
        # Initialize result structure
        result = {
            "name": funder_name,
            "website": website,
            "requirements": {},
            "deadlines": {},
            "focus_areas": [],
            "key_decision_makers": [],
            "mission": None,
            "values": [],
            "priorities": [],
            "application_process": {},
            "funding_amounts": {},
            "eligibility_criteria": [],
            "research_method": "cached" if funder_key in self.funder_database else "new"
        }
        
        # If we have cached data, start with it
        if funder_key in self.funder_database:
            cached = self.funder_database[funder_key]
            result.update(cached)
            result["research_method"] = "cached_enhanced"
        
        # Find website if not provided
        if not result.get("website") and deep_research:
            result["website"] = self._find_funder_website(funder_name)
        
        # Deep research if requested
        if deep_research and result.get("website"):
            web_data = self._scrape_funder_website(result["website"])
            result.update(web_data)
        
        # Use LLM to extract and structure information
        if deep_research:
            structured_data = self._extract_structured_info(result)
            result.update(structured_data)
        
        # Store in database
        self.funder_database[funder_key] = result
        self._save_funder_database()
        
        self.log_action(f"Completed research for {funder_name}", {
            "website": result.get("website"),
            "focus_areas": len(result.get("focus_areas", []))
        })
        
        return result
    
    def _find_funder_website(self, funder_name: str) -> Optional[str]:
        """Find funder website using search"""
        prompt = f"""Find the official website URL for the funding organization: {funder_name}

Return ONLY the URL, nothing else. If you cannot find it, return "NOT_FOUND".
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.GEMINI,
                temperature=0.3,
                max_tokens=200
            )
            
            # Extract URL from response
            url_match = re.search(r'https?://[^\s<>"{}|\\^`\[\]]+', response)
            if url_match:
                return url_match.group(0)
            
            # Try to find in response text
            if "NOT_FOUND" not in response.upper():
                # Sometimes LLM returns just the domain
                if "." in response.strip():
                    potential_url = response.strip()
                    if not potential_url.startswith("http"):
                        potential_url = f"https://{potential_url}"
                    return potential_url
        
        except Exception as e:
            self.logger.warning(f"Failed to find website for {funder_name}: {e}")
        
        return None
    
    def _scrape_funder_website(self, website: str) -> Dict[str, Any]:
        """Scrape funder website for information"""
        self.logger.info(f"Scraping website: {website}")
        
        scraped_data = {
            "website": website,
            "scraped_content": {}
        }
        
        try:
            # Scrape main page
            main_page = web_scraper.scrape(
                website,
                extract_text=True,
                extract_links=True
            )
            
            if "error" not in main_page:
                scraped_data["scraped_content"]["main_page"] = {
                    "title": main_page.get("title"),
                    "text": main_page.get("text", "")[:5000],  # Limit text length
                    "links": main_page.get("links", [])[:50]  # Limit links
                }
            
            # Try to find key pages
            key_pages = ["/funding", "/grants", "/apply", "/requirements", "/about"]
            for page_path in key_pages:
                page_url = f"{website.rstrip('/')}{page_path}"
                try:
                    page_data = web_scraper.scrape(
                        page_url,
                        extract_text=True,
                        timeout=5
                    )
                    if "error" not in page_data:
                        scraped_data["scraped_content"][page_path] = {
                            "title": page_data.get("title"),
                            "text": page_data.get("text", "")[:3000]
                        }
                except Exception:
                    pass  # Page might not exist
        
        except Exception as e:
            self.logger.error(f"Error scraping {website}: {e}")
            scraped_data["scrape_error"] = str(e)
        
        return scraped_data
    
    def _extract_structured_info(self, funder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to extract structured information from scraped data"""
        scraped_content = funder_data.get("scraped_content", {})
        
        if not scraped_content:
            return {}
        
        # Prepare content for LLM
        content_text = ""
        for page, data in scraped_content.items():
            if isinstance(data, dict) and "text" in data:
                content_text += f"\n\n=== {page} ===\n{data['text'][:2000]}\n"
        
        if not content_text:
            return {}
        
        prompt = f"""Extract structured information about this funding organization from the scraped website content.

Funder Name: {funder_data.get('name')}
Website: {funder_data.get('website')}

Scraped Content:
{content_text[:8000]}

Extract and return a JSON object with the following structure:
{{
    "focus_areas": ["area1", "area2", ...],
    "mission": "mission statement",
    "values": ["value1", "value2", ...],
    "priorities": ["priority1", "priority2", ...],
    "requirements": {{
        "application_format": "description",
        "required_documents": ["doc1", "doc2", ...],
        "eligibility": ["requirement1", "requirement2", ...]
    }},
    "deadlines": {{
        "next_deadline": "date or description",
        "frequency": "annual/quarterly/etc",
        "notes": "deadline information"
    }},
    "funding_amounts": {{
        "typical_range": "range description",
        "maximum": "max amount if mentioned"
    }},
    "key_decision_makers": ["name1", "name2", ...],
    "application_process": {{
        "steps": ["step1", "step2", ...],
        "timeline": "timeline description"
    }}
}}

Return ONLY valid JSON, no other text.
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.GEMINI,
                temperature=0.3,
                max_tokens=3000
            )
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
                return extracted
            else:
                # Try to parse entire response as JSON
                return json.loads(response)
        
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse LLM response as JSON: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error extracting structured info: {e}")
            return {}
    
    def _save_funder_database(self):
        """Save funder database to file"""
        try:
            # Ensure directory exists
            self.funder_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to list format
            funders_list = list(self.funder_database.values())
            
            with open(self.funder_db_path, 'w', encoding='utf-8') as f:
                json.dump({"funders": funders_list}, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            self.logger.error(f"Failed to save funder database: {e}")
    
    def get_funder_info(self, funder_name: str) -> Optional[Dict[str, Any]]:
        """Get cached funder information"""
        return self.funder_database.get(funder_name.lower())
    
    def list_known_funders(self) -> List[str]:
        """List all known funders"""
        return [funder["name"] for funder in self.funder_database.values()]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input - research funder"""
        funder_name = input_data.get("funder_name")
        if not funder_name:
            raise ValueError("funder_name is required")
        
        website = input_data.get("website")
        deep_research = input_data.get("deep_research", True)
        
        result = self.research_funder(
            funder_name=funder_name,
            website=website,
            deep_research=deep_research
        )
        
        return {
            "status": "success",
            "funder_info": result,
            "research_complete": True
        }

