"""
Tests for database models and storage service
"""

import pytest
import os
import tempfile
import shutil
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.db import init_db, get_session, SessionLocal
from database.models import Project, Document, DocumentVersion, Job, Base
from services.storage import StorageService


@pytest.fixture
def db_session():
    """Create a test database session"""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    engine.dispose()


@pytest.fixture
def temp_storage():
    """Create a temporary storage directory"""
    temp_dir = tempfile.mkdtemp()
    storage = StorageService(base_path=temp_dir)
    
    yield storage
    
    shutil.rmtree(temp_dir)


class TestProject:
    """Test Project model"""
    
    def test_create_project(self, db_session):
        """Test creating a project"""
        project = Project(
            name="Test Project",
            funder_name="Test Funder",
            user_email="test@example.com",
            status="draft"
        )
        db_session.add(project)
        db_session.commit()
        
        assert project.id is not None
        assert project.name == "Test Project"
        assert project.funder_name == "Test Funder"
        assert project.status == "draft"
        assert project.created_at is not None
    
    def test_project_to_dict(self, db_session):
        """Test project to_dict method"""
        project = Project(
            name="Test Project",
            funder_name="Test Funder",
            user_email="test@example.com"
        )
        db_session.add(project)
        db_session.commit()
        
        project_dict = project.to_dict()
        assert project_dict["name"] == "Test Project"
        assert project_dict["id"] == project.id
        assert "created_at" in project_dict


class TestDocument:
    """Test Document model"""
    
    def test_create_document(self, db_session):
        """Test creating a document"""
        project = Project(
            name="Test Project",
            funder_name="Test Funder",
            user_email="test@example.com"
        )
        db_session.add(project)
        db_session.commit()
        
        document = Document(
            project_id=project.id,
            content={"title": "Test Document", "sections": []},
            version_number=1
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.id is not None
        assert document.project_id == project.id
        assert document.version_number == 1
        assert document.content == {"title": "Test Document", "sections": []}
    
    def test_document_relationship(self, db_session):
        """Test document-project relationship"""
        project = Project(
            name="Test Project",
            funder_name="Test Funder",
            user_email="test@example.com"
        )
        db_session.add(project)
        db_session.commit()
        
        document = Document(
            project_id=project.id,
            content={"title": "Test"},
            version_number=1
        )
        db_session.add(document)
        db_session.commit()
        
        assert document.project.id == project.id
        assert document in project.documents


class TestDocumentVersion:
    """Test DocumentVersion model"""
    
    def test_create_document_version(self, db_session):
        """Test creating a document version"""
        project = Project(
            name="Test Project",
            funder_name="Test Funder",
            user_email="test@example.com"
        )
        db_session.add(project)
        db_session.commit()
        
        document = Document(
            project_id=project.id,
            content={"title": "Test"},
            version_number=1
        )
        db_session.add(document)
        db_session.commit()
        
        version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            content={"title": "Test"},
            changes={"added": ["section1"]},
            created_by="test_agent"
        )
        db_session.add(version)
        db_session.commit()
        
        assert version.id is not None
        assert version.document_id == document.id
        assert version.created_by == "test_agent"
        assert version.changes == {"added": ["section1"]}


class TestJob:
    """Test Job model"""
    
    def test_create_job(self, db_session):
        """Test creating a job"""
        project = Project(
            name="Test Project",
            funder_name="Test Funder",
            user_email="test@example.com"
        )
        db_session.add(project)
        db_session.commit()
        
        job = Job(
            project_id=project.id,
            task_type="research",
            status="pending"
        )
        db_session.add(job)
        db_session.commit()
        
        assert job.id is not None
        assert job.task_type == "research"
        assert job.status == "pending"
        assert job.created_at is not None
    
    def test_job_mark_completed(self, db_session):
        """Test marking job as completed"""
        project = Project(
            name="Test Project",
            funder_name="Test Funder",
            user_email="test@example.com"
        )
        db_session.add(project)
        db_session.commit()
        
        job = Job(
            project_id=project.id,
            task_type="research",
            status="pending"
        )
        db_session.add(job)
        db_session.commit()
        
        job.mark_completed({"result": "success"})
        db_session.commit()
        
        assert job.status == "completed"
        assert job.result == {"result": "success"}
        assert job.completed_at is not None
    
    def test_job_mark_failed(self, db_session):
        """Test marking job as failed"""
        project = Project(
            name="Test Project",
            funder_name="Test Funder",
            user_email="test@example.com"
        )
        db_session.add(project)
        db_session.commit()
        
        job = Job(
            project_id=project.id,
            task_type="research",
            status="running"
        )
        db_session.add(job)
        db_session.commit()
        
        job.mark_failed("Test error")
        db_session.commit()
        
        assert job.status == "failed"
        assert job.error == "Test error"
        assert job.completed_at is not None


class TestStorageService:
    """Test StorageService"""
    
    def test_save_and_load_text(self, temp_storage):
        """Test saving and loading text files"""
        content = "Test content"
        file_path = "test/test.txt"
        
        temp_storage.save(file_path, content)
        assert temp_storage.exists(file_path)
        
        loaded = temp_storage.load(file_path)
        assert loaded == content
    
    def test_save_and_load_json(self, temp_storage):
        """Test saving and loading JSON files"""
        content = {"key": "value", "number": 42}
        file_path = "test/test.json"
        
        temp_storage.save(file_path, content, is_json=True)
        assert temp_storage.exists(file_path)
        
        loaded = temp_storage.load(file_path, is_json=True)
        assert loaded == content
    
    def test_save_and_load_binary(self, temp_storage):
        """Test saving and loading binary files"""
        content = b"Binary content"
        file_path = "test/test.bin"
        
        temp_storage.save(file_path, content, mode="wb")
        assert temp_storage.exists(file_path)
        
        loaded = temp_storage.load(file_path, mode="rb")
        assert loaded == content
    
    def test_delete_file(self, temp_storage):
        """Test deleting files"""
        file_path = "test/test.txt"
        temp_storage.save(file_path, "content")
        assert temp_storage.exists(file_path)
        
        result = temp_storage.delete(file_path)
        assert result is True
        assert not temp_storage.exists(file_path)
    
    def test_list_files(self, temp_storage):
        """Test listing files"""
        temp_storage.save("dir1/file1.txt", "content1")
        temp_storage.save("dir1/file2.txt", "content2")
        temp_storage.save("dir2/file3.txt", "content3")
        
        files = temp_storage.list_files()
        assert len(files) == 3
        assert "dir1/file1.txt" in files
        assert "dir2/file3.txt" in files
    
    def test_get_project_storage_path(self, temp_storage):
        """Test getting project storage path"""
        path = temp_storage.get_project_storage_path(123)
        assert path == "projects/123"
    
    def test_get_document_path(self, temp_storage):
        """Test getting document storage path"""
        path = temp_storage.get_document_path(123, 456)
        assert path == "projects/123/documents/456.json"
        
        path_with_version = temp_storage.get_document_path(123, 456, version=2)
        assert path_with_version == "projects/123/documents/456_v2.json"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

