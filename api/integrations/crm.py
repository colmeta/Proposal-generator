"""CRM integration module"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class CRMIntegration(ABC):
    """Abstract base class for CRM integrations"""
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with CRM system"""
        pass
    
    @abstractmethod
    def create_contact(self, contact_data: Dict[str, Any]) -> Optional[str]:
        """Create a contact in CRM"""
        pass
    
    @abstractmethod
    def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> bool:
        """Update a contact in CRM"""
        pass
    
    @abstractmethod
    def create_deal(self, deal_data: Dict[str, Any]) -> Optional[str]:
        """Create a deal/opportunity in CRM"""
        pass
    
    @abstractmethod
    def update_deal(self, deal_id: str, deal_data: Dict[str, Any]) -> bool:
        """Update a deal/opportunity in CRM"""
        pass
    
    @abstractmethod
    def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact details from CRM"""
        pass
    
    @abstractmethod
    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Search for contacts in CRM"""
        pass


class SalesforceIntegration(CRMIntegration):
    """Salesforce CRM integration"""
    
    def __init__(self):
        self.base_url = None
        self.access_token = None
        self.instance_url = None
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Salesforce using OAuth 2.0"""
        try:
            client_id = credentials.get('client_id')
            client_secret = credentials.get('client_secret')
            username = credentials.get('username')
            password = credentials.get('password')
            security_token = credentials.get('security_token', '')
            sandbox = credentials.get('sandbox', False)
            
            login_url = 'https://test.salesforce.com' if sandbox else 'https://login.salesforce.com'
            
            response = requests.post(
                f"{login_url}/services/oauth2/token",
                data={
                    'grant_type': 'password',
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'username': username,
                    'password': password + security_token
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                self.instance_url = data['instance_url']
                self.base_url = f"{self.instance_url}/services/data/v57.0"
                logger.info("Salesforce authentication successful")
                return True
            else:
                logger.error(f"Salesforce authentication failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Salesforce authentication error: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Optional[str]:
        """Create a contact in Salesforce"""
        if not self.access_token:
            logger.error("Not authenticated with Salesforce")
            return None
        
        try:
            response = requests.post(
                f"{self.base_url}/sobjects/Contact/",
                json=contact_data,
                headers=self._get_headers()
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"Contact created in Salesforce: {result['id']}")
                return result['id']
            else:
                logger.error(f"Failed to create contact: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Salesforce contact: {e}")
            return None
    
    def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> bool:
        """Update a contact in Salesforce"""
        if not self.access_token:
            return False
        
        try:
            response = requests.patch(
                f"{self.base_url}/sobjects/Contact/{contact_id}",
                json=contact_data,
                headers=self._get_headers()
            )
            
            if response.status_code == 204:
                logger.info(f"Contact updated in Salesforce: {contact_id}")
                return True
            else:
                logger.error(f"Failed to update contact: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating Salesforce contact: {e}")
            return False
    
    def create_deal(self, deal_data: Dict[str, Any]) -> Optional[str]:
        """Create an opportunity in Salesforce"""
        if not self.access_token:
            return None
        
        try:
            response = requests.post(
                f"{self.base_url}/sobjects/Opportunity/",
                json=deal_data,
                headers=self._get_headers()
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"Opportunity created in Salesforce: {result['id']}")
                return result['id']
            else:
                logger.error(f"Failed to create opportunity: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Salesforce opportunity: {e}")
            return None
    
    def update_deal(self, deal_id: str, deal_data: Dict[str, Any]) -> bool:
        """Update an opportunity in Salesforce"""
        if not self.access_token:
            return False
        
        try:
            response = requests.patch(
                f"{self.base_url}/sobjects/Opportunity/{deal_id}",
                json=deal_data,
                headers=self._get_headers()
            )
            
            if response.status_code == 204:
                logger.info(f"Opportunity updated in Salesforce: {deal_id}")
                return True
            else:
                logger.error(f"Failed to update opportunity: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating Salesforce opportunity: {e}")
            return False
    
    def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact details from Salesforce"""
        if not self.access_token:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/sobjects/Contact/{contact_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get contact: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Salesforce contact: {e}")
            return None
    
    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Search for contacts in Salesforce using SOQL"""
        if not self.access_token:
            return []
        
        try:
            soql_query = f"SELECT Id, FirstName, LastName, Email, Phone FROM Contact WHERE Name LIKE '%{query}%' OR Email LIKE '%{query}%' LIMIT 10"
            response = requests.get(
                f"{self.base_url}/query",
                params={'q': soql_query},
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('records', [])
            else:
                logger.error(f"Failed to search contacts: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Salesforce contacts: {e}")
            return []


class HubSpotIntegration(CRMIntegration):
    """HubSpot CRM integration"""
    
    def __init__(self):
        self.api_key = None
        self.base_url = "https://api.hubapi.com"
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with HubSpot using API key"""
        api_key = credentials.get('api_key')
        if api_key:
            self.api_key = api_key
            logger.info("HubSpot authentication successful")
            return True
        else:
            logger.error("HubSpot API key not provided")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_contact(self, contact_data: Dict[str, Any]) -> Optional[str]:
        """Create a contact in HubSpot"""
        if not self.api_key:
            return None
        
        try:
            # HubSpot expects properties format
            properties = []
            for key, value in contact_data.items():
                properties.append({"property": key, "value": value})
            
            response = requests.post(
                f"{self.base_url}/contacts/v1/contact",
                json={"properties": properties},
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                vid = result.get('vid')
                logger.info(f"Contact created in HubSpot: {vid}")
                return str(vid)
            else:
                logger.error(f"Failed to create contact: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating HubSpot contact: {e}")
            return None
    
    def update_contact(self, contact_id: str, contact_data: Dict[str, Any]) -> bool:
        """Update a contact in HubSpot"""
        if not self.api_key:
            return False
        
        try:
            properties = []
            for key, value in contact_data.items():
                properties.append({"property": key, "value": value})
            
            response = requests.post(
                f"{self.base_url}/contacts/v1/contact/vid/{contact_id}/profile",
                json={"properties": properties},
                headers=self._get_headers()
            )
            
            if response.status_code == 204:
                logger.info(f"Contact updated in HubSpot: {contact_id}")
                return True
            else:
                logger.error(f"Failed to update contact: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating HubSpot contact: {e}")
            return False
    
    def create_deal(self, deal_data: Dict[str, Any]) -> Optional[str]:
        """Create a deal in HubSpot"""
        if not self.api_key:
            return None
        
        try:
            properties = []
            for key, value in deal_data.items():
                properties.append({"name": key, "value": value})
            
            response = requests.post(
                f"{self.base_url}/deals/v1/deal",
                json={"properties": properties},
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                deal_id = result.get('dealId')
                logger.info(f"Deal created in HubSpot: {deal_id}")
                return str(deal_id)
            else:
                logger.error(f"Failed to create deal: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating HubSpot deal: {e}")
            return None
    
    def update_deal(self, deal_id: str, deal_data: Dict[str, Any]) -> bool:
        """Update a deal in HubSpot"""
        if not self.api_key:
            return False
        
        try:
            properties = []
            for key, value in deal_data.items():
                properties.append({"name": key, "value": value})
            
            response = requests.put(
                f"{self.base_url}/deals/v1/deal/{deal_id}",
                json={"properties": properties},
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                logger.info(f"Deal updated in HubSpot: {deal_id}")
                return True
            else:
                logger.error(f"Failed to update deal: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating HubSpot deal: {e}")
            return False
    
    def get_contact(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Get contact details from HubSpot"""
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/contacts/v1/contact/vid/{contact_id}/profile",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get contact: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting HubSpot contact: {e}")
            return None
    
    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Search for contacts in HubSpot"""
        if not self.api_key:
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/contacts/v1/search/query",
                params={'q': query},
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('contacts', [])
            else:
                logger.error(f"Failed to search contacts: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching HubSpot contacts: {e}")
            return []

