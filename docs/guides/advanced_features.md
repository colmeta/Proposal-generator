# Advanced Features Guide

Learn about advanced features and capabilities of the Proposal Generator.

## Custom Agents

### Creating Custom Agents

Custom agents allow you to extend the proposal generation process with specialized tasks.

```python
from agents.base import BaseAgent

class CustomAgent(BaseAgent):
    def process(self, context):
        # Custom processing logic
        return result
```

### Agent Configuration

Configure agents in settings:

```json
{
  "agents": {
    "custom_agent": {
      "enabled": true,
      "priority": 1,
      "config": {
        "custom_param": "value"
      }
    }
  }
}
```

## API Integration

### Programmatic Access

Use the API to integrate with your systems:

```python
import requests

# Create proposal
response = requests.post("http://localhost:5000/api/proposals", json={
    "title": "API Proposal",
    "funder_name": "Foundation",
    # ... other fields
}, headers={"Authorization": "Bearer <token>"})

proposal_id = response.json()["id"]

# Create job
job_response = requests.post(
    f"http://localhost:5000/api/proposals/{proposal_id}/jobs",
    headers={"Authorization": "Bearer <token>"}
)

job_id = job_response.json()["id"]

# Monitor job
status_response = requests.get(
    f"http://localhost:5000/api/jobs/{job_id}/status",
    headers={"Authorization": "Bearer <token>"}
)
```

### Webhooks

Subscribe to events:

```python
# Register webhook
webhook_response = requests.post("http://localhost:5000/api/webhooks", json={
    "url": "https://your-server.com/webhook",
    "events": ["job.completed", "job.failed"]
}, headers={"Authorization": "Bearer <token>"})
```

## Automation

### Batch Processing

Process multiple proposals:

```python
proposals = [
    {"title": "Proposal 1", ...},
    {"title": "Proposal 2", ...},
]

for proposal_data in proposals:
    # Create proposal
    proposal = create_proposal(proposal_data)
    
    # Create job
    job = create_job(proposal["id"])
    
    # Wait for completion
    wait_for_completion(job["id"])
    
    # Download document
    download_document(job["document_id"])
```

### Scheduled Jobs

Use cron or task scheduler:

```bash
# Run daily at 9 AM
0 9 * * * /path/to/script.sh
```

## Custom Templates

### Creating Templates

Create custom proposal templates:

```yaml
sections:
  - name: "Executive Summary"
    required: true
    max_words: 500
  - name: "Project Description"
    required: true
    max_words: 2000
  - name: "Budget"
    required: true
```

### Using Templates

Select template when creating proposal:

```python
proposal_data = {
    "title": "Proposal",
    "template": "custom_template",
    # ... other fields
}
```

## Quality Control

### Quality Metrics

Monitor quality scores:

```python
job = get_job(job_id)
quality_score = job["quality_score"]

if quality_score < 0.7:
    # Trigger revision
    revise_proposal(proposal_id)
```

### Custom Quality Checks

Implement custom quality checks:

```python
def custom_quality_check(document):
    # Custom quality logic
    score = calculate_score(document)
    return score
```

## Performance Optimization

### Caching

Cache frequently accessed data:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_funder_guidelines(funder_name):
    return research_funder(funder_name)
```

### Parallel Processing

Process multiple tasks in parallel:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(process_proposal, proposal_id)
        for proposal_id in proposal_ids
    ]
    results = [f.result() for f in futures]
```

## Integration Examples

### Slack Integration

Send notifications to Slack:

```python
import requests

def notify_slack(message):
    requests.post("https://hooks.slack.com/services/YOUR/WEBHOOK/URL", json={
        "text": message
    })

# On job completion
if job["status"] == "completed":
    notify_slack(f"Proposal {proposal_id} completed!")
```

### Email Integration

Send emails with documents:

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

def send_proposal_email(to_email, document_path):
    msg = MIMEMultipart()
    msg['From'] = "sender@example.com"
    msg['To'] = to_email
    msg['Subject'] = "Your Proposal"
    
    with open(document_path, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        msg.attach(part)
    
    server = smtplib.SMTP('smtp.example.com', 587)
    server.send_message(msg)
```

## Advanced Configuration

### Environment-Specific Settings

Use different settings for different environments:

```python
# development.py
SETTINGS = {
    "llm": {"provider": "OpenAI", "model": "gpt-3.5-turbo"},
    "debug": True
}

# production.py
SETTINGS = {
    "llm": {"provider": "OpenAI", "model": "gpt-4"},
    "debug": False
}
```

### Custom LLM Providers

Add custom LLM providers:

```python
class CustomLLMProvider:
    def generate(self, prompt, **kwargs):
        # Custom generation logic
        return response
```

## Monitoring and Analytics

### Metrics Collection

Collect usage metrics:

```python
from prometheus_client import Counter

proposal_counter = Counter('proposals_created', 'Total proposals created')

def create_proposal(data):
    proposal = create_proposal_internal(data)
    proposal_counter.inc()
    return proposal
```

### Logging

Structured logging:

```python
import logging
import json

logger = logging.getLogger(__name__)

def process_job(job_id):
    logger.info("Processing job", extra={
        "job_id": job_id,
        "timestamp": datetime.now().isoformat()
    })
```

## Security

### API Key Management

Secure API key storage:

```python
import os
from cryptography.fernet import Fernet

def encrypt_api_key(key):
    cipher = Fernet(os.environ['ENCRYPTION_KEY'])
    return cipher.encrypt(key.encode())
```

### Access Control

Implement role-based access:

```python
def require_role(role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not has_role(current_user, role):
                raise Forbidden()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@require_role("admin")
def delete_proposal(proposal_id):
    # Delete logic
    pass
```

## Next Steps

- Review [Best Practices](best_practices.md)
- Check [Integration Guide](integration_guide.md)
- See [Deployment Guide](deployment_guide.md)


