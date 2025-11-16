"""
Business Architect Agent
Financial structures design, revenue models development, business model design, monetization strategies
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json


class BusinessArchitectAgent(BaseAgent):
    """
    Business Architect Agent
    Designs financial structures, revenue models, business models, and monetization strategies
    """
    
    def __init__(self):
        super().__init__(
            name="Business Architect",
            role="Design financial structures and business models",
            task_type="strategy"
        )
    
    def design_financial_structure(
        self,
        project_requirements: Dict[str, Any],
        budget_constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Design financial structure for project
        
        Args:
            project_requirements: Project requirements and scope
            budget_constraints: Budget limits and constraints
        
        Returns:
            Financial structure with cost breakdown, funding sources, and financial plan
        """
        self.log_action("Designing financial structure")
        
        prompt = f"""As a Business Architect, design a comprehensive financial structure.

Project Requirements:
{json.dumps(project_requirements, indent=2)}

Budget Constraints:
{json.dumps(budget_constraints, indent=2)}

Design a financial structure that includes:
1. Cost breakdown by category (personnel, operations, capital, etc.)
2. Funding sources and allocation
3. Financial timeline and cash flow
4. Contingency planning
5. Financial controls and monitoring

Return JSON:
{{
    "cost_breakdown": {{
        "personnel": {{"amount": 0, "description": "description"}},
        "operations": {{"amount": 0, "description": "description"}},
        "capital": {{"amount": 0, "description": "description"}},
        "contingency": {{"amount": 0, "percentage": 0}}
    }},
    "total_budget": 0,
    "funding_sources": [
        {{
            "source": "source name",
            "amount": 0,
            "terms": "terms description"
        }}
    ],
    "financial_timeline": [
        {{
            "phase": "phase name",
            "cost": 0,
            "timeline": "duration"
        }}
    ],
    "cash_flow_projection": "description",
    "financial_controls": ["control 1", "control 2"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.3,
                max_tokens=3000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                structure = json.loads(json_match.group())
                self.log_action("Financial structure designed", {"total_budget": structure.get("total_budget")})
                return structure
        except Exception as e:
            self.logger.warning(f"Financial structure design LLM call failed: {e}")
        
        # Fallback structure
        total_budget = budget_constraints.get("total_budget", 100000)
        return {
            "cost_breakdown": {
                "personnel": {"amount": total_budget * 0.5, "description": "Team salaries and benefits"},
                "operations": {"amount": total_budget * 0.3, "description": "Operational expenses"},
                "capital": {"amount": total_budget * 0.15, "description": "Capital expenditures"},
                "contingency": {"amount": total_budget * 0.05, "percentage": 5}
            },
            "total_budget": total_budget,
            "funding_sources": [
                {
                    "source": "Primary funding",
                    "amount": total_budget,
                    "terms": "As per agreement"
                }
            ],
            "financial_timeline": [
                {
                    "phase": "Phase 1",
                    "cost": total_budget * 0.4,
                    "timeline": "Months 1-3"
                },
                {
                    "phase": "Phase 2",
                    "cost": total_budget * 0.4,
                    "timeline": "Months 4-6"
                },
                {
                    "phase": "Phase 3",
                    "cost": total_budget * 0.2,
                    "timeline": "Months 7-9"
                }
            ],
            "cash_flow_projection": "Monthly disbursements based on milestones",
            "financial_controls": ["Monthly budget reviews", "Expense approvals", "Financial reporting"]
        }
    
    def develop_revenue_model(
        self,
        business_concept: Dict[str, Any],
        market_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Develop revenue model for business concept
        
        Args:
            business_concept: Business concept and value proposition
            market_analysis: Market analysis and competitive landscape
        
        Returns:
            Revenue model with pricing strategy and revenue streams
        """
        self.log_action("Developing revenue model")
        
        market_str = json.dumps(market_analysis, indent=2) if market_analysis else "None provided"
        
        prompt = f"""As a Business Architect, develop a comprehensive revenue model.

Business Concept:
{json.dumps(business_concept, indent=2)}

Market Analysis:
{market_str}

Develop a revenue model that includes:
1. Revenue streams (primary and secondary)
2. Pricing strategy and models
3. Revenue projections
4. Monetization mechanisms
5. Revenue sustainability

Return JSON:
{{
    "revenue_streams": [
        {{
            "stream": "stream name",
            "type": "recurring/one-time/subscription/etc",
            "pricing_model": "model description",
            "projected_revenue": 0,
            "description": "description"
        }}
    ],
    "pricing_strategy": {{
        "model": "pricing model",
        "rationale": "why this model",
        "price_points": ["price 1", "price 2"]
    }},
    "revenue_projections": {{
        "year_1": 0,
        "year_2": 0,
        "year_3": 0
    }},
    "monetization_mechanisms": ["mechanism 1", "mechanism 2"],
    "sustainability": "assessment"
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.4,
                max_tokens=3000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                model = json.loads(json_match.group())
                self.log_action("Revenue model developed", {"streams": len(model.get("revenue_streams", []))})
                return model
        except Exception as e:
            self.logger.warning(f"Revenue model development LLM call failed: {e}")
        
        # Fallback model
        return {
            "revenue_streams": [
                {
                    "stream": "Primary service",
                    "type": "recurring",
                    "pricing_model": "Subscription or project-based",
                    "projected_revenue": 0,
                    "description": "Main revenue source"
                }
            ],
            "pricing_strategy": {
                "model": "Value-based pricing",
                "rationale": "Based on value delivered",
                "price_points": ["Tier 1", "Tier 2", "Tier 3"]
            },
            "revenue_projections": {
                "year_1": 0,
                "year_2": 0,
                "year_3": 0
            },
            "monetization_mechanisms": ["Service delivery", "Consulting", "Products"],
            "sustainability": "Requires market validation"
        }
    
    def design_business_model(
        self,
        value_proposition: Dict[str, Any],
        target_market: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Design complete business model
        
        Args:
            value_proposition: Value proposition and unique selling points
            target_market: Target market and customer segments
        
        Returns:
            Complete business model canvas
        """
        self.log_action("Designing business model")
        
        prompt = f"""As a Business Architect, design a complete business model using Business Model Canvas framework.

Value Proposition:
{json.dumps(value_proposition, indent=2)}

Target Market:
{json.dumps(target_market, indent=2)}

Create a comprehensive business model that includes:
1. Value Proposition (what value we deliver)
2. Customer Segments (who we serve)
3. Channels (how we reach customers)
4. Customer Relationships (how we interact)
5. Revenue Streams (how we make money)
6. Key Resources (what we need)
7. Key Activities (what we do)
8. Key Partnerships (who we work with)
9. Cost Structure (what it costs)

Return JSON:
{{
    "value_proposition": ["proposition 1", "proposition 2"],
    "customer_segments": ["segment 1", "segment 2"],
    "channels": ["channel 1", "channel 2"],
    "customer_relationships": ["relationship type 1"],
    "revenue_streams": ["stream 1", "stream 2"],
    "key_resources": ["resource 1", "resource 2"],
    "key_activities": ["activity 1", "activity 2"],
    "key_partnerships": ["partner 1", "partner 2"],
    "cost_structure": ["cost 1", "cost 2"],
    "competitive_advantages": ["advantage 1"]
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.4,
                max_tokens=3000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                model = json.loads(json_match.group())
                self.log_action("Business model designed")
                return model
        except Exception as e:
            self.logger.warning(f"Business model design LLM call failed: {e}")
        
        # Fallback model
        return {
            "value_proposition": value_proposition.get("propositions", ["Quality service", "Expertise"]),
            "customer_segments": target_market.get("segments", ["Primary market"]),
            "channels": ["Direct sales", "Online", "Partnerships"],
            "customer_relationships": ["Long-term partnerships", "Consultative approach"],
            "revenue_streams": ["Service fees", "Consulting"],
            "key_resources": ["Expert team", "Technology", "Knowledge"],
            "key_activities": ["Service delivery", "Client management", "Innovation"],
            "key_partnerships": ["Strategic partners", "Suppliers"],
            "cost_structure": ["Personnel", "Operations", "Technology"],
            "competitive_advantages": ["Expertise", "Quality", "Innovation"]
        }
    
    def create_monetization_strategy(
        self,
        product_or_service: Dict[str, Any],
        market_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create monetization strategy
        
        Args:
            product_or_service: Product or service description
            market_context: Market context and competitive landscape
        
        Returns:
            Monetization strategy with pricing and revenue tactics
        """
        self.log_action("Creating monetization strategy")
        
        prompt = f"""As a Business Architect, create a comprehensive monetization strategy.

Product/Service:
{json.dumps(product_or_service, indent=2)}

Market Context:
{json.dumps(market_context, indent=2)}

Create a monetization strategy that includes:
1. Pricing models (subscription, one-time, freemium, etc.)
2. Pricing tiers and packages
3. Revenue optimization tactics
4. Market positioning for pricing
5. Competitive pricing analysis

Return JSON:
{{
    "pricing_models": [
        {{
            "model": "model name",
            "description": "description",
            "target_segment": "segment",
            "pricing": "pricing details"
        }}
    ],
    "pricing_tiers": [
        {{
            "tier": "tier name",
            "price": 0,
            "features": ["feature 1"],
            "target_customer": "customer type"
        }}
    ],
    "revenue_optimization": ["tactic 1", "tactic 2"],
    "market_positioning": "positioning description",
    "competitive_analysis": "analysis"
}}
"""
        
        try:
            response = self.call_llm(
                prompt,
                provider=LLMProvider.ANTHROPIC,
                temperature=0.4,
                max_tokens=3000
            )
            
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                strategy = json.loads(json_match.group())
                self.log_action("Monetization strategy created", {"models": len(strategy.get("pricing_models", []))})
                return strategy
        except Exception as e:
            self.logger.warning(f"Monetization strategy LLM call failed: {e}")
        
        # Fallback strategy
        return {
            "pricing_models": [
                {
                    "model": "Project-based",
                    "description": "Fixed price per project",
                    "target_segment": "Enterprise clients",
                    "pricing": "Based on scope"
                }
            ],
            "pricing_tiers": [
                {
                    "tier": "Basic",
                    "price": 0,
                    "features": ["Core features"],
                    "target_customer": "Small clients"
                },
                {
                    "tier": "Premium",
                    "price": 0,
                    "features": ["All features", "Priority support"],
                    "target_customer": "Enterprise clients"
                }
            ],
            "revenue_optimization": ["Upselling", "Cross-selling", "Retention"],
            "market_positioning": "Premium quality at competitive pricing",
            "competitive_analysis": "Positioned as value leader"
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input - route to appropriate method"""
        action = input_data.get("action", "design_financial")
        
        if action == "design_financial":
            return self.design_financial_structure(
                input_data.get("project_requirements", {}),
                input_data.get("budget_constraints", {})
            )
        elif action == "develop_revenue":
            return self.develop_revenue_model(
                input_data.get("business_concept", {}),
                input_data.get("market_analysis")
            )
        elif action == "design_business":
            return self.design_business_model(
                input_data.get("value_proposition", {}),
                input_data.get("target_market", {})
            )
        elif action == "monetize":
            return self.create_monetization_strategy(
                input_data.get("product_or_service", {}),
                input_data.get("market_context", {})
            )
        else:
            # Default to financial structure design
            return self.design_financial_structure(
                input_data.get("project_requirements", {}),
                input_data.get("budget_constraints", {})
            )

