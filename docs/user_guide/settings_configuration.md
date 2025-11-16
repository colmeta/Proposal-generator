# Settings Configuration Guide

This guide explains how to configure system settings for optimal proposal generation.

## Overview

The Settings panel allows you to configure:
- LLM provider and model selection
- API keys and authentication
- Quality thresholds
- Email notifications
- Storage preferences

## Accessing Settings

1. Open the web interface
2. Click **Settings** in the navigation menu
3. Use tabs to navigate different setting categories
4. Click **Save Settings** when done

## LLM Provider Settings

### Selecting a Provider

Choose from:
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude 3 Opus, Claude 3 Sonnet
- **Google**: Gemini Pro, Gemini Ultra
- **Groq**: Fast inference models
- **Custom**: Custom API endpoint

### Model Configuration

#### Model Name
- Enter the specific model name
- Examples: `gpt-4`, `claude-3-opus`, `gemini-pro`
- Check provider documentation for available models

#### Temperature
- **Range**: 0.0 to 2.0
- **Default**: 0.7
- **Lower (0.0-0.5)**: More deterministic, focused
- **Higher (0.7-2.0)**: More creative, varied
- **Recommendation**: 0.7 for proposals (balanced)

#### Max Tokens
- **Range**: 100 to 32,000
- **Default**: 2,000
- Controls maximum response length
- Higher = longer outputs, more cost

#### Request Timeout
- **Range**: 10 to 300 seconds
- **Default**: 60 seconds
- Time to wait for API response
- Increase for slower connections

### Fallback Provider

Enable fallback to use a secondary provider if primary fails:
- **Use Case**: High availability, redundancy
- **Configuration**: Select fallback provider and model
- **Behavior**: Automatically switches on failure

## API Keys Management

### Adding API Keys

1. Navigate to **API Keys** tab
2. Enter key in password field
3. Click **Save Settings**
4. Key is encrypted and stored securely

### Supported Providers

#### OpenAI
- Get key from: https://platform.openai.com/api-keys
- Format: `sk-...`
- Required for OpenAI models

#### Anthropic
- Get key from: https://console.anthropic.com/
- Format: `sk-ant-...`
- Required for Claude models

#### Google
- Get key from: https://makersuite.google.com/app/apikey
- Format: Varies
- Required for Gemini models

#### Groq
- Get key from: https://console.groq.com/keys
- Format: `gsk_...`
- Required for Groq models

#### SendGrid
- Get key from: https://app.sendgrid.com/settings/api_keys
- Format: `SG....`
- Required for email notifications

### Security Best Practices

- **Never Share Keys**: Keep keys confidential
- **Rotate Regularly**: Change keys periodically
- **Use Environment Variables**: For production
- **Monitor Usage**: Check for unauthorized use
- **Revoke if Compromised**: Immediately revoke compromised keys

## Quality Settings

### Minimum Quality Score

- **Range**: 0.0 to 1.0
- **Default**: 0.7
- **Purpose**: Minimum score required for completion
- **Lower**: Accept lower quality (faster)
- **Higher**: Require higher quality (slower, more cost)

### Quality Checks

Enable automatic quality checks:
- **On**: System checks quality before completion
- **Off**: Skip quality checks (faster)
- **Recommendation**: Keep enabled for best results

### Auto-Revision

Automatically revise low-quality documents:
- **On**: System revises if quality below threshold
- **Off**: Manual revision required
- **Max Attempts**: Limit revision attempts (1-5)
- **Recommendation**: Enable with 2-3 max attempts

## Email Settings

### Enabling Email

1. Toggle **Enable Email Notifications**
2. Enter **From Email Address**
3. Configure notification preferences
4. Save settings

### Notification Preferences

#### Job Completion
- **On**: Email when job completes
- **Off**: No completion emails
- **Includes**: Job summary, document link

#### Errors
- **On**: Email on errors
- **Off**: No error emails
- **Includes**: Error details, troubleshooting

#### Progress Updates
- **On**: Email on major milestones
- **Off**: No progress emails
- **Includes**: Progress percentage, status

### Email Configuration

#### From Address
- **Required**: Valid email address
- **Format**: `name@domain.com`
- **Verification**: May need to verify with provider

#### SendGrid Setup
1. Create SendGrid account
2. Generate API key
3. Verify sender email
4. Add key to settings

## Storage Settings

### Storage Type

Choose storage backend:

#### Local
- **Path**: Local directory path
- **Default**: `./storage/documents`
- **Use Case**: Development, single server
- **Pros**: Simple, fast
- **Cons**: Not scalable, no backup

#### AWS S3
- **Bucket Name**: S3 bucket name
- **Region**: AWS region (e.g., `us-east-1`)
- **Use Case**: Production, scalable
- **Pros**: Scalable, reliable, backup
- **Cons**: Requires AWS account, cost

#### Azure Blob Storage
- **Container**: Blob container name
- **Use Case**: Azure deployments
- **Pros**: Integrated with Azure
- **Cons**: Azure-specific

#### Google Cloud Storage
- **Bucket**: GCS bucket name
- **Use Case**: GCP deployments
- **Pros**: Integrated with GCP
- **Cons**: GCP-specific

### Document Retention

#### Automatic Cleanup
- **On**: Automatically delete old documents
- **Off**: Keep all documents
- **Retention Period**: Days to keep (1-365)
- **Default**: 90 days

#### Retention Policy
- Documents older than retention period are deleted
- Cannot be recovered after deletion
- Set appropriate period for your needs

## Best Practices

### LLM Configuration
1. **Choose Right Model**: Balance quality and cost
2. **Set Appropriate Temperature**: 0.7 for proposals
3. **Configure Timeout**: Based on connection speed
4. **Enable Fallback**: For reliability

### API Keys
1. **Keep Secure**: Never share or commit keys
2. **Rotate Regularly**: Change every 90 days
3. **Monitor Usage**: Check for anomalies
4. **Use Environment Variables**: In production

### Quality Settings
1. **Start with Defaults**: Adjust as needed
2. **Enable Quality Checks**: For best results
3. **Use Auto-Revision**: With reasonable limits
4. **Monitor Quality Scores**: Adjust threshold

### Email Configuration
1. **Verify Email**: Ensure from address works
2. **Test Notifications**: Send test emails
3. **Configure Preferences**: Set appropriate notifications
4. **Monitor Delivery**: Check spam folders

### Storage
1. **Choose Appropriate Type**: Based on needs
2. **Set Retention**: Balance storage and history
3. **Backup Important Data**: Don't rely solely on system
4. **Monitor Storage**: Check usage regularly

## Troubleshooting

### Common Issues

#### API Key Not Working
- **Check**: Key is correct and active
- **Verify**: Provider account status
- **Test**: Use provider's test endpoint
- **Solution**: Regenerate key if needed

#### Quality Too Low
- **Check**: Quality threshold setting
- **Adjust**: Lower threshold or improve input
- **Enable**: Auto-revision
- **Review**: Generated content for issues

#### Email Not Sending
- **Check**: SendGrid key and configuration
- **Verify**: From email address
- **Test**: Send test email
- **Review**: SendGrid logs

#### Storage Issues
- **Check**: Storage path/credentials
- **Verify**: Permissions
- **Test**: Write access
- **Review**: Storage logs

### Getting Help
- Review error messages
- Check provider documentation
- Test with minimal configuration
- Contact support if needed

## Advanced Configuration

### Environment Variables
For production, use environment variables:
```env
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
DATABASE_URL=your_url
```

### Configuration Files
Advanced users can use config files:
- YAML configuration
- JSON configuration
- Environment-specific configs

### API Configuration
- Custom API endpoints
- Proxy settings
- Rate limiting
- Retry policies

## Next Steps

- Review [Getting Started Guide](getting_started.md)
- Learn about [Proposal Creation](proposal_creation.md)
- Explore [Advanced Features](../guides/advanced_features.md)

