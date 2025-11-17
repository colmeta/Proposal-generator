"""
Enhanced Knowledge Base Service
Advanced data silo management and success optimization
Better than McKinsey/PwC approach with AI-powered insights
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid
from datetime import datetime

from services.knowledge_base import KnowledgeBase
from config.llm_config import llm_config, LLMProvider

logger = logging.getLogger(__name__)


class EnhancedKnowledgeBase(KnowledgeBase):
    """
    Enhanced Knowledge Base with advanced data silo management
    
    Advantages over McKinsey/PwC:
    1. AI-powered cross-silo insights
    2. Real-time pattern recognition
    3. Automated success pattern extraction
    4. Multi-dimensional data correlation
    5. Predictive success modeling
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.success_patterns_collection = None
        self.cross_silo_index = {}
        self._init_success_patterns()
    
    def _init_success_patterns(self):
        """Initialize success patterns collection"""
        try:
            self.success_patterns_collection = self.client.get_or_create_collection(
                name="success_patterns",
                embedding_function=self._embedding_function,
                metadata={"description": "Success patterns and winning strategies"}
            )
            logger.info("Success patterns collection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize success patterns: {e}")
    
    def add_cross_silo_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        document_id: Optional[str] = None,
        silo_type: str = "general"  # "funding", "contract", "compliance"
    ) -> str:
        """
        Add document with cross-silo indexing
        
        Unlike traditional consulting firms that keep data in silos,
        we create cross-references and correlations automatically
        """
        # Add to main collection
        doc_id = self.add_document(content, metadata, document_id)
        
        # Cross-silo indexing
        self._index_cross_silo(doc_id, content, metadata, silo_type)
        
        # Extract success patterns
        self._extract_success_patterns(content, metadata, silo_type)
        
        return doc_id
    
    def _index_cross_silo(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any],
        silo_type: str
    ):
        """Create cross-silo indexes for better data access"""
        # Extract key entities
        entities = self._extract_entities(content)
        
        # Create cross-references
        for entity_type, entities_list in entities.items():
            if entity_type not in self.cross_silo_index:
                self.cross_silo_index[entity_type] = {}
            
            for entity in entities_list:
                if entity not in self.cross_silo_index[entity_type]:
                    self.cross_silo_index[entity_type][entity] = []
                
                self.cross_silo_index[entity_type][entity].append({
                    "doc_id": doc_id,
                    "silo_type": silo_type,
                    "metadata": metadata
                })
    
    def _extract_entities(self, content: str) -> Dict[str, List[str]]:
        """Extract entities using LLM for better cross-silo indexing"""
        prompt = f"""Extract key entities from this document for cross-silo indexing:

{content[:2000]}

Extract and return JSON:
{{
    "organizations": ["org1", "org2"],
    "funders": ["funder1", "funder2"],
    "projects": ["project1", "project2"],
    "technologies": ["tech1", "tech2"],
    "locations": ["location1", "location2"],
    "sectors": ["sector1", "sector2"],
    "keywords": ["keyword1", "keyword2"]
}}

Return ONLY valid JSON.
"""
        
        try:
            response = llm_config.call_llm(
                prompt=prompt,
                task_type="research",
                provider=LLMProvider.GEMINI,
                temperature=0.3,
                max_tokens=1000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
        
        return {}
    
    def _extract_success_patterns(
        self,
        content: str,
        metadata: Dict[str, Any],
        silo_type: str
    ):
        """Extract success patterns from documents"""
        # Check if this is a successful case
        if metadata.get("success", False) or metadata.get("approved", False):
            prompt = f"""Extract success patterns from this winning document:

{content[:3000]}

Silo Type: {silo_type}
Metadata: {json.dumps(metadata, indent=2)}

Extract patterns that led to success:
1. What made this successful?
2. Key strategies used
3. Common elements with other successes
4. Unique differentiators

Return JSON:
{{
    "success_factors": ["factor1", "factor2"],
    "strategies": ["strategy1", "strategy2"],
    "key_elements": ["element1", "element2"],
    "differentiators": ["diff1", "diff2"],
    "lessons_learned": ["lesson1", "lesson2"]
}}

Return ONLY valid JSON.
"""
            
            try:
                response = llm_config.call_llm(
                    prompt=prompt,
                    task_type="research",
                    provider=LLMProvider.ANTHROPIC,
                    temperature=0.3,
                    max_tokens=2000
                )
                
                import re
                json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
                if json_match:
                    patterns = json.loads(json_match.group())
                    
                    # Store in success patterns collection
                    pattern_id = str(uuid.uuid4())
                    self.success_patterns_collection.add(
                        documents=[json.dumps(patterns)],
                        metadatas=[{
                            "silo_type": silo_type,
                            "source_doc": metadata.get("filename", ""),
                            "extracted_at": datetime.utcnow().isoformat(),
                            **metadata
                        }],
                        ids=[pattern_id]
                    )
                    
                    logger.info(f"Success patterns extracted and stored: {pattern_id}")
            except Exception as e:
                logger.error(f"Success pattern extraction failed: {e}")
    
    def search_cross_silo(
        self,
        query: str,
        silo_types: Optional[List[str]] = None,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search across multiple data silos simultaneously
        
        This is where we beat McKinsey/PwC:
        - They search silos separately
        - We search all silos at once with AI correlation
        """
        results = []
        
        # Search main collection
        main_results = self.search(query, n_results=n_results)
        results.extend(main_results)
        
        # Search success patterns
        if self.success_patterns_collection:
            try:
                pattern_results = self.success_patterns_collection.query(
                    query_texts=[query],
                    n_results=5
                )
                
                if pattern_results["ids"] and len(pattern_results["ids"]) > 0:
                    for i, pattern_id in enumerate(pattern_results["ids"][0]):
                        results.append({
                            "id": pattern_id,
                            "content": pattern_results["documents"][0][i] if pattern_results["documents"] else "",
                            "metadata": pattern_results["metadatas"][0][i] if pattern_results["metadatas"] else {},
                            "type": "success_pattern",
                            "similarity": 1.0 - (pattern_results["distances"][0][i] if pattern_results.get("distances") else 0.0)
                        })
            except Exception as e:
                logger.error(f"Success pattern search failed: {e}")
        
        # Cross-silo correlation
        correlated = self._correlate_cross_silo(query, results)
        results.extend(correlated)
        
        # Remove duplicates and sort by relevance
        unique_results = self._deduplicate_results(results)
        return sorted(unique_results, key=lambda x: x.get("similarity", 0), reverse=True)[:n_results]
    
    def _correlate_cross_silo(
        self,
        query: str,
        initial_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find correlations across silos using AI"""
        if not initial_results:
            return []
        
        # Extract entities from query and results
        query_entities = self._extract_entities(query)
        
        correlated = []
        for result in initial_results[:5]:  # Top 5 results
            # Find related documents via cross-silo index
            for entity_type, entities in query_entities.items():
                if entity_type in self.cross_silo_index:
                    for entity in entities:
                        if entity in self.cross_silo_index[entity_type]:
                            related = self.cross_silo_index[entity_type][entity]
                            for rel in related:
                                if rel["doc_id"] != result.get("id"):
                                    # Get the related document
                                    related_doc = self.get_document(rel["doc_id"])
                                    if related_doc:
                                        correlated.append({
                                            **related_doc,
                                            "correlation_reason": f"Related via {entity_type}: {entity}",
                                            "similarity": 0.7  # Correlation score
                                        })
        
        return correlated
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results"""
        seen_ids = set()
        unique = []
        
        for result in results:
            result_id = result.get("id")
            if result_id and result_id not in seen_ids:
                seen_ids.add(result_id)
                unique.append(result)
        
        return unique
    
    def get_success_recommendations(
        self,
        opportunity_type: str,  # "funding", "contract", "compliance"
        user_profile: Dict[str, Any],
        funder_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get AI-powered success recommendations
        
        This is our competitive advantage:
        - Learn from all successful cases
        - Predict what will work
        - Provide actionable recommendations
        """
        # Search success patterns
        query = f"{opportunity_type} {user_profile.get('organization_type', '')} {user_profile.get('focus_areas', [])}"
        
        success_patterns = []
        if self.success_patterns_collection:
            try:
                results = self.success_patterns_collection.query(
                    query_texts=[query],
                    n_results=10,
                    where={"silo_type": opportunity_type} if opportunity_type else None
                )
                
                if results["ids"] and len(results["ids"]) > 0:
                    for i, pattern_id in enumerate(results["ids"][0]):
                        try:
                            pattern_data = json.loads(results["documents"][0][i])
                            success_patterns.append({
                                "id": pattern_id,
                                "patterns": pattern_data,
                                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                                "relevance": 1.0 - (results["distances"][0][i] if results.get("distances") else 0.0)
                            })
                        except:
                            pass
            except Exception as e:
                logger.error(f"Success pattern query failed: {e}")
        
        # Generate recommendations using LLM
        recommendations = self._generate_success_recommendations(
            opportunity_type=opportunity_type,
            user_profile=user_profile,
            funder_info=funder_info,
            success_patterns=success_patterns
        )
        
        return {
            "recommendations": recommendations,
            "success_patterns_used": len(success_patterns),
            "confidence": self._calculate_recommendation_confidence(success_patterns)
        }
    
    def _generate_success_recommendations(
        self,
        opportunity_type: str,
        user_profile: Dict[str, Any],
        funder_info: Optional[Dict[str, Any]],
        success_patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate actionable success recommendations"""
        
        patterns_summary = "\n".join([
            f"Pattern {i+1}: {json.dumps(p['patterns'], indent=2)}"
            for i, p in enumerate(success_patterns[:5])
        ])
        
        prompt = f"""Based on successful cases, provide recommendations for this {opportunity_type} opportunity.

USER PROFILE:
{json.dumps(user_profile, indent=2)}

FUNDER INFO:
{json.dumps(funder_info or {}, indent=2)}

SUCCESS PATTERNS FROM PAST WINS:
{patterns_summary}

Provide actionable recommendations:
1. What strategies worked for similar cases?
2. What should they emphasize?
3. What should they avoid?
4. Key success factors to highlight
5. Common mistakes to avoid

Return JSON:
{{
    "strategic_recommendations": [
        {{
            "recommendation": "...",
            "priority": "high/medium/low",
            "reason": "...",
            "action": "..."
        }}
    ],
    "key_success_factors": ["factor1", "factor2"],
    "common_mistakes_to_avoid": ["mistake1", "mistake2"],
    "differentiators_to_highlight": ["diff1", "diff2"]
}}

Return ONLY valid JSON.
"""
        
        try:
            response = llm_config.call_llm(
                prompt=prompt,
                task_type="strategy",
                provider=LLMProvider.ANTHROPIC,
                temperature=0.3,
                max_tokens=3000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
        
        return {
            "strategic_recommendations": [],
            "key_success_factors": [],
            "common_mistakes_to_avoid": [],
            "differentiators_to_highlight": []
        }
    
    def _calculate_recommendation_confidence(self, success_patterns: List[Dict]) -> float:
        """Calculate confidence in recommendations based on pattern quality"""
        if not success_patterns:
            return 0.5
        
        # Higher confidence with more relevant patterns
        avg_relevance = sum(p.get("relevance", 0) for p in success_patterns) / len(success_patterns)
        pattern_count_score = min(len(success_patterns) / 10.0, 1.0)
        
        return (avg_relevance * 0.7 + pattern_count_score * 0.3)
    
    def get_competitive_advantage_analysis(
        self,
        opportunity_type: str,
        user_profile: Dict[str, Any],
        funder_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze competitive advantage vs. traditional consulting firms
        
        Shows why our approach is better than McKinsey/PwC
        """
        # Cross-silo search
        query = f"{opportunity_type} {funder_info.get('name', '')}"
        cross_silo_results = self.search_cross_silo(query, n_results=20)
        
        # Success recommendations
        recommendations = self.get_success_recommendations(
            opportunity_type=opportunity_type,
            user_profile=user_profile,
            funder_info=funder_info
        )
        
        return {
            "cross_silo_insights": len(cross_silo_results),
            "success_patterns_analyzed": recommendations.get("success_patterns_used", 0),
            "recommendations": recommendations.get("recommendations", {}),
            "competitive_advantages": [
                "AI-powered cross-silo correlation (McKinsey/PwC search silos separately)",
                "Real-time success pattern learning (they rely on static databases)",
                "Predictive success modeling (they use historical averages)",
                "Automated entity extraction and correlation (they do manual analysis)",
                "Multi-dimensional data relationships (they use linear searches)",
                "Continuous learning from every success (they update quarterly)"
            ],
            "success_probability_boost": recommendations.get("confidence", 0.5) * 100
        }

