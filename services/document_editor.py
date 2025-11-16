"""
Document Editor Service
Edit tracking, change merging, diff generation, and collaborative editing support.
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Try to import diff-match-patch
try:
    import diff_match_patch as dmp_module
    DMP_AVAILABLE = True
except ImportError:
    DMP_AVAILABLE = False
    logger.warning("diff-match-patch not available. Diff generation will be limited.")


class DocumentEditorService:
    """
    Document editor service with edit tracking, change merging,
    diff generation, and collaborative editing support.
    """
    
    def __init__(self):
        """Initialize document editor service"""
        self.dmp = dmp_module.diff_match_patch() if DMP_AVAILABLE else None
        self.edit_history: Dict[str, List[Dict[str, Any]]] = {}
    
    def track_edit(
        self,
        document_id: str,
        edit: Dict[str, Any],
        editor_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track a document edit
        
        Args:
            document_id: Document identifier
            edit: Edit operation {"type": "...", "section": "...", "old": "...", "new": "..."}
            editor_id: Optional editor identifier
            
        Returns:
            Edit tracking result
        """
        if document_id not in self.edit_history:
            self.edit_history[document_id] = []
        
        edit_record = {
            "edit_id": len(self.edit_history[document_id]) + 1,
            "editor_id": editor_id or "unknown",
            "edit": edit,
            "timestamp": datetime.now().isoformat()
        }
        
        self.edit_history[document_id].append(edit_record)
        
        logger.debug(f"Tracked edit {edit_record['edit_id']} for document {document_id}")
        
        return {
            "edit_id": edit_record["edit_id"],
            "document_id": document_id,
            "timestamp": edit_record["timestamp"],
            "success": True
        }
    
    def get_edit_history(
        self,
        document_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get edit history for a document
        
        Args:
            document_id: Document identifier
            limit: Optional limit on number of edits to return
            
        Returns:
            List of edit records
        """
        history = self.edit_history.get(document_id, [])
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def generate_diff(
        self,
        old_content: str,
        new_content: str,
        format: str = "unified"
    ) -> Dict[str, Any]:
        """
        Generate diff between two content versions
        
        Args:
            old_content: Old content (string)
            new_content: New content (string)
            format: Diff format ("unified", "html", "raw")
            
        Returns:
            Diff result
        """
        if not DMP_AVAILABLE:
            # Fallback: simple character-based diff
            return self._simple_diff(old_content, new_content)
        
        # Use diff-match-patch for better diff
        diffs = self.dmp.diff_main(old_content, new_content)
        self.dmp.diff_cleanupSemantic(diffs)
        
        if format == "html":
            html_diff = self.dmp.diff_prettyHtml(diffs)
            return {
                "format": "html",
                "diff": html_diff,
                "changes": self._parse_diffs(diffs)
            }
        elif format == "unified":
            unified_diff = self.dmp.diff_toDelta(diffs)
            return {
                "format": "unified",
                "diff": unified_diff,
                "changes": self._parse_diffs(diffs)
            }
        else:
            return {
                "format": "raw",
                "diff": diffs,
                "changes": self._parse_diffs(diffs)
            }
    
    def generate_json_diff(
        self,
        old_content: Dict[str, Any],
        new_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate diff for JSON/structured content
        
        Args:
            old_content: Old content (dict)
            new_content: New content (dict)
            
        Returns:
            JSON diff result
        """
        changes = []
        
        # Compare keys
        old_keys = set(old_content.keys()) if isinstance(old_content, dict) else set()
        new_keys = set(new_content.keys()) if isinstance(new_content, dict) else set()
        
        # Added keys
        for key in new_keys - old_keys:
            changes.append({
                "type": "added",
                "key": key,
                "value": new_content[key]
            })
        
        # Removed keys
        for key in old_keys - new_keys:
            changes.append({
                "type": "removed",
                "key": key,
                "value": old_content[key]
            })
        
        # Modified keys
        for key in old_keys & new_keys:
            old_val = old_content[key]
            new_val = new_content[key]
            
            if old_val != new_val:
                if isinstance(old_val, dict) and isinstance(new_val, dict):
                    # Recursive diff for nested dicts
                    nested_changes = self.generate_json_diff(old_val, new_val)
                    changes.append({
                        "type": "modified",
                        "key": key,
                        "changes": nested_changes.get("changes", [])
                    })
                elif isinstance(old_val, str) and isinstance(new_val, str):
                    # Text diff for strings
                    text_diff = self.generate_diff(old_val, new_val)
                    changes.append({
                        "type": "modified",
                        "key": key,
                        "old_value": old_val,
                        "new_value": new_val,
                        "text_diff": text_diff
                    })
                else:
                    changes.append({
                        "type": "modified",
                        "key": key,
                        "old_value": old_val,
                        "new_value": new_val
                    })
        
        return {
            "changes": changes,
            "summary": {
                "added": len([c for c in changes if c["type"] == "added"]),
                "removed": len([c for c in changes if c["type"] == "removed"]),
                "modified": len([c for c in changes if c["type"] == "modified"])
            }
        }
    
    def merge_changes(
        self,
        base_content: Dict[str, Any],
        changes: List[Dict[str, Any]],
        conflict_resolution: str = "last_wins"
    ) -> Dict[str, Any]:
        """
        Merge multiple changes into base content
        
        Args:
            base_content: Base content
            changes: List of changes to apply
            conflict_resolution: Conflict resolution strategy ("last_wins", "first_wins", "manual")
            
        Returns:
            Merged content and conflict report
        """
        merged = json.loads(json.dumps(base_content))  # Deep copy
        conflicts = []
        
        for change in changes:
            edit = change.get("edit", {})
            edit_type = edit.get("type")
            section = edit.get("section")
            old_value = edit.get("old")
            new_value = edit.get("new")
            
            if edit_type == "replace":
                if section in merged:
                    current_value = merged[section]
                    if current_value != old_value and conflict_resolution != "last_wins":
                        conflicts.append({
                            "section": section,
                            "expected": old_value,
                            "actual": current_value,
                            "proposed": new_value
                        })
                    merged[section] = new_value
                else:
                    merged[section] = new_value
            
            elif edit_type == "add":
                if section not in merged:
                    merged[section] = new_value
                else:
                    conflicts.append({
                        "section": section,
                        "conflict": "Section already exists",
                        "proposed": new_value
                    })
            
            elif edit_type == "delete":
                if section in merged:
                    if merged[section] != old_value and conflict_resolution != "last_wins":
                        conflicts.append({
                            "section": section,
                            "expected": old_value,
                            "actual": merged[section]
                        })
                    del merged[section]
                else:
                    conflicts.append({
                        "section": section,
                        "conflict": "Section does not exist"
                    })
        
        return {
            "merged_content": merged,
            "conflicts": conflicts,
            "has_conflicts": len(conflicts) > 0,
            "conflict_count": len(conflicts)
        }
    
    def apply_edit(
        self,
        content: Dict[str, Any],
        edit: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply a single edit to content
        
        Args:
            content: Content to edit
            edit: Edit operation
            
        Returns:
            Edited content
        """
        edited = json.loads(json.dumps(content))  # Deep copy
        
        edit_type = edit.get("type")
        section = edit.get("section")
        new_value = edit.get("new")
        
        if edit_type == "replace":
            if section in edited:
                edited[section] = new_value
        
        elif edit_type == "add":
            edited[section] = new_value
        
        elif edit_type == "delete":
            if section in edited:
                del edited[section]
        
        return edited
    
    def _simple_diff(self, old_content: str, new_content: str) -> Dict[str, Any]:
        """Simple character-based diff (fallback)"""
        changes = []
        
        if old_content != new_content:
            changes.append({
                "type": "modified",
                "description": "Content has changed",
                "old_length": len(old_content),
                "new_length": len(new_content)
            })
        
        return {
            "format": "simple",
            "diff": f"Content changed: {len(old_content)} -> {len(new_content)} characters",
            "changes": changes
        }
    
    def _parse_diffs(self, diffs: List[Tuple[int, str]]) -> List[Dict[str, Any]]:
        """Parse diff-match-patch diffs into structured format"""
        changes = []
        
        for op, text in diffs:
            if op == -1:  # Deletion
                changes.append({
                    "type": "deleted",
                    "text": text
                })
            elif op == 1:  # Insertion
                changes.append({
                    "type": "added",
                    "text": text
                })
            # op == 0 means no change, skip
        
        return changes


# Global document editor service instance
document_editor_service = DocumentEditorService()

