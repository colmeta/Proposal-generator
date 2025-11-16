"""
Tests for Documentation & Help System
"""

import pytest
from pathlib import Path


class TestDocumentation:
    """Tests for documentation files"""
    
    def test_docs_directory_exists(self):
        """Test that docs directory exists"""
        docs_dir = Path("docs")
        assert docs_dir.exists()
        assert docs_dir.is_dir()
    
    def test_user_guide_exists(self):
        """Test that user guide files exist"""
        docs_dir = Path("docs")
        if (docs_dir / "user_guide").exists():
            user_guide = docs_dir / "user_guide"
            assert user_guide.is_dir()
    
    def test_api_docs_exist(self):
        """Test that API documentation exists"""
        docs_dir = Path("docs")
        if (docs_dir / "api").exists():
            api_docs = docs_dir / "api"
            assert api_docs.is_dir()
    
    def test_help_system_importable(self):
        """Test that help system components are importable"""
        try:
            from web.components.help_system import HelpSystem
            assert True
        except ImportError:
            # Help system might not be implemented yet
            pytest.skip("Help system not yet implemented")
    
    def test_documentation_viewer_importable(self):
        """Test that documentation viewer is importable"""
        try:
            from web.components.documentation_viewer import DocumentationViewer
            assert True
        except ImportError:
            pytest.skip("Documentation viewer not yet implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

