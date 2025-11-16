"""
Tests for background processing and API endpoints
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from database.db import get_session, init_db
from database.models import Project, Job
from agents.project_manager import ProjectManagerAgent
from services.background_processor import BackgroundProcessor, background_processor
from workers.task_worker import TaskWorker, execute_task_async
from core.workflow_orchestrator import WorkflowOrchestrator


@pytest.fixture
def db_session():
    """Create a test database session"""
    from database.models import Base
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    engine.dispose()


@pytest.fixture
def test_project(db_session):
    """Create a test project"""
    project = Project(
        name="Test Project",
        funder_name="Test Funder",
        user_email="test@example.com",
        status="draft"
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def test_job(db_session, test_project):
    """Create a test job"""
    job = Job(
        project_id=test_project.id,
        task_type="test_task",
        status="pending"
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


class TestProjectManagerAgent:
    """Tests for ProjectManagerAgent"""
    
    def test_init(self):
        """Test agent initialization"""
        agent = ProjectManagerAgent()
        assert agent.name == "Project Manager Agent"
        assert agent.task_type == "coordination"
    
    def test_breakdown_tasks(self):
        """Test task breakdown"""
        agent = ProjectManagerAgent()
        project_data = {
            "name": "Test Project",
            "funder_name": "Test Funder",
            "requirements": {"budget": 100000}
        }
        
        result = agent.breakdown_tasks(project_data)
        
        assert "tasks" in result
        assert isinstance(result["tasks"], list)
        assert len(result["tasks"]) > 0
        assert "estimated_total_hours" in result
    
    def test_track_progress(self):
        """Test progress tracking"""
        agent = ProjectManagerAgent()
        progress_data = {
            "project_id": 1,
            "tasks": [
                {"id": "task_1", "status": "completed"},
                {"id": "task_2", "status": "running"},
                {"id": "task_3", "status": "pending"}
            ]
        }
        
        result = agent.track_progress(progress_data)
        
        assert "progress_percent" in result
        assert result["progress_percent"] == pytest.approx(33.33, abs=0.1)
        assert result["completed_tasks"] == 1
        assert result["total_tasks"] == 3
    
    def test_manage_dependencies(self):
        """Test dependency management"""
        agent = ProjectManagerAgent()
        dependency_data = {
            "tasks": [
                {"id": "task_1", "dependencies": []},
                {"id": "task_2", "dependencies": ["task_1"]},
                {"id": "task_3", "dependencies": ["task_1"]}
            ]
        }
        
        result = agent.manage_dependencies(dependency_data)
        
        assert "execution_order" in result
        assert "task_1" in result["execution_order"]
        assert result["execution_order"].index("task_1") < result["execution_order"].index("task_2")
    
    def test_check_deadlines(self):
        """Test deadline checking"""
        agent = ProjectManagerAgent()
        deadline_data = {
            "deadline": (datetime.utcnow().replace(microsecond=0) + 
                        pytest.importorskip("datetime").timedelta(days=5)).isoformat(),
            "tasks": [],
            "progress_percent": 50,
            "elapsed_days": 2
        }
        
        result = agent.check_deadlines(deadline_data)
        
        assert "days_remaining" in result
        assert "risk_level" in result
        assert "alert" in result
        assert result["days_remaining"] > 0
    
    def test_allocate_resources(self):
        """Test resource allocation"""
        agent = ProjectManagerAgent()
        resource_data = {
            "tasks": [
                {"id": "task_1", "type": "research", "priority": "high", "duration_hours": 4},
                {"id": "task_2", "type": "writing", "priority": "medium", "duration_hours": 6}
            ],
            "available_agents": ["research_agent", "writing_agent", "general_agent"],
            "max_concurrent": 5
        }
        
        result = agent.allocate_resources(resource_data)
        
        assert "allocation" in result
        assert "task_1" in result["allocation"]
        assert "assigned_agent" in result["allocation"]["task_1"]


class TestBackgroundProcessor:
    """Tests for BackgroundProcessor"""
    
    def test_init(self):
        """Test processor initialization"""
        processor = BackgroundProcessor(max_workers=3)
        assert processor.max_workers == 3
        assert not processor._started
    
    def test_start_shutdown(self):
        """Test starting and shutting down processor"""
        processor = BackgroundProcessor()
        processor.start()
        assert processor._started
        assert processor.scheduler is not None
        
        processor.shutdown()
        assert not processor._started
    
    def test_add_job(self):
        """Test adding a job"""
        processor = BackgroundProcessor()
        processor.start()
        
        def test_func():
            pass
        
        job_id = processor.add_job(
            job_id=1,
            func=test_func,
            job_type="test"
        )
        
        assert job_id is not None
        assert "job_1_test" in processor.job_callbacks
        
        processor.shutdown()
    
    def test_remove_job(self):
        """Test removing a job"""
        processor = BackgroundProcessor()
        processor.start()
        
        def test_func():
            pass
        
        job_id = processor.add_job(1, test_func, job_type="test")
        processor.remove_job(job_id)
        
        assert job_id not in processor.job_callbacks
        
        processor.shutdown()
    
    def test_list_jobs(self):
        """Test listing jobs"""
        processor = BackgroundProcessor()
        processor.start()
        
        def test_func():
            pass
        
        processor.add_job(1, test_func, job_type="test")
        jobs = processor.list_jobs()
        
        assert len(jobs) > 0
        
        processor.shutdown()


class TestTaskWorker:
    """Tests for TaskWorker"""
    
    @patch('workers.task_worker.get_session')
    def test_execute_task(self, mock_get_session, test_job):
        """Test task execution"""
        mock_db = MagicMock()
        mock_get_session.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = test_job
        
        orchestrator = Mock(spec=WorkflowOrchestrator)
        orchestrator.execute_task.return_value = {"result": "success"}
        
        worker = TaskWorker(orchestrator)
        
        # Mock the job update
        test_job.status = "running"
        
        result = worker.execute_task(1, {"test": "data"})
        
        assert "result" in result or result.get("status") in ["completed", "running"]
        orchestrator.execute_task.assert_called_once()
    
    def test_cancel_task(self, db_session, test_job):
        """Test task cancellation"""
        with patch('workers.task_worker.get_session', return_value=db_session):
            with patch('workers.task_worker.background_processor') as mock_processor:
                worker = TaskWorker()
                
                result = worker.cancel_task(test_job.id)
                
                assert result is True
                mock_processor.remove_job.assert_called_once()


class TestAPIEndpoints:
    """Tests for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create Flask test client"""
        from api.endpoints import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
    
    @patch('api.endpoints.orchestrator')
    @patch('api.endpoints.execute_task_async')
    def test_create_job(self, mock_execute, mock_orchestrator, client, test_project):
        """Test job creation endpoint"""
        mock_job = Mock()
        mock_job.id = 1
        mock_job.status = "pending"
        mock_job.task_type = "test_task"
        mock_job.created_at = datetime.utcnow()
        mock_orchestrator.create_job.return_value = mock_job
        
        with patch('api.endpoints.get_session') as mock_get_session:
            mock_db = MagicMock()
            mock_get_session.return_value = mock_db
            mock_db.query.return_value.filter.return_value.first.return_value = test_project
            
            response = client.post('/api/jobs', json={
                "project_id": test_project.id,
                "task_type": "test_task",
                "input_data": {"test": "data"}
            })
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data["job_id"] == 1
            assert data["status"] == "pending"
    
    def test_get_job_status(self, client, test_job):
        """Test get job status endpoint"""
        with patch('api.endpoints.get_session') as mock_get_session:
            mock_db = MagicMock()
            mock_get_session.return_value = mock_db
            mock_db.query.return_value.filter.return_value.first.return_value = test_job
            test_job.to_dict.return_value = {
                "id": test_job.id,
                "status": "pending"
            }
            
            response = client.get(f'/api/jobs/{test_job.id}')
            assert response.status_code == 200
    
    def test_list_jobs(self, client):
        """Test list jobs endpoint"""
        with patch('api.endpoints.get_session') as mock_get_session:
            mock_db = MagicMock()
            mock_get_session.return_value = mock_db
            mock_job = Mock()
            mock_job.to_dict.return_value = {"id": 1, "status": "pending"}
            mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_job]
            mock_db.query.return_value.filter.return_value.order_by.return_value.count.return_value = 1
            
            response = client.get('/api/jobs')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "jobs" in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

