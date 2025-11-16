"""
Field Research Agent
Performs primary data gathering, industry statistics collection, and market research
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json
import logging

logger = logging.getLogger(__name__)


class FieldResearchAgent(BaseAgent):
    """
    Field Research Agent
    Gathers primary data, collects industry statistics, performs market research, and validates data
    """
    
    def __init__(self, knowledge_base=None):
        """
        Initialize Field Research Agent
        
        Args:
            knowledge_base: Optional knowledge base service for storing and retrieving research data
        """
        super().__init__(
            name="Field Research Agent",
            role="Primary research and data gathering specialist",
            task_type="research"
        )
        self.knowledge_base = knowledge_base
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process field research request
        
        Args:
            input_data: Should contain:
                - project_name: Name of the project
                - research_questions: List of research questions to answer
                - industry: Industry sector
                - geographic_scope: Geographic scope of research
                - data_types: Types of data needed (statistics, trends, benchmarks, etc.)
        
        Returns:
            Field research results including:
                - primary_data: Primary data gathered
                - industry_statistics: Industry statistics collected
                - market_research: Market research findings
                - data_sources: Sources of data
                - validation_status: Data validation results
                - evidence: Supporting evidence gathered
        """
        self.log_action("Starting field research", input_data)
        
        # Validate input
        required_fields = ["project_name"]
        self.validate_input(input_data, required_fields)
        
        project_name = input_data.get("project_name")
        research_questions = input_data.get("research_questions", [])
        industry = input_data.get("industry", "general")
        geographic_scope = input_data.get("geographic_scope", "global")
        data_types = input_data.get("data_types", ["statistics", "trends", "benchmarks"])
        
        # Gather primary data
        primary_data = self._gather_primary_data(
            project_name, research_questions, industry, geographic_scope
        )
        
        # Collect industry statistics
        industry_statistics = self._collect_industry_statistics(
            industry, geographic_scope, data_types
        )
        
        # Perform market research
        market_research = self._perform_market_research(
            project_name, industry, geographic_scope
        )
        
        # Gather evidence
        evidence = self._gather_evidence(
            project_name, industry, research_questions
        )
        
        # Validate data
        validation_status = self._validate_data(
            primary_data, industry_statistics, market_research, evidence
        )
        
        # Store in knowledge base if available
        if self.knowledge_base:
            try:
                self._store_research_data(
                    project_name, primary_data, industry_statistics, market_research
                )
            except Exception as e:
                self.logger.warning(f"Failed to store research data in knowledge base: {e}")
        
        result = {
            "primary_data": primary_data,
            "industry_statistics": industry_statistics,
            "market_research": market_research,
            "data_sources": self._identify_data_sources(
                primary_data, industry_statistics, market_research
            ),
            "validation_status": validation_status,
            "evidence": evidence,
            "summary": self._generate_research_summary(
                primary_data, industry_statistics, market_research
            )
        }
        
        self.log_action("Field research completed", {
            "data_points": len(primary_data.get("findings", [])),
            "statistics_count": len(industry_statistics.get("statistics", []))
        })
        
        return result
    
    def _gather_primary_data(
        self,
        project_name: str,
        research_questions: List[str],
        industry: str,
        geographic_scope: str
    ) -> Dict[str, Any]:
        """Gather primary data based on research questions"""
        questions_str = "\n".join([
            f"{i+1}. {q}" for i, q in enumerate(research_questions)
        ]) if research_questions else "General research about the project and industry"
        
        prompt = f"""As a field research expert, gather primary data for:

Project: {project_name}
Industry: {industry}
Geographic Scope: {geographic_scope}

Research Questions:
{questions_str}

Gather primary data including:
1. Key findings for each research question
2. Relevant data points and metrics
3. Observations and insights
4. Gaps in current knowledge

Return your response as a JSON object:
{{
  "findings": [
    {{
      "question": "Research question",
      "finding": "Key finding",
      "data_points": ["data1", "data2"],
      "insights": ["insight1", "insight2"],
      "confidence": "high|medium|low"
    }}
  ],
  "key_metrics": {{
    "metric_name": "value or description"
  }},
  "knowledge_gaps": ["gap1", "gap2"]
}}

Only return the JSON object, no additional text."""
        
        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=3000
            )
            
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"Error gathering primary data: {e}")
        
        return {
            "findings": [],
            "key_metrics": {},
            "knowledge_gaps": []
        }
    
    def _collect_industry_statistics(
        self,
        industry: str,
        geographic_scope: str,
        data_types: List[str]
    ) -> Dict[str, Any]:
        """Collect industry statistics"""
        data_types_str = ", ".join(data_types)
        
        prompt = f"""As an industry research expert, collect relevant industry statistics for:

Industry: {industry}
Geographic Scope: {geographic_scope}
Data Types Needed: {data_types_str}

Collect statistics including:
1. Market size and growth rates
2. Industry trends and patterns
3. Benchmark data
4. Key performance indicators
5. Demographic data (if relevant)
6. Economic indicators

For each statistic, provide:
- Statistic name
- Value or range
- Source type (if known)
- Year/period
- Relevance

Return your response as a JSON object:
{{
  "statistics": [
    {{
      "name": "Statistic name",
      "value": "Value or description",
      "source_type": "academic|industry|government|other",
      "period": "Year or period",
      "relevance": "Why this statistic matters"
    }}
  ],
  "trends": [
    {{
      "trend": "Trend description",
      "direction": "increasing|decreasing|stable",
      "impact": "Impact description"
    }}
  ],
  "benchmarks": {{
    "benchmark_name": "value or description"
  }}
}}

Only return the JSON object, no additional text."""
        
        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=3000
            )
            
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"Error collecting industry statistics: {e}")
        
        return {
            "statistics": [],
            "trends": [],
            "benchmarks": {}
        }
    
    def _perform_market_research(
        self,
        project_name: str,
        industry: str,
        geographic_scope: str
    ) -> Dict[str, Any]:
        """Perform market research"""
        prompt = f"""As a market research expert, perform market research for:

Project: {project_name}
Industry: {industry}
Geographic Scope: {geographic_scope}

Conduct market research covering:
1. Market size and segmentation
2. Target audience characteristics
3. Market dynamics and drivers
4. Competitive landscape overview
5. Market opportunities and challenges
6. Regulatory environment (if relevant)

Return your response as a JSON object:
{{
  "market_size": {{
    "description": "Market size description",
    "segments": ["segment1", "segment2"]
  }},
  "target_audience": {{
    "characteristics": ["char1", "char2"],
    "needs": ["need1", "need2"],
    "behaviors": ["behavior1", "behavior2"]
  }},
  "market_dynamics": {{
    "drivers": ["driver1", "driver2"],
    "barriers": ["barrier1", "barrier2"],
    "trends": ["trend1", "trend2"]
  }},
  "opportunities": ["opportunity1", "opportunity2"],
  "challenges": ["challenge1", "challenge2"]
}}

Only return the JSON object, no additional text."""
        
        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2500
            )
            
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"Error performing market research: {e}")
        
        return {
            "market_size": {"description": "", "segments": []},
            "target_audience": {"characteristics": [], "needs": [], "behaviors": []},
            "market_dynamics": {"drivers": [], "barriers": [], "trends": []},
            "opportunities": [],
            "challenges": []
        }
    
    def _gather_evidence(
        self,
        project_name: str,
        industry: str,
        research_questions: List[str]
    ) -> List[Dict[str, Any]]:
        """Gather supporting evidence"""
        questions_str = "\n".join([
            f"- {q}" for q in research_questions
        ]) if research_questions else "General project evidence"
        
        prompt = f"""As a research evidence specialist, gather supporting evidence for:

Project: {project_name}
Industry: {industry}

Research Questions:
{questions_str}

Gather evidence including:
1. Case studies or examples
2. Research studies or reports
3. Expert opinions or quotes
4. Data points that support claims
5. Success stories or precedents

For each piece of evidence, provide:
- Evidence type
- Description
- Relevance to research questions
- Strength of evidence

Return your response as a JSON array:
[
  {{
    "type": "case_study|research|expert_opinion|data|success_story",
    "description": "Evidence description",
    "relevance": "Why this evidence matters",
    "strength": "strong|moderate|weak"
  }}
]

Only return the JSON array, no additional text."""
        
        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                evidence = json.loads(json_str)
                return evidence if isinstance(evidence, list) else []
        except Exception as e:
            self.logger.error(f"Error gathering evidence: {e}")
        
        return []
    
    def _validate_data(
        self,
        primary_data: Dict[str, Any],
        industry_statistics: Dict[str, Any],
        market_research: Dict[str, Any],
        evidence: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate gathered data"""
        prompt = f"""As a data validation expert, validate the following research data:

Primary Data:
{json.dumps(primary_data, indent=2)}

Industry Statistics:
{json.dumps(industry_statistics, indent=2)}

Market Research:
{json.dumps(market_research, indent=2)}

Evidence:
{json.dumps(evidence, indent=2)}

Assess:
1. Data quality and reliability
2. Consistency across sources
3. Completeness
4. Potential biases or limitations
5. Confidence levels

Return your response as a JSON object:
{{
  "overall_quality": "high|medium|low",
  "reliability_score": 0.0-1.0,
  "consistency": "consistent|mostly_consistent|inconsistent",
  "completeness": "complete|mostly_complete|incomplete",
  "limitations": ["limitation1", "limitation2"],
  "biases": ["bias1", "bias2"],
  "confidence_level": "high|medium|low",
  "validation_notes": "Additional validation notes"
}}

Only return the JSON object, no additional text."""
        
        try:
            response = self.call_llm(
                prompt=prompt,
                temperature=0.5,
                max_tokens=1500
            )
            
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"Error validating data: {e}")
        
        return {
            "overall_quality": "unknown",
            "reliability_score": 0.5,
            "consistency": "unknown",
            "completeness": "unknown",
            "limitations": [],
            "biases": [],
            "confidence_level": "medium",
            "validation_notes": "Validation failed"
        }
    
    def _identify_data_sources(
        self,
        primary_data: Dict[str, Any],
        industry_statistics: Dict[str, Any],
        market_research: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify data sources used"""
        sources = []
        
        # Extract sources from statistics
        for stat in industry_statistics.get("statistics", []):
            sources.append({
                "type": stat.get("source_type", "unknown"),
                "description": f"Industry statistic: {stat.get('name', '')}",
                "reliability": "high" if stat.get("source_type") in ["academic", "government"] else "medium"
            })
        
        # Add generic source types
        if primary_data.get("findings"):
            sources.append({
                "type": "primary_research",
                "description": "Primary data gathering",
                "reliability": "medium"
            })
        
        if market_research.get("market_size"):
            sources.append({
                "type": "market_research",
                "description": "Market research analysis",
                "reliability": "medium"
            })
        
        return sources
    
    def _store_research_data(
        self,
        project_name: str,
        primary_data: Dict[str, Any],
        industry_statistics: Dict[str, Any],
        market_research: Dict[str, Any]
    ):
        """Store research data in knowledge base"""
        if not self.knowledge_base:
            return
        
        # Store primary data findings
        for finding in primary_data.get("findings", []):
            content = f"Project: {project_name}\nFinding: {finding.get('finding', '')}\nData Points: {', '.join(finding.get('data_points', []))}"
            self.knowledge_base.add_document(
                content=content,
                metadata={
                    "type": "primary_research",
                    "project": project_name,
                    "finding_id": finding.get("question", "unknown")
                }
            )
        
        # Store industry statistics
        for stat in industry_statistics.get("statistics", []):
            content = f"Industry Statistic: {stat.get('name', '')}\nValue: {stat.get('value', '')}\nRelevance: {stat.get('relevance', '')}"
            self.knowledge_base.add_document(
                content=content,
                metadata={
                    "type": "industry_statistic",
                    "statistic_name": stat.get("name", ""),
                    "period": stat.get("period", "")
                }
            )
    
    def _generate_research_summary(
        self,
        primary_data: Dict[str, Any],
        industry_statistics: Dict[str, Any],
        market_research: Dict[str, Any]
    ) -> str:
        """Generate research summary"""
        prompt = f"""Generate a concise executive summary (2-3 paragraphs) of the field research findings:

Primary Data:
{json.dumps(primary_data, indent=2)}

Industry Statistics:
{json.dumps(industry_statistics, indent=2)}

Market Research:
{json.dumps(market_research, indent=2)}

Provide a clear summary highlighting key findings, important statistics, and market insights."""
        
        try:
            return self.call_llm(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500
            )
        except Exception as e:
            self.logger.error(f"Error generating research summary: {e}")
            return "Summary generation failed."

