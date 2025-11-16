"""
Compliance Reports
GDPR compliance reports, security audit reports, access control reports
"""

import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path
import logging

from security.audit_log import audit_log_service, AuditEventType
from security.gdpr_compliance import gdpr_compliance_service
from security.authorization import authorization_service, Role

logger = logging.getLogger(__name__)


class ComplianceReportsService:
    """
    Service for generating compliance and security reports
    """
    
    def __init__(self):
        """Initialize compliance reports service"""
        logger.info("ComplianceReportsService initialized")
    
    def generate_gdpr_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate GDPR compliance report
        
        Args:
            start_date: Report start date
            end_date: Report end date
        
        Returns:
            GDPR compliance report
        """
        # Get GDPR requests in period
        gdpr_requests = [
            req for req in gdpr_compliance_service.gdpr_requests.values()
            if start_date <= datetime.fromisoformat(req["created_at"]) <= end_date
        ]
        
        # Get consent records
        consent_summary = {}
        for user_id, consents in gdpr_compliance_service.consent_records.items():
            consent_summary[user_id] = {
                "total_consents": len(consents),
                "active_consents": sum(1 for c in consents.values() if c.get("granted") and not c.get("withdrawn")),
                "withdrawn_consents": sum(1 for c in consents.values() if c.get("withdrawn"))
            }
        
        # Get data processing records
        processing_records = [
            record for record in gdpr_compliance_service.data_processing_records
            if start_date <= datetime.fromisoformat(record["timestamp"]) <= end_date
        ]
        
        return {
            "report_type": "gdpr_compliance",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "generated_at": datetime.utcnow().isoformat(),
            "gdpr_requests": {
                "total": len(gdpr_requests),
                "by_type": self._count_by_type(gdpr_requests, "request_type"),
                "pending": sum(1 for r in gdpr_requests if r["status"] == "pending"),
                "completed": sum(1 for r in gdpr_requests if r["status"] == "completed")
            },
            "consent_management": {
                "total_users": len(consent_summary),
                "summary": consent_summary
            },
            "data_processing": {
                "total_records": len(processing_records),
                "by_purpose": self._count_by_field(processing_records, "purpose")
            },
            "compliance_status": "compliant"  # Would need actual compliance checks
        }
    
    def generate_security_audit_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate security audit report
        
        Args:
            start_date: Report start date
            end_date: Report end date
        
        Returns:
            Security audit report
        """
        # Query audit logs
        audit_events = audit_log_service.query_audit_log(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        # Analyze events
        failed_auth = [
            e for e in audit_events
            if e.get("event_type") == AuditEventType.AUTHENTICATION.value and not e.get("success")
        ]
        
        security_events = [
            e for e in audit_events
            if e.get("event_type") == AuditEventType.SECURITY_EVENT.value
        ]
        
        data_access = [
            e for e in audit_events
            if e.get("event_type") == AuditEventType.DATA_ACCESS.value
        ]
        
        return {
            "report_type": "security_audit",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_events": len(audit_events),
                "failed_authentications": len(failed_auth),
                "security_events": len(security_events),
                "data_access_events": len(data_access)
            },
            "failed_authentications": {
                "count": len(failed_auth),
                "top_ips": self._get_top_ips(failed_auth, 10)
            },
            "security_events": {
                "count": len(security_events),
                "events": security_events[:20]  # Top 20
            },
            "data_access": {
                "count": len(data_access),
                "by_resource_type": self._count_by_field(data_access, "resource_type")
            }
        }
    
    def generate_access_control_report(self) -> Dict[str, Any]:
        """
        Generate access control report
        
        Returns:
            Access control report
        """
        # Get role permissions
        role_permissions = {}
        for role in Role:
            role_permissions[role.value] = [
                perm.value for perm in authorization_service.get_user_permissions([role])
            ]
        
        return {
            "report_type": "access_control",
            "generated_at": datetime.utcnow().isoformat(),
            "role_permissions": role_permissions,
            "total_roles": len(role_permissions),
            "total_permissions": len(authorization_service.role_permissions)
        }
    
    def generate_data_processing_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generate data processing report
        
        Args:
            start_date: Report start date
            end_date: Report end date
        
        Returns:
            Data processing report
        """
        processing_records = [
            record for record in gdpr_compliance_service.data_processing_records
            if start_date <= datetime.fromisoformat(record["timestamp"]) <= end_date
        ]
        
        return {
            "report_type": "data_processing",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "generated_at": datetime.utcnow().isoformat(),
            "total_processing_activities": len(processing_records),
            "by_purpose": self._count_by_field(processing_records, "purpose"),
            "by_legal_basis": self._count_by_field(processing_records, "legal_basis"),
            "by_data_category": self._count_by_field_list(processing_records, "data_categories")
        }
    
    def _count_by_type(self, items: List[Dict], field: str) -> Dict[str, int]:
        """Count items by type"""
        counts = {}
        for item in items:
            value = item.get(field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def _count_by_field(self, items: List[Dict], field: str) -> Dict[str, int]:
        """Count items by field value"""
        counts = {}
        for item in items:
            value = item.get(field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def _count_by_field_list(self, items: List[Dict], field: str) -> Dict[str, int]:
        """Count items by field list values"""
        counts = {}
        for item in items:
            values = item.get(field, [])
            if isinstance(values, list):
                for value in values:
                    counts[value] = counts.get(value, 0) + 1
        return counts
    
    def _get_top_ips(self, events: List[Dict], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top IPs by event count"""
        ip_counts = {}
        for event in events:
            ip = event.get("ip_address", "unknown")
            ip_counts[ip] = ip_counts.get(ip, 0) + 1
        
        sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"ip": ip, "count": count} for ip, count in sorted_ips[:limit]]


# Global instance
compliance_reports_service = ComplianceReportsService()

