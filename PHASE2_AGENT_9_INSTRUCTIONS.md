# PHASE 2 - AGENT 9: Web Interface & UI

## Your Mission
Build a comprehensive Streamlit web interface with real-time dashboards, document viewing, and user experience enhancements.

## Files to Create

### 1. `web/__init__.py`
```python
"""Web interface package"""
```

### 2. `web/app.py`
Main Streamlit application:
- User interface for proposal creation
- Real-time job status monitoring
- Document viewer and download
- Settings and configuration
- User authentication (optional)
- Navigation and routing

### 3. `web/components/__init__.py`
```python
"""UI components package"""
```

### 4. `web/components/proposal_form.py`
Proposal creation form component:
- Input fields for proposal details
- Funder selection
- Project information
- Team details
- Budget inputs
- File uploads
- Form validation

### 5. `web/components/status_dashboard.py`
Real-time status dashboard:
- Job status monitoring
- Progress bars
- Task completion tracking
- Error display
- Real-time updates (auto-refresh)

### 6. `web/components/document_viewer.py`
Document viewer component:
- Display generated proposals
- Version history
- Download options (PDF, DOCX)
- Print functionality
- Side-by-side comparison

### 7. `web/components/settings_panel.py`
Settings and configuration panel:
- LLM provider selection
- API key management
- Quality thresholds
- Email settings
- Storage preferences

### 8. `web/utils/__init__.py`
```python
"""Web utilities package"""
```

### 9. `web/utils/api_client.py`
API client for backend communication:
- REST API calls
- Error handling
- Request/response formatting
- Authentication handling

### 10. `web/utils/helpers.py`
Helper functions:
- Data formatting
- Date/time utilities
- File handling
- Validation helpers

### 11. `tests/test_web.py`
Tests for web interface:
- Component tests
- API integration tests
- UI flow tests

## Dependencies to Add
- streamlit>=1.28.0
- streamlit-aggrid (for tables)
- streamlit-option-menu (for navigation)
- plotly (for charts/graphs)

## Key Requirements
1. Must integrate with existing API endpoints (`api/endpoints.py`)
2. Real-time status updates using polling or websockets
3. Responsive design (mobile-friendly)
4. Error handling and user feedback
5. Loading states and progress indicators
6. Clean, professional UI design

## Integration Points
- Uses API endpoints from Agent 2 (`api/endpoints.py`)
- Displays data from database models (Agent 1)
- Shows job status from background processor (Agent 2)
- Integrates with all agent outputs

## UI Features to Implement

### Main Dashboard
- Overview of all projects
- Recent activity
- Quick actions
- Statistics and metrics

### Proposal Creation
- Step-by-step wizard
- Form validation
- Preview before submission
- Save as draft

### Job Monitoring
- Real-time status updates
- Progress tracking
- Error messages
- Completion notifications

### Document Management
- View generated documents
- Version history
- Download options
- Share functionality

### Settings
- User preferences
- API configuration
- Notification settings
- Theme selection

## Testing Requirements
- Test all UI components
- Test API integration
- Test form validation
- Test error handling
- Test responsive design

## Success Criteria
- ✅ All components created and functional
- ✅ Integrates with backend API
- ✅ Real-time updates working
- ✅ Professional UI design
- ✅ Mobile responsive
- ✅ Comprehensive error handling
- ✅ Tests written and passing

