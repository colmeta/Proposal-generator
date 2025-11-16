"""
Intelligent question generation for users with only ideas
"""
from typing import List, Dict
from config import FUNDER_REQUIREMENTS, DOCUMENT_TYPES


class QuestionGenerator:
    """Generates intelligent questions to gather necessary information"""
    
    def __init__(self, funder_type: str, document_type: str):
        self.funder_type = funder_type
        self.document_type = document_type
        self.funder_reqs = FUNDER_REQUIREMENTS.get(funder_type, {})
    
    def generate_questions(self, user_input: str = "") -> List[Dict[str, str]]:
        """Generate questions based on what information is missing"""
        questions = []
        
        # Core questions for any proposal
        core_questions = [
            {
                "category": "Problem Statement",
                "question": "What specific problem or challenge are you trying to solve? Please describe the issue in detail, including who is affected and the scale of the problem.",
                "why": "Funders need to understand the problem clearly to assess the need for your solution"
            },
            {
                "category": "Solution",
                "question": "What is your proposed solution or approach? How does it address the problem you described?",
                "why": "This is the core of your proposal - funders need to understand your unique approach"
            },
            {
                "category": "Target Beneficiaries",
                "question": "Who will benefit from your project? Please specify demographics, geographic location, and estimated number of beneficiaries.",
                "why": "Funders need to understand the reach and impact of your project"
            },
            {
                "category": "Objectives",
                "question": "What are your specific, measurable objectives? What do you hope to achieve in 1 year, 3 years, and 5 years?",
                "why": "Clear objectives help funders understand your goals and measure success"
            },
            {
                "category": "Budget",
                "question": "What is your estimated total budget? Can you break down major cost categories (personnel, equipment, operations, etc.)?",
                "why": "Budget information is critical for funders to assess feasibility and resource needs"
            },
            {
                "category": "Timeline",
                "question": "What is your proposed timeline? What are the key milestones and phases of your project?",
                "why": "A realistic timeline shows funders you have a clear implementation plan"
            },
            {
                "category": "Impact Metrics",
                "question": "How will you measure success? What specific metrics or indicators will you track?",
                "why": "Funders require measurable outcomes to evaluate impact"
            },
            {
                "category": "Sustainability",
                "question": "How will your project continue after the initial funding period? What is your sustainability plan?",
                "why": "Funders want to ensure long-term impact beyond their initial investment"
            },
            {
                "category": "Partnerships",
                "question": "Do you have existing partnerships or collaborations? Who are your key stakeholders and partners?",
                "why": "Partnerships demonstrate credibility and capacity for implementation"
            },
            {
                "category": "Organization",
                "question": "Tell us about your organization: What is your mission, track record, and capacity to implement this project?",
                "why": "Funders need to trust that you have the capability to deliver on your proposal"
            }
        ]
        
        # Add funder-specific questions
        funder_questions = self._get_funder_specific_questions()
        
        # Combine and return
        all_questions = core_questions + funder_questions
        
        return all_questions
    
    def _get_funder_specific_questions(self) -> List[Dict[str, str]]:
        """Get questions specific to the selected funder"""
        questions = []
        
        if self.funder_type == "gates_foundation":
            questions.extend([
                {
                    "category": "Evidence Base",
                    "question": "What evidence or research supports your approach? Can you cite studies, pilot results, or similar successful interventions?",
                    "why": "Gates Foundation prioritizes evidence-based solutions"
                },
                {
                    "category": "Gender Equity",
                    "question": "How does your project address gender equity and inclusion? What specific measures will you take?",
                    "why": "Gender equality is a core focus area for Gates Foundation"
                },
                {
                    "category": "Scale and Replication",
                    "question": "How can your solution be scaled or replicated in other contexts? What is your scaling strategy?",
                    "why": "Gates Foundation seeks solutions that can have broad impact"
                }
            ])
        
        elif self.funder_type == "world_bank":
            questions.extend([
                {
                    "category": "Economic Analysis",
                    "question": "What is the economic case for your project? Can you provide cost-benefit analysis or economic impact projections?",
                    "why": "World Bank requires strong economic justification"
                },
                {
                    "category": "Government Engagement",
                    "question": "How will you engage with government stakeholders? Do you have government support or partnerships?",
                    "why": "World Bank projects typically require government alignment"
                },
                {
                    "category": "Environmental Impact",
                    "question": "What are the environmental impacts of your project? How will you mitigate any negative effects?",
                    "why": "World Bank requires environmental impact assessments"
                },
                {
                    "category": "Social Inclusion",
                    "question": "How will your project ensure inclusion of marginalized groups? What is your social inclusion strategy?",
                    "why": "World Bank prioritizes inclusive development"
                }
            ])
        
        elif self.funder_type == "who":
            questions.extend([
                {
                    "category": "Public Health Impact",
                    "question": "What is the specific public health impact? How will you measure health outcomes and improvements?",
                    "why": "WHO focuses on measurable public health outcomes"
                },
                {
                    "category": "Health System Integration",
                    "question": "How will your project integrate with existing health systems? What is your engagement with health ministries?",
                    "why": "WHO projects must align with national health systems"
                },
                {
                    "category": "Capacity Building",
                    "question": "How will you build local capacity? What training or knowledge transfer will you provide?",
                    "why": "WHO emphasizes sustainable capacity building"
                },
                {
                    "category": "Disease/Health Focus",
                    "question": "What specific health issue or disease does your project address? What is the epidemiological context?",
                    "why": "WHO needs clear understanding of the health problem"
                }
            ])
        
        elif self.funder_type == "fortune_500":
            questions.extend([
                {
                    "category": "Business Alignment",
                    "question": "How does your project align with corporate values and business objectives? What is the value proposition for the company?",
                    "why": "Corporate funders need clear business case alignment"
                },
                {
                    "category": "Brand Value",
                    "question": "What brand value or PR opportunities does your project offer? How will it enhance the company's reputation?",
                    "why": "Corporate funders consider brand and reputation impact"
                },
                {
                    "category": "ROI",
                    "question": "What is the return on investment? How will you demonstrate value and impact to stakeholders?",
                    "why": "Corporate funders need to justify investment to stakeholders"
                },
                {
                    "category": "Partnership Opportunities",
                    "question": "What partnership or collaboration opportunities exist? How can the company be involved beyond funding?",
                    "why": "Corporate funders often seek active partnership opportunities"
                }
            ])
        
        return questions
    
    def format_questions_for_user(self, questions: List[Dict[str, str]]) -> str:
        """Format questions in a user-friendly way"""
        output = "To create a compelling proposal, I need to understand your project better.\n"
        output += "Please answer the following questions:\n\n"
        output += "=" * 70 + "\n\n"
        
        for i, q in enumerate(questions, 1):
            output += f"Question {i}: {q['category']}\n"
            output += f"{q['question']}\n"
            output += f"\n💡 Why this matters: {q['why']}\n"
            output += "\n" + "-" * 70 + "\n\n"
        
        output += "\nYou can answer these questions in any order, and feel free to provide as much detail as possible.\n"
        output += "The more information you provide, the stronger your proposal will be.\n"
        
        return output

