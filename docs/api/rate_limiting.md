# Rate Limiting Guide

The Proposal Generator API implements rate limiting to ensure fair usage and prevent abuse.

## Overview

Rate limiting restricts the number of API requests you can make within a specific time period. Limits vary based on authentication status and user tier.

## Rate Limits

### Default Limits

- **Authenticated Users**: 100 requests per minute
- **Unauthenticated Users**: 10 requests per minute

### Per-Endpoint Limits

Some endpoints have specific limits:
- **Job Creation**: 10 requests per minute
- **Document Download**: 50 requests per minute
- **Settings Update**: 5 requests per minute

## Rate Limit Headers

All API responses include rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

- **X-RateLimit-Limit**: Maximum requests allowed
- **X-RateLimit-Remaining**: Remaining requests in current window
- **X-RateLimit-Reset**: Unix timestamp when limit resets

## Rate Limit Exceeded

When rate limit is exceeded, you receive a `429 Too Many Requests` response:

```json
{
  "status": "error",
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 60
}
```

The `retry_after` field indicates seconds to wait before retrying.

## Handling Rate Limits

### Check Headers

Monitor rate limit headers to avoid hitting limits:

```python
import requests
import time

response = requests.get("http://localhost:5000/api/proposals", headers=headers)
remaining = int(response.headers.get('X-RateLimit-Remaining', 0))

if remaining < 10:
    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
    wait_time = reset_time - time.time()
    if wait_time > 0:
        time.sleep(wait_time)
```

### Exponential Backoff

Implement exponential backoff for retries:

```python
import time
import random

def make_request_with_retry(url, headers, max_retries=5):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        
        if response.status_code == 429:
            retry_after = response.json().get('retry_after', 60)
            wait_time = retry_after + random.uniform(0, 1)
            time.sleep(wait_time)
            continue
        
        return response
    
    raise Exception("Max retries exceeded")
```

### Request Batching

Batch requests when possible to reduce API calls:

```python
# Instead of multiple requests
for proposal_id in proposal_ids:
    response = requests.get(f"/api/proposals/{proposal_id}")

# Use list endpoint with filters
response = requests.get("/api/proposals", params={
    "ids": ",".join(proposal_ids)
})
```

## Best Practices

### 1. Monitor Rate Limits

Always check rate limit headers:

```python
remaining = response.headers.get('X-RateLimit-Remaining')
if int(remaining) < 10:
    # Slow down or wait
    pass
```

### 2. Implement Caching

Cache responses to reduce API calls:

```python
from functools import lru_cache
import requests

@lru_cache(maxsize=100)
def get_proposal(proposal_id):
    return requests.get(f"/api/proposals/{proposal_id}")
```

### 3. Use Webhooks

Use webhooks instead of polling to reduce requests:

```python
# Instead of polling
while True:
    response = requests.get("/api/jobs/{id}/status")
    if response.json()['status'] == 'completed':
        break
    time.sleep(5)

# Use webhooks
# Job completion triggers webhook automatically
```

### 4. Optimize Requests

- Use pagination efficiently
- Request only needed fields
- Use filters to reduce results
- Combine related requests

## Increasing Limits

### Authentication

Authenticated users have higher limits. Always authenticate when possible.

### User Tiers

Higher tier users may have increased limits:
- **Free**: 100 requests/minute
- **Pro**: 500 requests/minute
- **Enterprise**: Custom limits

Contact support for tier upgrades.

## Rate Limit by Endpoint

### High-Limit Endpoints
- `GET /api/health`: No limit
- `GET /api/proposals`: 100/minute
- `GET /api/documents`: 100/minute

### Medium-Limit Endpoints
- `POST /api/proposals`: 20/minute
- `GET /api/jobs`: 50/minute
- `GET /api/documents/{id}/download`: 50/minute

### Low-Limit Endpoints
- `POST /api/proposals/{id}/jobs`: 10/minute
- `PUT /api/settings`: 5/minute
- `DELETE /api/proposals/{id}`: 5/minute

## Testing Rate Limits

### Check Current Usage

```python
response = requests.get("/api/proposals", headers=headers)
print(f"Remaining: {response.headers.get('X-RateLimit-Remaining')}")
print(f"Reset at: {response.headers.get('X-RateLimit-Reset')}")
```

### Test Rate Limit

```python
# Make requests until rate limited
for i in range(150):
    response = requests.get("/api/proposals", headers=headers)
    if response.status_code == 429:
        print(f"Rate limited after {i} requests")
        break
```

## Troubleshooting

### Unexpected Rate Limiting

1. **Check Authentication**: Ensure you're authenticated
2. **Check Headers**: Monitor rate limit headers
3. **Check Endpoint**: Some endpoints have lower limits
4. **Check Time Window**: Limits reset at specific times

### Reducing API Calls

1. **Cache Responses**: Cache frequently accessed data
2. **Use Webhooks**: Avoid polling
3. **Batch Requests**: Combine multiple requests
4. **Optimize Code**: Reduce unnecessary requests

## Next Steps

- Review [API Overview](api_overview.md)
- Check [Authentication Guide](authentication.md)
- See [Error Codes](error_codes.md)


