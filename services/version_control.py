"""
Version Control Service
Document versioning, change tracking, version comparison, rollback capability,
and version history management.
"""

import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class VersionControlService:
    """
    Version control service for document versioning and change tracking.
    Supports versioning, comparison, rollback, and history management.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize version control service
        
        Args:
            storage_path: Path to store version history (defaults to ./storage/versions)
        """
        if storage_path is None:
            storage_path = "./storage/versions"
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Version control service initialized: {self.storage_path}")
    
    def create_version(
        self,
        document_id: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new version of a document
        
        Args:
            document_id: Document identifier
            content: Document content
            metadata: Optional metadata
            created_by: Optional creator identifier
            
        Returns:
            Version information
        """
        # Get current version number
        version_number = self._get_next_version_number(document_id)
        
        # Calculate content hash
        content_hash = self._calculate_hash(content)
        
        # Get previous version for change tracking
        previous_version = self.get_latest_version(document_id)
        changes = None
        if previous_version:
            changes = self._calculate_changes(
                previous_version.get("content", {}),
                content
            )
        
        # Create version record
        version = {
            "document_id": document_id,
            "version_number": version_number,
            "content": content,
            "content_hash": content_hash,
            "metadata": metadata or {},
            "created_by": created_by,
            "created_at": datetime.now().isoformat(),
            "changes": changes
        }
        
        # Save version
        self._save_version(version)
        
        # Update version index
        self._update_version_index(document_id, version_number)
        
        logger.info(f"Created version {version_number} for document {document_id}")
        
        return {
            "document_id": document_id,
            "version_number": version_number,
            "content_hash": content_hash,
            "created_at": version["created_at"],
            "changes_count": len(changes.get("changes", [])) if changes else 0
        }
    
    def get_version(
        self,
        document_id: str,
        version_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific version of a document
        
        Args:
            document_id: Document identifier
            version_number: Version number
            
        Returns:
            Version data or None if not found
        """
        version_path = self._get_version_path(document_id, version_number)
        
        if not version_path.exists():
            return None
        
        try:
            with open(version_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load version {version_number} for {document_id}: {e}")
            return None
    
    def get_latest_version(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest version of a document"""
        version_number = self._get_latest_version_number(document_id)
        if version_number is None:
            return None
        
        return self.get_version(document_id, version_number)
    
    def get_version_history(
        self,
        document_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get version history for a document
        
        Args:
            document_id: Document identifier
            limit: Optional limit on number of versions to return
            
        Returns:
            List of version summaries
        """
        index = self._load_version_index(document_id)
        if not index:
            return []
        
        versions = index.get("versions", [])
        
        # Sort by version number (descending)
        versions.sort(key=lambda v: v.get("version_number", 0), reverse=True)
        
        if limit:
            versions = versions[:limit]
        
        return versions
    
    def compare_versions(
        self,
        document_id: str,
        version1: int,
        version2: int
    ) -> Dict[str, Any]:
        """
        Compare two versions of a document
        
        Args:
            document_id: Document identifier
            version1: First version number
            version2: Second version number
            
        Returns:
            Comparison result with differences
        """
        v1_data = self.get_version(document_id, version1)
        v2_data = self.get_version(document_id, version2)
        
        if not v1_data or not v2_data:
            return {
                "error": "One or both versions not found",
                "version1_found": v1_data is not None,
                "version2_found": v2_data is not None
            }
        
        changes = self._calculate_changes(
            v1_data.get("content", {}),
            v2_data.get("content", {})
        )
        
        return {
            "version1": version1,
            "version2": version2,
            "version1_created_at": v1_data.get("created_at"),
            "version2_created_at": v2_data.get("created_at"),
            "changes": changes,
            "summary": {
                "total_changes": len(changes.get("changes", [])),
                "added": len([c for c in changes.get("changes", []) if c.get("type") == "added"]),
                "modified": len([c for c in changes.get("changes", []) if c.get("type") == "modified"]),
                "deleted": len([c for c in changes.get("changes", []) if c.get("type") == "deleted"])
            }
        }
    
    def rollback_to_version(
        self,
        document_id: str,
        version_number: int,
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rollback document to a specific version
        
        Args:
            document_id: Document identifier
            version_number: Version to rollback to
            created_by: Optional creator identifier
            
        Returns:
            New version created from rollback
        """
        target_version = self.get_version(document_id, version_number)
        if not target_version:
            return {
                "success": False,
                "error": f"Version {version_number} not found"
            }
        
        # Create new version from target version content
        new_version = self.create_version(
            document_id=document_id,
            content=target_version.get("content", {}),
            metadata={
                "rollback": True,
                "rollback_from_version": version_number,
                "original_created_at": target_version.get("created_at")
            },
            created_by=created_by or "system"
        )
        
        logger.info(f"Rolled back document {document_id} to version {version_number}, created new version {new_version['version_number']}")
        
        return {
            "success": True,
            "rollback_to_version": version_number,
            "new_version": new_version["version_number"],
            "message": f"Rolled back to version {version_number}, created new version {new_version['version_number']}"
        }
    
    def delete_version(
        self,
        document_id: str,
        version_number: int
    ) -> bool:
        """
        Delete a specific version (use with caution)
        
        Args:
            document_id: Document identifier
            version_number: Version number to delete
            
        Returns:
            True if deleted, False otherwise
        """
        version_path = self._get_version_path(document_id, version_number)
        
        if not version_path.exists():
            return False
        
        try:
            version_path.unlink()
            self._update_version_index_after_delete(document_id, version_number)
            logger.info(f"Deleted version {version_number} for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete version {version_number} for {document_id}: {e}")
            return False
    
    def _get_version_path(self, document_id: str, version_number: int) -> Path:
        """Get file path for a version"""
        doc_dir = self.storage_path / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)
        return doc_dir / f"v{version_number}.json"
    
    def _get_index_path(self, document_id: str) -> Path:
        """Get path for version index"""
        doc_dir = self.storage_path / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)
        return doc_dir / "index.json"
    
    def _save_version(self, version: Dict[str, Any]):
        """Save version to disk"""
        version_path = self._get_version_path(
            version["document_id"],
            version["version_number"]
        )
        
        with open(version_path, 'w', encoding='utf-8') as f:
            json.dump(version, f, indent=2, ensure_ascii=False)
    
    def _load_version_index(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Load version index"""
        index_path = self._get_index_path(document_id)
        
        if not index_path.exists():
            return None
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load version index for {document_id}: {e}")
            return None
    
    def _update_version_index(self, document_id: str, version_number: int):
        """Update version index"""
        index = self._load_version_index(document_id) or {
            "document_id": document_id,
            "versions": [],
            "latest_version": 0
        }
        
        # Add version summary
        version_summary = {
            "version_number": version_number,
            "created_at": datetime.now().isoformat()
        }
        
        index["versions"].append(version_summary)
        index["latest_version"] = version_number
        
        # Save index
        index_path = self._get_index_path(document_id)
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def _update_version_index_after_delete(self, document_id: str, version_number: int):
        """Update index after version deletion"""
        index = self._load_version_index(document_id)
        if not index:
            return
        
        # Remove version from index
        index["versions"] = [
            v for v in index["versions"]
            if v.get("version_number") != version_number
        ]
        
        # Update latest version if needed
        if index.get("latest_version") == version_number:
            if index["versions"]:
                index["latest_version"] = max(
                    v.get("version_number", 0) for v in index["versions"]
                )
            else:
                index["latest_version"] = 0
        
        # Save index
        index_path = self._get_index_path(document_id)
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def _get_next_version_number(self, document_id: str) -> int:
        """Get next version number"""
        latest = self._get_latest_version_number(document_id)
        return (latest or 0) + 1
    
    def _get_latest_version_number(self, document_id: str) -> Optional[int]:
        """Get latest version number"""
        index = self._load_version_index(document_id)
        if not index:
            return None
        
        return index.get("latest_version")
    
    def _calculate_hash(self, content: Any) -> str:
        """Calculate content hash"""
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()
    
    def _calculate_changes(
        self,
        old_content: Dict[str, Any],
        new_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate changes between two versions
        
        Args:
            old_content: Previous version content
            new_content: New version content
            
        Returns:
            Changes dictionary
        """
        changes = []
        
        # Simple change detection (can be enhanced with diff-match-patch)
        old_str = json.dumps(old_content, sort_keys=True)
        new_str = json.dumps(new_content, sort_keys=True)
        
        if old_str != new_str:
            # Content has changed
            changes.append({
                "type": "modified",
                "description": "Document content modified",
                "location": "document"
            })
        
        # More detailed change detection can be added here
        # For now, this is a simplified version
        
        return {
            "changes": changes,
            "has_changes": len(changes) > 0,
            "change_count": len(changes)
        }


# Global version control service instance
version_control_service = VersionControlService()

