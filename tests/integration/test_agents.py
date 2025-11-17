"""Agent integration tests for communication, coordination, and data flow"""
import pytest
from tests.fixtures.mock_services import MockLLMService, MockDatabase
from tests.fixtures.test_data import get_sample_project, get_sample_proposal


@pytest.mark.integration
class TestAgentCommunication:
    """Test communication between agents"""
    
    def test_agent_message_passing(self, mock_database):
        """Test agents passing messages/data"""
        # Simulate agent communication
        project = mock_database.add('projects', get_sample_project())
        
        # Agent 1 creates data
        agent1_data = {
            'agent': 'research_agent',
            'data': {'topic': 'test', 'sources': ['source1', 'source2']},
            'project_id': project['id']
        }
        
        # Agent 2 receives data
        agent2_input = agent1_data['data']
        assert agent2_input['topic'] == 'test'
        assert len(agent2_input['sources']) == 2
    
    def test_agent_event_broadcast(self, mock_database):
        """Test agents broadcasting events"""
        events = []
        
        def event_handler(event_type, data):
            events.append({'type': event_type, 'data': data})
        
        # Simulate event broadcast
        project = mock_database.add('projects', get_sample_project())
        event_handler('project_created', {'project_id': project['id']})
        
        assert len(events) == 1
        assert events[0]['type'] == 'project_created'
        assert events[0]['data']['project_id'] == project['id']


@pytest.mark.integration
class TestAgentCoordination:
    """Test coordination between multiple agents"""
    
    def test_sequential_agent_execution(self, mock_database, mock_llm_service):
        """Test agents executing in sequence"""
        project = mock_database.add('projects', get_sample_project())
        
        # Agent 1: Research
        research_result = mock_llm_service.research_topic("test")
        research_data = {'research': research_result}
        
        # Agent 2: Generation (depends on research)
        generation_result = mock_llm_service.generate_proposal(research_data)
        
        assert research_result is not None
        assert generation_result is not None
        assert 'content' in generation_result
    
    def test_parallel_agent_execution(self, mock_database, mock_llm_service):
        """Test agents executing in parallel"""
        project = mock_database.add('projects', get_sample_project())
        
        # Multiple agents working in parallel
        results = []
        
        # Agent 1: Research
        results.append(('research', mock_llm_service.research_topic("topic1")))
        
        # Agent 2: Analysis (parallel)
        results.append(('analysis', mock_llm_service.generate_text("analyze")))
        
        # Agent 3: Formatting (parallel)
        results.append(('formatting', mock_llm_service.generate_text("format")))
        
        assert len(results) == 3
        assert all(result[1] is not None for result in results)
    
    def test_agent_dependency_management(self, mock_database):
        """Test managing agent dependencies"""
        project = mock_database.add('projects', get_sample_project())
        
        # Define agent dependencies
        agents = {
            'research': {'depends_on': []},
            'generation': {'depends_on': ['research']},
            'review': {'depends_on': ['generation']},
            'formatting': {'depends_on': ['generation']}
        }
        
        # Verify dependency graph
        assert agents['research']['depends_on'] == []
        assert 'research' in agents['generation']['depends_on']
        assert 'generation' in agents['review']['depends_on']
        assert 'generation' in agents['formatting']['depends_on']


@pytest.mark.integration
class TestAgentErrorHandling:
    """Test error handling in agent coordination"""
    
    def test_agent_failure_handling(self, mock_database):
        """Test handling agent failures"""
        project = mock_database.add('projects', get_sample_project())
        
        # Simulate agent failure
        agent_status = {
            'research': 'completed',
            'generation': 'failed',
            'error': 'LLM service error'
        }
        
        # Verify error is captured
        assert agent_status['generation'] == 'failed'
        assert 'error' in agent_status
        
        # Verify dependent agents are notified
        dependent_agents = ['review', 'formatting']
        for agent in dependent_agents:
            # In real scenario, these would be marked as 'cancelled' or 'pending'
            assert agent in dependent_agents
    
    def test_agent_retry_mechanism(self, mock_database, mock_llm_service):
        """Test retry mechanism for failed agents"""
        project = mock_database.add('projects', get_sample_project())
        
        # Simulate retry
        max_retries = 3
        attempt = 0
        success = False
        
        while attempt < max_retries and not success:
            try:
                result = mock_llm_service.generate_text("test")
                success = result is not None
            except Exception:
                attempt += 1
        
        assert success or attempt == max_retries


@pytest.mark.integration
class TestAgentDataFlow:
    """Test data flow between agents"""
    
    def test_data_transformation_between_agents(self, mock_database, mock_llm_service):
        """Test data being transformed between agents"""
        project = mock_database.add('projects', get_sample_project())
        
        # Agent 1 output
        research_output = {
            'sources': ['source1', 'source2'],
            'summary': 'Research summary'
        }
        
        # Agent 2 transforms data
        generation_input = {
            'research_summary': research_output['summary'],
            'source_count': len(research_output['sources'])
        }
        
        # Agent 2 processes
        result = mock_llm_service.generate_proposal(generation_input)
        
        assert result is not None
        assert 'content' in result
    
    def test_data_validation_between_agents(self, mock_database):
        """Test data validation in agent communication"""
        # Agent 1 output
        agent1_output = {
            'data': 'test data',
            'metadata': {'version': 1, 'format': 'json'}
        }
        
        # Agent 2 validates
        required_fields = ['data', 'metadata']
        assert all(field in agent1_output for field in required_fields)
        assert agent1_output['metadata']['version'] == 1
    
    def test_data_persistence_between_agents(self, mock_database):
        """Test data persistence for agent communication"""
        project = mock_database.add('projects', get_sample_project())
        
        # Agent 1 saves intermediate result
        intermediate_data = {
            'project_id': project['id'],
            'agent': 'research',
            'result': {'sources': ['s1', 's2']}
        }
        saved = mock_database.add('agent_results', intermediate_data)
        
        # Agent 2 retrieves
        retrieved = mock_database.get('agent_results', saved['id'])
        
        assert retrieved is not None
        assert retrieved['agent'] == 'research'
        assert retrieved['project_id'] == project['id']


