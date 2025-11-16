# Research Agents - Usage Guide

## Funder Intelligence Agent

Researches ANY funding organization dynamically (not just hardcoded ones).

### Basic Usage

```python
from agents.research.funder_intelligence import FunderIntelligenceAgent

# Initialize agent
agent = FunderIntelligenceAgent()

# Research a funder
result = agent.research_funder(
    funder_name="National Science Foundation",
    website="https://www.nsf.gov",  # Optional, will be searched if not provided
    deep_research=True  # Set to False to use cached data only
)

print(result)
# Returns: {
#     "name": "National Science Foundation",
#     "website": "https://www.nsf.gov",
#     "requirements": {...},
#     "deadlines": {...},
#     "focus_areas": [...],
#     ...
# }

# Get cached funder info
info = agent.get_funder_info("National Science Foundation")

# List all known funders
funders = agent.list_known_funders()
```

### Using the Process Method

```python
result = agent.process({
    "funder_name": "Bill & Melinda Gates Foundation",
    "website": "https://www.gatesfoundation.org",  # Optional
    "deep_research": True
})
```

## Success Analyzer Agent

Studies winning proposals and extracts success patterns.

### Basic Usage

```python
from agents.research.success_analyzer import SuccessAnalyzerAgent

# Initialize agent
agent = SuccessAnalyzerAgent()

# Analyze a winning proposal
result = agent.analyze_winning_proposal(
    proposal_content="... proposal text ...",
    funder_name="National Science Foundation",
    source="Public database"
)

print(result)
# Returns: {
#     "analysis": {...},
#     "patterns": {...},
#     "funder": "National Science Foundation",
#     ...
# }

# Get success patterns and recommendations
patterns = agent.get_success_patterns()
recommendations = agent.get_recommendations(funder_name="NSF")

# Research public winners
research_result = agent.research_public_winners(
    funder_name="National Science Foundation",
    search_terms=["NSF grant winners", "NSF funded projects"]
)
```

### Using the Process Method

```python
# Analyze a proposal
result = agent.process({
    "proposal_content": "... proposal text ...",
    "funder_name": "NSF",
    "source": "Public database"
})

# Research public winners
result = agent.process({
    "funder_name": "National Science Foundation",
    "search_terms": ["NSF winners"]
})

# Get patterns
result = agent.process({
    "get_patterns": True,
    "funder_name": "NSF"  # Optional
})
```

## Web Scraper Service

The web scraper service is used internally but can also be used directly:

```python
from services.web_scraper import web_scraper

# Scrape a URL
result = web_scraper.scrape(
    url="https://www.nsf.gov",
    extract_text=True,
    extract_links=True
)

# Extract specific content using CSS selectors
result = web_scraper.extract_specific_content(
    url="https://www.nsf.gov/funding",
    selectors={
        "title": "h1",
        "deadlines": ".deadline-list",
        "requirements": ".requirements"
    }
)
```

## Features

### Funder Intelligence Agent
- ✅ Research ANY funder (not just hardcoded)
- ✅ Automatic website discovery
- ✅ Web scraping with rate limiting
- ✅ Structured data extraction using LLM
- ✅ Caching for performance
- ✅ Seed database with major funders

### Success Analyzer Agent
- ✅ Analyze winning proposals
- ✅ Extract success patterns
- ✅ Build pattern database
- ✅ Generate actionable recommendations
- ✅ Research public winners
- ✅ Learn from multiple sources

### Web Scraper
- ✅ Respects robots.txt
- ✅ Rate limiting
- ✅ Caching
- ✅ Error handling
- ✅ CSS selector extraction
- ✅ Multiple parser support (lxml, html5lib)

## Integration

These agents integrate with:
- **BaseAgent** - Inherits common functionality
- **LLM Config** - Uses multi-LLM support
- **Knowledge Base** (Agent 4) - Stores research results
- **Other agents** - Provides funder intelligence and success patterns

