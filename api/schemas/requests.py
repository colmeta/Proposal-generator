"""Request schemas using Pydantic for validation"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, EmailStr, validator
from datetime import datetime
from enum import Enum


class JobCreateSchema(BaseModel):
    """Schema for creating a new job"""
    project_id: int = Field(..., description="ID of the project")
    template_id: Optional[int] = Field(None, description="ID of the template to use")
    name: str = Field(..., min_length=1, max_length=255, description="Job name")
    description: Optional[str] = Field(None, max_length=1000, description="Job description")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Job parameters")
    priority: Optional[int] = Field(1, ge=1, le=10, description="Job priority (1-10)")
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": 1,
                "template_id": 1,
                "name": "Generate Proposal",
                "description": "Generate proposal for client",
                "parameters": {"client_name": "Acme Corp"},
                "priority": 5
            }
        }


class ProjectCreateSchema(BaseModel):
    """Schema for creating a new project"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    client_name: Optional[str] = Field(None, max_length=255, description="Client name")
    client_email: Optional[EmailStr] = Field(None, description="Client email")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Q1 2024 Proposal",
                "description": "Proposal for Q1 2024",
                "client_name": "Acme Corporation",
                "client_email": "contact@acme.com",
                "metadata": {"industry": "Technology"}
            }
        }


class ProjectUpdateSchema(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    client_name: Optional[str] = Field(None, max_length=255, description="Client name")
    client_email: Optional[EmailStr] = Field(None, description="Client email")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    status: Optional[str] = Field(None, description="Project status")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Q1 2024 Proposal - Updated",
                "status": "active"
            }
        }


class DocumentCreateSchema(BaseModel):
    """Schema for creating a document"""
    project_id: int = Field(..., description="ID of the project")
    name: str = Field(..., min_length=1, max_length=255, description="Document name")
    document_type: str = Field(..., description="Type of document")
    content: Optional[str] = Field(None, description="Document content")
    template_id: Optional[int] = Field(None, description="Template ID to use")
    format: Optional[str] = Field("pdf", description="Document format (pdf, docx, etc.)")
    
    class Config:
        schema_extra = {
            "example": {
                "project_id": 1,
                "name": "Proposal Document",
                "document_type": "proposal",
                "format": "pdf"
            }
        }


class WebhookEventType(str, Enum):
    """Webhook event types"""
    JOB_CREATED = "job.created"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    JOB_UPDATED = "job.updated"
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    DOCUMENT_GENERATED = "document.generated"
    ERROR_OCCURRED = "error.occurred"


class WebhookRegisterSchema(BaseModel):
    """Schema for registering a webhook"""
    url: HttpUrl = Field(..., description="Webhook URL to receive events")
    event_types: List[WebhookEventType] = Field(..., min_items=1, description="Event types to subscribe to")
    secret: Optional[str] = Field(None, description="Secret for signature verification (auto-generated if not provided)")
    active: Optional[bool] = Field(True, description="Whether webhook is active")
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com/webhook",
                "event_types": ["job.completed", "job.failed"],
                "active": True
            }
        }


class IntegrationType(str, Enum):
    """Integration types"""
    SALESFORCE = "salesforce"
    HUBSPOT = "hubspot"
    ASANA = "asana"
    TRELLO = "trello"
    JIRA = "jira"


class IntegrationConfigSchema(BaseModel):
    """Schema for configuring an integration"""
    integration_type: IntegrationType = Field(..., description="Type of integration")
    credentials: Dict[str, str] = Field(..., description="Integration credentials")
    enabled: Optional[bool] = Field(True, description="Whether integration is enabled")
    
    class Config:
        schema_extra = {
            "example": {
                "integration_type": "salesforce",
                "credentials": {
                    "client_id": "your_client_id",
                    "client_secret": "your_client_secret",
                    "username": "your_username",
                    "password": "your_password"
                },
                "enabled": True
            }
        }


class AuthLoginSchema(BaseModel):
    """Schema for user login"""
    username: str = Field(..., min_length=1, description="Username or email")
    password: str = Field(..., min_length=1, description="Password")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "user@example.com",
                "password": "secure_password"
            }
        }


class OAuthTokenRequestSchema(BaseModel):
    """Schema for OAuth 2.0 token request"""
    grant_type: str = Field(..., description="Grant type (authorization_code, refresh_token)")
    code: Optional[str] = Field(None, description="Authorization code")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    client_id: str = Field(..., description="OAuth client ID")
    client_secret: str = Field(..., description="OAuth client secret")
    redirect_uri: Optional[HttpUrl] = Field(None, description="Redirect URI")
    
    class Config:
        schema_extra = {
            "example": {
                "grant_type": "authorization_code",
                "code": "authorization_code_here",
                "client_id": "your_client_id",
                "client_secret": "your_client_secret",
                "redirect_uri": "https://example.com/callback"
            }
        }

