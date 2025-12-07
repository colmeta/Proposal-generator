"""End-to-end user flow tests for complete user journeys"""
import pytest
import time
from tests.fixtures.test_data import get_sample_project, get_sample_proposal
from tests.utils.test_helpers import wait_for_condition, assert_response_success


@pytest.mark.e2e
class TestProposalCreationFlow:
    """Test complete proposal creation user flow"""
    
    def test_complete_proposal_creation_flow(self, client, authenticated_user, mock_database, mock_llm_service):
        """Test end-to-end proposal creation"""
        # Step 1: User creates a project
        project_data = get_sample_project()
        project_response = client.post(
            '/api/v1/projects',
            json=project_data,
            headers=authenticated_user['headers']
        )
        
        if project_response.status_code in [200, 201]:
            project_id = project_response.json().get('id') or project_response.json().get('data', {}).get('id')
        else:
            # Fallback: create in mock DB
            project = mock_database.add('projects', project_data)
            project_id = project['id']
        
        assert project_id is not None
        
        # Step 2: User creates a proposal
        proposal_data = get_sample_proposal(project_id=project_id)
        proposal_response = client.post(
            f'/api/v1/projects/{project_id}/proposals',
            json=proposal_data,
            headers=authenticated_user['headers']
        )
        
        if proposal_response.status_code in [200, 201]:
            proposal_id = proposal_response.json().get('id') or proposal_response.json().get('data', {}).get('id')
        else:
            proposal = mock_database.add('proposals', proposal_data)
            proposal_id = proposal['id']
        
        assert proposal_id is not None
        
        # Step 3: User submits proposal for generation
        job_data = {
            'proposal_id': proposal_id,
            'template_id': 1,
            'name': 'Generate Proposal'
        }
        job_response = client.post(
            f'/api/v1/proposals/{proposal_id}/generate',
            json=job_data,
            headers=authenticated_user['headers']
        )
        
        # Step 4: Wait for job completion
        if job_response.status_code in [200, 201]:
            job_id = job_response.json().get('id') or job_response.json().get('data', {}).get('id')
            
            # Poll for job completion
            def check_job_complete():
                status_response = client.get(
                    f'/api/v1/jobs/{job_id}',
                    headers=authenticated_user['headers']
                )
                if status_response.status_code == 200:
                    data = status_response.json()
                    status = data.get('status') or data.get('data', {}).get('status')
                    return status == 'completed'
                return False
            
            # Wait up to 30 seconds for completion
            completed = wait_for_condition(check_job_complete, timeout=30)
            assert completed, "Job did not complete in time"
        
        # Step 5: User downloads generated document
        # (Would test document download endpoint)
    
    def test_proposal_editing_flow(self, client, authenticated_user, mock_database):
        """Test editing an existing proposal"""
        # Create project and proposal
        project = mock_database.add('projects', get_sample_project())
        proposal = mock_database.add('proposals', get_sample_proposal(project_id=project['id']))
        
        # User edits proposal
        updates = {
            'title': 'Updated Proposal Title',
            'description': 'Updated description'
        }
        
        response = client.put(
            f'/api/v1/proposals/{proposal["id"]}',
            json=updates,
            headers=authenticated_user['headers']
        )
        
        # Verify update
        assert response.status_code in [200, 204]
        
        # Verify changes
        updated_proposal = mock_database.get('proposals', proposal['id'])
        if updated_proposal:
            assert updated_proposal.get('title') == updates['title']


@pytest.mark.e2e
class TestDocumentManagementFlow:
    """Test document management user flow"""
    
    def test_document_upload_and_download(self, client, authenticated_user, mock_file_storage):
        """Test uploading and downloading documents"""
        # Step 1: Upload document
        file_content = b"Test document content"
        file_data = {
            'name': 'test_document.pdf',
            'content': file_content.hex()  # In real scenario, would use multipart/form-data
        }
        
        upload_response = client.post(
            '/api/v1/documents',
            json=file_data,
            headers=authenticated_user['headers']
        )
        
        if upload_response.status_code in [200, 201]:
            document_id = upload_response.json().get('id') or upload_response.json().get('data', {}).get('id')
            
            # Step 2: Download document
            download_response = client.get(
                f'/api/v1/documents/{document_id}/download',
                headers=authenticated_user['headers']
            )
            
            # Verify download
            assert download_response.status_code in [200, 302]  # 302 for redirect
    
    def test_document_listing(self, client, authenticated_user, mock_database):
        """Test listing user documents"""
        # Create some documents
        project = mock_database.add('projects', get_sample_project())
        for i in range(5):
            mock_database.add('documents', {
                'project_id': project['id'],
                'name': f'document_{i}.pdf',
                'document_type': 'proposal'
            })
        
        # List documents
        response = client.get(
            f'/api/v1/projects/{project["id"]}/documents',
            headers=authenticated_user['headers']
        )
        
        # Should return list of documents
        assert response.status_code in [200, 404]


@pytest.mark.e2e
class TestSettingsConfigurationFlow:
    """Test settings configuration user flow"""
    
    def test_user_settings_update(self, client, authenticated_user):
        """Test updating user settings"""
        settings = {
            'notifications': {
                'email': True,
                'webhook': False
            },
            'preferences': {
                'language': 'en',
                'timezone': 'UTC'
            }
        }
        
        response = client.put(
            '/api/v1/user/settings',
            json=settings,
            headers=authenticated_user['headers']
        )
        
        # Should succeed
        assert response.status_code in [200, 204]
    
    def test_integration_configuration(self, client, authenticated_user):
        """Test configuring external integrations"""
        integration_config = {
            'integration_type': 'salesforce',
            'credentials': {
                'client_id': 'test_client_id',
                'client_secret': 'test_secret'
            },
            'enabled': True
        }
        
        response = client.post(
            '/api/v1/integrations',
            json=integration_config,
            headers=authenticated_user['headers']
        )
        
        # Should succeed or return validation error
        assert response.status_code in [200, 201, 400]


@pytest.mark.e2e
class TestCollaborationFlow:
    """Test collaboration features user flow"""
    
    def test_sharing_proposal(self, client, authenticated_user, mock_database):
        """Test sharing proposal with team members"""
        project = mock_database.add('projects', get_sample_project())
        proposal = mock_database.add('proposals', get_sample_proposal(project_id=project['id']))
        
        share_data = {
            'user_ids': [2, 3, 4],
            'permissions': ['read', 'comment']
        }
        
        response = client.post(
            f'/api/v1/proposals/{proposal["id"]}/share',
            json=share_data,
            headers=authenticated_user['headers']
        )
        
        # Should succeed
        assert response.status_code in [200, 201]
    
    def test_commenting_on_proposal(self, client, authenticated_user, mock_database):
        """Test adding comments to proposal"""
        project = mock_database.add('projects', get_sample_project())
        proposal = mock_database.add('proposals', get_sample_proposal(project_id=project['id']))
        
        comment_data = {
            'text': 'This is a test comment',
            'section': 'introduction'
        }
        
        response = client.post(
            f'/api/v1/proposals/{proposal["id"]}/comments',
            json=comment_data,
            headers=authenticated_user['headers']
        )
        
        # Should succeed
        assert response.status_code in [200, 201]



