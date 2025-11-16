"""
Configuration settings for the proposal generator
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4-turbo-preview"  # Use GPT-4 for best quality

# Funder-specific requirements
FUNDER_REQUIREMENTS = {
    "gates_foundation": {
        "name": "Bill & Melinda Gates Foundation",
        "focus_areas": [
            "Global Health",
            "Global Development",
            "Global Growth & Opportunity",
            "Gender Equality"
        ],
        "key_requirements": [
            "Clear problem statement with data",
            "Evidence-based solution",
            "Measurable impact metrics",
            "Sustainability plan",
            "Partnership strategy",
            "Budget breakdown",
            "Timeline with milestones"
        ],
        "tone": "Data-driven, compassionate, impact-focused"
    },
    "world_bank": {
        "name": "World Bank",
        "focus_areas": [
            "Poverty Reduction",
            "Infrastructure Development",
            "Climate Change",
            "Education",
            "Healthcare Systems"
        ],
        "key_requirements": [
            "Economic analysis",
            "Stakeholder engagement plan",
            "Risk assessment",
            "Environmental impact assessment",
            "Gender and social inclusion",
            "Financial sustainability",
            "Monitoring and evaluation framework"
        ],
        "tone": "Formal, technical, evidence-based"
    },
    "who": {
        "name": "World Health Organization",
        "focus_areas": [
            "Public Health",
            "Disease Prevention",
            "Health Systems Strengthening",
            "Emergency Response",
            "Health Equity"
        ],
        "key_requirements": [
            "Public health impact",
            "Evidence-based interventions",
            "Health system integration",
            "Capacity building",
            "Monitoring and surveillance",
            "Partnership with health ministries",
            "Sustainability and scalability"
        ],
        "tone": "Scientific, authoritative, public health-focused"
    },
    "fortune_500": {
        "name": "Fortune 500 Corporate",
        "focus_areas": [
            "CSR Initiatives",
            "Social Impact",
            "Innovation",
            "Community Development",
            "Environmental Sustainability"
        ],
        "key_requirements": [
            "Business case alignment",
            "Brand value proposition",
            "ROI and impact metrics",
            "Stakeholder engagement",
            "Media and PR opportunities",
            "Scalability",
            "Partnership opportunities"
        ],
        "tone": "Business-oriented, strategic, value-driven"
    }
}

# Document types
DOCUMENT_TYPES = {
    "proposal": {
        "name": "Full Proposal",
        "sections": [
            "Executive Summary",
            "Problem Statement",
            "Solution/Approach",
            "Objectives and Goals",
            "Methodology",
            "Timeline and Milestones",
            "Budget",
            "Impact and Outcomes",
            "Sustainability Plan",
            "Partnerships",
            "Risk Assessment",
            "Monitoring and Evaluation"
        ]
    },
    "concept_note": {
        "name": "Concept Note",
        "sections": [
            "Introduction",
            "Problem Statement",
            "Proposed Solution",
            "Objectives",
            "Expected Outcomes",
            "Budget Estimate",
            "Timeline",
            "Next Steps"
        ]
    },
    "pitch_deck": {
        "name": "Pitch Deck",
        "sections": [
            "Title Slide",
            "Problem",
            "Solution",
            "Market Opportunity",
            "Business Model",
            "Traction/Milestones",
            "Team",
            "Financials",
            "Ask",
            "Contact"
        ]
    },
    "executive_summary": {
        "name": "Executive Summary",
        "sections": [
            "Overview",
            "Problem",
            "Solution",
            "Impact",
            "Budget",
            "Timeline",
            "Call to Action"
        ]
    }
}

