"""
Storage Service
File storage service with local filesystem storage and optional S3 integration
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List, BinaryIO
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """
    Storage service for file operations
    Supports local filesystem storage and optional S3 integration
    """
    
    def __init__(self, base_path: Optional[str] = None, use_s3: bool = False):
        """
        Initialize storage service
        
        Args:
            base_path: Base path for local storage (defaults to ./storage)
            use_s3: Whether to use S3 storage (requires boto3 and AWS credentials)
        """
        if base_path is None:
            base_path = os.getenv("STORAGE_PATH", "./storage")
        
        self.base_path = Path(base_path)
        self.use_s3 = use_s3
        
        # Create base directory if it doesn't exist
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # S3 configuration (optional)
        if self.use_s3:
            try:
                import boto3
                self.s3_client = boto3.client('s3')
                self.s3_bucket = os.getenv("S3_BUCKET_NAME")
                if not self.s3_bucket:
                    logger.warning("S3 enabled but S3_BUCKET_NAME not set. Falling back to local storage.")
                    self.use_s3 = False
            except ImportError:
                logger.warning("boto3 not installed. S3 storage disabled. Falling back to local storage.")
                self.use_s3 = False
        
        logger.info(f"Storage service initialized: base_path={self.base_path}, use_s3={self.use_s3}")
    
    def _get_local_path(self, file_path: str) -> Path:
        """
        Get local file path
        
        Args:
            file_path: Relative file path
        
        Returns:
            Full local path
        """
        full_path = self.base_path / file_path
        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        return full_path
    
    def save(
        self,
        file_path: str,
        content: Any,
        is_json: bool = False,
        mode: str = "w"
    ) -> str:
        """
        Save content to file
        
        Args:
            file_path: Relative file path
            content: Content to save (string, bytes, or dict/list for JSON)
            is_json: If True, save as JSON
            mode: File mode ('w' for text, 'wb' for binary)
        
        Returns:
            Saved file path
        """
        try:
            if self.use_s3:
                return self._save_to_s3(file_path, content, is_json, mode)
            else:
                return self._save_to_local(file_path, content, is_json, mode)
        except Exception as e:
            logger.error(f"Failed to save file {file_path}: {e}")
            raise
    
    def _save_to_local(
        self,
        file_path: str,
        content: Any,
        is_json: bool,
        mode: str
    ) -> str:
        """Save to local filesystem"""
        full_path = self._get_local_path(file_path)
        
        if is_json:
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
        elif mode == 'wb':
            with open(full_path, 'wb') as f:
                if isinstance(content, str):
                    content = content.encode('utf-8')
                f.write(content)
        else:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(str(content))
        
        logger.debug(f"Saved file to local storage: {full_path}")
        return str(full_path)
    
    def _save_to_s3(
        self,
        file_path: str,
        content: Any,
        is_json: bool,
        mode: str
    ) -> str:
        """Save to S3"""
        if is_json:
            content = json.dumps(content, indent=2, ensure_ascii=False).encode('utf-8')
            content_type = 'application/json'
        elif mode == 'wb':
            if isinstance(content, str):
                content = content.encode('utf-8')
            content_type = 'application/octet-stream'
        else:
            content = str(content).encode('utf-8')
            content_type = 'text/plain'
        
        self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=file_path,
            Body=content,
            ContentType=content_type
        )
        
        logger.debug(f"Saved file to S3: s3://{self.s3_bucket}/{file_path}")
        return f"s3://{self.s3_bucket}/{file_path}"
    
    def load(
        self,
        file_path: str,
        is_json: bool = False,
        mode: str = "r"
    ) -> Any:
        """
        Load content from file
        
        Args:
            file_path: Relative file path
            is_json: If True, load as JSON
            mode: File mode ('r' for text, 'rb' for binary)
        
        Returns:
            File content
        """
        try:
            if self.use_s3:
                return self._load_from_s3(file_path, is_json, mode)
            else:
                return self._load_from_local(file_path, is_json, mode)
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {e}")
            raise
    
    def _load_from_local(
        self,
        file_path: str,
        is_json: bool,
        mode: str
    ) -> Any:
        """Load from local filesystem"""
        full_path = self._get_local_path(file_path)
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        
        if is_json:
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif mode == 'rb':
            with open(full_path, 'rb') as f:
                return f.read()
        else:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def _load_from_s3(
        self,
        file_path: str,
        is_json: bool,
        mode: str
    ) -> Any:
        """Load from S3"""
        response = self.s3_client.get_object(
            Bucket=self.s3_bucket,
            Key=file_path
        )
        content = response['Body'].read()
        
        if is_json:
            return json.loads(content.decode('utf-8'))
        elif mode == 'rb':
            return content
        else:
            return content.decode('utf-8')
    
    def delete(self, file_path: str) -> bool:
        """
        Delete a file
        
        Args:
            file_path: Relative file path
        
        Returns:
            True if deleted, False if not found
        """
        try:
            if self.use_s3:
                return self._delete_from_s3(file_path)
            else:
                return self._delete_from_local(file_path)
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    def _delete_from_local(self, file_path: str) -> bool:
        """Delete from local filesystem"""
        full_path = self._get_local_path(file_path)
        if full_path.exists():
            if full_path.is_file():
                full_path.unlink()
            else:
                shutil.rmtree(full_path)
            logger.debug(f"Deleted file from local storage: {full_path}")
            return True
        return False
    
    def _delete_from_s3(self, file_path: str) -> bool:
        """Delete from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.s3_bucket,
                Key=file_path
            )
            logger.debug(f"Deleted file from S3: s3://{self.s3_bucket}/{file_path}")
            return True
        except self.s3_client.exceptions.NoSuchKey:
            return False
    
    def list_files(self, directory: str = "", pattern: Optional[str] = None) -> List[str]:
        """
        List files in a directory
        
        Args:
            directory: Directory path (relative to base_path)
            pattern: Optional glob pattern to filter files
        
        Returns:
            List of file paths (relative to base_path)
        """
        try:
            if self.use_s3:
                return self._list_s3_files(directory, pattern)
            else:
                return self._list_local_files(directory, pattern)
        except Exception as e:
            logger.error(f"Failed to list files in {directory}: {e}")
            return []
    
    def _list_local_files(self, directory: str, pattern: Optional[str]) -> List[str]:
        """List files in local directory"""
        dir_path = self._get_local_path(directory)
        if not dir_path.exists():
            return []
        
        if pattern:
            files = list(dir_path.glob(pattern))
        else:
            files = list(dir_path.rglob('*'))
        
        # Return relative paths
        base_len = len(str(self.base_path)) + 1
        return [str(f)[base_len:] for f in files if f.is_file()]
    
    def _list_s3_files(self, directory: str, pattern: Optional[str]) -> List[str]:
        """List files in S3 directory"""
        prefix = directory.rstrip('/') + '/' if directory else ''
        
        response = self.s3_client.list_objects_v2(
            Bucket=self.s3_bucket,
            Prefix=prefix
        )
        
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                file_path = obj['Key']
                if pattern:
                    if pattern in file_path:
                        files.append(file_path)
                else:
                    files.append(file_path)
        
        return files
    
    def exists(self, file_path: str) -> bool:
        """
        Check if file exists
        
        Args:
            file_path: Relative file path
        
        Returns:
            True if file exists, False otherwise
        """
        try:
            if self.use_s3:
                try:
                    self.s3_client.head_object(
                        Bucket=self.s3_bucket,
                        Key=file_path
                    )
                    return True
                except self.s3_client.exceptions.NoSuchKey:
                    return False
            else:
                full_path = self._get_local_path(file_path)
                return full_path.exists()
        except Exception:
            return False
    
    def get_project_storage_path(self, project_id: int) -> str:
        """
        Get storage path for a project
        
        Args:
            project_id: Project ID
        
        Returns:
            Storage path for the project
        """
        return f"projects/{project_id}"
    
    def get_document_path(self, project_id: int, document_id: int, version: Optional[int] = None) -> str:
        """
        Get storage path for a document
        
        Args:
            project_id: Project ID
            document_id: Document ID
            version: Optional version number
        
        Returns:
            Storage path for the document
        """
        base_path = self.get_project_storage_path(project_id)
        if version:
            return f"{base_path}/documents/{document_id}_v{version}.json"
        return f"{base_path}/documents/{document_id}.json"


# Global storage service instance
storage_service = StorageService()

