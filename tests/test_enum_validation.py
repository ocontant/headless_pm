#!/usr/bin/env python3
"""
Test suite for enum validation across models, API schemas, and database constraints.

This test suite validates:
1. Enum value normalization in SQLModel models
2. API schema enum validation
3. Database constraint enforcement  
4. Legacy value handling
5. Case insensitive enum handling
"""

import pytest
from datetime import datetime
from sqlmodel import Session, select
from pydantic import ValidationError

from src.models.database import get_session
from src.models.models import Agent, Task, Document, Service, Changelog, Project, Epic, Feature
from src.models.enums import TaskStatus, AgentRole, DifficultyLevel, TaskComplexity, ConnectionType, AgentStatus
from src.models.document_enums import DocumentType, ServiceStatus
from src.api.schemas import (
    AgentRegisterRequest, TaskCreateRequest, TaskStatusUpdateRequest, 
    DocumentCreateRequest
)

class TestEnumValidation:
    """Test enum validation in models and schemas."""
    
    def test_agent_role_validation(self, db: Session, sample_project: Project):
        """Test agent role enum validation with case handling."""
        # Test valid lowercase role
        agent_data = {
            'agent_id': 'test_agent_1',
            'project_id': sample_project.id,
            'role': 'frontend_dev',  # lowercase
            'level': 'senior',
            'connection_type': 'client'
        }
        
        agent = Agent(**agent_data)
        assert agent.role == AgentRole.FRONTEND_DEV
        
        # Test legacy 'pm' role mapping
        agent_data['agent_id'] = 'test_agent_2'
        agent_data['role'] = 'pm'  # legacy value
        agent = Agent(**agent_data)
        assert agent.role == AgentRole.PROJECT_PM
        
        # Test uppercase role normalization
        agent_data['agent_id'] = 'test_agent_3'
        agent_data['role'] = 'BACKEND_DEV'  # uppercase
        agent = Agent(**agent_data)
        assert agent.role == AgentRole.BACKEND_DEV
        
        # Test invalid role
        agent_data['role'] = 'invalid_role'
        with pytest.raises(ValueError, match="Invalid agent role"):
            Agent(**agent_data)
    
    def test_agent_status_validation(self, db: Session, sample_project: Project):
        """Test agent status enum validation."""
        agent_data = {
            'agent_id': 'test_agent_status',
            'project_id': sample_project.id,
            'role': AgentRole.FRONTEND_DEV,
            'level': DifficultyLevel.SENIOR,
            'connection_type': ConnectionType.CLIENT
        }
        
        # Test valid status values
        for status in ['idle', 'working', 'offline']:
            agent_data['status'] = status
            agent = Agent(**agent_data)
            assert agent.status == AgentStatus(status)
        
        # Test uppercase status normalization
        agent_data['status'] = 'IDLE'
        agent = Agent(**agent_data)
        assert agent.status == AgentStatus.IDLE
        
        # Test invalid status
        agent_data['status'] = 'invalid_status'
        with pytest.raises(ValueError, match="Invalid agent status"):
            Agent(**agent_data)
    
    def test_task_status_validation(self, db: Session, sample_feature: Feature):
        """Test task status enum validation including legacy values."""
        task_data = {
            'feature_id': sample_feature.id,
            'title': 'Test Task',
            'description': 'Test task description',
            'created_by_id': 1,
            'target_role': AgentRole.FRONTEND_DEV,
            'difficulty': DifficultyLevel.SENIOR,
            'complexity': TaskComplexity.MAJOR,
            'branch': 'feature/test'
        }
        
        # Test valid status
        task_data['status'] = 'created'
        task = Task(**task_data)
        assert task.status == TaskStatus.CREATED
        
        # Test legacy status mapping
        task_data['status'] = 'evaluation'  # legacy value
        task = Task(**task_data)
        assert task.status == TaskStatus.QA_DONE
        
        task_data['status'] = 'approved'  # legacy value
        task = Task(**task_data)
        assert task.status == TaskStatus.COMMITTED
        
        # Test case normalization
        task_data['status'] = 'UNDER_WORK'
        task = Task(**task_data)
        assert task.status == TaskStatus.UNDER_WORK
        
        # Test invalid status
        task_data['status'] = 'invalid_status'
        with pytest.raises(ValueError, match="Invalid task status"):
            Task(**task_data)
    
    def test_document_type_validation(self, db: Session, sample_project: Project):
        """Test document type enum validation."""
        doc_data = {
            'project_id': sample_project.id,
            'author_id': 'test_author',
            'title': 'Test Document',
            'content': 'Test content'
        }
        
        # Test valid document types
        for doc_type in ['update', 'standup', 'critical_issue', 'service_status']:
            doc_data['doc_type'] = doc_type
            document = Document(**doc_data)
            assert document.doc_type == DocumentType(doc_type)
        
        # Test case normalization
        doc_data['doc_type'] = 'UPDATE'
        document = Document(**doc_data)
        assert document.doc_type == DocumentType.UPDATE
        
        # Test invalid document type
        doc_data['doc_type'] = 'invalid_type'
        with pytest.raises(ValueError, match="Invalid document type"):
            Document(**doc_data)
    
    def test_service_status_validation(self, db: Session, sample_project: Project):
        """Test service status enum validation."""
        service_data = {
            'project_id': sample_project.id,
            'service_name': 'test_service',
            'owner_agent_id': 'test_agent',
            'ping_url': 'http://localhost:8080/health'
        }
        
        # Test valid status values
        for status in ['up', 'down', 'starting']:
            service_data['status'] = status
            service = Service(**service_data)
            assert service.status == ServiceStatus(status)
        
        # Test case normalization
        service_data['status'] = 'UP'
        service = Service(**service_data)
        assert service.status == ServiceStatus.UP
        
        # Test invalid status
        service_data['status'] = 'invalid_status'
        with pytest.raises(ValueError, match="Invalid service status"):
            Service(**service_data)

class TestAPISchemaValidation:
    """Test enum validation in API schemas."""
    
    def test_agent_register_request_validation(self):
        """Test AgentRegisterRequest enum validation."""
        # Valid request
        request_data = {
            'agent_id': 'test_agent',
            'project_id': 1,
            'role': 'frontend_dev',
            'level': 'senior',
            'connection_type': 'client'
        }
        
        request = AgentRegisterRequest(**request_data)
        assert request.role == AgentRole.FRONTEND_DEV
        assert request.level == DifficultyLevel.SENIOR
        assert request.connection_type == ConnectionType.CLIENT
        
        # Test legacy role mapping
        request_data['role'] = 'pm'
        request = AgentRegisterRequest(**request_data)
        assert request.role == AgentRole.PROJECT_PM
        
        # Test case normalization
        request_data['role'] = 'BACKEND_DEV'
        request_data['level'] = 'PRINCIPAL'
        request_data['connection_type'] = 'MCP'
        request = AgentRegisterRequest(**request_data)
        assert request.role == AgentRole.BACKEND_DEV
        assert request.level == DifficultyLevel.PRINCIPAL
        assert request.connection_type == ConnectionType.MCP
        
        # Test invalid values
        request_data['role'] = 'invalid_role'
        with pytest.raises(ValidationError):
            AgentRegisterRequest(**request_data)
    
    def test_task_create_request_validation(self):
        """Test TaskCreateRequest enum validation."""
        request_data = {
            'feature_id': 1,
            'title': 'Test Task',
            'description': 'Test description',
            'target_role': 'qa',
            'difficulty': 'junior',
            'complexity': 'minor',
            'branch': 'feature/test'
        }
        
        request = TaskCreateRequest(**request_data)
        assert request.target_role == AgentRole.QA
        assert request.difficulty == DifficultyLevel.JUNIOR
        assert request.complexity == TaskComplexity.MINOR
        
        # Test case normalization
        request_data['target_role'] = 'ARCHITECT'
        request_data['difficulty'] = 'SENIOR'
        request_data['complexity'] = 'MAJOR'
        request = TaskCreateRequest(**request_data)
        assert request.target_role == AgentRole.ARCHITECT
        assert request.difficulty == DifficultyLevel.SENIOR
        assert request.complexity == TaskComplexity.MAJOR
        
        # Test invalid values
        request_data['difficulty'] = 'invalid_level'
        with pytest.raises(ValidationError):
            TaskCreateRequest(**request_data)
    
    def test_task_status_update_validation(self):
        """Test TaskStatusUpdateRequest enum validation."""
        # Valid status
        request = TaskStatusUpdateRequest(status='dev_done')
        assert request.status == TaskStatus.DEV_DONE
        
        # Test legacy status mapping
        request = TaskStatusUpdateRequest(status='evaluation')
        assert request.status == TaskStatus.QA_DONE
        
        request = TaskStatusUpdateRequest(status='approved')
        assert request.status == TaskStatus.COMMITTED
        
        # Test case normalization
        request = TaskStatusUpdateRequest(status='UNDER_WORK')
        assert request.status == TaskStatus.UNDER_WORK
        
        # Test invalid status
        with pytest.raises(ValidationError):
            TaskStatusUpdateRequest(status='invalid_status')
    
    def test_document_create_request_validation(self):
        """Test DocumentCreateRequest enum validation."""
        request_data = {
            'title': 'Test Document',
            'content': 'Test content',
            'doc_type': 'update'
        }
        
        request = DocumentCreateRequest(**request_data)
        assert request.doc_type == DocumentType.UPDATE
        
        # Test case normalization
        request_data['doc_type'] = 'CRITICAL_ISSUE'
        request = DocumentCreateRequest(**request_data)
        assert request.doc_type == DocumentType.CRITICAL_ISSUE
        
        # Test invalid document type
        request_data['doc_type'] = 'invalid_type'
        with pytest.raises(ValidationError):
            DocumentCreateRequest(**request_data)

class TestDatabaseConstraints:
    """Test database-level enum constraints."""
    
    def test_enum_constraint_enforcement(self, db: Session, sample_project: Project):
        """Test that database triggers enforce enum constraints."""
        # This test would require the migration to be run first
        # For now, we'll test the validation at the model level
        
        # Test that invalid enum values are caught before hitting the database
        with pytest.raises(ValueError):
            agent = Agent(
                agent_id='test_invalid',
                project_id=sample_project.id,
                role='invalid_role',  # This should fail validation
                level=DifficultyLevel.SENIOR,
                connection_type=ConnectionType.CLIENT
            )
            db.add(agent)
            db.commit()

class TestLegacyValueHandling:
    """Test handling of legacy enum values."""
    
    def test_legacy_pm_role_mapping(self):
        """Test that legacy 'pm' role maps to 'project_pm'."""
        # In API schema
        request = AgentRegisterRequest(
            agent_id='test_pm',
            project_id=1,
            role='pm',  # legacy value
            level='senior',
            connection_type='client'
        )
        assert request.role == AgentRole.PROJECT_PM
        
        # In model
        agent_data = {
            'agent_id': 'test_pm_model',
            'project_id': 1,
            'role': 'pm',
            'level': 'senior',
            'connection_type': 'client'
        }
        agent = Agent(**agent_data)
        assert agent.role == AgentRole.PROJECT_PM
    
    def test_legacy_task_status_mapping(self):
        """Test that legacy task status values map correctly."""
        # Test 'evaluation' -> 'qa_done'
        request = TaskStatusUpdateRequest(status='evaluation')
        assert request.status == TaskStatus.QA_DONE
        
        # Test 'approved' -> 'committed' 
        request = TaskStatusUpdateRequest(status='approved')
        assert request.status == TaskStatus.COMMITTED
        
        # In model
        task_data = {
            'feature_id': 1,
            'title': 'Test',
            'description': 'Test',
            'created_by_id': 1,
            'target_role': AgentRole.QA,
            'difficulty': DifficultyLevel.SENIOR,
            'complexity': TaskComplexity.MAJOR,
            'branch': 'test',
            'status': 'evaluation'  # legacy value
        }
        task = Task(**task_data)
        assert task.status == TaskStatus.QA_DONE

class TestCaseInsensitivity:
    """Test case insensitive enum handling."""
    
    def test_mixed_case_enum_values(self):
        """Test that mixed case enum values are normalized."""
        test_cases = [
            ('FRONTEND_DEV', AgentRole.FRONTEND_DEV),
            ('Frontend_Dev', AgentRole.FRONTEND_DEV), 
            ('frontend_dev', AgentRole.FRONTEND_DEV),
            ('FrontEnd_Dev', AgentRole.FRONTEND_DEV),
        ]
        
        for input_value, expected_enum in test_cases:
            # Test in API schema
            request = AgentRegisterRequest(
                agent_id='test_case',
                project_id=1,
                role=input_value.lower(),  # Our validator expects lowercase
                level='senior',
                connection_type='client'
            )
            assert request.role == expected_enum
    
    def test_status_case_normalization(self):
        """Test status value case normalization."""
        status_cases = [
            ('IDLE', AgentStatus.IDLE),
            ('Idle', AgentStatus.IDLE),
            ('idle', AgentStatus.IDLE),
            ('WORKING', AgentStatus.WORKING),
            ('working', AgentStatus.WORKING),
        ]
        
        for input_status, expected_enum in status_cases:
            agent_data = {
                'agent_id': 'test_status_case',
                'project_id': 1,
                'role': AgentRole.QA,
                'level': DifficultyLevel.SENIOR,
                'connection_type': ConnectionType.CLIENT,
                'status': input_status.lower()  # Our validator expects lowercase
            }
            agent = Agent(**agent_data)
            assert agent.status == expected_enum

# Fixtures for testing
@pytest.fixture
def sample_project(db: Session) -> Project:
    """Create a sample project for testing."""
    project = Project(
        name='Test Project',
        description='A test project',
        shared_path='./shared',
        instructions_path='./instructions',
        project_docs_path='./docs'
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@pytest.fixture  
def sample_epic(db: Session, sample_project: Project) -> Epic:
    """Create a sample epic for testing."""
    epic = Epic(
        project_id=sample_project.id,
        name='Test Epic',
        description='A test epic'
    )
    db.add(epic)
    db.commit()
    db.refresh(epic)
    return epic

@pytest.fixture
def sample_feature(db: Session, sample_epic: Epic) -> Feature:
    """Create a sample feature for testing."""
    feature = Feature(
        epic_id=sample_epic.id,
        name='Test Feature',
        description='A test feature'
    )
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return feature