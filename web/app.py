"""Main Streamlit application"""
import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.utils.api_client import get_api_client
from web.utils.helpers import show_error, show_info, show_success
from web.components.proposal_form import render_proposal_form, render_preview
from web.components.status_dashboard import render_status_dashboard, render_job_details
from web.components.document_viewer import render_document_viewer, render_document_comparison
from web.components.settings_panel import render_settings_panel


# Page configuration
st.set_page_config(
    page_title="Proposal Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if 'api_base_url' not in st.session_state:
        st.session_state.api_base_url = 'http://localhost:5000/api'
    
    if 'api_client' not in st.session_state:
        from web.utils.api_client import APIClient
        st.session_state.api_client = APIClient(base_url=st.session_state.api_base_url)
    
    if 'budget_items' not in st.session_state:
        st.session_state.budget_items = []
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'


def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.markdown('<h1 class="main-header">📝 Proposal Generator</h1>', unsafe_allow_html=True)
        
        # API Configuration
        with st.expander("⚙️ API Configuration", expanded=False):
            api_url = st.text_input(
                "API Base URL",
                value=st.session_state.get('api_base_url', 'http://localhost:5000/api'),
                help="Base URL for the backend API"
            )
            if api_url != st.session_state.get('api_base_url'):
                st.session_state.api_base_url = api_url
                from web.utils.api_client import APIClient
                st.session_state.api_client = APIClient(base_url=api_url)
                st.rerun()
            
            # Health check
            api_client = get_api_client()
            try:
                health = api_client.health_check()
                if health.get('status') == 'healthy':
                    st.success("✅ API Connected")
                else:
                    st.error("❌ API Unhealthy")
            except Exception:
                st.warning("⚠️ Cannot reach API")
        
        st.divider()
        
        # Navigation menu
        selected = option_menu(
            menu_title="Navigation",
            options=["Dashboard", "Create Proposal", "Jobs", "Documents", "Settings"],
            icons=["house", "file-earmark-plus", "list-task", "file-text", "gear"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#fafafa"},
                "icon": {"color": "#1f77b4", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#1f77b4"},
            }
        )
        
        st.session_state.current_page = selected
        
        st.divider()
        
        # Quick actions
        st.write("**Quick Actions**")
        if st.button("🔄 Refresh All", use_container_width=True):
            st.rerun()
        
        if st.button("📊 View Statistics", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        st.divider()
        
        # Footer
        st.caption("Proposal Generator v1.0")
        st.caption("Built with Streamlit")


def render_dashboard():
    """Render main dashboard"""
    st.header("📊 Dashboard")
    
    api_client = get_api_client()
    
    # Check API health
    try:
        health = api_client.health_check()
        if health.get('status') != 'healthy':
            show_error("API is not healthy. Some features may not work.")
    except Exception:
        show_error("Cannot connect to API. Please check your API configuration in the sidebar.")
        return
    
    # Statistics
    try:
        proposals_response = api_client.list_proposals(limit=100)
        proposals = proposals_response.get('proposals', [])
        
        jobs_response = api_client.list_jobs(limit=100)
        jobs = jobs_response.get('jobs', [])
        
        docs_response = api_client.list_documents()
        documents = docs_response.get('documents', [])
    except Exception as e:
        show_error(f"Failed to load data: {str(e)}")
        proposals = []
        jobs = []
        documents = []
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Proposals", len(proposals))
    
    with col2:
        active_jobs = len([j for j in jobs if j.get('status', '').lower() in ['pending', 'processing', 'running']])
        st.metric("Active Jobs", active_jobs)
    
    with col3:
        completed_jobs = len([j for j in jobs if j.get('status', '').lower() in ['completed', 'success']])
        st.metric("Completed Jobs", completed_jobs)
    
    with col4:
        st.metric("Documents Generated", len(documents))
    
    st.divider()
    
    # Recent Activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Recent Proposals")
        if proposals:
            recent_proposals = sorted(proposals, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
            for proposal in recent_proposals:
                with st.container():
                    st.write(f"**{proposal.get('title', 'Untitled')}**")
                    st.caption(f"Created: {proposal.get('created_at', 'N/A')}")
                    if st.button("View", key=f"view_prop_{proposal.get('id')}"):
                        st.session_state.view_proposal_id = proposal.get('id')
                        st.session_state.current_page = "Documents"
                        st.rerun()
                    st.divider()
        else:
            st.info("No proposals yet. Create your first proposal!")
    
    with col2:
        st.subheader("⚙️ Recent Jobs")
        if jobs:
            recent_jobs = sorted(jobs, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
            for job in recent_jobs:
                with st.container():
                    status = job.get('status', 'Unknown')
                    st.write(f"**Job {job.get('id', 'Unknown')[:8]}...** - {status}")
                    st.caption(f"Created: {job.get('created_at', 'N/A')}")
                    if st.button("View", key=f"view_job_{job.get('id')}"):
                        st.session_state.view_job_id = job.get('id')
                        st.session_state.current_page = "Jobs"
                        st.rerun()
                    st.divider()
        else:
            st.info("No jobs yet. Create a proposal to generate a job!")
    
    # Quick Actions
    st.divider()
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Create New Proposal", use_container_width=True, type="primary"):
            st.session_state.current_page = "Create Proposal"
            st.rerun()
    
    with col2:
        if st.button("📊 View All Jobs", use_container_width=True):
            st.session_state.current_page = "Jobs"
            st.rerun()
    
    with col3:
        if st.button("📄 View Documents", use_container_width=True):
            st.session_state.current_page = "Documents"
            st.rerun()


def render_create_proposal():
    """Render proposal creation page"""
    # Check for preview mode
    if 'preview_data' in st.session_state:
        render_preview(st.session_state.preview_data)
        return
    
    st.header("📝 Create New Proposal")
    
    form_data = render_proposal_form()
    
    if form_data:
        api_client = get_api_client()
        
        try:
            if form_data.get('status') == 'submitted':
                # Create proposal and job
                proposal = api_client.create_proposal(form_data)
                show_success(f"Proposal created successfully! ID: {proposal.get('id')}")
                
                # Create job for proposal generation
                try:
                    job = api_client.create_job(proposal.get('id'))
                    show_success(f"Job created! Job ID: {job.get('id')}")
                    st.session_state.view_job_id = job.get('id')
                    st.session_state.current_page = "Jobs"
                    st.rerun()
                except Exception as e:
                    show_error(f"Proposal created but failed to create job: {str(e)}")
            
            elif form_data.get('status') == 'draft':
                # Save as draft
                proposal = api_client.create_proposal(form_data)
                show_success(f"Draft saved! Proposal ID: {proposal.get('id')}")
                st.session_state.view_proposal_id = proposal.get('id')
                st.rerun()
        
        except Exception as e:
            show_error(f"Failed to create proposal: {str(e)}")


def render_jobs_page():
    """Render jobs monitoring page"""
    if 'view_job_id' in st.session_state:
        render_job_details(st.session_state.view_job_id)
    else:
        render_status_dashboard()


def render_documents_page():
    """Render documents page"""
    document_id = st.session_state.get('view_document_id')
    proposal_id = st.session_state.get('view_proposal_id')
    
    if document_id or proposal_id:
        render_document_viewer(document_id=document_id, proposal_id=proposal_id)
    else:
        render_document_viewer()


def render_settings_page():
    """Render settings page"""
    render_settings_panel()


def main():
    """Main application entry point"""
    init_session_state()
    render_sidebar()
    
    # Route to appropriate page
    current_page = st.session_state.current_page
    
    if current_page == "Dashboard":
        render_dashboard()
    elif current_page == "Create Proposal":
        render_create_proposal()
    elif current_page == "Jobs":
        render_jobs_page()
    elif current_page == "Documents":
        render_documents_page()
    elif current_page == "Settings":
        render_settings_page()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()



