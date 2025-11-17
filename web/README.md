# Web Interface

Streamlit-based web interface for the Proposal Generator application.

## Features

- **Dashboard**: Overview of proposals, jobs, and documents
- **Proposal Creation**: Step-by-step form for creating new proposals
- **Job Monitoring**: Real-time status tracking with auto-refresh
- **Document Viewer**: View and download generated documents
- **Settings**: Configure LLM providers, API keys, and preferences

## Running the Application

### Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the backend API is running (default: http://localhost:5000)

### Start the Web Interface

```bash
streamlit run web/app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Configuration

You can configure the API base URL in the sidebar under "API Configuration". The default is `http://localhost:5000/api`.

## Project Structure

```
web/
├── __init__.py              # Package initialization
├── app.py                   # Main Streamlit application
├── components/              # UI components
│   ├── __init__.py
│   ├── proposal_form.py     # Proposal creation form
│   ├── status_dashboard.py  # Job status dashboard
│   ├── document_viewer.py   # Document viewer
│   └── settings_panel.py    # Settings panel
└── utils/                   # Utilities
    ├── __init__.py
    ├── api_client.py        # API client for backend communication
    └── helpers.py           # Helper functions
```

## Components

### Proposal Form (`proposal_form.py`)
- Multi-section form for proposal details
- Form validation
- Draft saving
- Preview functionality

### Status Dashboard (`status_dashboard.py`)
- Real-time job monitoring
- Progress tracking
- Task details
- Auto-refresh capability

### Document Viewer (`document_viewer.py`)
- Document preview
- PDF and DOCX download
- Version history
- Side-by-side comparison

### Settings Panel (`settings_panel.py`)
- LLM provider configuration
- API key management
- Quality thresholds
- Email settings
- Storage configuration

## API Integration

The web interface communicates with the backend API through the `APIClient` class in `web/utils/api_client.py`. All API calls are handled with proper error handling and user feedback.

## Testing

Run tests with:
```bash
pytest tests/test_web.py -v
```

## Notes

- The interface uses Streamlit's session state for state management
- Auto-refresh is configurable in the status dashboard
- All API keys are stored securely and never displayed in full
- The interface is responsive and mobile-friendly


