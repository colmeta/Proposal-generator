"""Proposal creation form component"""
import streamlit as st
from typing import Dict, Any, Optional
from web.utils.helpers import (
    validate_email, validate_url, validate_required_fields,
    format_currency, parse_budget, show_error, show_warning
)


def render_proposal_form(initial_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Render proposal creation/editing form
    
    Args:
        initial_data: Optional initial data for editing
        
    Returns:
        Proposal data dictionary if submitted, None otherwise
    """
    st.header("📝 Proposal Details")
    
    # Initialize form data
    if initial_data is None:
        initial_data = {}
    
    # Basic Information Section
    with st.expander("Basic Information", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "Proposal Title *",
                value=initial_data.get('title', ''),
                help="Enter a clear and descriptive title for your proposal"
            )
            
            funder_name = st.text_input(
                "Funder Name *",
                value=initial_data.get('funder_name', ''),
                help="Name of the funding organization"
            )
            
            funder_url = st.text_input(
                "Funder Website",
                value=initial_data.get('funder_url', ''),
                help="Website URL of the funding organization"
            )
        
        with col2:
            proposal_type = st.selectbox(
                "Proposal Type *",
                options=['Research Grant', 'Project Funding', 'Scholarship', 'Fellowship', 'Other'],
                index=0 if not initial_data.get('proposal_type') else 
                      ['Research Grant', 'Project Funding', 'Scholarship', 'Fellowship', 'Other'].index(initial_data.get('proposal_type', 'Research Grant')),
                help="Type of proposal"
            )
            
            deadline = st.date_input(
                "Submission Deadline *",
                value=initial_data.get('deadline') if initial_data.get('deadline') else None,
                help="Deadline for proposal submission"
            )
            
            budget = st.text_input(
                "Requested Budget *",
                value=initial_data.get('budget', ''),
                help="Total budget requested (e.g., $50,000 or 50000)"
            )
    
    # Project Information Section
    with st.expander("Project Information", expanded=True):
        project_description = st.text_area(
            "Project Description *",
            value=initial_data.get('project_description', ''),
            height=150,
            help="Detailed description of your project"
        )
        
        objectives = st.text_area(
            "Project Objectives *",
            value=initial_data.get('objectives', ''),
            height=100,
            help="Key objectives and goals of the project"
        )
        
        methodology = st.text_area(
            "Methodology",
            value=initial_data.get('methodology', ''),
            height=100,
            help="Research or project methodology"
        )
        
        expected_outcomes = st.text_area(
            "Expected Outcomes",
            value=initial_data.get('expected_outcomes', ''),
            height=100,
            help="Expected results and impact"
        )
    
    # Team Information Section
    with st.expander("Team Information"):
        col1, col2 = st.columns(2)
        
        with col1:
            principal_investigator = st.text_input(
                "Principal Investigator *",
                value=initial_data.get('principal_investigator', ''),
                help="Name of the principal investigator"
            )
            
            pi_email = st.text_input(
                "PI Email *",
                value=initial_data.get('pi_email', ''),
                help="Email address of the principal investigator"
            )
            
            pi_affiliation = st.text_input(
                "PI Affiliation *",
                value=initial_data.get('pi_affiliation', ''),
                help="Institution or organization"
            )
        
        with col2:
            co_investigators = st.text_area(
                "Co-Investigators",
                value=initial_data.get('co_investigators', ''),
                height=100,
                help="List of co-investigators (one per line)"
            )
            
            team_members = st.text_area(
                "Team Members",
                value=initial_data.get('team_members', ''),
                height=100,
                help="Additional team members (one per line)"
            )
    
    # Budget Breakdown Section
    with st.expander("Budget Breakdown"):
        st.write("Break down your budget by category:")
        
        budget_items = st.session_state.get('budget_items', [])
        
        if st.button("➕ Add Budget Item"):
            budget_items.append({
                'category': '',
                'amount': '',
                'description': ''
            })
            st.session_state.budget_items = budget_items
            st.rerun()
        
        for i, item in enumerate(budget_items):
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    category = st.text_input(
                        "Category",
                        value=item.get('category', ''),
                        key=f"budget_category_{i}",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    amount = st.text_input(
                        "Amount",
                        value=item.get('amount', ''),
                        key=f"budget_amount_{i}",
                        label_visibility="collapsed"
                    )
                
                with col3:
                    if st.button("🗑️", key=f"remove_budget_{i}"):
                        budget_items.pop(i)
                        st.session_state.budget_items = budget_items
                        st.rerun()
                
                description = st.text_input(
                    "Description",
                    value=item.get('description', ''),
                    key=f"budget_desc_{i}"
                )
    
    # Additional Information Section
    with st.expander("Additional Information"):
        keywords = st.text_input(
            "Keywords",
            value=initial_data.get('keywords', ''),
            help="Comma-separated keywords for your proposal"
        )
        
        references = st.text_area(
            "References",
            value=initial_data.get('references', ''),
            height=100,
            help="Key references or citations"
        )
        
        notes = st.text_area(
            "Internal Notes",
            value=initial_data.get('notes', ''),
            height=100,
            help="Private notes (not included in proposal)"
        )
    
    # File Uploads Section
    with st.expander("Supporting Documents"):
        uploaded_files = st.file_uploader(
            "Upload supporting documents",
            type=['pdf', 'docx', 'doc', 'txt'],
            accept_multiple_files=True,
            help="Upload any supporting documents (CVs, letters, etc.)"
        )
        
        if uploaded_files:
            st.write(f"Uploaded {len(uploaded_files)} file(s)")
            for file in uploaded_files:
                st.write(f"- {file.name} ({file.size} bytes)")
    
    # Form Validation and Submission
    st.divider()
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        save_draft = st.button("💾 Save as Draft", use_container_width=True)
    
    with col2:
        preview = st.button("👁️ Preview", use_container_width=True)
    
    with col3:
        submit = st.button("🚀 Submit Proposal", type="primary", use_container_width=True)
    
    # Prepare form data
    form_data = {
        'title': title,
        'funder_name': funder_name,
        'funder_url': funder_url if funder_url else None,
        'proposal_type': proposal_type,
        'deadline': deadline.isoformat() if deadline else None,
        'budget': parse_budget(budget),
        'project_description': project_description,
        'objectives': objectives,
        'methodology': methodology if methodology else None,
        'expected_outcomes': expected_outcomes if expected_outcomes else None,
        'principal_investigator': principal_investigator,
        'pi_email': pi_email,
        'pi_affiliation': pi_affiliation,
        'co_investigators': co_investigators.split('\n') if co_investigators else [],
        'team_members': team_members.split('\n') if team_members else [],
        'budget_items': budget_items if budget_items else [],
        'keywords': [k.strip() for k in keywords.split(',')] if keywords else [],
        'references': references if references else None,
        'notes': notes if notes else None,
        'uploaded_files': [f.name for f in uploaded_files] if uploaded_files else []
    }
    
    # Validate required fields
    required_fields = [
        'title', 'funder_name', 'proposal_type', 'deadline', 'budget',
        'project_description', 'objectives', 'principal_investigator',
        'pi_email', 'pi_affiliation'
    ]
    
    is_valid, error_msg = validate_required_fields(form_data, required_fields)
    
    # Additional validations
    if form_data.get('pi_email') and not validate_email(form_data['pi_email']):
        is_valid = False
        error_msg = "Invalid PI email address"
    
    if form_data.get('funder_url') and not validate_url(form_data['funder_url']):
        is_valid = False
        error_msg = "Invalid funder URL"
    
    if form_data.get('budget') is None or form_data['budget'] <= 0:
        is_valid = False
        error_msg = "Invalid budget amount"
    
    # Handle form actions
    if submit:
        if is_valid:
            form_data['status'] = 'submitted'
            return form_data
        else:
            show_error(error_msg or "Please fill in all required fields")
    
    if save_draft:
        form_data['status'] = 'draft'
        return form_data
    
    if preview:
        if is_valid:
            st.session_state.preview_data = form_data
            st.rerun()
        else:
            show_warning("Please fill in all required fields before previewing")
    
    return None


def render_preview(data: Dict[str, Any]):
    """Render proposal preview
    
    Args:
        data: Proposal data to preview
    """
    st.header("👁️ Proposal Preview")
    
    st.subheader(data.get('title', 'Untitled Proposal'))
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Funder:** {data.get('funder_name', 'N/A')}")
        st.write(f"**Type:** {data.get('proposal_type', 'N/A')}")
    with col2:
        st.write(f"**Deadline:** {data.get('deadline', 'N/A')}")
        st.write(f"**Budget:** {format_currency(data.get('budget', 0))}")
    
    st.divider()
    
    st.subheader("Project Description")
    st.write(data.get('project_description', ''))
    
    st.subheader("Objectives")
    st.write(data.get('objectives', ''))
    
    if data.get('methodology'):
        st.subheader("Methodology")
        st.write(data['methodology'])
    
    if data.get('expected_outcomes'):
        st.subheader("Expected Outcomes")
        st.write(data['expected_outcomes'])
    
    st.divider()
    
    st.subheader("Team Information")
    st.write(f"**Principal Investigator:** {data.get('principal_investigator', 'N/A')}")
    st.write(f"**Email:** {data.get('pi_email', 'N/A')}")
    st.write(f"**Affiliation:** {data.get('pi_affiliation', 'N/A')}")
    
    if data.get('co_investigators'):
        st.write("**Co-Investigators:**")
        for ci in data['co_investigators']:
            st.write(f"- {ci}")
    
    if data.get('budget_items'):
        st.subheader("Budget Breakdown")
        total = 0
        for item in data['budget_items']:
            amount = parse_budget(item.get('amount', '0')) or 0
            total += amount
            st.write(f"- **{item.get('category', 'N/A')}:** {format_currency(amount)}")
            if item.get('description'):
                st.write(f"  _{item['description']}_")
        st.write(f"**Total:** {format_currency(total)}")
    
    if st.button("← Back to Form"):
        if 'preview_data' in st.session_state:
            del st.session_state.preview_data
        st.rerun()

