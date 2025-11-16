"""Research agents package"""

# Agent 3 agents (if they exist)
try:
    from agents.research.funder_intelligence import FunderIntelligenceAgent
    from agents.research.success_analyzer import SuccessAnalyzerAgent
    _AGENT_3_AVAILABLE = True
except ImportError:
    _AGENT_3_AVAILABLE = False

# Agent 4 agents
from agents.research.competitive_intelligence import CompetitiveIntelligenceAgent
from agents.research.field_research import FieldResearchAgent

__all__ = [
    "CompetitiveIntelligenceAgent",
    "FieldResearchAgent",
]

# Add Agent 3 agents if available
if _AGENT_3_AVAILABLE:
    __all__.extend([
        "FunderIntelligenceAgent",
        "SuccessAnalyzerAgent",
    ])
