"""Settings and configuration panel component"""
import streamlit as st
from typing import Dict, Any, Optional
from web.utils.helpers import (
    validate_email, validate_url, show_error, show_success, show_info
)
from web.utils.api_client import get_api_client


def render_settings_panel():
    """Render settings and configuration panel"""
    st.header("⚙️ Settings & Configuration")
    
    api_client = get_api_client()
    
    # Load current settings
    try:
        current_settings = api_client.get_settings()
    except Exception as e:
        show_error(f"Failed to load settings: {str(e)}")
        current_settings = {}
        show_info("Using default settings. Some features may not work until settings are configured.")
    
    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "LLM Provider", "API Keys", "Quality Settings", "Email", "Storage"
    ])
    
    settings = {}
    
    # LLM Provider Settings
    with tab1:
        settings.update(render_llm_provider_settings(current_settings.get('llm', {})))
    
    # API Keys Settings
    with tab2:
        settings.update(render_api_keys_settings(current_settings.get('api_keys', {})))
    
    # Quality Settings
    with tab3:
        settings.update(render_quality_settings(current_settings.get('quality', {})))
    
    # Email Settings
    with tab4:
        settings.update(render_email_settings(current_settings.get('email', {})))
    
    # Storage Settings
    with tab5:
        settings.update(render_storage_settings(current_settings.get('storage', {})))
    
    # Save button
    st.divider()
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        pass
    
    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.session_state.reset_settings = True
            st.rerun()
    
    with col3:
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            try:
                api_client.update_settings(settings)
                show_success("Settings saved successfully!")
            except Exception as e:
                show_error(f"Failed to save settings: {str(e)}")


def render_llm_provider_settings(current_llm: Dict[str, Any]) -> Dict[str, Any]:
    """Render LLM provider settings
    
    Args:
        current_llm: Current LLM settings
        
    Returns:
        LLM settings dictionary
    """
    st.subheader("LLM Provider Configuration")
    
    provider = st.selectbox(
        "Primary LLM Provider *",
        options=['OpenAI', 'Anthropic', 'Google', 'Groq', 'Custom'],
        index=0 if not current_llm.get('provider') else 
              ['OpenAI', 'Anthropic', 'Google', 'Groq', 'Custom'].index(current_llm.get('provider', 'OpenAI')),
        help="Select your primary LLM provider"
    )
    
    model = st.text_input(
        "Model Name *",
        value=current_llm.get('model', 'gpt-4'),
        help="Model name (e.g., gpt-4, claude-3-opus, gemini-pro)"
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=current_llm.get('temperature', 0.7),
        step=0.1,
        help="Controls randomness in output (0 = deterministic, 2 = very creative)"
    )
    
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=100,
        max_value=32000,
        value=current_llm.get('max_tokens', 2000),
        step=100,
        help="Maximum number of tokens in response"
    )
    
    timeout = st.number_input(
        "Request Timeout (seconds)",
        min_value=10,
        max_value=300,
        value=current_llm.get('timeout', 60),
        step=10,
        help="Timeout for API requests"
    )
    
    # Fallback provider
    st.divider()
    st.write("**Fallback Provider**")
    use_fallback = st.checkbox(
        "Enable Fallback Provider",
        value=current_llm.get('use_fallback', False),
        help="Use a fallback provider if primary fails"
    )
    
    fallback_provider = None
    fallback_model = None
    if use_fallback:
        fallback_provider = st.selectbox(
            "Fallback Provider",
            options=['OpenAI', 'Anthropic', 'Google', 'Groq'],
            index=0 if not current_llm.get('fallback_provider') else
                  ['OpenAI', 'Anthropic', 'Google', 'Groq'].index(current_llm.get('fallback_provider', 'OpenAI'))
        )
        fallback_model = st.text_input(
            "Fallback Model",
            value=current_llm.get('fallback_model', 'gpt-3.5-turbo')
        )
    
    return {
        'llm': {
            'provider': provider,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'timeout': timeout,
            'use_fallback': use_fallback,
            'fallback_provider': fallback_provider,
            'fallback_model': fallback_model
        }
    }


def render_api_keys_settings(current_keys: Dict[str, Any]) -> Dict[str, Any]:
    """Render API keys settings
    
    Args:
        current_keys: Current API keys (may be masked)
        
    Returns:
        API keys settings dictionary
    """
    st.subheader("API Keys Management")
    st.info("🔒 API keys are stored securely and never displayed in full.")
    
    api_keys = {}
    
    # OpenAI
    st.write("**OpenAI**")
    openai_key = st.text_input(
        "OpenAI API Key",
        value="",
        type="password",
        help="Enter your OpenAI API key",
        key="openai_key"
    )
    if openai_key:
        api_keys['openai'] = openai_key
    elif current_keys.get('openai'):
        st.caption("✓ Key already configured (not shown for security)")
        api_keys['openai'] = current_keys.get('openai')  # Keep existing
    
    # Anthropic
    st.write("**Anthropic**")
    anthropic_key = st.text_input(
        "Anthropic API Key",
        value="",
        type="password",
        help="Enter your Anthropic API key",
        key="anthropic_key"
    )
    if anthropic_key:
        api_keys['anthropic'] = anthropic_key
    elif current_keys.get('anthropic'):
        st.caption("✓ Key already configured (not shown for security)")
        api_keys['anthropic'] = current_keys.get('anthropic')
    
    # Google
    st.write("**Google**")
    google_key = st.text_input(
        "Google API Key",
        value="",
        type="password",
        help="Enter your Google API key",
        key="google_key"
    )
    if google_key:
        api_keys['google'] = google_key
    elif current_keys.get('google'):
        st.caption("✓ Key already configured (not shown for security)")
        api_keys['google'] = current_keys.get('google')
    
    # Groq
    st.write("**Groq**")
    groq_key = st.text_input(
        "Groq API Key",
        value="",
        type="password",
        help="Enter your Groq API key",
        key="groq_key"
    )
    if groq_key:
        api_keys['groq'] = groq_key
    elif current_keys.get('groq'):
        st.caption("✓ Key already configured (not shown for security)")
        api_keys['groq'] = current_keys.get('groq')
    
    # SendGrid (for email)
    st.divider()
    st.write("**SendGrid (Email)**")
    sendgrid_key = st.text_input(
        "SendGrid API Key",
        value="",
        type="password",
        help="Enter your SendGrid API key for email notifications",
        key="sendgrid_key"
    )
    if sendgrid_key:
        api_keys['sendgrid'] = sendgrid_key
    elif current_keys.get('sendgrid'):
        st.caption("✓ Key already configured (not shown for security)")
        api_keys['sendgrid'] = current_keys.get('sendgrid')
    
    return {'api_keys': api_keys}


def render_quality_settings(current_quality: Dict[str, Any]) -> Dict[str, Any]:
    """Render quality threshold settings
    
    Args:
        current_quality: Current quality settings
        
    Returns:
        Quality settings dictionary
    """
    st.subheader("Quality Thresholds")
    
    min_quality_score = st.slider(
        "Minimum Quality Score",
        min_value=0.0,
        max_value=1.0,
        value=current_quality.get('min_quality_score', 0.7),
        step=0.05,
        help="Minimum quality score required for document generation"
    )
    
    enable_quality_check = st.checkbox(
        "Enable Quality Checks",
        value=current_quality.get('enable_quality_check', True),
        help="Automatically check document quality before completion"
    )
    
    auto_revision = st.checkbox(
        "Auto-Revision on Low Quality",
        value=current_quality.get('auto_revision', False),
        help="Automatically revise documents that don't meet quality threshold"
    )
    
    max_revision_attempts = None
    if auto_revision:
        max_revision_attempts = st.number_input(
            "Max Revision Attempts",
            min_value=1,
            max_value=5,
            value=current_quality.get('max_revision_attempts', 3),
            help="Maximum number of revision attempts"
        )
    
    return {
        'quality': {
            'min_quality_score': min_quality_score,
            'enable_quality_check': enable_quality_check,
            'auto_revision': auto_revision,
            'max_revision_attempts': max_revision_attempts
        }
    }


def render_email_settings(current_email: Dict[str, Any]) -> Dict[str, Any]:
    """Render email settings
    
    Args:
        current_email: Current email settings
        
    Returns:
        Email settings dictionary
    """
    st.subheader("Email Configuration")
    
    enable_email = st.checkbox(
        "Enable Email Notifications",
        value=current_email.get('enable_email', False),
        help="Send email notifications for job completion and errors"
    )
    
    email_settings = {'enable_email': enable_email}
    
    if enable_email:
        from_email = st.text_input(
            "From Email Address *",
            value=current_email.get('from_email', ''),
            help="Email address to send notifications from"
        )
        
        if from_email and not validate_email(from_email):
            show_error("Invalid email address")
        
        email_settings['from_email'] = from_email
        
        # Notification preferences
        st.divider()
        st.write("**Notification Preferences**")
        
        notify_on_completion = st.checkbox(
            "Notify on Job Completion",
            value=current_email.get('notify_on_completion', True)
        )
        email_settings['notify_on_completion'] = notify_on_completion
        
        notify_on_error = st.checkbox(
            "Notify on Errors",
            value=current_email.get('notify_on_error', True)
        )
        email_settings['notify_on_error'] = notify_on_error
        
        notify_on_progress = st.checkbox(
            "Notify on Major Milestones",
            value=current_email.get('notify_on_progress', False)
        )
        email_settings['notify_on_progress'] = notify_on_progress
    
    return {'email': email_settings}


def render_storage_settings(current_storage: Dict[str, Any]) -> Dict[str, Any]:
    """Render storage settings
    
    Args:
        current_storage: Current storage settings
        
    Returns:
        Storage settings dictionary
    """
    st.subheader("Storage Configuration")
    
    storage_type = st.selectbox(
        "Storage Type",
        options=['Local', 'AWS S3', 'Azure Blob', 'Google Cloud Storage'],
        index=0 if not current_storage.get('type') else
              ['Local', 'AWS S3', 'Azure Blob', 'Google Cloud Storage'].index(current_storage.get('type', 'Local')),
        help="Where to store generated documents"
    )
    
    storage_settings = {'type': storage_type}
    
    if storage_type == 'Local':
        storage_path = st.text_input(
            "Storage Path",
            value=current_storage.get('path', './storage/documents'),
            help="Local directory path for storing documents"
        )
        storage_settings['path'] = storage_path
    
    elif storage_type == 'AWS S3':
        bucket_name = st.text_input(
            "S3 Bucket Name *",
            value=current_storage.get('bucket_name', ''),
            help="AWS S3 bucket name"
        )
        storage_settings['bucket_name'] = bucket_name
        
        region = st.text_input(
            "AWS Region",
            value=current_storage.get('region', 'us-east-1'),
            help="AWS region"
        )
        storage_settings['region'] = region
    
    # Retention settings
    st.divider()
    st.write("**Document Retention**")
    
    enable_retention = st.checkbox(
        "Enable Automatic Cleanup",
        value=current_storage.get('enable_retention', False),
        help="Automatically delete old documents"
    )
    
    retention_days = None
    if enable_retention:
        retention_days = st.number_input(
            "Retention Period (days)",
            min_value=1,
            max_value=365,
            value=current_storage.get('retention_days', 90),
            help="Number of days to keep documents before deletion"
        )
    
    storage_settings['enable_retention'] = enable_retention
    storage_settings['retention_days'] = retention_days
    
    return {'storage': storage_settings}


