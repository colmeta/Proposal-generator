"""
GDPR Compliance Service
Data subject rights, consent management, privacy policy integration
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class GDPRRequestType(str, Enum):
    """GDPR request types"""
    ACCESS = "access"  # Right to access
    DELETION = "deletion"  # Right to be forgotten
    PORTABILITY = "portability"  # Right to data portability
    RECTIFICATION = "rectification"  # Right to rectification
    RESTRICTION = "restriction"  # Right to restriction of processing


class GDPRComplianceService:
    """
    GDPR compliance service for handling data subject rights
    """
    
    def __init__(self):
        """Initialize GDPR compliance service"""
        self.consent_records: Dict[str, Dict[str, Any]] = {}  # user_id -> consent data
        self.gdpr_requests: Dict[str, Dict[str, Any]] = {}  # request_id -> request data
        self.data_processing_records: List[Dict[str, Any]] = []
        logger.info("GDPRComplianceService initialized")
    
    def record_consent(self, user_id: str, consent_type: str, granted: bool, purpose: str):
        """
        Record user consent
        
        Args:
            user_id: User ID
            consent_type: Type of consent (e.g., "data_processing", "marketing")
            granted: Whether consent was granted
            purpose: Purpose of data processing
        """
        if user_id not in self.consent_records:
            self.consent_records[user_id] = {}
        
        self.consent_records[user_id][consent_type] = {
            "granted": granted,
            "purpose": purpose,
            "timestamp": datetime.utcnow().isoformat(),
            "withdrawn": False
        }
        logger.info(f"Consent recorded for user {user_id}: {consent_type} = {granted}")
    
    def withdraw_consent(self, user_id: str, consent_type: str):
        """
        Withdraw user consent
        
        Args:
            user_id: User ID
            consent_type: Type of consent to withdraw
        """
        if user_id in self.consent_records:
            if consent_type in self.consent_records[user_id]:
                self.consent_records[user_id][consent_type]["withdrawn"] = True
                self.consent_records[user_id][consent_type]["withdrawn_at"] = datetime.utcnow().isoformat()
                logger.info(f"Consent withdrawn for user {user_id}: {consent_type}")
    
    def has_consent(self, user_id: str, consent_type: str) -> bool:
        """
        Check if user has given consent
        
        Args:
            user_id: User ID
            consent_type: Type of consent
        
        Returns:
            True if consent is granted and not withdrawn
        """
        if user_id not in self.consent_records:
            return False
        
        consent = self.consent_records[user_id].get(consent_type)
        if not consent:
            return False
        
        return consent.get("granted", False) and not consent.get("withdrawn", False)
    
    def create_gdpr_request(
        self,
        user_id: str,
        request_type: GDPRRequestType,
        description: Optional[str] = None
    ) -> str:
        """
        Create a GDPR request
        
        Args:
            user_id: User ID
            request_type: Type of GDPR request
            description: Optional description
        
        Returns:
            Request ID
        """
        import uuid
        request_id = str(uuid.uuid4())
        
        self.gdpr_requests[request_id] = {
            "request_id": request_id,
            "user_id": user_id,
            "request_type": request_type.value,
            "description": description,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": None
        }
        
        logger.info(f"GDPR request created: {request_id} ({request_type.value}) for user {user_id}")
        return request_id
    
    def handle_access_request(self, user_id: str, data_source: callable) -> Dict[str, Any]:
        """
        Handle right to access request (export all user data)
        
        Args:
            user_id: User ID
            data_source: Function to retrieve user data
        
        Returns:
            Exported user data
        """
        try:
            user_data = data_source(user_id)
            export_data = {
                "user_id": user_id,
                "exported_at": datetime.utcnow().isoformat(),
                "data": user_data,
                "consent_records": self.consent_records.get(user_id, {}),
                "data_processing_records": [
                    record for record in self.data_processing_records
                    if record.get("user_id") == user_id
                ]
            }
            logger.info(f"Data export completed for user {user_id}")
            return export_data
        except Exception as e:
            logger.error(f"Failed to export data for user {user_id}: {e}")
            raise
    
    def handle_deletion_request(self, user_id: str, delete_function: callable) -> bool:
        """
        Handle right to deletion request (right to be forgotten)
        
        Args:
            user_id: User ID
            delete_function: Function to delete user data
        
        Returns:
            True if deletion successful
        """
        try:
            # Delete user data
            delete_function(user_id)
            
            # Anonymize consent records (keep for legal compliance)
            if user_id in self.consent_records:
                self.consent_records[user_id] = {"anonymized": True, "anonymized_at": datetime.utcnow().isoformat()}
            
            # Anonymize GDPR requests
            for request_id, request in self.gdpr_requests.items():
                if request.get("user_id") == user_id:
                    request["user_id"] = "[ANONYMIZED]"
                    request["anonymized"] = True
            
            logger.info(f"Data deletion completed for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete data for user {user_id}: {e}")
            return False
    
    def handle_portability_request(self, user_id: str, data_source: callable) -> str:
        """
        Handle right to data portability request (export in machine-readable format)
        
        Args:
            user_id: User ID
            data_source: Function to retrieve user data
        
        Returns:
            JSON string of exported data
        """
        try:
            user_data = data_source(user_id)
            export_data = {
                "user_id": user_id,
                "exported_at": datetime.utcnow().isoformat(),
                "format": "json",
                "data": user_data
            }
            return json.dumps(export_data, indent=2)
        except Exception as e:
            logger.error(f"Failed to export portable data for user {user_id}: {e}")
            raise
    
    def record_data_processing(
        self,
        user_id: str,
        purpose: str,
        data_categories: List[str],
        legal_basis: str
    ):
        """
        Record data processing activity
        
        Args:
            user_id: User ID
            purpose: Purpose of processing
            data_categories: Categories of data processed
            legal_basis: Legal basis for processing
        """
        record = {
            "user_id": user_id,
            "purpose": purpose,
            "data_categories": data_categories,
            "legal_basis": legal_basis,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.data_processing_records.append(record)
        logger.debug(f"Data processing recorded for user {user_id}: {purpose}")
    
    def get_privacy_policy_summary(self) -> Dict[str, Any]:
        """
        Get privacy policy summary
        
        Returns:
            Privacy policy information
        """
        return {
            "data_controller": "Proposal Generator System",
            "data_processor": "Proposal Generator System",
            "purposes": [
                "Proposal generation",
                "User account management",
                "Service improvement"
            ],
            "legal_basis": [
                "Consent",
                "Contract performance",
                "Legitimate interests"
            ],
            "data_retention": "As specified in retention policies",
            "user_rights": [
                "Right to access",
                "Right to rectification",
                "Right to erasure",
                "Right to restrict processing",
                "Right to data portability",
                "Right to object"
            ],
            "contact": "privacy@proposal-generator.com"
        }


# Global instance
gdpr_compliance_service = GDPRComplianceService()

