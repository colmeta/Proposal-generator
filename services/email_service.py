"""
Email Service
Email delivery service with SendGrid integration and SMTP fallback.
Supports email templates, delivery tracking, and progress updates.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import SendGrid
try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logger.warning("SendGrid not available. Will use SMTP fallback.")

# Try to import SMTP
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email import encoders
    SMTP_AVAILABLE = True
except ImportError:
    SMTP_AVAILABLE = False
    logger.warning("SMTP libraries not available.")


class EmailService:
    """
    Email service with SendGrid integration and SMTP fallback.
    Supports templates, tracking, and delivery status.
    """
    
    def __init__(self):
        """Initialize email service"""
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@proposal-generator.com")
        self.from_name = os.getenv("FROM_NAME", "Proposal Generator")
        
        # Initialize SendGrid client if available
        self.sendgrid_client = None
        if SENDGRID_AVAILABLE and self.sendgrid_api_key:
            try:
                self.sendgrid_client = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
                logger.info("SendGrid client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize SendGrid: {e}")
                self.sendgrid_client = None
        
        # Delivery tracking
        self.delivery_log: List[Dict[str, Any]] = []
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        content_type: str = "html",
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send email using SendGrid or SMTP fallback
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            content: Email content (HTML or plain text)
            content_type: "html" or "text"
            from_email: Sender email (optional)
            from_name: Sender name (optional)
            attachments: List of attachments [{"filename": "...", "content": "...", "type": "..."}]
            template_data: Template data for template emails
            
        Returns:
            Delivery result with status and tracking info
        """
        from_email = from_email or self.from_email
        from_name = from_name or self.from_name
        
        # Try SendGrid first
        if self.sendgrid_client:
            try:
                return self._send_via_sendgrid(
                    to_email, subject, content, content_type,
                    from_email, from_name, attachments
                )
            except Exception as e:
                logger.warning(f"SendGrid send failed: {e}, falling back to SMTP")
        
        # Fallback to SMTP
        if SMTP_AVAILABLE:
            try:
                return self._send_via_smtp(
                    to_email, subject, content, content_type,
                    from_email, from_name, attachments
                )
            except Exception as e:
                logger.error(f"SMTP send failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "method": "smtp",
                    "timestamp": datetime.now().isoformat()
                }
        else:
            return {
                "success": False,
                "error": "No email service available (SendGrid and SMTP both unavailable)",
                "method": "none",
                "timestamp": datetime.now().isoformat()
            }
    
    def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        content: str,
        content_type: str,
        from_email: str,
        from_name: str,
        attachments: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Send email via SendGrid"""
        message = Mail(
            from_email=Email(from_email, from_name),
            to_emails=To(to_email),
            subject=subject,
            html_content=Content("text/html", content) if content_type == "html" else None,
            plain_text_content=Content("text/plain", content) if content_type == "text" else None
        )
        
        # Add attachments if provided
        if attachments:
            for att in attachments:
                message.add_attachment(att)
        
        response = self.sendgrid_client.send(message)
        
        result = {
            "success": response.status_code in [200, 201, 202],
            "status_code": response.status_code,
            "method": "sendgrid",
            "message_id": response.headers.get("X-Message-Id", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        # Log delivery
        self._log_delivery(to_email, subject, result)
        
        return result
    
    def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        content: str,
        content_type: str,
        from_email: str,
        from_name: str,
        attachments: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Send email via SMTP"""
        if not self.smtp_user or not self.smtp_password:
            raise ValueError("SMTP credentials not configured")
        
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add content
        if content_type == "html":
            msg.attach(MIMEText(content, 'html'))
        else:
            msg.attach(MIMEText(content, 'plain'))
        
        # Add attachments
        if attachments:
            for att in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(att.get("content", b""))
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {att.get("filename", "attachment")}'
                )
                msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        server.starttls()
        server.login(self.smtp_user, self.smtp_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        
        result = {
            "success": True,
            "method": "smtp",
            "timestamp": datetime.now().isoformat()
        }
        
        # Log delivery
        self._log_delivery(to_email, subject, result)
        
        return result
    
    def send_template_email(
        self,
        to_email: str,
        template_name: str,
        template_data: Dict[str, Any],
        subject: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send email using a template
        
        Args:
            to_email: Recipient email
            template_name: Template name (e.g., "proposal_ready", "status_update")
            template_data: Data to fill template
            subject: Optional custom subject
            attachments: Optional attachments
            
        Returns:
            Delivery result
        """
        # Load template
        template = self._load_template(template_name)
        
        # Fill template
        content = self._fill_template(template, template_data)
        
        # Get subject from template or use provided
        email_subject = subject or template_data.get("subject", "Email from Proposal Generator")
        
        return self.send_email(
            to_email=to_email,
            subject=email_subject,
            content=content,
            content_type="html",
            attachments=attachments
        )
    
    def send_proposal_ready_email(
        self,
        to_email: str,
        project_name: str,
        proposal_url: Optional[str] = None,
        download_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email when proposal is ready"""
        template_data = {
            "project_name": project_name,
            "proposal_url": proposal_url or "#",
            "download_url": download_url or "#",
            "subject": f"Your proposal for {project_name} is ready"
        }
        
        return self.send_template_email(
            to_email=to_email,
            template_name="proposal_ready",
            template_data=template_data
        )
    
    def send_status_update_email(
        self,
        to_email: str,
        project_name: str,
        status: str,
        message: str,
        progress: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send status update email"""
        template_data = {
            "project_name": project_name,
            "status": status,
            "message": message,
            "progress": progress or 0,
            "subject": f"Update: {project_name} - {status}"
        }
        
        return self.send_template_email(
            to_email=to_email,
            template_name="status_update",
            template_data=template_data
        )
    
    def _load_template(self, template_name: str) -> str:
        """Load email template"""
        # Default templates
        templates = {
            "proposal_ready": """
            <html>
            <body>
                <h2>Your Proposal is Ready!</h2>
                <p>Dear User,</p>
                <p>Your proposal for <strong>{{project_name}}</strong> has been completed and is ready for review.</p>
                {% if proposal_url %}
                <p><a href="{{proposal_url}}">View Proposal</a></p>
                {% endif %}
                {% if download_url %}
                <p><a href="{{download_url}}">Download Proposal</a></p>
                {% endif %}
                <p>Best regards,<br>Proposal Generator Team</p>
            </body>
            </html>
            """,
            "status_update": """
            <html>
            <body>
                <h2>Proposal Status Update</h2>
                <p>Dear User,</p>
                <p>Your proposal for <strong>{{project_name}}</strong> has been updated.</p>
                <p><strong>Status:</strong> {{status}}</p>
                <p>{{message}}</p>
                {% if progress %}
                <p>Progress: {{progress}}%</p>
                {% endif %}
                <p>Best regards,<br>Proposal Generator Team</p>
            </body>
            </html>
            """
        }
        
        return templates.get(template_name, templates["status_update"])
    
    def _fill_template(self, template: str, data: Dict[str, Any]) -> str:
        """Fill template with data"""
        content = template
        
        # Simple template replacement
        for key, value in data.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
            content = content.replace(f"{{{{ {key} }}}}", str(value))
        
        # Remove unused template blocks (simple implementation)
        import re
        content = re.sub(r'{% if \w+ %}.*?{% endif %}', '', content, flags=re.DOTALL)
        
        return content
    
    def _log_delivery(
        self,
        to_email: str,
        subject: str,
        result: Dict[str, Any]
    ):
        """Log email delivery"""
        log_entry = {
            "to": to_email,
            "subject": subject,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        self.delivery_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.delivery_log) > 1000:
            self.delivery_log = self.delivery_log[-1000:]
    
    def get_delivery_status(self, message_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get delivery status (if tracking available)
        
        Args:
            message_id: Optional message ID to track
            
        Returns:
            Delivery status information
        """
        if message_id:
            # Find specific message in log
            for entry in self.delivery_log:
                if entry["result"].get("message_id") == message_id:
                    return {
                        "found": True,
                        "entry": entry
                    }
            return {"found": False}
        else:
            return {
                "total_sent": len(self.delivery_log),
                "recent_entries": self.delivery_log[-10:]
            }


# Global email service instance
email_service = EmailService()

