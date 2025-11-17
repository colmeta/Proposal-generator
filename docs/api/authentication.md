# Authentication Guide

The Proposal Generator API uses JWT (JSON Web Tokens) for authentication.

## Overview

Authentication is required for most API endpoints. Unauthenticated requests are limited and may have restricted access.

## Getting an API Token

### Option 1: User Registration/Login

1. Register a new account or login
2. Obtain JWT token from login response
3. Use token in subsequent requests

### Option 2: API Key

1. Generate API key in settings
2. Use API key as Bearer token
3. Key has same permissions as user account

## Using Authentication

### Header Format

Include the token in the Authorization header:

```
Authorization: Bearer <your_token>
```

### Example Request

```bash
curl -X GET "http://localhost:5000/api/proposals" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Python Example

```python
import requests

headers = {
    "Authorization": "Bearer <your_token>",
    "Content-Type": "application/json"
}

response = requests.get("http://localhost:5000/api/proposals", headers=headers)
```

### JavaScript Example

```javascript
const response = await fetch('http://localhost:5000/api/proposals', {
  headers: {
    'Authorization': 'Bearer <your_token>',
    'Content-Type': 'application/json'
  }
});
```

## Token Lifecycle

### Token Expiration

- **Access Token**: Expires after 24 hours
- **Refresh Token**: Expires after 30 days

### Refreshing Tokens

When access token expires, use refresh token to get new access token:

```bash
POST /api/auth/refresh
{
  "refresh_token": "<refresh_token>"
}
```

Response:
```json
{
  "access_token": "<new_access_token>",
  "refresh_token": "<new_refresh_token>"
}
```

## Authentication Endpoints

### Login

```bash
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "password"
}
```

Response:
```json
{
  "access_token": "<access_token>",
  "refresh_token": "<refresh_token>",
  "expires_in": 86400
}
```

### Register

```bash
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "password",
  "name": "User Name"
}
```

Response:
```json
{
  "access_token": "<access_token>",
  "refresh_token": "<refresh_token>",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "name": "User Name"
  }
}
```

### Logout

```bash
POST /api/auth/logout
Authorization: Bearer <token>
```

### Verify Token

```bash
GET /api/auth/verify
Authorization: Bearer <token>
```

Response:
```json
{
  "valid": true,
  "user": {
    "id": "user_id",
    "email": "user@example.com"
  }
}
```

## Error Responses

### 401 Unauthorized

Token missing or invalid:

```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing token"
}
```

### 403 Forbidden

Token valid but insufficient permissions:

```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

## Security Best Practices

### Token Storage

- **Web Applications**: Store in httpOnly cookies
- **Mobile Apps**: Use secure storage
- **CLI Tools**: Store in secure keychain
- **Never**: Commit tokens to version control

### Token Transmission

- **Always**: Use HTTPS in production
- **Never**: Send tokens in URL parameters
- **Always**: Use Authorization header
- **Never**: Log tokens

### Token Rotation

- **Regular**: Rotate tokens periodically
- **Compromised**: Immediately revoke if compromised
- **Expired**: Use refresh tokens to renew

## API Keys

### Generating API Keys

1. Navigate to Settings > API Keys
2. Click "Generate New Key"
3. Copy and store key securely
4. Key is shown only once

### Using API Keys

Use API key as Bearer token:

```
Authorization: Bearer <api_key>
```

### Revoking API Keys

1. Navigate to Settings > API Keys
2. Find key to revoke
3. Click "Revoke"
4. Key is immediately invalidated

## OAuth (Future)

OAuth 2.0 support is planned for future releases:
- Google OAuth
- GitHub OAuth
- Microsoft OAuth

## Troubleshooting

### Token Not Working

1. **Check Format**: Ensure "Bearer " prefix
2. **Verify Token**: Check token is valid
3. **Check Expiration**: Token may be expired
4. **Refresh Token**: Use refresh token to get new token

### Authentication Errors

1. **401 Unauthorized**: Token missing or invalid
2. **403 Forbidden**: Insufficient permissions
3. **429 Too Many Requests**: Too many auth attempts

### Getting Help

- Check token format
- Verify token expiration
- Review error messages
- Contact support if needed

## Examples

### Complete Authentication Flow

```python
import requests

# Login
login_response = requests.post("http://localhost:5000/api/auth/login", json={
    "email": "user@example.com",
    "password": "password"
})

token = login_response.json()["access_token"]

# Use token for authenticated requests
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Make authenticated request
response = requests.get("http://localhost:5000/api/proposals", headers=headers)
proposals = response.json()
```

## Next Steps

- Review [API Overview](api_overview.md)
- Check [Endpoints Documentation](endpoints.md)
- See [Error Codes](error_codes.md)


