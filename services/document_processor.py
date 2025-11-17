"""
Document Processor Service
Handles PDF, images, text extraction, and document analysis
"""

import os
import io
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import logging
import base64

# PDF processing
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Image processing
try:
    from PIL import Image
    import pytesseract
    IMAGE_OCR_AVAILABLE = True
except ImportError:
    IMAGE_OCR_AVAILABLE = False

# Document processing
try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from config.llm_config import llm_config, LLMProvider

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Document processor for PDFs, images, DOCX, and text files
    """
    
    def __init__(self):
        """Initialize document processor"""
        self.supported_formats = {
            'pdf': PDF_AVAILABLE,
            'docx': DOCX_AVAILABLE,
            'doc': DOCX_AVAILABLE,
            'txt': True,
            'png': IMAGE_OCR_AVAILABLE,
            'jpg': IMAGE_OCR_AVAILABLE,
            'jpeg': IMAGE_OCR_AVAILABLE,
            'gif': IMAGE_OCR_AVAILABLE,
            'bmp': IMAGE_OCR_AVAILABLE,
        }
        logger.info("DocumentProcessor initialized")
    
    def process_document(
        self,
        file_content: bytes,
        filename: str,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a document and extract text content
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            file_type: File type/extension (auto-detected if None)
        
        Returns:
            Dict with extracted text and metadata
        """
        if file_type is None:
            file_type = Path(filename).suffix.lower().lstrip('.')
        
        if file_type not in self.supported_formats:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        if not self.supported_formats[file_type]:
            raise ValueError(f"File type {file_type} not available (missing dependencies)")
        
        try:
            if file_type == 'pdf':
                return self._process_pdf(file_content, filename)
            elif file_type in ['docx', 'doc']:
                return self._process_docx(file_content, filename)
            elif file_type == 'txt':
                return self._process_text(file_content, filename)
            elif file_type in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
                return self._process_image(file_content, filename, file_type)
            else:
                raise ValueError(f"Unknown file type: {file_type}")
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            raise
    
    def _process_pdf(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from PDF"""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")
        
        text_parts = []
        num_pages = 0
        
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
        
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            raise
        
        full_text = "\n\n".join(text_parts)
        
        return {
            "filename": filename,
            "file_type": "pdf",
            "text": full_text,
            "num_pages": num_pages,
            "char_count": len(full_text),
            "word_count": len(full_text.split())
        }
    
    def _process_docx(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from DOCX"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx not installed. Install with: pip install python-docx")
        
        try:
            docx_file = io.BytesIO(content)
            doc = DocxDocument(docx_file)
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            full_text = "\n".join(text_parts)
        
        except Exception as e:
            logger.error(f"Error reading DOCX: {e}")
            raise
        
        return {
            "filename": filename,
            "file_type": "docx",
            "text": full_text,
            "char_count": len(full_text),
            "word_count": len(full_text.split())
        }
    
    def _process_text(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Process plain text file"""
        try:
            # Try UTF-8 first
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback to latin-1
                text = content.decode('latin-1', errors='ignore')
        
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            raise
        
        return {
            "filename": filename,
            "file_type": "txt",
            "text": text,
            "char_count": len(text),
            "word_count": len(text.split())
        }
    
    def _process_image(self, content: bytes, filename: str, file_type: str) -> Dict[str, Any]:
        """Extract text from image using OCR"""
        if not IMAGE_OCR_AVAILABLE:
            raise ImportError("PIL/pytesseract not installed. Install with: pip install Pillow pytesseract")
        
        try:
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
        
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
        
        return {
            "filename": filename,
            "file_type": file_type,
            "text": text,
            "char_count": len(text),
            "word_count": len(text.split()),
            "image_size": image.size if 'image' in locals() else None
        }
    
    def extract_structured_info(self, text: str, document_type: str = "general") -> Dict[str, Any]:
        """
        Use LLM to extract structured information from document text
        
        Args:
            text: Extracted text from document
            document_type: Type of document (project_report, team_profile, budget, etc.)
        
        Returns:
            Structured information extracted from document
        """
        # Limit text length for LLM
        text_preview = text[:10000] if len(text) > 10000 else text
        
        prompt = f"""Extract structured information from this {document_type} document.

Document Text:
{text_preview}

Extract and return a JSON object with relevant information. Structure depends on document type:

For project reports:
{{
    "projects": [{{"name": "...", "description": "...", "status": "...", "achievements": [...]}}],
    "activities": [{{"activity": "...", "date": "...", "impact": "..."}}],
    "metrics": {{"key_metric": "value"}},
    "team_members": [{{"name": "...", "role": "..."}}]
}}

For team profiles:
{{
    "team_members": [{{"name": "...", "role": "...", "expertise": [...], "experience": "..."}}],
    "organizational_structure": "...",
    "key_skills": [...]
}}

For budgets/financial:
{{
    "budget_items": [{{"item": "...", "amount": "...", "category": "..."}}],
    "total_budget": "...",
    "funding_sources": [...],
    "expenses": [...]
}}

For general documents, extract:
{{
    "key_points": [...],
    "important_dates": [...],
    "people_mentioned": [...],
    "organizations": [...],
    "metrics": {{}},
    "summary": "..."
}}

Return ONLY valid JSON, no other text.
"""
        
        try:
            response = llm_config.call_llm(
                prompt=prompt,
                task_type="research",
                provider=LLMProvider.GEMINI,
                temperature=0.3,
                max_tokens=3000
            )
            
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response["content"], re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response["content"])
        
        except Exception as e:
            logger.error(f"Error extracting structured info: {e}")
            return {
                "error": str(e),
                "raw_text": text_preview
            }


# Global instance
document_processor = DocumentProcessor()

