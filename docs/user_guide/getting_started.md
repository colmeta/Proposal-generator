# Getting Started

Welcome to the Proposal Generator! This guide will help you get started with creating your first proposal.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL (for database)
- API keys for LLM providers (OpenAI, Anthropic, Google, or Groq)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd proposal-generator
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/proposal_generator

# LLM Provider (choose one)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
GROQ_API_KEY=your_groq_key

# API Configuration
API_HOST=localhost
API_PORT=5000
SECRET_KEY=your_secret_key

# Optional: Email
SENDGRID_API_KEY=your_sendgrid_key
FROM_EMAIL=noreply@example.com
```

### Step 4: Initialize Database

```bash
# Run migrations
alembic upgrade head
```

### Step 5: Start the Backend API

```bash
python -m api.main
```

The API will be available at `http://localhost:5000`

### Step 6: Start the Web Interface

```bash
streamlit run web/app.py
```

The web interface will open at `http://localhost:8501`

## First Steps

### 1. Configure Settings

1. Open the web interface
2. Navigate to **Settings** in the sidebar
3. Configure your LLM provider and API keys
4. Set quality thresholds and preferences
5. Save your settings

### 2. Create Your First Proposal

1. Click **Create Proposal** in the navigation menu
2. Fill in the basic information:
   - Proposal title
   - Funder name
   - Proposal type
   - Submission deadline
   - Budget
3. Add project details:
   - Project description
   - Objectives
   - Methodology
   - Expected outcomes
4. Enter team information:
   - Principal Investigator
   - Co-investigators
   - Team members
5. Add budget breakdown (optional)
6. Click **Submit Proposal**

### 3. Monitor Job Progress

1. Navigate to **Jobs** to see your proposal generation job
2. Watch the real-time progress updates
3. View task completion status
4. Check for any errors

### 4. View Generated Document

1. Once the job completes, go to **Documents**
2. View your generated proposal
3. Download in PDF or DOCX format
4. Review and make revisions if needed

## Quick Tips

- **Save as Draft**: Use the "Save as Draft" button to save your work without submitting
- **Preview**: Use the preview button to review your proposal before submission
- **Auto-refresh**: Enable auto-refresh in the Jobs dashboard to see real-time updates
- **API Health**: Check the API health status in the sidebar

## Next Steps

- Read the [Proposal Creation Guide](proposal_creation.md) for detailed instructions
- Explore [Advanced Features](advanced_features.md) for more capabilities
- Check the [FAQ](faq.md) for common questions
- Review [Best Practices](best_practices.md) for tips

## Getting Help

- Check the [Troubleshooting Guide](troubleshooting.md) for common issues
- Use the in-app help system (click the help icon)
- Review the [API Documentation](../api/api_overview.md) for integration
- Contact support if you need additional assistance

## System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 1GB disk space
- Internet connection for API calls

### Recommended Requirements
- Python 3.10+
- 8GB RAM
- 5GB disk space
- Stable internet connection

## Support

For issues, questions, or feature requests:
- Check the documentation
- Review the FAQ
- Open an issue on GitHub
- Contact the support team

Happy proposal writing! 🚀



