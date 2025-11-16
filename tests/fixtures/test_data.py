"""Test data fixtures for proposals, funders, users, and mock LLM responses"""
from faker import Faker
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

fake = Faker()


def get_sample_user(user_id: int = None) -> Dict[str, Any]:
    """Generate sample user data"""
    return {
        'id': user_id or fake.random_int(min=1, max=10000),
        'username': fake.user_name(),
        'email': fake.email(),
        'password': fake.password(length=12),
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'role': random.choice(['user', 'admin', 'editor']),
        'created_at': datetime.utcnow().isoformat(),
        'active': True
    }


def get_sample_funder(funder_id: int = None) -> Dict[str, Any]:
    """Generate sample funder data"""
    return {
        'id': funder_id or fake.random_int(min=1, max=10000),
        'name': fake.company(),
        'description': fake.text(max_nb_chars=500),
        'website': fake.url(),
        'email': fake.email(),
        'phone': fake.phone_number(),
        'address': fake.address(),
        'funding_areas': random.sample([
            'Technology', 'Healthcare', 'Education', 'Environment',
            'Arts', 'Social Services', 'Research', 'Innovation'
        ], k=random.randint(2, 5)),
        'funding_range_min': fake.random_int(min=10000, max=100000),
        'funding_range_max': fake.random_int(min=100000, max=1000000),
        'deadline': (datetime.utcnow() + timedelta(days=random.randint(30, 365))).isoformat(),
        'requirements': fake.text(max_nb_chars=300),
        'created_at': datetime.utcnow().isoformat()
    }


def get_sample_proposal(proposal_id: int = None, project_id: int = None, user_id: int = None) -> Dict[str, Any]:
    """Generate sample proposal data"""
    return {
        'id': proposal_id or fake.random_int(min=1, max=10000),
        'project_id': project_id or fake.random_int(min=1, max=1000),
        'user_id': user_id or fake.random_int(min=1, max=100),
        'title': fake.sentence(nb_words=6),
        'description': fake.text(max_nb_chars=1000),
        'funder_id': fake.random_int(min=1, max=100),
        'status': random.choice(['draft', 'in_progress', 'submitted', 'approved', 'rejected']),
        'budget': fake.random_int(min=50000, max=500000),
        'duration_months': random.randint(6, 36),
        'objectives': [fake.sentence() for _ in range(random.randint(3, 7))],
        'methodology': fake.text(max_nb_chars=800),
        'expected_outcomes': [fake.sentence() for _ in range(random.randint(2, 5))],
        'team_members': [
            {
                'name': fake.name(),
                'role': random.choice(['Principal Investigator', 'Co-Investigator', 'Researcher', 'Consultant']),
                'qualifications': fake.text(max_nb_chars=200)
            }
            for _ in range(random.randint(2, 5))
        ],
        'timeline': [
            {
                'phase': f'Phase {i+1}',
                'description': fake.sentence(),
                'start_date': (datetime.utcnow() + timedelta(days=i*30)).isoformat(),
                'end_date': (datetime.utcnow() + timedelta(days=(i+1)*30)).isoformat()
            }
            for i in range(random.randint(3, 6))
        ],
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }


def get_sample_project(project_id: int = None, user_id: int = None) -> Dict[str, Any]:
    """Generate sample project data"""
    return {
        'id': project_id or fake.random_int(min=1, max=10000),
        'user_id': user_id or fake.random_int(min=1, max=100),
        'name': fake.sentence(nb_words=4),
        'description': fake.text(max_nb_chars=500),
        'client_name': fake.company(),
        'client_email': fake.email(),
        'status': random.choice(['active', 'completed', 'on_hold', 'cancelled']),
        'metadata': {
            'industry': random.choice(['Technology', 'Healthcare', 'Finance', 'Education']),
            'priority': random.choice(['low', 'medium', 'high']),
            'tags': [fake.word() for _ in range(random.randint(2, 5))]
        },
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }


def get_sample_job(job_id: int = None, project_id: int = None) -> Dict[str, Any]:
    """Generate sample job data"""
    return {
        'id': job_id or fake.random_int(min=1, max=10000),
        'project_id': project_id or fake.random_int(min=1, max=1000),
        'template_id': fake.random_int(min=1, max=50),
        'name': fake.sentence(nb_words=4),
        'description': fake.text(max_nb_chars=300),
        'status': random.choice(['pending', 'processing', 'completed', 'failed']),
        'priority': random.randint(1, 10),
        'parameters': {
            'format': random.choice(['pdf', 'docx', 'html']),
            'language': random.choice(['en', 'es', 'fr']),
            'style': random.choice(['formal', 'casual', 'technical'])
        },
        'result': None,
        'error': None,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }


def get_mock_llm_response(prompt: str = None, response_type: str = 'proposal') -> Dict[str, Any]:
    """Generate mock LLM response"""
    if response_type == 'proposal':
        return {
            'content': fake.text(max_nb_chars=2000),
            'sections': {
                'executive_summary': fake.text(max_nb_chars=300),
                'introduction': fake.text(max_nb_chars=400),
                'objectives': [fake.sentence() for _ in range(3)],
                'methodology': fake.text(max_nb_chars=500),
                'budget': fake.text(max_nb_chars=200),
                'timeline': fake.text(max_nb_chars=200),
                'conclusion': fake.text(max_nb_chars=300)
            },
            'tokens_used': fake.random_int(min=1000, max=5000),
            'model': 'gpt-4',
            'timestamp': datetime.utcnow().isoformat()
        }
    elif response_type == 'research':
        return {
            'content': fake.text(max_nb_chars=1500),
            'sources': [
                {
                    'title': fake.sentence(),
                    'url': fake.url(),
                    'relevance': random.uniform(0.7, 1.0)
                }
                for _ in range(random.randint(3, 8))
            ],
            'tokens_used': fake.random_int(min=500, max=3000),
            'model': 'gpt-4',
            'timestamp': datetime.utcnow().isoformat()
        }
    else:
        return {
            'content': fake.text(max_nb_chars=1000),
            'tokens_used': fake.random_int(min=100, max=2000),
            'model': 'gpt-4',
            'timestamp': datetime.utcnow().isoformat()
        }


def get_sample_document(document_id: int = None, project_id: int = None) -> Dict[str, Any]:
    """Generate sample document data"""
    return {
        'id': document_id or fake.random_int(min=1, max=10000),
        'project_id': project_id or fake.random_int(min=1, max=1000),
        'name': fake.file_name(extension='pdf'),
        'document_type': random.choice(['proposal', 'report', 'contract', 'memo']),
        'format': random.choice(['pdf', 'docx', 'html', 'txt']),
        'size': fake.random_int(min=1000, max=10000000),  # bytes
        'path': f'/documents/{fake.uuid4()}.pdf',
        'status': random.choice(['draft', 'final', 'archived']),
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }


def get_sample_webhook_event(event_type: str = 'job.completed') -> Dict[str, Any]:
    """Generate sample webhook event"""
    return {
        'id': fake.uuid4(),
        'event_type': event_type,
        'data': {
            'job_id': fake.random_int(min=1, max=1000),
            'status': 'completed',
            'result': {'document_id': fake.random_int(min=1, max=1000)}
        },
        'timestamp': datetime.utcnow().isoformat()
    }


def get_batch_users(count: int = 10) -> List[Dict[str, Any]]:
    """Generate batch of sample users"""
    return [get_sample_user() for _ in range(count)]


def get_batch_proposals(count: int = 10) -> List[Dict[str, Any]]:
    """Generate batch of sample proposals"""
    return [get_sample_proposal() for _ in range(count)]


def get_batch_funders(count: int = 10) -> List[Dict[str, Any]]:
    """Generate batch of sample funders"""
    return [get_sample_funder() for _ in range(count)]

