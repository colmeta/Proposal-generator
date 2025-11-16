"""Project management tools integration module"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class PMIntegration(ABC):
    """Abstract base class for project management integrations"""
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with PM system"""
        pass
    
    @abstractmethod
    def create_project(self, project_data: Dict[str, Any]) -> Optional[str]:
        """Create a project"""
        pass
    
    @abstractmethod
    def create_task(self, project_id: str, task_data: Dict[str, Any]) -> Optional[str]:
        """Create a task in a project"""
        pass
    
    @abstractmethod
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Update a task"""
        pass
    
    @abstractmethod
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project details"""
        pass


class AsanaIntegration(PMIntegration):
    """Asana project management integration"""
    
    def __init__(self):
        self.access_token = None
        self.base_url = "https://app.asana.com/api/1.0"
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Asana using Personal Access Token"""
        access_token = credentials.get('access_token')
        if access_token:
            self.access_token = access_token
            logger.info("Asana authentication successful")
            return True
        else:
            logger.error("Asana access token not provided")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def create_project(self, project_data: Dict[str, Any]) -> Optional[str]:
        """Create a project in Asana"""
        if not self.access_token:
            return None
        
        try:
            workspace_id = project_data.pop('workspace_id', None)
            if not workspace_id:
                logger.error("Workspace ID required for Asana project creation")
                return None
            
            payload = {
                "data": {
                    "name": project_data.get('name'),
                    "workspace": workspace_id,
                    **project_data
                }
            }
            
            response = requests.post(
                f"{self.base_url}/projects",
                json=payload,
                headers=self._get_headers()
            )
            
            if response.status_code == 201:
                result = response.json()
                project_id = result['data']['gid']
                logger.info(f"Project created in Asana: {project_id}")
                return project_id
            else:
                logger.error(f"Failed to create project: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Asana project: {e}")
            return None
    
    def create_task(self, project_id: str, task_data: Dict[str, Any]) -> Optional[str]:
        """Create a task in Asana"""
        if not self.access_token:
            return None
        
        try:
            payload = {
                "data": {
                    "name": task_data.get('name'),
                    "projects": [project_id],
                    **{k: v for k, v in task_data.items() if k != 'name'}
                }
            }
            
            response = requests.post(
                f"{self.base_url}/tasks",
                json=payload,
                headers=self._get_headers()
            )
            
            if response.status_code == 201:
                result = response.json()
                task_id = result['data']['gid']
                logger.info(f"Task created in Asana: {task_id}")
                return task_id
            else:
                logger.error(f"Failed to create task: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Asana task: {e}")
            return None
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Update a task in Asana"""
        if not self.access_token:
            return False
        
        try:
            payload = {
                "data": task_data
            }
            
            response = requests.put(
                f"{self.base_url}/tasks/{task_id}",
                json=payload,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                logger.info(f"Task updated in Asana: {task_id}")
                return True
            else:
                logger.error(f"Failed to update task: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating Asana task: {e}")
            return False
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project details from Asana"""
        if not self.access_token:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/projects/{project_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('data')
            else:
                logger.error(f"Failed to get project: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Asana project: {e}")
            return None


class TrelloIntegration(PMIntegration):
    """Trello project management integration"""
    
    def __init__(self):
        self.api_key = None
        self.api_token = None
        self.base_url = "https://api.trello.com/1"
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Trello using API key and token"""
        api_key = credentials.get('api_key')
        api_token = credentials.get('api_token')
        
        if api_key and api_token:
            self.api_key = api_key
            self.api_token = api_token
            logger.info("Trello authentication successful")
            return True
        else:
            logger.error("Trello API key and token required")
            return False
    
    def _get_params(self) -> Dict[str, str]:
        """Get query parameters for API requests"""
        return {
            'key': self.api_key,
            'token': self.api_token
        }
    
    def create_project(self, project_data: Dict[str, str]) -> Optional[str]:
        """Create a board in Trello"""
        if not self.api_key or not self.api_token:
            return None
        
        try:
            params = self._get_params()
            params['name'] = project_data.get('name')
            params['defaultLists'] = 'true'
            
            response = requests.post(
                f"{self.base_url}/boards",
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                board_id = result['id']
                logger.info(f"Board created in Trello: {board_id}")
                return board_id
            else:
                logger.error(f"Failed to create board: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Trello board: {e}")
            return None
    
    def create_task(self, project_id: str, task_data: Dict[str, Any]) -> Optional[str]:
        """Create a card in Trello"""
        if not self.api_key or not self.api_token:
            return None
        
        try:
            # Get the first list (To Do) from the board
            params = self._get_params()
            response = requests.get(
                f"{self.base_url}/boards/{project_id}/lists",
                params=params
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to get board lists: {response.text}")
                return None
            
            lists = response.json()
            if not lists:
                logger.error("No lists found in board")
                return None
            
            list_id = lists[0]['id']
            
            # Create card
            card_params = self._get_params()
            card_params['name'] = task_data.get('name')
            card_params['desc'] = task_data.get('description', '')
            card_params['idList'] = list_id
            
            response = requests.post(
                f"{self.base_url}/cards",
                params=card_params
            )
            
            if response.status_code == 200:
                result = response.json()
                card_id = result['id']
                logger.info(f"Card created in Trello: {card_id}")
                return card_id
            else:
                logger.error(f"Failed to create card: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Trello card: {e}")
            return None
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Update a card in Trello"""
        if not self.api_key or not self.api_token:
            return False
        
        try:
            params = self._get_params()
            for key, value in task_data.items():
                params[key] = value
            
            response = requests.put(
                f"{self.base_url}/cards/{task_id}",
                params=params
            )
            
            if response.status_code == 200:
                logger.info(f"Card updated in Trello: {task_id}")
                return True
            else:
                logger.error(f"Failed to update card: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating Trello card: {e}")
            return False
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get board details from Trello"""
        if not self.api_key or not self.api_token:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/boards/{project_id}",
                params=self._get_params()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get board: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Trello board: {e}")
            return None


class JiraIntegration(PMIntegration):
    """Jira project management integration"""
    
    def __init__(self):
        self.base_url = None
        self.username = None
        self.api_token = None
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Jira using API token"""
        base_url = credentials.get('base_url')
        username = credentials.get('username')
        api_token = credentials.get('api_token')
        
        if base_url and username and api_token:
            self.base_url = base_url.rstrip('/')
            self.username = username
            self.api_token = api_token
            logger.info("Jira authentication successful")
            return True
        else:
            logger.error("Jira base_url, username, and api_token required")
            return False
    
    def _get_auth(self) -> tuple:
        """Get authentication tuple for requests"""
        return (self.username, self.api_token)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def create_project(self, project_data: Dict[str, Any]) -> Optional[str]:
        """Create a project in Jira"""
        if not self.base_url:
            return None
        
        try:
            payload = {
                "key": project_data.get('key'),
                "name": project_data.get('name'),
                "projectTypeKey": project_data.get('project_type', 'software'),
                "projectTemplateKey": project_data.get('template', 'com.pyxis.greenhopper.jira:gh-simplified-scrum-classic')
            }
            
            response = requests.post(
                f"{self.base_url}/rest/api/3/project",
                json=payload,
                auth=self._get_auth(),
                headers=self._get_headers()
            )
            
            if response.status_code == 201:
                result = response.json()
                project_key = result['key']
                logger.info(f"Project created in Jira: {project_key}")
                return project_key
            else:
                logger.error(f"Failed to create project: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Jira project: {e}")
            return None
    
    def create_task(self, project_id: str, task_data: Dict[str, Any]) -> Optional[str]:
        """Create an issue in Jira"""
        if not self.base_url:
            return None
        
        try:
            payload = {
                "fields": {
                    "project": {
                        "key": project_id
                    },
                    "summary": task_data.get('name'),
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": task_data.get('description', '')
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {
                        "name": task_data.get('issue_type', 'Task')
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/rest/api/3/issue",
                json=payload,
                auth=self._get_auth(),
                headers=self._get_headers()
            )
            
            if response.status_code == 201:
                result = response.json()
                issue_key = result['key']
                logger.info(f"Issue created in Jira: {issue_key}")
                return issue_key
            else:
                logger.error(f"Failed to create issue: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Jira issue: {e}")
            return None
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Update an issue in Jira"""
        if not self.base_url:
            return False
        
        try:
            fields = {}
            if 'name' in task_data:
                fields['summary'] = task_data['name']
            if 'description' in task_data:
                fields['description'] = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": task_data['description']
                                }
                            ]
                        }
                    ]
                }
            
            payload = {
                "fields": fields
            }
            
            response = requests.put(
                f"{self.base_url}/rest/api/3/issue/{task_id}",
                json=payload,
                auth=self._get_auth(),
                headers=self._get_headers()
            )
            
            if response.status_code == 204:
                logger.info(f"Issue updated in Jira: {task_id}")
                return True
            else:
                logger.error(f"Failed to update issue: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating Jira issue: {e}")
            return False
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project details from Jira"""
        if not self.base_url:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/rest/api/3/project/{project_id}",
                auth=self._get_auth(),
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get project: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting Jira project: {e}")
            return None

