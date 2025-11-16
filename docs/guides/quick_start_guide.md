# Quick Start Guide

Get up and running with the Proposal Generator in 5 minutes.

## Prerequisites

- Python 3.8+
- API key for at least one LLM provider
- 5 minutes of time

## Step 1: Installation (2 minutes)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file:

```env
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### Start Services

```bash
# Terminal 1: Start API
python -m api.main

# Terminal 2: Start Web Interface
streamlit run web/app.py
```

## Step 2: Create Your First Proposal (2 minutes)

1. **Open Web Interface**: Navigate to `http://localhost:8501`

2. **Configure Settings**:
   - Click **Settings** in sidebar
   - Enter your API key
   - Save settings

3. **Create Proposal**:
   - Click **Create Proposal**
   - Fill in basic information:
     - Title: "My First Proposal"
     - Funder: "Example Foundation"
     - Type: "Research Grant"
     - Deadline: Select a date
     - Budget: 50000
   - Add project description
   - Add objectives
   - Enter PI information
   - Click **Submit Proposal**

## Step 3: Monitor Progress (1 minute)

1. **View Jobs**:
   - Click **Jobs** in navigation
   - See your job status
   - Watch progress updates

2. **View Document**:
   - Once complete, click **Documents**
   - View your generated proposal
   - Download in PDF or DOCX

## Congratulations! 🎉

You've created your first proposal. Next steps:

- Read the [Full User Guide](../user_guide/getting_started.md)
- Explore [Advanced Features](advanced_features.md)
- Check [Best Practices](best_practices.md)

## Common Issues

### API Not Connecting
- Check API is running on port 5000
- Verify API URL in settings

### Job Not Starting
- Check API key is valid
- Verify settings are saved

### Document Not Generated
- Check job completed successfully
- Review error messages if any

For more help, see the [Troubleshooting Guide](../user_guide/troubleshooting.md).

