# Integration Guide

Learn how to integrate the Proposal Generator with other systems and services.

## Overview

The Proposal Generator can be integrated with:
- Web applications
- Mobile apps
- Workflow automation tools
- Document management systems
- Notification services
- Analytics platforms

## API Integration

### Basic Integration

```python
import requests

class ProposalGeneratorClient:
    def __init__(self, base_url, api_token):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def create_proposal(self, data):
        response = requests.post(
            f"{self.base_url}/api/proposals",
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_job_status(self, job_id):
        response = requests.get(
            f"{self.base_url}/api/jobs/{job_id}/status",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
```

### Webhook Integration

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    event = request.json
    
    if event['type'] == 'job.completed':
        job_id = event['data']['job_id']
        document_id = event['data']['document_id']
        # Process completed job
        process_completed_job(job_id, document_id)
    
    return {'status': 'ok'}, 200
```

## Web Application Integration

### React Example

```javascript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ProposalCreator() {
  const [proposal, setProposal] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);

  const createProposal = async (data) => {
    const response = await axios.post('/api/proposals', data, {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    });
    setProposal(response.data);
    
    // Create job
    const jobResponse = await axios.post(
      `/api/proposals/${response.data.id}/jobs`,
      {},
      { headers: { 'Authorization': `Bearer ${getToken()}` } }
    );
    
    // Poll for status
    pollJobStatus(jobResponse.data.id);
  };

  const pollJobStatus = async (jobId) => {
    const interval = setInterval(async () => {
      const response = await axios.get(`/api/jobs/${jobId}/status`, {
        headers: { 'Authorization': `Bearer ${getToken()}` }
      });
      
      setJobStatus(response.data);
      
      if (response.data.status === 'completed' || response.data.status === 'failed') {
        clearInterval(interval);
      }
    }, 5000);
  };

  return (
    <div>
      {/* Proposal form */}
    </div>
  );
}
```

## Workflow Automation

### Zapier Integration

1. **Trigger**: New proposal created
2. **Action**: Send notification
3. **Action**: Create task in project management tool

### Make (Integromat) Integration

1. **Webhook**: Receive job completion event
2. **HTTP Request**: Download document
3. **Google Drive**: Upload document
4. **Email**: Send notification

## Document Management Systems

### SharePoint Integration

```python
from office365.sharepoint.client_context import ClientContext

def upload_to_sharepoint(document_path, site_url, library_name):
    ctx = ClientContext(site_url).with_credentials(credentials)
    target_library = ctx.web.lists.get_by_title(library_name)
    
    with open(document_path, 'rb') as content_file:
        file_content = content_file.read()
    
    target_library.root_folder.upload_file(
        os.path.basename(document_path),
        file_content
    ).execute_query()
```

### Google Drive Integration

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file_path, folder_id):
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    
    media = MediaFileUpload(file_path, mimetype='application/pdf')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    return file.get('id')
```

## Notification Services

### Slack Integration

```python
import requests

def send_slack_notification(message, webhook_url):
    payload = {
        "text": message,
        "username": "Proposal Generator",
        "icon_emoji": ":memo:"
    }
    requests.post(webhook_url, json=payload)
```

### Microsoft Teams Integration

```python
def send_teams_notification(title, message, webhook_url):
    payload = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": title,
        "themeColor": "0078D4",
        "title": title,
        "text": message
    }
    requests.post(webhook_url, json=payload)
```

## Analytics Integration

### Google Analytics

```javascript
// Track proposal creation
gtag('event', 'proposal_created', {
  'event_category': 'Proposal',
  'event_label': proposalId,
  'value': 1
});

// Track job completion
gtag('event', 'job_completed', {
  'event_category': 'Job',
  'event_label': jobId,
  'value': 1
});
```

### Custom Analytics

```python
import requests

def track_event(event_name, properties):
    requests.post('https://your-analytics.com/events', json={
        'event': event_name,
        'properties': properties,
        'timestamp': datetime.now().isoformat()
    })
```

## Database Integration

### Direct Database Access

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_proposals_from_db():
    session = Session()
    proposals = session.query(Proposal).all()
    session.close()
    return proposals
```

## Email Integration

### SendGrid Integration

```python
import sendgrid
from sendgrid.helpers.mail import Mail

def send_proposal_email(to_email, document_path):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    
    message = Mail(
        from_email='noreply@example.com',
        to_emails=to_email,
        subject='Your Proposal is Ready',
        html_content='<p>Your proposal has been generated.</p>'
    )
    
    with open(document_path, 'rb') as f:
        data = f.read()
        f.close()
    
    message.attachment = Attachment(
        FileContent(base64.b64encode(data).decode()),
        FileName(os.path.basename(document_path)),
        FileType('application/pdf')
    )
    
    sg.send(message)
```

## CRM Integration

### Salesforce Integration

```python
from simple_salesforce import Salesforce

def create_salesforce_opportunity(proposal_data):
    sf = Salesforce(username=USERNAME, password=PASSWORD, security_token=TOKEN)
    
    opportunity = {
        'Name': proposal_data['title'],
        'Amount': proposal_data['budget'],
        'StageName': 'Proposal',
        'CloseDate': proposal_data['deadline']
    }
    
    sf.Opportunity.create(opportunity)
```

## Next Steps

- Review [API Documentation](../api/api_overview.md)
- Check [Advanced Features](advanced_features.md)
- See [Deployment Guide](deployment_guide.md)



