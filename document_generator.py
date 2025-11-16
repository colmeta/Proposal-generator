"""
Professional document generator with human-like writing
"""
import os
from typing import Dict, List, Optional
from openai import OpenAI
from config import FUNDER_REQUIREMENTS, DOCUMENT_TYPES, OPENAI_API_KEY, OPENAI_MODEL


class DocumentGenerator:
    """Generates professional, human-written quality documents"""
    
    def __init__(self, funder_type: str, document_type: str):
        self.funder_type = funder_type
        self.document_type = document_type
        self.funder_reqs = FUNDER_REQUIREMENTS.get(funder_type, {})
        self.doc_template = DOCUMENT_TYPES.get(document_type, {})
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
    
    def generate_document(self, user_responses: Dict[str, str], existing_doc: Optional[str] = None) -> str:
        """Generate a complete document based on user responses"""
        
        if not self.client:
            return "Error: OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file."
        
        # Build context for the AI
        context = self._build_context(user_responses, existing_doc)
        
        # Generate the document
        prompt = self._create_generation_prompt(context)
        
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Balanced creativity and consistency
                max_tokens=4000
            )
            
            generated_text = response.choices[0].message.content
            return generated_text
        
        except Exception as e:
            return f"Error generating document: {str(e)}"
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for natural, human-like writing"""
        funder_name = self.funder_reqs.get("name", "the funder")
        tone = self.funder_reqs.get("tone", "professional and compelling")
        
        return f"""You are an expert grant writer and proposal specialist with over 20 years of experience writing winning proposals for {funder_name}.

Your writing style is:
- Natural, engaging, and human-written (never robotic or AI-generated sounding)
- Professional yet accessible
- Data-driven and evidence-based
- Compelling and persuasive
- {tone}

You write proposals that:
- Tell a compelling story
- Use specific examples and concrete details
- Include quantitative data and evidence
- Address the funder's specific priorities
- Demonstrate clear impact and value
- Show passion and commitment without being overly emotional

Never use phrases like "it is important to note" or "it should be mentioned" - these sound AI-generated. Instead, state facts directly and confidently.

Write as if you deeply understand the project and are personally committed to its success. Use varied sentence structure, natural transitions, and authentic language."""
    
    def _build_context(self, user_responses: Dict[str, str], existing_doc: Optional[str]) -> Dict:
        """Build context from user responses"""
        context = {
            "funder": self.funder_reqs.get("name", ""),
            "funder_focus": self.funder_reqs.get("focus_areas", []),
            "funder_requirements": self.funder_reqs.get("key_requirements", []),
            "document_type": self.doc_template.get("name", ""),
            "required_sections": self.doc_template.get("sections", []),
            "user_responses": user_responses,
            "existing_doc": existing_doc
        }
        return context
    
    def _create_generation_prompt(self, context: Dict) -> str:
        """Create the prompt for document generation"""
        doc_type = context["document_type"]
        funder = context["funder"]
        sections = context["required_sections"]
        
        prompt = f"""Write a professional {doc_type} for {funder}.

REQUIRED SECTIONS:
{chr(10).join(f"- {section}" for section in sections)}

FUNDER PRIORITIES:
{chr(10).join(f"- {req}" for req in context["funder_requirements"])}

PROJECT INFORMATION:
"""
        
        # Add user responses
        for key, value in context["user_responses"].items():
            if value:
                prompt += f"\n{key}: {value}\n"
        
        if context["existing_doc"]:
            prompt += f"\n\nEXISTING DOCUMENT (enhance and improve this):\n{context['existing_doc']}\n"
            prompt += "\nIMPORTANT: Enhance the existing document by:\n"
            prompt += "- Improving clarity and flow\n"
            prompt += "- Adding missing critical information\n"
            prompt += "- Strengthening arguments with data and evidence\n"
            prompt += "- Making it more compelling and persuasive\n"
            prompt += "- Ensuring it meets all funder requirements\n"
        
        prompt += f"""

INSTRUCTIONS:
1. Write in a natural, human voice - avoid AI-generated language patterns
2. Use specific examples, data, and concrete details from the project information
3. Make it compelling and persuasive while remaining professional
4. Ensure all required sections are included and comprehensive
5. Address all funder priorities and requirements
6. Use varied sentence structure and natural transitions
7. Write with confidence and authority - avoid hedging language
8. Include quantitative data where possible
9. Tell a story that connects the problem, solution, and impact

Generate the complete {doc_type} now:"""
        
        return prompt
    
    def generate_change_summary(self, existing_doc: str, new_doc: str) -> str:
        """Generate a summary of what will be changed"""
        if not self.client:
            return "Error: OpenAI API key not configured."
        
        prompt = f"""Compare these two documents and provide a clear summary of what will be changed, added, or improved.

EXISTING DOCUMENT:
{existing_doc[:2000]}

NEW DOCUMENT:
{new_doc[:2000]}

Provide a concise summary in the following format:
- What sections will be added
- What sections will be enhanced/improved
- What new information will be included
- What gaps will be filled

Be specific and clear about the improvements."""

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a document review specialist. Provide clear, concise summaries of document changes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating change summary: {str(e)}"

