"""Response schemas using Pydantic for standardized API responses"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobResponseSchema(BaseModel):
    """Schema for job response"""
    id: int = Field(..., description="Job ID")
    project_id: int = Field(..., description="Project ID")
    template_id: Optional[int] = Field(None, description="Template ID")
    name: str = Field(..., description="Job name")
    description: Optional[str] = Field(None, description="Job description")
    status: JobStatus = Field(..., description="Job status")
    priority: int = Field(..., description="Job priority")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Job parameters")
    result: Optional[Dict[str, Any]] = Field(None, description="Job result")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "project_id": 1,
                "template_id": 1,
                "name": "Generate Proposal",
                "description": "Generate proposal for client",
                "status": "completed",
                "priority": 5,
                "parameters": {"client_name": "Acme Corp"},
                "result": {"document_id": 123},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:05:00Z",
                "completed_at": "2024-01-01T00:05:00Z"
            }
        }


class ProjectResponseSchema(BaseModel):
    """Schema for project response"""
    id: int = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    client_name: Optional[str] = Field(None, description="Client name")
    client_email: Optional[str] = Field(None, description="Client email")
    status: str = Field(..., description="Project status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Q1 2024 Proposal",
                "description": "Proposal for Q1 2024",
                "client_name": "Acme Corporation",
                "client_email": "contact@acme.com",
                "status": "active",
                "metadata": {"industry": "Technology"},
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class ErrorResponseSchema(BaseModel):
    """Schema for error responses"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid input data",
                "details": {"field": "email", "issue": "Invalid email format"},
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


class SuccessResponseSchema(BaseModel):
    """Schema for success responses"""
    success: bool = Field(True, description="Success indicator")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {"id": 1},
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }


class WebhookResponseSchema(BaseModel):
    """Schema for webhook response"""
    id: int = Field(..., description="Webhook ID")
    url: str = Field(..., description="Webhook URL")
    event_types: List[str] = Field(..., description="Subscribed event types")
    active: bool = Field(..., description="Whether webhook is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "url": "https://example.com/webhook",
                "event_types": ["job.completed", "job.failed"],
                "active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }


class PaginatedResponseSchema(BaseModel):
    """Schema for paginated responses"""
    items: List[Dict[str, Any]] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    class Config:
        schema_extra = {
            "example": {
                "items": [{"id": 1, "name": "Item 1"}],
                "total": 100,
                "page": 1,
                "page_size": 10,
                "total_pages": 10
            }
        }


class AuthTokenResponseSchema(BaseModel):
    """Schema for authentication token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    token_type: str = Field("Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "expires_in": 3600
            }
        }

