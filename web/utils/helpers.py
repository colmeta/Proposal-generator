"""Helper functions for web interface"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import re
import streamlit as st


def format_date(date_str: Optional[str], date_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format date string for display
    
    Args:
        date_str: Date string or None
        date_format: Date format string
        
    Returns:
        Formatted date string or "N/A"
    """
    if not date_str:
        return "N/A"
    
    try:
        if isinstance(date_str, str):
            # Try parsing ISO format
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = date_str
        
        return dt.strftime(date_format)
    except Exception:
        return str(date_str)


def format_relative_time(date_str: Optional[str]) -> str:
    """Format date as relative time (e.g., "2 hours ago")
    
    Args:
        date_str: Date string or None
        
    Returns:
        Relative time string
    """
    if not date_str:
        return "N/A"
    
    try:
        if isinstance(date_str, str):
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt = date_str
        
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
    except Exception:
        return str(date_str)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def validate_email(email: str) -> bool:
    """Validate email address
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    return bool(re.match(pattern, url))


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, Optional[str]]:
    """Validate that required fields are present
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "GBP":
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def get_status_color(status: str) -> str:
    """Get color for status badge
    
    Args:
        status: Status string
        
    Returns:
        Color name for Streamlit
    """
    status_lower = status.lower()
    if status_lower in ['completed', 'success', 'done']:
        return "green"
    elif status_lower in ['pending', 'queued', 'waiting']:
        return "orange"
    elif status_lower in ['processing', 'running', 'in_progress']:
        return "blue"
    elif status_lower in ['failed', 'error', 'cancelled']:
        return "red"
    else:
        return "gray"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    return filename


def parse_budget(budget_str: str) -> Optional[float]:
    """Parse budget string to float
    
    Args:
        budget_str: Budget string (may contain currency symbols)
        
    Returns:
        Budget as float or None if invalid
    """
    if not budget_str:
        return None
    
    # Remove currency symbols and commas
    cleaned = re.sub(r'[$,€£¥,\s]', '', str(budget_str))
    try:
        return float(cleaned)
    except ValueError:
        return None


def format_progress(completed: int, total: int) -> str:
    """Format progress as percentage
    
    Args:
        completed: Number of completed items
        total: Total number of items
        
    Returns:
        Progress percentage string
    """
    if total == 0:
        return "0%"
    percentage = (completed / total) * 100
    return f"{percentage:.1f}%"


def get_error_message(error: Exception) -> str:
    """Extract user-friendly error message from exception
    
    Args:
        error: Exception object
        
    Returns:
        Error message string
    """
    error_str = str(error)
    # Try to extract meaningful error message
    if "HTTP Error" in error_str:
        return error_str
    elif "Request failed" in error_str:
        return "Unable to connect to the server. Please check your connection."
    else:
        return error_str or "An unexpected error occurred."


def show_error(message: str):
    """Display error message in Streamlit
    
    Args:
        message: Error message to display
    """
    st.error(f"❌ {message}")


def show_success(message: str):
    """Display success message in Streamlit
    
    Args:
        message: Success message to display
    """
    st.success(f"✅ {message}")


def show_warning(message: str):
    """Display warning message in Streamlit
    
    Args:
        message: Warning message to display
    """
    st.warning(f"⚠️ {message}")


def show_info(message: str):
    """Display info message in Streamlit
    
    Args:
        message: Info message to display
    """
    st.info(f"ℹ️ {message}")

