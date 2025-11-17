"""In-app help system component"""
import streamlit as st
from typing import Dict, Any, Optional, List
import os
import markdown
from pathlib import Path


def render_help_sidebar():
    """Render help sidebar"""
    with st.sidebar.expander("❓ Help", expanded=False):
        st.write("**Quick Help**")
        
        if st.button("📖 Documentation", use_container_width=True):
            st.session_state.show_help = "documentation"
            st.rerun()
        
        if st.button("❓ FAQ", use_container_width=True):
            st.session_state.show_help = "faq"
            st.rerun()
        
        if st.button("🎓 Tutorials", use_container_width=True):
            st.session_state.show_help = "tutorials"
            st.rerun()
        
        if st.button("🐛 Report Issue", use_container_width=True):
            st.session_state.show_help = "report_issue"
            st.rerun()


def render_contextual_help(context: str):
    """Render contextual help based on current context
    
    Args:
        context: Current page/feature context
    """
    help_content = get_help_content(context)
    
    if help_content:
        with st.expander("💡 Help", expanded=False):
            st.markdown(help_content)


def get_help_content(context: str) -> Optional[str]:
    """Get help content for context
    
    Args:
        context: Context identifier
        
    Returns:
        Help content as markdown string
    """
    help_map = {
        "proposal_form": """
### Creating a Proposal

1. **Fill in all required fields** (marked with *)
2. **Provide detailed information** for better results
3. **Include funder website URL** for automated research
4. **Review before submitting** using the preview button
5. **Save as draft** if not ready to submit

**Tips:**
- Be specific in your descriptions
- Include clear objectives
- Provide accurate budget information
- Add supporting documents if available
        """,
        "status_dashboard": """
### Job Status Dashboard

- **Monitor progress** in real-time
- **View task details** by expanding job cards
- **Auto-refresh** updates status automatically
- **Filter by status** to find specific jobs
- **View errors** if job fails

**Status Colors:**
- 🟢 Green: Completed
- 🔵 Blue: Processing
- 🟠 Orange: Pending
- 🔴 Red: Failed
        """,
        "document_viewer": """
### Document Viewer

- **Preview** documents in browser
- **Download** as PDF or DOCX
- **Compare versions** side-by-side
- **View history** of all versions

**Tips:**
- PDF is best for final submission
- DOCX is best for editing
- Always review before submission
        """,
        "settings": """
### Settings Configuration

- **LLM Provider**: Choose your AI provider
- **API Keys**: Securely store your keys
- **Quality**: Set quality thresholds
- **Email**: Configure notifications
- **Storage**: Choose storage backend

**Security:**
- API keys are encrypted
- Never share your keys
- Rotate keys regularly
        """
    }
    
    return help_map.get(context)


def render_help_page(page: str):
    """Render full help page
    
    Args:
        page: Help page to display
    """
    if page == "documentation":
        render_documentation_help()
    elif page == "faq":
        render_faq_help()
    elif page == "tutorials":
        render_tutorials_help()
    elif page == "report_issue":
        render_report_issue()


def render_documentation_help():
    """Render documentation help page"""
    st.header("📖 Documentation")
    
    st.write("Browse our comprehensive documentation:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("User Guides")
        if st.button("Getting Started"):
            st.session_state.view_doc = "user_guide/getting_started.md"
            st.rerun()
        if st.button("Proposal Creation"):
            st.session_state.view_doc = "user_guide/proposal_creation.md"
            st.rerun()
        if st.button("Document Management"):
            st.session_state.view_doc = "user_guide/document_management.md"
            st.rerun()
        if st.button("Settings Configuration"):
            st.session_state.view_doc = "user_guide/settings_configuration.md"
            st.rerun()
        if st.button("Troubleshooting"):
            st.session_state.view_doc = "user_guide/troubleshooting.md"
            st.rerun()
    
    with col2:
        st.subheader("API Documentation")
        if st.button("API Overview"):
            st.session_state.view_doc = "api/api_overview.md"
            st.rerun()
        if st.button("Authentication"):
            st.session_state.view_doc = "api/authentication.md"
            st.rerun()
        if st.button("Endpoints"):
            st.session_state.view_doc = "api/endpoints.md"
            st.rerun()
        if st.button("Webhooks"):
            st.session_state.view_doc = "api/webhooks.md"
            st.rerun()
        if st.button("Error Codes"):
            st.session_state.view_doc = "api/error_codes.md"
            st.rerun()
    
    st.divider()
    
    st.subheader("Guides")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Quick Start Guide"):
            st.session_state.view_doc = "guides/quick_start_guide.md"
            st.rerun()
        if st.button("Advanced Features"):
            st.session_state.view_doc = "guides/advanced_features.md"
            st.rerun()
    
    with col2:
        if st.button("Best Practices"):
            st.session_state.view_doc = "guides/best_practices.md"
            st.rerun()
        if st.button("Integration Guide"):
            st.session_state.view_doc = "guides/integration_guide.md"
            st.rerun()


def render_faq_help():
    """Render FAQ help page"""
    st.header("❓ Frequently Asked Questions")
    
    # Load FAQ content
    try:
        faq_path = Path("docs/faq.md")
        if faq_path.exists():
            faq_content = faq_path.read_text(encoding='utf-8')
            st.markdown(faq_content)
        else:
            st.info("FAQ documentation not found. Please check the docs folder.")
    except Exception as e:
        st.error(f"Error loading FAQ: {str(e)}")
    
    st.divider()
    
    st.subheader("Still have questions?")
    st.write("If you can't find the answer you're looking for:")
    st.write("- Check the [Troubleshooting Guide](user_guide/troubleshooting.md)")
    st.write("- Review the [Documentation](documentation)")
    st.write("- Report an issue on GitHub")


def render_tutorials_help():
    """Render tutorials help page"""
    st.header("🎓 Tutorials")
    
    st.write("Learn how to use the Proposal Generator with our interactive tutorials:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Getting Started")
        if st.button("Quick Start (5 min)", use_container_width=True):
            st.session_state.start_tutorial = "quick_start"
            st.rerun()
        
        st.subheader("Features")
        if st.button("Creating Proposals", use_container_width=True):
            st.session_state.start_tutorial = "proposal_creation"
            st.rerun()
        if st.button("Job Monitoring", use_container_width=True):
            st.session_state.start_tutorial = "job_monitoring"
            st.rerun()
        if st.button("Document Management", use_container_width=True):
            st.session_state.start_tutorial = "document_management"
            st.rerun()
    
    with col2:
        st.subheader("Advanced")
        if st.button("API Integration", use_container_width=True):
            st.session_state.start_tutorial = "api_integration"
            st.rerun()
        if st.button("Settings Configuration", use_container_width=True):
            st.session_state.start_tutorial = "settings"
            st.rerun()
        if st.button("Best Practices", use_container_width=True):
            st.session_state.start_tutorial = "best_practices"
            st.rerun()
    
    st.divider()
    
    st.subheader("Video Tutorials")
    st.info("Video tutorials coming soon!")


def render_report_issue():
    """Render issue reporting page"""
    st.header("🐛 Report an Issue")
    
    st.write("Found a bug or have a suggestion? Let us know!")
    
    issue_type = st.radio(
        "Issue Type",
        options=["Bug Report", "Feature Request", "Documentation", "Question"]
    )
    
    title = st.text_input("Title *", help="Brief description of the issue")
    
    description = st.text_area(
        "Description *",
        height=200,
        help="Detailed description of the issue"
    )
    
    steps = st.text_area(
        "Steps to Reproduce",
        height=150,
        help="If reporting a bug, describe how to reproduce it"
    )
    
    expected = st.text_area(
        "Expected Behavior",
        height=100,
        help="What you expected to happen"
    )
    
    actual = st.text_area(
        "Actual Behavior",
        height=100,
        help="What actually happened"
    )
    
    environment = st.text_input(
        "Environment",
        help="OS, Python version, etc."
    )
    
    if st.button("Submit Issue"):
        if title and description:
            st.success("Thank you for reporting! Your issue has been logged.")
            st.info("""
            **Next Steps:**
            1. Check existing issues on GitHub
            2. Create a new issue with the information above
            3. Include any relevant logs or screenshots
            """)
        else:
            st.error("Please fill in at least title and description.")


def render_help_search():
    """Render help search functionality"""
    st.subheader("🔍 Search Help")
    
    search_query = st.text_input("Search documentation", placeholder="Enter search term...")
    
    if search_query:
        # Simple search implementation
        results = search_documentation(search_query)
        
        if results:
            st.write(f"Found {len(results)} results:")
            for result in results:
                with st.expander(result['title']):
                    st.markdown(result['snippet'])
                    if st.button("View Full", key=result['path']):
                        st.session_state.view_doc = result['path']
                        st.rerun()
        else:
            st.info("No results found. Try different keywords.")


def search_documentation(query: str) -> List[Dict[str, Any]]:
    """Search documentation files
    
    Args:
        query: Search query
        
    Returns:
        List of search results
    """
    results = []
    docs_path = Path("docs")
    
    if not docs_path.exists():
        return results
    
    query_lower = query.lower()
    
    # Search markdown files
    for md_file in docs_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
            if query_lower in content.lower():
                # Extract snippet
                lines = content.split('\n')
                snippet_lines = []
                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        snippet_lines = lines[start:end]
                        break
                
                snippet = '\n'.join(snippet_lines)
                if len(snippet) > 200:
                    snippet = snippet[:200] + "..."
                
                results.append({
                    'title': md_file.stem.replace('_', ' ').title(),
                    'path': str(md_file.relative_to(docs_path)),
                    'snippet': snippet
                })
        except Exception:
            continue
    
    return results[:10]  # Limit to 10 results


def show_tooltip(text: str, help_text: str):
    """Show tooltip with help text
    
    Args:
        text: Main text to display
        help_text: Help text for tooltip
    """
    st.markdown(f"""
    <div title="{help_text}">
        {text} <span style="color: #666; cursor: help;">(?)</span>
    </div>
    """, unsafe_allow_html=True)


