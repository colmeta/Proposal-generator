# Frequently Asked Questions (FAQ)

Common questions and answers about the Proposal Generator.

## General Questions

### What is the Proposal Generator?

The Proposal Generator is an AI-powered tool that helps you create professional grant proposals automatically. It uses large language models to generate proposal content based on your input and funder guidelines.

### How does it work?

1. You provide proposal details (title, description, objectives, etc.)
2. The system researches the funder (if URL provided)
3. AI agents generate proposal content
4. Quality checks ensure high-quality output
5. You receive a formatted document (PDF or DOCX)

### What LLM providers are supported?

- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude 3 Opus, Claude 3 Sonnet)
- Google (Gemini Pro, Gemini Ultra)
- Groq (Fast inference models)

### Is my data secure?

Yes. We take security seriously:
- All data is encrypted in transit (HTTPS)
- API keys are encrypted at rest
- Documents are stored securely
- Regular security audits

## Getting Started

### How do I get started?

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment variables
3. Start the API: `python -m api.main`
4. Start the web interface: `streamlit run web/app.py`
5. Create your first proposal!

See the [Getting Started Guide](user_guide/getting_started.md) for detailed instructions.

### Do I need an API key?

Yes, you need an API key from at least one LLM provider. You can get keys from:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Google: https://makersuite.google.com/app/apikey
- Groq: https://console.groq.com/keys

### How much does it cost?

The Proposal Generator itself is free and open-source. However, you'll need to pay for:
- LLM API usage (varies by provider)
- Hosting (if deploying to cloud)
- Database (if using managed database)

## Proposal Creation

### How long does it take to generate a proposal?

Typically 5-15 minutes depending on:
- Proposal complexity
- Funder research requirements
- LLM provider speed
- System load

### Can I edit the generated proposal?

Yes! You can:
- Download as DOCX and edit in Word
- Make changes and regenerate
- Create new versions
- Compare versions

### What information do I need to provide?

Minimum required:
- Proposal title
- Funder name
- Proposal type
- Deadline
- Budget
- Project description
- Objectives
- Principal Investigator information

Optional but recommended:
- Funder website URL
- Methodology
- Expected outcomes
- Team members
- Budget breakdown
- Supporting documents

### Can I save drafts?

Yes! Click "Save as Draft" to save your work without submitting. Drafts can be edited and submitted later.

## Quality and Accuracy

### How accurate is the generated content?

The AI generates high-quality content, but you should always:
- Review all generated content
- Verify facts and figures
- Check alignment with funder requirements
- Make necessary edits

### What quality checks are performed?

- Content completeness
- Alignment with funder guidelines
- Grammar and style
- Structure and formatting
- Required sections present

### Can I improve the quality?

Yes:
- Provide detailed input
- Include funder website URL
- Enable quality checks
- Use higher-quality models (GPT-4, Claude 3 Opus)
- Review and revise

## Technical Questions

### What are the system requirements?

**Minimum:**
- Python 3.8+
- 4GB RAM
- 1GB disk space
- Internet connection

**Recommended:**
- Python 3.10+
- 8GB RAM
- 5GB disk space
- Stable internet connection

### Can I run it locally?

Yes! The Proposal Generator can run entirely on your local machine. See the [Getting Started Guide](user_guide/getting_started.md).

### Can I deploy it to production?

Yes! See the [Deployment Guide](guides/deployment_guide.md) for instructions on deploying to various platforms.

### How do I update?

1. Pull latest changes: `git pull`
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Run migrations: `alembic upgrade head`
4. Restart services

## API and Integration

### Is there an API?

Yes! The Proposal Generator provides a REST API. See the [API Documentation](api/api_overview.md) for details.

### Can I integrate it with other systems?

Yes! The API allows integration with:
- Web applications
- Mobile apps
- Workflow automation tools
- Document management systems

See the [Integration Guide](guides/integration_guide.md) for examples.

### Do you support webhooks?

Yes! You can subscribe to events like job completion, job failure, etc. See the [Webhooks Guide](api/webhooks.md).

## Troubleshooting

### The API won't start

1. Check Python version: `python --version` (should be 3.8+)
2. Check dependencies: `pip install -r requirements.txt`
3. Check port availability: Ensure port 5000 is free
4. Check logs for errors

### Jobs are failing

1. Check API keys are valid
2. Check API key quotas
3. Review error messages
4. Check network connectivity
5. Verify input data is valid

### Documents aren't generating

1. Check job completed successfully
2. Check storage configuration
3. Review error logs
4. Verify storage permissions

### Quality scores are low

1. Provide more detailed input
2. Include funder website URL
3. Enable auto-revision
4. Use higher-quality models
5. Review and improve input

## Pricing and Limits

### Are there usage limits?

The Proposal Generator itself has no limits. However:
- LLM providers have usage limits
- Rate limiting applies to API requests
- Storage limits depend on your setup

### How much do LLM API calls cost?

Costs vary by provider and model:
- GPT-3.5-turbo: ~$0.002 per 1K tokens
- GPT-4: ~$0.03 per 1K tokens
- Claude 3 Sonnet: ~$0.003 per 1K tokens
- Claude 3 Opus: ~$0.015 per 1K tokens

A typical proposal might cost $0.50-$5.00 depending on length and model.

## Support

### Where can I get help?

- **Documentation**: Check the user guides
- **FAQ**: This document
- **GitHub Issues**: Report bugs and request features
- **Email Support**: Contact support team

### How do I report a bug?

1. Check if it's already reported
2. Create a GitHub issue
3. Include:
   - Description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Error messages/logs

### Can I contribute?

Yes! We welcome contributions. See the [Contributing Guide](contributing.md) for details.

## Privacy and Data

### What data do you store?

We store:
- Proposal data you provide
- Generated documents
- Job status and logs
- Settings and configuration

### Is my data private?

Yes. Your data is private and not shared with third parties (except LLM providers for processing).

### Can I delete my data?

Yes. You can:
- Delete individual proposals
- Delete documents
- Clear all data
- Export data before deletion

### Do you use my data to train models?

No. Your data is only used to generate your proposals and is not used for training.

## Next Steps

- Read the [Getting Started Guide](user_guide/getting_started.md)
- Check the [User Guides](user_guide/)
- Explore [Advanced Features](guides/advanced_features.md)
- Review [Best Practices](guides/best_practices.md)

