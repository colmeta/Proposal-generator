"""Real-time status dashboard component"""
import streamlit as st
import time
from typing import Dict, Any, List, Optional
from web.utils.helpers import (
    format_date, format_relative_time, get_status_color,
    format_progress, show_error, show_info
)
from web.utils.api_client import get_api_client
import plotly.graph_objects as go
import plotly.express as px


def render_status_dashboard(job_id: Optional[str] = None, auto_refresh: bool = True):
    """Render job status dashboard
    
    Args:
        job_id: Optional specific job ID to monitor
        auto_refresh: Whether to auto-refresh the dashboard
    """
    st.header("📊 Job Status Dashboard")
    
    api_client = get_api_client()
    
    # Auto-refresh control
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        refresh_interval = st.slider(
            "Auto-refresh interval (seconds)",
            min_value=0,
            max_value=60,
            value=5 if auto_refresh else 0,
            step=5,
            help="Set to 0 to disable auto-refresh"
        )
    
    with col2:
        if st.button("🔄 Refresh Now"):
            st.rerun()
    
    with col3:
        if st.button("🛑 Stop All Jobs"):
            st.warning("Stop functionality not yet implemented")
    
    # Get jobs data
    try:
        if job_id:
            # Get specific job
            job_data = api_client.get_job(job_id)
            jobs = [job_data]
        else:
            # Get all jobs
            jobs_response = api_client.list_jobs(limit=50)
            jobs = jobs_response.get('jobs', [])
    except Exception as e:
        show_error(f"Failed to load jobs: {str(e)}")
        return
    
    if not jobs:
        show_info("No jobs found. Create a proposal to generate a job.")
        return
    
    # Filter and sort jobs
    status_filter = st.selectbox(
        "Filter by Status",
        options=['All', 'Pending', 'Processing', 'Completed', 'Failed'],
        index=0
    )
    
    filtered_jobs = jobs
    if status_filter != 'All':
        filtered_jobs = [j for j in jobs if j.get('status', '').lower() == status_filter.lower()]
    
    # Sort by creation date (newest first)
    filtered_jobs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Statistics Overview
    st.subheader("📈 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    total_jobs = len(jobs)
    pending = len([j for j in jobs if j.get('status', '').lower() in ['pending', 'queued']])
    processing = len([j for j in jobs if j.get('status', '').lower() in ['processing', 'running', 'in_progress']])
    completed = len([j for j in jobs if j.get('status', '').lower() in ['completed', 'success', 'done']])
    failed = len([j for j in jobs if j.get('status', '').lower() in ['failed', 'error', 'cancelled']])
    
    with col1:
        st.metric("Total Jobs", total_jobs)
    with col2:
        st.metric("Pending", pending, delta=None)
    with col3:
        st.metric("Processing", processing, delta=None)
    with col4:
        st.metric("Completed", completed, delta=f"{failed} failed")
    
    # Status Chart
    if total_jobs > 0:
        status_counts = {
            'Pending': pending,
            'Processing': processing,
            'Completed': completed,
            'Failed': failed
        }
        
        fig = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="Job Status Distribution",
            color_discrete_map={
                'Pending': '#FFA500',
                'Processing': '#1f77b4',
                'Completed': '#2ca02c',
                'Failed': '#d62728'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Jobs List
    st.subheader("📋 Jobs")
    
    if not filtered_jobs:
        st.info(f"No jobs found with status: {status_filter}")
        return
    
    for job in filtered_jobs:
        render_job_card(job, api_client)
    
    # Auto-refresh logic
    if refresh_interval > 0:
        time.sleep(refresh_interval)
        st.rerun()


def render_job_card(job: Dict[str, Any], api_client):
    """Render a single job card
    
    Args:
        job: Job data dictionary
        api_client: API client instance
    """
    job_id = job.get('id', 'Unknown')
    status = job.get('status', 'Unknown')
    status_lower = status.lower()
    
    # Determine card color based on status
    if status_lower in ['completed', 'success', 'done']:
        border_color = "#2ca02c"
    elif status_lower in ['failed', 'error', 'cancelled']:
        border_color = "#d62728"
    elif status_lower in ['processing', 'running', 'in_progress']:
        border_color = "#1f77b4"
    else:
        border_color = "#FFA500"
    
    with st.container():
        st.markdown(
            f"""
            <div style="
                border-left: 4px solid {border_color};
                padding: 1rem;
                margin: 0.5rem 0;
                background-color: #f8f9fa;
                border-radius: 4px;
            ">
            """,
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**Job ID:** `{job_id}`")
            if job.get('proposal_id'):
                st.write(f"**Proposal ID:** `{job.get('proposal_id')}`")
            if job.get('proposal_title'):
                st.write(f"**Proposal:** {job.get('proposal_title')}")
        
        with col2:
            st.write(f"**Status:**")
            st.markdown(f"<span style='color: {border_color}; font-weight: bold;'>{status}</span>", unsafe_allow_html=True)
            created_at = job.get('created_at', '')
            if created_at:
                st.write(f"**Created:** {format_relative_time(created_at)}")
        
        with col3:
            if job.get('updated_at'):
                st.write(f"**Updated:** {format_relative_time(job.get('updated_at'))}")
            
            # Progress bar
            progress = job.get('progress', 0)
            if isinstance(progress, dict):
                completed = progress.get('completed', 0)
                total = progress.get('total', 0)
                if total > 0:
                    progress_pct = (completed / total) * 100
                    st.progress(progress_pct / 100)
                    st.caption(f"{completed}/{total} tasks completed")
            elif isinstance(progress, (int, float)):
                st.progress(progress / 100 if progress <= 100 else 1.0)
                st.caption(f"{progress}% complete")
        
        # Task details
        if job.get('tasks'):
            with st.expander("View Tasks"):
                tasks = job.get('tasks', [])
                for task in tasks:
                    task_status = task.get('status', 'Unknown')
                    task_name = task.get('name', 'Unknown Task')
                    
                    status_icon = "✅" if task_status.lower() == 'completed' else \
                                 "❌" if task_status.lower() == 'failed' else \
                                 "⏳" if task_status.lower() == 'processing' else "⏸️"
                    
                    st.write(f"{status_icon} **{task_name}** - {task_status}")
                    
                    if task.get('error'):
                        st.error(f"Error: {task.get('error')}")
        
        # Error details
        if job.get('error'):
            st.error(f"**Error:** {job.get('error')}")
        
        # Actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Refresh", key=f"refresh_{job_id}"):
                st.rerun()
        
        with col2:
            if status_lower in ['completed', 'success', 'done']:
                if st.button("📄 View Document", key=f"view_{job_id}"):
                    st.session_state.view_document_id = job.get('document_id')
                    st.rerun()
        
        with col3:
            if status_lower in ['processing', 'running', 'in_progress']:
                if st.button("🛑 Cancel", key=f"cancel_{job_id}"):
                    st.warning("Cancel functionality not yet implemented")
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.divider()


def render_job_details(job_id: str):
    """Render detailed view of a specific job
    
    Args:
        job_id: Job ID to display
    """
    st.header(f"Job Details: {job_id}")
    
    api_client = get_api_client()
    
    try:
        job = api_client.get_job(job_id)
        status = api_client.get_job_status(job_id)
    except Exception as e:
        show_error(f"Failed to load job: {str(e)}")
        return
    
    # Job Information
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Status:** {job.get('status', 'Unknown')}")
        st.write(f"**Created:** {format_date(job.get('created_at'))}")
        st.write(f"**Updated:** {format_date(job.get('updated_at'))}")
    
    with col2:
        if job.get('proposal_id'):
            st.write(f"**Proposal ID:** {job.get('proposal_id')}")
        if job.get('started_at'):
            st.write(f"**Started:** {format_date(job.get('started_at'))}")
        if job.get('completed_at'):
            st.write(f"**Completed:** {format_date(job.get('completed_at'))}")
    
    # Progress Visualization
    if status.get('progress'):
        progress = status['progress']
        if isinstance(progress, dict):
            completed = progress.get('completed', 0)
            total = progress.get('total', 0)
            
            if total > 0:
                st.subheader("Progress")
                progress_pct = (completed / total) * 100
                st.progress(progress_pct / 100)
                st.write(f"{completed} of {total} tasks completed ({progress_pct:.1f}%)")
                
                # Progress chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Completed', 'Remaining'],
                        y=[completed, total - completed],
                        marker_color=['#2ca02c', '#d3d3d3']
                    )
                ])
                fig.update_layout(title="Task Progress", height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    # Task Timeline
    if job.get('tasks'):
        st.subheader("Task Timeline")
        tasks = job.get('tasks', [])
        
        for i, task in enumerate(tasks):
            task_status = task.get('status', 'Unknown')
            task_name = task.get('name', 'Unknown Task')
            
            status_icon = "✅" if task_status.lower() == 'completed' else \
                         "❌" if task_status.lower() == 'failed' else \
                         "⏳" if task_status.lower() == 'processing' else "⏸️"
            
            with st.container():
                st.write(f"{status_icon} **{task_name}**")
                st.write(f"Status: {task_status}")
                
                if task.get('started_at'):
                    st.write(f"Started: {format_date(task.get('started_at'))}")
                if task.get('completed_at'):
                    st.write(f"Completed: {format_date(task.get('completed_at'))}")
                
                if task.get('error'):
                    st.error(f"Error: {task.get('error')}")
                
                if task.get('output'):
                    with st.expander("View Output"):
                        st.text(task.get('output'))
                
                if i < len(tasks) - 1:
                    st.divider()
    
    # Error Information
    if job.get('error'):
        st.subheader("Error Information")
        st.error(job.get('error'))
        if job.get('error_details'):
            with st.expander("Error Details"):
                st.json(job.get('error_details'))
    
    # Logs
    if status.get('logs'):
        st.subheader("Logs")
        logs = status.get('logs', [])
        log_text = "\n".join([f"[{log.get('timestamp', '')}] {log.get('message', '')}" for log in logs])
        st.text_area("Job Logs", log_text, height=300, disabled=True)
    
    # Actions
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Dashboard"):
            if 'view_job_id' in st.session_state:
                del st.session_state.view_job_id
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh Status"):
            st.rerun()

