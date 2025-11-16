"""
SQLAlchemy database models
Defines Project, Document, DocumentVersion, and Job models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, Optional

Base = declarative_base()


class Project(Base):
    """
    Project model - represents a proposal project
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    funder_name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), default="draft", index=True)  # draft, in_progress, completed, cancelled
    user_email = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_project_status", "status"),
        Index("idx_project_user", "user_email"),
        Index("idx_project_funder", "funder_name"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "funder_name": self.funder_name,
            "status": self.status,
            "user_email": self.user_email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"


class Document(Base):
    """
    Document model - represents a proposal document
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(JSON, nullable=False)  # Document content as JSON
    version_number = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_document_project", "project_id"),
        Index("idx_document_version", "project_id", "version_number"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "content": self.content,
            "version_number": self.version_number,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<Document(id={self.id}, project_id={self.project_id}, version={self.version_number})>"


class DocumentVersion(Base):
    """
    DocumentVersion model - tracks document version history
    """
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    content = Column(JSON, nullable=False)  # Document content at this version
    changes = Column(JSON, nullable=True)  # Changes made in this version
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=True)  # Agent or user who created this version
    
    # Relationships
    document = relationship("Document", back_populates="versions")
    
    # Indexes
    __table_args__ = (
        Index("idx_version_document", "document_id"),
        Index("idx_version_number", "document_id", "version_number"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "version_number": self.version_number,
            "content": self.content,
            "changes": self.changes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
        }
    
    def __repr__(self):
        return f"<DocumentVersion(id={self.id}, document_id={self.document_id}, version={self.version_number})>"


class Job(Base):
    """
    Job model - tracks background tasks and agent operations
    """
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type = Column(String(100), nullable=False, index=True)  # e.g., "research", "writing", "review"
    status = Column(String(50), default="pending", nullable=False, index=True)  # pending, running, completed, failed, cancelled
    result = Column(JSON, nullable=True)  # Task result data
    error = Column(Text, nullable=True)  # Error message if failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="jobs")
    
    # Indexes
    __table_args__ = (
        Index("idx_job_project", "project_id"),
        Index("idx_job_status", "status"),
        Index("idx_job_type", "task_type"),
        Index("idx_job_project_status", "project_id", "status"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "task_type": self.task_type,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
    
    def mark_completed(self, result: Optional[Dict[str, Any]] = None):
        """Mark job as completed"""
        self.status = "completed"
        self.result = result
        self.completed_at = datetime.utcnow()
    
    def mark_failed(self, error: str):
        """Mark job as failed"""
        self.status = "failed"
        self.error = error
        self.completed_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<Job(id={self.id}, project_id={self.project_id}, task_type='{self.task_type}', status='{self.status}')>"

