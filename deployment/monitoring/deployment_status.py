"""Deployment status tracking and monitoring"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class DeploymentStatus:
    """Tracks deployment status and health"""
    
    def __init__(self, status_file: str = '/tmp/deployment_status.json'):
        self.status_file = Path(status_file)
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current deployment status"""
        if not self.status_file.exists():
            return {
                'status': 'unknown',
                'version': 'unknown',
                'deployed_at': None,
                'health': 'unknown'
            }
        
        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {
                'status': 'error',
                'version': 'unknown',
                'deployed_at': None,
                'health': 'error'
            }
    
    def update_status(self, status: str, version: Optional[str] = None, health: Optional[str] = None) -> None:
        """Update deployment status"""
        current = self.get_status()
        
        current['status'] = status
        current['updated_at'] = datetime.utcnow().isoformat()
        
        if version:
            current['version'] = version
        
        if health:
            current['health'] = health
        
        if status == 'deployed':
            current['deployed_at'] = datetime.utcnow().isoformat()
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(current, f, indent=2)
        except Exception as e:
            print(f"Failed to update deployment status: {e}")
    
    def mark_deploying(self, version: str) -> None:
        """Mark deployment as in progress"""
        self.update_status('deploying', version=version, health='checking')
    
    def mark_deployed(self, version: str, health: str = 'healthy') -> None:
        """Mark deployment as complete"""
        self.update_status('deployed', version=version, health=health)
    
    def mark_failed(self, version: str, error: str) -> None:
        """Mark deployment as failed"""
        self.update_status('failed', version=version, health='unhealthy')
        current = self.get_status()
        current['error'] = error
        try:
            with open(self.status_file, 'w') as f:
                json.dump(current, f, indent=2)
        except Exception:
            pass
    
    def mark_rolling_back(self, version: str) -> None:
        """Mark rollback as in progress"""
        self.update_status('rolling_back', version=version, health='checking')
    
    def get_version(self) -> str:
        """Get current deployed version"""
        status = self.get_status()
        return status.get('version', 'unknown')
    
    def is_healthy(self) -> bool:
        """Check if deployment is healthy"""
        status = self.get_status()
        return status.get('health') == 'healthy' and status.get('status') == 'deployed'



