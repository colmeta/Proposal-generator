"""
Tests for Quality & Delivery Agents and Services
Tests QA Agent, Persuasion Optimizer, Editor Agent, Email Service,
Version Control, and Document Editor.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.quality.qa_agent import QAAgent
from agents.quality.persuasion_optimizer import PersuasionOptimizerAgent
from agents.quality.editor_agent import EditorAgent
from services.email_service import EmailService
from services.version_control import VersionControlService
from services.document_editor import DocumentEditorService


class TestQAAgent(unittest.TestCase):
    """Test QA Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = QAAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertEqual(self.agent.name, "QA Agent")
        self.assertEqual(self.agent.role, "Multi-layer quality assurance and consistency verification")
        self.assertEqual(self.agent.task_type, "quality")
        self.assertEqual(self.agent.min_quality_score, 8.0)
    
    def test_perform_quality_check(self):
        """Test comprehensive quality check"""
        document = {
            "content": {
                "sections": {
                    "introduction": "This is an introduction",
                    "body": "This is the body"
                }
            }
        }
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"issues": [], "score": 9.0}'
            
            result = self.agent.perform_quality_check(document)
            
            self.assertIn("quality_acceptable", result)
            self.assertIn("overall_score", result)
            self.assertIn("checks", result)
            self.assertIn("issues", result)
    
    def test_check_structure(self):
        """Test structure check"""
        document = {
            "content": {
                "sections": {
                    "intro": "Introduction",
                    "body": "Body content"
                }
            }
        }
        
        result = self.agent._check_structure(document, None)
        
        self.assertIn("score", result)
        self.assertIn("status", result)
        self.assertIn("issues", result)
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 10)
    
    def test_check_structure_missing_sections(self):
        """Test structure check with missing sections"""
        document = {"content": {}}
        requirements = {"required_sections": ["intro", "body"]}
        
        result = self.agent._check_structure(document, requirements)
        
        self.assertIn("issues", result)
        self.assertLess(result["score"], 10)
    
    def test_check_consistency(self):
        """Test consistency check"""
        document = {
            "content": {
                "section1": "Text with consistent style",
                "section2": "More text"
            }
        }
        
        result = self.agent._check_consistency(document)
        
        self.assertIn("score", result)
        self.assertIn("issues", result)
    
    def test_check_errors(self):
        """Test error check"""
        document = {
            "content": {
                "text": "This is a test document with no obvious errors"
            }
        }
        
        result = self.agent._check_errors(document)
        
        self.assertIn("score", result)
        self.assertIn("errors", result)
    
    def test_check_completeness(self):
        """Test completeness check"""
        document = {
            "content": {
                "text": "This is a complete document with sufficient content"
            }
        }
        
        result = self.agent._check_completeness(document, None)
        
        self.assertIn("score", result)
        self.assertIn("issues", result)
    
    def test_check_clarity(self):
        """Test clarity check"""
        document = {
            "content": {
                "text": "This is a clear and readable document"
            }
        }
        
        result = self.agent._check_clarity(document)
        
        self.assertIn("score", result)
        self.assertIn("issues", result)
    
    def test_process(self):
        """Test process method"""
        input_data = {
            "document": {"content": {"text": "Test"}},
            "requirements": {}
        }
        
        with patch.object(self.agent, 'perform_quality_check') as mock_check:
            mock_check.return_value = {"quality_acceptable": True}
            
            result = self.agent.process(input_data)
            
            mock_check.assert_called_once()
            self.assertIn("quality_acceptable", result)


class TestPersuasionOptimizerAgent(unittest.TestCase):
    """Test Persuasion Optimizer Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = PersuasionOptimizerAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertEqual(self.agent.name, "Persuasion Optimizer")
        self.assertEqual(self.agent.role, "Maximize win probability through optimized messaging and persuasion")
        self.assertEqual(self.agent.task_type, "strategy")
    
    def test_optimize_messaging(self):
        """Test messaging optimization"""
        proposal = {"content": {"title": "Test Proposal"}}
        target_audience = {"segment": "Businesses"}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"optimized_messaging": {}, "improvements": []}'
            
            result = self.agent.optimize_messaging(proposal, target_audience)
            
            self.assertIn("optimized_messaging", result)
            mock_llm.assert_called_once()
    
    def test_suggest_ab_tests(self):
        """Test A/B test suggestions"""
        proposal = {"content": {"title": "Test"}}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"ab_tests": []}'
            
            result = self.agent.suggest_ab_tests(proposal)
            
            self.assertIn("ab_tests", result)
            mock_llm.assert_called_once()
    
    def test_apply_persuasion_techniques(self):
        """Test applying persuasion techniques"""
        proposal = {"content": {"text": "Test proposal"}}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"applied_techniques": []}'
            
            result = self.agent.apply_persuasion_techniques(proposal)
            
            self.assertIn("applied_techniques", result)
            mock_llm.assert_called_once()
    
    def test_maximize_win_probability(self):
        """Test comprehensive win probability maximization"""
        proposal = {"content": {}}
        requirements = {}
        competitive_context = {}
        target_audience = {}
        
        with patch.object(self.agent, 'optimize_messaging') as mock_opt, \
             patch.object(self.agent, 'apply_persuasion_techniques') as mock_pers, \
             patch.object(self.agent, 'suggest_ab_tests') as mock_ab, \
             patch.object(self.agent, '_assess_win_probability') as mock_assess:
            
            mock_opt.return_value = {}
            mock_pers.return_value = {}
            mock_ab.return_value = {}
            mock_assess.return_value = {"probability_percent": 75}
            
            result = self.agent.maximize_win_probability(
                proposal, requirements, competitive_context, target_audience
            )
            
            self.assertIn("win_probability", result)
            self.assertIn("messaging_optimization", result)
    
    def test_process(self):
        """Test process method"""
        input_data = {
            "action": "optimize_messaging",
            "proposal": {},
            "target_audience": {}
        }
        
        with patch.object(self.agent, 'optimize_messaging') as mock_opt:
            mock_opt.return_value = {}
            
            result = self.agent.process(input_data)
            
            mock_opt.assert_called_once()


class TestEditorAgent(unittest.TestCase):
    """Test Editor Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = EditorAgent()
    
    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        self.assertEqual(self.agent.name, "Editor Agent")
        self.assertEqual(self.agent.role, "Final polish, grammar, style, and professional editing")
        self.assertEqual(self.agent.task_type, "quality")
    
    def test_edit_document_comprehensive(self):
        """Test comprehensive document editing"""
        document = {"content": {"text": "Test document"}}
        
        with patch.object(self.agent, '_comprehensive_edit') as mock_edit:
            mock_edit.return_value = {"edited_document": {}, "changes": {}}
            
            result = self.agent.edit_document(document, "comprehensive")
            
            mock_edit.assert_called_once()
            self.assertIn("edited_document", result)
    
    def test_check_grammar(self):
        """Test grammar check"""
        document = {"content": {"text": "This is a test document."}}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"issues": [], "changes": []}'
            
            result = self.agent.check_grammar(document)
            
            self.assertIn("issues", result)
            self.assertIn("changes", result)
            mock_llm.assert_called_once()
    
    def test_check_style(self):
        """Test style check"""
        document = {"content": {"text": "Test text"}}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"improvements": [], "changes": []}'
            
            result = self.agent.check_style(document)
            
            self.assertIn("improvements", result)
            mock_llm.assert_called_once()
    
    def test_check_consistency(self):
        """Test consistency check"""
        document = {"content": {"text": "Test"}}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"fixes": [], "changes": []}'
            
            result = self.agent.check_consistency(document)
            
            self.assertIn("fixes", result)
            mock_llm.assert_called_once()
    
    def test_apply_final_polish(self):
        """Test final polish"""
        document = {"content": {"text": "Test"}}
        
        with patch.object(self.agent, 'call_llm') as mock_llm:
            mock_llm.return_value = '{"polished_content": "Test", "changes": []}'
            
            result = self.agent.apply_final_polish(document)
            
            self.assertIn("polished_content", result)
            mock_llm.assert_called_once()
    
    def test_process(self):
        """Test process method"""
        input_data = {
            "document": {"content": {}},
            "edit_type": "grammar"
        }
        
        with patch.object(self.agent, 'edit_document') as mock_edit:
            mock_edit.return_value = {}
            
            result = self.agent.process(input_data)
            
            mock_edit.assert_called_once()


class TestEmailService(unittest.TestCase):
    """Test Email Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = EmailService()
    
    def test_service_initialization(self):
        """Test service initializes correctly"""
        self.assertIsNotNone(self.service.from_email)
        self.assertIsNotNone(self.service.smtp_host)
    
    def test_send_email_no_service(self):
        """Test send email when no service available"""
        with patch.object(self.service, 'sendgrid_client', None):
            # Mock SMTP as unavailable
            import sys
            original_smtp = sys.modules.get('smtplib')
            sys.modules['smtplib'] = None
            
            result = self.service.send_email(
                "test@example.com",
                "Test",
                "Test content"
            )
            
            # Restore
            if original_smtp:
                sys.modules['smtplib'] = original_smtp
            
            self.assertIn("success", result)
    
    def test_send_template_email(self):
        """Test template email sending"""
        with patch.object(self.service, 'send_email') as mock_send:
            mock_send.return_value = {"success": True}
            
            result = self.service.send_template_email(
                "test@example.com",
                "proposal_ready",
                {"project_name": "Test Project"}
            )
            
            mock_send.assert_called_once()
            self.assertIn("success", result)
    
    def test_send_proposal_ready_email(self):
        """Test proposal ready email"""
        with patch.object(self.service, 'send_template_email') as mock_template:
            mock_template.return_value = {"success": True}
            
            result = self.service.send_proposal_ready_email(
                "test@example.com",
                "Test Project"
            )
            
            mock_template.assert_called_once()
    
    def test_send_status_update_email(self):
        """Test status update email"""
        with patch.object(self.service, 'send_template_email') as mock_template:
            mock_template.return_value = {"success": True}
            
            result = self.service.send_status_update_email(
                "test@example.com",
                "Test Project",
                "In Progress",
                "Working on it"
            )
            
            mock_template.assert_called_once()
    
    def test_get_delivery_status(self):
        """Test delivery status retrieval"""
        result = self.service.get_delivery_status()
        
        self.assertIn("total_sent", result)


class TestVersionControlService(unittest.TestCase):
    """Test Version Control Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.service = VersionControlService(storage_path=self.temp_dir)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_version(self):
        """Test version creation"""
        content = {"text": "Test content"}
        
        result = self.service.create_version(
            "doc1",
            content,
            created_by="test_user"
        )
        
        self.assertIn("document_id", result)
        self.assertIn("version_number", result)
        self.assertEqual(result["version_number"], 1)
    
    def test_get_version(self):
        """Test get version"""
        content = {"text": "Test"}
        self.service.create_version("doc1", content)
        
        version = self.service.get_version("doc1", 1)
        
        self.assertIsNotNone(version)
        self.assertEqual(version["version_number"], 1)
        self.assertEqual(version["content"], content)
    
    def test_get_latest_version(self):
        """Test get latest version"""
        self.service.create_version("doc1", {"text": "V1"})
        self.service.create_version("doc1", {"text": "V2"})
        
        latest = self.service.get_latest_version("doc1")
        
        self.assertIsNotNone(latest)
        self.assertEqual(latest["version_number"], 2)
    
    def test_get_version_history(self):
        """Test version history"""
        self.service.create_version("doc1", {"text": "V1"})
        self.service.create_version("doc1", {"text": "V2"})
        self.service.create_version("doc1", {"text": "V3"})
        
        history = self.service.get_version_history("doc1")
        
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]["version_number"], 3)  # Latest first
    
    def test_compare_versions(self):
        """Test version comparison"""
        self.service.create_version("doc1", {"text": "Version 1"})
        self.service.create_version("doc1", {"text": "Version 2"})
        
        comparison = self.service.compare_versions("doc1", 1, 2)
        
        self.assertIn("changes", comparison)
        self.assertIn("summary", comparison)
    
    def test_rollback_to_version(self):
        """Test rollback to version"""
        self.service.create_version("doc1", {"text": "V1"})
        self.service.create_version("doc1", {"text": "V2"})
        
        result = self.service.rollback_to_version("doc1", 1)
        
        self.assertTrue(result["success"])
        self.assertIn("new_version", result)
        
        # Check that new version has V1 content
        new_version = self.service.get_version("doc1", result["new_version"])
        self.assertEqual(new_version["content"]["text"], "V1")


class TestDocumentEditorService(unittest.TestCase):
    """Test Document Editor Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = DocumentEditorService()
    
    def test_track_edit(self):
        """Test edit tracking"""
        edit = {
            "type": "replace",
            "section": "intro",
            "old": "Old text",
            "new": "New text"
        }
        
        result = self.service.track_edit("doc1", edit, "editor1")
        
        self.assertIn("edit_id", result)
        self.assertEqual(result["document_id"], "doc1")
    
    def test_get_edit_history(self):
        """Test get edit history"""
        self.service.track_edit("doc1", {"type": "replace", "section": "a", "old": "1", "new": "2"})
        self.service.track_edit("doc1", {"type": "replace", "section": "b", "old": "3", "new": "4"})
        
        history = self.service.get_edit_history("doc1")
        
        self.assertEqual(len(history), 2)
    
    def test_generate_diff(self):
        """Test diff generation"""
        old_text = "This is old text"
        new_text = "This is new text"
        
        result = self.service.generate_diff(old_text, new_text)
        
        self.assertIn("diff", result)
        self.assertIn("changes", result)
    
    def test_generate_json_diff(self):
        """Test JSON diff generation"""
        old_content = {"a": 1, "b": 2}
        new_content = {"a": 1, "b": 3, "c": 4}
        
        result = self.service.generate_json_diff(old_content, new_content)
        
        self.assertIn("changes", result)
        self.assertIn("summary", result)
        self.assertEqual(result["summary"]["modified"], 1)
        self.assertEqual(result["summary"]["added"], 1)
    
    def test_merge_changes(self):
        """Test change merging"""
        base = {"section1": "Original", "section2": "Original2"}
        changes = [
            {
                "edit": {
                    "type": "replace",
                    "section": "section1",
                    "old": "Original",
                    "new": "Modified"
                }
            }
        ]
        
        result = self.service.merge_changes(base, changes)
        
        self.assertIn("merged_content", result)
        self.assertEqual(result["merged_content"]["section1"], "Modified")
    
    def test_apply_edit(self):
        """Test apply single edit"""
        content = {"section1": "Original"}
        edit = {
            "type": "replace",
            "section": "section1",
            "new": "Modified"
        }
        
        result = self.service.apply_edit(content, edit)
        
        self.assertEqual(result["section1"], "Modified")


if __name__ == '__main__':
    unittest.main()

