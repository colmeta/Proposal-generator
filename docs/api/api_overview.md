# API Overview

The Proposal Generator API provides a RESTful interface for creating proposals, managing jobs, and accessing generated documents.

## Base URL

```
http://localhost:5000/api
```

For production, replace with your production API URL.

## API Version

Current version: **v1**

All endpoints are prefixed with `/api/v1` (or just `/api` for default version).

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_token>
```

See [Authentication Guide](authentication.md) for details.

## Request Format

### Content-Type

All requests should include:
```
Content-Type: application/json
```

### Request Body

JSON format for POST/PUT requests:
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

## Response Format

### Success Response

```json
{
  "status": "success",
  "data": {
    // Response data
  }
}
```

### Error Response

```json
{
  "status": "error",
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

See [Error Codes](error_codes.md) for detailed error information.

## Rate Limiting

API requests are rate-limited to prevent abuse. See [Rate Limiting Guide](rate_limiting.md) for details.

Default limits:
- **Authenticated users**: 100 requests per minute
- **Unauthenticated users**: 10 requests per minute

## Pagination

List endpoints support pagination:

```
GET /api/proposals?limit=50&offset=0
```

Parameters:
- `limit`: Number of items per page (default: 50, max: 100)
- `offset`: Number of items to skip (default: 0)

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "total": 150,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

## Filtering and Sorting

Many endpoints support filtering and sorting:

```
GET /api/proposals?status=completed&sort=created_at&order=desc
```

Common parameters:
- `status`: Filter by status
- `sort`: Field to sort by
- `order`: `asc` or `desc`

## Webhooks

Subscribe to events using webhooks. See [Webhooks Guide](webhooks.md) for details.

## SDKs and Libraries

### Python

```python
import requests

headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.get("http://localhost:5000/api/proposals", headers=headers)
```

### JavaScript/Node.js

```javascript
const fetch = require('node-fetch');

const response = await fetch('http://localhost:5000/api/proposals', {
  headers: {
    'Authorization': 'Bearer <token>',
    'Content-Type': 'application/json'
  }
});
```

### cURL

```bash
curl -X GET "http://localhost:5000/api/proposals" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"
```

## Endpoints

### Proposals
- `GET /api/proposals` - List proposals
- `POST /api/proposals` - Create proposal
- `GET /api/proposals/{id}` - Get proposal
- `PUT /api/proposals/{id}` - Update proposal
- `DELETE /api/proposals/{id}` - Delete proposal

### Jobs
- `GET /api/jobs` - List jobs
- `POST /api/proposals/{id}/jobs` - Create job
- `GET /api/jobs/{id}` - Get job
- `GET /api/jobs/{id}/status` - Get job status
- `DELETE /api/jobs/{id}` - Cancel job

### Documents
- `GET /api/documents` - List documents
- `GET /api/documents/{id}` - Get document
- `GET /api/documents/{id}/download` - Download document

### Settings
- `GET /api/settings` - Get settings
- `PUT /api/settings` - Update settings

### Health
- `GET /api/health` - Health check

See [Endpoints Documentation](endpoints.md) for detailed endpoint documentation.

## Best Practices

1. **Use HTTPS**: Always use HTTPS in production
2. **Handle Errors**: Implement proper error handling
3. **Rate Limiting**: Respect rate limits
4. **Pagination**: Use pagination for large datasets
5. **Caching**: Cache responses when appropriate
6. **Retry Logic**: Implement retry for transient errors
7. **Logging**: Log API calls for debugging

## Support

- **Documentation**: See endpoint documentation
- **Examples**: Check code examples
- **Issues**: Report on GitHub
- **Support**: Contact support team


