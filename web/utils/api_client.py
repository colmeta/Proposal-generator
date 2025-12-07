"""API client for backend communication"""
import requests
from typing import Dict, Any, Optional, List
import streamlit as st
from datetime import datetime


class APIClient:
    """Client for communicating with the backend API"""
    
    def __init__(self, base_url: str = "http://localhost:5000/api"):
        """Initialize API client
        
        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication if available"""
        headers = {"Content-Type": "application/json"}
        # Add authentication token if available in session state
        if hasattr(st, 'session_state') and 'api_token' in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.api_token}"
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response with error checking"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error: {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', error_msg)
            except:
                error_msg = response.text or error_msg
            raise Exception(error_msg) from e
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}") from e
    
    def create_proposal(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new proposal
        
        Args:
            proposal_data: Proposal data dictionary
            
        Returns:
            Created proposal data
        """
        response = self.session.post(
            f"{self.base_url}/proposals",
            json=proposal_data,
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def get_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Get proposal by ID
        
        Args:
            proposal_id: Proposal ID
            
        Returns:
            Proposal data
        """
        response = self.session.get(
            f"{self.base_url}/proposals/{proposal_id}",
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def list_proposals(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List all proposals
        
        Args:
            limit: Maximum number of proposals to return
            offset: Number of proposals to skip
            
        Returns:
            Dictionary with proposals list and metadata
        """
        response = self.session.get(
            f"{self.base_url}/proposals",
            params={"limit": limit, "offset": offset},
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def update_proposal(self, proposal_id: str, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a proposal
        
        Args:
            proposal_id: Proposal ID
            proposal_data: Updated proposal data
            
        Returns:
            Updated proposal data
        """
        response = self.session.put(
            f"{self.base_url}/proposals/{proposal_id}",
            json=proposal_data,
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def delete_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Delete a proposal
        
        Args:
            proposal_id: Proposal ID
            
        Returns:
            Deletion confirmation
        """
        response = self.session.delete(
            f"{self.base_url}/proposals/{proposal_id}",
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def create_job(self, proposal_id: str, job_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new job for proposal generation
        
        Args:
            proposal_id: Proposal ID
            job_data: Optional job configuration
            
        Returns:
            Created job data
        """
        payload = job_data or {}
        response = self.session.post(
            f"{self.base_url}/proposals/{proposal_id}/jobs",
            json=payload,
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Get job by ID
        
        Args:
            job_id: Job ID
            
        Returns:
            Job data with status
        """
        response = self.session.get(
            f"{self.base_url}/jobs/{job_id}",
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def list_jobs(self, proposal_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """List jobs
        
        Args:
            proposal_id: Optional proposal ID to filter by
            limit: Maximum number of jobs to return
            
        Returns:
            Dictionary with jobs list
        """
        params = {"limit": limit}
        if proposal_id:
            params["proposal_id"] = proposal_id
        
        response = self.session.get(
            f"{self.base_url}/jobs",
            params=params,
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status
        
        Args:
            job_id: Job ID
            
        Returns:
            Job status information
        """
        response = self.session.get(
            f"{self.base_url}/jobs/{job_id}/status",
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def download_document(self, document_id: str, format: str = "pdf") -> bytes:
        """Download a generated document
        
        Args:
            document_id: Document ID
            format: Document format (pdf, docx)
            
        Returns:
            Document file bytes
        """
        response = self.session.get(
            f"{self.base_url}/documents/{document_id}/download",
            params={"format": format},
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.content
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get document metadata
        
        Args:
            document_id: Document ID
            
        Returns:
            Document metadata
        """
        response = self.session.get(
            f"{self.base_url}/documents/{document_id}",
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def list_documents(self, proposal_id: Optional[str] = None) -> Dict[str, Any]:
        """List documents
        
        Args:
            proposal_id: Optional proposal ID to filter by
            
        Returns:
            Dictionary with documents list
        """
        params = {}
        if proposal_id:
            params["proposal_id"] = proposal_id
        
        response = self.session.get(
            f"{self.base_url}/documents",
            params=params,
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get user settings
        
        Returns:
            Settings data
        """
        response = self.session.get(
            f"{self.base_url}/settings",
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Update user settings
        
        Args:
            settings: Settings data
            
        Returns:
            Updated settings
        """
        response = self.session.put(
            f"{self.base_url}/settings",
            json=settings,
            headers=self._get_headers()
        )
        return self._handle_response(response)
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health
        
        Returns:
            Health status
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                headers=self._get_headers(),
                timeout=5
            )
            return self._handle_response(response)
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


def get_api_client() -> APIClient:
    """Get or create API client instance"""
    if 'api_client' not in st.session_state:
        base_url = st.session_state.get('api_base_url', 'http://localhost:5000/api')
        st.session_state.api_client = APIClient(base_url=base_url)
    return st.session_state.api_client



