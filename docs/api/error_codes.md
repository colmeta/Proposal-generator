# Error Codes Reference

Complete reference for all API error codes.

## Error Response Format

All errors follow this format:

```json
{
  "status": "error",
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    // Additional error details
  }
}
```

## HTTP Status Codes

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

## Error Codes

### Authentication Errors

#### `AUTH_REQUIRED`
- **Status**: 401
- **Message**: "Authentication required"
- **Cause**: Missing or invalid authentication token
- **Solution**: Include valid Bearer token in Authorization header

#### `AUTH_INVALID`
- **Status**: 401
- **Message**: "Invalid authentication token"
- **Cause**: Token is invalid or expired
- **Solution**: Refresh token or re-authenticate

#### `AUTH_EXPIRED`
- **Status**: 401
- **Message**: "Authentication token expired"
- **Cause**: Token has expired
- **Solution**: Use refresh token to get new access token

#### `AUTH_INSUFFICIENT_PERMISSIONS`
- **Status**: 403
- **Message**: "Insufficient permissions"
- **Cause**: Token valid but lacks required permissions
- **Solution**: Use account with appropriate permissions

### Validation Errors

#### `VALIDATION_ERROR`
- **Status**: 422
- **Message**: "Validation error"
- **Cause**: Request data fails validation
- **Solution**: Check error details and fix invalid fields

#### `MISSING_REQUIRED_FIELD`
- **Status**: 422
- **Message**: "Missing required field: {field}"
- **Cause**: Required field is missing
- **Solution**: Include all required fields

#### `INVALID_FIELD_VALUE`
- **Status**: 422
- **Message**: "Invalid value for field: {field}"
- **Cause**: Field value is invalid
- **Solution**: Use valid value for field

#### `INVALID_EMAIL`
- **Status**: 422
- **Message**: "Invalid email address"
- **Cause**: Email format is invalid
- **Solution**: Use valid email format

#### `INVALID_URL`
- **Status**: 422
- **Message**: "Invalid URL"
- **Cause**: URL format is invalid
- **Solution**: Use valid URL format

### Resource Errors

#### `RESOURCE_NOT_FOUND`
- **Status**: 404
- **Message**: "Resource not found"
- **Cause**: Requested resource doesn't exist
- **Solution**: Verify resource ID and existence

#### `PROPOSAL_NOT_FOUND`
- **Status**: 404
- **Message**: "Proposal not found"
- **Cause**: Proposal ID doesn't exist
- **Solution**: Verify proposal ID

#### `JOB_NOT_FOUND`
- **Status**: 404
- **Message**: "Job not found"
- **Cause**: Job ID doesn't exist
- **Solution**: Verify job ID

#### `DOCUMENT_NOT_FOUND`
- **Status**: 404
- **Message**: "Document not found"
- **Cause**: Document ID doesn't exist
- **Solution**: Verify document ID

#### `RESOURCE_CONFLICT`
- **Status**: 409
- **Message**: "Resource conflict"
- **Cause**: Resource already exists or conflicts
- **Solution**: Use different identifier or update existing resource

### Rate Limiting Errors

#### `RATE_LIMIT_EXCEEDED`
- **Status**: 429
- **Message**: "Rate limit exceeded"
- **Cause**: Too many requests in time window
- **Solution**: Wait for rate limit reset or reduce request frequency

#### `RATE_LIMIT_TOO_MANY_REQUESTS`
- **Status**: 429
- **Message**: "Too many requests"
- **Cause**: Exceeded rate limit
- **Solution**: Implement exponential backoff and retry

### Processing Errors

#### `JOB_FAILED`
- **Status**: 500
- **Message**: "Job processing failed"
- **Cause**: Error during job processing
- **Solution**: Check job details and error logs, retry if appropriate

#### `GENERATION_FAILED`
- **Status**: 500
- **Message**: "Document generation failed"
- **Cause**: Error generating document
- **Solution**: Check input data and retry

#### `LLM_ERROR`
- **Status**: 500
- **Message**: "LLM provider error"
- **Cause**: Error from LLM provider
- **Solution**: Check LLM configuration and API keys

#### `API_KEY_INVALID`
- **Status**: 500
- **Message**: "Invalid API key"
- **Cause**: LLM API key is invalid
- **Solution**: Verify and update API key in settings

#### `API_KEY_QUOTA_EXCEEDED`
- **Status**: 500
- **Message**: "API key quota exceeded"
- **Cause**: LLM API quota exceeded
- **Solution**: Check API usage and upgrade plan if needed

### Server Errors

#### `INTERNAL_SERVER_ERROR`
- **Status**: 500
- **Message**: "Internal server error"
- **Cause**: Unexpected server error
- **Solution**: Retry request, contact support if persistent

#### `SERVICE_UNAVAILABLE`
- **Status**: 503
- **Message**: "Service temporarily unavailable"
- **Cause**: Service is down or overloaded
- **Solution**: Retry after delay, check status page

#### `DATABASE_ERROR`
- **Status**: 500
- **Message**: "Database error"
- **Cause**: Database operation failed
- **Solution**: Retry request, contact support if persistent

#### `STORAGE_ERROR`
- **Status**: 500
- **Message**: "Storage error"
- **Cause**: File storage operation failed
- **Solution**: Check storage configuration, retry request

### Configuration Errors

#### `SETTINGS_INVALID`
- **Status**: 422
- **Message**: "Invalid settings"
- **Cause**: Settings configuration is invalid
- **Solution**: Review and fix settings

#### `LLM_CONFIG_INVALID`
- **Status**: 422
- **Message**: "Invalid LLM configuration"
- **Cause**: LLM provider or model configuration is invalid
- **Solution**: Verify LLM settings

## Handling Errors

### Error Handling Example

```python
import requests

try:
    response = requests.get("http://localhost:5000/api/proposals/123", headers=headers)
    response.raise_for_status()
    proposal = response.json()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print("Proposal not found")
    elif e.response.status_code == 401:
        print("Authentication required")
    elif e.response.status_code == 429:
        retry_after = e.response.json().get('retry_after', 60)
        print(f"Rate limited. Retry after {retry_after} seconds")
    else:
        error_data = e.response.json()
        print(f"Error: {error_data.get('error')} ({error_data.get('code')})")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### Retry Logic

```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retry():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST", "PUT", "DELETE"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

session = create_session_with_retry()
response = session.get("http://localhost:5000/api/proposals", headers=headers)
```

## Error Details

Some errors include additional details:

```json
{
  "status": "error",
  "error": "Validation error",
  "code": "VALIDATION_ERROR",
  "details": {
    "fields": {
      "email": "Invalid email format",
      "budget": "Must be a positive number"
    }
  }
}
```

## Best Practices

1. **Check Status Codes**: Always check HTTP status codes
2. **Read Error Messages**: Error messages provide helpful information
3. **Handle Specific Errors**: Handle common errors specifically
4. **Implement Retry Logic**: Retry transient errors
5. **Log Errors**: Log errors for debugging
6. **User-Friendly Messages**: Show user-friendly error messages

## Next Steps

- Review [API Overview](api_overview.md)
- Check [Authentication Guide](authentication.md)
- See [Rate Limiting Guide](rate_limiting.md)



