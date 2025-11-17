# Webhooks Guide

Webhooks allow you to receive real-time notifications when events occur in the Proposal Generator.

## Overview

Webhooks are HTTP callbacks that send event data to your server when specific events occur. This allows you to integrate the Proposal Generator with your own systems.

## Setting Up Webhooks

### 1. Create Webhook Endpoint

Create an HTTP endpoint on your server to receive webhook events:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.json
    # Process event
    return {'status': 'ok'}, 200
```

### 2. Register Webhook

Register your webhook URL:

```http
POST /api/webhooks
```

**Request Body:**
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["job.completed", "job.failed"],
  "secret": "your_webhook_secret"
}
```

**Response:**
```json
{
  "id": "webhook_123",
  "url": "https://your-server.com/webhook",
  "events": ["job.completed", "job.failed"],
  "status": "active",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### 3. Verify Webhook

The system will send a verification request to your endpoint. Respond with the challenge:

```python
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.json.get('type') == 'webhook.verify':
        return {'challenge': request.json['challenge']}, 200
    # Process other events
    return {'status': 'ok'}, 200
```

## Event Types

### Job Events

#### job.created
Triggered when a new job is created.

```json
{
  "type": "job.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "job_id": "job_123",
    "proposal_id": "prop_123",
    "status": "pending"
  }
}
```

#### job.started
Triggered when a job starts processing.

```json
{
  "type": "job.started",
  "timestamp": "2024-01-15T10:31:00Z",
  "data": {
    "job_id": "job_123",
    "status": "processing"
  }
}
```

#### job.progress
Triggered when job progress updates (throttled to once per 10 seconds).

```json
{
  "type": "job.progress",
  "timestamp": "2024-01-15T10:32:00Z",
  "data": {
    "job_id": "job_123",
    "progress": {
      "completed": 5,
      "total": 10,
      "percentage": 50
    }
  }
}
```

#### job.completed
Triggered when a job completes successfully.

```json
{
  "type": "job.completed",
  "timestamp": "2024-01-15T10:40:00Z",
  "data": {
    "job_id": "job_123",
    "proposal_id": "prop_123",
    "document_id": "doc_123",
    "status": "completed"
  }
}
```

#### job.failed
Triggered when a job fails.

```json
{
  "type": "job.failed",
  "timestamp": "2024-01-15T10:35:00Z",
  "data": {
    "job_id": "job_123",
    "error": "Error message",
    "error_details": {
      // Error details
    }
  }
}
```

### Document Events

#### document.created
Triggered when a document is created.

```json
{
  "type": "document.created",
  "timestamp": "2024-01-15T11:00:00Z",
  "data": {
    "document_id": "doc_123",
    "proposal_id": "prop_123",
    "version": 1
  }
}
```

### Proposal Events

#### proposal.created
Triggered when a proposal is created.

```json
{
  "type": "proposal.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "proposal_id": "prop_123",
    "title": "AI Research Proposal"
  }
}
```

## Webhook Security

### Signature Verification

Webhooks include a signature in the `X-Webhook-Signature` header for verification:

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Webhook-Signature')
    if not verify_webhook_signature(request.data, signature, WEBHOOK_SECRET):
        return {'error': 'Invalid signature'}, 401
    
    event = request.json
    # Process event
    return {'status': 'ok'}, 200
```

### HTTPS Required

Webhook URLs must use HTTPS in production. HTTP is only allowed for local development.

## Managing Webhooks

### List Webhooks

```http
GET /api/webhooks
```

**Response:**
```json
{
  "webhooks": [
    {
      "id": "webhook_123",
      "url": "https://your-server.com/webhook",
      "events": ["job.completed"],
      "status": "active"
    }
  ]
}
```

### Get Webhook

```http
GET /api/webhooks/{id}
```

### Update Webhook

```http
PUT /api/webhooks/{id}
```

**Request Body:**
```json
{
  "url": "https://new-url.com/webhook",
  "events": ["job.completed", "job.failed"]
}
```

### Delete Webhook

```http
DELETE /api/webhooks/{id}
```

### Test Webhook

```http
POST /api/webhooks/{id}/test
```

Sends a test event to the webhook URL.

## Best Practices

### Idempotency

Make your webhook handler idempotent to handle duplicate events:

```python
processed_events = set()

@app.route('/webhook', methods=['POST'])
def webhook():
    event_id = request.json.get('id')
    if event_id in processed_events:
        return {'status': 'already_processed'}, 200
    
    # Process event
    processed_events.add(event_id)
    return {'status': 'ok'}, 200
```

### Retry Logic

The system retries failed webhook deliveries:
- Immediate retry on failure
- Exponential backoff (1s, 2s, 4s, 8s, 16s)
- Maximum 5 retries
- Events older than 24 hours are dropped

### Response Codes

Return appropriate HTTP status codes:
- `200 OK`: Event processed successfully
- `400 Bad Request`: Invalid event data
- `401 Unauthorized`: Invalid signature
- `500 Internal Server Error`: Temporary failure (will retry)

### Timeout

Webhook endpoints should respond within 5 seconds. Longer responses may timeout.

## Testing

### Local Testing

Use tools like ngrok to test webhooks locally:

```bash
ngrok http 5000
```

Use the ngrok URL as your webhook URL.

### Test Events

Use the test endpoint to send test events:

```http
POST /api/webhooks/{id}/test
```

## Troubleshooting

### Webhook Not Receiving Events

1. **Check URL**: Verify webhook URL is correct
2. **Check Status**: Ensure webhook is active
3. **Check Events**: Verify subscribed events
4. **Check Logs**: Review webhook delivery logs

### Signature Verification Failing

1. **Check Secret**: Verify webhook secret is correct
2. **Check Algorithm**: Use SHA256 HMAC
3. **Check Payload**: Use raw request body

### Delivery Failures

1. **Check Endpoint**: Ensure endpoint is accessible
2. **Check Response**: Return 200 OK
3. **Check Timeout**: Respond within 5 seconds
4. **Check Logs**: Review error logs

## Next Steps

- Review [API Overview](api_overview.md)
- Check [Endpoints Documentation](endpoints.md)
- See [Error Codes](error_codes.md)


