"""
Master Writer Agent
Proposal writing, content generation, multi-LLM optimization (use best LLM for writing), professional writing style
"""

from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from config.llm_config import LLMProvider
import json


class MasterWriterAgent(BaseAgent):
    """
    Master Writer Agent
    Handles proposal writing and content generation using OpenAI (best for writing)
    """
    
    def __init__(self):
        super().__init__(
            name="Master Writer",
            role="Professional proposal writing and content generation",
            task_type="writing"
        )
    
    def write_proposal_section(
        self,
        section_name: str,
        requirements: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        style_guide: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Write a proposal section with professional quality
        
        Args:
            section_name: Name of the section (e.g., "Executive Summary")
            requirements: Section requirements and guidelines
            data: Data and information to include
            style_guide: Writing style guidelines
        
        Returns:
            Written section with content and metadata
        """
        self.log_action(f"Writing proposal section: {section_name}")
        
        data_str = json.dumps(data, indent=2) if data else "None provided"
        style_str = json.dumps(style_guide, indent=2) if style_guide else "Standard professional style"
        
        prompt = f"""As a Master Writer, write a professional, compelling proposal section.

Section Name: {section_name}

Requirements:
{json.dumps(requirements, indent=2)}

Data to Include:
{data_str}

Style Guide:
{style_str}

Write a high-quality section that:
1. Is clear, professional, and persuasive
2. Addresses all requirements
3. Incorporates provided data effectively
4. Follows the style guide
5. Is engaging and compelling
6. Uses appropriate tone and language

Return the written content as professional prose. Make it compelling and well-structured.
"""
        
        try:
            # Use OpenAI for writing (best for writing tasks)
            content = self.call_llm(
                prompt,
                provider=LLMProvider.OPENAI,
                temperature=0.7,
                max_tokens=4000
            )
            
            self.log_action(f"Section written: {section_name}", {"length": len(content)})
            
            return {
                "section_name": section_name,
                "content": content,
                "word_count": len(content.split()),
                "style": "professional",
                "requirements_met": True
            }
        except Exception as e:
            self.logger.warning(f"Writing LLM call failed: {e}")
            # Fallback content
            return {
                "section_name": section_name,
                "content": f"[{section_name}]\n\nContent for {section_name} section. This section addresses the requirements: {json.dumps(requirements)}",
                "word_count": 0,
                "style": "professional",
                "requirements_met": False,
                "error": str(e)
            }
    
    def write_full_proposal(
        self,
        proposal_structure: Dict[str, Any],
        data: Dict[str, Any],
        style_guide: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Write a complete proposal document
        
        Args:
            proposal_structure: Structure with sections and requirements
            data: All data to include in proposal
            style_guide: Writing style guidelines
        
        Returns:
            Complete proposal with all sections
        """
        self.log_action("Writing full proposal")
        
        sections = proposal_structure.get("sections", [])
        written_sections = {}
        
        for section in sections:
            section_name = section.get("name", "Section")
            section_requirements = section.get("requirements", {})
            section_data = data.get(section_name.lower().replace(" ", "_"), {})
            
            written_section = self.write_proposal_section(
                section_name,
                section_requirements,
                section_data,
                style_guide
            )
            written_sections[section_name] = written_section
        
        # Create executive summary if not already written
        if "Executive Summary" not in written_sections:
            exec_summary = self.write_executive_summary(
                written_sections,
                proposal_structure.get("overview", {})
            )
            written_sections["Executive Summary"] = exec_summary
        
        self.log_action("Full proposal written", {"sections": len(written_sections)})
        
        return {
            "proposal": written_sections,
            "total_sections": len(written_sections),
            "total_word_count": sum(s.get("word_count", 0) for s in written_sections.values()),
            "style": style_guide.get("style", "professional") if style_guide else "professional"
        }
    
    def write_executive_summary(
        self,
        proposal_sections: Dict[str, Any],
        overview: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Write executive summary that captures key points
        
        Args:
            proposal_sections: All proposal sections
            overview: Overview and key highlights
        
        Returns:
            Executive summary section
        """
        self.log_action("Writing executive summary")
        
        # Extract key points from sections
        key_points = []
        for section_name, section_data in proposal_sections.items():
            if isinstance(section_data, dict):
                content = section_data.get("content", "")
                # Extract first sentence or key phrase
                if content:
                    first_sentence = content.split('.')[0] if '.' in content else content[:100]
                    key_points.append(f"{section_name}: {first_sentence}")
        
        overview_str = json.dumps(overview, indent=2) if overview else "None"
        
        prompt = f"""As a Master Writer, write a compelling executive summary for a proposal.

Key Points from Sections:
{json.dumps(key_points, indent=2)}

Overview:
{overview_str}

Write an executive summary that:
1. Captures the essence of the proposal
2. Highlights key value propositions
3. Is concise but comprehensive (1-2 pages)
4. Is compelling and persuasive
5. Makes a strong case for approval
6. Uses professional, engaging language

Return the executive summary as professional prose.
"""
        
        try:
            content = self.call_llm(
                prompt,
                provider=LLMProvider.OPENAI,
                temperature=0.7,
                max_tokens=2000
            )
            
            return {
                "section_name": "Executive Summary",
                "content": content,
                "word_count": len(content.split()),
                "style": "professional",
                "requirements_met": True
            }
        except Exception as e:
            self.logger.warning(f"Executive summary writing failed: {e}")
            return {
                "section_name": "Executive Summary",
                "content": "Executive Summary: [Summary of proposal key points]",
                "word_count": 0,
                "style": "professional",
                "requirements_met": False
            }
    
    def refine_content(
        self,
        content: str,
        feedback: List[str],
        style_guide: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Refine and improve existing content based on feedback
        
        Args:
            content: Original content
            feedback: Feedback and improvement suggestions
            style_guide: Writing style guidelines
        
        Returns:
            Refined content
        """
        self.log_action("Refining content")
        
        style_str = json.dumps(style_guide, indent=2) if style_guide else "Standard professional style"
        
        prompt = f"""As a Master Writer, refine and improve this content based on feedback.

Original Content:
{content}

Feedback:
{json.dumps(feedback, indent=2)}

Style Guide:
{style_str}

Refine the content to:
1. Address all feedback points
2. Improve clarity and flow
3. Enhance persuasiveness
4. Maintain professional style
5. Ensure consistency
6. Strengthen key messages

Return the refined content.
"""
        
        try:
            refined = self.call_llm(
                prompt,
                provider=LLMProvider.OPENAI,
                temperature=0.6,
                max_tokens=4000
            )
            
            return {
                "original_content": content,
                "refined_content": refined,
                "improvements_made": feedback,
                "word_count": len(refined.split())
            }
        except Exception as e:
            self.logger.warning(f"Content refinement failed: {e}")
            return {
                "original_content": content,
                "refined_content": content,
                "improvements_made": [],
                "error": str(e)
            }
    
    def generate_content(
        self,
        topic: str,
        purpose: str,
        audience: str,
        length: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate content for a specific topic and purpose
        
        Args:
            topic: Content topic
            purpose: Purpose of the content
            audience: Target audience
            length: Content length (short/medium/long)
        
        Returns:
            Generated content
        """
        self.log_action(f"Generating content: {topic}")
        
        length_guidance = {
            "short": "500-800 words",
            "medium": "1000-1500 words",
            "long": "2000-3000 words"
        }
        
        prompt = f"""As a Master Writer, generate professional content.

Topic: {topic}
Purpose: {purpose}
Target Audience: {audience}
Length: {length_guidance.get(length, "medium")}

Generate content that:
1. Is relevant to the topic and purpose
2. Is appropriate for the target audience
3. Is well-structured and engaging
4. Uses professional language
5. Is persuasive and compelling
6. Meets the specified length requirements

Return the generated content.
"""
        
        try:
            content = self.call_llm(
                prompt,
                provider=LLMProvider.OPENAI,
                temperature=0.7,
                max_tokens=4000 if length == "long" else 2000
            )
            
            return {
                "topic": topic,
                "purpose": purpose,
                "audience": audience,
                "content": content,
                "word_count": len(content.split()),
                "length": length
            }
        except Exception as e:
            self.logger.warning(f"Content generation failed: {e}")
            return {
                "topic": topic,
                "purpose": purpose,
                "audience": audience,
                "content": f"Content about {topic} for {purpose}",
                "word_count": 0,
                "length": length,
                "error": str(e)
            }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input - route to appropriate method"""
        action = input_data.get("action", "write_section")
        
        if action == "write_section":
            return self.write_proposal_section(
                input_data.get("section_name", "Section"),
                input_data.get("requirements", {}),
                input_data.get("data"),
                input_data.get("style_guide")
            )
        elif action == "write_proposal":
            return self.write_full_proposal(
                input_data.get("proposal_structure", {}),
                input_data.get("data", {}),
                input_data.get("style_guide")
            )
        elif action == "refine":
            return self.refine_content(
                input_data.get("content", ""),
                input_data.get("feedback", []),
                input_data.get("style_guide")
            )
        elif action == "generate":
            return self.generate_content(
                input_data.get("topic", ""),
                input_data.get("purpose", ""),
                input_data.get("audience", ""),
                input_data.get("length", "medium")
            )
        else:
            # Default to writing a section
            return self.write_proposal_section(
                input_data.get("section_name", "Section"),
                input_data.get("requirements", {}),
                input_data.get("data")
            )

