# API Endpoints Reference

Complete reference for all API endpoints.

## Proposals

### List Proposals

```http
GET /api/proposals
```

**Query Parameters:**
- `limit` (integer, optional): Number of items per page (default: 50, max: 100)
- `offset` (integer, optional): Number of items to skip (default: 0)
- `status` (string, optional): Filter by status
- `sort` (string, optional): Field to sort by
- `order` (string, optional): Sort order (`asc` or `desc`)

**Response:**
```json
{
  "proposals": [
    {
      "id": "prop_123",
      "title": "AI Research Proposal",
      "status": "completed",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T11:00:00Z"
    }
  ],
  "pagination": {
    "total": 100,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

### Create Proposal

```http
POST /api/proposals
```

**Request Body:**
```json
{
  "title": "AI Research Proposal",
  "funder_name": "National Science Foundation",
  "proposal_type": "Research Grant",
  "deadline": "2024-06-01",
  "budget": 50000,
  "project_description": "Description...",
  "objectives": ["Objective 1", "Objective 2"],
  "principal_investigator": "Dr. Jane Smith",
  "pi_email": "jane@example.com",
  "pi_affiliation": "University of Example"
}
```

**Response:**
```json
{
  "id": "prop_123",
  "title": "AI Research Proposal",
  "status": "draft",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Proposal

```http
GET /api/proposals/{id}
```

**Response:**
```json
{
  "id": "prop_123",
  "title": "AI Research Proposal",
  "funder_name": "National Science Foundation",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "data": {
    // Full proposal data
  }
}
```

### Update Proposal

```http
PUT /api/proposals/{id}
```

**Request Body:** (same as create, partial updates allowed)

**Response:**
```json
{
  "id": "prop_123",
  "title": "Updated Title",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

### Delete Proposal

```http
DELETE /api/proposals/{id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Proposal deleted"
}
```

## Jobs

### List Jobs

```http
GET /api/jobs
```

**Query Parameters:**
- `proposal_id` (string, optional): Filter by proposal ID
- `status` (string, optional): Filter by status
- `limit` (integer, optional): Number of items per page

**Response:**
```json
{
  "jobs": [
    {
      "id": "job_123",
      "proposal_id": "prop_123",
      "status": "completed",
      "progress": {
        "completed": 10,
        "total": 10
      },
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Create Job

```http
POST /api/proposals/{proposal_id}/jobs
```

**Request Body:**
```json
{
  "options": {
    "quality_threshold": 0.7,
    "auto_revision": true
  }
}
```

**Response:**
```json
{
  "id": "job_123",
  "proposal_id": "prop_123",
  "status": "pending",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Job

```http
GET /api/jobs/{id}
```

**Response:**
```json
{
  "id": "job_123",
  "proposal_id": "prop_123",
  "status": "processing",
  "progress": {
    "completed": 5,
    "total": 10
  },
  "tasks": [
    {
      "name": "Research Funder",
      "status": "completed"
    },
    {
      "name": "Generate Content",
      "status": "processing"
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### Get Job Status

```http
GET /api/jobs/{id}/status
```

**Response:**
```json
{
  "id": "job_123",
  "status": "processing",
  "progress": {
    "completed": 5,
    "total": 10,
    "percentage": 50
  },
  "current_task": "Generate Content",
  "estimated_completion": "2024-01-15T10:40:00Z"
}
```

### Cancel Job

```http
DELETE /api/jobs/{id}
```

**Response:**
```json
{
  "status": "success",
  "message": "Job cancelled"
}
```

## Documents

### List Documents

```http
GET /api/documents
```

**Query Parameters:**
- `proposal_id` (string, optional): Filter by proposal ID
- `limit` (integer, optional): Number of items per page

**Response:**
```json
{
  "documents": [
    {
      "id": "doc_123",
      "proposal_id": "prop_123",
      "title": "AI Research Proposal",
      "document_type": "proposal",
      "version": 1,
      "file_size": 102400,
      "created_at": "2024-01-15T11:00:00Z"
    }
  ]
}
```

### Get Document

```http
GET /api/documents/{id}
```

**Response:**
```json
{
  "id": "doc_123",
  "proposal_id": "prop_123",
  "title": "AI Research Proposal",
  "document_type": "proposal",
  "version": 1,
  "file_size": 102400,
  "content": "Document content...",
  "metadata": {
    "pages": 10,
    "word_count": 5000
  },
  "created_at": "2024-01-15T11:00:00Z"
}
```

### Download Document

```http
GET /api/documents/{id}/download
```

**Query Parameters:**
- `format` (string, optional): Document format (`pdf` or `docx`, default: `pdf`)

**Response:**
Binary file (PDF or DOCX)

**Headers:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="proposal.pdf"
```

## Settings

### Get Settings

```http
GET /api/settings
```

**Response:**
```json
{
  "llm": {
    "provider": "OpenAI",
    "model": "gpt-4",
    "temperature": 0.7
  },
  "api_keys": {
    "openai": "***"
  },
  "quality": {
    "min_quality_score": 0.7
  }
}
```

### Update Settings

```http
PUT /api/settings
```

**Request Body:**
```json
{
  "llm": {
    "provider": "OpenAI",
    "model": "gpt-4",
    "temperature": 0.7
  },
  "quality": {
    "min_quality_score": 0.8
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Settings updated"
}
```

## Health

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Responses

All endpoints may return error responses. See [Error Codes](error_codes.md) for details.

**Error Response Format:**
```json
{
  "status": "error",
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    // Additional error details
  }
}
```

## Rate Limiting

All endpoints are subject to rate limiting. See [Rate Limiting Guide](rate_limiting.md) for details.

## Next Steps

- Review [API Overview](api_overview.md)
- Check [Authentication Guide](authentication.md)
- See [Error Codes](error_codes.md)


